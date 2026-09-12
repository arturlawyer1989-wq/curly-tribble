import type { MetadataRoute } from "next";

// Правила для поисковых роботов: сайт открыт для индексации, служебные адреса закрыты.
export default function robots(): MetadataRoute.Robots {
  return {
    rules: { userAgent: "*", allow: "/", disallow: ["/api/"] },
  };
}
