from pathlib import Path

path = Path("lib/main.dart")
text = path.read_text(encoding="utf-8")

text = text.replace(
    """      if (j['goal'] != null)
        goal = Goal.fromJson(Map<String, dynamic>.from(j['goal']));""",
    """      if (j['goal'] != null) {
        goal = Goal.fromJson(Map<String, dynamic>.from(j['goal']));
      }""",
)

text = text.replace(
    "builder: (_, __) => MaterialApp(",
    "builder: (context, child) => MaterialApp(",
)

text = text.replace(
    """    if (!await Speech.i.init()) {
      if (mounted)
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text(
              'Голосовой ввод недоступен. Проверьте разрешение микрофона.',
            ),
          ),
        );
      return;
    }""",
    """    if (!await Speech.i.init()) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text(
              'Голосовой ввод недоступен. Проверьте разрешение микрофона.',
            ),
          ),
        );
      }
      return;
    }""",
)

text = text.replace(
    """    await Speech.i.engine.listen(
      localeId: 'ru_RU',
      onResult: (r) {""",
    """    await Speech.i.engine.listen(
      listenOptions: const stt.SpeechListenOptions(localeId: 'ru_RU'),
      onResult: (r) {""",
)

support_logic = r'''class SupportLogic {
  static String n(String value) => value.toLowerCase().replaceAll('ё', 'е');

  static bool has(String value, List<String> words) =>
      words.any(value.contains);

  static (Support, String) recommend(String task) {
    final normalized = n(task);

    if (normalized.trim().isEmpty) {
      return (
        Support.ai,
        'После описания действия рекомендация станет точнее.',
      );
    }
    if (has(normalized, ['заряд', 'тренир', 'подтяг', 'бег', 'спорт'])) {
      return (
        Support.together,
        'Физические действия часто легче сохранять при одновременном старте или обмене результатами.',
      );
    }
    if (has(normalized, ['доход', 'заработ', 'клиент', 'продаж'])) {
      return (
        Support.curator,
        'Для долгой финансовой цели полезна регулярная подотчётность по конкретным действиям.',
      );
    }
    if (has(normalized, [
      'сайт',
      'страниц',
      'код',
      'приложен',
      'книга',
      'проект',
    ])) {
      return (
        Support.ai,
        'Сложную работу полезно сначала разложить на ближайшие понятные действия.',
      );
    }
    if (has(normalized, ['убрать комнат', 'уборк', 'порядок'])) {
      return (
        Support.together,
        'Простую уборку можно выполнять параллельно и подтвердить результат.',
      );
    }
    if (has(normalized, ['ремонт', 'почин', 'закреп', 'прикрут'])) {
      return (
        Support.ai,
        'Ремонт чаще выполняется самостоятельно, но выигрывает от подготовки и последовательности.',
      );
    }
    if (has(normalized, ['позвон', 'забрать', 'купить', 'оплатить'])) {
      return (
        Support.solo,
        'Здесь обычно достаточно точного напоминания и ясного результата.',
      );
    }

    return (
      Support.ai,
      'Помощник предложит первый шаг, а позже рекомендации уточнятся по вашим результатам.',
    );
  }

  static List<String> steps(String task) {
    final normalized = n(task);

    if (has(normalized, ['убир', 'комнат', 'вещ', 'порядок', 'шкаф'])) {
      return [
        'Выберите одну конкретную зону, а не всё помещение.',
        'Подготовьте пакет для мусора и место для вещей без постоянного места.',
        'Начните с пяти предметов, решение по которым очевидно.',
      ];
    }
    if (has(normalized, ['ремонт', 'почин', 'закреп', 'прикрут'])) {
      return [
        'Назовите видимый результат работы.',
        'Соберите инструменты и материалы в одной точке.',
        'Сделайте первый необратимый шаг: снять, очистить или разметить.',
      ];
    }
    if (has(normalized, ['сайт', 'страниц', 'код', 'приложен'])) {
      return [
        'Откройте нужный проект или страницу.',
        'Определите один готовый результат этой сессии.',
        'Сделайте первый самостоятельный блок, не редактируя всё сразу.',
      ];
    }
    if (has(normalized, ['заряд', 'тренир', 'спорт', 'подтяг'])) {
      return [
        'Подготовьте место и всё необходимое.',
        'Начните с короткой разминки или первого лёгкого подхода.',
        'Зафиксируйте повторения, время или другой результат.',
      ];
    }
    if (has(normalized, ['доход', 'заработ', 'клиент'])) {
      return [
        'Выберите действие, которое может привести к доходу.',
        'Определите объём: один звонок, три предложения или готовый блок.',
        'После выполнения отправьте короткий отчёт.',
      ];
    }

    return [
      'Подготовьте всё необходимое для начала.',
      'Определите видимый результат короткой сессии.',
      'Сделайте первое действие, после которого процесс уже начался.',
    ];
  }

  static List<String> blockers(String task) {
    final first = steps(task).first;
    return [
      'Неясно, с чего начать — попробуйте: «$first»',
      'Действие слишком большое — сократите его до первой завершённой части.',
      'Не хватает предмета или информации — запишите, что нужно получить.',
      'Отвлекают другие дела — запишите их одной строкой и вернитесь к текущему.',
    ];
  }
}
'''

start = text.index("class SupportLogic {")
end = text.index("String supportName(", start)
text = text[:start] + support_logic + "\n" + text[end:]

path.write_text(text, encoding="utf-8")
