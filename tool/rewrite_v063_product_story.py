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


# Existing users see the rebuilt product introduction once without losing data.
text = text.replace(
    '  bool onboarded = false;\n',
    '  bool onboarded = false;\n  int onboardingVersion = 0;\n',
    1,
)
text = text.replace(
    "      onboarded = j['onboarded'] ?? false;\n",
    "      onboarded = j['onboarded'] ?? false;\n"
    "      onboardingVersion = j['onboardingVersion'] ?? 0;\n"
    "      if (onboarded && onboardingVersion < 3) onboarded = false;\n",
    1,
)
text = text.replace(
    "    'onboarded': onboarded,\n",
    "    'onboarded': onboarded,\n    'onboardingVersion': onboardingVersion,\n",
    1,
)
text = text.replace(
    '    onboarded = true;\n    notifyListeners();',
    '    onboarded = true;\n    onboardingVersion = 3;\n    notifyListeners();',
    1,
)

THEME_TEXT = r'''        textTheme: const TextTheme(
          headlineLarge: TextStyle(
            color: ink,
            fontSize: 27,
            height: 1.08,
            fontWeight: FontWeight.w700,
            letterSpacing: -0.55,
          ),
          headlineMedium: TextStyle(
            color: ink,
            fontSize: 22,
            height: 1.14,
            fontWeight: FontWeight.w700,
            letterSpacing: -0.3,
          ),
          titleLarge: TextStyle(
            color: ink,
            fontSize: 17,
            fontWeight: FontWeight.w700,
          ),
          titleMedium: TextStyle(
            color: ink,
            fontSize: 15.5,
            fontWeight: FontWeight.w600,
          ),
          bodyLarge: TextStyle(color: ink, fontSize: 15, height: 1.42),
          bodyMedium: TextStyle(color: ink, fontSize: 14, height: 1.38),
        ),'''
text = replace_section(
    text,
    '        textTheme: const TextTheme(',
    '        cardTheme: CardThemeData(',
    THEME_TEXT,
)

THEME_INPUT = r'''        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: Colors.white,
          isDense: true,
          contentPadding: const EdgeInsets.fromLTRB(14, 15, 48, 15),
          hintStyle: const TextStyle(
            color: Color(0xFF89938F),
            fontSize: 13.5,
            height: 1.32,
          ),
          labelStyle: const TextStyle(fontSize: 14, fontWeight: FontWeight.w500),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide: BorderSide.none,
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide: const BorderSide(color: Color(0xFFE2DED4)),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
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
            minimumSize: const Size.fromHeight(47),
            padding: const EdgeInsets.symmetric(horizontal: 17, vertical: 12),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(14),
            ),
            textStyle: const TextStyle(
              fontSize: 14.5,
              fontWeight: FontWeight.w700,
            ),
          ),
        ),
        outlinedButtonTheme: OutlinedButtonThemeData(
          style: OutlinedButton.styleFrom(
            minimumSize: const Size.fromHeight(45),
            padding: const EdgeInsets.symmetric(horizontal: 15, vertical: 11),
            side: const BorderSide(color: Color(0xFFBAC7C2)),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(14),
            ),
            textStyle: const TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
        textButtonTheme: TextButtonThemeData(
          style: TextButton.styleFrom(
            visualDensity: VisualDensity.compact,
            textStyle: const TextStyle(fontWeight: FontWeight.w600),
          ),
        ),'''
text = replace_section(
    text,
    '        filledButtonTheme: FilledButtonThemeData(',
    '        navigationBarTheme: const NavigationBarThemeData(',
    THEME_BUTTONS,
)

