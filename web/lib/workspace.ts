import {
  ActionItem,
  ActionState,
  Challenge,
  ImportantGoal,
  Routine,
  WORKSPACE_SCHEMA_VERSION,
  WorkspaceExportV1,
  WorkspaceState,
  newId,
  nowIso,
} from "./domain";

export const STORAGE_KEY = "vmeste.workspace.v1";

export function createEmptyWorkspace(): WorkspaceState {
  const now = nowIso();
  return {
    schemaVersion: WORKSPACE_SCHEMA_VERSION,
    workspaceId: newId("workspace"),
    createdAt: now,
    updatedAt: now,
    onboardingCompleted: false,
    selectedAreas: [],
    importantGoal: null,
    actions: [],
    challenges: [],
    routines: [],
    supportAgreements: [],
  };
}

export function createImportantGoal(input: {
  title: string;
  horizonResult: string;
  why: string;
  firstStep: string;
  minimumVersion?: string;
  plannedAt?: string | null;
}): { goal: ImportantGoal; action: ActionItem } {
  const now = nowIso();
  const goalId = newId("goal");
  const actionId = newId("action");
  return {
    goal: {
      id: goalId,
      title: input.title.trim(),
      horizonResult: input.horizonResult.trim(),
      why: input.why.trim(),
      horizonDays: 90,
      currentActionId: actionId,
      createdAt: now,
      updatedAt: now,
    },
    action: {
      id: actionId,
      title: input.firstStep.trim(),
      minimumVersion: input.minimumVersion?.trim() ?? "",
      kind: "goal_step",
      goalId,
      supportMode: "solo",
      plannedAt: input.plannedAt ?? null,
      state: "active",
      outcomeNote: "",
      createdAt: now,
      updatedAt: now,
    },
  };
}

export function addTask(
  state: WorkspaceState,
  input: { title: string; minimumVersion?: string },
): WorkspaceState {
  const now = nowIso();
  const action: ActionItem = {
    id: newId("action"),
    title: input.title.trim(),
    minimumVersion: input.minimumVersion?.trim() ?? "",
    kind: "task",
    goalId: null,
    supportMode: "solo",
    plannedAt: null,
    state: "active",
    outcomeNote: "",
    createdAt: now,
    updatedAt: now,
  };
  return touch({
    ...state,
    onboardingCompleted: true,
    selectedAreas: withArea(state.selectedAreas, "task"),
    actions: [action, ...state.actions],
  });
}

export function addChallenge(
  state: WorkspaceState,
  input: { title: string; rule: string; durationDays: number },
): WorkspaceState {
  const now = nowIso();
  const challenge: Challenge = {
    id: newId("challenge"),
    title: input.title.trim(),
    rule: input.rule.trim(),
    durationDays: Math.max(1, Math.round(input.durationDays)),
    startedAt: now,
    completedAt: null,
  };
  return touch({
    ...state,
    onboardingCompleted: true,
    selectedAreas: withArea(state.selectedAreas, "challenge"),
    challenges: [challenge, ...state.challenges],
  });
}

export function completeChallenge(
  state: WorkspaceState,
  challengeId: string,
): WorkspaceState {
  const completedAt = nowIso();
  return touch({
    ...state,
    challenges: state.challenges.map((challenge) =>
      challenge.id === challengeId
        ? { ...challenge, completedAt }
        : challenge,
    ),
  });
}

export function addRoutine(
  state: WorkspaceState,
  input: {
    title: string;
    minimumVersion?: string;
    scheduleLabel: string;
  },
): WorkspaceState {
  const routine: Routine = {
    id: newId("routine"),
    title: input.title.trim(),
    minimumVersion: input.minimumVersion?.trim() ?? "",
    scheduleLabel: input.scheduleLabel.trim(),
    active: true,
  };
  return touch({
    ...state,
    onboardingCompleted: true,
    selectedAreas: withArea(state.selectedAreas, "routine"),
    routines: [routine, ...state.routines],
  });
}

export function setRoutineActive(
  state: WorkspaceState,
  routineId: string,
  active: boolean,
): WorkspaceState {
  return touch({
    ...state,
    routines: state.routines.map((routine) =>
      routine.id === routineId ? { ...routine, active } : routine,
    ),
  });
}

