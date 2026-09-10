import { beforeEach, describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import i18n from "@/locales";
import { UserDropdown } from "./UserDropdown";
import { resetStores, seedAuth, adminUser, managerUser } from "@/test/helpers";
import { useAuthStore } from "@/store/auth";

function renderDropdown() {
  return render(
    <MemoryRouter initialEntries={["/dashboard"]}>
      <Routes>
        <Route path="/dashboard" element={<UserDropdown />} />
        <Route path="/admin" element={<div>admin-page</div>} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("UserDropdown", () => {
  beforeEach(async () => {
    await i18n.changeLanguage("fr");
    resetStores();
    seedAuth(adminUser);
  });

  it("renders nothing when no user is logged in", () => {
    resetStores();
    renderDropdown();
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });

  it("opens a menu with the user identity and logout action", async () => {
    const user = userEvent.setup();
    renderDropdown();
    await user.click(screen.getByRole("button", { name: "Profil utilisateur" }));
    expect(screen.getByText("Admin Diallo — Administrateur")).toBeInTheDocument();
    expect(screen.getByRole("menuitem", { name: "Déconnexion" })).toBeInTheDocument();
  });

  it("uses the localized role label", async () => {
    const user = userEvent.setup();
    seedAuth(managerUser);
    renderDropdown();
    await user.click(screen.getByRole("button", { name: "Profil utilisateur" }));
    expect(screen.getByText("Manager Sow — Responsable crédit")).toBeInTheDocument();
  });

  it("navigates to the admin page when the profile item is selected", async () => {
    const user = userEvent.setup();
    renderDropdown();
    await user.click(screen.getByRole("button", { name: "Profil utilisateur" }));
    await user.click(screen.getByRole("menuitem", { name: "Admin Diallo — Administrateur" }));
    expect(await screen.findByText("admin-page")).toBeInTheDocument();
  });

  it("signs the user out when logout is selected", async () => {
    const user = userEvent.setup();
    renderDropdown();
    await user.click(screen.getByRole("button", { name: "Profil utilisateur" }));
    await user.click(screen.getByRole("menuitem", { name: "Déconnexion" }));
    expect(useAuthStore.getState().user).toBeNull();
    expect(screen.queryByRole("button", { name: "Profil utilisateur" })).not.toBeInTheDocument();
  });
});
