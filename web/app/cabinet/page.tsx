"use client";

import Link from "next/link";
import { ChangeEvent, FormEvent, useEffect, useMemo, useState } from "react";
import { WorkspaceState, nowIso } from "@/lib/domain";
import {
  addTask,
  createEmptyWorkspace,
  createImportantGoal,
  exportWorkspace,
  importWorkspace,
  loadWorkspace,
  saveWorkspace,
  setActionState,
  setNextGoalStep,
} from "@/lib/workspace";

export default function CabinetPage() {
  const [workspace, setWorkspace] = useState<WorkspaceState>(() =>
    createEmptyWorkspace(),
  );
  const [ready, setReady] = useState(false);
  const [message, setMessage] = useState("");

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
    event.currentTarget.reset();
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
      setMessage(error instanceof Error ? error.message : "Не удалось импортировать файл.");
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
        <header className="topbar">
          <Link className="brand" href="/">
            Вместе к цели
          </Link>
          <button className="button secondary" onClick={downloadBackup}>
            Скачать резервную копию
          </button>
        </header>

        {message ? <div className="notice">{message}</div> : null}

        <section style={{ padding: "32px 0 22px" }}>
          <div className="eyebrow">ГОСТЕВОЙ ЛИЧНЫЙ КАБИНЕТ</div>
          <h2>Что важно сделать сейчас?</h2>
          <p className="lead">
            Данные сохраняются только в этом браузере. Регистрация и серверная
            синхронизация появятся после проверки базового сценария.
          </p>
        </section>

        <div className="cabinet-grid">
          <div className="stack">
            {workspace.importantGoal ? (
              <section className="card goal-card">
                <div className="eyebrow">ВАЖНАЯ ЦЕЛЬ · ОРИЕНТИР 90 ДНЕЙ</div>
                <h3>{workspace.importantGoal.title}</h3>
                <p className="muted">{workspace.importantGoal.horizonResult}</p>
                {workspace.importantGoal.why ? (
                  <p><strong>Почему важно:</strong> {workspace.importantGoal.why}</p>
                ) : null}
              </section>
            ) : (
              <section className="card">
                <h3>Создать важную цель</h3>
                <p className="muted">
                  90 дней — только горизонт результата. Цель, путь и темп можно
                  менять.
                </p>
                <form className="form" onSubmit={createGoal}>
                  <label>
                    Название цели
                    <input name="title" required placeholder="Например: выпустить приложение" />
                  </label>
                  <label>
                    Заметный результат примерно через 90 дней
                    <textarea name="result" required />
                  </label>
                  <label>
                    Почему это важно
                    <textarea name="why" required />
                  </label>
                  <label>
                    Ближайший посильный шаг
                    <textarea name="firstStep" required />
                  </label>
                  <label>
                    Минимальный вариант на сложный день
                    <input name="minimum" />
                  </label>
                  <button className="button" type="submit">Сохранить цель и шаг</button>
                </form>
              </section>
            )}

            {currentGoalAction?.state === "active" ? (
              <section className="card">
                <div className="eyebrow">ГЛАВНОЕ ДЕЙСТВИЕ</div>
                <div className="today-action">
                  <h3>{currentGoalAction.title}</h3>
                  {currentGoalAction.minimumVersion ? (
                    <div className="minimum">
                      Посильный вариант: {currentGoalAction.minimumVersion}
                    </div>
                  ) : null}
                  <div className="statuses">
                    <button onClick={() => setWorkspace((state) => setActionState(state, currentGoalAction.id, "done"))}>
                      Выполнено
                    </button>
                    <button onClick={() => setWorkspace((state) => setActionState(state, currentGoalAction.id, "partial"))}>
                      Частично
                    </button>
                    <button onClick={() => setWorkspace((state) => setActionState(state, currentGoalAction.id, "not_happened"))}>
                      Не состоялось
                    </button>
                  </div>
                </div>
              </section>
            ) : workspace.importantGoal ? (
              <section className="card">
                <h3>Что будет следующим шагом?</h3>
                <p className="muted">
                  Важная цель не должна оставаться без ближайшего действия.
                </p>
                <form className="form" onSubmit={submitNextStep}>
                  <label>
                    Следующий шаг
                    <textarea name="nextStep" required />
                  </label>
                  <label>
                    Минимальный вариант
                    <input name="nextMinimum" />
                  </label>
                  <button className="button" type="submit">Добавить следующий шаг</button>
                </form>
              </section>
            ) : null}

            <section className="card">
              <h3>Дела и задачи</h3>
              <form className="form" onSubmit={submitTask}>
                <label>
                  Новое дело
                  <input name="task" required placeholder="Что нужно сделать?" />
                </label>
                <label>
                  Посильный вариант
                  <input name="taskMinimum" placeholder="Что сделать, если сил мало?" />
                </label>
                <button className="button" type="submit">Добавить дело</button>
              </form>
            </section>
          </div>

          <aside className="stack">
            <section className="card">
              <h3>Сегодня</h3>
              <div className="list">
                {workspace.actions.length === 0 ? (
                  <p className="muted">Действий пока нет.</p>
                ) : (
                  workspace.actions.slice(0, 12).map((action) => (
                    <div
                      className={`list-item ${action.state === "done" ? "done" : ""}`}
                      key={action.id}
                    >
                      <strong>{action.title}</strong>
                      <div className="muted">
                        {action.kind === "goal_step" ? "Шаг к важной цели" : "Дело"}
                        {action.state !== "active" ? ` · ${action.state}` : ""}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </section>

            <section className="card">
              <h3>Переносимость данных</h3>
              <p className="muted">
                Резервная копия использует стабильный формат
                <code> vmeste-export-v1.json</code>. Этот же формат станет мостом
                между браузером, сервером, расширением и Android.
              </p>
              <label className="file-input">
                Восстановить из файла
                <input type="file" accept="application/json,.json" onChange={restoreBackup} />
              </label>
            </section>

            <section className="card">
              <h3>Следующие контуры</h3>
              <p className="muted">
                Челленджи, практики и поддержка уже предусмотрены моделью данных,
                но не мешают проверке основного цикла «цель → действие → результат
                → следующий шаг».
              </p>
            </section>
          </aside>
        </div>
      </div>
    </main>
  );
}
