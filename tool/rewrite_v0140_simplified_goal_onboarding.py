from pathlib import Path
import re

main_path = Path('lib/main.dart')
pubspec_path = Path('pubspec.yaml')
text = main_path.read_text(encoding='utf-8')
pubspec = pubspec_path.read_text(encoding='utf-8')


def replace_class(source: str, name: str, next_name: str, replacement: str) -> str:
    start = source.index(f'class {name}')
    end = source.index(f'class {next_name}', start)
    return source[:start] + replacement.rstrip() + '\n\n' + source[end:]


def replace_once(old: str, new: str, label: str) -> None:
    global text
    if old not in text:
        raise SystemExit(f'{label} anchor not found')
    text = text.replace(old, new, 1)


replace_once(
    'if (onboarded && onboardingVersion < 7) onboarded = false;',
    'if (onboarded && onboardingVersion < 8) onboarded = false;',
    'onboarding migration 8',
)
replace_once(
    '    onboardingVersion = 7;\n    startChoiceSeen = false;',
    '    onboardingVersion = 8;\n    startChoiceSeen = false;',
    'onboarding completion 8',
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
    pages.nextPage(
      duration: const Duration(milliseconds: 300),
      curve: Curves.easeOutCubic,
    );
  }

  void complete() {
    if (widget.preview) {
      Navigator.pop(context);
    } else {
      widget.app.finish(Age.adult, '');
    }
  }

  @override
  void dispose() {
    pages.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    backgroundColor: const Color(0xFFFBF9F4),
    body: SafeArea(
      child: Column(
        children: [
          _OnboardingHeader(
            preview: widget.preview,
            onSkip: close,
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
          _OnboardingPrimaryButton(
            key: ValueKey(
              page == 0 ? 'onboarding-next' : 'onboarding-complete',
            ),
            label: page == 0
                ? 'Дальше'
                : widget.preview
                ? 'Закрыть'
                : 'Выбрать, с чего начать',
            onPressed: page == 0 ? next : complete,
          ),
        ],
      ),
    ),
  );
}'''

START_CHOICE = r'''class StartChoiceScreen extends StatefulWidget {
  const StartChoiceScreen({required this.app, super.key});
  final AppState app;

  @override
  State<StartChoiceScreen> createState() => _StartChoiceScreenState();
}

class _StartChoiceScreenState extends State<StartChoiceScreen> {
  late final Set<StartArea> selected;
  bool opening = false;

  @override
  void initState() {
    super.initState();
    selected = {...widget.app.startAreas};
    if (selected.isEmpty) {
      if (widget.app.goal != null) selected.add(StartArea.goal);
      if (widget.app.challenges.isNotEmpty) selected.add(StartArea.challenge);
      if (widget.app.actions.any(
        (item) => !item.goal && item.kind != IntentKind.routine,
      )) {
        selected.add(StartArea.tasks);
      }
      if (widget.app.actions.any(
        (item) => item.kind == IntentKind.routine,
      )) {
        selected.add(StartArea.routines);
      }
    }
  }

  void toggle(StartArea area) => setState(() {
    if (!selected.add(area)) selected.remove(area);
  });

  Widget editorFor(StartArea area) => switch (area) {
    StartArea.goal => GoalFocusEntryPage(app: widget.app),
    StartArea.challenge => ChallengeEditor(app: widget.app),
    StartArea.tasks => ActionEditor(app: widget.app, goalDefault: false),
    StartArea.routines => RoutineEditor(app: widget.app),
  };

