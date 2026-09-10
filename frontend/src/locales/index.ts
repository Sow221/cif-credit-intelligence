import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import frCommon from "./fr/common.json";
import frDashboard from "./fr/dashboard.json";
import frApplications from "./fr/applications.json";
import frClients from "./fr/clients.json";
import frReview from "./fr/review.json";
import frModels from "./fr/models.json";
import frMonitoring from "./fr/monitoring.json";
import frAdmin from "./fr/admin.json";
import enCommon from "./en/common.json";
import enDashboard from "./en/dashboard.json";
import enApplications from "./en/applications.json";
import enClients from "./en/clients.json";
import enReview from "./en/review.json";
import enModels from "./en/models.json";
import enMonitoring from "./en/monitoring.json";
import enAdmin from "./en/admin.json";

export const resources = {
  fr: {
    translation: {
      common: frCommon,
      dashboard: frDashboard,
      applications: frApplications,
      clients: frClients,
      review: frReview,
      models: frModels,
      monitoring: frMonitoring,
      admin: frAdmin,
    },
  },
  en: {
    translation: {
      common: enCommon,
      dashboard: enDashboard,
      applications: enApplications,
      clients: enClients,
      review: enReview,
      models: enModels,
      monitoring: enMonitoring,
      admin: enAdmin,
    },
  },
} as const;

function resolveInitialLanguage(): string {
  if (typeof localStorage !== "undefined") {
    const stored = localStorage.getItem("cif_lang");
    if (stored === "fr" || stored === "en") return stored;
  }
  if (typeof navigator !== "undefined" && navigator.language?.toLowerCase().startsWith("en")) {
    return "en";
  }
  return "fr";
}

void i18n.use(initReactI18next).init({
  resources,
  lng: resolveInitialLanguage(),
  fallbackLng: "fr",
  interpolation: { escapeValue: false },
  react: { useSuspense: false },
});

export default i18n;
