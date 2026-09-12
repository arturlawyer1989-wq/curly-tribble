import { expect, test } from "@playwright/test";

// Проверки nginx: маршрутизация к бэкенду и ограничение частоты запросов

for (const path of ["/health", "/api/v1/health"]) {
  test(`состояние сервисов доступно через nginx по адресу ${path}`, async ({ request }) => {
    const response = await request.get(path);
    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(["ok", "degraded"]).toContain(body.status);
    expect(body.app.status).toBe("ok");
    expect(body.db.status).toBe("ok");
    expect(body.redis.status).toBe("ok");
  });
}

test("robots.txt отдаётся и запрещает индексацию API", async ({ request }) => {
  const response = await request.get("/robots.txt");
  expect(response.status()).toBe(200);
  expect(await response.text()).toContain("Disallow: /api/");
});

test("шквал запросов к API ограничивается ответом 429 на русском", async ({ request }) => {
  const responses = await Promise.all(Array.from({ length: 60 }, () => request.get("/api/v1/health")));
  const limited = responses.filter((response) => response.status() === 429);
  expect(limited.length).toBeGreaterThan(0);
  const body = await limited[0].json();
  expect(body.error.code).toBe("too_many_requests");
  expect(body.error.message).toContain("Слишком много запросов");
});
