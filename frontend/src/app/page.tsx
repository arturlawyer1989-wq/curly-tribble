import { Hero } from "@/components/home/hero";
import { ProjectStatus } from "@/components/home/project-status";
import { Usp } from "@/components/home/usp";
import { getHealth, getShop } from "@/lib/api";

// Главная страница. Каталог узлов, подборка под машину из гаража и поиск
// появятся на этапе каталога, когда будет что показывать.
export default async function HomePage() {
  const [{ shop }, { health }] = await Promise.all([getShop(), getHealth()]);
  return (
    <>
      <Hero />
      <Usp />
      <ProjectStatus shop={shop} health={health} />
    </>
  );
}
