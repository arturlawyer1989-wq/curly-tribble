import { notFound } from "next/navigation";

import { adminFetch, type Overview } from "@/lib/admin-api";
import { SECTIONS, SECTION_COUNTER, type SectionKey } from "@/lib/admin-sections";

export async function generateMetadata({ params }: { params: Promise<{ section: string }> }) {
  const { section } = await params;
  const found = SECTIONS.find((s) => s.key === section);
  return { title: found?.title ?? "Раздел" };
}

// Раздел панели: живой счётчик записей и пояснение, на каком этапе появится содержимое
export default async function SectionPage({ params }: { params: Promise<{ section: string }> }) {
  const { section } = await params;
  const found = SECTIONS.find((s) => s.key === section);
  if (!found) notFound();
  const counterKey = SECTION_COUNTER[found.key as SectionKey];
  let count: number | null = null;
  if (counterKey) {
    const result = await adminFetch<Overview>("/api/v1/admin/overview");
    if (result.ok) count = result.data.sections.find((s) => s.key === counterKey)?.count ?? null;
  }
  return (
    <>
      <h1 className="mt-2 mb-2 font-display text-[22px] font-bold text-white">{found.title}</h1>
      <p className="mt-0 mb-4 text-[14px] text-[#b4c0c9]">{found.description}</p>
      <div className="admin-card p-[16px]">
        {count !== null && (
          <p className="m-0 mb-2 text-[14px]">
            Записей в базе: <b className="font-mono text-white">{count}</b>
          </p>
        )}
        <p className="m-0 text-[13.5px] text-[#8a97a2]">
          {count === 0 ? "Пока пусто. " : ""}
          Работа с этим разделом появится на этапе {found.stage}.
        </p>
      </div>
    </>
  );
}
