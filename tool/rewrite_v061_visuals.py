from pathlib import Path

main_path = Path('lib/main.dart')
pubspec_path = Path('pubspec.yaml')
text = main_path.read_text(encoding='utf-8')


def replace_class(source: str, name: str, next_name: str, replacement: str) -> str:
    start = source.index(f'class {name}')
    end = source.index(f'class {next_name}', start)
    return source[:start] + replacement.rstrip() + '\n\n' + source[end:]


def replace_section(source: str, start_marker: str, end_marker: str, replacement: str) -> str:
    start = source.index(start_marker)
    end = source.index(end_marker, start)
    return source[:start] + replacement.rstrip() + '\n' + source[end:]


THEME_TEXT = r'''        textTheme: const TextTheme(
          headlineLarge: TextStyle(
            color: ink,
            fontSize: 26,
            height: 1.08,
            fontWeight: FontWeight.w900,
            letterSpacing: -0.7,
          ),
          headlineMedium: TextStyle(
            color: ink,
            fontSize: 20,
            height: 1.16,
            fontWeight: FontWeight.w900,
            letterSpacing: -0.25,
          ),
          titleLarge: TextStyle(
            color: ink,
            fontSize: 17,
            fontWeight: FontWeight.w900,
          ),
          titleMedium: TextStyle(
            color: ink,
            fontSize: 15.5,
            fontWeight: FontWeight.w800,
          ),
          bodyLarge: TextStyle(color: ink, fontSize: 15, height: 1.38),
          bodyMedium: TextStyle(color: ink, fontSize: 14, height: 1.35),
        ),'''
text = replace_section(
    text,
    '        textTheme: const TextTheme(',
    '        cardTheme: CardThemeData(',
    THEME_TEXT,
)

THEME_CARD = r'''        cardTheme: CardThemeData(
          color: Colors.white,
          elevation: 0,
          shadowColor: const Color(0x100A2A26),
          surfaceTintColor: Colors.white,
          margin: EdgeInsets.zero,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
            side: const BorderSide(color: Color(0x14132D2A)),
          ),
        ),'''
text = replace_section(
    text,
    '        cardTheme: CardThemeData(',
    '        appBarTheme: const AppBarTheme(',
    THEME_CARD,
)

THEME_INPUT = r'''        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: Colors.white,
          isDense: true,
          contentPadding: const EdgeInsets.fromLTRB(14, 14, 48, 14),
          hintStyle: const TextStyle(
            color: Color(0xFF8A9591),
            fontSize: 13.5,
            height: 1.3,
          ),
          labelStyle: const TextStyle(fontSize: 14),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(15),
            borderSide: BorderSide.none,
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(15),
            borderSide: const BorderSide(color: Color(0xFFE1DED4)),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(15),
            borderSide: const BorderSide(color: green, width: 1.4),
          ),
        ),'''
text = replace_section(
    text,
    '        inputDecorationTheme: InputDecorationTheme(',
    '        filledButtonTheme: FilledButtonThemeData(',
    THEME_INPUT,
)

THEME_BUTTONS = r'''        filledButtonTheme: FilledButtonThemeData(
          style: FilledButton.styleFrom(
            backgroundColor: ink,
            minimumSize: const Size.fromHeight(46),
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 11),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(14),
            ),
            textStyle: const TextStyle(
              fontSize: 14.5,
              fontWeight: FontWeight.w800,
            ),
          ),
        ),
        outlinedButtonTheme: OutlinedButtonThemeData(
          style: OutlinedButton.styleFrom(
            minimumSize: const Size.fromHeight(44),
            padding: const EdgeInsets.symmetric(horizontal: 15, vertical: 10),
            side: const BorderSide(color: Color(0xFFB9C7C2)),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(14),
            ),
            textStyle: const TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w800,
            ),
          ),
        ),
        textButtonTheme: TextButtonThemeData(
          style: TextButton.styleFrom(
            visualDensity: VisualDensity.compact,
            textStyle: const TextStyle(fontWeight: FontWeight.w800),
          ),
        ),'''
text = replace_section(
    text,
    '        filledButtonTheme: FilledButtonThemeData(',
    '        navigationBarTheme: const NavigationBarThemeData(',
    THEME_BUTTONS,
)

