from pathlib import Path

main_path = Path('lib/main.dart')
pubspec_path = Path('pubspec.yaml')
text = main_path.read_text(encoding='utf-8')


def replace(old: str, new: str) -> None:
    global text
    if old not in text:
        raise SystemExit(f'Expected fragment not found:\n{old[:240]}')
    text = text.replace(old, new, 1)


# Onboarding: human Russian, no promises that are not implemented yet.
replace(
    "'Одному бывает трудно довести важную цель до результата.'",
    "'Бывает, что цель важна, но одному трудно начать и не бросить.'",
)
replace(
    "'Это нормально. Человеку часто не хватает не силы воли, а поддержки: понятного следующего действия, напоминания или того, кто заметит его усилия.'",
    "'Это не всегда вопрос силы воли. Иногда не хватает понятного первого действия, напоминания или человека, который поддержит.'",
)
replace(
    "'После остановки поможет спокойно продолжить'",
    "'Пропуск не считается провалом'",
)
replace(
    "'Найдём то, что поможет именно вам.'",
    "'Для разных дел нужна разная помощь.'",
)
replace(
    "'Зарядку можно делать вместе. Результат тренировки — отправлять товарищу. Работу над сайтом — начинать одновременно с напарником. Иногда достаточно точного напоминания или помощи AI.'",
    "'Одно дело легче начать вместе. Для другого достаточно показать результат знакомому. Сложную задачу сначала полезно разобрать с цифровым помощником.'",
)
replace(
    "'Имя поможет обращаться к вам лично. Его можно не указывать. Возраст нужен, чтобы приложение подбирало понятные слова и примеры.'",
    "'Имя можно не указывать. Выберите свою возрастную группу.'",
)

# Greeting and Today screen.
replace(
    "String get hello => name.isEmpty ? 'Сегодня' : 'Сегодня, $name';",
    "String get hello => name.isEmpty ? 'С чего начнём?' : '$name, с чего начнём?';",
)
replace(
    """      appBar: AppBar(
        title: const Row(
          children: [
            Logo(size: 30),
            SizedBox(width: 10),
            Text('Вместе к цели'),
          ],
        ),
      ),""",
    """      appBar: AppBar(
        title: const Row(
          children: [
            Logo(size: 30),
            SizedBox(width: 10),
            Text('Вместе к цели'),
          ],
        ),
        actions: [
          IconButton(
            tooltip: 'Как это работает',
            icon: const Icon(Icons.info_outline_rounded),
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => const HowItWorksPage()),
            ),
          ),
        ],
      ),""",
)
replace(
    """          Text(app.hello, style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 5),
          const Text('Выберите дело или получите помощь, если трудно начать.'),""",
    """          Text('Сегодня', style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 5),
          Text(app.hello, style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 5),
          const Text(
            'Выберите дело из списка. Если снова откладываете его — разберёмся, что мешает.',
          ),""",
)
replace(
    "'Здесь появятся обычные дела, которые вы добавите на сегодня.'",
    "'Других дел на сегодня пока нет.'",
)

# Quick help card and flow labels.
replace("'БЫСТРАЯ ПОМОЩЬ'", "'КОГДА НЕ ПОЛУЧАЕТСЯ НАЧАТЬ'")
replace("'Трудно начать конкретное дело?'", "'Есть дело, которое вы откладываете?'")
replace(
    "'Назовите дело и выберите, что мешает. Приложение предложит первый шаг и способ помощи.'",
    "'Напишите, что нужно сделать, и выберите, почему вы не начинаете. Приложение предложит один конкретный способ начать.'",
)
replace("'Помочь мне начать'", "'Разобраться, что мешает'")
replace("title: const Text('Помочь начать'),", "title: const Text('Как начать это дело'),")

