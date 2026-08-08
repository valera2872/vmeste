"use client";

import { FormEvent, useMemo, useState } from "react";
import {
  ActionItem,
  ActionStartMode,
  ActionState,
} from "@/lib/domain";

export function ActionFocus({
  action,
  onStart,
  onState,
  onPlan,
}: {
  action: ActionItem;
  onStart: (mode: ActionStartMode) => void;
  onState: (state: Exclude<ActionState, "active">) => void;
  onPlan: (plannedAt: string) => void;
}) {
  const [showRecovery, setShowRecovery] = useState(false);
  const [showSchedule, setShowSchedule] = useState(false);
  const defaultPlan = useMemo(
    () => toDateTimeInput(action.plannedAt ?? oneHourFromNow()),
    [action.plannedAt],
  );
  const started = Boolean(action.startedAt);
  const minimumMode = action.outcomeNote === "started:minimum";

  function submitSchedule(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const plannedAt = String(form.get("plannedAt") ?? "").trim();
    if (!plannedAt) return;
    onPlan(plannedAt);
    setShowSchedule(false);
    setShowRecovery(false);
  }

  return (
    <div className="today-action focus-action">
      <h2>{action.title}</h2>
      {action.minimumVersion ? (
        <div className="minimum">
          Посильный вариант: {action.minimumVersion}
        </div>
      ) : null}

      {started ? (
        <>
          <div className="notice">
            <strong>
              {minimumMode ? "Вы начали с посильного варианта." : "Действие начато."}
            </strong>{" "}
            {action.startedAt
              ? `Старт: ${formatDateTime(action.startedAt)}.`
              : ""}
          </div>
          <p className="muted">
            Не нужно завершать весь путь. Отметьте результат этого подхода или
            выберите спокойный способ вернуться после остановки.
          </p>
          <div className="statuses">
            <button type="button" onClick={() => onState("done")}>
              Выполнено
            </button>
            <button type="button" onClick={() => onState("partial")}>
              Сделано частично
            </button>
            <button
              type="button"
              onClick={() => setShowRecovery((value) => !value)}
            >
              Я остановился
            </button>
          </div>

          {showRecovery ? (
            <div className="notice">
              <strong>Остановка не отменяет движение.</strong>
              <p>
                Можно уменьшить действие, назначить время возвращения или
                честно закрыть этот подход без чувства провала.
              </p>
              <div className="row">
                {action.minimumVersion ? (
                  <button
                    className="small-action primary-small"
                    type="button"
                    onClick={() => {
                      onStart("minimum");
                      setShowRecovery(false);
                    }}
                  >
                    Продолжить минимумом
                  </button>
                ) : null}
                <button
                  className="small-action"
                  type="button"
                  onClick={() => setShowSchedule(true)}
                >
                  Назначить возвращение
                </button>
                <button
                  className="small-action"
                  type="button"
                  onClick={() => onState("not_happened")}
                >
                  На сегодня не состоялось
                </button>
              </div>
            </div>
          ) : null}
        </>
      ) : (
        <>
          {action.plannedAt ? (
            <div className="notice">
              Возвращение запланировано на{" "}
              <strong>{formatDateTime(action.plannedAt)}</strong>. Начать раньше
              тоже можно.
            </div>
          ) : (
            <p className="muted">
              Выберите не оценку себя, а следующий режим действия: обычный,
              минимальный или конкретное время возвращения.
            </p>
          )}
          <div className="statuses">
            <button type="button" onClick={() => onStart("full")}>
              Начать сейчас
            </button>
            {action.minimumVersion ? (
              <button type="button" onClick={() => onStart("minimum")}>
                Начать с минимума
              </button>
            ) : null}
            <button
              type="button"
              onClick={() => setShowSchedule((value) => !value)}
            >
              Назначить время
            </button>
          </div>
        </>
      )}

      {showSchedule ? (
        <form className="form" onSubmit={submitSchedule}>
          <label>
            Когда вернуться к этому действию?
            <input
              name="plannedAt"
              type="datetime-local"
              defaultValue={defaultPlan}
              min={toDateTimeInput(new Date().toISOString())}
              required
            />
          </label>
          <div className="row">
            <button className="button" type="submit">
              Сохранить время
            </button>
            <button
              className="button secondary"
              type="button"
              onClick={() => setShowSchedule(false)}
            >
              Отмена
            </button>
          </div>
        </form>
      ) : null}
    </div>
  );
}

function oneHourFromNow(): string {
  return new Date(Date.now() + 60 * 60 * 1000).toISOString();
}

function toDateTimeInput(value: string): string {
  const date = new Date(value);
  const offset = date.getTimezoneOffset() * 60_000;
  return new Date(date.getTime() - offset).toISOString().slice(0, 16);
}

function formatDateTime(value: string): string {
  return new Date(value).toLocaleString("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}