THEME_NAV = r'''        navigationBarTheme: const NavigationBarThemeData(
          height: 64,
          backgroundColor: Colors.white,
          indicatorColor: mint,
          labelTextStyle: WidgetStatePropertyAll(
            TextStyle(fontSize: 11.5, fontWeight: FontWeight.w700),
          ),
        ),'''
text = replace_section(
    text,
    '        navigationBarTheme: const NavigationBarThemeData(',
    '      ),\n      home:',
    THEME_NAV,
)

ONBOARDING = r'''class Onboarding extends StatefulWidget {
  const Onboarding({required this.app, this.preview = false, super.key});
  final AppState app;
  final bool preview;

  @override
  State<Onboarding> createState() => _OnboardingState();
}

class _OnboardingState extends State<Onboarding> {
  final pages = PageController();
  int page = 0;

  void close() {
    if (widget.preview) {
      Navigator.pop(context);
    } else {
      widget.app.finish(Age.adult, '');
    }
  }

  void next() {
    if (page < 1) {
      pages.nextPage(
        duration: const Duration(milliseconds: 260),
        curve: Curves.easeOutCubic,
      );
    } else {
      close();
    }
  }

  @override
  void dispose() {
    pages.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    backgroundColor: ink,
    body: SafeArea(
      child: Column(
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(18, 8, 8, 0),
            child: Row(
              children: [
                const Logo(size: 30),
                const SizedBox(width: 9),
                const Text(
                  'Вместе к цели',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 17,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                const Spacer(),
                TextButton(
                  onPressed: close,
                  child: Text(
                    widget.preview ? 'Закрыть' : 'Пропустить',
                    style: const TextStyle(color: Colors.white70),
                  ),
                ),
              ],
            ),
          ),
          Expanded(
            child: PageView(
              controller: pages,
              onPageChanged: (value) => setState(() => page = value),
              children: [
                IntroPage(
                  icon: Icons.route_rounded,
                  kicker: 'ОДНА ЦЕЛЬ — БЛИЖАЙШИЙ ШАГ',
                  title: 'Видеть то, что важно сейчас',
                  text:
                      'Цель остаётся перед глазами, а путь собирается из небольших действий.',
                  points: const [
                    'Цель и действия находятся рядом',
                    'Шаг можно изменить или перенести',
                  ],
                  onPreviewTap: next,
                ),
                IntroPage(
                  icon: Icons.tune_rounded,
                  kicker: 'ПОДДЕРЖКА ПОД КОНКРЕТНОЕ ДЕЛО',
                  title: 'Подбирать условия, которые помогают',
                  text:
                      'Таймер, минимум, напоминание или человек рядом подключаются только по необходимости.',
                  points: const [
                    'Практика не исчезает после пропуска',
                    'Рабочие способы постепенно становятся заметны',
                  ],
                  onPreviewTap: next,
                ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.fromLTRB(18, 5, 18, 14),
            child: Column(
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: List.generate(
                    2,
                    (index) => AnimatedContainer(
                      duration: const Duration(milliseconds: 180),
                      margin: const EdgeInsets.all(3),
                      width: index == page ? 21 : 6,
                      height: 6,
                      decoration: BoxDecoration(
                        color: index == page ? mint : Colors.white24,
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 9),
                FilledButton(
                  style: FilledButton.styleFrom(
                    backgroundColor: mint,
                    foregroundColor: ink,
                  ),
                  onPressed: next,
                  child: Text(
                    page == 1
                        ? widget.preview
                              ? 'Вернуться'
                              : 'Начать'
                        : 'Дальше',
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    ),
  );
}'''
text = replace_class(
    text,
    'Onboarding extends StatefulWidget',
    'IntroPage extends StatelessWidget',
    ONBOARDING,
)

