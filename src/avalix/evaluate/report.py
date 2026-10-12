"""Rapport de validation du modèle (structure inspirée de SR 11-7).

Produit, sur le bloc de TEST temporel (jamais vu à l'entraînement ni à la
calibration) :

- métriques de discrimination usuelles en crédit : ROC-AUC, Gini, KS, PR-AUC,
  avec intervalles de confiance bootstrap, comparées à une régression
  logistique de référence ;
- calibration (fiabilité des probabilités) ;
- classement par tranches de score (rank ordering) et courbe de stratégie ;
- performance par profil d'historique et équité (sexe, secteur, zone) ;
- explicabilité SHAP globale, locale et codes de motif ;
- contrôles : jeu sans signal, backtest par période, stabilité (PSI).

Usage :
    uv run avalix-report            # écrit reports/validation/
"""

from __future__ import annotations

import argparse
import json
import warnings
from typing import Any

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score, roc_curve
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from avalix.config import PROJECT_ROOT, get_config

OUT_DIR = PROJECT_ROOT / "reports" / "validation"
FONT_DIR = PROJECT_ROOT / "reports" / "assets" / "fonts"

# Palette Avalix
BG, PANEL, GRID = "#0E0F11", "#16171A", "#2A2D33"
FG, MUTED, DIM = "#ECEAE4", "#A3A7AE", "#6E727A"
BLUE, BLUE2 = "#3D4BFF", "#6F7BFF"

SEGMENTS = [
    ("Sans historique", lambda h: h == 0),
    ("1 prêt", lambda h: h == 1),
    ("2 à 3 prêts", lambda h: (h >= 2) & (h <= 3)),
    ("4 prêts et +", lambda h: h >= 4),
]


# ---------------------------------------------------------------- métriques
def ks_stat(y: np.ndarray, p: np.ndarray) -> float:
    """Statistique de Kolmogorov-Smirnov (écart max entre les répartitions)."""
    fpr, tpr, _ = roc_curve(y, p)
    return float(np.max(tpr - fpr))


def core_metrics(y: np.ndarray, p: np.ndarray) -> dict[str, float]:
    auc = roc_auc_score(y, p)
    return {
        "roc_auc": float(auc),
        "gini": float(2 * auc - 1),
        "ks": ks_stat(y, p),
        "pr_auc": float(average_precision_score(y, p)),
        "brier": float(brier_score_loss(y, p)),
    }


def bootstrap(y: np.ndarray, p: np.ndarray, n: int = 1000, seed: int = 42) -> dict:
    rng = np.random.default_rng(seed)
    out: dict[str, list[float]] = {k: [] for k in ("roc_auc", "gini", "ks", "pr_auc", "brier")}
    for _ in range(n):
        idx = rng.integers(0, len(y), len(y))
        if y[idx].min() == y[idx].max():
            continue
        for k, v in core_metrics(y[idx], p[idx]).items():
            out[k].append(v)
    return {
        k: [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))] for k, v in out.items()
    }


def psi(expected: np.ndarray, actual: np.ndarray, bins: int = 10) -> float:
    """Population Stability Index entre deux distributions."""
    qs = np.unique(np.quantile(expected, np.linspace(0, 1, bins + 1)))
    if len(qs) < 3:
        return 0.0
    e = np.histogram(np.clip(expected, qs[0], qs[-1]), qs)[0] / len(expected)
    a = np.histogram(np.clip(actual, qs[0], qs[-1]), qs)[0] / len(actual)
    e, a = np.clip(e, 1e-4, None), np.clip(a, 1e-4, None)
    return float(np.sum((a - e) * np.log(a / e)))


