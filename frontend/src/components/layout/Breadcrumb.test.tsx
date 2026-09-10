import { beforeEach, describe, expect, it } from "vitest";
import { render, screen, within } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import i18n from "@/locales";
import { Breadcrumb } from "./Breadcrumb";

function renderAt(path: string) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <Breadcrumb />
    </MemoryRouter>,
  );
}

function crumbsText() {
  const nav = screen.getByRole("navigation", { name: "Fil d'Ariane" });
  return within(nav).getByText((content) => content.trim().length > 0).textContent;
}

describe("Breadcrumb", () => {
  beforeEach(async () => {
    await i18n.changeLanguage("fr");
  });

  it("renders the dashboard crumb and greeting title", () => {
    renderAt("/dashboard");
    expect(crumbsText()).toBe("Tableau de bord");
    expect(screen.getByRole("heading", { name: "Bonjour" })).toBeInTheDocument();
  });

  it("renders the applications crumb and title", () => {
    renderAt("/applications");
    expect(crumbsText()).toBe("Demandes");
    expect(screen.getByRole("heading", { name: "Demandes" })).toBeInTheDocument();
  });

  it("renders an ellipsis crumb on application detail without a page title", () => {
    renderAt("/applications/app-1");
    expect(crumbsText()).toBe("Demandes / …");
    expect(screen.queryByRole("heading")).not.toBeInTheDocument();
  });

  it("renders the clients crumb and title", () => {
    renderAt("/clients");
    expect(crumbsText()).toBe("Clients");
    expect(screen.getByRole("heading", { name: "Clients" })).toBeInTheDocument();
  });

  it("renders an ellipsis crumb on client detail without a page title", () => {
    renderAt("/clients/c1");
    expect(crumbsText()).toBe("Clients / …");
    expect(screen.queryByRole("heading")).not.toBeInTheDocument();
  });

  it("renders the monitoring crumb title", () => {
    renderAt("/monitoring");
    expect(crumbsText()).toBe("Monitoring");
    expect(screen.getByRole("heading", { name: "Monitoring" })).toBeInTheDocument();
  });

  it("falls back to the app name on unknown routes", () => {
    renderAt("/unknown");
    expect(crumbsText()).toBe("Adaptive Credit");
    expect(screen.queryByRole("heading")).not.toBeInTheDocument();
  });
});
