export const WORKSPACE_SCHEMA_VERSION = 1 as const;

export type ISODateTime = string;
export type StartArea =
  | "important_goal"
  | "challenge"
  | "task"
  | "routine";

export type ActionKind = "goal_step" | "task" | "routine_step";
export type ActionState = "active" | "done" | "partial" | "not_happened";
export type SupportMode = "solo" | "person";

export interface ImportantGoal {
  id: string;
  title: string;
  horizonResult: string;
  why: string;
  horizonDays: 90;
  currentActionId: string | null;
  createdAt: ISODateTime;
  updatedAt: ISODateTime;
}

export interface ActionItem {
  id: string;
  title: string;
  minimumVersion: string;
  kind: ActionKind;
  goalId: string | null;
  supportMode: SupportMode;
  plannedAt: ISODateTime | null;
  state: ActionState;
  outcomeNote: string;
  createdAt: ISODateTime;
  updatedAt: ISODateTime;
}

export interface Challenge {
  id: string;
  title: string;
  rule: string;
  durationDays: number;
  startedAt: ISODateTime;
  completedAt: ISODateTime | null;
}

export interface Routine {
  id: string;
  title: string;
  minimumVersion: string;
  scheduleLabel: string;
  active: boolean;
}

export interface SupportAgreement {
  id: string;
  personName: string;
  actionId: string | null;
  note: string;
  active: boolean;
}

export interface WorkspaceState {
  schemaVersion: typeof WORKSPACE_SCHEMA_VERSION;
  workspaceId: string;
  createdAt: ISODateTime;
  updatedAt: ISODateTime;
  onboardingCompleted: boolean;
  selectedAreas: StartArea[];
  importantGoal: ImportantGoal | null;
  actions: ActionItem[];
  challenges: Challenge[];
  routines: Routine[];
  supportAgreements: SupportAgreement[];
}

export interface WorkspaceExportV1 {
  format: "vmeste-export";
  version: 1;
  exportedAt: ISODateTime;
  state: WorkspaceState;
}

export function newId(prefix: string): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return `${prefix}_${crypto.randomUUID()}`;
  }
  return `${prefix}_${Date.now()}_${Math.random().toString(16).slice(2)}`;
}

export function nowIso(): ISODateTime {
  return new Date().toISOString();
}