export function logRoutineCompletion(
  state: WorkspaceState,
  routineId: string,
): WorkspaceState {
  const routine = state.routines.find((item) => item.id === routineId);
  if (!routine) return state;
  const now = nowIso();
  const action: ActionItem = {
    id: newId("action"),
    title: routine.title,
    minimumVersion: routine.minimumVersion,
    kind: "routine_step",
    goalId: null,
    supportMode: "solo",
    plannedAt: now,
    state: "done",
    outcomeNote: `routine:${routine.id}`,
    createdAt: now,
    updatedAt: now,
  };
  return touch({ ...state, actions: [action, ...state.actions] });
}

export function setActionState(
  state: WorkspaceState,
  actionId: string,
  actionState: ActionState,
  outcomeNote = "",
): WorkspaceState {
  const now = nowIso();
  const actions = state.actions.map((action) =>
    action.id === actionId
      ? { ...action, state: actionState, outcomeNote, updatedAt: now }
      : action,
  );
  return touch({ ...state, actions });
}

export function setNextGoalStep(
  state: WorkspaceState,
  input: { title: string; minimumVersion?: string },
): WorkspaceState {
  if (!state.importantGoal) return state;
  const now = nowIso();
  const action: ActionItem = {
    id: newId("action"),
    title: input.title.trim(),
    minimumVersion: input.minimumVersion?.trim() ?? "",
    kind: "goal_step",
    goalId: state.importantGoal.id,
    supportMode: "solo",
    plannedAt: null,
    state: "active",
    outcomeNote: "",
    createdAt: now,
    updatedAt: now,
  };
  return touch({
    ...state,
    importantGoal: {
      ...state.importantGoal,
      currentActionId: action.id,
      updatedAt: now,
    },
    actions: [action, ...state.actions],
  });
}

export function exportWorkspace(state: WorkspaceState): string {
  const payload: WorkspaceExportV1 = {
    format: "vmeste-export",
    version: 1,
    exportedAt: nowIso(),
    state,
  };
  return JSON.stringify(payload, null, 2);
}

export function importWorkspace(raw: string): WorkspaceState {
  const parsed: unknown = JSON.parse(raw);
  if (!isRecord(parsed)) throw new Error("Файл не содержит объект данных.");
  if (parsed.format !== "vmeste-export" || parsed.version !== 1) {
    throw new Error("Это не файл vmeste-export-v1.json.");
  }
  if (!isWorkspaceState(parsed.state)) {
    throw new Error("Структура резервной копии повреждена или несовместима.");
  }
  return touch(parsed.state);
}

export function loadWorkspace(): WorkspaceState {
  if (typeof window === "undefined") return createEmptyWorkspace();
  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (!raw) return createEmptyWorkspace();
  try {
    const parsed: unknown = JSON.parse(raw);
    return isWorkspaceState(parsed) ? parsed : createEmptyWorkspace();
  } catch {
    return createEmptyWorkspace();
  }
}

export function saveWorkspace(state: WorkspaceState): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function withArea(
  areas: WorkspaceState["selectedAreas"],
  area: WorkspaceState["selectedAreas"][number],
): WorkspaceState["selectedAreas"] {
  return areas.includes(area) ? areas : [...areas, area];
}

function touch(state: WorkspaceState): WorkspaceState {
  return { ...state, updatedAt: nowIso() };
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isWorkspaceState(value: unknown): value is WorkspaceState {
  if (!isRecord(value)) return false;
  return (
    value.schemaVersion === WORKSPACE_SCHEMA_VERSION &&
    typeof value.workspaceId === "string" &&
    typeof value.createdAt === "string" &&
    typeof value.updatedAt === "string" &&
    typeof value.onboardingCompleted === "boolean" &&
    Array.isArray(value.selectedAreas) &&
    (value.importantGoal === null || isRecord(value.importantGoal)) &&
    Array.isArray(value.actions) &&
    Array.isArray(value.challenges) &&
    Array.isArray(value.routines) &&
    Array.isArray(value.supportAgreements)
  );
}
