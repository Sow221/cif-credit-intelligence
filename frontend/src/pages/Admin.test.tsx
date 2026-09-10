import { beforeEach, describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import i18n from "@/locales";
import AdminPage from "./Admin";
import { resetStores, seedAuth, adminUser, officerUser, managerUser } from "@/test/helpers";

function renderPage() {
  return render(<AdminPage />);
}

describe("AdminPage", () => {
  beforeEach(async () => {
    await i18n.changeLanguage("fr");
    resetStores();
    seedAuth(adminUser);
  });

  it("renders the title and the tabs", () => {
    renderPage();
    expect(screen.getByRole("heading", { name: "Administration" })).toBeInTheDocument();
    for (const label of ["Utilisateurs", "Rôles", "Politiques", "Configuration"]) {
      expect(screen.getByRole("tab", { name: label })).toBeInTheDocument();
    }
  });

  it("lists the demo users with their roles for an admin", () => {
    renderPage();
    expect(screen.getByText("Awa Diallo")).toBeInTheDocument();
    expect(screen.getByText("awa.diallo")).toBeInTheDocument();
    expect(screen.getByText("Moussa Sow")).toBeInTheDocument();
    expect(screen.getAllByText("CREDIT_MUTUEL").length).toBeGreaterThan(0);
    expect(screen.getByText("Administrateur")).toBeInTheDocument();
    expect(screen.getByText("Responsable crédit")).toBeInTheDocument();
    expect(screen.getByText("Agent crédit")).toBeInTheDocument();
  });

  it("blocks the users tab content for non-admin roles", () => {
    seedAuth(officerUser);
    renderPage();
    expect(screen.getByText("Vous n'avez pas les permissions nécessaires.")).toBeInTheDocument();
    expect(screen.queryByText("awa.diallo")).not.toBeInTheDocument();
  });

  it("shows the permissions grid on the roles tab", async () => {
    const user = userEvent.setup();
    renderPage();
    await user.click(screen.getByRole("tab", { name: "Rôles" }));
    expect(screen.getByText("users:write")).toBeInTheDocument();
    expect(screen.getByText("decisions:override")).toBeInTheDocument();
  });

  it("shows the policies placeholder", async () => {
    const user = userEvent.setup();
    renderPage();
    await user.click(screen.getByRole("tab", { name: "Politiques" }));
    expect(screen.getByText("Configurer les seuils de décision")).toBeInTheDocument();
  });

  it("uses the localized role label for a manager tab title", async () => {
    const user = userEvent.setup();
    seedAuth(managerUser);
    renderPage();
    await user.click(screen.getByRole("tab", { name: "Rôles" }));
    expect(screen.getByText("Responsable crédit")).toBeInTheDocument();
  });
});
