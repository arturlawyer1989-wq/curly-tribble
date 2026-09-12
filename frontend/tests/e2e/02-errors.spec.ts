import { expect, test } from "@playwright/test";

test("несуществующая страница показывает русскую 404 и ведёт на главную", async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 800 });
  const response = await page.goto("/takoy-stranitsy-net");
  expect(response?.status()).toBe(404);
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Такой страницы нет");
  await expect(page.getByRole("banner")).toContainText("ДЕТАЛЬ 24");
  await page.screenshot({ path: "test-results/screenshots/not-found-360.png", fullPage: true });
  await page.getByRole("link", { name: "На главную", exact: true }).click();
  await expect(page).toHaveURL(/\/$/);
  await expect(page.getByRole("heading", { level: 1 })).toContainText("Запчасти для иномарок");
});

test("неизвестный адрес API отдаёт ошибку в едином формате на русском", async ({ request }) => {
  const response = await request.get("/api/v1/net-takogo");
  expect(response.status()).toBe(404);
  const body = await response.json();
  expect(body.error.code).toBe("not_found");
  expect(body.error.message).toMatch(/[а-яА-Я]/);
});
