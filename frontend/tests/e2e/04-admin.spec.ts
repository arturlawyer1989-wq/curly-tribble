import { expect, test } from "@playwright/test";

// Панель управления: вход, разделы, выход, чужой токен.
// Логин и пароль владельца передаются через E2E_ADMIN_LOGIN и E2E_ADMIN_PASSWORD (значения из .env).
const LOGIN = process.env.E2E_ADMIN_LOGIN ?? "owner";
const PASSWORD = process.env.E2E_ADMIN_PASSWORD ?? "";
const BASE_URL = process.env.E2E_BASE_URL ?? "http://localhost:8080";

test.describe("панель управления", () => {
  test.skip(!PASSWORD, "Задайте E2E_ADMIN_LOGIN и E2E_ADMIN_PASSWORD, чтобы проверить вход в панель");

  test("неверный пароль показывает ошибку по-русски", async ({ page }) => {
    await page.goto("/admin/login");
    await page.getByLabel("Логин").fill(LOGIN);
    await page.getByLabel("Пароль").fill("неверный-пароль");
    await page.getByRole("button", { name: "Войти" }).click();
    await expect(page.getByTestId("login-error")).toHaveText("Неверный логин или пароль.");
    await expect(page).toHaveURL(/\/admin\/login/);
    await page.screenshot({ path: "test-results/screenshots/admin-login-error-360.png", fullPage: true });
  });

  test("верный пароль открывает панель, разделы работают, выход закрывает панель", async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.goto("/admin/login");
    await page.getByLabel("Логин").fill(LOGIN);
    await page.getByLabel("Пароль").fill(PASSWORD);
    await page.getByRole("button", { name: "Войти" }).click();
    await expect(page).toHaveURL(/\/admin$/);
    await expect(page.getByRole("heading", { level: 1 })).toHaveText("Сводка");
    await expect(page.getByTestId("admin-user")).toContainText("Владелец");
    await page.screenshot({ path: "test-results/screenshots/admin-home-1440.png", fullPage: true });

    for (const [title, path] of [
      ["Заказы", "/admin/orders"],
      ["Клиенты", "/admin/customers"],
      ["Доставка", "/admin/delivery"],
      ["Настройки", "/admin/settings"],
    ] as const) {
      await page.getByRole("navigation", { name: "Разделы панели" }).getByRole("link", { name: title, exact: true }).click();
      await expect(page).toHaveURL(new RegExp(`${path}$`));
      await expect(page.getByRole("heading", { level: 1 })).toHaveText(title);
      // У разделов с данными виден живой счётчик, у настроек только пояснение этапа
      if (title === "Настройки") {
        await expect(page.getByText("появится на этапе")).toBeVisible();
      } else {
        await expect(page.getByText("Записей в базе:")).toBeVisible();
      }
    }

    await page.getByRole("button", { name: "Выйти" }).click();
    await expect(page).toHaveURL(/\/admin\/login/);
    await expect(page.getByTestId("login-error")).toHaveText("Вы вышли из панели управления.");

    const closed = await page.goto("/admin");
    expect(closed?.status()).toBe(401);
    await expect(page.getByRole("heading", { level: 1 })).toHaveText("Вход для сотрудников");
  });

  test("чужой или истёкший токен в /admin/* даёт 401", async ({ browser, request }) => {
    const context = await browser.newContext();
    await context.addCookies([{ name: "d24_access", value: "foreign-token-of-someone-else", url: BASE_URL }]);
    const page = await context.newPage();
    const response = await page.goto("/admin/orders");
    expect(response?.status()).toBe(401);
    await expect(page.getByRole("heading", { level: 1 })).toHaveText("Вход для сотрудников");
    await expect(page.getByTestId("login-error")).toHaveText("Сессия истекла, войдите снова.");
    await page.screenshot({ path: "test-results/screenshots/admin-401-360.png", fullPage: true });
    await context.close();

    const api = await request.get("/api/v1/admin/overview", { headers: { Authorization: "Bearer foreign-token-of-someone-else" } });
    expect(api.status()).toBe(401);
    const body = await api.json();
    expect(body.error.code).toBe("unauthorized");
    expect(body.error.message).toMatch(/[а-яА-Я]/);

    const noToken = await request.get("/api/v1/admin/auth/me");
    expect(noToken.status()).toBe(401);
  });
});
