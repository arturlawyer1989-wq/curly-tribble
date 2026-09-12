import type { Metadata } from "next";
import { headers } from "next/headers";

import "@fontsource/golos-text/400.css";
import "@fontsource/golos-text/500.css";
import "@fontsource/golos-text/600.css";
import "@fontsource/golos-text/700.css";
import "@fontsource/unbounded/600.css";
import "@fontsource/unbounded/700.css";
import "@fontsource/jetbrains-mono/500.css";
import "@fontsource/jetbrains-mono/700.css";
import "./globals.css";

import { DegradedBanner } from "@/components/layout/degraded-banner";
import { Footer } from "@/components/layout/footer";
import { Header } from "@/components/layout/header";
import { getShop } from "@/lib/api";

export async function generateMetadata(): Promise<Metadata> {
  const { shop } = await getShop();
  return {
    title: {
      default: `${shop.name} — запчасти для иномарок в Старобельске и районе`,
      template: `%s · ${shop.name}`,
    },
    description:
      "Оригинальные автозапчасти и проверенные аналоги для иномарок. Подбор по VIN, схемы узлов, оплата при получении, доставка по северным районам ЛНР.",
    openGraph: {
      title: `${shop.name} — запчасти для иномарок`,
      description: "Оригинал и аналоги, подбор по VIN, оплата наличными при получении.",
      type: "website",
      locale: "ru_RU",
    },
  };
}

export const viewport = {
  themeColor: "#0B3B52",
  width: "device-width",
  initialScale: 1,
};

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  // Панель управления живёт в своей оболочке без витринной шапки и подвала (заголовок ставит proxy.ts)
  const area = (await headers()).get("x-d24-area");
  if (area === "admin") {
    return (
      <html lang="ru">
        <body className="min-h-dvh">{children}</body>
      </html>
    );
  }
  const { shop, ok } = await getShop();
  return (
    <html lang="ru">
      <body className="flex min-h-dvh flex-col">
        <Header shop={shop} />
        {!ok && <DegradedBanner />}
        <main className="flex-1">{children}</main>
        <Footer shop={shop} />
      </body>
    </html>
  );
}
