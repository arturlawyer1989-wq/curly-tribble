import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Сборка в отдельную папку standalone: в Docker-образ попадает только нужное
  output: "standalone",
  reactStrictMode: true,
  poweredByHeader: false,
};

export default nextConfig;