INTRO = r'''class IntroPage extends StatelessWidget {
  const IntroPage({
    required this.icon,
    required this.kicker,
    required this.title,
    required this.text,
    required this.points,
    required this.onPreviewTap,
    super.key,
  });

  final IconData icon;
  final String kicker, title, text;
  final List<String> points;
  final VoidCallback onPreviewTap;

  @override
  Widget build(BuildContext context) => ListView(
    padding: const EdgeInsets.fromLTRB(18, 8, 18, 12),
    children: [
      Material(
        color: Colors.transparent,
        child: InkWell(
          key: const ValueKey('onboarding-goal-preview'),
          onTap: onPreviewTap,
          borderRadius: BorderRadius.circular(20),
          child: Ink(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: const Color(0xFF1C4540),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: Colors.white10),
            ),
            child: Row(
              children: [
                Container(
                  width: 42,
                  height: 42,
                  decoration: BoxDecoration(
                    color: mint,
                    borderRadius: BorderRadius.circular(13),
                  ),
                  child: Icon(icon, color: ink, size: 23),
                ),
                const SizedBox(width: 12),
                const Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'ПРИМЕР ЦЕЛИ',
                        style: TextStyle(
                          color: Colors.white54,
                          fontSize: 9.5,
                          fontWeight: FontWeight.w900,
                          letterSpacing: 1,
                        ),
                      ),
                      SizedBox(height: 3),
                      Text(
                        'Доделать важный проект',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 15.5,
                          fontWeight: FontWeight.w900,
                        ),
                      ),
                    ],
                  ),
                ),
                Container(
                  width: 32,
                  height: 32,
                  decoration: const BoxDecoration(
                    color: Colors.white10,
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(
                    Icons.arrow_forward_rounded,
                    color: mint,
                    size: 19,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
      const SizedBox(height: 20),
      Text(
        kicker,
        style: const TextStyle(
          color: mint,
          fontSize: 10,
          fontWeight: FontWeight.w900,
          letterSpacing: 1,
        ),
      ),
      const SizedBox(height: 8),
      Text(
        title,
        style: const TextStyle(
          color: Colors.white,
          fontSize: 21,
          height: 1.12,
          fontWeight: FontWeight.w900,
          letterSpacing: -0.25,
        ),
      ),
      const SizedBox(height: 9),
      Text(
        text,
        style: const TextStyle(
          color: Color(0xFFD5E0DD),
          fontSize: 14.5,
          height: 1.38,
        ),
      ),
      const SizedBox(height: 13),
      ...points.map(
        (point) => Padding(
          padding: const EdgeInsets.only(bottom: 7),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Icon(Icons.check_circle_rounded, color: mint, size: 17),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  point,
                  style: const TextStyle(color: Colors.white, fontSize: 13.5),
                ),
              ),
            ],
          ),
        ),
      ),
    ],
  );
}'''
text = replace_class(
    text,
    'IntroPage extends StatelessWidget',
    'HowItWorksPage extends StatelessWidget',
    INTRO,
)

GOAL_GROUP = r'''class _GoalActionGroup extends StatelessWidget {
  const _GoalActionGroup({
    required this.app,
    required this.actions,
    required this.onOpenGoal,
  });

  final AppState app;
  final List<ActionItem> actions;
  final VoidCallback onOpenGoal;

  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.fromLTRB(10, 10, 10, 2),
    decoration: BoxDecoration(
      color: const Color(0xFFF0F6F3),
      borderRadius: BorderRadius.circular(17),
      border: Border.all(color: const Color(0x1939776B)),
    ),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        InkWell(
          onTap: onOpenGoal,
          borderRadius: BorderRadius.circular(12),
          child: Padding(
            padding: const EdgeInsets.fromLTRB(4, 1, 3, 8),
            child: Row(
              children: [
                const Icon(Icons.route_rounded, color: green, size: 18),
                const SizedBox(width: 7),
                Expanded(
                  child: Text(
                    '${app.goal!.title} · ${actions.length} в работе',
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      color: ink,
                      fontSize: 14,
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                ),
                const Icon(Icons.chevron_right_rounded, color: green, size: 21),
              ],
            ),
          ),
        ),
        if (actions.isEmpty)
          Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: EmptyAction(
              onTap: () => Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => ActionEditor(app: app, goalDefault: true),
                ),
              ),
            ),
          )
        else
          ...actions.asMap().entries.map(
            (entry) => Padding(
              padding: const EdgeInsets.only(bottom: 7),
              child: ActionCard(
                app: app,
                item: entry.value,
                featured: entry.key == 0,
              ),
            ),
          ),
      ],
    ),
  );
}'''
text = replace_class(
    text,
    '_GoalActionGroup extends StatelessWidget',
    '_PremiumTodayHeader extends StatelessWidget',
    GOAL_GROUP,
)

