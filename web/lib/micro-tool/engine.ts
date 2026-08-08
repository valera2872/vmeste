export type ProblemType =
  | "task_start"
  | "cleaning_start"
  | "study_delay"
  | "overwhelming_task"
  | "unclear_start";

export type MicroToolAction =
  | "first_step"
  | "smaller_step"
  | "next_step"
  | "choose_between_tasks"
  | "two_minute_start";

export interface StepSuggestion {
  action: MicroToolAction;
  step: string;
  minimum: string;
}

export interface StepGenerationInput {
  problemType: ProblemType;
  userTask: string;
  action: MicroToolAction;
  previousStep?: StepSuggestion | null;
}

export interface MicroToolGenerator {
  generate(input: StepGenerationInput): StepSuggestion;
}

function cleanTask(value: string): string {
  return value.trim().replace(/\s+/g, " ").replace(/[.!?]+$/, "");
}

function firstStep(problemType: ProblemType, userTask: string): StepSuggestion {
  const task = cleanTask(userTask);

  switch (problemType) {
    case "cleaning_start":
      return {
        action: "first_step",
        step:
          "Выберите одну маленькую зону — например, стол, раковину или один участок пола — поставьте таймер на 5 минут и уберите только её.",
        minimum: "Уберите на место один предмет из этой зоны.",
      };
    case "study_delay":
      return {
        action: "first_step",
        step: `Откройте материал, который нужен для «${task}», выберите одну страницу, абзац или одно задание и поработайте только 10 минут.`,
        minimum: "Только откройте материал и отметьте место, с которого начнёте.",
      };
    case "overwhelming_task":
      return {
        action: "first_step",
        step: `Для «${task}» запишите один маленький видимый результат, который реально получить за 10–15 минут, и сделайте первое действие только к нему.`,
        minimum: "Сформулируйте этот маленький результат одним предложением.",
      };
    case "unclear_start":
      return {
        action: "first_step",
        step: `Ответьте одним предложением: что должно стать заметно другим, чтобы «${task}» немного продвинулось? Затем выберите первое физическое действие: открыть, написать, позвонить или найти.`,
        minimum: "Запишите только одно первое действие-глагол.",
      };
    case "task_start":
    default:
      return {
        action: "first_step",
        step: `Подготовьте всё необходимое для «${task}» и сделайте только первое конкретное действие, которое занимает не больше 10 минут.`,
        minimum: "Только откройте нужный файл, страницу, материалы или место работы.",
      };
  }
}

function smallerStep(
  problemType: ProblemType,
  userTask: string,
  previousStep?: StepSuggestion | null,
): StepSuggestion {
  const task = cleanTask(userTask);
  const previousMinimum = previousStep?.minimum?.trim();

  switch (problemType) {
    case "cleaning_start":
      return {
        action: "smaller_step",
        step: previousMinimum || "Уберите на место один предмет.",
        minimum: "Просто подойдите к выбранной зоне и возьмите первый предмет.",
      };
    case "study_delay":
      return {
        action: "smaller_step",
        step: previousMinimum || "Откройте учебный материал.",
        minimum: "Найдите нужный файл, книгу или страницу и оставьте её открытой.",
      };
    case "overwhelming_task":
      return {
        action: "smaller_step",
        step: previousMinimum || "Запишите один маленький результат.",
        minimum: `Напишите: «Сейчас я продвину “${task}” хотя бы на один шаг».`,
      };
    case "unclear_start":
      return {
        action: "smaller_step",
        step: previousMinimum || "Назовите одно первое действие.",
        minimum: "Выберите только один глагол: открыть, написать, позвонить или найти.",
      };
    case "task_start":
    default:
      return {
        action: "smaller_step",
        step: previousMinimum || "Только подготовьте место для начала.",
        minimum: `Откройте то, без чего нельзя начать «${task}», и на этом остановитесь.`,
      };
  }
}

