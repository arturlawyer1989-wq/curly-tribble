import Link from "next/link";

import { adminFetch, type Overview } from "@/lib/admin-api";
import { SECTIONS } from "@/lib/admin-sections";

export const metadata = { title: "Сводка" };

const STATUS_TITLES: Record<string, string> = {
  new: "Новые",
  processing: "В обработке",
  confirmed: "Цена подтверждена",
  ordered: "В пути",
  arrived: "Ожидают выдачи",
  issued: "Выданы",
  refused: "Невыкуп",
  cancelled: "Отменены",
};

export default async function AdminHome() {
  const result = await adminFetch<Overview>("/api/v1/admin/overview");
  if (!result.ok) {
    return <p className="admin-error mt-4">Не удалось получить сводку. Обновите страницу через минуту.</p>;
  }
  const counts = Object.fromEntries(result.data.sections.map((s) => [s.key, s.count]));
  const kpi = [
    { label: "Новых заказов", value: result.data.orders_by_status.new ?? 0, warn: (result.data.orders_by_status.new ?? 0) > 0 },
    { label: "Заказов всего", value: counts.orders ?? 0 },
    { label: "Товаров в каталоге", value: counts.products ?? 0 },
    { label: "Клиентов", value: counts.customers ?? 0 },
  ];
  return (
    <>
      <h1 className="mt-2 mb-4 font-display text-[22px] font-bold text-white">Сводка</h1>
      <div className="mb-[18px] grid grid-cols-2 gap-[10px] lg:grid-cols-4">
        {kpi.map((item) => (
          <div key={item.label} className="admin-card p-[14px]">
            <b className={`block font-mono text-[23px] leading-[1.15] ${item.warn ? "text-[#ffb37a]" : "text-white"}`}>{item.value}</b>
            <span className="text-[11.5px] text-[#8a97a2]">{item.label}</span>
          </div>
        ))}
      </div>
      <div className="admin-card mb-[18px] px-[14px] py-[6px]">
        <table className="w-full border-collapse text-[13px]">
          <thead>
            <tr>
              <th className="admin-th">Раздел</th>
              <th className="admin-th">Записей</th>
              <th className="admin-th">Что здесь будет</th>
            </tr>
          </thead>
          <tbody>
            {SECTIONS.map((section) => (
              <tr key={section.key}>
                <td className="admin-td">
                  <Link href={`/admin/${section.key}`} className="text-white hover:underline">
                    {section.title}
                  </Link>
                </td>
                <td className="admin-td font-mono">{counts[section.key] ?? "—"}</td>
                <td className="admin-td text-[#b4c0c9]">
                  {section.description} Этап {section.stage}.
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="admin-card px-[14px] py-[6px]">
        <table className="w-full border-collapse text-[13px]">
          <thead>
            <tr>
              <th className="admin-th">Статус заказа</th>
              <th className="admin-th">Сколько</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(result.data.orders_by_status).map(([status, count]) => (
              <tr key={status}>
                <td className="admin-td">{STATUS_TITLES[status] ?? status}</td>
                <td className="admin-td font-mono">{count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
