import type { Metadata } from "next";

export const metadata: Metadata = {
  title: { default: "Панель управления", template: "%s · Панель управления" },
  robots: { index: false, follow: false },
};

// Общая тёмная подложка панели управления, как в прототипе
export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return <div className="admin">{children}</div>;
}
