import type { ProblemType } from "../lib/micro-tool/engine";

export type ProblemPageStatus = "draft" | "published";

export interface ProblemPageDefinition {
  title: string;
  slug: string;
  problemType: ProblemType;
  intro: string;
  examples: string[];
  prompts: {
    inputLabel: string;
    placeholder: string;
    buttonLabel: string;
  };
  seoTitle: string;
  seoDescription: string;
  status: ProblemPageStatus;
  relatedSlugs?: string[];
}

export const problemPages: ProblemPageDefinition[] = [
  {
    title: "Не могу начать задачу",
    slug: "ne-mogu-nachat",
    problemType: "task_start",
    intro:
      "Если вы понимаете, что задачу нужно сделать, но всё равно не начинаете, не пытайтесь сначала составить идеальный план. Введите конкретную задачу — найдём действие, которое можно сделать сейчас.",
    examples: [
      "подготовить отчёт",
      "позвонить по важному вопросу",
      "разобрать документы",
    ],
    prompts: {
      inputLabel: "Что именно нужно начать?",
      placeholder: "Например: подготовить отчёт для клиента",
      buttonLabel: "Дай первый шаг",
    },
    seoTitle: "Не могу начать задачу — найдите первый маленький шаг",
    seoDescription:
      "Бесплатный интерактивный инструмент: опишите задачу и получите первый маленький шаг без регистрации и длинного плана.",
    status: "published",
    relatedSlugs: ["bolshaya-zadacha", "ne-znayu-s-chego-nachat"],
  },
  {
    title: "Не могу начать уборку",
    slug: "ne-mogu-nachat-uborku",
    problemType: "cleaning_start",
    intro:
      "Уборка часто ощущается не как одно действие, а как бесконечный объём. Здесь мы уменьшим её до одной зоны и одного короткого старта, который не требует наводить порядок во всём доме.",
    examples: [
      "разобрать кухню",
      "начать уборку в комнате",
      "убрать вещи со стола",
    ],
    prompts: {
      inputLabel: "Что именно вы хотите убрать?",
      placeholder: "Например: разобрать кухню после выходных",
      buttonLabel: "Дай первый шаг",
    },
    seoTitle: "Не могу начать уборку — первый маленький шаг за 5 минут",
    seoDescription:
      "Не получается начать уборку? Введите конкретную задачу и получите маленький стартовый шаг без регистрации.",
    status: "published",
    relatedSlugs: ["ne-mogu-nachat", "bolshaya-zadacha"],
  },
  {
    title: "Откладываю учёбу",
    slug: "otkladyvayu-uchebu",
    problemType: "study_delay",
    intro:
      "Когда учёба постоянно откладывается, обещание «сесть на несколько часов» обычно только увеличивает сопротивление. Начнём с конкретного материала и короткого учебного блока.",
    examples: [
      "начать готовиться к экзамену",
      "сделать домашнее задание",
      "прочитать главу учебника",
    ],
    prompts: {
      inputLabel: "Что именно по учёбе вы откладываете?",
      placeholder: "Например: начать готовиться к экзамену по истории",
      buttonLabel: "Дай первый шаг",
    },
    seoTitle: "Откладываю учёбу — как начать с маленького шага",
    seoDescription:
      "Опишите учебную задачу и получите короткий первый шаг, с которого легче начать. Бесплатно и без регистрации.",
    status: "published",
    relatedSlugs: ["ne-mogu-nachat", "ne-znayu-s-chego-nachat"],
  },
  {
    title: "Задача кажется слишком большой",
    slug: "bolshaya-zadacha",
    problemType: "overwhelming_task",
    intro:
      "Большая задача парализует, когда в ней не видно границы первого действия. Сначала выделим небольшой видимый результат, который реально получить за один короткий подход.",
    examples: [
      "сделать большой рабочий проект",
      "подготовить диплом",
      "разобрать накопившиеся дела",
    ],
    prompts: {
      inputLabel: "Какая задача сейчас кажется слишком большой?",
      placeholder: "Например: подготовить дипломную работу",
      buttonLabel: "Разбить до первого шага",
    },
    seoTitle: "Задача кажется слишком большой — разбейте её до первого шага",
    seoDescription:
      "Интерактивно уменьшите большую задачу до одного выполнимого шага. Без регистрации, списков на сотню пунктов и давления.",
    status: "published",
    relatedSlugs: ["ne-mogu-nachat", "ne-znayu-s-chego-nachat"],
  },
  {
    title: "Не знаю, с чего начать",
    slug: "ne-znayu-s-chego-nachat",
    problemType: "unclear_start",
    intro:
      "Если непонятно, с чего начать, подробный план пока не нужен. Сначала превратим расплывчатую задачу в одно наблюдаемое действие, которое можно выполнить или хотя бы подготовить.",
    examples: [
      "начать новый проект",
      "заняться документами",
      "решить накопившуюся проблему",
    ],
    prompts: {
      inputLabel: "С чем вы не понимаете, как начать?",
      placeholder: "Например: начать новый проект для работы",
      buttonLabel: "Помоги найти первый шаг",
    },
    seoTitle: "Не знаю, с чего начать — найдите первое конкретное действие",
    seoDescription:
      "Введите расплывчатую или сложную задачу и получите первое конкретное действие. Бесплатный инструмент без регистрации.",
    status: "published",
    relatedSlugs: ["ne-mogu-nachat", "bolshaya-zadacha"],
  },
];

export const publishedProblemPages = problemPages.filter(
  (page) => page.status === "published",
);

export function getPublishedProblemPage(
  slug: string,
): ProblemPageDefinition | undefined {
  return publishedProblemPages.find((page) => page.slug === slug);
}

export function problemPagePath(page: ProblemPageDefinition): string {
  return `/procrastination/${page.slug}/`;
}
