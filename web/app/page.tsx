import Link from "next/link";

const areas = [
  ["Важная цель", "Ориентир на 90 дней и один ближайший шаг."],
  ["Челлендж", "Понятное правило с началом и финишем."],
  ["Дела и задачи", "Обычные действия без лишней методологии."],
  ["Практики", "Регулярные действия с посильным вариантом."],
] as const;

export default function LandingPage() {
  return (
    <main className="shell">
      <div className="container">
        <header className="topbar">
          <div className="brand">Вместе к цели</div>
          <Link className="button secondary" href="/cabinet">
            Открыть кабинет
          </Link>
        </header>

        <section className="hero">
          <div>
            <div className="eyebrow">КОГДА ВАЖНОЕ НЕ ДВИГАЕТСЯ</div>
            <h1>Не только записать цель. Действительно начать.</h1>
            <p className="lead">
              Превратите важное намерение в ближайший посильный шаг — даже
              когда мешают прокрастинация, перегрузка или нехватка сил.
            </p>
            <div className="actions">
              <Link className="button" href="/cabinet">
                Начать без регистрации
              </Link>
              <a className="button ghost" href="#how">
                Как это работает
              </a>
            </div>
          </div>

          <div className="hero-card">
            <small>ЧТО ВАЖНО СЕЙЧАС</small>
            <h3>Один ближайший шаг</h3>
            <p>
              Не весь путь сразу. Выберите действие, уменьшите его при
              необходимости и после результата определите следующий шаг.
            </p>
            <div className="minimum">Минимальный вариант сохраняет контакт, а не имитирует успех.</div>
          </div>
        </section>

        <section id="how">
          <h2>Четыре самостоятельных направления</h2>
          <p className="lead">
            Девяносто дней относятся только к важной цели. Дела, практики и
            челленджи не обязаны становиться частью одного большого плана.
          </p>
          <div className="grid">
            {areas.map(([title, text]) => (
              <article className="feature" key={title}>
                <strong>{title}</strong>
                <span>{text}</span>
              </article>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}