LOGO = r'''class Logo extends StatelessWidget {
  const Logo({this.size = 44, super.key});
  final double size;

  @override
  Widget build(BuildContext context) => Container(
    width: size,
    height: size,
    decoration: BoxDecoration(
      color: const Color(0xFFE5EFEB),
      borderRadius: BorderRadius.circular(size * .3),
      border: Border.all(color: const Color(0x1F39776B)),
    ),
    child: Icon(Icons.route_rounded, color: green, size: size * .56),
  );
}'''
text = replace_class(text, 'Logo extends StatelessWidget', 'Onboarding extends StatefulWidget', LOGO)

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
    pages.nextPage(
      duration: const Duration(milliseconds: 260),
      curve: Curves.easeOutCubic,
    );
  }

  void createGoal() {
    if (widget.preview) {
      Navigator.pop(context);
      return;
    }
    final hasGoal = widget.app.goal != null;
    widget.app.finish(Age.adult, '');
    if (!hasGoal) {
      Navigator.of(context).push(
        MaterialPageRoute(builder: (_) => GoalEditor(app: widget.app)),
      );
    }
  }

  @override
  void dispose() {
    pages.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    backgroundColor: cream,
    body: SafeArea(
      child: Column(
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(18, 10, 10, 3),
            child: Row(
              children: [
                const Logo(size: 29),
                const SizedBox(width: 9),
                const Text(
                  'Вместе к цели',
                  style: TextStyle(
                    color: ink,
                    fontSize: 16,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const Spacer(),
                TextButton(
                  onPressed: close,
                  child: Text(widget.preview ? 'Закрыть' : 'Пропустить'),
                ),
              ],
            ),
          ),
          Expanded(
            child: PageView(
              controller: pages,
              onPageChanged: (value) => setState(() => page = value),
              children: const [
                _ProductStoryPage(),
                _SupportStoryPage(),
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
                      margin: const EdgeInsets.symmetric(horizontal: 3),
                      width: index == page ? 22 : 7,
                      height: 6,
                      decoration: BoxDecoration(
                        color: index == page ? green : const Color(0xFFD2D8D5),
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 10),
                FilledButton(
                  key: ValueKey(page == 0 ? 'onboarding-next' : 'onboarding-create-goal'),
                  onPressed: page == 0 ? next : createGoal,
                  child: Text(
                    page == 0
                        ? 'Дальше'
                        : widget.preview
                        ? 'Закрыть'
                        : widget.app.goal == null
                        ? 'Создать первую цель'
                        : 'Продолжить',
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    ),
  );
}

class _ProductStoryPage extends StatelessWidget {
  const _ProductStoryPage();

  @override
  Widget build(BuildContext context) => ListView(
    key: const ValueKey('product-story-page'),
    padding: const EdgeInsets.fromLTRB(18, 10, 18, 10),
    children: [
      const Text(
        'НЕ ПРОСТО СПИСОК ДЕЛ',
        style: TextStyle(
          color: green,
          fontSize: 10.5,
          fontWeight: FontWeight.w700,
          letterSpacing: 1,
        ),
      ),
      const SizedBox(height: 9),
      const Text(
        'Найдите свой способ двигаться к цели',
        style: TextStyle(
          color: ink,
          fontSize: 28,
          height: 1.08,
          fontWeight: FontWeight.w700,
          letterSpacing: -0.55,
        ),
      ),
      const SizedBox(height: 12),
      const Text(
        '«Вместе к цели» помогает превратить важную цель в конкретные действия, подобрать подходящую поддержку и постепенно понять, какие условия помогают именно вам начинать и доводить дела до результата.',
        style: TextStyle(fontSize: 14.5, height: 1.42, color: Color(0xFF4F5D59)),
      ),
      const SizedBox(height: 15),
      Container(
        padding: const EdgeInsets.symmetric(horizontal: 13, vertical: 14),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: const Color(0x1739776B)),
        ),
        child: const Row(
          children: [
            Expanded(child: _StoryStep(icon: Icons.flag_outlined, text: 'Цель')),
            Icon(Icons.arrow_forward_rounded, color: Color(0xFF8B9692), size: 18),
            Expanded(child: _StoryStep(icon: Icons.route_rounded, text: 'Шаг')),
            Icon(Icons.arrow_forward_rounded, color: Color(0xFF8B9692), size: 18),
            Expanded(child: _StoryStep(icon: Icons.support_outlined, text: 'Поддержка')),
          ],
        ),
      ),
      const SizedBox(height: 11),
      const _StoryNote(
        icon: Icons.inbox_outlined,
        text:
            'А остальные дела можно быстро записать, запланировать или сохранить как регулярную практику — чтобы не держать всё в голове.',
      ),
      const SizedBox(height: 9),
      const _StoryNote(
        icon: Icons.science_outlined,
        text:
            'С опорой на исследования о планировании действий, формировании привычек, обратной связи и социальной поддержке.',
      ),
    ],
  );
}

class _SupportStoryPage extends StatelessWidget {
  const _SupportStoryPage();

  @override
  Widget build(BuildContext context) => ListView(
    key: const ValueKey('support-story-page'),
    padding: const EdgeInsets.fromLTRB(18, 10, 18, 10),
    children: const [
      Text(
        'НЕ ВСЕМ ПОМОГАЕТ ОДИН И ТОТ ЖЕ СПОСОБ',
        style: TextStyle(
          color: green,
          fontSize: 10.5,
          fontWeight: FontWeight.w700,
          letterSpacing: .85,
        ),
      ),
      SizedBox(height: 8),
      Text(
        'Подберите поддержку под конкретное действие',
        style: TextStyle(
          color: ink,
          fontSize: 25,
          height: 1.1,
          fontWeight: FontWeight.w700,
          letterSpacing: -.4,
        ),
      ),
      SizedBox(height: 10),
      Text(
        'Одно дело легче начать самостоятельно. Для другого может понадобиться цифровой помощник, совместное присутствие или человек, перед которым вы договорились отчитаться.',
        style: TextStyle(fontSize: 14, height: 1.38, color: Color(0xFF4F5D59)),
      ),
      SizedBox(height: 12),
      _OnboardingSupportRow(
        icon: Icons.person_outline_rounded,
        title: 'Самостоятельно',
        text: 'Выполнить действие с таймером или без него.',
      ),
      _OnboardingSupportRow(
        icon: Icons.auto_awesome_outlined,
        title: 'С цифровым помощником',
        text: 'Разобрать большую задачу и выбрать выполнимый первый шаг.',
      ),
      _OnboardingSupportRow(
        icon: Icons.video_call_outlined,
        title: 'Вместе с человеком',
        text:
            'Начать одновременно или оставаться на аудио- или видеосвязи, пока каждый занимается своим делом.',
      ),
      _OnboardingSupportRow(
        icon: Icons.verified_outlined,
        title: 'С отчётом или куратором',
        text: 'Показать результат, попросить напомнить и поддержать после пропуска.',
      ),
      SizedBox(height: 4),
      _StoryNote(
        icon: Icons.playlist_add_check_circle_outlined,
        text:
            'Не каждое дело должно становиться большой целью. Напоминания, разовые дела и регулярные практики сохраняются отдельно.',
      ),
      SizedBox(height: 8),
      Text(
        'Приложение будет постепенно замечать, какие способы чаще помогают именно вам.',
        style: TextStyle(color: green, fontSize: 13, height: 1.35, fontWeight: FontWeight.w600),
      ),
    ],
  );
}

class _StoryStep extends StatelessWidget {
  const _StoryStep({required this.icon, required this.text});
  final IconData icon;
  final String text;

  @override
  Widget build(BuildContext context) => Column(
    children: [
      Icon(icon, color: green, size: 21),
      const SizedBox(height: 5),
      Text(text, style: const TextStyle(fontSize: 12.5, fontWeight: FontWeight.w600)),
    ],
  );
}

class _StoryNote extends StatelessWidget {
  const _StoryNote({required this.icon, required this.text});
  final IconData icon;
  final String text;

  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.all(12),
    decoration: BoxDecoration(
      color: const Color(0xFFF0F4F2),
      borderRadius: BorderRadius.circular(14),
    ),
    child: Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, color: green, size: 20),
        const SizedBox(width: 9),
        Expanded(child: Text(text, style: const TextStyle(fontSize: 12.8, height: 1.35))),
      ],
    ),
  );
}

