from pathlib import Path
import re

main_path = Path('lib/main.dart')
pubspec_path = Path('pubspec.yaml')
text = main_path.read_text(encoding='utf-8')
pubspec = pubspec_path.read_text(encoding='utf-8')

if 'class StartChoiceScreen' in text:
    print('v0.13.1 unified start already applied')
    raise SystemExit(0)


def replace_once(old: str, new: str, label: str) -> None:
    global text
    if old not in text:
        raise SystemExit(f'{label} anchor not found')
    text = text.replace(old, new, 1)


# A first-entry preference is not a permanent app mode: several contours may
# remain active at the same time.
replace_once(
    'enum ChallengeDayResult { full, partial, skipped }',
    '''enum ChallengeDayResult { full, partial, skipped }

enum StartArea { goal, challenge, tasks, routines }

String startAreaTitle(StartArea area) => switch (area) {
  StartArea.goal => 'Важная цель',
  StartArea.challenge => 'Челлендж',
  StartArea.tasks => 'Дела и задачи',
  StartArea.routines => 'Регулярные практики',
};

String startAreaDescription(StartArea area) => switch (area) {
  StartArea.goal =>
    'Двигаться к значимому результату небольшими понятными шагами.',
  StartArea.challenge =>
    'Выполнять конкретное правило в течение выбранного срока.',
  StartArea.tasks =>
    'Разобрать накопившееся и выбрать, что требует внимания.',
  StartArea.routines =>
    'Поддерживать действия, которые важно повторять постоянно.',
};

IconData startAreaIcon(StartArea area) => switch (area) {
  StartArea.goal => Icons.flag_outlined,
  StartArea.challenge => Icons.emoji_events_outlined,
  StartArea.tasks => Icons.checklist_rounded,
  StartArea.routines => Icons.repeat_rounded,
};''',
    'start area enum',
)

# Persist the one-time chooser independently from the accepted introduction.
replace_once(
    '  bool onboarded = false;\n  int onboardingVersion = 0;',
    '''  bool onboarded = false;
  int onboardingVersion = 0;
  bool startChoiceSeen = true;
  final Set<StartArea> startAreas = <StartArea>{};''',
    'start choice fields',
)
replace_once(
    'static const schemaVersion = 7;',
    'static const schemaVersion = 8;',
    'schema version 8',
)

load_anchor = '''      onboardingVersion = j['onboardingVersion'] ?? 0;
      if (onboarded && onboardingVersion < 6) onboarded = false;'''
replace_once(
    load_anchor,
    load_anchor + '''
      startChoiceSeen = j['startChoiceSeen'] ?? false;
      startAreas.addAll(
        (j['startAreas'] ?? const [])
            .map<StartArea>(
              (value) => StartArea.values.firstWhere(
                (area) => area.name == value,
                orElse: () => StartArea.tasks,
              ),
            ),
      );''',
    'start choice load',
)
replace_once(
    "    'onboardingVersion': onboardingVersion,\n",
    "    'onboardingVersion': onboardingVersion,\n    'startChoiceSeen': startChoiceSeen,\n    'startAreas': startAreas.map((area) => area.name).toList(),\n",
    'start choice payload',
)
replace_once(
    '    onboarded = true;\n    onboardingVersion = 6;\n    notifyListeners();',
    '''    onboarded = true;
    onboardingVersion = 6;
    startChoiceSeen = false;
    notifyListeners();''',
    'onboarding opens start choice',
)

start_choice_methods = r'''  void completeStartChoice(Iterable<StartArea> values) {
    startAreas
      ..clear()
      ..addAll(values);
    startChoiceSeen = true;
    notifyListeners();
    save();
  }

  void reopenStartChoice() {
    startChoiceSeen = false;
    notifyListeners();
    save();
  }

'''
set_goal_at = text.index('  void setGoal(Goal g) {')
text = text[:set_goal_at] + start_choice_methods + text[set_goal_at:]

# Route both new and migrated users through the multi-select chooser once.
replace_once(
    'home: app.onboarded ? Shell(app: app) : Onboarding(app: app),',
    '''home: !app.onboarded
          ? Onboarding(app: app)
          : !app.startChoiceSeen
          ? StartChoiceScreen(app: app)
          : Shell(app: app),''',
    'root start choice route',
)

# The accepted two-page introduction now leads to the chooser rather than
# assuming that every person must create a goal first.
old_create_goal = r'''  void createGoal() {
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
  }'''
new_create_goal = r'''  void createGoal() {
    if (widget.preview) {
      Navigator.pop(context);
      return;
    }
    widget.app.finish(Age.adult, '');
  }'''
