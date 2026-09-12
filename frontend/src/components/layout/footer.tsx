import type { Shop } from "@/lib/api";

type Props = { shop: Shop };

// Подвал: контакты из настроек магазина и условия оплаты.
// Колонки «Каталог» и «Покупателям» появятся вместе с соответствующими страницами.
export function Footer({ shop }: Props) {
  const hasContacts = Boolean(shop.phone || shop.address || shop.work_hours || shop.email);
  const legalParts = [shop.legal_name && `ИП ${shop.legal_name}`, shop.inn && `ИНН ${shop.inn}`].filter(Boolean);
  const year = new Date().getFullYear();

  return (
    <footer className="mt-[10px] bg-petrol-dark py-7 text-[13px] text-[#a9c1ce]">
      <div className="wrap">
        <div className="grid grid-cols-1 gap-[22px] sm:grid-cols-2">
          <div>
            <b className="mb-[10px] block text-[13.5px] text-white">Контакты</b>
            {hasContacts ? (
              <>
                {shop.phone && (
                  <a href={shop.phone_href} className="block py-1 hover:text-white">
                    {shop.phone}
                  </a>
                )}
                {shop.address && <span className="block py-1">{shop.address}</span>}
                {shop.work_hours && <span className="block py-1">{shop.work_hours}</span>}
                {shop.email && (
                  <a href={`mailto:${shop.email}`} className="block py-1 hover:text-white">
                    {shop.email}
                  </a>
                )}
              </>
            ) : (
              <span className="block py-1">Контакты магазина будут указаны после заполнения настроек.</span>
            )}
          </div>
          <div>
            <b className="mb-[10px] block text-[13.5px] text-white">Оплата</b>
            <span className="block py-1">Наличными при получении</span>
            <span className="block py-1">Онлайн-оплаты и предоплаты на сайте нет</span>
          </div>
        </div>
        <div className="mt-[22px] border-t border-white/[.12] pt-[15px] text-[11.5px] leading-[1.5] text-[#7a93a2]">
          {legalParts.length > 0 && <span>{legalParts.join(" · ")} · </span>}
          Информация на сайте не является публичной офертой. Цена и срок подтверждаются менеджером до оплаты. ©{" "}
          {year} {shop.name}
        </div>
      </div>
    </footer>
  );
}
