"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

export function LogoutButton() {
  const [pending, setPending] = useState(false);
  const router = useRouter();

  async function onClick() {
    setPending(true);
    try {
      await fetch("/api/v1/admin/auth/logout", { method: "POST", headers: { "X-Requested-With": "XMLHttpRequest" }, credentials: "same-origin" });
    } catch (error) {
      console.error("Не удалось завершить сессию на сервере:", error instanceof Error ? error.message : error);
    }
    router.replace("/admin/login?reason=logout");
    router.refresh();
  }

  return (
    <button type="button" onClick={onClick} disabled={pending} className="admin-tab">
      {pending ? "Выходим…" : "Выйти"}
    </button>
  );
}
