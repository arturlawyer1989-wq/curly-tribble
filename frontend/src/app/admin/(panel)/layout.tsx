import Link from "next/link";

import { AdminNav } from "@/components/admin/nav";
import { LogoutButton } from "@/components/admin/logout-button";
import { adminFetch, type AdminUser } from "@/lib/admin-api";
import { ROLE_TITLES } from "@/lib/admin-sections";

// Оболочка всех страниц панели: шапка с сотрудником и выходом, вкладки разделов
export default async function PanelLayout({ children }: { children: React.ReactNode }) {
  const me = await adminFetch<AdminUser>("/api/v1/admin/auth/me");
  const user = me.ok ? me.data : null;
  return (
    <div className="wrap pb-8">
      <header className="flex items-center gap-3 border-b border-white/[.08] py-[13px]">
        <Link href="/admin" className="flex min-h-[44px] items-center gap-[9px] font-display text-[15px] font-bold text-white">
          <i className="grid h-7 w-7 place-items-center rounded-[7px] bg-accent font-mono text-[12.5px] font-bold not-italic">Д24</i>
          Панель управления
        </Link>
        <div className="ml-auto flex items-center gap-3">
          {user && (
            <span className="hidden text-[13px] text-[#b4c0c9] sm:inline" data-testid="admin-user">
              {user.full_name || user.login} · {ROLE_TITLES[user.role]}
            </span>
          )}
          <LogoutButton />
        </div>
      </header>
      <AdminNav />
      <main>{children}</main>
    </div>
  );
}
