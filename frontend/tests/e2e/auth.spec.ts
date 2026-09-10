import { expect, test } from "@playwright/test";
import { login, mockBackend } from "./api.mock";

test.describe("authentication", () => {
  test("redirects unauthenticated users to the login page", async ({ page }) => {
    await mockBackend(page);
    await page.goto("/");
    await page.waitForURL("**/login");
    await expect(page.getByTestId("submit")).toBeVisible();
  });

  test("redirects authenticated users away from login", async ({ page }) => {
    await mockBackend(page);
    await page.goto("/login");
    await page.getByTestId("username").fill("awa.diallo");
    await page.getByTestId("password").fill("secret");
    await page.getByTestId("submit").click();
    await page.waitForURL("**/dashboard");
    await page.goto("/login");
    await page.waitForURL("**/dashboard");
  });

  test("logs in and lands on the dashboard", async ({ page }) => {
    await login(page);
    await expect(page).toHaveURL(/\/dashboard$/);
    await expect(page.getByText(/^Bonjour/).first()).toBeVisible();
  });

  test("shows the server error returned by the API", async ({ page }) => {
    await mockBackend(page);
    await page.route("**/api/v1/auth/login", (route) =>
      route.fulfill({
        status: 401,
        contentType: "application/json",
        body: JSON.stringify({
          error: { code: "INVALID_CREDENTIALS", message: "Identifiants invalides" },
        }),
      }),
    );
    await page.goto("/login");
    await page.getByTestId("username").fill("wrong");
    await page.getByTestId("password").fill("wrong");
    await page.getByTestId("submit").click();
    await expect(page.getByRole("alert")).toBeVisible();
    await expect(page.getByText("Identifiants invalides")).toBeVisible();
  });
});