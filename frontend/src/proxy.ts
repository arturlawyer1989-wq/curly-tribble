import { NextResponse, type NextRequest } from "next/server";

// Охрана панели управления: без действующего входа страницы /admin/* не открываются.
// Токен проверяет бэкенд; просроченный токен доступа тихо обновляется по сессии.
const BACKEND_URL = process.env.BACKEND_INTERNAL_URL ?? "http://backend:8000";
const ACCESS_COOKIE = "d24_access";
const REFRESH_COOKIE = "d24_refresh";

async function tokenIsValid(access: string): Promise<boolean> {
  try {
    const response = await fetch(`${BACKEND_URL}/api/v1/admin/auth/me`, {
      headers: { authorization: `Bearer ${access}` },
      cache: "no-store",
      signal: AbortSignal.timeout(4000),
    });
    return response.ok;
  } catch (error) {
    console.error("Не удалось проверить вход в панель:", error instanceof Error ? error.message : error);
    return false;
  }
}

function cookieValue(setCookies: string[], name: string): string | null {
  for (const raw of setCookies) {
    if (raw.startsWith(`${name}=`)) return raw.slice(name.length + 1).split(";")[0];
  }
  return null;
}

export async function proxy(request: NextRequest) {
  const { pathname, search } = request.nextUrl;
  const requestHeaders = new Headers(request.headers);
  requestHeaders.set("x-d24-area", "admin");

  if (pathname === "/admin/login") {
    return NextResponse.next({ request: { headers: requestHeaders } });
  }

  const access = request.cookies.get(ACCESS_COOKIE)?.value;
  const refresh = request.cookies.get(REFRESH_COOKIE)?.value;

  if (access && (await tokenIsValid(access))) {
    return NextResponse.next({ request: { headers: requestHeaders } });
  }

  if (refresh) {
    try {
      const refreshed = await fetch(`${BACKEND_URL}/api/v1/admin/auth/refresh`, {
        method: "POST",
        headers: { cookie: `${REFRESH_COOKIE}=${refresh}`, "x-requested-with": "XMLHttpRequest" },
        cache: "no-store",
        signal: AbortSignal.timeout(4000),
      });
      if (refreshed.ok) {
        const setCookies = refreshed.headers.getSetCookie();
        const newAccess = cookieValue(setCookies, ACCESS_COOKIE);
        if (newAccess) requestHeaders.set("x-d24-access", newAccess);
        const response = NextResponse.next({ request: { headers: requestHeaders } });
        for (const cookie of setCookies) response.headers.append("set-cookie", cookie);
        return response;
      }
    } catch (error) {
      console.error("Не удалось обновить сессию панели:", error instanceof Error ? error.message : error);
    }
  }

  // Не вошёл или сессия истекла: показываем форму входа и отвечаем кодом 401
  const loginUrl = new URL("/admin/login", request.url);
  loginUrl.searchParams.set("next", pathname + search);
  loginUrl.searchParams.set("reason", access || refresh ? "expired" : "login");
  const response = NextResponse.rewrite(loginUrl, { status: 401, request: { headers: requestHeaders } });
  response.cookies.delete(ACCESS_COOKIE);
  response.cookies.delete(REFRESH_COOKIE);
  return response;
}

export const config = {
  matcher: ["/admin/:path*"],
};