# Add an explicit exit from every wizard step.
replace(
    """        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () {
            if (stage == 0) {
              Navigator.pop(context);
            } else {
              setState(() => stage--);
            }
          },
        ),""",
    """        leading: IconButton(
          tooltip: 'Назад',
          icon: const Icon(Icons.arrow_back),
          onPressed: () {
            if (stage == 0) {
              Navigator.pop(context);
            } else {
              setState(() => stage--);
            }
          },
        ),
        actions: [
          IconButton(
            tooltip: 'Вернуться к делам',
            icon: const Icon(Icons.close_rounded),
            onPressed: () => Navigator.pop(context),
          ),
        ],""",
)
replace("'Что вам нужно начать?'", "'Какое дело вы откладываете?'")
replace(
    "'Назовите одно дело, которое вы откладываете прямо сейчас.'",
    "'Запишите одно конкретное дело.'",
)
replace(
    "'Например: начать делать страницу сайта'",
    "'Например: написать текст для первого экрана сайта'",
)
replace(
    "'Это дело можно не добавлять в главную цель. Быстрая помощь работает и для обычных задач.'",
    "'Это может быть и обычное дело, не связанное с главной целью.'",
)
replace("'Что мешает начать?'", "'Почему вы не начинаете?'")
replace("'Подобрать помощь'", "'Показать, что можно сделать'")
replace("'Вот с чего можно начать'", "'Что можно сделать сейчас'")
replace("'Первое действие'", "'Сделайте сначала'")
replace("'Если сил мало'", "'Если совсем нет сил'")
replace("'Сколько времени начать сейчас?'", "'Сколько времени вы готовы уделить сейчас?'")
replace("'Сохранить на сегодня'", "'Добавить в дела на сегодня'")

# Natural problem wording.
replace(
    "'Понимаю, что делать, но не могу заставить себя начать'",
    "'Понимаю, что делать, но всё равно откладываю'",
)
replace(
    "'Нужен человек, которому я пообещаю результат'",
    "'Мне легче, когда кто-то ждёт от меня результат'",
)
replace(
    "'Боюсь снова забыть или отложить'",
    "'Без напоминания я снова отложу'",
)

# Replace the whole plan generator to avoid duplicated generic advice.
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

# Goal and action copy.
replace("'Чего вам пока не удаётся добиться?'", "'Чего вы хотите добиться?'")
replace("child: const Text('Выбрать цель'),", "child: const Text('Добавить главную цель'),")
replace("_metric('${app.goalDone}', 'действий')", "_metric('${app.goalDone}', 'сделано')")
replace("_metric('${g.minutes} мин', 'обычный блок')", "_metric('${g.minutes} мин', 'за один раз')")
replace("_metric('${g.areas.length}', 'направлений')", "_metric('${g.areas.length}', 'частей цели')")
replace(
    "'Здесь собраны желаемый результат и части работы, которые к нему ведут.'",
    "'Здесь видно, чего вы хотите добиться и что для этого нужно сделать.'",
)
replace("'Какой результат я хочу получить?'", "'Как вы поймёте, что цель достигнута?'")
replace(
    "'Выберите одно конкретное действие, которое можно начать без долгой подготовки.'",
    "'Запишите одно конкретное дело, которое хотите выполнить сегодня.'",
)
replace(
    "'Если времени или сил будет мало, что вы всё равно сможете сделать?'",
    "'Что вы сможете сделать хотя бы частично?'",
)
replace("'Например: подготовить инструменты'", "'Например: только подготовить инструменты'")
replace(
    "'Можно попробовать: ${supportName(rec.$1)}. ${rec.$2}'",
    "'Для этого дела может подойти: ${supportName(rec.$1)}. ${rec.$2}'",
)

# Support naming and descriptions.
replace("Support.ai => 'С AI-помощником'", "Support.ai => 'С цифровым помощником'")
replace("Support.together => 'Действовать вместе'", "Support.together => 'Начать вместе'")
replace(
    "Support.solo => 'Приложение напомнит и сохранит результат.'",
    "Support.solo => 'Запустить таймер и сохранить результат без участия других людей.'",
)
replace(
    "Support.ai => 'Поможет понять, с чего начать и что делать дальше.'",
    "Support.ai => 'Помощник предложит первый шаг и короткий план.'",
)
replace(
    "Support.together => 'Начать одновременно, даже если у вас разные дела.'",
    "Support.together => 'Вы и другой человек начинаете одновременно. Делать можно разные дела.'",
)
replace(
    "Support.report => 'Показать знакомому, что вы действительно сделали.'",
    "Support.report => 'После дела отправить знакомому фото, видео или короткий итог.'",
)
replace(
    "Support.curator => 'Человек напомнит, спросит и поможет продолжить.'",
    "Support.curator => 'Знакомый напоминает, спрашивает о результате и поддерживает.'",
)
replace(
    "'Выберите человека, который согласен напоминать, спрашивать, что получилось, и помогать продолжить после пропуска. Он не управляет вашей целью.'",
    "'Выберите знакомого, который согласен напоминать и спрашивать о результате. Куратор не контролирует вас: его задача — напомнить и поддержать.'",
)
replace("child: const Text('Сохранить имя куратора'),", "child: const Text('Сохранить'),")
replace(
    "'Реальные приглашения и уведомления куратору появятся после подключения серверной части.'",
    "'Пока приложение не отправляет сообщения автоматически. Связаться с куратором можно через привычный мессенджер.'",
)

