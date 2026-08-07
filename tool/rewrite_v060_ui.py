from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')


def replace_class(source: str, name: str, next_name: str, replacement: str) -> str:
    start = source.index(f'class {name}')
    end = source.index(f'class {next_name}', start)
    return source[:start] + replacement.rstrip() + '\n\n' + source[end:]


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
            padding: const EdgeInsets.fromLTRB(20, 12, 12, 4),
            child: Row(
              children: [
                const Logo(size: 34),
                const SizedBox(width: 10),
                const Text(
                  'Вместе к цели',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 18,
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
              children: const [
                IntroPage(
                  icon: Icons.route_rounded,
                  kicker: 'ОДНА ЦЕЛЬ — БЛИЖАЙШИЙ ШАГ',
                  title: 'Видеть не весь путь, а то, что важно сейчас',
                  text:
                      'Создайте направление, добавляйте действия постепенно и отмечайте даже частичное движение.',
                  points: [
                    'Цель и связанные действия остаются рядом',
                    'Следующий шаг можно изменить или перенести',
                  ],
                ),
                IntroPage(
                  icon: Icons.tune_rounded,
                  kicker: 'ПОДДЕРЖКА ПОД КОНКРЕТНОЕ ДЕЛО',
                  title: 'Выбирать условия, с которыми легче продолжать',
                  text:
                      'Таймер, напоминание, минимальный вариант, совместный старт или куратор — только когда это действительно помогает.',
                  points: [
                    'Практики переживают паузы и пропуски',
                    'Приложение постепенно замечает рабочие способы',
                  ],
                ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 8, 20, 18),
            child: Column(
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: List.generate(
                    2,
                    (index) => AnimatedContainer(
                      duration: const Duration(milliseconds: 200),
                      margin: const EdgeInsets.all(4),
                      width: index == page ? 24 : 7,
                      height: 7,
                      decoration: BoxDecoration(
                        color: index == page ? mint : Colors.white24,
                        borderRadius: BorderRadius.circular(9),
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                FilledButton(
                  style: FilledButton.styleFrom(
                    backgroundColor: mint,
                    foregroundColor: ink,
                  ),
                  onPressed: () {
                    if (page < 1) {
                      pages.nextPage(
                        duration: const Duration(milliseconds: 300),
                        curve: Curves.easeOutCubic,
                      );
                    } else {
                      close();
                    }
                  },
                  child: Text(
                    page == 1
                        ? widget.preview
                              ? 'Вернуться в приложение'
                              : 'Перейти к цели'
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

INTRO = r'''class IntroPage extends StatelessWidget {
  const IntroPage({
    required this.icon,
    required this.kicker,
    required this.title,
    required this.text,
    required this.points,
    super.key,
  });
  final IconData icon;
  final String kicker, title, text;
  final List<String> points;

  @override
  Widget build(BuildContext context) => ListView(
    padding: const EdgeInsets.fromLTRB(20, 10, 20, 16),
    children: [
      Container(
        padding: const EdgeInsets.all(18),
        decoration: BoxDecoration(
          color: const Color(0xFF1C4540),
          borderRadius: BorderRadius.circular(25),
          border: Border.all(color: Colors.white10),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: mint,
                borderRadius: BorderRadius.circular(15),
              ),
              child: Icon(icon, color: ink, size: 26),
            ),
            const SizedBox(height: 18),
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: Colors.white10,
                borderRadius: BorderRadius.circular(18),
              ),
              child: const Row(
                children: [
                  Icon(Icons.flag_rounded, color: mint, size: 21),
                  SizedBox(width: 10),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Главная цель',
                          style: TextStyle(color: Colors.white60, fontSize: 11),
                        ),
                        Text(
                          'Доделать важный проект',
                          style: TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.w900,
                          ),
                        ),
                      ],
                    ),
                  ),
                  Icon(Icons.arrow_forward_rounded, color: mint),
                ],
              ),
            ),
          ],
        ),
      ),
      const SizedBox(height: 18),
      Text(
        kicker,
        style: const TextStyle(
          color: mint,
          fontSize: 11,
          fontWeight: FontWeight.w900,
          letterSpacing: 1.1,
        ),
      ),
      const SizedBox(height: 9),
      Text(
        title,
        style: const TextStyle(
          color: Colors.white,
          fontSize: 25,
          height: 1.12,
          fontWeight: FontWeight.w900,
          letterSpacing: -0.4,
        ),
      ),
      const SizedBox(height: 11),
      Text(
        text,
        style: const TextStyle(
          color: Color(0xFFD5E0DD),
          fontSize: 15.5,
          height: 1.42,
        ),
      ),
      const SizedBox(height: 15),
      ...points.map(
        (point) => Padding(
          padding: const EdgeInsets.only(bottom: 9),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Icon(Icons.check_circle_rounded, color: mint, size: 18),
              const SizedBox(width: 9),
              Expanded(
                child: Text(
                  point,
                  style: const TextStyle(color: Colors.white, fontSize: 14.5),
                ),
              ),
            ],
          ),
        ),
      ),
    ],
  );
}'''

SHELL = r'''class Shell extends StatefulWidget {
  const Shell({required this.app, super.key});
  final AppState app;

  @override
  State<Shell> createState() => _ShellState();
}

class _ShellState extends State<Shell> {
  int index = 0;

  void openGoal() => setState(() => index = 1);

  @override
  Widget build(BuildContext context) => Scaffold(
    body: IndexedStack(
      index: index,
      children: [
        Today(app: widget.app, onOpenGoal: openGoal),
        GoalScreen(app: widget.app),
        SupportScreen(app: widget.app),
        Progress(app: widget.app),
      ],
    ),
    bottomNavigationBar: NavigationBar(
      selectedIndex: index,
      onDestinationSelected: (value) => setState(() => index = value),
      destinations: const [
        NavigationDestination(
          icon: Icon(Icons.today_outlined),
          selectedIcon: Icon(Icons.today),
          label: 'Сегодня',
        ),
        NavigationDestination(
          icon: Icon(Icons.flag_outlined),
          selectedIcon: Icon(Icons.flag),
          label: 'Цель',
        ),
        NavigationDestination(
          icon: Icon(Icons.people_outline_rounded),
          selectedIcon: Icon(Icons.people_alt_rounded),
          label: 'Вместе',
        ),
        NavigationDestination(
          icon: Icon(Icons.history_rounded),
          selectedIcon: Icon(Icons.history_toggle_off_rounded),
          label: 'История',
        ),
      ],
    ),
  );
}'''

TODAY = r'''class Today extends StatelessWidget {
  const Today({required this.app, required this.onOpenGoal, super.key});
  final AppState app;
  final VoidCallback onOpenGoal;

  @override
  Widget build(BuildContext context) {
    final active = app.actions.where((item) => item.state == null).toList();
    final nonRoutines = active
        .where((item) => item.kind != IntentKind.routine)
        .toList();
    final due = nonRoutines.where((item) => !isLater(item)).toList();
    final later = nonRoutines.where(isLater).toList()
      ..sort((a, b) => a.scheduledAt!.compareTo(b.scheduledAt!));
    final goalActions = due.where((item) => item.goal).toList();
    final routines = active
        .where((item) => item.kind == IntentKind.routine)
        .toList();
    final reminders = due
        .where((item) => !item.goal && item.kind == IntentKind.reminder)
        .toList();
    final other = due
        .where((item) => !item.goal && item.kind == IntentKind.focus)
        .toList();

    return Scaffold(
      appBar: AppBar(
        title: const Row(
          children: [
            Logo(size: 28),
            SizedBox(width: 9),
            Text('Вместе к цели'),
          ],
        ),
        actions: [
          IconButton(
            tooltip: 'Как работает приложение',
            icon: const Icon(Icons.info_outline_rounded),
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => Onboarding(app: app, preview: true),
              ),
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        backgroundColor: ink,
        foregroundColor: Colors.white,
        elevation: 2,
        onPressed: () => Navigator.push(
          context,
          MaterialPageRoute(builder: (_) => IntentChooserPage(app: app)),
        ),
        icon: const Icon(Icons.add_rounded),
        label: const Text('Добавить'),
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(16, 2, 16, 110),
        children: [
          _PremiumTodayHeader(count: due.length, goalCount: goalActions.length),
          const SizedBox(height: 12),
          if (app.goal == null)
            CreateGoal(app: app)
          else ...[
            GoalHero(app: app, onTap: onOpenGoal),
            const SizedBox(height: 13),
            _GoalActionGroup(
              app: app,
              actions: goalActions,
              onOpenGoal: onOpenGoal,
            ),
          ],
          if (routines.isNotEmpty) ...[
            const SizedBox(height: 17),
            _section('Регулярные практики', routines.length),
            const SizedBox(height: 8),
            ...routines.map(
              (item) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: RoutineCard(app: app, item: item),
              ),
            ),
          ],
          if (reminders.isNotEmpty) ...[
            const SizedBox(height: 17),
            _section('Не забыть', reminders.length),
            const SizedBox(height: 8),
            ...reminders.map(
              (item) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: ActionCard(app: app, item: item),
              ),
            ),
          ],
          if (other.isNotEmpty) ...[
            const SizedBox(height: 17),
            _section('Другие дела', other.length),
            const SizedBox(height: 8),
            ...other.map(
              (item) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: ActionCard(app: app, item: item),
              ),
            ),
          ],
          if (due.isEmpty && routines.isEmpty && app.goal == null) ...[
            const SizedBox(height: 18),
            const _PremiumEmptyState(),
          ],
          if (later.isNotEmpty) ...[
            const SizedBox(height: 19),
            _section('Запланировано позже', later.length),
            const SizedBox(height: 8),
            ...later.take(6).map(
              (item) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: ActionCard(app: app, item: item),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _section(String text, int count) => Row(
    children: [
      Expanded(
        child: Text(
          text,
          style: const TextStyle(
            fontSize: 17,
            fontWeight: FontWeight.w900,
            color: ink,
          ),
        ),
      ),
      Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
        decoration: BoxDecoration(
          color: const Color(0xFFE4EEE9),
          borderRadius: BorderRadius.circular(20),
        ),
        child: Text(
          '$count',
          style: const TextStyle(
            color: green,
            fontSize: 12,
            fontWeight: FontWeight.w900,
          ),
        ),
      ),
    ],
  );
}

class _GoalActionGroup extends StatelessWidget {
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
    padding: const EdgeInsets.fromLTRB(12, 12, 12, 4),
    decoration: BoxDecoration(
      color: const Color(0xFFF0F6F3),
      borderRadius: BorderRadius.circular(21),
      border: Border.all(color: const Color(0x1939776B)),
    ),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        InkWell(
          onTap: onOpenGoal,
          borderRadius: BorderRadius.circular(14),
          child: Padding(
            padding: const EdgeInsets.fromLTRB(5, 1, 4, 10),
            child: Row(
              children: [
                const Icon(Icons.route_rounded, color: green, size: 20),
                const SizedBox(width: 8),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'ДВИЖЕНИЕ К ЦЕЛИ',
                        style: TextStyle(
                          color: green,
                          fontSize: 10,
                          fontWeight: FontWeight.w900,
                          letterSpacing: 1,
                        ),
                      ),
                      Text(
                        '${app.goal!.title} · ${actions.length} в работе',
                        style: const TextStyle(fontWeight: FontWeight.w900),
                      ),
                    ],
                  ),
                ),
                const Icon(Icons.arrow_forward_rounded, color: green),
              ],
            ),
          ),
        ),
        if (actions.isEmpty)
          Padding(
            padding: const EdgeInsets.only(bottom: 9),
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
              padding: const EdgeInsets.only(bottom: 8),
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

HEADER = r'''class _PremiumTodayHeader extends StatelessWidget {
  const _PremiumTodayHeader({required this.count, required this.goalCount});
  final int count, goalCount;

  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.symmetric(horizontal: 15, vertical: 13),
    decoration: BoxDecoration(
      color: Colors.white,
      borderRadius: BorderRadius.circular(20),
      border: Border.all(color: const Color(0x1739776B)),
    ),
    child: Row(
      children: [
        Container(
          width: 38,
          height: 38,
          decoration: BoxDecoration(
            color: const Color(0xFFEAF3EF),
            borderRadius: BorderRadius.circular(13),
          ),
          child: const Icon(Icons.wb_sunny_outlined, color: green, size: 21),
        ),
        const SizedBox(width: 11),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                count == 0
                    ? 'Сегодня · день свободен'
                    : 'Сегодня · $count ${taskWord(count)}',
                style: const TextStyle(
                  color: ink,
                  fontSize: 19,
                  fontWeight: FontWeight.w900,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                goalCount == 0
                    ? longToday()
                    : '$goalCount ${taskWord(goalCount)} ведёт к главной цели',
                style: const TextStyle(color: Color(0xFF60706B), fontSize: 12.5),
              ),
            ],
          ),
        ),
      ],
    ),
  );
}'''

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
        borderRadius: BorderRadius.circular(23),
        child: Ink(
          padding: const EdgeInsets.all(17),
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [Color(0xFF102E2A), Color(0xFF356A61)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(23),
            boxShadow: const [
              BoxShadow(
                color: Color(0x1D132D2A),
                blurRadius: 18,
                offset: Offset(0, 9),
              ),
            ],
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
                      fontSize: 10,
                      fontWeight: FontWeight.w900,
                      letterSpacing: 1.1,
                    ),
                  ),
                  const Spacer(),
                  if (onTap != null)
                    const Icon(
                      Icons.arrow_forward_rounded,
                      color: Colors.white70,
                      size: 21,
                    ),
                ],
              ),
              const SizedBox(height: 9),
              Text(
                goal.title,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 22,
                  height: 1.12,
                  fontWeight: FontWeight.w900,
                ),
              ),
              if (next != null) ...[
                const SizedBox(height: 7),
                Text(
                  'Ближайший шаг: ${next.title}',
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    color: Color(0xFFD4E0DD),
                    fontSize: 13.5,
                  ),
                ),
              ],
              const SizedBox(height: 13),
              ClipRRect(
                borderRadius: BorderRadius.circular(9),
                child: LinearProgressIndicator(
                  value: progress,
                  minHeight: 5,
                  backgroundColor: Colors.white12,
                  valueColor: const AlwaysStoppedAnimation(mint),
                ),
              ),
              const SizedBox(height: 10),
              Row(
                children: [
                  _metric('${app.goalDone}', 'завершено'),
                  const SizedBox(width: 7),
                  _metric('${app.goalActive}', 'в работе'),
                  const SizedBox(width: 7),
                  _metric('${goal.areas.length}', 'этапов'),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _metric(String value, String label) => Expanded(
    child: Container(
      padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 4),
      decoration: BoxDecoration(
        color: Colors.white10,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            value,
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.w900,
            ),
          ),
          const SizedBox(width: 4),
          Flexible(
            child: Text(
              label,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(color: Colors.white60, fontSize: 10.5),
            ),
          ),
        ],
      ),
    ),
  );
}'''

GOAL_SCREEN = r'''class GoalScreen extends StatelessWidget {
  const GoalScreen({required this.app, super.key});
  final AppState app;

  @override
  Widget build(BuildContext context) {
    final active = app.actions
        .where((item) => item.goal && item.state == null)
        .toList();
    final recent = app.history.where((item) => item.goal).take(5).toList();

    return Scaffold(
      appBar: AppBar(title: const Text('Моя цель')),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(16, 2, 16, 88),
        children: [
          if (app.goal == null)
            CreateGoal(app: app)
          else ...[
            Text(
              'Путь к результату',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
            const SizedBox(height: 4),
            const Text(
              'Добавляйте действия постепенно — весь путь заранее не нужен.',
            ),
            const SizedBox(height: 13),
            GoalHero(app: app),
            if (app.goal!.result.isNotEmpty) ...[
              const SizedBox(height: 13),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(15),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Желаемый результат',
                        style: TextStyle(
                          color: green,
                          fontSize: 12,
                          fontWeight: FontWeight.w900,
                        ),
                      ),
                      const SizedBox(height: 5),
                      Text(app.goal!.result),
                    ],
                  ),
                ),
              ),
            ],
            const SizedBox(height: 17),
            Row(
              children: [
                const Expanded(
                  child: Text(
                    'Следующие действия',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900),
                  ),
                ),
                Text(
                  '${active.length} в работе',
                  style: const TextStyle(
                    color: green,
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            if (active.isEmpty)
              EmptyAction(
                onTap: () => Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => ActionEditor(app: app, goalDefault: true),
                  ),
                ),
              )
            else
              ...active.map(
                (item) => Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: ActionCard(app: app, item: item),
                ),
              ),
            if (app.goal!.areas.isNotEmpty) ...[
              const SizedBox(height: 14),
              const Text(
                'Этапы цели',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900),
              ),
              const SizedBox(height: 8),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(15),
                  child: Wrap(
                    spacing: 7,
                    runSpacing: 7,
                    children: app.goal!.areas
                        .map(
                          (area) => Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 11,
                              vertical: 8,
                            ),
                            decoration: BoxDecoration(
                              color: const Color(0xFFEAF3EF),
                              borderRadius: BorderRadius.circular(14),
                            ),
                            child: Text(
                              area,
                              style: const TextStyle(fontWeight: FontWeight.w800),
                            ),
                          ),
                        )
                        .toList(),
                  ),
                ),
              ),
            ],
            if (recent.isNotEmpty) ...[
              const SizedBox(height: 14),
              const Text(
                'Недавнее движение',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900),
              ),
              const SizedBox(height: 8),
              Card(
                child: Column(
                  children: recent
                      .map(
                        (entry) => ListTile(
                          dense: true,
                          leading: Icon(resultIcon(entry.state), color: green),
                          title: Text(entry.title),
                          subtitle: Text(
                            '${resultName(entry.state)} · ${shortDate(entry.date)}',
                          ),
                        ),
                      )
                      .toList(),
                ),
              ),
            ],
            const SizedBox(height: 16),
            FilledButton.icon(
              onPressed: () => Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => ActionEditor(app: app, goalDefault: true),
                ),
              ),
              icon: const Icon(Icons.add_task),
              label: const Text('Добавить следующее действие'),
            ),
            const SizedBox(height: 8),
            OutlinedButton.icon(
              onPressed: () => Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => GoalEditor(app: app, existing: app.goal),
                ),
              ),
              icon: const Icon(Icons.edit_outlined),
              label: const Text('Изменить цель'),
            ),
          ],
        ],
      ),
    );
  }
}'''

ROUTINE_BLOCK = r'''class RoutineEditor extends StatefulWidget {
  const RoutineEditor({required this.app, this.existing, super.key});
  final AppState app;
  final ActionItem? existing;

  @override
  State<RoutineEditor> createState() => _RoutineEditorState();
}

class _RoutineEditorState extends State<RoutineEditor> {
  late final TextEditingController title;
  late final TextEditingController minimum;
  int minutes = 15;
  int minimumMinutes = 3;
  bool useTimer = true;
  bool remindersEnabled = true;
  RoutineSchedule schedule = RoutineSchedule.daily;
  Set<int> weekdays = {1, 3, 5};
  int weeklyTarget = 3;
  late DateTime scheduledAt;

  @override
  void initState() {
    super.initState();
    final existing = widget.existing;
    title = TextEditingController(text: existing?.title ?? '');
    minimum = TextEditingController(text: existing?.small ?? '');
    minutes = existing?.minutes ?? 15;
    minimumMinutes = existing?.minimumMinutes ?? 3;
    useTimer = existing?.useTimer ?? true;
    remindersEnabled = existing?.remindersEnabled ?? true;
    schedule = existing?.routineSchedule ?? RoutineSchedule.daily;
    weekdays = (existing?.weekdays ?? const [1, 3, 5]).toSet();
    weeklyTarget = existing?.weeklyTarget ?? 3;
    final next = DateTime.now().add(const Duration(hours: 1));
    scheduledAt = existing?.scheduledAt ??
        DateTime(next.year, next.month, next.day, next.hour, 0);
    title.addListener(() => setState(() {}));
  }

  @override
  void dispose() {
    title.dispose();
    minimum.dispose();
    super.dispose();
  }

  Future<void> chooseTime() async {
    final value = await showTimePicker(
      context: context,
      initialTime: TimeOfDay.fromDateTime(scheduledAt),
    );
    if (value == null) return;
    setState(() {
      scheduledAt = DateTime(
        scheduledAt.year,
        scheduledAt.month,
        scheduledAt.day,
        value.hour,
        value.minute,
      );
    });
  }

  Future<void> save() async {
    final existing = widget.existing;
    final item = existing ??
        ActionItem(
          id: DateTime.now().microsecondsSinceEpoch.toString(),
          title: title.text.trim(),
          small: minimum.text.trim(),
          minutes: useTimer ? minutes : 0,
          support: Support.solo,
          goal: false,
          kind: IntentKind.routine,
          scheduledAt: scheduledAt,
          repeatDaily: schedule == RoutineSchedule.daily,
          useTimer: useTimer,
        );

    item.title = title.text.trim();
    item.small = minimum.text.trim();
    item.minutes = useTimer ? minutes : 0;
    item.minimumMinutes = minimum.text.trim().isEmpty ? 0 : minimumMinutes;
    item.kind = IntentKind.routine;
    item.goal = false;
    item.routineSchedule = schedule;
    item.weekdays = weekdays.toList()..sort();
    item.weeklyTarget = weeklyTarget;
    item.repeatDaily = schedule == RoutineSchedule.daily;
    item.useTimer = useTimer;
    item.remindersEnabled = remindersEnabled;
    item.routinePaused = false;
    item.pausedUntil = null;
    item.scheduledAt = scheduledAt;
    item.scheduledAt = nextRoutineDate(
      item,
      DateTime.now().subtract(const Duration(seconds: 1)),
    );

    if (existing == null) {
      widget.app.add(item);
    } else {
      widget.app.updateAction(item);
    }
    await NotificationService.instance.cancel(item.id);
    if (remindersEnabled) {
      await NotificationService.instance.scheduleRoutine(item);
    }
    if (!mounted) return;
    Navigator.popUntil(context, (route) => route.isFirst);
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(
      title: Text(widget.existing == null ? 'Регулярная практика' : 'Изменить практику'),
    ),
    body: ListView(
      padding: const EdgeInsets.fromLTRB(16, 2, 16, 32),
      children: [
        Text(
          'Что хотите повторять?',
          style: Theme.of(context).textTheme.headlineMedium,
        ),
        const SizedBox(height: 5),
        const Text('Задайте ритм, который можно сохранить в обычной жизни.'),
        const SizedBox(height: 15),
        VoiceField(
          controller: title,
          label: 'Практика',
          hint: 'Например: заниматься английским',
          lines: 2,
        ),
        const SizedBox(height: 17),
        const Text(
          'Расписание',
          style: TextStyle(fontSize: 17, fontWeight: FontWeight.w900),
        ),
        const SizedBox(height: 8),
        Wrap(
          spacing: 7,
          runSpacing: 7,
          children: [
            _scheduleChip(RoutineSchedule.daily, 'Каждый день'),
            _scheduleChip(RoutineSchedule.weekdays, 'Будни'),
            _scheduleChip(RoutineSchedule.weekends, 'Выходные'),
            _scheduleChip(RoutineSchedule.selectedDays, 'Выбрать дни'),
            _scheduleChip(RoutineSchedule.timesPerWeek, 'Раз в неделю'),
          ],
        ),
        if (schedule == RoutineSchedule.selectedDays) ...[
          const SizedBox(height: 11),
          Wrap(
            spacing: 6,
            children: List.generate(7, (index) {
              final day = index + 1;
              return FilterChip(
                label: Text(shortWeekday(day).toUpperCase()),
                selected: weekdays.contains(day),
                onSelected: (selected) => setState(() {
                  if (selected) {
                    weekdays.add(day);
                  } else if (weekdays.length > 1) {
                    weekdays.remove(day);
                  }
                }),
              );
            }),
          ),
        ],
        if (schedule == RoutineSchedule.timesPerWeek) ...[
          const SizedBox(height: 11),
          const Text('Сколько выполнений достаточно за неделю?'),
          const SizedBox(height: 7),
          Wrap(
            spacing: 7,
            children: [1, 2, 3, 4, 5, 6, 7]
                .map(
                  (value) => ChoiceChip(
                    label: Text('$value'),
                    selected: weeklyTarget == value,
                    onSelected: (_) => setState(() => weeklyTarget = value),
                  ),
                )
                .toList(),
          ),
        ],
        const SizedBox(height: 11),
        Card(
          child: ListTile(
            dense: true,
            leading: const Icon(Icons.schedule_rounded),
            title: const Text('Предпочтительное время'),
            subtitle: Text(clockTime(scheduledAt)),
            trailing: const Icon(Icons.chevron_right),
            onTap: chooseTime,
          ),
        ),
        SwitchListTile.adaptive(
          contentPadding: EdgeInsets.zero,
          title: const Text(
            'Напоминать',
            style: TextStyle(fontWeight: FontWeight.w900),
          ),
          subtitle: const Text('Расписание сохранится и без уведомлений.'),
          value: remindersEnabled,
          onChanged: (value) => setState(() => remindersEnabled = value),
        ),
        SwitchListTile.adaptive(
          contentPadding: EdgeInsets.zero,
          title: const Text(
            'Использовать таймер',
            style: TextStyle(fontWeight: FontWeight.w900),
          ),
          subtitle: const Text('Можно отмечать выполнение без ограничения времени.'),
          value: useTimer,
          onChanged: (value) => setState(() => useTimer = value),
        ),
        if (useTimer) ...[
          const SizedBox(height: 4),
          const Text(
            'Обычный вариант',
            style: TextStyle(fontWeight: FontWeight.w900),
          ),
          const SizedBox(height: 7),
          Wrap(
            spacing: 7,
            runSpacing: 7,
            children: [5, 10, 15, 20, 30, 45, 60]
                .map(
                  (value) => ChoiceChip(
                    label: Text('$value мин'),
                    selected: minutes == value,
                    onSelected: (_) => setState(() => minutes = value),
                  ),
                )
                .toList(),
          ),
        ],
        const SizedBox(height: 17),
        const Text(
          'Минимальный вариант',
          style: TextStyle(fontSize: 17, fontWeight: FontWeight.w900),
        ),
        const SizedBox(height: 5),
        const Text(
          'Не замена полноценной практике, а способ не потерять с ней связь в трудный день.',
          style: TextStyle(color: Colors.black54),
        ),
        const SizedBox(height: 10),
        VoiceField(
          controller: minimum,
          label: 'Что считается минимумом? Необязательно',
          hint: 'Например: повторить 10 слов или позаниматься 3 минуты',
          lines: 3,
        ),
        if (minimum.text.trim().isNotEmpty) ...[
          const SizedBox(height: 9),
          Wrap(
            spacing: 7,
            children: [1, 3, 5, 10, 15]
                .map(
                  (value) => ChoiceChip(
                    label: Text('$value мин'),
                    selected: minimumMinutes == value,
                    onSelected: (_) => setState(() => minimumMinutes = value),
                  ),
                )
                .toList(),
          ),
        ],
        const SizedBox(height: 21),
        FilledButton.icon(
          onPressed: title.text.trim().isEmpty ? null : save,
          icon: const Icon(Icons.repeat_rounded),
          label: Text(
            widget.existing == null ? 'Сохранить практику' : 'Сохранить изменения',
          ),
        ),
      ],
    ),
  );

  Widget _scheduleChip(RoutineSchedule value, String label) => ChoiceChip(
    label: Text(label),
    selected: schedule == value,
    onSelected: (_) => setState(() => schedule = value),
  );
}

class RoutineCard extends StatelessWidget {
  const RoutineCard({required this.app, required this.item, super.key});
  final AppState app;
  final ActionItem item;

  Future<void> record(BuildContext context) async {
    final result = await showModalBottomSheet<RoutineResult>(
      context: context,
      showDragHandle: true,
      builder: (_) => RoutineResultSheet(item: item),
    );
    if (result == null || !context.mounted) return;
    app.completeRoutine(item, result);
    if (result == RoutineResult.skipped && context.mounted) {
      await showModalBottomSheet<void>(
        context: context,
        showDragHandle: true,
        builder: (_) => RoutineRecoverySheet(app: app, item: item),
      );
    }
  }

  Future<void> menu(BuildContext context, String value) async {
    if (value == 'edit') {
      await Navigator.push(
        context,
        MaterialPageRoute(builder: (_) => RoutineEditor(app: app, existing: item)),
      );
    } else if (value == 'pause') {
      await showRoutinePause(context, app, item);
    } else if (value == 'resume') {
      await app.resumeRoutine(item);
    } else if (value == 'delete') {
      final confirmed = await showDialog<bool>(
        context: context,
        builder: (dialogContext) => AlertDialog(
          title: const Text('Удалить практику?'),
          content: Text('История «${item.title}» останется, практика будет удалена.'),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(dialogContext, false),
              child: const Text('Отмена'),
            ),
            FilledButton(
              onPressed: () => Navigator.pop(dialogContext, true),
              child: const Text('Удалить'),
            ),
          ],
        ),
      );
      if (confirmed == true) app.deleteAction(item);
    }
  }

  @override
  Widget build(BuildContext context) {
    final full = app.routineFullThisWeek(item);
    final minimum = app.routineMinimumThisWeek(item);
    final completed = full + minimum;
    final goal = routineWeeklyGoal(item);
    final progress = goal == 0 ? 0.0 : (completed / goal).clamp(0.0, 1.0);
    final paused = item.routinePaused;

    return Card(
      color: paused ? const Color(0xFFF1F0EC) : Colors.white,
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  width: 40,
                  height: 40,
                  decoration: BoxDecoration(
                    color: paused
                        ? const Color(0xFFE2E0D9)
                        : const Color(0xFFDCE7F2),
                    borderRadius: BorderRadius.circular(13),
                  ),
                  child: Icon(
                    paused ? Icons.pause_rounded : Icons.repeat_rounded,
                    color: ink,
                  ),
                ),
                const SizedBox(width: 11),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        item.title,
                        style: const TextStyle(
                          fontSize: 17,
                          fontWeight: FontWeight.w900,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        paused
                            ? item.pausedUntil == null
                                  ? 'На паузе до возобновления'
                                  : 'На паузе до ${shortDate(item.pausedUntil!)}'
                            : '${routineScheduleLabel(item)} · ${clockTime(item.scheduledAt ?? DateTime.now())}',
                        style: const TextStyle(
                          color: Color(0xFF5C6965),
                          fontSize: 12.5,
                        ),
                      ),
                    ],
                  ),
                ),
                PopupMenuButton<String>(
                  onSelected: (value) => menu(context, value),
                  itemBuilder: (_) => [
                    const PopupMenuItem(value: 'edit', child: Text('Изменить')),
                    PopupMenuItem(
                      value: paused ? 'resume' : 'pause',
                      child: Text(paused ? 'Возобновить' : 'Поставить на паузу'),
                    ),
                    const PopupMenuItem(value: 'delete', child: Text('Удалить')),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 11),
            Row(
              children: [
                Expanded(
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(8),
                    child: LinearProgressIndicator(
                      value: progress,
                      minHeight: 6,
                      backgroundColor: const Color(0xFFE9ECEA),
                      valueColor: const AlwaysStoppedAnimation(green),
                    ),
                  ),
                ),
                const SizedBox(width: 9),
                Text(
                  '$completed из $goal',
                  style: const TextStyle(fontWeight: FontWeight.w900),
                ),
              ],
            ),
            if (minimum > 0) ...[
              const SizedBox(height: 5),
              Text(
                'Полностью: $full · минимум: $minimum',
                style: const TextStyle(color: Colors.black54, fontSize: 12),
              ),
            ],
            if (item.small.isNotEmpty) ...[
              const SizedBox(height: 9),
              Text(
                'Минимум: ${item.small}',
                style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700),
              ),
            ],
            const SizedBox(height: 11),
            if (paused)
              SizedBox(
                width: double.infinity,
                child: OutlinedButton.icon(
                  onPressed: () => app.resumeRoutine(item),
                  icon: const Icon(Icons.play_arrow_rounded),
                  label: const Text('Возобновить практику'),
                ),
              )
            else
              Row(
                children: [
                  if (item.useTimer) ...[
                    Expanded(
                      child: FilledButton.icon(
                        onPressed: () => Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (_) => Session(app: app, item: item),
                          ),
                        ),
                        icon: const Icon(Icons.play_arrow_rounded),
                        label: const Text('Начать'),
                      ),
                    ),
                    const SizedBox(width: 8),
                  ],
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () => record(context),
                      icon: const Icon(Icons.check_rounded),
                      label: const Text('Отметить'),
                    ),
                  ),
                ],
              ),
          ],
        ),
      ),
    );
  }
}

class RoutineResultSheet extends StatelessWidget {
  const RoutineResultSheet({required this.item, super.key});
  final ActionItem item;

  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.fromLTRB(18, 0, 18, 22),
    child: Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Как прошла практика?',
          style: TextStyle(fontSize: 22, fontWeight: FontWeight.w900),
        ),
        const SizedBox(height: 8),
        _option(context, 'Выполнено полностью', Icons.check_circle_rounded, RoutineResult.full),
        if (item.small.isNotEmpty || item.minimumMinutes > 0)
          _option(context, 'Выполнен минимальный вариант', Icons.spa_outlined, RoutineResult.minimum),
        _option(context, 'Сделана часть', Icons.timelapse_rounded, RoutineResult.partial),
        _option(context, 'Сегодня пропущено', Icons.remove_circle_outline, RoutineResult.skipped),
      ],
    ),
  );

  Widget _option(
    BuildContext context,
    String title,
    IconData icon,
    RoutineResult result,
  ) => ListTile(
    contentPadding: EdgeInsets.zero,
    leading: Icon(icon, color: green),
    title: Text(title, style: const TextStyle(fontWeight: FontWeight.w800)),
    trailing: const Icon(Icons.chevron_right_rounded),
    onTap: () => Navigator.pop(context, result),
  );
}

class RoutineRecoverySheet extends StatelessWidget {
  const RoutineRecoverySheet({required this.app, required this.item, super.key});
  final AppState app;
  final ActionItem item;

  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.fromLTRB(18, 0, 18, 22),
    child: Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Что стоит изменить?',
          style: TextStyle(fontSize: 22, fontWeight: FontWeight.w900),
        ),
        const SizedBox(height: 6),
        const Text('Пропуск не обнуляет путь. Можно изменить одно неудобное условие.'),
        const SizedBox(height: 10),
        ...[
          'Не подходит время',
          'Слишком большой объём',
          'Неудобные дни',
          'Напоминание раздражает',
          'Пока ничего не менять',
        ].map(
          (reason) => ListTile(
            contentPadding: EdgeInsets.zero,
            title: Text(reason),
            trailing: const Icon(Icons.chevron_right_rounded),
            onTap: () async {
              Navigator.pop(context);
              if (reason == 'Пока ничего не менять') return;
              await Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => RoutineEditor(app: app, existing: item),
                ),
              );
            },
          ),
        ),
      ],
    ),
  );
}

Future<void> showRoutinePause(
  BuildContext context,
  AppState app,
  ActionItem item,
) async {
  final choice = await showModalBottomSheet<String>(
    context: context,
    showDragHandle: true,
    builder: (sheetContext) => Padding(
      padding: const EdgeInsets.fromLTRB(18, 0, 18, 22),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Поставить практику на паузу',
            style: TextStyle(fontSize: 22, fontWeight: FontWeight.w900),
          ),
          const SizedBox(height: 6),
          const Text('Пауза не считается пропуском и не удаляет историю.'),
          ListTile(
            contentPadding: EdgeInsets.zero,
            title: const Text('На 3 дня'),
            onTap: () => Navigator.pop(sheetContext, '3'),
          ),
          ListTile(
            contentPadding: EdgeInsets.zero,
            title: const Text('На неделю'),
            onTap: () => Navigator.pop(sheetContext, '7'),
          ),
          ListTile(
            contentPadding: EdgeInsets.zero,
            title: const Text('Выбрать дату возвращения'),
            onTap: () => Navigator.pop(sheetContext, 'date'),
          ),
          ListTile(
            contentPadding: EdgeInsets.zero,
            title: const Text('Без даты'),
            onTap: () => Navigator.pop(sheetContext, 'open'),
          ),
        ],
      ),
    ),
  );
  if (choice == null || !context.mounted) return;
  DateTime? until;
  if (choice == '3' || choice == '7') {
    until = DateTime.now().add(Duration(days: int.parse(choice)));
  } else if (choice == 'date') {
    until = await showDatePicker(
      context: context,
      initialDate: DateTime.now().add(const Duration(days: 7)),
      firstDate: DateTime.now().add(const Duration(days: 1)),
      lastDate: DateTime.now().add(const Duration(days: 730)),
    );
    if (until == null) return;
  }
  await app.pauseRoutine(item, until);
}'''

text = replace_class(text, 'Onboarding', 'IntroPage', ONBOARDING)
text = replace_class(text, 'IntroPage', 'HowItWorksPage', INTRO)
text = replace_class(text, 'Shell', 'Today', SHELL)
text = replace_class(text, 'Today', '_PremiumTodayHeader', TODAY)
text = replace_class(text, '_PremiumTodayHeader', '_PremiumEmptyState', HEADER)
text = replace_class(text, 'RoutineEditor', 'GoalSupportPanel', ROUTINE_BLOCK)
text = replace_class(text, 'GoalHero', 'EmptyAction', GOAL_HERO)
text = replace_class(text, 'GoalScreen', 'GoalEditor', GOAL_SCREEN)

text = text.replace('fontSize: 34,\n            height: 1.07,', 'fontSize: 30,\n            height: 1.1,', 1)
text = text.replace('fontSize: 27,\n            fontWeight: FontWeight.w900,', 'fontSize: 23,\n            fontWeight: FontWeight.w900,', 1)
text = text.replace('fontSize: 20,\n            fontWeight: FontWeight.w900,', 'fontSize: 18,\n            fontWeight: FontWeight.w900,', 1)
text = text.replace('bodyLarge: TextStyle(color: ink, fontSize: 17, height: 1.45)', 'bodyLarge: TextStyle(color: ink, fontSize: 16, height: 1.42)', 1)
text = text.replace('minimumSize: const Size.fromHeight(56)', 'minimumSize: const Size.fromHeight(52)', 1)
text = text.replace('borderRadius: BorderRadius.circular(22)', 'borderRadius: BorderRadius.circular(19)', 1)

old_meta = """  if (item.kind == IntentKind.routine) {
    return 'Каждый день${item.scheduledAt == null ? '' : ' в ${clockTime(item.scheduledAt!)}'}${item.useTimer ? ' · ${durationLabel(item.minutes)}' : ' · без таймера'}';
  }"""
new_meta = """  if (item.kind == IntentKind.routine) {
    final time = item.scheduledAt == null ? '' : ' · ${clockTime(item.scheduledAt!)}';
    final duration = item.useTimer ? ' · ${durationLabel(item.minutes)}' : ' · без таймера';
    return '${routineScheduleLabel(item)}$time$duration';
  }"""
if old_meta in text:
    text = text.replace(old_meta, new_meta, 1)

path.write_text(text, encoding='utf-8')
print('Applied compact v0.6 UI, goal navigation and routine experience')
