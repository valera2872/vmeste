import { newId, nowIso } from "../domain";
import type { ProblemType, StepSuggestion } from "./engine";

const SESSION_KEY = "vmeste.micro-tool.session.v1";

export interface MicroToolSession {
  version: 1;
  id: string;
  problemSlug: string;
  problemType: ProblemType;
  task: string;
  history: StepSuggestion[];
  createdAt: string;
  updatedAt: string;
}

export function createMicroToolSession(input: {
  problemSlug: string;
  problemType: ProblemType;
  task: string;
  history?: StepSuggestion[];
}): MicroToolSession {
  const now = nowIso();
  return {
    version: 1,
    id: newId("micro_session"),
    problemSlug: input.problemSlug,
    problemType: input.problemType,
    task: input.task.trim(),
    history: input.history ?? [],
    createdAt: now,
    updatedAt: now,
  };
}

export function saveMicroToolSession(session: MicroToolSession): void {
  if (typeof window === "undefined") return;
  window.sessionStorage.setItem(
    SESSION_KEY,
    JSON.stringify({ ...session, updatedAt: nowIso() }),
  );
}

export function loadMicroToolSession(
  problemSlug: string,
): MicroToolSession | null {
  if (typeof window === "undefined") return null;
  const raw = window.sessionStorage.getItem(SESSION_KEY);
  if (!raw) return null;

  try {
    const parsed: unknown = JSON.parse(raw);
    if (!isSession(parsed) || parsed.problemSlug !== problemSlug) return null;
    return parsed;
  } catch {
    return null;
  }
}

export function clearMicroToolSession(): void {
  if (typeof window === "undefined") return;
  window.sessionStorage.removeItem(SESSION_KEY);
}

function isSession(value: unknown): value is MicroToolSession {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    return false;
  }

  const session = value as Record<string, unknown>;
  return (
    session.version === 1 &&
    typeof session.id === "string" &&
    typeof session.problemSlug === "string" &&
    typeof session.problemType === "string" &&
    typeof session.task === "string" &&
    Array.isArray(session.history) &&
    typeof session.createdAt === "string" &&
    typeof session.updatedAt === "string"
  );
}
