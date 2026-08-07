from pathlib import Path

main_path = Path('lib/main.dart')
text = main_path.read_text(encoding='utf-8')

FIRST_CAPTURE = r'''class FirstCapturePage extends StatefulWidget {
  const FirstCapturePage({required this.app, super.key});
  final AppState app;

  @override
  State<FirstCapturePage> createState() => _FirstCapturePageState();
}

class _FirstCapturePageState extends State<FirstCapturePage> {
  final quick = TextEditingController();
  final List<ActionItem> added = [];

  @override
  void dispose() {
    quick.dispose();
    super.dispose();
  }

  void addQuick() {
    final value = quick.text.trim();
    if (value.isEmpty) return;
    final item = ActionItem(
      id: DateTime.now().microsecondsSinceEpoch.toString(),
      title: value,
      small: '',
      minutes: 0,
      support: Support.solo,
      goal: false,
      kind: IntentKind.focus,
      useTimer: false,
    );
    widget.app.add(item);
    added.add(item);
    quick.clear();
    setState(() {});
  }

  Future<void> setReminder(ActionItem item) async {
    final when = await showActionSchedule(context, item.scheduledAt);
    if (when == null) return;
    item.kind = IntentKind.reminder;
    item.useTimer = false;
    item.scheduledAt = when;
    widget.app.updateAction(item);
    await NotificationService.instance.schedule(item);
    if (mounted) setState(() {});
  }

  Future<void> plan(ActionItem item) async {
    final when = await showActionSchedule(context, item.scheduledAt);
    if (when == null) return;
    item.kind = IntentKind.focus;
    item.scheduledAt = when;
    widget.app.updateAction(item);
    await NotificationService.instance.schedule(item);
    if (mounted) setState(() {});
  }

  Future<void> repeat(ActionItem item) async {
    await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => RoutineEditor(app: widget.app, existing: item),
      ),
    );
    if (mounted) setState(() {});
  }

  void remove(ActionItem item) {
    widget.app.deleteAction(item);
    added.remove(item);
    setState(() {});
  }

  void continueToStep() {
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(
        builder: (_) => ActionEditor(app: widget.app, goalDefault: true),
      ),
    );
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Новый план')),
    body: ListView(
      key: const ValueKey('first-capture-page'),
      padding: const EdgeInsets.fromLTRB(18, 8, 18, 24),
      children: [
        const Icon(Icons.check_circle_rounded, color: green, size: 34),
        const SizedBox(height: 10),
        const Text(
          'Главная цель создана',
          style: TextStyle(
            color: ink,
            fontSize: 25,
            height: 1.08,
            fontWeight: FontWeight.w700,
            letterSpacing: -.45,
          ),
        ),
        if (widget.app.goal != null) ...[
          const SizedBox(height: 5),
          Text(
            widget.app.goal!.title,
            style: const TextStyle(
              color: green,
              fontSize: 14,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
        const SizedBox(height: 22),
        const Text(
          'Что ещё сейчас занимает вашу голову?',
          style: TextStyle(
            color: ink,
            fontSize: 20,
            height: 1.15,
            fontWeight: FontWeight.w700,
            letterSpacing: -.25,
          ),
        ),
        const SizedBox(height: 7),
        const Text(
          'Быстро запишите несколько дел. Они останутся отдельно от главной цели, а время и повторение можно добавить сразу или позже.',
          style: TextStyle(
            color: Color(0xFF5E6A66),
            fontSize: 13.5,
            height: 1.4,
          ),
        ),
        const SizedBox(height: 14),
        Row(
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            Expanded(
              key: const ValueKey('first-capture-field'),
              child: VoiceField(
                controller: quick,
                label: 'Быстрая запись',
                hint: 'Оплатить счёт, позвонить врачу…',
                lines: 1,
              ),
            ),
            const SizedBox(width: 8),
            SizedBox(
              width: 48,
              height: 48,
              child: FilledButton(
                key: const ValueKey('first-capture-add'),
                style: FilledButton.styleFrom(
                  padding: EdgeInsets.zero,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14),
                  ),
                ),
                onPressed: addQuick,
                child: const Icon(Icons.add_rounded),
              ),
            ),
          ],
        ),
        if (added.isNotEmpty) ...[
          const SizedBox(height: 14),
          ...added.map(
            (item) => Container(
              key: ValueKey('captured-${item.id}'),
              padding: const EdgeInsets.symmetric(vertical: 9),
              decoration: const BoxDecoration(
                border: Border(bottom: BorderSide(color: Color(0xFFE1E5E3))),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.check_box_outline_blank_rounded, color: green, size: 19),
                      const SizedBox(width: 9),
                      Expanded(
                        child: Text(
                          item.title,
                          style: const TextStyle(
                            color: ink,
                            fontSize: 14.5,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                      IconButton(
                        tooltip: 'Удалить',
                        visualDensity: VisualDensity.compact,
                        onPressed: () => remove(item),
                        icon: const Icon(Icons.close_rounded, size: 18),
                      ),
                    ],
                  ),
                  Padding(
                    padding: const EdgeInsets.only(left: 28),
                    child: Wrap(
                      spacing: 3,
                      runSpacing: 1,
                      children: [
                        TextButton(
                          onPressed: () => setReminder(item),
                          child: const Text('Напомнить'),
                        ),
                        TextButton(
                          onPressed: () => plan(item),
                          child: const Text('Запланировать'),
                        ),
                        TextButton(
                          onPressed: () => repeat(item),
                          child: const Text('Повторять'),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
        const SizedBox(height: 18),
        FilledButton(
          key: const ValueKey('continue-first-step'),
          onPressed: continueToStep,
          child: const Text('Перейти к первому шагу'),
        ),
        TextButton(
          key: const ValueKey('skip-first-capture'),
          onPressed: continueToStep,
          child: const Text('Пока ничего не добавлять'),
        ),
      ],
    ),
  );
}'''

text = text.replace(
    'class ActionEditor extends StatefulWidget',
    FIRST_CAPTURE.rstrip() + '\n\nclass ActionEditor extends StatefulWidget',
    1,
)

old_goal_route = '''        MaterialPageRoute(
          builder: (_) => ActionEditor(app: widget.app, goalDefault: true),
        ),'''
new_goal_route = '''        MaterialPageRoute(
          builder: (_) => FirstCapturePage(app: widget.app),
        ),'''
goal_start = text.index('class GoalEditor extends StatefulWidget')
goal_end = text.index('class FirstCapturePage extends StatefulWidget', goal_start)
goal_section = text[goal_start:goal_end]
if old_goal_route not in goal_section:
    raise SystemExit('Goal creation route not found in GoalEditor')
goal_section = goal_section.replace(old_goal_route, new_goal_route, 1)
text = text[:goal_start] + goal_section + text[goal_end:]

# Editing a regular practice should return to the screen that opened it.
old_routine_close = '''    if (!mounted) return;
    Navigator.popUntil(context, (route) => route.isFirst);
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(
      title: Text(
        widget.existing == null ? 'Регулярная практика' : 'Изменить практику','''
new_routine_close = '''    if (!mounted) return;
    if (existing == null) {
      Navigator.popUntil(context, (route) => route.isFirst);
    } else {
      Navigator.pop(context);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(
      title: Text(
        widget.existing == null ? 'Регулярная практика' : 'Изменить практику','''
if old_routine_close not in text:
    raise SystemExit('Routine close block not found')
text = text.replace(old_routine_close, new_routine_close, 1)

main_path.write_text(text, encoding='utf-8')
print('Applied v0.6.5 first capture flow')
