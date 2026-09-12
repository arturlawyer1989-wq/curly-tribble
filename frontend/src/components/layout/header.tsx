import Link from "next/link";

import type { Shop } from "@/lib/api";

type Props = { shop: Shop };

// Шапка: логотип и телефон. Разделы каталога, кабинет и корзина появятся на своих этапах.
export function Header({ shop }: Props) {
  return (
    <header className="relative z-40 bg-petrol text-white">
      <div className="wrap flex h-[60px] items-center gap-[14px] lg:h-[74px]">
        <Link
          href="/"
          className="flex min-h-[44px] items-center gap-[9px] whitespace-nowrap font-display text-[16.5px] font-bold tracking-[-0.02em]"
          aria-label={`${shop.name}, на главную`}
        >
          <i className="grid h-7 w-7 place-items-center rounded-[7px] bg-accent font-mono text-[12.5px] font-bold not-italic">
            {shop.short_name}
          </i>
          {shop.name}
        </Link>
        <div className="ml-auto flex items-center gap-2">
          {shop.phone && (
            <>
              <a
                href={shop.phone_href}
                className="hidden min-h-[44px] items-center font-mono text-[14.5px] font-bold lg:flex"
              >
                {shop.phone}
              </a>
              <a href={shop.phone_href} className="icon-btn lg:hidden" aria-label={`Позвонить ${shop.phone}`}>
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2" />
                </svg>
              </a>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
