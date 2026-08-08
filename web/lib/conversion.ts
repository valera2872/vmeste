import type { ProblemType, StepSuggestion } from "./micro-tool/engine";
import { addTask, loadWorkspace, saveWorkspace } from "./workspace";

const ACQUISITION_KEY = "vmeste.acquisition.v1";

export interface AcquisitionContext {
  source: "problem_page";
  problemSlug: string;
  problemType: ProblemType;
  originalTask: string;
  savedAt: string;
}

export function continueFromProblemPage(input: {
  problemSlug: string;
  problemType: ProblemType;
  originalTask: string;
  suggestion: StepSuggestion;
}): void {
  if (typeof window === "undefined") return;

  const nextState = addTask(loadWorkspace(), {
    title: input.suggestion.step,
    minimumVersion: input.suggestion.minimum,
  });
  saveWorkspace(nextState);

  const acquisition: AcquisitionContext = {
    source: "problem_page",
    problemSlug: input.problemSlug,
    problemType: input.problemType,
    originalTask: input.originalTask.trim(),
    savedAt: new Date().toISOString(),
  };

  // Attribution stays private in the browser and never becomes part of an URL.
  window.sessionStorage.setItem(ACQUISITION_KEY, JSON.stringify(acquisition));
}