TODAY_HEADER = r'''class _PremiumTodayHeader extends StatelessWidget {
  const _PremiumTodayHeader({required this.count, required this.goalCount});
  final int count, goalCount;

  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
    decoration: BoxDecoration(
      color: const Color(0xFFF0F4F2),
      borderRadius: BorderRadius.circular(16),
    ),
    child: Row(
      children: [
        Container(
          width: 32,
          height: 32,
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(10),
          ),
          child: const Icon(Icons.wb_sunny_outlined, color: green, size: 18),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                count == 0 ? 'Сегодня свободно' : '$count ${taskWord(count)} на сегодня',
                style: const TextStyle(
                  color: ink,
                  fontSize: 16.5,
                  fontWeight: FontWeight.w900,
                ),
              ),
              const SizedBox(height: 1),
              Text(
                goalCount == 0
                    ? longToday()
                    : '$goalCount ${taskWord(goalCount)} для главной цели',
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(
                  color: Color(0xFF60706B),
                  fontSize: 11.5,
                ),
              ),
            ],
          ),
        ),
      ],
    ),
  );
}'''
text = replace_class(
    text,
    '_PremiumTodayHeader extends StatelessWidget',
    '_PremiumEmptyState extends StatelessWidget',
    TODAY_HEADER,
)

EMPTY_STATE = r'''class _PremiumEmptyState extends StatelessWidget {
  const _PremiumEmptyState();

  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.all(13),
    decoration: BoxDecoration(
      color: Colors.white,
      borderRadius: BorderRadius.circular(15),
      border: Border.all(color: const Color(0x14132D2A)),
    ),
    child: const Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(Icons.check_circle_outline_rounded, color: green, size: 24),
        SizedBox(width: 10),
        Expanded(
          child: Text(
            'На сегодня ничего не запланировано. Можно оставить день свободным или добавить одно дело.',
            style: TextStyle(fontSize: 13.5, height: 1.35),
          ),
        ),
      ],
    ),
  );
}'''
text = replace_class(
    text,
    '_PremiumEmptyState extends StatelessWidget',
    'IntentChooserPage extends StatelessWidget',
    EMPTY_STATE,
)

INTENT_CHOICE = r'''class _PremiumIntentChoice extends StatelessWidget {
  const _PremiumIntentChoice({
    required this.number,
    required this.icon,
    required this.color,
    required this.title,
    required this.text,
    required this.onTap,
  });

  final String number, title, text;
  final IconData icon;
  final Color color;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.only(bottom: 9),
    child: InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(17),
      child: Ink(
        padding: const EdgeInsets.all(13),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(17),
          border: Border.all(color: const Color(0x14132D2A)),
        ),
        child: Row(
          children: [
            Container(
              width: 42,
              height: 42,
              decoration: BoxDecoration(
                color: color,
                borderRadius: BorderRadius.circular(13),
              ),
              child: Icon(icon, color: ink, size: 22),
            ),
            const SizedBox(width: 11),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(
                      fontSize: 15.5,
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    text,
                    style: const TextStyle(
                      color: Color(0xFF596762),
                      fontSize: 12.5,
                      height: 1.3,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(width: 6),
            const Icon(Icons.chevron_right_rounded, color: green, size: 22),
          ],
        ),
      ),
    ),
  );
}'''
text = replace_class(
    text,
    '_PremiumIntentChoice extends StatelessWidget',
    'ReminderEditor extends StatefulWidget',
    INTENT_CHOICE,
)

