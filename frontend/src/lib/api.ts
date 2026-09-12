// Запросы к бэкенду с сервера Next.js. Адрес приходит из переменной BACKEND_INTERNAL_URL.
import { unstable_rethrow } from "next/navigation";
import { cache } from "react";

export type Shop = {
  name: string;
  short_name: string;
  city: string;
  phone: string;
  phone_href: string;
  address: string;
  work_hours: string;
  legal_name: string;
  inn: string;
  email: string;
};

// Значения на случай, если бэкенд не ответил: сайт всё равно должен открыться
export const DEFAULT_SHOP: Shop = {
  name: "ДЕТАЛЬ 24",
  short_name: "Д24",
  city: "Старобельск",
  phone: "",
  phone_href: "",
  address: "",
  work_hours: "",
  legal_name: "",
  inn: "",
  email: "",
};

export type ShopResult = { shop: Shop; ok: boolean };

const BACKEND_URL = process.env.BACKEND_INTERNAL_URL ?? "http://backend:8000";
const REQUEST_TIMEOUT_MS = 3000;

// cache() из React: в пределах одного запроса страницы данные читаются один раз,
// даже если их просят и шапка, и подвал, и сама страница.
export const getShop = cache(async (): Promise<ShopResult> => {
  try {
    const response = await fetch(`${BACKEND_URL}/api/v1/shop`, {
      cache: "no-store",
      signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
    });
    if (!response.ok) {
      console.error(`Бэкенд ответил ошибкой ${response.status} на запрос настроек магазина`);
      return { shop: DEFAULT_SHOP, ok: false };
    }
    const data = (await response.json()) as Partial<Shop>;
    return { shop: { ...DEFAULT_SHOP, ...data }, ok: true };
  } catch (error) {
    // Служебные ошибки Next.js (переход на динамический рендер, редиректы) обрабатывает сам Next
    unstable_rethrow(error);
    console.error("Не удалось получить настройки магазина:", error instanceof Error ? error.message : error);
    return { shop: DEFAULT_SHOP, ok: false };
  }
});