replace_once(old_create_goal, new_create_goal, 'onboarding completion')
replace_once(
    '''            label: page == 0
                ? 'Дальше'
                : widget.preview
                ? 'Закрыть'
                : widget.app.goal == null
                ? 'Создать первую цель'
                : 'Продолжить',''',
    '''            label: page == 0
                ? 'Дальше'
                : widget.preview
                ? 'Закрыть'
                : 'Продолжить',''',
    'onboarding final label',
)

start_choice_ui = r'''class StartChoiceScreen extends StatefulWidget {
  const StartChoiceScreen({required this.app, super.key});
  final AppState app;

  @override
  State<StartChoiceScreen> createState() => _StartChoiceScreenState();
}

class _StartChoiceScreenState extends State<StartChoiceScreen> {
  late final Set<StartArea> selected;

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

  void continueToApp() => widget.app.completeStartChoice(selected);

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
                      onPressed: () => widget.app.completeStartChoice(const []),
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
                  'Можно выбрать несколько вариантов и вернуться к остальным позже.',
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
                      onTap: () => toggle(area),
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
            child: FilledButton(
              key: const ValueKey('continue-start-choice'),
              onPressed: selected.isEmpty ? null : continueToApp,
              child: Text(
                selected.length > 1
                    ? 'Продолжить · выбрано ${selected.length}'
                    : 'Продолжить',
              ),
            ),
          ),
        ],
      ),
    ),
  );
}

class _StartAreaChoiceCard extends StatelessWidget {
  const _StartAreaChoiceCard({
    required this.area,
    required this.selected,
    required this.onTap,
  });

  final StartArea area;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) => Material(
    color: selected ? const Color(0xFFE5F1EB) : Colors.white,
    clipBehavior: Clip.antiAlias,
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(21),
      side: BorderSide(
        color: selected ? green : const Color(0xFFDFE4E0),
        width: selected ? 1.5 : 1,
      ),
    ),
    child: InkWell(
      key: ValueKey('start-area-${area.name}'),
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.fromLTRB(14, 14, 13, 14),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: 46,
              height: 46,
              decoration: BoxDecoration(
                color: selected
                    ? const Color(0xFFD0E7DC)
                    : const Color(0xFFF1F3EF),
                borderRadius: BorderRadius.circular(15),
              ),
              child: Icon(startAreaIcon(area), color: green, size: 23),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    startAreaTitle(area),
                    style: const TextStyle(
                      color: ink,
                      fontSize: 16,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    startAreaDescription(area),
                    style: const TextStyle(
                      color: Color(0xFF63706B),
                      fontSize: 12.7,
                      height: 1.4,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(width: 8),
            Icon(
              selected
                  ? Icons.check_circle_rounded
                  : Icons.radio_button_unchecked_rounded,
              color: selected ? green : const Color(0xFFA6AEAA),
              size: 23,
            ),
          ],
        ),
      ),
    ),
  );
}

'''
onboarding_header_at = text.index('class _OnboardingHeader')
text = text[:onboarding_header_at] + start_choice_ui + text[onboarding_header_at:]

# Optional relationship: a challenge may support the current important goal,
# but it remains a separate contour with its own rule and distance.
replace_once(
    "    this.consequence = '',\n    List<ChallengeEntry>? entries,",
    "    this.consequence = '',\n    this.goalId = '',\n    List<ChallengeEntry>? entries,",
    'challenge goal constructor',
)
replace_once(
    '  String consequence;\n  List<ChallengeEntry> entries;',
    '  String consequence;\n  String goalId;\n  List<ChallengeEntry> entries;',
    'challenge goal field',
)
replace_once(
    "    'consequence': consequence,\n    'entries': entries.map((entry) => entry.toJson()).toList(),",
    "    'consequence': consequence,\n    'goalId': goalId,\n    'entries': entries.map((entry) => entry.toJson()).toList(),",
    'challenge goal payload',
)
replace_once(
    "      consequence: (json['consequence'] ?? '').toString(),\n      entries:",
    "      consequence: (json['consequence'] ?? '').toString(),\n      goalId: (json['goalId'] ?? '').toString(),\n      entries:",
    'challenge goal restore',
)
replace_once(
    '  late int duration;\n  late ChallengeMode mode;',
    '  late int duration;\n  late ChallengeMode mode;\n  late bool linkedToGoal;',
    'challenge editor goal state',
)
replace_once(
    '    mode = value?.mode ?? ChallengeMode.solo;\n  }',
    '''    mode = value?.mode ?? ChallengeMode.solo;
    linkedToGoal =
        value != null &&
        value.goalId.isNotEmpty &&
        value.goalId == widget.app.goal?.id;
  }''',
    'challenge editor goal init',
)
replace_once(
    "          consequence: consequence.text.trim(),\n        ),",
    "          consequence: consequence.text.trim(),\n          goalId: linkedToGoal ? widget.app.goal?.id ?? '' : '',\n        ),",
    'new challenge goal link',
)
replace_once(
    '''      existing.consequence = consequence.text.trim();
      widget.app.updateChallenge(existing);''',
    '''      existing.consequence = consequence.text.trim();
      existing.goalId = linkedToGoal ? widget.app.goal?.id ?? '' : '';
      widget.app.updateChallenge(existing);''',
    'existing challenge goal link',
)