function nextStep(problemType: ProblemType, userTask: string): StepSuggestion {
  const task = cleanTask(userTask);

  switch (problemType) {
    case "cleaning_start":
      return {
        action: "next_step",
        step:
          "После первой зоны выберите одну соседнюю маленькую зону и повторите ещё один короткий подход на 5 минут.",
        minimum: "Переложите на место ещё один предмет из соседней зоны.",
      };
    case "study_delay":
      return {
        action: "next_step",
        step: `После первого короткого блока по «${task}» запишите одним предложением, что поняли или сделали, и выберите ещё одно небольшое задание на 10 минут.`,
        minimum: "Запишите одну мысль или один вопрос по изученному материалу.",
      };
    case "overwhelming_task":
      return {
        action: "next_step",
        step: `Когда первый маленький результат по «${task}» готов, определите следующий такой же небольшой результат — не весь проект целиком — и выделите на него 10–15 минут.`,
        minimum: "Назовите следующий маленький результат одним предложением.",
      };
    case "unclear_start":
      return {
        action: "next_step",
        step: `После первого действия по «${task}» спросите: «Что теперь стало понятно?» — и выберите одно следующее физическое действие из нового состояния.`,
        minimum: "Запишите только следующий глагол-действие.",
      };
    case "task_start":
    default:
      return {
        action: "next_step",
        step: `После первого действия по «${task}» продолжите ещё один короткий блок до ближайшего заметного промежуточного результата.`,
        minimum: "Сделайте ещё одно действие, которое занимает не больше 5 минут.",
      };
  }
}

function twoMinuteStart(problemType: ProblemType, userTask: string): StepSuggestion {
  const task = cleanTask(userTask);

  switch (problemType) {
    case "cleaning_start":
      return {
        action: "two_minute_start",
        step: "За 2 минуты уберите на место три предмета и остановитесь, даже если хочется продолжить.",
        minimum: "Уберите один предмет.",
      };
    case "study_delay":
      return {
        action: "two_minute_start",
        step: `За 2 минуты откройте материал по «${task}» и прочитайте только заголовок и первый абзац или условие первого задания.`,
        minimum: "Просто откройте нужный материал.",
      };
    default:
      return {
        action: "two_minute_start",
        step: `Поставьте таймер на 2 минуты и сделайте для «${task}» только подготовительное действие: открыть, найти, создать черновик или записать первый пункт.`,
        minimum: "Только откройте то, с чего начинается задача.",
      };
  }
}

function chooseBetweenTasks(userTask: string): StepSuggestion {
  const tasks = userTask
    .split(/\n|;|\sили\s/iu)
    .map((item) => cleanTask(item))
    .filter(Boolean);

  const list = tasks.length > 1 ? ` Из вариантов: ${tasks.join("; ")}.` : "";
  return {
    action: "choose_between_tasks",
    step:
      "Сначала выберите задачу с реальным сроком сегодня. Если срочной нет — ту, которую можно заметно продвинуть за 10 минут и после которой станет психологически легче." +
      list,
    minimum: "Выберите одну задачу только на ближайшие 10 минут, не на весь день.",
  };
}

export const ruleBasedStepGenerator: MicroToolGenerator = {
  generate(input) {
    switch (input.action) {
      case "smaller_step":
        return smallerStep(input.problemType, input.userTask, input.previousStep);
      case "next_step":
        return nextStep(input.problemType, input.userTask);
      case "two_minute_start":
        return twoMinuteStart(input.problemType, input.userTask);
      case "choose_between_tasks":
        return chooseBetweenTasks(input.userTask);
      case "first_step":
      default:
        return firstStep(input.problemType, input.userTask);
    }
  },
};

// Единственная точка выбора генератора. Позже здесь можно подключить AI-адаптер
// с тем же интерфейсом, не меняя URL Problem Pages и их клиентский код.
const activeGenerator: MicroToolGenerator = ruleBasedStepGenerator;

export function generateMicroToolStep(input: StepGenerationInput): StepSuggestion {
  return activeGenerator.generate(input);
}

export function generateFirstStep(
  problemType: ProblemType,
  userTask: string,
): StepSuggestion {
  return generateMicroToolStep({
    problemType,
    userTask,
    action: "first_step",
  });
}