  Future<bool> continueWithNext(StartArea next) async {
    final answer = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Первый элемент настроен'),
        content: Text(
          'Продолжим и настроим «${startAreaTitle(next)}»?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Перейти к Сегодня'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Продолжить'),
          ),
        ],
      ),
    );
    return answer == true;
  }

  Future<void> continueToSetup() async {
    if (selected.isEmpty || opening) return;
    setState(() => opening = true);
    final ordered = StartArea.values
        .where((area) => selected.contains(area))
        .toList();

    for (var index = 0; index < ordered.length; index += 1) {
      if (!mounted) return;
      await Navigator.push(
        context,
        MaterialPageRoute(builder: (_) => editorFor(ordered[index])),
      );
      if (!mounted) return;
      if (index < ordered.length - 1) {
        final shouldContinue = await continueWithNext(ordered[index + 1]);
        if (!mounted) return;
        if (!shouldContinue) break;
      }
    }

    widget.app.completeStartChoice(selected);
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    key: const ValueKey('start-choice-screen'),
    backgroundColor: const Color(0xFFFBF9F4),
    body: SafeArea(
      child: Column(
        children: [
          Expanded(
            child: ListView(
              key: const ValueKey('start-choice-scroll'),
              padding: const EdgeInsets.fromLTRB(20, 22, 20, 18),
              children: [
                Row(
                  children: [
                    const _OnboardingBrandMark(),
                    const SizedBox(width: 11),
                    const Expanded(
                      child: Text(
                        'Вместе к цели',
                        style: TextStyle(
                          color: ink,
                          fontSize: 17,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ),
                    TextButton(
                      key: const ValueKey('skip-start-choice'),
                      onPressed: opening
                          ? null
                          : () => widget.app.completeStartChoice(const []),
                      child: const Text('Позже'),
                    ),
                  ],
                ),
                const SizedBox(height: 30),
                const Text(
                  'С чего начнём?',
                  key: ValueKey('start-choice-title'),
                  style: TextStyle(
                    color: ink,
                    fontSize: 31,
                    height: 1.08,
                    fontWeight: FontWeight.w800,
                    letterSpacing: -.8,
                  ),
                ),
                const SizedBox(height: 10),
                const Text(
                  'Выберите одно или несколько направлений. После нажатия приложение сразу поможет создать первый элемент.',
                  style: TextStyle(
                    color: Color(0xFF56635F),
                    fontSize: 14.5,
                    height: 1.45,
                  ),
                ),
                const SizedBox(height: 22),
                ...StartArea.values.map(
                  (area) => Padding(
                    padding: const EdgeInsets.only(bottom: 10),
                    child: _StartAreaChoiceCard(
                      area: area,
                      selected: selected.contains(area),
                      onTap: opening ? () {} : () => toggle(area),
                    ),
                  ),
                ),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.fromLTRB(20, 12, 20, 18),
            decoration: const BoxDecoration(
              color: Color(0xFFFBF9F4),
              border: Border(top: BorderSide(color: Color(0xFFE7E4DC))),
            ),
            child: FilledButton.icon(
              key: const ValueKey('continue-start-choice'),
              onPressed: selected.isEmpty || opening ? null : continueToSetup,
              icon: opening
                  ? const SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.arrow_forward_rounded),
              label: Text(
                opening
                    ? 'Открываем…'
                    : selected.length > 1
                    ? 'Настроить выбранное · ${selected.length}'
                    : 'Начать',
              ),
            ),
          ),
        ],
      ),
    ),
  );
}'''

HEADER = r'''class _OnboardingHeader extends StatelessWidget {
  const _OnboardingHeader({
    required this.preview,
    required this.onSkip,
  });

  final bool preview;
  final VoidCallback onSkip;

  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.fromLTRB(22, 12, 14, 7),
    child: Row(
      children: [
        const _OnboardingBrandMark(),
        const SizedBox(width: 11),
        const Expanded(
          child: Text(
            'Вместе к цели',
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: TextStyle(
              color: ink,
              fontSize: 17,
              fontWeight: FontWeight.w700,
              letterSpacing: -.25,
            ),
          ),
        ),
        TextButton(
          style: TextButton.styleFrom(
            foregroundColor: green,
            minimumSize: Size.zero,
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
            tapTargetSize: MaterialTapTargetSize.shrinkWrap,
            textStyle: const TextStyle(
              fontSize: 13.5,
              fontWeight: FontWeight.w600,
            ),
          ),
          onPressed: onSkip,
          child: Text(preview ? 'Закрыть' : 'Пропустить'),
        ),
      ],
    ),
  );
}'''

PRODUCT = r'''class _ProductStoryPage extends StatelessWidget {
  const _ProductStoryPage();

  @override
  Widget build(BuildContext context) => ListView(
    key: const ValueKey('product-story-page'),
    padding: const EdgeInsets.fromLTRB(22, 15, 22, 28),
    children: const [
      Text(
        'КОГДА ВАЖНОЕ НЕ ДВИГАЕТСЯ',
        style: TextStyle(
          color: Color(0xFF4A9F78),
          fontSize: 10.2,
          fontWeight: FontWeight.w800,
          letterSpacing: .88,
        ),
      ),
      SizedBox(height: 11),
      Text(
        'Хотите чего-то добиться, но не получается начать или продолжать?',
        key: ValueKey('approved-product-title'),
        style: TextStyle(
          color: ink,
          fontSize: 26,
          height: 1.12,
          fontWeight: FontWeight.w800,
          letterSpacing: -.55,
        ),
      ),
      SizedBox(height: 14),
      _IntroLead(
        key: ValueKey('product-intro-lead'),
        text:
            '«Вместе к цели» помогает превратить важное намерение в ближайший посильный шаг — даже когда мешают прокрастинация, перегрузка или нехватка сил.',
      ),
      SizedBox(height: 12),
      Text(
        'Не только что делать — но и как именно вам легче начать.',
        style: TextStyle(
          color: green,
          fontSize: 14,
          height: 1.4,
          fontWeight: FontWeight.w800,
        ),
      ),
      SizedBox(height: 21),
      _IntroAreasPanel(),
      SizedBox(height: 17),
      _IntroQuietNote(
        icon: Icons.layers_outlined,
        text:
            'Важная цель, челлендж, обычные дела и регулярные практики остаются самостоятельными направлениями.',
      ),
    ],
  );
}'''

SUPPORT = r'''class _SupportStoryPage extends StatelessWidget {
  const _SupportStoryPage();

  @override
  Widget build(BuildContext context) => ListView(
    key: const ValueKey('support-story-page'),
    padding: const EdgeInsets.fromLTRB(22, 15, 22, 28),
    children: const [
      Text(
        'НЕ ТОЛЬКО ПЛАНИРОВАТЬ',
        style: TextStyle(
          color: Color(0xFF4A9F78),
          fontSize: 10.4,
          fontWeight: FontWeight.w800,
          letterSpacing: .92,
        ),
      ),
      SizedBox(height: 11),
      Text(
        'Помогаем перейти\nк действию',
        key: ValueKey('approved-support-title'),
        style: TextStyle(
          color: ink,
          fontSize: 26,
          height: 1.12,
          fontWeight: FontWeight.w800,
          letterSpacing: -.52,
        ),
      ),
      SizedBox(height: 14),
      _IntroLead(
        key: ValueKey('support-intro-lead'),
        text:
            '«Вместе к цели» помогает увидеть ближайшее действие, уменьшить его до посильного размера и подобрать поддержку — особенно когда вы откладываете, сомневаетесь или не знаете, с чего начать.',
      ),
      SizedBox(height: 20),
      _ActionBridgeCard(
        key: ValueKey('intro-action-step'),
        number: '01',
        icon: Icons.route_outlined,
        title: 'Ближайший шаг',
        text:
            'Не весь путь сразу, а конкретное действие, которое можно сделать сейчас.',
      ),
      SizedBox(height: 9),
      _ActionBridgeCard(
        key: ValueKey('intro-action-feasible'),
        number: '02',
        icon: Icons.compress_rounded,
        title: 'Посильный вариант',
        text:
            'Полный шаг, малый объём или сохранение контакта в сложный день.',
      ),
      SizedBox(height: 9),
      _ActionBridgeCard(
        key: ValueKey('intro-action-support'),
        number: '03',
        icon: Icons.people_alt_outlined,
        title: 'Поддержка',
        text:
            'Самостоятельно или вместе с человеком — только когда это действительно помогает.',
      ),
      SizedBox(height: 16),
      _IntroQuietNote(
        icon: Icons.science_outlined,
        text:
            'Подход опирается на исследования планирования действий, отслеживания прогресса, формирования привычек и социальной поддержки.',
      ),
    ],
  );
}'''

CREATE_GOAL = r'''class CreateGoal extends StatelessWidget {
  const CreateGoal({required this.app, super.key});
  final AppState app;

  @override
  Widget build(BuildContext context) => Container(
    key: const ValueKey('focus-empty-card'),
    padding: const EdgeInsets.all(23),
    decoration: BoxDecoration(
      gradient: const LinearGradient(
        colors: [Color(0xFF102E2A), Color(0xFF356A61)],
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
      ),
      borderRadius: BorderRadius.circular(28),
      boxShadow: const [
        BoxShadow(
          color: Color(0x26132D2A),
          blurRadius: 20,
          offset: Offset(0, 10),
        ),
      ],
    ),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Row(
          children: [
            Icon(Icons.flag_outlined, color: mint, size: 19),
            SizedBox(width: 7),
            Expanded(
              child: Text(
                'ВАЖНАЯ ЦЕЛЬ · ОРИЕНТИР 90 ДНЕЙ',
                maxLines: 2,
                overflow: TextOverflow.visible,
                style: TextStyle(
                  color: mint,
                  fontSize: 11,
                  fontWeight: FontWeight.w900,
                  letterSpacing: .8,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 11),
        const Text(
          'Какой важный результат вы хотите приблизить?',
          style: TextStyle(
            color: Colors.white,
            fontSize: 27,
            height: 1.12,
            fontWeight: FontWeight.w900,
          ),
        ),
        const SizedBox(height: 11),
        const Text(
          '90 дней — только удобный горизонт, чтобы сделать результат понятным. Это не контракт: цель, путь и темп можно уточнять.',
          style: TextStyle(
            color: Color(0xFFD7E2DF),
            fontSize: 15.5,
            height: 1.42,
          ),
        ),
        const SizedBox(height: 18),
        FilledButton.icon(
          key: const ValueKey('focus-start-entry'),
          style: FilledButton.styleFrom(
            backgroundColor: mint,
            foregroundColor: ink,
          ),
          onPressed: () => Navigator.push(
            context,
            MaterialPageRoute(builder: (_) => GoalFocusEntryPage(app: app)),
          ),
          icon: const Icon(Icons.flag_outlined),
          label: const Text('Создать важную цель'),
        ),
      ],
    ),
  );
}'''

ENTRY = r'''class GoalFocusEntryPage extends StatelessWidget {
  const GoalFocusEntryPage({required this.app, super.key});
  final AppState app;

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Важная цель')),
    body: ListView(
      padding: const EdgeInsets.fromLTRB(18, 4, 18, 32),
      children: [
        Text(
          'Как сформулируем важную цель?',
          style: Theme.of(context).textTheme.headlineMedium,
        ),
        const SizedBox(height: 8),
        const Text(
          'Можно пройти короткий путь или открыть более глубокий опросник, когда трудно понять, что действительно стоит менять.',
          style: TextStyle(height: 1.42),
        ),
        const SizedBox(height: 20),
        _FocusRouteCard(
          key: const ValueKey('focus-quick-route'),
          icon: Icons.flag_outlined,
          color: const Color(0xFFDCEEE7),
          title: 'Я знаю, чего хочу',
          text:
              'Название цели, ориентир на 90 дней, личный смысл, ближайший шаг и конкретное время.',
          badge: '5 шагов',
          onTap: () => Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => GoalFocusWizard(app: app, guided: false),
            ),
          ),
        ),
        const SizedBox(height: 12),
        _FocusRouteCard(
          key: const ValueKey('focus-guided-route'),
          icon: Icons.psychology_alt_outlined,
          color: const Color(0xFFF2E8D8),
          title: 'Мне трудно выбрать цель',
          text:
              'Необязательный глубокий разбор ситуации, зоны влияния, избегания и цены бездействия.',
          badge: 'по желанию',
          onTap: () => Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => GoalFocusWizard(app: app, guided: true),
            ),
          ),
        ),
        const SizedBox(height: 17),
        Container(
          padding: const EdgeInsets.all(15),
          decoration: BoxDecoration(
            color: const Color(0xFFF0F5F2),
            borderRadius: BorderRadius.circular(20),
          ),
          child: const Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(Icons.info_outline_rounded, color: green, size: 21),
              SizedBox(width: 10),
              Expanded(
                child: Text(
                  '90 дней относятся только к важной цели. Челленджи, обычные дела и регулярные практики создаются отдельно.',
                  style: TextStyle(height: 1.4),
                ),
              ),
            ],
          ),
        ),
      ],
    ),
  );
}'''

QUICK_PAGE = r'''  Widget _quickPage() => switch (step) {
    0 => _question(
      eyebrow: 'ВАЖНАЯ ЦЕЛЬ',
      titleText: 'Как коротко назовём важную цель?',
      subtitle:
          'Одно понятное направление. Например: выпустить приложение, восстановить здоровье или подготовить переезд.',
      children: [
        _field(
          keyName: 'focus-title-field',
          controller: title,
          label: 'Название цели',
          hint: 'Например: выпустить приложение',
          lines: 2,
        ),
      ],
    ),
    1 => _question(
      eyebrow: 'ОРИЕНТИР НА 90 ДНЕЙ',
      titleText: 'Какой заметный результат вы хотите увидеть?',
      subtitle:
          'Это не обязательство на весь срок, а ориентир, который делает цель конкретнее.',
      children: [
        _field(
          keyName: 'focus-result-field',
          controller: result,
          label: 'Результат примерно через 90 дней',
          hint:
              'Например: рабочая версия опубликована и доступна пользователям',
          lines: 4,
        ),
      ],
    ),
    2 => _question(
      eyebrow: 'ЛИЧНЫЙ СМЫСЛ',
      titleText: 'Почему это важно именно вам?',
      subtitle:
          'Не то, что выглядит правильно, а ваша собственная причина двигаться.',
      children: [
        _field(
          keyName: 'focus-why-field',
          controller: why,
          label: 'Моя причина',
          hint: 'Что ценного изменится для вас?',
          lines: 4,
        ),
      ],
    ),
    3 => _question(
      eyebrow: 'БЛИЖАЙШИЙ ШАГ',
      titleText: 'Какое посильное действие приблизит цель?',
      subtitle:
          'Не весь план. Только одно действие, которое можно действительно выполнить.',
      children: [
        _field(
          keyName: 'focus-first-step-field',
          controller: firstStep,
          label: 'Ближайший шаг',
          hint: 'Например: проверить первый сценарий на одном телефоне',
          lines: 4,
        ),
      ],
    ),
    _ => _question(
      eyebrow: 'КОНКРЕТНЫЙ МОМЕНТ',
      titleText: 'Когда вы сделаете этот шаг?',
      subtitle:
          'Укажите день, примерное время или событие, после которого начнёте.',
      children: [
        _field(
          keyName: 'focus-when-field',
          controller: whenWhere,
          label: 'Когда',
          hint: 'Например: завтра после завтрака',
          lines: 3,
        ),
      ],
    ),
  };

