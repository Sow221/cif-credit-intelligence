import { beforeEach, describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import i18n from "@/locales";
import { RiskGauge } from "./RiskGauge";
import type { RiskAssessment } from "@/types/risk";

const risk: RiskAssessment = {
  pd_raw: 0.12,
  pd_calibrated: 0.1,
  risk_band: "LOW",
  model_version: "gbm-v1",
  feature_set_id: "CORE_25",
};

describe("RiskGauge", () => {
  beforeEach(async () => {
    await i18n.changeLanguage("fr");
  });

  it("renders the gauge using the calibrated PD", () => {
    render(<RiskGauge risk={risk} />);
    expect(screen.getByText("10%")).toBeInTheDocument();
  });

  it("renders raw and calibrated PD values", () => {
    render(<RiskGauge risk={risk} />);
    expect(screen.getByText("12.00 %")).toBeInTheDocument();
    expect(screen.getByText("10.00 %")).toBeInTheDocument();
    expect(screen.getByText("PD estimée")).toBeInTheDocument();
    expect(screen.getByText("PD calibrée")).toBeInTheDocument();
  });

  it("falls back to the raw PD for the gauge when calibrated is null", () => {
    render(<RiskGauge risk={{ ...risk, pd_calibrated: null }} />);
    expect(screen.getByText("12%")).toBeInTheDocument();
    expect(screen.queryByText("PD calibrée")).not.toBeInTheDocument();
  });

  it("renders the risk band, model and feature set", () => {
    render(<RiskGauge risk={risk} />);
    expect(screen.getByText("Risque faible")).toBeInTheDocument();
    expect(screen.getByText("Bande de risque")).toBeInTheDocument();
    expect(screen.getByText("gbm-v1")).toBeInTheDocument();
    expect(screen.getByText("CORE_25")).toBeInTheDocument();
  });
});