class _OnboardingSupportRow extends StatelessWidget {
  const _OnboardingSupportRow({required this.icon, required this.title, required this.text});
  final IconData icon;
  final String title, text;

  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.only(bottom: 7),
    child: Container(
      padding: const EdgeInsets.fromLTRB(10, 9, 10, 9),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0x14132D2A)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 34,
            height: 34,
            decoration: BoxDecoration(
              color: const Color(0xFFE7F0EC),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(icon, color: green, size: 19),
          ),
          const SizedBox(width: 9),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(fontSize: 13.5, fontWeight: FontWeight.w700)),
                const SizedBox(height: 2),
                Text(text, style: const TextStyle(fontSize: 12, height: 1.3, color: Color(0xFF5B6864))),
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
    'HowItWorksPage extends StatelessWidget',
    ONBOARDING,
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
    areas = TextEditingController(text: widget.existing?.areas.join(', ') ?? '');
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
    appBar: AppBar(title: Text(widget.existing == null ? 'Главная цель' : 'Изменить цель')),
    body: ListView(
      padding: const EdgeInsets.fromLTRB(16, 5, 16, 22),
      children: [
        const Text(
          'ВАША ГЛАВНАЯ ЦЕЛЬ',
          style: TextStyle(
            color: green,
            fontSize: 10.5,
            fontWeight: FontWeight.w700,
            letterSpacing: 1,
          ),
        ),
        const SizedBox(height: 7),
        const Text(
          'Чего вы хотите добиться?',
          style: TextStyle(
            color: ink,
            fontSize: 24,
            height: 1.1,
            fontWeight: FontWeight.w700,
            letterSpacing: -.35,
          ),
        ),
        const SizedBox(height: 8),
        const Text(
          'Назовите одну цель, которая сейчас для вас действительно важна. Не нужно сразу продумывать весь путь — начнём с ближайшего выполнимого действия.',
          style: TextStyle(color: Color(0xFF56635F), fontSize: 13.5, height: 1.38),
        ),
        const SizedBox(height: 14),
        VoiceField(
          controller: title,
          label: 'Моя цель',
          hint: 'Например: закончить ремонт, подготовиться к экзамену, запустить свой проект',
          lines: 3,
        ),
        const SizedBox(height: 9),
        InkWell(
          onTap: () => setState(() => showDetails = !showDetails),
          borderRadius: BorderRadius.circular(14),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: const Color(0xFFE2DED4)),
            ),
            child: Row(
              children: [
                Icon(showDetails ? Icons.expand_less : Icons.tune_rounded, color: green, size: 20),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    showDetails ? 'Скрыть результат и этапы' : 'Уточнить результат и этапы',
                    style: const TextStyle(fontSize: 13.5, fontWeight: FontWeight.w600),
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
            label: 'Какой результат вы хотите получить? · необязательно',
            hint: 'Например: ремонт полностью закончен, квартира готова к проживанию',
            lines: 3,
          ),
          const SizedBox(height: 10),
          VoiceField(
            controller: areas,
            label: 'Какие этапы уже понятны? · необязательно',
            hint: 'Например: ванная, кухня, электрика, стены',
            lines: 3,
          ),
        ],
        const SizedBox(height: 13),
        FilledButton.icon(
          key: const ValueKey('goal-continue'),
          onPressed: title.text.trim().isEmpty ? null : save,
          icon: Icon(widget.existing == null ? Icons.arrow_forward_rounded : Icons.check_rounded, size: 19),
          label: Text(widget.existing == null ? 'Продолжить' : 'Сохранить изменения'),
        ),
        if (widget.existing == null) ...[
          const SizedBox(height: 10),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFFF0F4F2),
              borderRadius: BorderRadius.circular(14),
            ),
            child: const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Что произойдёт дальше', style: TextStyle(fontSize: 13.5, fontWeight: FontWeight.w700)),
                SizedBox(height: 4),
                Text(
                  'Вы выберете первое действие и подходящую поддержку: самостоятельно, с цифровым помощником, вместе с человеком или с отчётом о результате.',
                  style: TextStyle(fontSize: 12.5, height: 1.34),
                ),
                SizedBox(height: 5),
                Text(
                  'Приложение будет постепенно замечать, какие условия чаще помогают именно вам.',
                  style: TextStyle(fontSize: 12.3, height: 1.32, color: green, fontWeight: FontWeight.w600),
                ),
              ],
            ),
          ),
        ],
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