challenge_format_anchor = '''        const SizedBox(height: 16),
        const Text(
          'Формат','''
challenge_goal_switch = '''        if (widget.app.goal != null) ...[
          const SizedBox(height: 13),
          SwitchListTile.adaptive(
            key: const ValueKey('challenge-link-goal'),
            contentPadding: EdgeInsets.zero,
            value: linkedToGoal,
            onChanged: (value) => setState(() => linkedToGoal = value),
            title: const Text(
              'Связать с главной целью',
              style: TextStyle(fontWeight: FontWeight.w800),
            ),
            subtitle: Text(
              'Этот челлендж помогает двигаться к «${widget.app.goal!.title}».',
            ),
          ),
        ],
        const SizedBox(height: 16),
        const Text(
          'Формат','''
replace_once(
    challenge_format_anchor,
    challenge_goal_switch,
    'challenge goal switch',
)
replace_once(
    "'День ${challenge.dayNumber()} из ${challenge.durationDays} · серия ${challenge.currentStreak}',",
    "'День ${challenge.dayNumber()} из ${challenge.durationDays} · серия ${challenge.currentStreak}${challenge.goalId.isNotEmpty ? ' · к цели' : ''}',",
    'compact challenge goal marker',
)

# A compact 2x2 overview keeps every contour visible above the detailed day
# surface. It is navigation, not another list of everything the person owns.
today_overview_anchor = '''          const SizedBox(height: 15),
          _TodayGoalArea('''
replace_once(
    today_overview_anchor,
    '''          const SizedBox(height: 12),
          _TodayAreaOverview(
            app: widget.app,
            onOpenGoal: widget.onOpenGoal,
          ),
          const SizedBox(height: 20),
          _TodayGoalArea(''',
    'today area overview insertion',
)

area_overview_ui = r'''class _TodayAreaOverview extends StatelessWidget {
  const _TodayAreaOverview({
    required this.app,
    required this.onOpenGoal,
  });

  final AppState app;
  final VoidCallback onOpenGoal;

  void openGoal(BuildContext context) {
    if (app.goal != null) {
      onOpenGoal();
      return;
    }
    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => GoalEditor(app: app)),
    );
  }

  void openChallenges(BuildContext context) => Navigator.push(
    context,
    MaterialPageRoute(builder: (_) => ChallengesScreen(app: app)),
  );

  void openTasks(BuildContext context) => Navigator.push(
    context,
    MaterialPageRoute(builder: (_) => IntentChooserPage(app: app)),
  );

  void openRoutines(BuildContext context) => Navigator.push(
    context,
    MaterialPageRoute(builder: (_) => RoutineEditor(app: app)),
  );

  @override
  Widget build(BuildContext context) {
    final activeChallenges = app.challenges
        .where((challenge) => challenge.isActive)
        .length;
    final active = app.actions.where((item) => item.state == null).toList();
    final tasksToday = active
        .where(
          (item) =>
              !item.goal &&
              item.kind != IntentKind.routine &&
              !isLater(item),
        )
        .length;
    final routinesToday = active
        .where(
          (item) =>
              item.kind == IntentKind.routine && routineDueToday(item),
        )
        .length;

    return Column(
      key: const ValueKey('today-area-overview'),
      children: [
        Row(
          children: [
            Expanded(
              child: _TodayAreaTile(
                key: const ValueKey('home-goal-entry'),
                icon: Icons.flag_outlined,
                title: 'Важная цель',
                status: app.goal?.title ?? 'Добавить',
                onTap: () => openGoal(context),
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: _TodayAreaTile(
                key: const ValueKey('home-challenge-entry'),
                icon: Icons.emoji_events_outlined,
                title: 'Челленджи',
                status: activeChallenges == 0
                    ? 'Начать'
                    : '$activeChallenges активных',
                onTap: () => openChallenges(context),
                warm: true,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Row(
          children: [
            Expanded(
              child: _TodayAreaTile(
                key: const ValueKey('home-tasks-entry'),
                icon: Icons.checklist_rounded,
                title: 'Дела',
                status: tasksToday == 0 ? 'Добавить' : '$tasksToday на сегодня',
                onTap: () => openTasks(context),
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: _TodayAreaTile(
                key: const ValueKey('home-routines-entry'),
                icon: Icons.repeat_rounded,
                title: 'Практики',
                status: routinesToday == 0
                    ? 'Добавить'
                    : '$routinesToday на сегодня',
                onTap: () => openRoutines(context),
              ),
            ),
          ],
        ),
      ],
    );
  }
}

class _TodayAreaTile extends StatelessWidget {
  const _TodayAreaTile({
    required this.icon,
    required this.title,
    required this.status,
    required this.onTap,
    this.warm = false,
    super.key,
  });

  final IconData icon;
  final String title;
  final String status;
  final VoidCallback onTap;
  final bool warm;

  @override
  Widget build(BuildContext context) => Material(
    color: warm ? const Color(0xFFFFF7E3) : Colors.white,
    clipBehavior: Clip.antiAlias,
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(18),
      side: BorderSide(
        color: warm
            ? const Color(0xFFE8D8AE)
            : const Color(0xFFDFE4E0),
      ),
    ),
    child: InkWell(
      onTap: onTap,
      child: SizedBox(
        height: 82,
        child: Padding(
          padding: const EdgeInsets.fromLTRB(12, 11, 10, 10),
          child: Row(
            children: [
              Container(
                width: 38,
                height: 38,
                decoration: BoxDecoration(
                  color: warm
                      ? const Color(0xFFFFEBC1)
                      : const Color(0xFFEAF3EF),
                  borderRadius: BorderRadius.circular(13),
                ),
                child: Icon(
                  icon,
                  color: warm ? const Color(0xFF866623) : green,
                  size: 20,
                ),
              ),
              const SizedBox(width: 9),
              Expanded(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        color: ink,
                        fontSize: 13,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                    const SizedBox(height: 3),
                    Text(
                      status,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: TextStyle(
                        color: warm
                            ? const Color(0xFF806321)
                            : const Color(0xFF64716C),
                        fontSize: 11.3,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    ),
  );
}

'''
goal_area_at = text.index('class _TodayGoalArea')
text = text[:goal_area_at] + area_overview_ui + text[goal_area_at:]

