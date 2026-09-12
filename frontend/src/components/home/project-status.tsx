import type { Health, Shop } from "@/lib/api";

type Props = { shop: Shop; health: Health | null };

const LABELS: Array<[keyof Pick<Health, "app" | "db" | "redis" | "worker">, string]> = [
  ["app", "Приложение"],
  ["db", "База данных"],
  ["redis", "Redis"],
  ["worker", "Фоновый воркер"],
];

// Блок этапа каркаса: подтверждает, что проект запущен, и показывает живое состояние сервисов.
// На этапе каталога его место займут товары.
export function ProjectStatus({ shop, health }: Props) {
  return (
    <section className="pb-[26px] lg:pb-[38px]">
      <div className="wrap">
        <div className="rounded-lg border border-line bg-paper p-4 lg:p-6">
          <p className="mb-[9px] font-mono text-[10.5px] font-bold tracking-[0.13em] text-accent uppercase">Этап 1 из 7: каркас</p>
          <h2 className="m-0 mb-[10px] font-display text-[20px] leading-[1.2] font-bold tracking-[-0.015em] lg:text-[25px]">
            {shop.name} — проект запущен
          </h2>
          {health ? (
            <ul className="m-0 grid list-none grid-cols-1 gap-2 p-0 sm:grid-cols-2">
              {LABELS.map(([key, label]) => {
                const item = health[key];
                const good = item.status === "ok";
                return (
                  <li key={key} className="flex items-start gap-[9px] text-[13.5px] leading-[1.4]">
                    <span
                      aria-hidden="true"
                      className={`mt-[6px] h-2 w-2 flex-none rounded-full ${good ? "bg-ok" : "bg-warn"}`}
                    />
                    <span>
                      <b>{label}:</b> {item.message}
                    </span>
                  </li>
                );
              })}
            </ul>
          ) : (
            <p className="m-0 text-[13.5px] text-steel">Состояние сервисов сейчас недоступно. Обновите страницу через минуту.</p>
          )}
          <p className="mt-3 mb-0 text-[12.5px] text-steel">
            Каталог, поиск, корзина и личный кабинет появятся на следующих этапах.
          </p>
        </div>
      </div>
    </section>
  );
}
