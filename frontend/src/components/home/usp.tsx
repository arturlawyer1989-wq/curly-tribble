// Четыре преимущества магазина, тексты из прототипа.
const ITEMS = [
  { title: "Подбираем по VIN", text: "Сверяем по каталогу производителя — деталь встанет, а не «должна подойти»" },
  { title: "Оплата при получении", text: "Наличными в пункте выдачи или курьеру. Предоплаты нет" },
  { title: "Свои маршруты", text: "Меловое, Беловодск, Марковка, Сватово — по расписанию" },
  { title: "Оригинал и аналоги", text: "Показываем оба варианта с ценой и сроком — выбираете вы" },
];

export function Usp() {
  return (
    <section className="py-[26px] lg:py-[38px]">
      <div className="wrap">
        <ul className="m-0 grid list-none grid-cols-2 gap-[10px] p-0 lg:grid-cols-4">
          {ITEMS.map((item) => (
            <li key={item.title} className="rounded-md border border-line bg-paper p-[13px]">
              <b className="mb-[3px] block text-[13.5px]">{item.title}</b>
              <span className="block text-[12px] leading-[1.4] text-steel">{item.text}</span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
