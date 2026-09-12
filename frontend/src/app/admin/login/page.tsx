import { LoginForm } from "./login-form";

export const metadata = { title: "Вход" };

const REASONS: Record<string, string> = {
  expired: "Сессия истекла, войдите снова.",
  logout: "Вы вышли из панели управления.",
};

function safeNext(value: string | undefined): string {
  // Возвращаемся только внутрь панели, чтобы нельзя было увести на чужой сайт
  if (value && value.startsWith("/admin") && !value.startsWith("//")) return value;
  return "/admin";
}

export default async function LoginPage({ searchParams }: { searchParams: Promise<{ next?: string; reason?: string }> }) {
  const params = await searchParams;
  return (
    <main className="flex min-h-dvh items-center justify-center px-4 py-8">
      <div className="admin-card w-full max-w-[420px] p-6 lg:p-8">
        <div className="mb-6 flex items-center gap-[9px] font-display text-[15px] font-bold text-white">
          <i className="grid h-7 w-7 place-items-center rounded-[7px] bg-accent font-mono text-[12.5px] font-bold not-italic">Д24</i>
          Панель управления
        </div>
        <h1 className="m-0 mb-5 font-display text-[22px] leading-[1.2] font-bold text-white">Вход для сотрудников</h1>
        <LoginForm nextPath={safeNext(params.next)} initialMessage={REASONS[params.reason ?? ""] ?? ""} />
        <p className="mt-5 mb-0 text-[12.5px] text-[#8a97a2]">
          Забыли пароль? Владелец меняет его командой из README: scripts/create_admin.py с ключом --reset-password.
        </p>
      </div>
    </main>
  );
}
