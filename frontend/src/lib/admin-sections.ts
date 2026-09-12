// Общие для сервера и браузера описания панели: типы, роли, разделы. Без серверных импортов.
export type AdminUser = { id: number; login: string; full_name: string; role: "owner" | "manager"; is_active: boolean; last_login_at: string | null };
export type OverviewSection = { key: string; title: string; count: number };
export type Overview = { sections: OverviewSection[]; orders_by_status: Record<string, number> };

export const ROLE_TITLES: Record<AdminUser["role"], string> = { owner: "Владелец", manager: "Менеджер" };

// Разделы панели: на каком этапе каждый получает содержимое
export const SECTIONS = [
  { key: "orders", title: "Заказы", description: "Новые заказы, статусы, подтверждение цены, история.", stage: 4 },
  { key: "vin-requests", title: "Заявки по VIN", description: "Ручной подбор по VIN: заявки, ответы, шаблоны VIN.", stage: 4 },
  { key: "products", title: "Товары и цены", description: "Каталог, остатки, закупочные и розничные цены, фото.", stage: 5 },
  { key: "suppliers", title: "Поставщики", description: "Поставщики и источники их прайсов.", stage: 5 },
  { key: "imports", title: "Импорт прайсов", description: "Шаблоны колонок и журнал загрузок.", stage: 5 },
  { key: "cross-references", title: "Кросс-номера", description: "Соответствия артикулов и аналоги.", stage: 5 },
  { key: "pricing", title: "Наценки", description: "Общая наценка и правила по группам, брендам, поставщикам.", stage: 5 },
  { key: "customers", title: "Клиенты", description: "Покупатели, репутация, чёрный список.", stage: 4 },
  { key: "delivery", title: "Доставка", description: "Зоны, цены и расписание маршрутов.", stage: 4 },
  { key: "receiving", title: "Приёмка", description: "Приёмка по штрихкоду, ячейки, накладные.", stage: 6 },
  { key: "reports", title: "Отчёты", description: "Заказано, пришло, выдано, деньги на полке, выгрузка в Excel.", stage: 6 },
  { key: "settings", title: "Настройки", description: "Реквизиты, телефон, адрес, часы работы, тексты страниц, сотрудники.", stage: 4 },
] as const;

export type SectionKey = (typeof SECTIONS)[number]["key"];

// Какой счётчик сводки показывать в разделе
export const SECTION_COUNTER: Partial<Record<SectionKey, string>> = {
  orders: "orders",
  "vin-requests": "vin-requests",
  products: "products",
  suppliers: "suppliers",
  imports: "imports",
  "cross-references": "cross-references",
  pricing: "pricing",
  customers: "customers",
  delivery: "delivery",
};
