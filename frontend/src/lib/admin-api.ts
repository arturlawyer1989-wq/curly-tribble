// Запросы к панели управления с сервера Next.js: токен берётся из cookie или из заголовка,
// который proxy.ts подставляет после тихого обновления сессии.
import { cookies, headers } from "next/headers";

const BACKEND_URL = process.env.BACKEND_INTERNAL_URL ?? "http://backend:8000";
const REQUEST_TIMEOUT_MS = 5000;

export type { AdminUser, Overview, OverviewSection } from "@/lib/admin-sections";

export type AdminResult<T> = { ok: true; data: T } | { ok: false; status: number };

export async function adminFetch<T>(path: string): Promise<AdminResult<T>> {
  const headerStore = await headers();
  const cookieStore = await cookies();
  const access = headerStore.get("x-d24-access") ?? cookieStore.get("d24_access")?.value ?? "";
  try {
    const response = await fetch(`${BACKEND_URL}${path}`, {
      headers: access ? { authorization: `Bearer ${access}` } : {},
      cache: "no-store",
      signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
    });
    if (!response.ok) return { ok: false, status: response.status };
    return { ok: true, data: (await response.json()) as T };
  } catch (error) {
    console.error(`Панель: не удалось запросить ${path}:`, error instanceof Error ? error.message : error);
    return { ok: false, status: 0 };
  }
}