'''

REVIEW = r'''class GoalFocusReviewPage extends StatelessWidget {
  const GoalFocusReviewPage({
    required this.app,
    required this.guided,
    required this.title,
    required this.result,
    required this.why,
    required this.influence,
    required this.firstStep,
    required this.confidence,
    required this.situation,
    required this.outsideControl,
    required this.avoidance,
    required this.protection,
    required this.cost,
    required this.whenWhere,
    super.key,
  });

  final AppState app;
  final bool guided;
  final String title, result, why, influence, firstStep;
  final int confidence;
  final String situation, outsideControl, avoidance, protection, cost, whenWhere;

  void save(BuildContext context) {
    final now = DateTime.now();
    app.setGoal(
      Goal(
        title,
        result,
        0,
        const [],
        why: why,
        influence: influence,
        firstStep: firstStep,
        confidence: confidence,
        guided: guided,
        focusStartedAt: now,
        situation: situation,
        outsideControl: outsideControl,
        avoidance: avoidance,
        protection: protection,
        cost: cost,
        whenWhere: whenWhere,
      ),
    );

    final duplicate = app.actions.any(
      (item) =>
          item.goal &&
          item.state == null &&
          item.title.trim().toLowerCase() == firstStep.trim().toLowerCase(),
    );
    if (!duplicate) {
      app.add(
        ActionItem(
          id: 'goal_${now.microsecondsSinceEpoch}',
          title: firstStep,
          small: '',
          minutes: 0,
          support: Support.solo,
          goal: true,
          kind: IntentKind.goalStep,
          useTimer: false,
        ),
      );
    }
    Navigator.popUntil(context, (route) => route.isFirst);
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Важная цель')),
    body: ListView(
      padding: const EdgeInsets.fromLTRB(18, 4, 18, 32),
      children: [
        Container(
          padding: const EdgeInsets.all(21),
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [Color(0xFF173C36), Color(0xFF356A60)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(27),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Row(
                children: [
                  Icon(Icons.flag_outlined, color: mint, size: 19),
                  SizedBox(width: 7),
                  Expanded(
                    child: Text(
                      'ВАША ВАЖНАЯ ЦЕЛЬ',
                      maxLines: 2,
                      overflow: TextOverflow.visible,
                      style: TextStyle(
                        color: mint,
                        fontSize: 10.5,
                        fontWeight: FontWeight.w900,
                        letterSpacing: .75,
                      ),
                    ),
                  ),
                  SizedBox(width: 8),
                  Text(
                    '90 дней',
                    style: TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Text(
                title,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 25,
                  height: 1.12,
                  fontWeight: FontWeight.w900,
                ),
              ),
              const SizedBox(height: 9),
              Text(
                result,
                style: const TextStyle(
                  color: Color(0xFFD6E1DE),
                  fontSize: 14.5,
                  height: 1.42,
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 15),
        _FocusSummaryBlock(
          icon: Icons.favorite_border_rounded,
          label: 'ПОЧЕМУ ЭТО ВАЖНО',
          text: why,
        ),
        if (influence.isNotEmpty) ...[
          const SizedBox(height: 10),
          _FocusSummaryBlock(
            icon: Icons.control_point_duplicate_outlined,
            label: 'В ВАШЕЙ ЗОНЕ ВЛИЯНИЯ',
            text: influence,
          ),
        ],
        const SizedBox(height: 10),
        _FocusSummaryBlock(
          icon: Icons.play_circle_outline_rounded,
          label: 'БЛИЖАЙШИЙ ШАГ',
          text: firstStep,
          accent: true,
        ),
        if (whenWhere.isNotEmpty) ...[
          const SizedBox(height: 10),
          _FocusSummaryBlock(
            icon: Icons.schedule_rounded,
            label: 'КОГДА',
            text: whenWhere,
          ),
        ],
        const SizedBox(height: 15),
        Container(
          padding: const EdgeInsets.all(15),
          decoration: BoxDecoration(
            color: const Color(0xFFF0F5F2),
            borderRadius: BorderRadius.circular(20),
          ),
          child: const Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(Icons.tune_rounded, color: green, size: 22),
              SizedBox(width: 10),
              Expanded(
                child: Text(
                  '90 дней — только ориентир для результата. Цель, путь, масштаб и следующий шаг можно уточнять.',
                  style: TextStyle(height: 1.42),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 19),
        FilledButton.icon(
          key: const ValueKey('save-important-goal'),
          onPressed: () => save(context),
          icon: const Icon(Icons.arrow_forward_rounded),
          label: const Text('Сохранить цель и перейти к действию'),
        ),
        const SizedBox(height: 8),
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Вернуться и уточнить ответы'),
        ),
      ],
    ),
  );
}'''

FOUNDATION = r'''class _FocusFoundationCard extends StatelessWidget {
  const _FocusFoundationCard({required this.goal});
  final Goal goal;

  @override
  Widget build(BuildContext context) {
    if (goal.why.isEmpty && goal.influence.isEmpty && goal.firstStep.isEmpty) {
      return const SizedBox.shrink();
    }
    return Container(
      key: const ValueKey('focus-foundation-card'),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFFF5F2E9),
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: const Color(0xFFE2DAC7)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.flag_outlined, color: green, size: 19),
              SizedBox(width: 7),
              Expanded(
                child: Text(
                  'О ВАЖНОЙ ЦЕЛИ',
                  style: TextStyle(
                    color: green,
                    fontSize: 10.5,
                    fontWeight: FontWeight.w900,
                    letterSpacing: .85,
                  ),
                ),
              ),
              Text(
                'ориентир 90 дней',
                style: TextStyle(
                  color: green,
                  fontSize: 10.5,
                  fontWeight: FontWeight.w800,
                ),
              ),
            ],
          ),
          if (goal.why.isNotEmpty) ...[
            const SizedBox(height: 10),
            Text(
              'Почему важно: ${goal.why}',
              style: const TextStyle(color: ink, height: 1.38),
            ),
          ],
          if (goal.influence.isNotEmpty) ...[
            const SizedBox(height: 7),
            Text(
              'В зоне влияния: ${goal.influence}',
              style: const TextStyle(
                color: Color(0xFF596762),
                height: 1.38,
              ),
            ),
          ],
          if (goal.firstStep.isNotEmpty) ...[
            const SizedBox(height: 9),
            Text(
              'Ближайший шаг: ${goal.firstStep}',
              style: const TextStyle(
                color: green,
                height: 1.38,
                fontWeight: FontWeight.w800,
              ),
            ),
          ],
        ],
      ),
    );
  }
}'''

text = replace_class(text, 'Onboarding extends StatefulWidget', 'StartChoiceScreen extends StatefulWidget', ONBOARDING)
text = replace_class(text, 'StartChoiceScreen extends StatefulWidget', '_StartAreaChoiceCard extends StatelessWidget', START_CHOICE)
text = replace_class(text, '_OnboardingHeader extends StatelessWidget', '_OnboardingPrimaryButton extends StatelessWidget', HEADER)
text = replace_class(text, '_ProductStoryPage extends StatelessWidget', '_IntroLead extends StatelessWidget', PRODUCT)
text = replace_class(text, '_SupportStoryPage extends StatelessWidget', '_ActionBridgeCard extends StatelessWidget', SUPPORT)
text = replace_class(text, 'CreateGoal extends StatelessWidget', 'GoalHero extends StatelessWidget', CREATE_GOAL)
text = replace_class(text, 'GoalFocusEntryPage extends StatelessWidget', '_FocusRouteCard extends StatelessWidget', ENTRY)

quick_start = text.index('  Widget _quickPage() => switch (step) {')
quick_end = text.index('  Widget _guidedPage() => switch (step) {', quick_start)
text = text[:quick_start] + QUICK_PAGE + text[quick_end:]

replace_once(
    '''    return switch (step) {
      0 => title.text.trim().isNotEmpty && result.text.trim().isNotEmpty,
      1 => why.text.trim().isNotEmpty,
      2 => influence.text.trim().isNotEmpty,
      3 => firstStep.text.trim().isNotEmpty,
      _ => confidence >= 7 || reducedStep.text.trim().isNotEmpty,
    };''',
    '''    return switch (step) {
      0 => title.text.trim().isNotEmpty,
      1 => result.text.trim().isNotEmpty,
      2 => why.text.trim().isNotEmpty,
      3 => firstStep.text.trim().isNotEmpty,
      _ => whenWhere.text.trim().isNotEmpty,
    };''',
    'quick route validation',
)
replace_once(
    '          influence: influence.text.trim(),',
    "          influence: widget.guided ? influence.text.trim() : '',",
    'quick route influence',
)
replace_once(
    '          confidence: confidence,',
    '          confidence: widget.guided ? confidence : 0,',
    'quick route confidence',
)

text = replace_class(text, 'GoalFocusReviewPage extends StatelessWidget', '_FocusSummaryBlock extends StatelessWidget', REVIEW)
text = replace_class(text, '_FocusFoundationCard extends StatelessWidget', 'GoalEditor extends StatefulWidget', FOUNDATION)

text = text.replace("'ГЛАВНЫЙ ФОКУС · 90 ДНЕЙ'", "'ВАЖНАЯ ЦЕЛЬ'")
text = text.replace("'Главный фокус'", "'Важная цель'")
text = text.replace("label: 'Фокус',", "label: 'Цель',")
text = text.replace("tooltip: 'Уточнить фокус'", "tooltip: 'Уточнить цель'")
text = text.replace('к главному фокусу', 'к важной цели')
text = text.replace('главному фокусу', 'важной цели')
text = text.replace('Уточнить главный фокус', 'Уточнить важную цель')
text = text.replace('Уточняйте формулировку, не начиная всё заново', 'Цель и путь можно менять')
text = text.replace(
    'Маршрут, масштаб и следующий шаг можно менять. Здесь сохраняется само направление, которому вы решили дать преимущество.',
    'Ориентир на 90 дней помогает видеть результат, но не запрещает менять формулировку, маршрут, масштаб и следующий шаг.',
)
text = text.replace("label: 'Короткое название фокуса'", "label: 'Короткое название цели'")

if 'Первые 7 дней — проверка фокуса действием.' in text:
    raise SystemExit('obsolete seven-day trial text still present')
if 'ВАШ ПРЕДВАРИТЕЛЬНЫЙ ФОКУС' in text:
    raise SystemExit('obsolete preliminary focus text still present')
if "ValueKey('save-important-goal')" not in text:
    raise SystemExit('simplified goal save action missing')
if "ValueKey('continue-start-choice')" not in text:
    raise SystemExit('start choice action missing')

if 'version: 0.14.0+33' not in pubspec:
    raise SystemExit('Expected v0.14.0+33 version not found')
pubspec = pubspec.replace('version: 0.14.0+33', 'version: 0.14.0+34', 1)

main_path.write_text(text, encoding='utf-8')
pubspec_path.write_text(pubspec, encoding='utf-8')
print('Applied simplified important-goal horizon and executable onboarding')
