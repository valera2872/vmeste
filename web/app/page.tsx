"use client";

import Link from "next/link";
import { FormEvent, useMemo, useState } from "react";
import { addTask, loadWorkspace, saveWorkspace } from "../lib/workspace";

type Obstacle = "large" | "unclear" | "fear" | "energy";

const problems = [
  [
    "Я давно откладываю",
    "Задача остаётся важной, но каждый день уступает место чему-то срочному.",
  ],
  [
    "Я не понимаю, с чего начать",
    "Цель выглядит слишком большой, расплывчатой или сложной для первого движения.",
  ],
  [
    "Я начинаю и бросаю",
    "После перерыва трудно вернуться, особенно когда кажется, что весь прогресс потерян.",
  ],
  [
    "Списки дел не помогают",
    "Записанных задач становится больше, но ясности и готовности действовать — не всегда.",
  ],
] as const;

const principles = [
  [
    "01",
    "Находим ближайшее действие",
    "Не строим идеальный план на всю жизнь. Определяем, что действительно можно сделать следующим.",
  ],
  [
    "02",
    "Уменьшаем до посильного",
    "Для сложного дня заранее появляется минимальный вариант, который сохраняет движение.",
  ],
  [
    "03",
    "Подбираем способ начать",
    "Можно назначить время, использовать таймер, действовать самостоятельно или с поддержкой человека.",
  ],
  [
    "04",
    "Помогаем вернуться",
    "Пропуск не обнуляет путь. Система предлагает упростить шаг, изменить маршрут или продолжить позже.",
  ],
] as const;

const areas = [
  [
    "Важная цель",
    "Выберите главное направление и заметный результат примерно на ближайшие 90 дней.",
    "90 дней — только ориентир",
  ],
  [
    "Дела и задачи",
    "Разберите накопившееся и определите, что стоит сделать сегодня, а что можно отложить.",
    "Без лишней методологии",
  ],
  [
    "Челлендж",
    "Проведите ограниченный по времени личный эксперимент с понятным правилом и финишем.",
    "Начало и конец видны",
  ],
  [
    "Регулярная практика",
    "Поддерживайте важное повторяющееся действие без наказания за пропуски.",
    "Есть посильный вариант",
  ],
] as const;

const obstacleOptions: { value: Obstacle; label: string }[] = [
  { value: "large", label: "Задача кажется слишком большой" },
  { value: "unclear", label: "Не понимаю первый шаг" },
  { value: "fear", label: "Боюсь сделать плохо или ошибиться" },
  { value: "energy", label: "Сейчас мало сил и внимания" },
];

function makeStep(task: string, obstacle: Obstacle) {
  const cleanTask = task.trim().replace(/[.!?]+$/, "");

  switch (obstacle) {
    case "large":
      return {
        step: `Открыть всё необходимое для задачи «${cleanTask}» и выполнить только её первую небольшую часть за 10 минут.`,
        minimum: `Просто открыть нужный файл, страницу или материалы и оставить их готовыми к работе.`,
      };
    case "unclear":
      return {
        step: `Записать один конкретный результат, который будет означать, что задача «${cleanTask}» немного продвинулась, и сделать первое действие к нему.`,
        minimum: `Сформулировать этот результат одним предложением.`,
      };
    case "fear":
      return {
        step: `Сделать черновой, заведомо неидеальный первый вариант для задачи «${cleanTask}» — пока без отправки и оценки.`,
        minimum: `Создать пустой черновик и написать первые две строки или пункта.`,
      };
    case "energy":
      return {
        step: `Уделить задаче «${cleanTask}» пять спокойных минут: подготовить материалы и сделать одно простое действие.`,
        minimum: `Только подготовить место и записать, с чего начать при следующем подходе.`,
      };
  }
}