# Session and result copy.
replace("'Первые понятные действия'", "'С чего начать'")
replace(
    "'Никаких лишних сообщений. Приложение сохранит время, контекст и итог.'",
    "'Работайте самостоятельно. Таймер покажет время, а результат сохранится в истории.'",
)
replace(
    "'Совместный старт может объединять одинаковые или разные дела.'",
    "'Вы и другой человек начинаете одновременно. Делать можно одно и то же или разные дела.'",
)
replace(
    "'Решите, чем подтвердите результат: фото, видео, ссылкой или цифрой.'",
    "'Решите, что отправите после дела: фото, видео, ссылку или короткий итог.'",
)
replace(
    "'Выберите конкретное препятствие прямо сейчас.'",
    "'Выберите, что мешает именно сейчас.'",
)
replace("'Перенести и вернуться'", "'Отложить на потом'")
replace("ResultState.moved => 'Перенесено без обнуления'", "ResultState.moved => 'Отложено на потом'")
replace("child: const Text('Вернуться на сегодня'),", "child: const Text('Вернуться к делам на сегодня'),")

# Better generic guidance and distinct small steps.
marker = """  static List<String> blockers(String task) {
    final first = steps(task).first;"""
insert = """  static String smallStep(String task) {
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
replace(marker, insert)
replace(
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
replace(
    "'Помощник предложит первый шаг, а позже рекомендации уточнятся по вашим результатам.'",
    "'Цифровой помощник предложит один понятный первый шаг.'",
)

# Insert a readable introduction page before the main shell.
how_it_works = r'''
class HowItWorksPage extends StatelessWidget {
  const HowItWorksPage({super.key});

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Как это работает')),
    body: ListView(
      padding: const EdgeInsets.fromLTRB(18, 4, 18, 32),
      children: [
        Text(
          'Не обязательно справляться в одиночку',
          style: Theme.of(context).textTheme.headlineMedium,
        ),
        const SizedBox(height: 9),
        const Text(
          'Бывает, что цель важна, но начать или продолжать одному трудно. Это не всегда вопрос силы воли: иногда не хватает ясного первого действия, напоминания или человека рядом.',
        ),
        const SizedBox(height: 18),
        const _InfoCard(
          icon: Icons.auto_awesome_rounded,
          title: 'Разобраться с делом',
          text:
              'Если задача непонятна или кажется слишком большой, цифровой помощник предложит первый шаг или небольшую часть.',
        ),
        const _InfoCard(
          icon: Icons.people_alt_rounded,
          title: 'Начать вместе',
          text:
              'Можно договориться с человеком начать одновременно, даже если каждый занимается своим делом.',
        ),
        const _InfoCard(
          icon: Icons.ios_share_rounded,
          title: 'Показать результат',
          text:
              'После дела можно отправить знакомому фото, видео, ссылку или короткий итог.',
        ),
        const _InfoCard(
          icon: Icons.verified_user_outlined,
          title: 'Попросить куратора',
          text:
              'Знакомый может напомнить, спросить о результате и поддержать после пропуска.',
        ),
        const SizedBox(height: 8),
        const Text(
          'Начните с одного дела',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.w900),
        ),
        const SizedBox(height: 8),
        const Text(
          'Запишите, что хотите сделать сегодня. Если не получается начать, выберите, что мешает, и приложение предложит подходящий вариант.',
        ),
      ],
    ),
  );
}

class _InfoCard extends StatelessWidget {
  const _InfoCard({
    required this.icon,
    required this.title,
    required this.text,
  });

  final IconData icon;
  final String title;
  final String text;

  @override
  Widget build(BuildContext context) => Card(
    margin: const EdgeInsets.only(bottom: 10),
    child: Padding(
      padding: const EdgeInsets.all(17),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 44,
            height: 44,
            decoration: BoxDecoration(
              color: mint,
              borderRadius: BorderRadius.circular(14),
            ),
            child: Icon(icon, color: ink),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 17,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                const SizedBox(height: 4),
                Text(text),
              ],
            ),
          ),
        ],
      ),
    ),
  );
}
'''
replace('class Shell extends StatefulWidget {', how_it_works + '\nclass Shell extends StatefulWidget {')

main_path.write_text(text, encoding='utf-8')

pubspec = pubspec_path.read_text(encoding='utf-8')
pubspec = pubspec.replace('version: 0.3.0+4', 'version: 0.3.1+5')
pubspec_path.write_text(pubspec, encoding='utf-8')