CREATE_GOAL = r'''class CreateGoal extends StatelessWidget {
  const CreateGoal({required this.app, super.key});
  final AppState app;

  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.all(16),
    decoration: BoxDecoration(
      gradient: const LinearGradient(
        colors: [Color(0xFF173833), Color(0xFF35685F)],
      ),
      borderRadius: BorderRadius.circular(19),
    ),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Row(
          children: [
            Icon(Icons.flag_rounded, color: mint, size: 19),
            SizedBox(width: 7),
            Text(
              'ГЛАВНАЯ ЦЕЛЬ',
              style: TextStyle(
                color: mint,
                fontSize: 10,
                fontWeight: FontWeight.w900,
                letterSpacing: 1,
              ),
            ),
          ],
        ),
        const SizedBox(height: 9),
        const Text(
          'Добавьте одну важную цель',
          style: TextStyle(
            color: Colors.white,
            fontSize: 20,
            height: 1.12,
            fontWeight: FontWeight.w900,
          ),
        ),
        const SizedBox(height: 6),
        const Text(
          'Достаточно названия. Действия и детали можно добавлять постепенно.',
          style: TextStyle(
            color: Color(0xFFD7E2DF),
            fontSize: 13.5,
            height: 1.34,
          ),
        ),
        const SizedBox(height: 13),
        FilledButton.icon(
          style: FilledButton.styleFrom(
            backgroundColor: mint,
            foregroundColor: ink,
          ),
          onPressed: () => Navigator.push(
            context,
            MaterialPageRoute(builder: (_) => GoalEditor(app: app)),
          ),
          icon: const Icon(Icons.add_rounded, size: 19),
          label: const Text('Создать цель'),
        ),
      ],
    ),
  );
}'''
text = replace_class(
    text,
    'CreateGoal extends StatelessWidget',
    'GoalHero extends StatelessWidget',
    CREATE_GOAL,
)

GOAL_HERO = r'''class GoalHero extends StatelessWidget {
  const GoalHero({required this.app, this.onTap, super.key});
  final AppState app;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final goal = app.goal!;
    final total = app.goalDone + app.goalActive;
    final progress = total == 0 ? 0.0 : app.goalDone / total;
    final next = app.actions
        .where((item) => item.goal && item.state == null)
        .firstOrNull;

    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(19),
        child: Ink(
          padding: const EdgeInsets.all(15),
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [Color(0xFF102E2A), Color(0xFF356A61)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(19),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Text(
                    'ГЛАВНАЯ ЦЕЛЬ',
                    style: TextStyle(
                      color: mint,
                      fontSize: 9.5,
                      fontWeight: FontWeight.w900,
                      letterSpacing: 1,
                    ),
                  ),
                  const Spacer(),
                  if (onTap != null)
                    Container(
                      width: 30,
                      height: 30,
                      decoration: const BoxDecoration(
                        color: Colors.white10,
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(
                        Icons.arrow_forward_rounded,
                        color: Colors.white70,
                        size: 18,
                      ),
                    ),
                ],
              ),
              const SizedBox(height: 7),
              Text(
                goal.title,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 19.5,
                  height: 1.12,
                  fontWeight: FontWeight.w900,
                ),
              ),
              if (next != null) ...[
                const SizedBox(height: 5),
                Text(
                  'Сейчас: ${next.title}',
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    color: Color(0xFFD4E0DD),
                    fontSize: 12.5,
                  ),
                ),
              ],
              const SizedBox(height: 10),
              ClipRRect(
                borderRadius: BorderRadius.circular(8),
                child: LinearProgressIndicator(
                  value: progress,
                  minHeight: 4,
                  backgroundColor: Colors.white12,
                  valueColor: const AlwaysStoppedAnimation(mint),
                ),
              ),
              const SizedBox(height: 8),
              Text(
                '${app.goalDone} завершено  ·  ${app.goalActive} в работе  ·  ${goal.areas.length} этапов',
                style: const TextStyle(color: Colors.white60, fontSize: 10.5),
              ),
            ],
          ),
        ),
      ),
    );
  }
}'''
text = replace_class(
    text,
    'GoalHero extends StatelessWidget',
    'EmptyAction extends StatelessWidget',
    GOAL_HERO,
)

