import { expect, test } from "@playwright/test";
import { login } from "./api.mock";

test.describe("navigation", () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  test("sidebar links navigate through the main sections", async ({ page }) => {
    const nav: Array<[string, string]> = [
      ["Demandes", "/applications"],
      ["Clients", "/clients"],
      ["Revue", "/review"],
      ["Modèles", "/models"],
      ["Monitoring", "/monitoring"],
      ["Administration", "/admin"],
      ["Tableau de bord", "/dashboard"],
    ];

    for (const [label, url] of nav) {
      await page.getByRole("link", { name: label }).click();
      await expect(page).toHaveURL(new RegExp(url.replace("/", "\\/") + "$"));
    }
  });

  test("page headings render for each protected section", async ({ page }) => {
    const expectations: Array<[string, string]> = [
      ["/applications", "Demandes"],
      ["/clients", "Clients"],
      ["/review", "File de revue"],
      ["/models", "Modèles"],
      ["/monitoring", "Monitoring"],
      ["/admin", "Administration"],
    ];
    for (const [url, heading] of expectations) {
      await page.goto(url);
      await expect(
        page.getByRole("main").getByRole("heading", { level: 1, name: heading }),
      ).toBeVisible();
    }
  });
});