export default function LandingPage() {
  const [task, setTask] = useState("");
  const [obstacle, setObstacle] = useState<Obstacle>("large");
  const [result, setResult] = useState<ReturnType<typeof makeStep> | null>(null);
  const [saved, setSaved] = useState(false);

  const selectedObstacle = useMemo(
    () => obstacleOptions.find((item) => item.value === obstacle)?.label ?? "",
    [obstacle],
  );

  function handleAnalyze(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!task.trim()) return;
    setResult(makeStep(task, obstacle));
    setSaved(false);
  }

  function handleSave() {
    if (!result) return;
    const nextState = addTask(loadWorkspace(), {
      title: result.step,
      minimumVersion: result.minimum,
    });
    saveWorkspace(nextState);
    setSaved(true);
  }

  return (
    <main className="shell landing">
      <div className="container">
        <header className="topbar landing-topbar">
          <Link className="brand" href="/">
            Вместе к цели
          </Link>
          <nav className="landing-nav" aria-label="Основная навигация">
            <a href="#difference">Как работает</a>
            <a href="#directions">Возможности</a>
            <a href="#starter">Найти первый шаг</a>
          </nav>
          <Link className="button secondary compact" href="/cabinet">
            Открыть кабинет
          </Link>
        </header>

        <section className="hero marketing-hero">
          <div className="hero-copy">
            <div className="eyebrow">НЕ ЕЩЁ ОДИН СПИСОК ДЕЛ</div>
            <h1>
              Важно не только знать, <span>что делать.</span> Важно суметь начать.
            </h1>
            <p className="lead">
              «Вместе к цели» помогает превратить важное намерение в ближайший
              посильный шаг — когда мешают прокрастинация, перегрузка,
              сомнения или нехватка сил.
            </p>
            <p className="hero-supporting">
              Не требует идеальной дисциплины. Не наказывает за остановки.
              Помогает понять, как именно вам легче перейти к действию.
            </p>
            <div className="actions">
              <a className="button" href="#starter">
                Найти ближайший шаг
              </a>
              <a className="button ghost" href="#difference">
                Посмотреть, как это работает
              </a>
            </div>
            <div className="trust-row" aria-label="Условия начала работы">
              <span>Без регистрации</span>
              <span>Начать можно за 2 минуты</span>
              <span>Данные остаются в браузере</span>
            </div>
          </div>

          <div className="product-preview" aria-label="Пример рабочего экрана">
            <div className="preview-header">
              <span>Сегодня</span>
              <small>СПОКОЙНЫЙ ФОКУС</small>
            </div>
            <div className="preview-goal">
              <small>ВАЖНАЯ ЦЕЛЬ</small>
              <strong>Подготовить веб-версию проекта</strong>
              <span>Ориентир: рабочий публичный сервис</span>
            </div>
            <div className="preview-action">
              <small>БЛИЖАЙШИЙ ШАГ</small>
              <h3>Проверить первый пользовательский сценарий</h3>
              <div className="preview-minimum">
                <span>Посильный вариант</span>
                Открыть проект и проверить один экран
              </div>
              <button type="button" className="button preview-button">
                Начать
              </button>
            </div>
            <p className="preview-note">
              Не весь путь сразу. Только то, что помогает сдвинуться сегодня.
            </p>
          </div>
        </section>

        <section className="section problem-section" aria-labelledby="problem-title">
          <div className="section-heading centered-heading">
            <div className="eyebrow">ПРОБЛЕМА НЕ ВСЕГДА В ДИСЦИПЛИНЕ</div>
            <h2 id="problem-title">Знакомо?</h2>
            <p className="lead">
              Иногда человеку нужен не новый жёсткий план, а более ясный,
              маленький и реалистичный следующий шаг.
            </p>
          </div>
          <div className="problem-grid">
            {problems.map(([title, text]) => (
              <article className="problem-card" key={title}>
                <span className="problem-mark" aria-hidden="true">✓</span>
                <h3>{title}</h3>
                <p>{text}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="section difference-section" id="difference">
          <div className="section-heading split-heading">
            <div>
              <div className="eyebrow">ЧТО ЗДЕСЬ ПРОИСХОДИТ ИНАЧЕ</div>
              <h2>От намерения — к действию, которое можно выполнить</h2>
            </div>
            <p className="lead">
              Обычный планировщик хранит ваши задачи. Эта система помогает
              определить следующий шаг, начать его и продолжить после паузы.
            </p>
          </div>
          <div className="principles-grid">
            {principles.map(([number, title, text]) => (
              <article className="principle-card" key={number}>
                <span className="principle-number">{number}</span>
                <h3>{title}</h3>
                <p>{text}</p>
              </article>
            ))}
          </div>
          <blockquote className="product-principle">
            <strong>Цель остаётся.</strong> Маршрут можно изменить. Следующий
            шаг всегда можно уменьшить.
          </blockquote>
        </section>

        <section className="section directions-section" id="directions">
          <div className="section-heading split-heading">
            <div>
              <div className="eyebrow">ОДНО ПРОСТРАНСТВО — РАЗНЫЕ ЗАДАЧИ</div>
              <h2>Используйте только то, что нужно сейчас</h2>
            </div>
            <p className="lead">
              Не всё обязано становиться частью большой цели. Дела, практики и
              челленджи остаются самостоятельными направлениями.
            </p>
          </div>
          <div className="direction-grid">
            {areas.map(([title, text, note]) => (
              <article className="direction-card" key={title}>
                <span className="direction-note">{note}</span>
                <h3>{title}</h3>
                <p>{text}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="section starter-section" id="starter">
          <div className="starter-copy">
            <div className="eyebrow">ПОЛУЧИТЕ ПЕРВУЮ ПОЛЬЗУ ПРЯМО СЕЙЧАС</div>
            <h2>Что вы давно откладываете?</h2>
            <p className="lead">
              Опишите одну задачу. Система предложит не идеальный план, а
              первый посильный вариант, с которого легче начать.
            </p>
            <div className="starter-examples">
              <span>Позвонить врачу</span>
              <span>Начать заниматься языком</span>
              <span>Подготовить сайт</span>
            </div>
          </div>

          <div className="starter-tool">
            <form className="starter-form" onSubmit={handleAnalyze}>
              <label>
                Задача, которую вы откладываете
                <textarea
                  value={task}
                  onChange={(event) => setTask(event.target.value)}
                  placeholder="Например: подготовить и отправить предложение клиенту"
                  required
                />
              </label>
              <label>
                Что мешает больше всего
                <select
                  value={obstacle}
                  onChange={(event) => setObstacle(event.target.value as Obstacle)}
                >
                  {obstacleOptions.map((item) => (
                    <option value={item.value} key={item.value}>
                      {item.label}
                    </option>
                  ))}
                </select>
              </label>
              <button className="button" type="submit">
                Найти посильный шаг
              </button>
            </form>

            {result ? (
              <div className="starter-result" aria-live="polite">
                <small>УЧЛИ: {selectedObstacle.toUpperCase()}</small>
                <h3>Ваш ближайший шаг</h3>
                <p>{result.step}</p>
                <div className="result-minimum">
                  <strong>Совсем минимальный вариант</strong>
                  <span>{result.minimum}</span>
                </div>
                <div className="result-actions">
                  <button className="button" type="button" onClick={handleSave}>
                    {saved ? "Сохранено" : "Сохранить в кабинете"}
                  </button>
                  <Link className="button secondary" href="/cabinet">
                    Перейти к сегодняшнему дню
                  </Link>
                </div>
                {saved ? (
                  <p className="saved-note">
                    Шаг добавлен в ваши дела и сохранён в этом браузере.
                  </p>
                ) : null}
              </div>
            ) : null}
          </div>
        </section>

        <section className="section evidence-section">
          <div>
            <div className="eyebrow">СПОКОЙНАЯ ПОВЕДЕНЧЕСКАЯ ОСНОВА</div>
            <h2>Без обещаний мгновенно изменить жизнь</h2>
          </div>
          <p>
            Подход соединяет конкретное действие вместо абстрактного
            намерения, посильный размер шага, наблюдение за прогрессом и
            поддержку при возвращении. Это практический инструмент организации
            движения к цели, а не медицинская или психотерапевтическая помощь.
          </p>
        </section>

        <section className="final-cta">
          <div>
            <div className="eyebrow">НАЧАТЬ МОЖНО С ОДНОГО ДЕЙСТВИЯ</div>
            <h2>Не нужно сразу менять всю жизнь.</h2>
            <p>
              Выберите то, что важно сегодня, уменьшите до выполнимого размера
              и сохраните следующий шаг.
            </p>
          </div>
          <Link className="button light-button" href="/cabinet">
            Начать без регистрации
          </Link>
        </section>

        <footer className="landing-footer">
          <strong>Вместе к цели</strong>
          <span>Помогаем начать, продолжить и вернуться без чувства провала.</span>
        </footer>
      </div>
    </main>
  );
}