EMPTY_ACTION = r'''class EmptyAction extends StatelessWidget {
  const EmptyAction({required this.onTap, super.key});
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.all(13),
    decoration: BoxDecoration(
      color: Colors.white,
      borderRadius: BorderRadius.circular(14),
      border: Border.all(color: const Color(0x14132D2A)),
    ),
    child: Row(
      children: [
        const Expanded(
          child: Text(
            'Добавьте один небольшой шаг к цели.',
            style: TextStyle(fontSize: 13.5, fontWeight: FontWeight.w800),
          ),
        ),
        const SizedBox(width: 9),
        IconButton.filledTonal(
          onPressed: onTap,
          tooltip: 'Добавить действие',
          icon: const Icon(Icons.add_rounded),
        ),
      ],
    ),
  );
}'''
text = replace_class(
    text,
    'EmptyAction extends StatelessWidget',
    'ActionCard extends StatelessWidget',
    EMPTY_ACTION,
)

GOAL_EDITOR = r'''class GoalEditor extends StatefulWidget {
  const GoalEditor({required this.app, this.existing, super.key});
  final AppState app;
  final Goal? existing;

  @override
  State<GoalEditor> createState() => _GoalEditorState();
}

class _GoalEditorState extends State<GoalEditor> {
  late final TextEditingController title;
  late final TextEditingController result;
  late final TextEditingController areas;
  bool showDetails = false;

  @override
  void initState() {
    super.initState();
    title = TextEditingController(text: widget.existing?.title ?? '');
    result = TextEditingController(text: widget.existing?.result ?? '');
    areas = TextEditingController(
      text: widget.existing?.areas.join(', ') ?? '',
    );
    showDetails =
        widget.existing != null &&
        (widget.existing!.result.isNotEmpty || widget.existing!.areas.isNotEmpty);
    title.addListener(() => setState(() {}));
  }

  @override
  void dispose() {
    title.dispose();
    result.dispose();
    areas.dispose();
    super.dispose();
  }

  void save() {
    widget.app.setGoal(
      Goal(
        title.text.trim(),
        result.text.trim(),
        widget.existing?.minutes ?? 0,
        areas.text
            .split(RegExp(r'[,;\n]'))
            .map((item) => item.trim())
            .where((item) => item.isNotEmpty)
            .toList(),
        id: widget.existing?.id,
        createdAt: widget.existing?.createdAt,
        updatedAt: DateTime.now(),
      ),
    );

    if (widget.existing == null) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (_) => ActionEditor(app: widget.app, goalDefault: true),
        ),
      );
    } else {
      Navigator.pop(context);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(
      title: Text(widget.existing == null ? 'Новая цель' : 'Изменить цель'),
    ),
    body: ListView(
      padding: const EdgeInsets.fromLTRB(16, 3, 16, 24),
      children: [
        Container(
          padding: const EdgeInsets.all(13),
          decoration: BoxDecoration(
            color: const Color(0xFFF0F4F2),
            borderRadius: BorderRadius.circular(15),
          ),
          child: const Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(Icons.flag_outlined, color: green, size: 22),
              SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Чего вы хотите добиться?',
                      style: TextStyle(fontSize: 17, fontWeight: FontWeight.w900),
                    ),
                    SizedBox(height: 3),
                    Text(
                      'Сначала достаточно названия. Следующий шаг выберем отдельно.',
                      style: TextStyle(fontSize: 12.5, color: Color(0xFF60706B)),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 12),
        VoiceField(
          controller: title,
          label: 'Моя цель',
          hint: 'Например: доделать ремонт в доме',
          lines: 2,
        ),
        const SizedBox(height: 8),
        InkWell(
          onTap: () => setState(() => showDetails = !showDetails),
          borderRadius: BorderRadius.circular(14),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: const Color(0xFFE1DED4)),
            ),
            child: Row(
              children: [
                Icon(
                  showDetails ? Icons.expand_less : Icons.tune_rounded,
                  color: green,
                  size: 20,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    showDetails
                        ? 'Скрыть результат и этапы'
                        : 'Уточнить результат и этапы',
                    style: const TextStyle(
                      fontSize: 13.5,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
        if (showDetails) ...[
          const SizedBox(height: 10),
          VoiceField(
            controller: result,
            label: 'Желаемый результат · необязательно',
            hint: 'Что должно измениться или быть готово?',
            lines: 2,
          ),
          const SizedBox(height: 10),
          VoiceField(
            controller: areas,
            label: 'Этапы · необязательно',
            hint: 'Например: ванная, кухня, электрика, стены',
            lines: 2,
          ),
        ],
        const SizedBox(height: 14),
        FilledButton.icon(
          onPressed: title.text.trim().isEmpty ? null : save,
          icon: const Icon(Icons.check_rounded, size: 19),
          label: const Text('Сохранить цель'),
        ),
      ],
    ),
  );
}'''
text = replace_class(
    text,
    'GoalEditor extends StatefulWidget',
    'ActionEditor extends StatefulWidget',
    GOAL_EDITOR,
)

