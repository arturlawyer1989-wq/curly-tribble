// Полоса под шапкой, если бэкенд не ответил: покупатель видит понятное сообщение, а не пустой экран.
export function DegradedBanner() {
  return (
    <div role="status" className="bg-warn-bg text-[#6b4310]">
      <div className="wrap py-3 text-[13px] leading-[1.45]">
        Сайт временно работает в ограниченном режиме: часть данных сейчас недоступна. Попробуйте обновить страницу
        через минуту.
      </div>
    </div>
  );
}
