"use client";

import Link from "next/link";
import {
  ChangeEvent,
  FormEvent,
  useEffect,
  useMemo,
  useState,
} from "react";
import { StartArea, WorkspaceState, nowIso } from "@/lib/domain";
import {
  addChallenge,
  addRoutine,
  addTask,
  completeChallenge,
  createEmptyWorkspace,
  createImportantGoal,
  exportWorkspace,
  importWorkspace,
  loadWorkspace,
  logRoutineCompletion,
  saveWorkspace,
  scheduleAction,
  setActionState,
  setNextGoalStep,
  setRoutineActive,
  startAction,
} from "@/lib/workspace";
import { ActionFocus } from "./action-focus";

const setupAreas: {
  id: StartArea;
  title: string;
  text: string;
  note: string;
}[] = [
  {
    id: "important_goal",
    title: "Важная цель",
    text: "Выбрать главное направление и сразу определить ближайший шаг.",
    note: "Ориентир примерно на 90 дней",
  },
  {
    id: "task",
    title: "Дела и задачи",
    text: "Добавить конкретное действие, которое не обязано относиться к большой цели.",
    note: "Можно начать за минуту",
  },
  {
    id: "challenge",
    title: "Челлендж",
    text: "Запустить ограниченный по времени эксперимент с понятным правилом.",
    note: "Есть начало и финиш",
  },
  {
    id: "routine",
    title: "Регулярная практика",
    text: "Поддерживать повторяющееся действие без наказания за пропуски.",
    note: "С посильным вариантом",
  },
];

const stateLabels = {
  active: "в работе",
  done: "выполнено",
  partial: "частично",
  not_happened: "не состоялось",
} as const;

const resultMessages = {
  done: "Действие выполнено. Можно выбрать следующий шаг.",
  partial: "Частичный результат сохранён. Это тоже движение.",
  not_happened: "Подход закрыт без наказания. Позже можно создать новый шаг.",
} as const;