EDITOR_HEADING = r'''class _PremiumEditorHeading extends StatelessWidget {
  const _PremiumEditorHeading({
    required this.number,
    required this.title,
    required this.text,
  });
  final String number, title, text;

  @override
  Widget build(BuildContext context) => Row(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Container(
        width: 27,
        height: 27,
        alignment: Alignment.center,
        decoration: const BoxDecoration(color: ink, shape: BoxShape.circle),
        child: Text(
          number,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 12,
            fontWeight: FontWeight.w900,
          ),
        ),
      ),
      const SizedBox(width: 9),
      Expanded(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w900),
            ),
            const SizedBox(height: 2),
            Text(
              text,
              style: const TextStyle(
                color: Color(0xFF64716D),
                fontSize: 12.5,
                height: 1.3,
              ),
            ),
          ],
        ),
      ),
    ],
  );
}'''
text = replace_class(
    text,
    '_PremiumEditorHeading extends StatelessWidget',
    'Speech',
    EDITOR_HEADING,
)

VOICE_FIELD = r'''class VoiceField extends StatefulWidget {
  const VoiceField({
    required this.controller,
    required this.label,
    required this.hint,
    this.lines = 1,
    super.key,
  });
  final TextEditingController controller;
  final String label, hint;
  final int lines;

  @override
  State<VoiceField> createState() => _VoiceFieldState();
}

class _VoiceFieldState extends State<VoiceField> {
  bool listening = false;

  Future<void> mic() async {
    if (listening) {
      await Speech.i.engine.stop();
      if (mounted) setState(() => listening = false);
      return;
    }
    if (!await Speech.i.init()) {
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
    }
    setState(() => listening = true);
    await Speech.i.engine.listen(
      listenOptions: stt.SpeechListenOptions(localeId: 'ru_RU'),
      onResult: (result) {
        widget.controller.text = result.recognizedWords;
        widget.controller.selection = TextSelection.collapsed(
          offset: widget.controller.text.length,
        );
        if (result.finalResult && mounted) setState(() => listening = false);
      },
    );
  }

  @override
  Widget build(BuildContext context) => TextField(
    controller: widget.controller,
    maxLines: widget.lines,
    decoration: InputDecoration(
      labelText: widget.label,
      hintText: widget.hint,
      hintMaxLines: widget.lines > 1 ? widget.lines : 2,
      alignLabelWithHint: widget.lines > 1,
      suffixIconConstraints: const BoxConstraints(minWidth: 44, minHeight: 44),
      suffixIcon: Tooltip(
        message: listening ? 'Остановить запись' : 'Голосовой ввод',
        child: IconButton(
          onPressed: mic,
          visualDensity: VisualDensity.compact,
          icon: Icon(
            listening ? Icons.stop_circle_rounded : Icons.mic_none_rounded,
            color: listening ? Colors.red : green,
            size: 21,
          ),
        ),
      ),
    ),
  );
}'''
text = replace_class(
    text,
    'VoiceField extends StatefulWidget',
    'SupportTile extends StatelessWidget',
    VOICE_FIELD,
)

