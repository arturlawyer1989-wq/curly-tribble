// Первый экран главной страницы. Сцена с автомобилями убрана по решению владельца,
// оставлена лёгкая графика шестерни, вращение отключается при настройке «меньше движения».
export function Hero() {
  return (
    <section className="hero">
      <div className="hero-art" aria-hidden="true">
        <svg viewBox="0 0 300 300" xmlns="http://www.w3.org/2000/svg">
          <g fill="none" stroke="#fff" strokeWidth="1.4">
            <circle cx="150" cy="150" r="140" />
            <circle cx="150" cy="150" r="128" />
            <circle cx="150" cy="150" r="96" />
            <circle cx="150" cy="150" r="44" />
            <circle cx="150" cy="150" r="16" />
          </g>
          <g fill="#fff" opacity=".5">
            <circle cx="150" cy="118" r="5" />
            <circle cx="178" cy="134" r="5" />
            <circle cx="178" cy="166" r="5" />
            <circle cx="150" cy="182" r="5" />
            <circle cx="122" cy="166" r="5" />
            <circle cx="122" cy="134" r="5" />
          </g>
          <g stroke="#fff" strokeWidth="1" opacity=".45">
            <path d="M150 54 v40" />
            <path d="M246 150 h-40" />
            <path d="M150 246 v-40" />
            <path d="M54 150 h40" />
            <path d="M218 82 l-28 28" />
            <path d="M218 218 l-28 -28" />
            <path d="M82 218 l28 -28" />
            <path d="M82 82 l28 28" />
          </g>
          <g stroke="#fff" strokeWidth=".8" opacity=".3">
            <circle cx="150" cy="150" r="112" strokeDasharray="6 10" />
            <circle cx="150" cy="150" r="70" strokeDasharray="3 7" />
          </g>
        </svg>
      </div>
      <div className="wrap relative px-4 pt-[26px] pb-[22px] lg:pt-[52px] lg:pb-10">
        <h1 className="m-0 mb-[10px] max-w-[820px] font-display text-[29px] leading-[1.14] font-bold tracking-[-0.03em] lg:text-[46px]">
          Запчасти для иномарок
          <br />
          <em className="not-italic text-[#ff9670]">в Старобельске</em> и районе
        </h1>
        <p className="m-0 mb-[18px] max-w-[520px] text-[14.5px] leading-[1.5] text-[#b9d0dc] lg:text-[16.5px]">
          Оригинал и проверенные аналоги. Подберём по VIN, привезём в ваш район, платите наличными при получении.
        </p>
        <ul className="m-0 flex list-none flex-wrap gap-2 p-0 text-[12.5px] text-[#dce9ef]">
          <li className="rounded-full border border-white/[.16] bg-white/[.09] px-[13px] py-[7px]">
            <b className="font-semibold text-white">Без предоплаты</b>
          </li>
          <li className="rounded-full border border-white/[.16] bg-white/[.09] px-[13px] py-[7px]">
            <b className="font-semibold text-white">Подбор по VIN</b> за день
          </li>
          <li className="rounded-full border border-white/[.16] bg-white/[.09] px-[13px] py-[7px]">
            <b className="font-semibold text-white">Свои маршруты</b> по северным районам
          </li>
          <li className="rounded-full border border-white/[.16] bg-white/[.09] px-[13px] py-[7px]">
            Уведомления в <b className="font-semibold text-white">MAX</b> и по <b className="font-semibold text-white">SMS</b>
          </li>
        </ul>
      </div>
    </section>
  );
}