export default function CabinetPage() {
  const [workspace, setWorkspace] = useState<WorkspaceState>(() =>
    createEmptyWorkspace(),
  );
  const [ready, setReady] = useState(false);
  const [message, setMessage] = useState("");
  const [setupArea, setSetupArea] = useState<StartArea | null>(null);

  useEffect(() => {
    setWorkspace(loadWorkspace());
    setReady(true);
  }, []);

  useEffect(() => {
    if (ready) saveWorkspace(workspace);
  }, [workspace, ready]);

  const currentGoalAction = useMemo(() => {
    const actionId = workspace.importantGoal?.currentActionId;
    if (!actionId) return null;
    return workspace.actions.find((action) => action.id === actionId) ?? null;
  }, [workspace]);

  const activeActions = useMemo(
    () => workspace.actions.filter((action) => action.state === "active"),
    [workspace.actions],
  );

  const focusAction = useMemo(() => {
    if (currentGoalAction?.state === "active") return currentGoalAction;
    return activeActions[0] ?? null;
  }, [activeActions, currentGoalAction]);

  const hasAnyContent = Boolean(
    workspace.importantGoal ||
      workspace.actions.length ||
      workspace.challenges.length ||
      workspace.routines.length,
  );

  const showWelcome = !workspace.onboardingCompleted && !hasAnyContent;

  function selectSetupArea(area: StartArea) {
    setSetupArea(area);
    window.setTimeout(() => {
      document
        .getElementById("setup-panel")
        ?.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 0);
  }

  function createGoal(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const created = createImportantGoal({
      title: String(form.get("title") ?? ""),
      horizonResult: String(form.get("result") ?? ""),
      why: String(form.get("why") ?? ""),
      firstStep: String(form.get("firstStep") ?? ""),
      minimumVersion: String(form.get("minimum") ?? ""),
    });
    setWorkspace((state) => ({
      ...state,
      onboardingCompleted: true,
      selectedAreas: Array.from(
        new Set([...state.selectedAreas, "important_goal" as const]),
      ),
      importantGoal: created.goal,
      actions: [created.action, ...state.actions],
      updatedAt: nowIso(),
    }));
    setSetupArea(null);
    setMessage("Важная цель и первый шаг сохранены.");
    event.currentTarget.reset();
  }

  function submitTask(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const title = String(form.get("task") ?? "").trim();
    if (!title) return;
    setWorkspace((state) =>
      addTask(state, {
        title,
        minimumVersion: String(form.get("taskMinimum") ?? ""),
      }),
    );
    setSetupArea(null);
    setMessage("Дело добавлено в ваше пространство.");
    event.currentTarget.reset();
  }

  function submitChallenge(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const title = String(form.get("challengeTitle") ?? "").trim();
    const rule = String(form.get("challengeRule") ?? "").trim();
    const durationDays = Number(form.get("challengeDuration") ?? 7);
    if (!title || !rule) return;
    setWorkspace((state) =>
      addChallenge(state, { title, rule, durationDays }),
    );
    setSetupArea(null);
    setMessage("Челлендж начат.");
    event.currentTarget.reset();
  }

  function submitRoutine(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const title = String(form.get("routineTitle") ?? "").trim();
    const scheduleLabel = String(form.get("routineSchedule") ?? "").trim();
    if (!title || !scheduleLabel) return;
    setWorkspace((state) =>
      addRoutine(state, {
        title,
        scheduleLabel,
        minimumVersion: String(form.get("routineMinimum") ?? ""),
      }),
    );
    setSetupArea(null);
    setMessage("Регулярная практика создана.");
    event.currentTarget.reset();
  }

  function submitNextStep(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const title = String(form.get("nextStep") ?? "").trim();
    if (!title) return;
    setWorkspace((state) =>
      setNextGoalStep(state, {
        title,
        minimumVersion: String(form.get("nextMinimum") ?? ""),
      }),
    );
    setMessage("Следующий шаг добавлен.");
    event.currentTarget.reset();
  }

  function skipWelcome() {
    setWorkspace((state) => ({
      ...state,
      onboardingCompleted: true,
      updatedAt: nowIso(),
    }));
  }

  function downloadBackup() {
    const blob = new Blob([exportWorkspace(workspace)], {
      type: "application/json;charset=utf-8",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "vmeste-export-v1.json";
    link.click();
    URL.revokeObjectURL(url);
    setMessage("Резервная копия сохранена.");
  }

  async function restoreBackup(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    try {
      const restored = importWorkspace(await file.text());
      setWorkspace(restored);
      setMessage("Данные из резервной копии восстановлены.");
    } catch (error) {
      setMessage(
        error instanceof Error
          ? error.message
          : "Не удалось импортировать файл.",
      );
    } finally {
      event.target.value = "";
    }
  }

  if (!ready) {
    return <main className="container">Загружаем ваше пространство…</main>;
  }

  return (
    <main className="shell cabinet">
      <div className="container">
        <header className="topbar cabinet-topbar">
          <Link className="brand" href="/">
            Вместе к цели
          </Link>
          <div className="row cabinet-header-actions">
            <button
              className="button secondary compact"
              onClick={() => selectSetupArea("task")}
            >
              + Добавить
            </button>
            <button
              className="button secondary compact"
              onClick={downloadBackup}
            >
              Резервная копия
            </button>
          </div>
        </header>

        {message ? (
          <div className="notice cabinet-notice">
            <span>{message}</span>
            <button type="button" onClick={() => setMessage("")}>×</button>
          </div>
        ) : null}

        {showWelcome ? (
          <section className="cabinet-welcome">
            <div className="eyebrow">ВАШЕ ЛИЧНОЕ ПРОСТРАНСТВО</div>
            <h1>С чего начнём?</h1>
            <p className="lead">
              Не нужно настраивать всю систему сразу. Выберите одну ситуацию,
              которая важнее сейчас, и создайте первый реальный элемент.
            </p>
            <div className="setup-choice-grid">
              {setupAreas.map((area) => (
                <button
                  className="setup-choice"
                  type="button"
                  key={area.id}
                  onClick={() => selectSetupArea(area.id)}
                >
                  <span className="setup-choice-note">{area.note}</span>
                  <strong>{area.title}</strong>
                  <span>{area.text}</span>
                </button>
              ))}
            </div>
            <button className="text-button" type="button" onClick={skipWelcome}>
              Пока просто открыть кабинет
            </button>
          </section>
        ) : (
          <section className="cabinet-intro">
            <div>
              <div className="eyebrow">ВАШЕ ПРОСТРАНСТВО</div>
              <h2>Что важно сделать сейчас?</h2>
              <p className="lead">
                Выберите одно ближайшее действие. Остальные направления можно
                добавлять постепенно, когда они действительно понадобятся.
              </p>
            </div>
            <div className="quick-setup-row">
              {setupAreas.map((area) => (
                <button
                  type="button"
                  key={area.id}
                  onClick={() => selectSetupArea(area.id)}
                >
                  + {area.title}
                </button>
              ))}
            </div>
          </section>
        )}

        {setupArea ? (
          <section className="card setup-panel" id="setup-panel">
            <div className="setup-panel-header">
              <div>
                <div className="eyebrow">ПЕРВЫЙ РЕАЛЬНЫЙ ЭЛЕМЕНТ</div>
                <h2>
                  {setupAreas.find((area) => area.id === setupArea)?.title}
                </h2>
              </div>
              <button
                type="button"
                className="text-button"
                onClick={() => setSetupArea(null)}
              >
                Закрыть
              </button>
            </div>

            {setupArea === "important_goal" ? (
              workspace.importantGoal ? (
                <div className="notice">
                  Главная цель уже создана. Сначала работайте с её ближайшим
                  шагом; возможность заменить или завершить цель добавим
                  отдельным безопасным сценарием.
                </div>
              ) : (
                <GoalForm onSubmit={createGoal} />
              )
            ) : null}

            {setupArea === "task" ? <TaskForm onSubmit={submitTask} /> : null}
            {setupArea === "challenge" ? (
              <ChallengeForm onSubmit={submitChallenge} />
            ) : null}
            {setupArea === "routine" ? (
              <RoutineForm onSubmit={submitRoutine} />
            ) : null}
          </section>
        ) : null}

        <div className="cabinet-grid">
          <div className="stack">
            <section className="card focus-card">
              <div className="eyebrow">ЧТО СЕЙЧАС ВАЖНЕЕ ВСЕГО</div>
              {focusAction ? (
                <ActionFocus
                  key={`${focusAction.id}:${focusAction.startedAt ?? "idle"}:${focusAction.plannedAt ?? "now"}`}
                  action={focusAction}
                  onStart={(mode) => {
                    setWorkspace((current) =>
                      startAction(current, focusAction.id, mode),
                    );
                    setMessage(
                      mode === "minimum"
                        ? "Запущен посильный вариант действия."
                        : "Действие начато.",
                    );
                  }}
                  onState={(state) => {
                    setWorkspace((current) =>
                      setActionState(current, focusAction.id, state),
                    );
                    setMessage(resultMessages[state]);
                  }}
                  onPlan={(plannedAt) => {
                    setWorkspace((current) =>
                      scheduleAction(current, focusAction.id, plannedAt),
                    );
                    setMessage("Время возвращения сохранено.");
                  }}
                />
              ) : (
                <div className="empty-focus">
                  <h3>Активного действия пока нет</h3>
                  <p className="muted">
                    Добавьте одно дело или ближайший шаг к важной цели. Этого
                    достаточно, чтобы начать.
                  </p>
                  <button
                    className="button"
                    type="button"
                    onClick={() => selectSetupArea("task")}
                  >
                    Добавить первое действие
                  </button>
                </div>
              )}
            </section>

            {workspace.importantGoal ? (
              <section className="card goal-card">
                <div className="eyebrow">ВАЖНАЯ ЦЕЛЬ · ОРИЕНТИР 90 ДНЕЙ</div>
                <h3>{workspace.importantGoal.title}</h3>
                <p className="muted">{workspace.importantGoal.horizonResult}</p>
                {workspace.importantGoal.why ? (
                  <p>
                    <strong>Почему важно:</strong> {workspace.importantGoal.why}
                  </p>
                ) : null}
              </section>
            ) : null}

            {workspace.importantGoal && currentGoalAction?.state !== "active" ? (
              <section className="card next-step-card">
                <h3>Что будет следующим шагом?</h3>
                <p className="muted">
                  Важная цель остаётся живой, когда у неё есть одно ближайшее
                  действие.
                </p>
                <form className="form" onSubmit={submitNextStep}>
                  <label>
                    Следующий шаг
                    <textarea
                      name="nextStep"
                      required
                      placeholder="Что приблизит результат в реальности?"
                    />
                  </label>
                  <label>
                    Посильный вариант
                    <input
                      name="nextMinimum"
                      placeholder="Что можно сделать даже в сложный день?"
                    />
                  </label>
                  <button className="button" type="submit">
                    Добавить следующий шаг
                  </button>
                </form>
              </section>
            ) : null}

            <section className="card">
              <div className="card-heading-row">
                <div>
                  <h3>Дела и ближайшие действия</h3>
                  <p className="muted">
                    Здесь видны обычные дела и шаги к важной цели.
                  </p>
                </div>
                <button
                  className="text-button"
                  type="button"
                  onClick={() => selectSetupArea("task")}
                >
                  + Добавить
                </button>
              </div>
              <div className="action-list">
                {workspace.actions.filter((action) => action.kind !== "routine_step")
                  .length === 0 ? (
                  <p className="muted">Действий пока нет.</p>
                ) : (
                  workspace.actions
                    .filter((action) => action.kind !== "routine_step")
                    .slice(0, 12)
                    .map((action) => (
                      <article className="action-row" key={action.id}>
                        <div>
                          <strong>{action.title}</strong>
                          <div className="action-meta">
                            {action.kind === "goal_step"
                              ? "Шаг к важной цели"
                              : "Самостоятельное дело"}
                            {action.minimumVersion
                              ? ` · посильный вариант: ${action.minimumVersion}`
                              : ""}
                          </div>
                          {action.state === "active" && action.startedAt ? (
                            <div className="action-meta">
                              Начато {formatDateTime(action.startedAt)}
                            </div>
                          ) : null}
                          {action.state === "active" && !action.startedAt && action.plannedAt ? (
                            <div className="action-meta">
                              Возвращение {formatDateTime(action.plannedAt)}
                            </div>
                          ) : null}
                        </div>
                        {action.state === "active" ? (
                          <div className="mini-statuses">
                            <button
                              type="button"
                              onClick={() => {
                                setWorkspace((state) =>
                                  startAction(state, action.id, "full"),
                                );
                                setMessage("Действие выбрано и начато.");
                              }}
                            >
                              Начать
                            </button>
                            <button
                              type="button"
                              onClick={() =>
                                setWorkspace((state) =>
                                  setActionState(state, action.id, "done"),
                                )
                              }
                            >
                              Готово
                            </button>
                          </div>
                        ) : (
                          <span className={`state-pill state-${action.state}`}>
                            {stateLabels[action.state]}
                          </span>
                        )}
                      </article>
                    ))
                )}
              </div>
            </section>
          </div>

          <aside className="stack">
            <section className="card">
              <div className="card-heading-row">
                <div>
                  <h3>Челленджи</h3>
                  <p className="muted">Короткие эксперименты с финишем.</p>
                </div>
                <button
                  className="text-button"
                  type="button"
                  onClick={() => selectSetupArea("challenge")}
                >
                  + Создать
                </button>
              </div>
              <div className="list">
                {workspace.challenges.length === 0 ? (
                  <p className="muted">Активных челленджей пока нет.</p>
                ) : (
                  workspace.challenges.map((challenge) => (
                    <article className="list-item" key={challenge.id}>
                      <strong>{challenge.title}</strong>
                      <p>{challenge.rule}</p>
                      <div className="action-meta">
                        {challenge.durationDays} дн. · начат{" "}
                        {new Date(challenge.startedAt).toLocaleDateString("ru-RU")}
                      </div>
                      {challenge.completedAt ? (
                        <span className="state-pill state-done">завершён</span>
                      ) : (
                        <button
                          className="small-action"
                          type="button"
                          onClick={() =>
                            setWorkspace((state) =>
                              completeChallenge(state, challenge.id),
                            )
                          }
                        >
                          Завершить челлендж
                        </button>
                      )}
                    </article>
                  ))
                )}
              </div>
            </section>

            <section className="card">
              <div className="card-heading-row">
                <div>
                  <h3>Регулярные практики</h3>
                  <p className="muted">Без серий и наказания за пропуск.</p>
                </div>
                <button
                  className="text-button"
                  type="button"
                  onClick={() => selectSetupArea("routine")}
                >
                  + Создать
                </button>
              </div>
              <div className="list">
                {workspace.routines.length === 0 ? (
                  <p className="muted">Практик пока нет.</p>
                ) : (
                  workspace.routines.map((routine) => (
                    <article
                      className={`list-item ${routine.active ? "" : "inactive-item"}`}
                      key={routine.id}
                    >
                      <strong>{routine.title}</strong>
                      <div className="action-meta">{routine.scheduleLabel}</div>
                      {routine.minimumVersion ? (
                        <div className="minimum">
                          Посильный вариант: {routine.minimumVersion}
                        </div>
                      ) : null}
                      <div className="row routine-actions">
                        {routine.active ? (
                          <>
                            <button
                              className="small-action primary-small"
                              type="button"
                              onClick={() => {
                                setWorkspace((state) =>
                                  logRoutineCompletion(state, routine.id),
                                );
                                setMessage("Практика отмечена. На сегодня достаточно.");
                              }}
                            >
                              Выполнено сегодня
                            </button>
                            <button
                              className="small-action"
                              type="button"
                              onClick={() =>
                                setWorkspace((state) =>
                                  setRoutineActive(state, routine.id, false),
                                )
                              }
                            >
                              Поставить на паузу
                            </button>
                          </>
                        ) : (
                          <button
                            className="small-action"
                            type="button"
                            onClick={() =>
                              setWorkspace((state) =>
                                setRoutineActive(state, routine.id, true),
                              )
                            }
                          >
                            Возобновить
                          </button>
                        )}
                      </div>
                    </article>
                  ))
                )}
              </div>
            </section>

            <section className="card data-card">
              <h3>Ваши данные</h3>
              <p className="muted">
                Сейчас информация хранится только в этом браузере. Резервная
                копия использует стабильный формат{" "}
                <code>vmeste-export-v1.json</code>.
              </p>
              <button className="button secondary" onClick={downloadBackup}>
                Скачать резервную копию
              </button>
              <label className="file-input">
                Восстановить из файла
                <input
                  type="file"
                  accept="application/json,.json"
                  onChange={restoreBackup}
                />
              </label>
            </section>
          </aside>
        </div>
      </div>
    </main>
  );
}

function GoalForm({
  onSubmit,
}: {
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}) {
  return (
    <form className="form setup-form" onSubmit={onSubmit}>
      <label>
        Чего вы хотите добиться?
        <input
          name="title"
          required
          placeholder="Например: запустить веб-версию проекта"
        />
      </label>
      <label>
        Какой заметный результат вы хотели бы получить примерно за 90 дней?
        <textarea
          name="result"
          required
          placeholder="Опишите конкретный, наблюдаемый результат"
        />
      </label>
      <label>
        Почему это важно?
        <textarea name="why" required />
      </label>
      <label>
        Какой ближайший посильный шаг?
        <textarea
          name="firstStep"
          required
          placeholder="Действие, которое касается реальности, а не всего плана"
        />
      </label>
      <label>
        Минимальный вариант на сложный день
        <input name="minimum" placeholder="Самая маленькая честная версия шага" />
      </label>
      <button className="button" type="submit">
        Сохранить цель и первый шаг
      </button>
    </form>
  );
}

function TaskForm({
  onSubmit,
}: {
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}) {
  return (
    <form className="form setup-form" onSubmit={onSubmit}>
      <label>
        Что нужно сделать?
        <textarea
          name="task"
          required
          placeholder="Одно конкретное действие"
        />
      </label>
      <label>
        Что можно сделать, если сил мало?
        <input
          name="taskMinimum"
          placeholder="Посильный вариант — необязательно"
        />
      </label>
      <button className="button" type="submit">
        Добавить дело
      </button>
    </form>
  );
}

function ChallengeForm({
  onSubmit,
}: {
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}) {
  return (
    <form className="form setup-form" onSubmit={onSubmit}>
      <label>
        Название челленджа
        <input
          name="challengeTitle"
          required
          placeholder="Например: 7 дней без телефона за завтраком"
        />
      </label>
      <label>
        Простое правило
        <textarea
          name="challengeRule"
          required
          placeholder="Что именно вы проверяете и что считается выполнением?"
        />
      </label>
      <label>
        Продолжительность в днях
        <input
          name="challengeDuration"
          type="number"
          min="1"
          max="365"
          defaultValue="7"
          required
        />
      </label>
      <button className="button" type="submit">
        Начать челлендж
      </button>
    </form>
  );
}

function RoutineForm({
  onSubmit,
}: {
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}) {
  return (
    <form className="form setup-form" onSubmit={onSubmit}>
      <label>
        Название практики
        <input
          name="routineTitle"
          required
          placeholder="Например: 10 минут сербского"
        />
      </label>
      <label>
        Когда или как часто?
        <input
          name="routineSchedule"
          required
          placeholder="Например: по будням после завтрака"
        />
      </label>
      <label>
        Посильный вариант
        <input
          name="routineMinimum"
          placeholder="Например: повторить пять слов"
        />
      </label>
      <button className="button" type="submit">
        Создать практику
      </button>
    </form>
  );
}

function formatDateTime(value: string): string {
  return new Date(value).toLocaleString("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}
