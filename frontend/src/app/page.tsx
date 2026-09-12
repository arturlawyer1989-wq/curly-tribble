import { Hero } from "@/components/home/hero";
import { Usp } from "@/components/home/usp";

// Главная страница. Каталог узлов, подборка под машину из гаража и поиск
// появятся на этапе каталога, когда будет что показывать.
export default function HomePage() {
  return (
    <>
      <Hero />
      <Usp />
    </>
  );
}
