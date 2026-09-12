import Link from "next/link";

export const metadata = { title: "Страница не найдена" };

export default function NotFound() {
  return (
    <section className="py-[26px] lg:py-[38px]">
      <div className="wrap">
        <div className="rounded-lg border border-line bg-paper p-6 lg:p-10">
          <p className="mb-[9px] font-mono text-[10.5px] font-bold tracking-[0.13em] text-accent uppercase">Ошибка 404</p>
          <h1 className="m-0 mb-[10px] font-display text-[27px] leading-[1.18] font-bold tracking-[-0.025em] lg:text-[40px]">
            Такой страницы нет
          </h1>
          <p className="mt-0 mb-5 max-w-[520px] text-steel">
            Возможно, ссылка устарела или в адресе опечатка. Вернитесь на главную и начните с поиска детали.
          </p>
          <Link href="/" className="btn">
            На главную
          </Link>
        </div>
      </div>
    </section>
  );
}
