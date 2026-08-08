"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import type { ProblemPageDefinition } from "../content/problem-pages";
import { trackEvent } from "../lib/analytics";
import { continueFromProblemPage } from "../lib/conversion";
import {
  generateFirstStep,
  generateMicroToolStep,
  type StepSuggestion,
} from "../lib/micro-tool/engine";
import {
  clearMicroToolSession,
  createMicroToolSession,
  loadMicroToolSession,
  saveMicroToolSession,
  type MicroToolSession,
} from "../lib/micro-tool/session";
import styles from "./problem-page.module.css";

function resultLabel(action: StepSuggestion["action"]): string {
  switch (action) {
    case "smaller_step":
      return "Ещё меньше";
    case "next_step":
      return "Следующий шаг";
    case "two_minute_start":
      return "Старт на 2 минуты";
    case "choose_between_tasks":
      return "Как выбрать";
    case "first_step":
    default:
      return "Первый шаг";
  }
}

function applyQueryNoindex(): void {
  if (typeof window === "undefined" || !window.location.search) return;

  let meta = document.querySelector<HTMLMetaElement>('meta[name="robots"]');
  if (!meta) {
    meta = document.createElement("meta");
    meta.name = "robots";
    document.head.appendChild(meta);
  }
  meta.content = "noindex, nofollow";
}

export function ProblemMicroTool({
  problem,
}: {
  problem: ProblemPageDefinition;
}) {
  const router = useRouter();
  const inputRef = useRef<HTMLTextAreaElement | null>(null);
  const sessionRef = useRef<MicroToolSession | null>(null);
  const toolStartedRef = useRef(false);
  const [task, setTask] = useState("");
  const [history, setHistory] = useState<StepSuggestion[]>([]);

  const current = history.at(-1) ?? null;

  useEffect(() => {
    applyQueryNoindex();
    trackEvent("problem_page_view", {
      problem_slug: problem.slug,
      problem_type: problem.problemType,
    });

    const saved = loadMicroToolSession(problem.slug);
    if (saved) {
      sessionRef.current = saved;
      setTask(saved.task);
      setHistory(saved.history);
    }
  }, [problem.problemType, problem.slug]);

  function markToolStarted() {
    if (toolStartedRef.current) return;
    toolStartedRef.current = true;
    trackEvent("tool_started", {
      problem_slug: problem.slug,
      problem_type: problem.problemType,
    });
  }

  function persist(nextTask: string, nextHistory: StepSuggestion[]) {
    const session = sessionRef.current
      ? {
          ...sessionRef.current,
          task: nextTask.trim(),
          history: nextHistory,
        }
      : createMicroToolSession({
          problemSlug: problem.slug,
          problemType: problem.problemType,
          task: nextTask,
          history: nextHistory,
        });

    sessionRef.current = session;
    saveMicroToolSession(session);
  }

  function handleGenerate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const cleanTask = task.trim();
    if (!cleanTask) return;

    markToolStarted();
    trackEvent("task_entered", {
      problem_slug: problem.slug,
      problem_type: problem.problemType,
      task_length: cleanTask.length,
    });

    const suggestion = generateFirstStep(problem.problemType, cleanTask);
    const nextHistory = [suggestion];
    setHistory(nextHistory);
    persist(cleanTask, nextHistory);

    trackEvent("first_step_generated", {
      problem_slug: problem.slug,
      problem_type: problem.problemType,
    });
  }

  function handleSmaller() {
    if (!current || !task.trim()) return;

    const suggestion = generateMicroToolStep({
      problemType: problem.problemType,
      userTask: task,
      action: "smaller_step",
      previousStep: current,
    });
    const nextHistory = [...history, suggestion];
    setHistory(nextHistory);
    persist(task, nextHistory);

    trackEvent("smaller_step_requested", {
      problem_slug: problem.slug,
      problem_type: problem.problemType,
      interaction_number: nextHistory.length,
    });
  }

  function handleNext() {
    if (!current || !task.trim()) return;

    const suggestion = generateMicroToolStep({
      problemType: problem.problemType,
      userTask: task,
      action: "next_step",
      previousStep: current,
    });
    const nextHistory = [...history, suggestion];
    setHistory(nextHistory);
    persist(task, nextHistory);

    trackEvent("next_step_requested", {
      problem_slug: problem.slug,
      problem_type: problem.problemType,
      interaction_number: nextHistory.length,
    });
  }

  function handleModify() {
    setHistory([]);
    sessionRef.current = null;
    clearMicroToolSession();
    requestAnimationFrame(() => inputRef.current?.focus());
  }

  function handleExample(example: string) {
    markToolStarted();
    setTask(example);
    setHistory([]);
    sessionRef.current = null;
    clearMicroToolSession();
    requestAnimationFrame(() => inputRef.current?.focus());
  }

  function handleContinue() {
    if (!current || !task.trim()) return;

    trackEvent("app_continue_clicked", {
      problem_slug: problem.slug,
      problem_type: problem.problemType,
      interaction_count: history.length,
    });

    continueFromProblemPage({
      problemSlug: problem.slug,
      problemType: problem.problemType,
      originalTask: task,
      suggestion: current,
    });
    clearMicroToolSession();
    router.push("/cabinet");
  }

  return (
    <section className={styles.toolCard} aria-label="Интерактивный первый шаг">
      <div className={styles.toolHeading}>
        <strong>Начнём не со всего дела, а с одного действия</strong>
        <p>Первый результат доступен сразу, без аккаунта.</p>
      </div>

      <form onSubmit={handleGenerate}>
        <label className={styles.field}>
          {problem.prompts.inputLabel}
          <textarea
            ref={inputRef}
            value={task}
            onFocus={markToolStarted}
            onChange={(event) => {
              markToolStarted();
              setTask(event.target.value);
            }}
            placeholder={problem.prompts.placeholder}
            required
          />
        </label>

        <div className={styles.examples} aria-label="Примеры задач">
          {problem.examples.map((example) => (
            <button
              className={styles.exampleButton}
              type="button"
              key={example}
              onClick={() => handleExample(example)}
            >
              {example}
            </button>
          ))}
        </div>

        <button className={styles.primaryButton} type="submit">
          {problem.prompts.buttonLabel}
        </button>
      </form>

      {current ? (
        <div className={styles.result} aria-live="polite">
          <span className={styles.resultLabel}>{resultLabel(current.action)}</span>
          <h2>{current.step}</h2>

          <div className={styles.minimum}>
            <strong>Если даже это много</strong>
            {current.minimum}
          </div>

          <div className={styles.toolActions}>
            <button
              className={styles.secondaryButton}
              type="button"
              onClick={handleSmaller}
            >
              Сделать шаг ещё меньше
            </button>
            <button
              className={styles.secondaryButton}
              type="button"
              onClick={handleNext}
            >
              Дать следующий шаг
            </button>
            <button
              className={styles.textButton}
              type="button"
              onClick={handleModify}
            >
              Изменить задачу
            </button>
          </div>

          <div className={styles.conversion}>
            <strong>Хотите не потерять этот шаг?</strong>
            <p>
              Сохраните его во «Вместе к цели». Он появится в кабинете как
              текущее действие, и можно будет начать, отложить или продолжить
              после паузы.
            </p>
            <button
              className={styles.primaryButton}
              type="button"
              onClick={handleContinue}
            >
              Сохранить шаг и продолжить
            </button>
          </div>
        </div>
      ) : null}
    </section>
  );
}
