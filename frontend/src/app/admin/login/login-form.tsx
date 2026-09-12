"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";

type Props = { nextPath: string; initialMessage: string };

// Форма входа: логин и пароль уходят на бэкенд, он ставит cookie и возвращает сотрудника
export function LoginForm({ nextPath, initialMessage }: Props) {
  const [login, setLogin] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(initialMessage);
  const [pending, setPending] = useState(false);
  const router = useRouter();

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPending(true);
    setError("");
    try {
      const response = await fetch("/api/v1/admin/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-Requested-With": "XMLHttpRequest" },
        body: JSON.stringify({ login, password }),
        credentials: "same-origin",
      });
      if (response.ok) {
        // Полное обновление маршрута: proxy.ts заново проверит cookie и откроет панель
        router.replace(nextPath);
        router.refresh();
        return;
      }
      let message = "Не удалось войти. Попробуйте ещё раз.";
      try {
        const body = (await response.json()) as { error?: { message?: string } };
        if (body.error?.message) message = body.error.message;
      } catch {
        // тело не JSON, оставляем общее сообщение
      }
      setError(message);
    } catch {
      setError("Нет связи с сервером. Проверьте подключение и попробуйте снова.");
    } finally {
      setPending(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="grid gap-4" noValidate>
      <label className="block">
        <span className="mb-[7px] block text-[13px] font-semibold">Логин</span>
        <input className="admin-input" name="login" autoComplete="username" value={login} onChange={(e) => setLogin(e.target.value)} required />
      </label>
      <label className="block">
        <span className="mb-[7px] block text-[13px] font-semibold">Пароль</span>
        <input className="admin-input" name="password" type="password" autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)} required />
      </label>
      {error && (
        <p role="alert" data-testid="login-error" className="admin-error m-0">
          {error}
        </p>
      )}
      <button type="submit" className="btn w-full" disabled={pending || !login || !password}>
        {pending ? "Проверяем…" : "Войти"}
      </button>
    </form>
  );
}