# ---------------------------------------------------------------- graphiques
def _style():
    import matplotlib as mpl
    from matplotlib import font_manager

    for f in FONT_DIR.glob("*.ttf"):
        font_manager.fontManager.addfont(str(f))
    mpl.rcParams.update(
        {
            "font.family": ["Instrument Sans", "DejaVu Sans"],
            "figure.facecolor": BG,
            "axes.facecolor": BG,
            "axes.edgecolor": GRID,
            "axes.labelcolor": MUTED,
            "axes.titlecolor": FG,
            "axes.titlesize": 17,
            "axes.titleweight": "medium",
            "axes.titlelocation": "left",
            "axes.titlepad": 14,
            "axes.labelsize": 12,
            "axes.grid": True,
            "grid.color": GRID,
            "grid.linewidth": 0.6,
            "xtick.color": DIM,
            "ytick.color": DIM,
            "xtick.labelsize": 11,
            "ytick.labelsize": 11,
            "legend.frameon": False,
            "legend.labelcolor": MUTED,
            "legend.fontsize": 11,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "savefig.facecolor": BG,
        }
    )


def _fig(w=16, h=9):
    import matplotlib.pyplot as plt

    return plt.subplots(figsize=(w / 1.6, h / 1.6), dpi=160)


def _save(fig, name: str, note: str = "") -> str:
    fig.text(
        0.012,
        -0.04,
        "AVALIX · données synthétiques · bloc de test temporel",
        color=DIM,
        fontsize=9,
        family="Geist Mono",
    )
    if note:
        fig.text(0.988, -0.04, note, color=DIM, fontsize=9, ha="right", family="Geist Mono")
    path = OUT_DIR / "figures" / f"{name}.png"
    fig.savefig(path, bbox_inches="tight", pad_inches=0.35)
    import matplotlib.pyplot as plt

    plt.close(fig)
    return f"figures/{name}.png"