# The empty goal area is now one available contour, not the only assumed entry.
goal_area_start = text.index('class _TodayGoalArea')
goal_area_end = text.index('class _TodayOtherArea', goal_area_start)
goal_area_block = text[goal_area_start:goal_area_end]
goal_area_block = goal_area_block.replace("'С чего начнём?'", "'Важная цель'", 1)
goal_area_block = goal_area_block.replace(
    "'Создайте важную цель или сразу выгрузите обычное дело из головы.'",
    "'Двигайтесь к значимому результату небольшими понятными шагами.'",
    1,
)
goal_area_block = goal_area_block.replace(
    "const Text('Создать главную цель')",
    "const Text('Создать цель')",
    1,
)
text = text[:goal_area_start] + goal_area_block + text[goal_area_end:]

# Make the empty challenge entry explicit and recognisable without requiring
# the person to know that a trophy card is actionable.
challenge_start = text.index('class _TodayChallengesArea')
challenge_end = text.index('class _ChallengeCompactCard', challenge_start)
challenge_block = text[challenge_start:challenge_end]
challenge_block = challenge_block.replace(
    "'Обещания на ограниченный срок.'",
    "'Конкретные обещания с началом и финишем.'",
    1,
)
old_empty_row = r'''              child: const Row(
                children: [
                  Icon(Icons.emoji_events_outlined, color: Color(0xFF8A6B25)),
                  SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      'Дайте себе конкретное обещание на 7, 30 или 90 дней.',
                      style: TextStyle(
                        color: ink,
                        fontSize: 13,
                        height: 1.35,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                  Icon(Icons.chevron_right_rounded, color: Color(0xFF8A6B25)),
                ],
              ),'''
new_empty_row = r'''              child: const Row(
                children: [
                  Icon(Icons.emoji_events_outlined, color: Color(0xFF8A6B25)),
                  SizedBox(width: 11),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Начать челлендж',
                          style: TextStyle(
                            color: ink,
                            fontSize: 14.5,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                        SizedBox(height: 3),
                        Text(
                          'Конкретное правило на 7, 21, 30, 60 или 90 дней.',
                          style: TextStyle(
                            color: Color(0xFF6B6556),
                            fontSize: 12,
                            height: 1.35,
                          ),
                        ),
                      ],
                    ),
                  ),
                  Icon(Icons.chevron_right_rounded, color: Color(0xFF8A6B25)),
                ],
              ),'''
if old_empty_row not in challenge_block:
    raise SystemExit('challenge empty row anchor not found')
challenge_block = challenge_block.replace(old_empty_row, new_empty_row, 1)
text = text[:challenge_start] + challenge_block + text[challenge_end:]

if 'version: 0.13.0+29' not in pubspec:
    raise SystemExit('Expected v0.13.0 version not found')
pubspec = pubspec.replace('version: 0.13.0+29', 'version: 0.13.1+30', 1)

main_path.write_text(text, encoding='utf-8')
pubspec_path.write_text(pubspec, encoding='utf-8')
print('Applied v0.13.1 unified start and home')
