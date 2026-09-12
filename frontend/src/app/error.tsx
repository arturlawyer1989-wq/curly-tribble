"use client";

import { useEffect } from "react";

// Ошибка при отрисовке страницы: покупатель видит понятный текст и кнопку, а подробности уходят в консоль.
export default function ErrorPage({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  useEffect(() => {
    console.error("Ошибка страницы:", error);
  }, [error]);

  return (
    <section className="py-[26px] lg:py-[38px]">
      <div className="wrap">
        <div className="rounded-lg border border-line bg-paper p-6 lg:p-10">
          <p className="mb-[9px] font-mono text-[10.5px] font-bold tracking-[0.13em] text-accent uppercase">Ошибка</p>
          <h1 className="m-0 mb-[10px] font-display text-[27px] leading-[1.18] font-bold tracking-[-0.025em] lg:text-[40px]">
            Что-то пошло не так
          </h1>
          <p className="mt-0 mb-5 max-w-[520px] text-steel">
            Мы уже знаем об ошибке. Попробуйте обновить страницу, а если не поможет, позвоните нам.
          </p>
          <button type="button" className="btn" onClick={() => reset()}>
            Обновить страницу
          </button>
        </div>
      </div>
    </section>
  );
}