SUPPORT_SCREEN = r'''class SupportScreen extends StatelessWidget {
  const SupportScreen({required this.app, super.key});
  final AppState app;

  @override
  Widget build(BuildContext context) {
    final active = app.actions.where((item) => item.state == null).toList();

    return Scaffold(
      appBar: AppBar(title: const Text('Вместе')),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(16, 3, 16, 80),
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF244F49), Color(0xFF4B7F73)],
              ),
              borderRadius: BorderRadius.circular(19),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Row(
                  children: [
                    Icon(Icons.people_alt_rounded, color: mint, size: 23),
                    SizedBox(width: 8),
                    Text(
                      'Начать вместе',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 20,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                const Text(
                  'Договоритесь с человеком начать в одно время — даже если каждый делает своё.',
                  style: TextStyle(
                    color: Color(0xFFD8E5E1),
                    fontSize: 13.5,
                    height: 1.34,
                  ),
                ),
                if (active.isEmpty) ...[
                  const SizedBox(height: 12),
                  FilledButton.icon(
                    style: FilledButton.styleFrom(
                      backgroundColor: mint,
                      foregroundColor: ink,
                    ),
                    onPressed: () => Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (_) => ActionEditor(
                          app: app,
                          goalDefault: app.goal != null,
                          initialSupport: Support.together,
                        ),
                      ),
                    ),
                    icon: const Icon(Icons.add_task_rounded, size: 19),
                    label: const Text('Выбрать действие'),
                  ),
                ],
              ],
            ),
          ),
          if (active.isNotEmpty) ...[
            const SizedBox(height: 15),
            Text('Что будете делать?', style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 8),
            ...active.map(
              (item) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: TogetherActionCard(app: app, item: item),
              ),
            ),
          ],
          const SizedBox(height: 15),
          Text(
            'Другие способы поддержки',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: 8),
          _SimpleSupportCard(
            type: Support.ai,
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => ActionEditor(
                  app: app,
                  goalDefault: app.goal != null,
                  initialSupport: Support.ai,
                ),
              ),
            ),
          ),
          _SimpleSupportCard(
            type: Support.report,
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => ActionEditor(
                  app: app,
                  goalDefault: app.goal != null,
                  initialSupport: Support.report,
                ),
              ),
            ),
          ),
          _SimpleSupportCard(
            type: Support.curator,
            onPressed: () => showModalBottomSheet(
              context: context,
              isScrollControlled: true,
              showDragHandle: true,
              builder: (_) => CuratorSheet(app: app),
            ),
          ),
        ],
      ),
    );
  }
}'''
text = replace_class(
    text,
    'SupportScreen extends StatelessWidget',
    'TogetherActionCard extends StatelessWidget',
    SUPPORT_SCREEN,
)

# Compact the most frequently repeated action-card geometry without touching behavior.
action_start = text.index('class ActionCard extends StatelessWidget')
action_end = text.index('Future<DateTime?> showActionSchedule', action_start)
action = text[action_start:action_end]
action = action.replace('padding: const EdgeInsets.all(17)', 'padding: const EdgeInsets.all(14)')
action = action.replace('width: 44,\n                  height: 44,', 'width: 38,\n                  height: 38,')
action = action.replace('borderRadius: BorderRadius.circular(15)', 'borderRadius: BorderRadius.circular(12)', 1)
action = action.replace('const SizedBox(width: 12)', 'const SizedBox(width: 10)', 1)
action = action.replace('fontSize: 18,', 'fontSize: 16,', 1)
action = action.replace('const SizedBox(height: 11)', 'const SizedBox(height: 8)')
action = action.replace('padding: const EdgeInsets.all(12)', 'padding: const EdgeInsets.all(10)')
action = action.replace('const SizedBox(height: 13)', 'const SizedBox(height: 10)')
text = text[:action_start] + action + text[action_end:]

# Smaller global spacings on the most visible pages.
text = text.replace(
    "children: [Logo(size: 28), SizedBox(width: 9), Text('Вместе к цели')]",
    "children: [Logo(size: 24), SizedBox(width: 8), Text('Вместе к цели', style: TextStyle(fontSize: 17))]",
)
text = text.replace(
    'padding: const EdgeInsets.fromLTRB(16, 2, 16, 110)',
    'padding: const EdgeInsets.fromLTRB(14, 1, 14, 96)',
)
text = text.replace(
    "label: const Text('Добавить'),",
    "label: const Text('Добавить', style: TextStyle(fontSize: 13.5)),",
    1,
)

main_path.write_text(text, encoding='utf-8')

pubspec = pubspec_path.read_text(encoding='utf-8')
pubspec = pubspec.replace('version: 0.6.0+13', 'version: 0.6.1+14')
pubspec_path.write_text(pubspec, encoding='utf-8')