# Split action creation into the approved action screen and a separate support screen.
text = text.replace('  bool showMoreSupport = false;\n', '', 1)
text = text.replace('  bool showSmall = false;\n', '  bool showSmall = false;\n  bool supportStep = false;\n', 1)
text = text.replace(
    "    showMoreSupport =\n        chosen != null && chosen != Support.solo && chosen != Support.together;\n",
    '',
    1,
)

action_state = text.index('class _ActionEditorState extends State<ActionEditor>')
action_build = text.index('  @override\n  Widget build(BuildContext context) {', action_state)
action_next = text.index('class _PremiumEditorHeading', action_build)
ACTION_BUILD = r'''  @override
  Widget build(BuildContext context) {
    final recommended = SupportLogic.recommend(title.text);
    final support = chosen ?? recommended.$1;
    const durationOptions = [10, 15, 30, 45, 60, 90, 120];
    final editing = widget.existing != null;

    if (supportStep) {
      return Scaffold(
        appBar: AppBar(
          leading: BackButton(onPressed: () => setState(() => supportStep = false)),
          title: const Text('Поддержка'),
        ),
        body: ListView(
          key: const ValueKey('action-support-step'),
          padding: const EdgeInsets.fromLTRB(16, 5, 16, 24),
          children: [
            const Text(
              'ПОДДЕРЖКА ПОД КОНКРЕТНОЕ ДЕЙСТВИЕ',
              style: TextStyle(color: green, fontSize: 10.5, fontWeight: FontWeight.w700, letterSpacing: .85),
            ),
            const SizedBox(height: 7),
            const Text(
              'Как вам будет легче начать?',
              style: TextStyle(color: ink, fontSize: 24, height: 1.1, fontWeight: FontWeight.w700, letterSpacing: -.35),
            ),
            const SizedBox(height: 8),
            Text(
              'Для действия «${title.text.trim()}» можно выбрать один способ, а позже попробовать другой.',
              style: const TextStyle(color: Color(0xFF56635F), fontSize: 13.5, height: 1.36),
            ),
            const SizedBox(height: 12),
            if (supportLocked)
              _SupportChoiceCard(
                type: support,
                selected: true,
                onTap: () {},
              )
            else ...[
              for (final type in const [
                Support.solo,
                Support.ai,
                Support.together,
                Support.report,
                Support.curator,
              ])
                _SupportChoiceCard(
                  type: type,
                  selected: support == type,
                  onTap: () => setState(() => chosen = type),
                ),
            ],
            const SizedBox(height: 4),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0xFFF0F4F2),
                borderRadius: BorderRadius.circular(14),
              ),
              child: Text(
                'Предложение приложения: ${recommended.$2} Выбор всегда можно изменить.',
                style: const TextStyle(fontSize: 12.5, height: 1.34),
              ),
            ),
            const SizedBox(height: 12),
            FilledButton.icon(
              key: const ValueKey('save-action-with-support'),
              onPressed:
                  title.text.trim().isEmpty ||
                      !durationReady ||
                      (scheduleAction && !scheduledAt.isAfter(DateTime.now()))
                  ? null
                  : () => saveOrStart(support),
              icon: Icon(
                editing
                    ? Icons.save_outlined
                    : scheduleAction
                    ? Icons.event_available_outlined
                    : useTimer
                    ? Icons.play_arrow_rounded
                    : Icons.check_rounded,
              ),
              label: Text(
                editing
                    ? 'Сохранить изменения'
                    : scheduleAction
                    ? 'Сохранить в план'
                    : useTimer
                    ? 'Начать'
                    : 'Сохранить действие',
              ),
            ),
          ],
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: Text(
          editing
              ? 'Изменить действие'
              : linked
              ? 'Первый шаг'
              : 'Новое дело',
        ),
      ),
      body: ListView(
        key: const ValueKey('action-details-step'),
        padding: const EdgeInsets.fromLTRB(16, 5, 16, 24),
        children: [
          Text(
            linked ? 'ПЕРВЫЙ ШАГ К ЦЕЛИ' : 'ОДНО КОНКРЕТНОЕ ДЕЛО',
            style: const TextStyle(color: green, fontSize: 10.5, fontWeight: FontWeight.w700, letterSpacing: 1),
          ),
          const SizedBox(height: 7),
          Text(
            linked ? 'Что вы можете сделать первым?' : 'Что вы хотите сделать?',
            style: const TextStyle(color: ink, fontSize: 24, height: 1.1, fontWeight: FontWeight.w700, letterSpacing: -.35),
          ),
          const SizedBox(height: 8),
          Text(
            linked
                ? 'Не нужно планировать весь путь. Выберите одно конкретное действие, которое действительно продвинет вас к цели.'
                : 'Запишите одно понятное действие. Оно останется отдельно от главной цели, если вы сами их не свяжете.',
            style: const TextStyle(color: Color(0xFF56635F), fontSize: 13.5, height: 1.38),
          ),
          const SizedBox(height: 14),
          VoiceField(
            controller: title,
            label: linked ? 'Первое действие' : 'Действие',
            hint: linked
                ? 'Например: выбрать материалы, открыть учебник, составить описание проекта'
                : 'Например: позвонить мастеру или оплатить интернет',
            lines: 3,
          ),
          const SizedBox(height: 7),
          TextButton.icon(
            onPressed: () => setState(() => showSmall = !showSmall),
            icon: Icon(showSmall ? Icons.expand_less : Icons.compress_rounded),
            label: Text(showSmall ? 'Скрыть минимальный вариант' : 'Добавить минимальный вариант'),
          ),
          if (showSmall) ...[
            const SizedBox(height: 5),
            VoiceField(
              controller: small,
              label: 'Минимальный вариант · необязательно',
              hint: 'Что можно сделать, даже если сегодня будет мало сил или времени?',
              lines: 3,
            ),
          ],
          const SizedBox(height: 13),
          const Text('Как выполнять', style: TextStyle(fontSize: 16.5, fontWeight: FontWeight.w700)),
          const SizedBox(height: 7),
          Row(
            children: [
              Expanded(
                child: _EditorChoice(
                  icon: Icons.check_circle_outline_rounded,
                  title: 'До результата',
                  text: 'Закончить без ограничения времени',
                  selected: !useTimer,
                  onTap: () => setState(() => useTimer = false),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _EditorChoice(
                  icon: Icons.timer_outlined,
                  title: 'С таймером',
                  text: 'Выделить определённое время',
                  selected: useTimer,
                  onTap: () => setState(() => useTimer = true),
                ),
              ),
            ],
          ),
          if (useTimer) ...[
            const SizedBox(height: 9),
            Wrap(
              spacing: 7,
              runSpacing: 7,
              children: [
                ...durationOptions.map(
                  (value) => ChoiceChip(
                    label: Text(durationLabel(value)),
                    selected: !customTime && minutes == value,
                    onSelected: (_) => setState(() {
                      customTime = false;
                      minutes = value;
                      customMinutes.clear();
                    }),
                  ),
                ),
                ChoiceChip(
                  label: const Text('Своё время'),
                  selected: customTime,
                  onSelected: (_) => setState(() => customTime = true),
                ),
              ],
            ),
            if (customTime) ...[
              const SizedBox(height: 9),
              TextField(
                controller: customMinutes,
                keyboardType: TextInputType.number,
                onChanged: (_) => setState(() {}),
                decoration: const InputDecoration(
                  labelText: 'Своя длительность в минутах',
                  hintText: 'Например: 80',
                  helperText: 'От 1 минуты до 12 часов',
                ),
              ),
            ],
          ],
          const SizedBox(height: 13),
          const Text('Когда начать', style: TextStyle(fontSize: 16.5, fontWeight: FontWeight.w700)),
          const SizedBox(height: 7),
          Row(
            children: [
              Expanded(
                child: _EditorChoice(
                  icon: Icons.play_arrow_rounded,
                  title: 'Сегодня',
                  text: 'Начать после выбора поддержки',
                  selected: !scheduleAction,
                  onTap: () => setState(() => scheduleAction = false),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _EditorChoice(
                  icon: Icons.event_outlined,
                  title: 'Запланировать',
                  text: 'Выбрать день и время',
                  selected: scheduleAction,
                  onTap: () => setState(() => scheduleAction = true),
                ),
              ),
            ],
          ),
          if (scheduleAction) ...[
            const SizedBox(height: 9),
            Card(
              child: Column(
                children: [
                  ListTile(
                    dense: true,
                    leading: const Icon(Icons.calendar_today_outlined),
                    title: const Text('День'),
                    subtitle: Text(shortDate(scheduledAt)),
                    trailing: const Icon(Icons.chevron_right),
                    onTap: chooseDate,
                  ),
                  const Divider(height: 1),
                  ListTile(
                    dense: true,
                    leading: const Icon(Icons.schedule_rounded),
                    title: const Text('Время'),
                    subtitle: Text(clockTime(scheduledAt)),
                    trailing: const Icon(Icons.chevron_right),
                    onTap: chooseTime,
                  ),
                ],
              ),
            ),
          ],
          if (!editing && !widget.goalDefault && widget.app.goal != null) ...[
            const SizedBox(height: 6),
            SwitchListTile.adaptive(
              contentPadding: EdgeInsets.zero,
              title: const Text('Связать с главной целью', style: TextStyle(fontWeight: FontWeight.w600)),
              subtitle: Text(widget.app.goal!.title),
              value: linked,
              onChanged: (value) => setState(() => linked = value),
            ),
          ],
          const SizedBox(height: 13),
          FilledButton.icon(
            key: const ValueKey('choose-support'),
            onPressed:
                title.text.trim().isEmpty ||
                    !durationReady ||
                    (scheduleAction && !scheduledAt.isAfter(DateTime.now()))
                ? null
                : () => setState(() => supportStep = true),
            icon: const Icon(Icons.arrow_forward_rounded, size: 19),
            label: const Text('Выбрать поддержку'),
          ),
          const SizedBox(height: 9),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFFF0F4F2),
              borderRadius: BorderRadius.circular(14),
            ),
            child: const Text(
              'Следующим шагом вы выберете, как удобнее начать: самостоятельно, с цифровым помощником, вместе с человеком или с договорённостью об отчёте.',
              style: TextStyle(fontSize: 12.5, height: 1.34),
            ),
          ),
        ],
      ),
    );
  }
}

class _EditorChoice extends StatelessWidget {
  const _EditorChoice({
    required this.icon,
    required this.title,
    required this.text,
    required this.selected,
    required this.onTap,
  });
  final IconData icon;
  final String title, text;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) => InkWell(
    onTap: onTap,
    borderRadius: BorderRadius.circular(14),
    child: Container(
      constraints: const BoxConstraints(minHeight: 94),
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: selected ? const Color(0xFFE5EFEB) : Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: selected ? green : const Color(0xFFE2DED4), width: selected ? 1.4 : 1),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: selected ? green : const Color(0xFF66736F), size: 20),
          const SizedBox(height: 6),
          Text(title, style: const TextStyle(fontSize: 13.5, fontWeight: FontWeight.w700)),
          const SizedBox(height: 2),
          Text(text, style: const TextStyle(fontSize: 11.5, height: 1.25, color: Color(0xFF65716D))),
        ],
      ),
    ),
  );
}

class _SupportChoiceCard extends StatelessWidget {
  const _SupportChoiceCard({required this.type, required this.selected, required this.onTap});
  final Support type;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.only(bottom: 8),
    child: InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(15),
      child: Container(
        padding: const EdgeInsets.all(11),
        decoration: BoxDecoration(
          color: selected ? supportColor(type) : Colors.white,
          borderRadius: BorderRadius.circular(15),
          border: Border.all(color: selected ? green : const Color(0xFFE2DED4), width: selected ? 1.4 : 1),
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: 38,
              height: 38,
              decoration: BoxDecoration(
                color: selected ? Colors.white54 : supportColor(type),
                borderRadius: BorderRadius.circular(11),
              ),
              child: Icon(_supportChoiceIcon(type), color: ink, size: 20),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(_supportChoiceTitle(type), style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w700)),
                  const SizedBox(height: 2),
                  Text(_supportChoiceText(type), style: const TextStyle(fontSize: 12, height: 1.3, color: Color(0xFF5E6A66))),
                ],
              ),
            ),
            const SizedBox(width: 6),
            Icon(selected ? Icons.check_circle_rounded : Icons.radio_button_unchecked, color: selected ? green : const Color(0xFFB4BCB9), size: 21),
          ],
        ),
      ),
    ),
  );
}

String _supportChoiceTitle(Support type) => switch (type) {
  Support.solo => 'Самостоятельно',
  Support.ai => 'С цифровым помощником',
  Support.together => 'Вместе с человеком',
  Support.report => 'С отчётом о результате',
  Support.curator => 'С куратором',
};

String _supportChoiceText(Support type) => switch (type) {
  Support.solo => 'Начать и выполнить без дополнительной поддержки.',
  Support.ai => 'Разобрать большую или непонятную задачу и выбрать первый шаг.',
  Support.together => 'Начать одновременно или оставаться на аудио- или видеосвязи, пока каждый занимается своим делом.',
  Support.report => 'Договориться, кому вы покажете выполненный результат.',
  Support.curator => 'Попросить человека напомнить, спросить о результате и поддержать после пропуска.',
};

IconData _supportChoiceIcon(Support type) => switch (type) {
  Support.solo => Icons.person_outline_rounded,
  Support.ai => Icons.auto_awesome_outlined,
  Support.together => Icons.video_call_outlined,
  Support.report => Icons.ios_share_outlined,
  Support.curator => Icons.verified_outlined,
};'''
text = text[:action_build] + ACTION_BUILD.rstrip() + '\n\n' + text[action_next:]

# Bring the social-support copy in the rest of the product in line with the approved concept.
text = text.replace(
    'Вы и другой человек начинаете в одно время. Можно делать одно и то же или заниматься разными делами.',
    'Вы начинаете одновременно или остаётесь на аудио- или видеосвязи. Каждый может заниматься своим делом.',
)
text = text.replace(
    'Начнём одновременно? Я начинаю дело «$title»$duration. Каждый может заниматься своим делом.',
    'Начнём одновременно? Я начинаю дело «$title»$duration. Можем остаться на аудио- или видеосвязи, пока каждый занимается своим делом.',
)

main_path.write_text(text, encoding='utf-8')

pubspec = pubspec_path.read_text(encoding='utf-8')
pubspec = pubspec.replace('version: 0.6.2+15', 'version: 0.6.3+16')
pubspec_path.write_text(pubspec, encoding='utf-8')
