from pathlib import Path

main_path = Path('lib/main.dart')
pubspec_path = Path('pubspec.yaml')
text = main_path.read_text(encoding='utf-8')

TODAY_BLOCK = r'''String _todayDateLabel(DateTime value) {
  const weekdays = [
    'понедельник',
    'вторник',
    'среда',
    'четверг',
    'пятница',
    'суббота',
    'воскресенье',
  ];
  const months = [
    'января',
    'февраля',
    'марта',
    'апреля',
    'мая',
    'июня',
    'июля',
    'августа',
    'сентября',
    'октября',
    'ноября',
    'декабря',
  ];
  return '${weekdays[value.weekday - 1]}, ${value.day} ${months[value.month - 1]}';
}

String _supportShortLabel(Support support) => switch (support) {
  Support.solo => 'Самостоятельно',
  Support.ai => 'С цифровым помощником',
  Support.together => 'Вместе с человеком',
  Support.report => 'С отчётом',
  Support.curator => 'С куратором',
};

String _workMeta(ActionItem item) {
  if (item.kind == IntentKind.routine) {
    return 'Регулярная практика · ${item.useTimer ? durationLabel(item.minutes) : 'до результата'}';
  }
  if (item.kind == IntentKind.reminder && item.scheduledAt != null) {
    return '${shortDate(item.scheduledAt!)} · ${clockTime(item.scheduledAt!)}';
  }
  if (item.scheduledAt != null) {
    return '${shortDate(item.scheduledAt!)} · ${clockTime(item.scheduledAt!)}';
  }
  return item.useTimer && item.minutes > 0
      ? durationLabel(item.minutes)
      : 'Без времени';
}

class Today extends StatefulWidget {
  const Today({required this.app, required this.onOpenGoal, super.key});
  final AppState app;
  final VoidCallback onOpenGoal;

  @override
  State<Today> createState() => _TodayState();
}

class _TodayState extends State<Today> {
  final quick = TextEditingController();

  @override
  void dispose() {
    quick.dispose();
    super.dispose();
  }

  void _addQuick() {
    final value = quick.text.trim();
    if (value.isEmpty) return;
    widget.app.add(
      ActionItem(
        id: DateTime.now().microsecondsSinceEpoch.toString(),
        title: value,
        small: '',
        minutes: 0,
        support: Support.solo,
        goal: false,
        kind: IntentKind.focus,
        useTimer: false,
      ),
    );
    quick.clear();
    setState(() {});
  }

  Future<void> _openWork(BuildContext context, ActionItem item) async {
    await showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      showDragHandle: true,
      builder: (_) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(14, 0, 14, 20),
          child: item.kind == IntentKind.routine
              ? RoutineCard(app: widget.app, item: item)
              : ActionCard(app: widget.app, item: item),
        ),
      ),
    );
    if (mounted) setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    final active = widget.app.actions.where((item) => item.state == null).toList();
    final goalActions = active
        .where((item) => item.goal && item.kind != IntentKind.routine)
        .toList()
      ..sort((a, b) {
        final aDate = a.scheduledAt;
        final bDate = b.scheduledAt;
        if (aDate == null && bDate == null) return 0;
        if (aDate == null) return -1;
        if (bDate == null) return 1;
        return aDate.compareTo(bDate);
      });
    final otherToday = active.where((item) {
      if (item.goal) return false;
      if (item.kind == IntentKind.routine) return routineDueToday(item);
      return !isLater(item);
    }).toList();
    final allOther = active.where((item) => !item.goal).toList();

    return Scaffold(
      backgroundColor: cream,
      appBar: AppBar(
        toolbarHeight: 64,
        titleSpacing: 18,
        title: const Text(
          'Сегодня',
          style: TextStyle(
            color: ink,
            fontSize: 29,
            height: 1,
            fontWeight: FontWeight.w700,
            letterSpacing: -.7,
          ),
        ),
        actions: [
          IconButton(
            key: const ValueKey('today-add'),
            tooltip: 'Добавить',
            icon: const Icon(Icons.add_rounded),
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => IntentChooserPage(app: widget.app),
              ),
            ),
          ),
          IconButton(
            tooltip: 'Как работает приложение',
            icon: const Icon(Icons.info_outline_rounded),
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => Onboarding(app: widget.app, preview: true),
              ),
            ),
          ),
          const SizedBox(width: 5),
        ],
      ),
      body: ListView(
        key: const ValueKey('today-editorial-scroll'),
        padding: const EdgeInsets.fromLTRB(18, 0, 18, 24),
        children: [
          Text(
            _todayDateLabel(DateTime.now()),
            style: const TextStyle(
              color: Color(0xFF7A8581),
              fontSize: 12.5,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 15),
          _TodayGoalArea(
            app: widget.app,
            actions: goalActions,
            onOpenGoal: widget.onOpenGoal,
          ),
          const SizedBox(height: 19),
          const Divider(height: 1, color: Color(0xFFDDE2DF)),
          const SizedBox(height: 17),
          _TodayOtherArea(
            app: widget.app,
            items: otherToday,
            allCount: allOther.length,
            quick: quick,
            onAddQuick: _addQuick,
            onOpen: (item) => _openWork(context, item),
          ),
        ],
      ),
    );
  }
}

class _TodayGoalArea extends StatelessWidget {
  const _TodayGoalArea({
    required this.app,
    required this.actions,
    required this.onOpenGoal,
  });

  final AppState app;
  final List<ActionItem> actions;
  final VoidCallback onOpenGoal;

  Future<void> _record(BuildContext context, ActionItem item) async {
    final state = await showModalBottomSheet<ResultState>(
      context: context,
      showDragHandle: true,
      builder: (sheetContext) =>
          Finish(onFinish: (value) => Navigator.pop(sheetContext, value)),
    );
    if (state == null || !context.mounted) return;
    if (state == ResultState.moved) {
      final when = await showActionSchedule(context, item.scheduledAt);
      if (when != null) await app.reschedule(item, when);
      return;
    }
    app.complete(item, state);
    if (!context.mounted) return;
    await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => ResultPage(app: app, item: item, state: state),
      ),
    );
  }

  Future<void> _start(BuildContext context, ActionItem item) async {
    if (!item.useTimer) {
      await _record(context, item);
      return;
    }
    await Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => Session(app: app, item: item)),
    );
  }

  @override
  Widget build(BuildContext context) {
    final goal = app.goal;
    if (goal == null) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'С чего начнём?',
            style: TextStyle(
              color: ink,
              fontSize: 23,
              height: 1.12,
              fontWeight: FontWeight.w700,
              letterSpacing: -.35,
            ),
          ),
          const SizedBox(height: 6),
          const Text(
            'Создайте важную цель или сразу выгрузите обычное дело из головы.',
            style: TextStyle(
              color: Color(0xFF5D6965),
              fontSize: 13.5,
              height: 1.38,
            ),
          ),
          const SizedBox(height: 13),
          FilledButton(
            key: const ValueKey('create-main-goal'),
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => GoalEditor(app: app)),
            ),
            child: const Text('Создать главную цель'),
          ),
        ],
      );
    }

    final next = actions.isEmpty ? null : actions.first;
    return Container(
      padding: const EdgeInsets.only(left: 15),
      decoration: const BoxDecoration(
        border: Border(
          left: BorderSide(color: green, width: 3),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'ГЛАВНАЯ ЦЕЛЬ',
            style: TextStyle(
              color: green,
              fontSize: 9.8,
              fontWeight: FontWeight.w700,
              letterSpacing: 1.05,
            ),
          ),
          const SizedBox(height: 5),
          Text(
            goal.title,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
            style: const TextStyle(
              color: ink,
              fontSize: 23,
              height: 1.1,
              fontWeight: FontWeight.w700,
              letterSpacing: -.45,
            ),
          ),
          const SizedBox(height: 13),
          const Text(
            'Следующий шаг',
            style: TextStyle(
              color: Color(0xFF7A8581),
              fontSize: 11.5,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 4),
          if (next == null) ...[
            const Text(
              'Выберите первое конкретное действие',
              style: TextStyle(
                color: ink,
                fontSize: 17,
                height: 1.25,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 10),
            OutlinedButton(
              onPressed: () => Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => ActionEditor(app: app, goalDefault: true),
                ),
              ),
              child: const Text('Выбрать первый шаг'),
            ),
          ] else ...[
            Text(
              next.title,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(
                color: ink,
                fontSize: 18,
                height: 1.22,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 5),
            Text(
              '${next.useTimer && next.minutes > 0 ? durationLabel(next.minutes) : 'До результата'}  ·  ${_supportShortLabel(next.support)}',
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(
                color: Color(0xFF66726E),
                fontSize: 12,
              ),
            ),
            const SizedBox(height: 11),
            Row(
              children: [
                Expanded(
                  child: FilledButton(
                    key: const ValueKey('today-primary-action'),
                    onPressed: () => _start(context, next),
                    child: Text(next.useTimer ? 'Начать' : 'Отметить'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: TextButton(
                    key: const ValueKey('today-open-goal'),
                    onPressed: onOpenGoal,
                    child: const Text('Путь к цели'),
                  ),
                ),
              ],
            ),
          ],
        ],
      ),
    );
  }
}

class _TodayOtherArea extends StatelessWidget {
  const _TodayOtherArea({
    required this.app,
    required this.items,
    required this.allCount,
    required this.quick,
    required this.onAddQuick,
    required this.onOpen,
  });

  final AppState app;
  final List<ActionItem> items;
  final int allCount;
  final TextEditingController quick;
  final VoidCallback onAddQuick;
  final ValueChanged<ActionItem> onOpen;

  @override
  Widget build(BuildContext context) {
    final visible = items.take(3).toList();
    final hidden = items.length - visible.length;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            const Expanded(
              child: Text(
                'Остальное на сегодня',
                style: TextStyle(
                  color: ink,
                  fontSize: 19,
                  fontWeight: FontWeight.w700,
                  letterSpacing: -.2,
                ),
              ),
            ),
            IconButton(
              key: const ValueKey('add-other-work'),
              tooltip: 'Добавить дело',
              visualDensity: VisualDensity.compact,
              onPressed: () => Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => IntentChooserPage(app: app),
                ),
              ),
              icon: const Icon(Icons.add_rounded, color: green),
            ),
          ],
        ),
        if (visible.isEmpty)
          const Padding(
            padding: EdgeInsets.only(top: 3, bottom: 5),
            child: Text(
              'Пока здесь пусто. Добавьте то, что не хочется держать в голове.',
              style: TextStyle(
                color: Color(0xFF68736F),
                fontSize: 13,
                height: 1.35,
              ),
            ),
          )
        else
          ...visible.map(
            (item) => _TodayTaskRow(
              item: item,
              onTap: () => onOpen(item),
            ),
          ),
        if (hidden > 0)
          Padding(
            padding: const EdgeInsets.only(top: 2),
            child: Text(
              'Ещё $hidden ${taskWord(hidden)}',
              style: const TextStyle(
                color: green,
                fontSize: 12,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        const SizedBox(height: 14),
        const Text(
          'Что ещё держите в голове?',
          style: TextStyle(
            color: ink,
            fontSize: 15,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 7),
        Row(
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            Expanded(
              key: const ValueKey('quick-capture-field'),
              child: VoiceField(
                controller: quick,
                label: 'Быстрая запись',
                hint: 'Дело, напоминание или мысль…',
                lines: 1,
              ),
            ),
            const SizedBox(width: 8),
            SizedBox(
              width: 48,
              height: 48,
              child: FilledButton(
                key: const ValueKey('quick-capture-add'),
                style: FilledButton.styleFrom(
                  padding: EdgeInsets.zero,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14),
                  ),
                ),
                onPressed: onAddQuick,
                child: const Icon(Icons.add_rounded),
              ),
            ),
          ],
        ),
        Align(
          alignment: Alignment.centerLeft,
          child: TextButton(
            key: const ValueKey('all-work-link'),
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => AllWorkPage(app: app)),
            ),
            child: Text(allCount == 0 ? 'Все дела и планы' : 'Все дела и планы · $allCount'),
          ),
        ),
      ],
    );
  }
}

class _TodayTaskRow extends StatelessWidget {
  const _TodayTaskRow({required this.item, required this.onTap});
  final ActionItem item;
  final VoidCallback onTap;

  IconData get icon => switch (item.kind) {
    IntentKind.reminder => Icons.notifications_none_rounded,
    IntentKind.routine => Icons.repeat_rounded,
    _ => Icons.circle_outlined,
  };

  @override
  Widget build(BuildContext context) => InkWell(
    onTap: onTap,
    borderRadius: BorderRadius.circular(10),
    child: Padding(
      padding: const EdgeInsets.symmetric(vertical: 9),
      child: Row(
        children: [
          Icon(icon, color: green, size: 19),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  item.title,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    color: ink,
                    fontSize: 14.2,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 1),
                Text(
                  _workMeta(item),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    color: Color(0xFF7A8581),
                    fontSize: 11.5,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 6),
          const Icon(Icons.chevron_right_rounded, color: Color(0xFF9AA39F), size: 19),
        ],
      ),
    ),
  );
}

class AllWorkPage extends StatelessWidget {
  const AllWorkPage({required this.app, super.key});
  final AppState app;

  Future<void> _open(BuildContext context, ActionItem item) async {
    await showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      showDragHandle: true,
      builder: (_) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(14, 0, 14, 20),
          child: item.kind == IntentKind.routine
              ? RoutineCard(app: app, item: item)
              : ActionCard(app: app, item: item),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final items = app.actions
        .where((item) => !item.goal && item.state == null)
        .toList();
    return Scaffold(
      appBar: AppBar(
        title: const Text('Все дела и планы'),
        actions: [
          IconButton(
            tooltip: 'Добавить',
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => IntentChooserPage(app: app)),
            ),
            icon: const Icon(Icons.add_rounded),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(18, 6, 18, 28),
        children: [
          if (items.isEmpty)
            const Text(
              'Здесь появятся разовые дела, напоминания и регулярные практики.',
              style: TextStyle(color: Color(0xFF68736F), height: 1.4),
            )
          else
            ...items.map(
              (item) => _TodayTaskRow(
                item: item,
                onTap: () => _open(context, item),
              ),
            ),
        ],
      ),
    );
  }
}'''

start = text.index('class Today extends StatelessWidget')
end = text.index('class IntentChooserPage extends StatelessWidget', start)
text = text[:start] + TODAY_BLOCK.rstrip() + '\n\n' + text[end:]

main_path.write_text(text, encoding='utf-8')
pubspec = pubspec_path.read_text(encoding='utf-8')
pubspec = pubspec.replace('version: 0.6.4+17', 'version: 0.6.5+18', 1)
pubspec_path.write_text(pubspec, encoding='utf-8')
print('Applied v0.6.5 editorial Today')
