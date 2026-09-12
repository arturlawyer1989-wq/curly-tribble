import { defineConfig, devices } from "@playwright/test";

// Сквозные тесты идут против уже запущенного сайта (по умолчанию через nginx на 8080).
// Адрес можно поменять переменной E2E_BASE_URL.
export default defineConfig({
  testDir: "./tests/e2e",
  timeout: 30_000,
  fullyParallel: false,
  workers: 1,
  retries: 0,
  reporter: [["list"]],
  outputDir: "test-results/artifacts",
  use: {
    baseURL: process.env.E2E_BASE_URL ?? "http://localhost:8080",
    trace: "retain-on-failure",
    locale: "ru-RU",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
});
