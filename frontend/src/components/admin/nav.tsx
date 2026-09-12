"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { SECTIONS } from "@/lib/admin-sections";

// Вкладки разделов, как в прототипе: активная белая, остальные полупрозрачные
export function AdminNav() {
  const pathname = usePathname();
  return (
    <nav aria-label="Разделы панели" className="flex gap-[6px] overflow-x-auto py-[13px] [scrollbar-width:none]">
      <Link href="/admin" className={`admin-tab ${pathname === "/admin" ? "on" : ""}`}>
        Сводка
      </Link>
      {SECTIONS.map((section) => {
        const href = `/admin/${section.key}`;
        const active = pathname === href || pathname.startsWith(`${href}/`);
        return (
          <Link key={section.key} href={href} className={`admin-tab ${active ? "on" : ""}`}>
            {section.title}
          </Link>
        );
      })}
    </nav>
  );
}
