from pathlib import Path

main_path = Path('lib/main.dart')
pubspec_path = Path('pubspec.yaml')
text = main_path.read_text(encoding='utf-8')

# Restore the distinct plans after the legacy lint helper rewrites SupportLogic.
start = text.index('  static StartPlan forProblem(String task, StartProblem problem) {')
end = text.index('\n  }\n}\n\nString problemName', start) + len('\n  }')
new_plan = '''  static StartPlan forProblem(String task, StartProblem problem) {
    final first = SupportLogic.steps(task).first;

    return switch (problem) {
      StartProblem.unclear => StartPlan(
        support: Support.ai,
        heading: 'Сначала уточните, что должно получиться',
        explanation:
            'Когда результат непонятен, трудно выбрать первое действие.',
        firstStep: first,
        small: SupportLogic.smallStep(task),
        shareButton: '',
      ),
      StartProblem.tooBig => StartPlan(
        support: Support.ai,
        heading: 'Выберите одну небольшую часть',
        explanation:
            'Не нужно выполнять всё дело сразу. Выберите часть, которую можно закончить за 10–15 минут.',
        firstStep: SupportLogic.smallPart(task),
        small: 'Потратьте на выбранную часть только 5 минут.',
        shareButton: '',
      ),
      StartProblem.noImpulse => const StartPlan(
        support: Support.together,
        heading: 'Начните одновременно с другим человеком',
        explanation:
            'Каждый может заниматься своим делом. Важно договориться об одном времени начала.',
        firstStep:
            'Отправьте знакомому сообщение и предложите начать одновременно.',
        small: 'Отправьте сообщение и начните сами хотя бы на 5 минут.',
        shareButton: 'Позвать человека',
      ),
      StartProblem.distracted => const StartPlan(
        support: Support.solo,
        heading: 'Уберите одно отвлечение и начните на 5 минут',
        explanation:
            'Не нужно обещать себе долгую работу. Сначала создайте пять спокойных минут.',
        firstStep:
            'Закройте лишнее приложение или уберите телефон подальше.',
        small: 'Сделайте только первые 5 минут дела.',
        shareButton: '',
      ),
      StartProblem.accountability => const StartPlan(
        support: Support.report,
        heading: 'Договоритесь, кому покажете результат',
        explanation:
            'Когда другой человек ждёт короткий итог, начать бывает легче.',
        firstStep:
            'Напишите знакомому, что начинаете и после дела отправите результат.',
        small: 'Отправьте итог даже после небольшой выполненной части.',
        shareButton: 'Сообщить о начале',
      ),
      StartProblem.reminder => const StartPlan(
        support: Support.curator,
        heading: 'Попросите знакомого напомнить',
        explanation:
            'Выберите человека и договоритесь, когда он напишет вам.',
        firstStep:
            'Отправьте просьбу и укажите точное время, когда нужно напомнить.',
        small: 'После напоминания начните хотя бы на 5 минут.',
        shareButton: 'Попросить напомнить',
      ),
    };
  }'''
text = text[:start] + new_plan + text[end:]

text = text.replace(
    "'Помощник предложит первый шаг, а позже рекомендации уточнятся по вашим результатам.'",
    "'Цифровой помощник предложит один понятный первый шаг.'",
)
text = text.replace(
    """    return [
      'Подготовьте всё необходимое для начала.',
      'Определите видимый результат короткой сессии.',
      'Сделайте первое действие, после которого процесс уже начался.',
    ];""",
    """    return [
      'Запишите, что должно быть готово в конце этого дела.',
      'Выберите первое действие, которое можно выполнить без подготовки.',
      'Начните с него и пока не планируйте остальное.',
    ];""",
)

if '  static String smallStep(String task) {' not in text:
    marker = """  static List<String> blockers(String task) {
    final first = steps(task).first;"""
    methods = """  static String smallStep(String task) {
    final normalized = n(task);
    if (has(normalized, ['убир', 'комнат', 'вещ', 'порядок', 'шкаф'])) {
      return 'Уберите только пять предметов.';
    }
    if (has(normalized, ['ремонт', 'почин', 'закреп', 'прикрут'])) {
      return 'Принесите один нужный инструмент.';
    }
    if (has(normalized, ['сайт', 'страниц', 'код', 'приложен'])) {
      return 'Откройте нужную страницу или проект.';
    }
    if (has(normalized, ['заряд', 'тренир', 'спорт', 'подтяг'])) {
      return 'Переоденьтесь и сделайте короткую разминку.';
    }
    if (has(normalized, ['доход', 'заработ', 'клиент'])) {
      return 'Запишите одно действие, которое может привести к доходу.';
    }
    return 'Откройте нужное место, файл или материал.';
  }

  static String smallPart(String task) {
    final normalized = n(task);
    if (has(normalized, ['убир', 'комнат', 'вещ', 'порядок', 'шкаф'])) {
      return 'Выберите одну полку, ящик или небольшой участок.';
    }
    if (has(normalized, ['ремонт', 'почин', 'закреп', 'прикрут'])) {
      return 'Сделайте только подготовку: осмотрите место и соберите инструменты.';
    }
    if (has(normalized, ['сайт', 'страниц', 'код', 'приложен'])) {
      return 'Сделайте только один блок страницы.';
    }
    if (has(normalized, ['заряд', 'тренир', 'спорт', 'подтяг'])) {
      return 'Выполните только разминку или один подход.';
    }
    if (has(normalized, ['доход', 'заработ', 'клиент'])) {
      return 'Сделайте один звонок, одно письмо или одно предложение.';
    }
    return 'Выберите одну часть, которую можно закончить за 10 минут.';
  }

  static List<String> blockers(String task) {
    final first = steps(task).first;"""
    if marker not in text:
        raise SystemExit('SupportLogic blocker marker not found')
    text = text.replace(marker, methods, 1)

main_path.write_text(text, encoding='utf-8')

pubspec = pubspec_path.read_text(encoding='utf-8')
pubspec = pubspec.replace('version: 0.3.0+4', 'version: 0.3.1+5')
pubspec_path.write_text(pubspec, encoding='utf-8')