# ---------------------------------------------------------------- rapport
def build(n_boot: int = 1000) -> dict:
    import joblib

    from avalix.data.bootstrap import MODEL_PATH, ensure_model, ensure_raw_data
    from avalix.data.ingest import load_customers, load_loans
    from avalix.decision.engine import decide
    from avalix.features.build import prepare_feature_matrix
    from avalix.models.train import temporal_split_3, train_model

    warnings.filterwarnings("ignore")
    _style()
    import matplotlib.pyplot as plt

    (OUT_DIR / "figures").mkdir(parents=True, exist_ok=True)
    cfg = get_config()
    ensure_raw_data()
    ensure_model()
    art = joblib.load(MODEL_PATH)
    model, calib, feats = art["model"], art["calibrator"], art["model_features"]

    cust, loans = load_customers(), load_loans()
    X, y = prepare_feature_matrix(cust, loans)
    df = X.copy()
    assert y is not None
    df["__y__"] = y.to_numpy()
    df["customer_id"] = cust["customer_id"].to_numpy()
    for col in ("gender", "sector", "location", "n_past_loans"):
        df[col] = cust[col].to_numpy()
    tr, cal, te = temporal_split_3(df)

    yte = te["__y__"].to_numpy()
    raw_te = model.predict_proba(te[feats])[:, 1]
    p_te = np.clip(calib.predict(raw_te), 0, 1)
    hist = te["n_past_loans"].to_numpy()

    # Référence : régression logistique standardisée, mêmes variables.
    base = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))
    base.fit(tr[feats], tr["__y__"])
    p_base = base.predict_proba(te[feats])[:, 1]

    res: dict = {
        "dataset": {
            "n_total": len(df),
            "n_train": len(tr),
            "n_calibration": len(cal),
            "n_test": len(te),
            "default_rate_test": float(yte.mean()),
        },
        "model": {**core_metrics(yte, p_te), "ci95": bootstrap(yte, p_te, n_boot)},
        "baseline_logreg": {**core_metrics(yte, p_base), "ci95": bootstrap(yte, p_base, n_boot)},
    }
    figs: dict[str, str] = {}

    # 1. ROC + PR
    from sklearn.metrics import precision_recall_curve

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(16 / 1.6, 7 / 1.6), dpi=160)
    for p, lab, c, lw in (
        (p_base, "Régression logistique", MUTED, 1.6),
        (p_te, "Avalix (XGBoost calibré)", BLUE2, 2.4),
    ):
        fpr, tpr, _ = roc_curve(yte, p)
        a1.plot(fpr, tpr, color=c, lw=lw, label=f"{lab} · AUC {roc_auc_score(yte, p):.3f}")
        pr, rc, _ = precision_recall_curve(yte, p)
        a2.plot(rc, pr, color=c, lw=lw, label=f"{lab} · AP {average_precision_score(yte, p):.3f}")
    a1.plot([0, 1], [0, 1], color=DIM, lw=1, ls="--", label="Hasard")
    a2.axhline(yte.mean(), color=DIM, lw=1, ls="--", label=f"Taux de défaut {yte.mean():.1%}")
    a1.set(title="Courbe ROC", xlabel="Taux de faux positifs", ylabel="Taux de vrais positifs")
    a2.set(title="Précision / rappel", xlabel="Rappel (défauts détectés)", ylabel="Précision")
    a1.legend(loc="lower right")
    a2.legend(loc="upper right")
    figs["roc_pr"] = _save(fig, "01_roc_pr")

    # 2. Calibration
    fig, ax = _fig(10, 8)
    bins = np.quantile(p_te, np.linspace(0, 1, 11))
    for p, lab, c in (
        (raw_te, "Avant calibration", DIM),
        (p_te, "Après calibration isotonique", BLUE2),
    ):
        idx = np.clip(np.digitize(p, np.unique(np.quantile(p, np.linspace(0, 1, 11)))[1:-1]), 0, 9)
        xs = [p[idx == k].mean() for k in range(10) if (idx == k).any()]
        ys = [yte[idx == k].mean() for k in range(10) if (idx == k).any()]
        ax.plot(xs, ys, "o-", color=c, lw=2, ms=6, label=lab)
    m = max(0.6, float(np.max(p_te)))
    ax.plot([0, m], [0, m], color=DIM, ls="--", lw=1, label="Calibration parfaite")
    ax.set(
        title="Fiabilité des probabilités",
        xlabel="Probabilité de défaut prédite",
        ylabel="Taux de défaut observé",
    )
    ax.legend(loc="upper left")
    figs["calibration"] = _save(fig, "02_calibration", f"Brier {brier_score_loss(yte, p_te):.3f}")
    del bins

    # 3. Tranches de score (rank ordering)
    order = np.argsort(p_te)
    deciles = np.array_split(order, 10)
    band = [
        {
            "band": i + 1,
            "n": len(d),
            "pd_mean": float(p_te[d].mean()),
            "default_rate": float(yte[d].mean()),
        }
        for i, d in enumerate(deciles)
    ]
    res["score_bands"] = band
    fig, ax = _fig(14, 8)
    dr = [b["default_rate"] for b in band]
    ax.bar(range(1, 11), dr, color=[BLUE if i == 9 else MUTED for i in range(10)], width=0.7)
    ax.plot(
        range(1, 11),
        [b["pd_mean"] for b in band],
        "o-",
        color=BLUE2,
        lw=2,
        label="Probabilité moyenne prédite",
    )
    for i, v in enumerate(dr):
        ax.text(
            i + 1, v + 0.005, f"{v:.0%}", ha="center", color=FG, fontsize=11, family="Geist Mono"
        )
    ax.set(
        title="Taux de défaut par tranche de score (du moins au plus risqué)",
        xlabel="Décile de risque",
        ylabel="Taux de défaut observé",
        xticks=range(1, 11),
    )
    ax.legend(loc="upper left")
    mono = all(dr[i] <= dr[i + 1] + 0.01 for i in range(9))
    res["rank_ordering_monotonic"] = bool(mono)
    figs["score_bands"] = _save(
        fig, "03_score_bands", "classement monotone" if mono else "classement non monotone"
    )

    # 4. Courbe de stratégie
    cuts = np.linspace(0.01, 0.6, 120)
    appr = [(p_te < c).mean() for c in cuts]
    bad = [yte[p_te < c].mean() if (p_te < c).any() else 0 for c in cuts]
    fig, ax = _fig(12, 8)
    ax.plot(appr, bad, color=BLUE2, lw=2.4)
    t = cfg.decision_engine["thresholds"]
    pts: dict[tuple[float, float], list[str]] = {}
    for name, c in (
        ("approbation auto", t["auto_approve"]),
        ("revue", t["human_review"]),
        ("ajustement", t["adjust"]),
    ):
        a, b = float((p_te < c).mean()), float(yte[p_te < c].mean())
        pts.setdefault((round(a, 2), round(b, 2)), []).append(f"{name} ({c:.2f})")
    for (a, b), names in pts.items():
        ax.plot(a, b, "o", color=FG, ms=7)
        ax.annotate(
            "seuils " + " = ".join(names) if len(names) > 1 else "seuil " + names[0],
            (a, b),
            textcoords="offset points",
            xytext=(-14, 14) if a > 0.7 else (12, -30),
            ha="right" if a > 0.7 else "left",
            color=FG,
            fontsize=10,
        )
        ax.annotate(
            f"{a:.0%} acceptés · {b:.1%} défauts",
            (a, b),
            textcoords="offset points",
            xytext=(-14, 0) if a > 0.7 else (12, -44),
            ha="right" if a > 0.7 else "left",
            color=MUTED,
            fontsize=10,
            family="Geist Mono",
        )
    ax.set(
        title="Courbe de stratégie : taux d'acceptation contre taux de défaut",
        xlabel="Part des demandes acceptées",
        ylabel="Taux de défaut parmi les acceptés",
    )
    figs["strategy"] = _save(fig, "04_strategy")

    # 5. Segments d'historique
    seg_rows = []
    for name, f in SEGMENTS:
        msk = f(hist)
        if yte[msk].min() == yte[msk].max():
            continue
        ci = bootstrap(yte[msk], p_te[msk], n_boot)["roc_auc"]
        nz = int((te.loc[msk, feats].abs().sum() > 0).sum())
        seg_rows.append(
            {
                "segment": name,
                "n": int(msk.sum()),
                "n_defaults": int(yte[msk].sum()),
                "roc_auc": float(roc_auc_score(yte[msk], p_te[msk])),
                "ci95": ci,
                "features_available": nz,
                "features_total": len(feats),
            }
        )
    res["segments"] = seg_rows
    fig, ax = _fig(14, 7)
    for i, r in enumerate(seg_rows):
        c = BLUE2 if r["segment"] == "Sans historique" else MUTED
        ax.plot(r["ci95"], [i, i], color=c, lw=3, solid_capstyle="butt")
        ax.plot(r["roc_auc"], i, "o", color=c, ms=11)
        ax.text(
            1.005,
            i,
            f"{r['roc_auc']:.2f}  [{r['ci95'][0]:.2f} – {r['ci95'][1]:.2f}]  "
            f"· {r['features_available']}/{r['features_total']} variables · {r['n_defaults']} défauts",
            va="center",
            color=c,
            fontsize=11,
            family="Geist Mono",
            transform=ax.get_yaxis_transform(),
        )
    ax.axvline(0.5, color=DIM, ls="--", lw=1)
    ax.set(
        yticks=range(len(seg_rows)),
        yticklabels=[r["segment"] for r in seg_rows],
        xlim=(0.45, 1.0),
        title="ROC-AUC par profil d'historique (intervalle de confiance à 95 %)",
        xlabel="ROC-AUC (0,50 = hasard)",
    )
    ax.invert_yaxis()
    figs["segments"] = _save(fig, "05_segments")

    # Décisions (moteur Avalix, boost revue pour les sans-historique)
    dec = decide(p_te, history_len=hist)
    res["decisions"] = dec["decision"].value_counts().to_dict()
    res["decisions_no_history"] = dec.loc[hist == 0, "decision"].value_counts().to_dict()

    # 6. Équité
    fair: list[dict[str, Any]] = []
    approved = dec["decision"].to_numpy() == "APPROBATION"
    for grp in ("gender", "sector", "location"):
        for val in sorted(te[grp].unique()):
            msk = (te[grp] == val).to_numpy()
            fair.append(
                {
                    "group": grp,
                    "value": str(val),
                    "n": int(msk.sum()),
                    "default_rate": float(yte[msk].mean()),
                    "roc_auc": float(roc_auc_score(yte[msk], p_te[msk])),
                    "auto_approval_rate": float(approved[msk].mean()),
                }
            )
    res["fairness"] = fair
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(16 / 1.6, 7 / 1.6), dpi=160, sharey=True)
    labels = [f"{r['value']}" for r in fair]
    ypos = np.arange(len(fair))
    a1.barh(ypos, [r["roc_auc"] for r in fair], color=MUTED, height=0.6)
    a2.barh(ypos, [r["auto_approval_rate"] for r in fair], color=BLUE, height=0.6)
    a1.set(yticks=ypos, yticklabels=labels, xlim=(0.5, 1.0), title="ROC-AUC par groupe")
    a2.set(xlim=(0, 1), title="Taux d'approbation automatique")
    a1.invert_yaxis()
    for i, r in enumerate(fair):
        a1.text(
            r["roc_auc"] + 0.005,
            i,
            f"{r['roc_auc']:.2f}",
            va="center",
            color=FG,
            fontsize=10,
            family="Geist Mono",
        )
        a2.text(
            r["auto_approval_rate"] + 0.01,
            i,
            f"{r['auto_approval_rate']:.0%}",
            va="center",
            color=FG,
            fontsize=10,
            family="Geist Mono",
        )
    figs["fairness"] = _save(fig, "06_fairness", "sexe · secteur · zone")

    # 7-8. SHAP
    import shap

    expl = shap.TreeExplainer(model)
    sv = expl.shap_values(te[feats])
    imp = pd.Series(np.abs(sv).mean(0), index=feats).sort_values(ascending=False)
    res["shap_global_top"] = {k: float(v) for k, v in imp.head(12).items()}
    fig, ax = _fig(12, 8)
    top = imp.head(12)[::-1]
    ax.barh(
        top.index,
        top.values,
        color=[BLUE if i == len(top) - 1 else MUTED for i in range(len(top))],
        height=0.65,
    )
    ax.set(
        title="Ce qui pèse le plus dans le score (|SHAP| moyen)",
        xlabel="Contribution moyenne au log-odds de défaut",
    )
    figs["shap_global"] = _save(fig, "07_shap_global")

    idx_thin = int(np.where((hist == 0) & (dec["decision"].to_numpy() == "REVUE_HUMAINE"))[0][0])
    idx_rich = int(np.where((hist >= 4) & approved)[0][0])
    reasons = {}
    fig, axes = plt.subplots(
        1, 2, figsize=(20 / 1.6, 7 / 1.6), dpi=160, gridspec_kw={"wspace": 0.75}
    )
    for ax, i, lab in (
        (axes[0], idx_thin, "Sans historique → revue humaine"),
        (axes[1], idx_rich, "4 prêts et + → approbation"),
    ):
        s = pd.Series(sv[i], index=feats)
        s = s.reindex(s.abs().sort_values(ascending=False).index).head(8)[::-1]
        ax.barh(s.index, s.values, color=[BLUE2 if v > 0 else MUTED for v in s.values], height=0.6)
        ax.axvline(0, color=DIM, lw=1)
        ax.set_title(f"{lab}\nPD {p_te[i]:.1%}", fontsize=12, loc="left")
        ax.set_xlabel("← réduit le risque · augmente le risque →", fontsize=9)
        reasons[lab] = [f"{k} ({'+' if v > 0 else '−'})" for k, v in s[::-1].head(4).items()]
    figs["shap_local"] = _save(fig, "08_shap_local", "codes de motif = 4 premières contributions")
    res["reason_codes_examples"] = reasons

    # 9. Contrôles : jeu sans signal + backtest
    # Test de permutation : 20 cibles mélangées, on rapporte la distribution
    # (une seule permutation est trop bruitée pour conclure).
    null_aucs = []
    for s in range(20):
        rng = np.random.default_rng(s)
        y_shuf = rng.permutation(tr["__y__"].to_numpy())
        y_cal_shuf = rng.permutation(cal["__y__"].to_numpy())
        m0 = train_model(tr[feats], pd.Series(y_shuf), cal[feats], pd.Series(y_cal_shuf))
        null_aucs.append(float(roc_auc_score(yte, m0.predict_proba(te[feats])[:, 1])))
    auc_nosignal = float(np.mean(null_aucs))
    null_q = [float(np.quantile(null_aucs, 0.025)), float(np.quantile(null_aucs, 0.975))]
    windows = np.array_split(np.arange(len(te)), 4)
    bt = []
    for k, w in enumerate(windows):
        ci = bootstrap(yte[w], p_te[w], max(200, n_boot // 5))["roc_auc"]
        bt.append(
            {
                "window": k + 1,
                "n": len(w),
                "roc_auc": float(roc_auc_score(yte[w], p_te[w])),
                "ci95": ci,
            }
        )
    res["controls"] = {
        "no_signal_auc": auc_nosignal,
        "no_signal_range95": null_q,
        "no_signal_n": len(null_aucs),
        "backtest_windows": bt,
    }
    fig, (a1, a2) = plt.subplots(
        1, 2, figsize=(16 / 1.6, 7 / 1.6), dpi=160, gridspec_kw={"width_ratios": [1, 1.6]}
    )
    a1.bar(
        ["Cible mélangée\n(20 tirages)", "Vraie cible"],
        [auc_nosignal, res["model"]["roc_auc"]],
        color=[MUTED, BLUE],
        width=0.55,
    )
    a1.errorbar(
        [0],
        [auc_nosignal],
        yerr=[[auc_nosignal - null_q[0]], [null_q[1] - auc_nosignal]],
        color=FG,
        capsize=5,
        lw=1.2,
    )
    a1.axhline(0.5, color=DIM, ls="--", lw=1)
    a1.set(ylim=(0.4, 1.0), title="Test sans signal", ylabel="ROC-AUC")
    for i, v in enumerate([auc_nosignal, res["model"]["roc_auc"]]):
        a1.text(i, v + 0.01, f"{v:.2f}", ha="center", color=FG, family="Geist Mono", fontsize=12)
    a2.errorbar(
        [b["window"] for b in bt],
        [b["roc_auc"] for b in bt],
        yerr=[[b["roc_auc"] - b["ci95"][0] for b in bt], [b["ci95"][1] - b["roc_auc"] for b in bt]],
        fmt="o-",
        color=BLUE2,
        ecolor=MUTED,
        capsize=5,
        lw=2,
    )
    a2.axhline(0.5, color=DIM, ls="--", lw=1)
    a2.set(
        ylim=(0.4, 1.0),
        xticks=[1, 2, 3, 4],
        title="Backtest par période (bloc de test)",
        xlabel="Période",
        ylabel="ROC-AUC",
    )
    figs["controls"] = _save(fig, "09_controls")

    # 10. Stabilité (PSI entraînement → test)
    ps = {f: psi(tr[f].to_numpy(dtype=float), te[f].to_numpy(dtype=float)) for f in feats}
    raw_tr = model.predict_proba(tr[feats])[:, 1]
    ps_score = psi(raw_tr, raw_te)
    res["stability"] = {
        "psi_score": ps_score,
        "psi_features_top": dict(sorted(ps.items(), key=lambda kv: -kv[1])[:8]),
    }
    fig, ax = _fig(12, 7)
    s = pd.Series(ps).sort_values(ascending=False).head(10)[::-1]
    ax.barh(s.index, s.values, color=MUTED, height=0.6)
    for x, lab in ((0.1, "0,10 surveiller"), (0.25, "0,25 dérive")):
        ax.axvline(x, color=BLUE2 if x == 0.25 else DIM, ls="--", lw=1)
        ax.text(x, len(s) - 0.4, lab, color=MUTED, fontsize=10, ha="left")
    ax.set(
        title=f"Stabilité des variables (PSI entraînement → test) · score : {ps_score:.3f}",
        xlabel="PSI",
    )
    figs["psi"] = _save(fig, "10_psi")

    res["figures"] = figs
    (OUT_DIR / "metrics.json").write_text(json.dumps(res, indent=2, ensure_ascii=False))
    write_html(res)
    return res


def _fmt(v: float, d: int = 3) -> str:
    return f"{v:.{d}f}".replace(".", ",")


def write_html(r: dict) -> None:
    m, b = r["model"], r["baseline_logreg"]

    def row(lab, k, d=3):
        ci = m["ci95"][k]
        return (
            f"<tr><td>{lab}</td><td class=n>{_fmt(m[k], d)}</td><td class=d>[{_fmt(ci[0], d)} – {_fmt(ci[1], d)}]</td>"
            f"<td class=n>{_fmt(b[k], d)}</td></tr>"
        )

    seg = "".join(
        f"<tr><td>{s['segment']}</td><td class=n>{s['n']}</td><td class=n>{s['n_defaults']}</td>"
        f"<td class=n>{s['features_available']}/{s['features_total']}</td><td class=n>{_fmt(s['roc_auc'], 2)}</td>"
        f"<td class=d>[{_fmt(s['ci95'][0], 2)} – {_fmt(s['ci95'][1], 2)}]</td></tr>"
        for s in r["segments"]
    )
    dec = " · ".join(f"{k} {v}" for k, v in r["decisions"].items())
    dec_nh = " · ".join(f"{k} {v}" for k, v in r["decisions_no_history"].items())
    figs = r["figures"]

    def fig(key, cap):
        return f'<figure><img src="{figs[key]}" alt="{cap}"><figcaption>{cap}</figcaption></figure>'

    d = r["dataset"]
    html = f"""<!doctype html><html lang=fr><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Avalix · Rapport de validation</title>
<style>
@font-face{{font-family:IS;src:url(../assets/fonts/InstrumentSans-Regular.ttf)}}
@font-face{{font-family:IS;font-weight:600;src:url(../assets/fonts/InstrumentSans-SemiBold.ttf)}}
@font-face{{font-family:GM;src:url(../assets/fonts/GeistMono-Regular.ttf)}}
body{{margin:0;background:{BG};color:{FG};font-family:IS,system-ui,sans-serif;line-height:1.55}}
main{{max-width:1080px;margin:0 auto;padding:48px 20px 80px}}
h1{{font-size:40px;font-weight:600;letter-spacing:-.02em;margin:.2em 0}}
h2{{font-size:24px;font-weight:600;margin:56px 0 12px;padding-top:24px;border-top:1px solid {GRID}}}
.k{{font-family:GM;color:{DIM};letter-spacing:.12em;font-size:13px;text-transform:uppercase}}
p,li{{color:{MUTED}}} strong{{color:{FG}}}
table{{border-collapse:collapse;width:100%;margin:12px 0;font-size:15px}}
td,th{{border-bottom:1px solid {GRID};padding:9px 8px;text-align:left}} th{{color:{DIM};font-weight:400;font-family:GM;font-size:12px;letter-spacing:.08em;text-transform:uppercase}}
td.n{{font-family:GM;color:{FG}}} td.d{{font-family:GM;color:{DIM}}}
figure{{margin:24px 0}} img{{width:100%;border:1px solid {GRID};border-radius:8px}} figcaption{{font-family:GM;font-size:12px;color:{DIM};margin-top:6px}}
.note{{border:1px dashed {DIM};border-radius:8px;padding:14px 18px;color:{MUTED}}}
.dia{{display:inline-block;width:10px;height:10px;background:{BLUE};transform:rotate(45deg);margin-right:10px}}
</style></head><body><main>
<div class=k><span class=dia></span>Avalix · rapport de validation</div>
<h1>Un moteur de décision qui sait quand il ne sait pas</h1>
<p class=note><strong>Données synthétiques.</strong> Ce rapport démontre une méthode ; il ne mesure aucune performance réelle. Toutes les métriques sont calculées sur le <strong>bloc de test temporel</strong> ({d["n_test"]} demandes, {_fmt(100 * d["default_rate_test"], 1)} % de défauts), jamais vu pendant l'entraînement ({d["n_train"]}) ni la calibration ({d["n_calibration"]}).</p>

<h2>1. Performance (analyse des résultats)</h2>
<table><tr><th>Métrique</th><th>Avalix</th><th>IC 95 % (bootstrap)</th><th>Régression logistique</th></tr>
{row("ROC-AUC", "roc_auc")}{row("Gini", "gini")}{row("KS", "ks")}{row("PR-AUC", "pr_auc")}{row("Brier (plus bas = mieux)", "brier")}</table>
<p><strong>Modèle challenger.</strong> {"La régression logistique fait jeu égal avec XGBoost : leurs intervalles de confiance se recouvrent largement. Sur ces données synthétiques, la complexité du modèle n'apporte pas de gain mesurable ; la valeur du système tient à la calibration, aux seuils et à la revue humaine, pas au choix de l'algorithme. Sur données réelles, le modèle le plus simple sera retenu tant qu'il ne fait pas significativement moins bien." if b["ci95"]["roc_auc"][0] <= m["roc_auc"] <= b["ci95"]["roc_auc"][1] else "XGBoost se distingue de la régression logistique au-delà des intervalles de confiance."}</p>
{fig("roc_pr", "ROC et précision/rappel, comparés à une régression logistique")}

<h2>2. Calibration et classement</h2>
<p>Une probabilité de 10 % doit correspondre à environ 10 % de défauts observés. Le taux de défaut doit croître d'une tranche de score à l'autre (classement {"monotone" if r["rank_ordering_monotonic"] else "non monotone"}).</p>
{fig("calibration", "Fiabilité des probabilités avant et après calibration isotonique")}
{fig("score_bands", "Taux de défaut par décile de risque")}
{fig("strategy", "Compromis acceptation / défaut aux seuils du moteur de décision")}

<h2>3. Les clients sans historique</h2>
<table><tr><th>Profil</th><th>Demandes</th><th>Défauts</th><th>Variables</th><th>ROC-AUC</th><th>IC 95 %</th></tr>{seg}</table>
<p>Décisions du moteur sur le bloc de test : <strong>{dec}</strong>. Pour les demandeurs sans historique : <strong>{dec_nh}</strong>. Faute d'information, ils sont orientés vers une revue humaine plutôt qu'approuvés ou refusés automatiquement.</p>
{fig("segments", "ROC-AUC par profil d'historique, avec intervalle de confiance")}

<h2>4. Équité</h2>
{fig("fairness", "ROC-AUC et taux d’approbation automatique par sexe, secteur et zone")}

<h2>5. Explicabilité</h2>
{fig("shap_global", "Importance globale des variables (SHAP)")}
{fig("shap_local", "Explication locale de deux décisions (codes de motif)")}

<h2>6. Contrôles et stabilité</h2>
<p>Test sans signal : en mélangeant la cible, le modèle tombe en moyenne à <strong>{_fmt(r["controls"]["no_signal_auc"], 2)}</strong> sur {r["controls"]["no_signal_n"]} tirages (intervalle {_fmt(r["controls"]["no_signal_range95"][0], 2)}–{_fmt(r["controls"]["no_signal_range95"][1], 2)}, hasard = 0,50) : il n'apprend pas d'artefact. PSI du score entre entraînement et test : <strong>{_fmt(r["stability"]["psi_score"], 3)}</strong> (alerte au-delà de 0,25).</p>
{fig("controls", "Test sans signal et backtest par période")}
{fig("psi", "Stabilité des variables (Population Stability Index)")}

<h2>Limites</h2>
<ul><li>Données synthétiques ; le générateur repose en partie sur un facteur de risque latent (voir <code>data/raw/DATASET.md</code>).</li>
<li><strong>Absence d'historique codée comme un historique propre.</strong> Sans prêt passé, les retards valent 0 : le modèle lit « aucun retard » là où il devrait lire « aucune information » (voir l'explication locale, section 5). Le générateur synthétique rend ces demandeurs peu risqués (environ 3 % de défauts), ce qui masque le problème ici. C'est pourquoi le moteur de décision ne laisse jamais le score seul trancher pour eux. Correctif prévu avant toute donnée réelle : valeurs manquantes explicites et indicateur « sans historique ».</li>
<li>L'ordre des identifiants sert de substitut à la date de demande.</li>
<li>Les seuils de décision et les coûts sont provisoires et devront être recalibrés sur données réelles.</li></ul>
<p class=k>Régénérer : uv run avalix-report</p>
</main></body></html>"""
    (OUT_DIR / "index.html").write_text(html, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="avalix-report", description=__doc__)
    parser.add_argument("--n-boot", type=int, default=1000)
    args = parser.parse_args(argv)
    r = build(args.n_boot)
    m = r["model"]
    print(
        f"ROC-AUC {m['roc_auc']:.3f} · Gini {m['gini']:.3f} · KS {m['ks']:.3f} → {OUT_DIR / 'index.html'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
