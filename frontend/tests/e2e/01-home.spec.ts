import { expect, test } from "@playwright/test";

// Главная страница на трёх ширинах: 360 (телефон), 768 (планшет), 1440 (компьютер)
const WIDTHS = [360, 768, 1440];

for (const width of WIDTHS) {
  test(`главная открывается на ширине ${width}`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    const failed: string[] = [];
    page.on("response", (response) => {
      if (response.status() >= 400) failed.push(`${response.status()} ${response.url()}`);
    });

    const response = await page.goto("/");
    expect(response?.status()).toBe(200);
    await page.waitForLoadState("networkidle");

    // Шапка, заголовок, преимущества и подвал на месте
    await expect(page.getByRole("banner")).toContainText("ДЕТАЛЬ 24");
    await expect(page.getByRole("heading", { level: 1 })).toContainText("Запчасти для иномарок");
    await expect(page.getByText("Оплата при получении")).toBeVisible();
    await expect(page.getByRole("contentinfo")).toContainText("Наличными при получении");
    // Блок этапа каркаса: слова «проект запущен» и живое состояние сервисов
    await expect(page.getByRole("heading", { level: 2, name: /проект запущен/ })).toBeVisible();
    await expect(page.getByText("База данных:", { exact: false })).toBeVisible();

    // Ни один запрос страницы не закончился ошибкой (шрифты, стили, скрипты)
    expect(failed).toEqual([]);

    // Нет горизонтальной прокрутки
    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
    );
    expect(overflow).toBeLessThanOrEqual(0);

    // Кнопки и ссылки в шапке не меньше 44 пикселей в высоту
    const small = await page.evaluate(() =>
      Array.from(document.querySelectorAll("button, header a, a.btn"))
        .map((el) => ({ text: el.textContent?.trim() ?? "", height: el.getBoundingClientRect().height, width: el.getBoundingClientRect().width }))
        .filter((item) => item.width > 0 && item.height > 0 && item.height < 44),
    );
    expect(small).toEqual([]);

    // Шрифты прототипа действительно загрузились
    const fonts = await page.evaluate(async () => {
      await document.fonts.ready;
      return {
        display: document.fonts.check('700 20px "Unbounded"'),
        text: document.fonts.check('400 16px "Golos Text"'),
      };
    });
    expect(fonts).toEqual({ display: true, text: true });

    await page.screenshot({ path: `test-results/screenshots/home-${width}.png`, fullPage: true });
  });
}
