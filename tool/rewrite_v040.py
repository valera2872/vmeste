from pathlib import Path

main_path = Path('lib/main.dart')
pubspec_path = Path('pubspec.yaml')
text = main_path.read_text(encoding='utf-8')
pubspec = pubspec_path.read_text(encoding='utf-8')

if 'class IntentChooserPage' in text and 'version: 0.4.0+9' in pubspec:
    print('v0.4.0 already applied')
    raise SystemExit(0)


def replace(old: str, new: str) -> None:
    global text
    if old not in text:
        raise SystemExit(f'Expected fragment not found:\n{old[:400]}')
    text = text.replace(old, new, 1)


def replace_between(start_marker: str, end_marker: str, new_block: str) -> None:
    global text
    start = text.index(start_marker)
    end = text.index(end_marker, start)
    text = text[:start] + new_block.rstrip() + '\n\n' + text[end:]


replace(
    "import 'package:flutter/material.dart';",
    """import 'package:flutter/material.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:flutter_timezone/flutter_timezone.dart';
import 'package:timezone/data/latest.dart' as tz_data;
import 'package:timezone/timezone.dart' as tz;""",
)
replace(
    """  WidgetsFlutterBinding.ensureInitialized();
  final app = AppState();""",
    """  WidgetsFlutterBinding.ensureInitialized();
  await NotificationService.instance.init();
  final app = AppState();""",
)
replace(
    "enum Support { solo, ai, together, report, curator }",
    """enum Support { solo, ai, together, report, curator }

enum IntentKind { reminder, focus, routine, goalStep }""",
)

replace_between(
    'class ActionItem {',
    'class HistoryItem {',
    '''class ActionItem {
  ActionItem({
    required this.id,
    required this.title,
    required this.small,
    required this.minutes,
    required this.support,
    required this.goal,
    this.kind = IntentKind.focus,
    this.scheduledAt,
    this.repeatDaily = false,
    this.useTimer = true,
    this.state,
  });

  final String id, title, small;
  final int minutes;
  Support support;
  final bool goal;
  final IntentKind kind;
  DateTime? scheduledAt;
  final bool repeatDaily;
  final bool useTimer;
  ResultState? state;

  Map<String, dynamic> toJson() => {
    'id': id,
    'title': title,
    'small': small,
    'minutes': minutes,
    'support': support.name,
    'goal': goal,
    'kind': kind.name,
    'scheduledAt': scheduledAt?.toIso8601String(),
    'repeatDaily': repeatDaily,
    'useTimer': useTimer,
    'state': state?.name,
  };

  factory ActionItem.fromJson(Map<String, dynamic> j) => ActionItem(
    id: j['id'] ?? '',
    title: j['title'] ?? '',
    small: j['small'] ?? '',
    minutes: j['minutes'] ?? 10,
    support: Support.values.firstWhere(
      (e) => e.name == j['support'],
      orElse: () => Support.ai,
    ),
    goal: j['goal'] ?? false,
    kind: IntentKind.values.firstWhere(
      (e) => e.name == j['kind'],
      orElse: () => (j['goal'] ?? false)
          ? IntentKind.goalStep
          : IntentKind.focus,
    ),
    scheduledAt: DateTime.tryParse(j['scheduledAt'] ?? ''),
    repeatDaily: j['repeatDaily'] ?? false,
    useTimer: j['useTimer'] ?? true,
    state: j['state'] == null
        ? null
        : ResultState.values.firstWhere((e) => e.name == j['state']),
  );
}''',
)

notification_service = r'''class NotificationService {
  NotificationService._();

  static final instance = NotificationService._();
  final FlutterLocalNotificationsPlugin plugin =
      FlutterLocalNotificationsPlugin();
  bool ready = false;

  Future<void> init() async {
    try {
      tz_data.initializeTimeZones();
      final zone = await FlutterTimezone.getLocalTimezone();
      tz.setLocalLocation(tz.getLocation(zone.identifier));
      await plugin.initialize(
        settings: const InitializationSettings(
          android: AndroidInitializationSettings('@mipmap/ic_launcher'),
        ),
      );
      ready = true;
    } catch (_) {
      ready = false;
    }
  }

  int _id(String value) {
    var hash = 0;
    for (final code in value.codeUnits) {
      hash = (hash * 31 + code) & 0x7fffffff;
    }
    return hash;
  }

  Future<bool> schedule(ActionItem item) async {
    if (!ready || item.scheduledAt == null) return false;
    try {
      final android = plugin.resolvePlatformSpecificImplementation<
          AndroidFlutterLocalNotificationsPlugin>();
      final allowed = await android?.requestNotificationsPermission();
      if (allowed == false) return false;

      var when = tz.TZDateTime.from(item.scheduledAt!, tz.local);
      final now = tz.TZDateTime.now(tz.local);
      if (item.repeatDaily) {
        while (!when.isAfter(now)) {
          when = when.add(const Duration(days: 1));
        }
      } else if (!when.isAfter(now)) {
        return false;
      }

      await plugin.zonedSchedule(
        id: _id(item.id),
        title: 'Вместе к цели',
        body: item.title,
        scheduledDate: when,
        notificationDetails: const NotificationDetails(
          android: AndroidNotificationDetails(
            'vmeste_reminders',
            'Напоминания',
            channelDescription: 'Напоминания о выбранных делах и практиках',
            importance: Importance.high,
            priority: Priority.high,
          ),
        ),
        androidScheduleMode: AndroidScheduleMode.inexactAllowWhileIdle,
        matchDateTimeComponents:
            item.repeatDaily ? DateTimeComponents.time : null,
        payload: item.id,
      );
      return true;
    } catch (_) {
      return false;
    }
  }

  Future<void> cancel(String id) async {
    if (!ready) return;
    try {
      await plugin.cancel(id: _id(id));
    } catch (_) {}
  }
}

'''
app_state_at = text.index('class AppState extends ChangeNotifier {')
text = text[:app_state_at] + notification_service + text[app_state_at:]

replace(
    '''  void complete(ActionItem a, ResultState s) {
    a.state = s;
    history.insert(
      0,
      HistoryItem(a.title, a.minutes, a.support, s, DateTime.now(), a.goal),
    );
    notifyListeners();
    save();
  }''',
    '''  void complete(ActionItem a, ResultState s) {
    history.insert(
      0,
      HistoryItem(a.title, a.minutes, a.support, s, DateTime.now(), a.goal),
    );

    if (a.kind == IntentKind.routine &&
        (s == ResultState.done || s == ResultState.part)) {
      final base = a.scheduledAt ?? DateTime.now();
      a.scheduledAt = DateTime(
        base.year,
        base.month,
        base.day + 1,
        base.hour,
        base.minute,
      );
    } else {
      a.state = s;
      unawaited(NotificationService.instance.cancel(a.id));
    }
    notifyListeners();
    save();
  }''',
)

replace(
    '''      floatingActionButton: FloatingActionButton.extended(
        backgroundColor: ink,
        foregroundColor: Colors.white,
        onPressed: () => Navigator.push(
          context,
          MaterialPageRoute(
            builder: (_) => ActionEditor(app: app, goalDefault: false),
          ),
        ),
        icon: const Icon(Icons.add),
        label: const Text('Добавить дело'),
      ),''',
    '''      floatingActionButton: FloatingActionButton.extended(
        backgroundColor: ink,
        foregroundColor: Colors.white,
        onPressed: () => Navigator.push(
          context,
          MaterialPageRoute(builder: (_) => IntentChooserPage(app: app)),
        ),
        icon: const Icon(Icons.add),
        label: const Text('Добавить'),
      ),''',
)
text = text.replace("section('Другие дела на сегодня')", "section('Сегодня и ближайшие дела')")
text = text.replace("'Других дел на сегодня пока нет.'", "'Других дел и напоминаний пока нет.'")

intent_pages = r'''class IntentChooserPage extends StatelessWidget {
  const IntentChooserPage({required this.app, super.key});

  final AppState app;

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Что добавить?')),
    body: ListView(
      padding: const EdgeInsets.fromLTRB(18, 4, 18, 32),
      children: [
        Text(
          'Какая помощь нужна сейчас?',
          style: Theme.of(context).textTheme.headlineMedium,
        ),
        const SizedBox(height: 7),
        const Text(
          'Не каждое намерение требует таймера или большой цели. Выберите подходящий формат.',
        ),
        const SizedBox(height: 18),
        _IntentChoice(
          icon: Icons.alarm_rounded,
          title: 'Просто напомнить',
          text: 'Разовое дело в выбранный день и время.',
          onTap: () => Navigator.push(
            context,
            MaterialPageRoute(builder: (_) => ReminderEditor(app: app)),
          ),
        ),
        _IntentChoice(
          icon: Icons.play_circle_outline_rounded,
          title: 'Сделать дело',
          text: 'Начать с таймером или без него и при необходимости выбрать поддержку.',
          onTap: () => Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => ActionEditor(app: app, goalDefault: false),
            ),
          ),
        ),
        _IntentChoice(
          icon: Icons.repeat_rounded,
          title: 'Повторять регулярно',
          text: 'Создать ежедневную практику и не терять её после пропуска.',
          onTap: () => Navigator.push(
            context,
            MaterialPageRoute(builder: (_) => RoutineEditor(app: app)),
          ),
        ),
        _IntentChoice(
          icon: Icons.flag_outlined,
          title: 'Дойти до цели',
          text: 'Описать долгосрочный результат и двигаться к нему отдельными действиями.',
          onTap: () => Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => GoalEditor(app: app, existing: app.goal),
            ),
          ),
        ),
      ],
    ),
  );
}

class _IntentChoice extends StatelessWidget {
  const _IntentChoice({
    required this.icon,
    required this.title,
    required this.text,
    required this.onTap,
  });

  final IconData icon;
  final String title, text;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) => Card(
    margin: const EdgeInsets.only(bottom: 10),
    child: ListTile(
      contentPadding: const EdgeInsets.all(15),
      leading: Container(
        width: 48,
        height: 48,
        decoration: BoxDecoration(
          color: mint,
          borderRadius: BorderRadius.circular(15),
        ),
        child: Icon(icon, color: ink),
      ),
      title: Text(title, style: const TextStyle(fontWeight: FontWeight.w900)),
      subtitle: Padding(
        padding: const EdgeInsets.only(top: 5),
        child: Text(text),
      ),
      trailing: const Icon(Icons.chevron_right_rounded),
      onTap: onTap,
    ),
  );
}

class ReminderEditor extends StatefulWidget {
  const ReminderEditor({required this.app, super.key});

  final AppState app;

  @override
  State<ReminderEditor> createState() => _ReminderEditorState();
}

class _ReminderEditorState extends State<ReminderEditor> {
  final title = TextEditingController();
  late DateTime scheduledAt;

  @override
  void initState() {
    super.initState();
    final next = DateTime.now().add(const Duration(hours: 1));
    scheduledAt = DateTime(next.year, next.month, next.day, next.hour, 0);
    title.addListener(() => setState(() {}));
  }

  @override
  void dispose() {
    title.dispose();
    super.dispose();
  }

  Future<void> chooseDate() async {
    final value = await showDatePicker(
      context: context,
      initialDate: scheduledAt,
      firstDate: DateTime.now(),
      lastDate: DateTime.now().add(const Duration(days: 730)),
    );
    if (value == null) return;
    setState(() {
      scheduledAt = DateTime(
        value.year,
        value.month,
        value.day,
        scheduledAt.hour,
        scheduledAt.minute,
      );
    });
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
    final item = ActionItem(
      id: DateTime.now().microsecondsSinceEpoch.toString(),
      title: title.text.trim(),
      small: '',
      minutes: 0,
      support: Support.solo,
      goal: false,
      kind: IntentKind.reminder,
      scheduledAt: scheduledAt,
      useTimer: false,
    );
    widget.app.add(item);
    final scheduled = await NotificationService.instance.schedule(item);
    if (!mounted) return;
    if (!scheduled) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text(
            'Дело сохранено. Разрешите уведомления в настройках телефона, чтобы получать напоминание.',
          ),
        ),
      );
    }
    Navigator.popUntil(context, (route) => route.isFirst);
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Просто напомнить')),
    body: ListView(
      padding: const EdgeInsets.all(18),
      children: [
        Text(
          'О чём напомнить?',
          style: Theme.of(context).textTheme.headlineMedium,
        ),
        const SizedBox(height: 7),
        const Text('Здесь не нужно указывать длительность или создавать цель.'),
        const SizedBox(height: 18),
        VoiceField(
          controller: title,
          label: 'Дело',
          hint: 'Например: оплатить интернет',
          lines: 2,
        ),
        const SizedBox(height: 16),
        Card(
          child: Column(
            children: [
              ListTile(
                leading: const Icon(Icons.calendar_today_outlined),
                title: const Text('День'),
                subtitle: Text(shortDate(scheduledAt)),
                trailing: const Icon(Icons.chevron_right),
                onTap: chooseDate,
              ),
              const Divider(height: 1),
              ListTile(
                leading: const Icon(Icons.schedule_rounded),
                title: const Text('Время'),
                subtitle: Text(clockTime(scheduledAt)),
                trailing: const Icon(Icons.chevron_right),
                onTap: chooseTime,
              ),
            ],
          ),
        ),
        const SizedBox(height: 20),
        FilledButton.icon(
          onPressed: title.text.trim().isEmpty ? null : save,
          icon: const Icon(Icons.notifications_active_outlined),
          label: const Text('Сохранить напоминание'),
        ),
      ],
    ),
  );
}

class RoutineEditor extends StatefulWidget {
  const RoutineEditor({required this.app, super.key});

  final AppState app;

  @override
  State<RoutineEditor> createState() => _RoutineEditorState();
}

class _RoutineEditorState extends State<RoutineEditor> {
  final title = TextEditingController();
  int minutes = 15;
  bool useTimer = true;
  late DateTime scheduledAt;

  @override
  void initState() {
    super.initState();
    final next = DateTime.now().add(const Duration(hours: 1));
    scheduledAt = DateTime(next.year, next.month, next.day, next.hour, 0);
    title.addListener(() => setState(() {}));
  }

  @override
  void dispose() {
    title.dispose();
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
    final item = ActionItem(
      id: DateTime.now().microsecondsSinceEpoch.toString(),
      title: title.text.trim(),
      small: '',
      minutes: useTimer ? minutes : 0,
      support: Support.solo,
      goal: false,
      kind: IntentKind.routine,
      scheduledAt: scheduledAt,
      repeatDaily: true,
      useTimer: useTimer,
    );
    widget.app.add(item);
    final scheduled = await NotificationService.instance.schedule(item);
    if (!mounted) return;
    if (!scheduled) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text(
            'Практика сохранена. Для ежедневных уведомлений разрешите их в настройках телефона.',
          ),
        ),
      );
    }
    Navigator.popUntil(context, (route) => route.isFirst);
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Регулярная практика')),
    body: ListView(
      padding: const EdgeInsets.all(18),
      children: [
        Text(
          'Что хотите повторять?',
          style: Theme.of(context).textTheme.headlineMedium,
        ),
        const SizedBox(height: 7),
        const Text(
          'В этой версии практика повторяется каждый день. Выбор отдельных дней недели будет следующим шагом.',
        ),
        const SizedBox(height: 18),
        VoiceField(
          controller: title,
          label: 'Практика',
          hint: 'Например: заниматься английским',
          lines: 2,
        ),
        const SizedBox(height: 14),
        Card(
          child: ListTile(
            leading: const Icon(Icons.alarm_rounded),
            title: const Text('Каждый день'),
            subtitle: Text('Напомнить в ${clockTime(scheduledAt)}'),
            trailing: const Icon(Icons.chevron_right),
            onTap: chooseTime,
          ),
        ),
        SwitchListTile.adaptive(
          contentPadding: EdgeInsets.zero,
          title: const Text(
            'Использовать таймер',
            style: TextStyle(fontWeight: FontWeight.w900),
          ),
          subtitle: const Text(
            'Можно оставить практику без ограничения времени и просто отмечать выполнение.',
          ),
          value: useTimer,
          onChanged: (value) => setState(() => useTimer = value),
        ),
        if (useTimer) ...[
          const SizedBox(height: 8),
          const Text(
            'Обычная длительность',
            style: TextStyle(fontWeight: FontWeight.w900, fontSize: 17),
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [5, 10, 15, 25, 40, 60]
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
        const SizedBox(height: 22),
        FilledButton.icon(
          onPressed: title.text.trim().isEmpty ? null : save,
          icon: const Icon(Icons.repeat_rounded),
          label: const Text('Сохранить практику'),
        ),
      ],
    ),
  );
}

'''
insert_at = text.index('class GoalSupportPanel extends StatelessWidget {')
text = text[:insert_at] + intent_pages + text[insert_at:]

replace_between(
    'class ActionCard extends StatelessWidget {',
    'class GoalScreen extends StatelessWidget {',
    r'''class ActionCard extends StatelessWidget {
  const ActionCard({
    required this.app,
    required this.item,
    this.featured = false,
    super.key,
  });

  final AppState app;
  final ActionItem item;
  final bool featured;

  Future<void> _startTogether(BuildContext context) async {
    app.setSupport(item, Support.together);
    await shareStartMessage(item.title, item.minutes, Support.together);
    if (!context.mounted || !item.useTimer) return;
    await Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => Session(app: app, item: item)),
    );
  }

  Future<void> _primary(BuildContext context) async {
    if (item.kind == IntentKind.reminder || !item.useTimer) {
      app.complete(item, ResultState.done);
      return;
    }
    await Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => Session(app: app, item: item)),
    );
  }

  @override
  Widget build(BuildContext context) => Card(
    color: featured ? const Color(0xFFFFFCF5) : Colors.white,
    child: Padding(
      padding: const EdgeInsets.all(17),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 42,
                height: 42,
                decoration: BoxDecoration(
                  color: intentColor(item.kind),
                  borderRadius: BorderRadius.circular(14),
                ),
                child: Icon(
                  item.state == null ? intentIcon(item.kind) : Icons.check,
                  color: ink,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      item.title,
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.w900,
                        decoration: item.state == null
                            ? null
                            : TextDecoration.lineThrough,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(actionMeta(item)),
                  ],
                ),
              ),
            ],
          ),
          if (item.small.isNotEmpty && item.state == null) ...[
            const SizedBox(height: 11),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: cream,
                borderRadius: BorderRadius.circular(14),
              ),
              child: Text('Если времени мало: ${item.small}'),
            ),
          ],
          const SizedBox(height: 13),
          if (item.state == null)
            item.kind == IntentKind.reminder
                ? SizedBox(
                    width: double.infinity,
                    child: FilledButton.icon(
                      onPressed: () => _primary(context),
                      icon: const Icon(Icons.check_rounded),
                      label: const Text('Отметить выполненным'),
                    ),
                  )
                : Row(
                    children: [
                      Expanded(
                        child: FilledButton.icon(
                          onPressed: () => _primary(context),
                          icon: Icon(
                            item.useTimer
                                ? Icons.play_arrow
                                : Icons.check_rounded,
                          ),
                          label: Text(
                            item.useTimer ? 'Начать' : 'Выполнено',
                          ),
                        ),
                      ),
                      const SizedBox(width: 9),
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: () => _startTogether(context),
                          icon: const Icon(Icons.people_alt_outlined),
                          label: const Text('Вместе'),
                        ),
                      ),
                    ],
                  )
          else
            Text(
              resultName(item.state!),
              style: const TextStyle(color: green, fontWeight: FontWeight.w900),
            ),
        ],
      ),
    ),
  );
}''',
)

replace_between(
    'class ActionEditor extends StatefulWidget {',
    'class Speech {',
    r'''class ActionEditor extends StatefulWidget {
  const ActionEditor({
    required this.app,
    required this.goalDefault,
    this.initialSupport,
    super.key,
  });

  final AppState app;
  final bool goalDefault;
  final Support? initialSupport;

  @override
  State<ActionEditor> createState() => _ActionEditorState();
}

class _ActionEditorState extends State<ActionEditor> {
  final title = TextEditingController(), small = TextEditingController();
  int minutes = 15;
  bool useTimer = true;
  late bool linked;
  Support? chosen;
  bool showMoreSupport = false;
  bool showSmall = false;

  bool get supportLocked => widget.initialSupport != null;

  @override
  void initState() {
    super.initState();
    linked = widget.goalDefault && widget.app.goal != null;
    chosen = widget.initialSupport;
    showMoreSupport =
        chosen != null && chosen != Support.solo && chosen != Support.together;
    title.addListener(() => setState(() {}));
  }

  @override
  void dispose() {
    title.dispose();
    small.dispose();
    super.dispose();
  }

  Future<void> createAndStart(Support support) async {
    final action = ActionItem(
      id: DateTime.now().microsecondsSinceEpoch.toString(),
      title: title.text.trim(),
      small: small.text.trim(),
      minutes: useTimer ? minutes : 0,
      support: support,
      goal: linked,
      kind: linked ? IntentKind.goalStep : IntentKind.focus,
      useTimer: useTimer,
    );
    widget.app.add(action);

    if (support == Support.together ||
        support == Support.report ||
        support == Support.curator) {
      await shareStartMessage(action.title, action.minutes, support);
    }
    if (!mounted) return;

    if (!useTimer) {
      Navigator.popUntil(context, (route) => route.isFirst);
      return;
    }
    await Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (_) => Session(app: widget.app, item: action)),
    );
  }

  @override
  Widget build(BuildContext context) {
    final recommended = SupportLogic.recommend(title.text);
    final support = chosen ?? recommended.$1;

    final pageTitle = switch (widget.initialSupport) {
      Support.together => 'Начать вместе',
      Support.ai => 'С цифровым помощником',
      Support.report => 'Показать результат',
      Support.curator => 'С куратором',
      _ => 'Сделать дело',
    };

    return Scaffold(
      appBar: AppBar(title: Text(pageTitle)),
      body: ListView(
        padding: const EdgeInsets.all(18),
        children: [
          Text(
            'Что вы хотите сделать?',
            style: Theme.of(context).textTheme.headlineMedium,
          ),
          if (linked && widget.app.goal != null) ...[
            const SizedBox(height: 7),
            Text(
              'Для цели: ${widget.app.goal!.title}',
              style: const TextStyle(color: Colors.black54),
            ),
          ],
          const SizedBox(height: 17),
          VoiceField(
            controller: title,
            label: 'Конкретное действие',
            hint: 'Например: подготовить первый экран приложения',
            lines: 3,
          ),
          const SizedBox(height: 13),
          SwitchListTile.adaptive(
            contentPadding: EdgeInsets.zero,
            title: const Text(
              'Использовать таймер',
              style: TextStyle(fontWeight: FontWeight.w900),
            ),
            subtitle: const Text(
              'Отключите, если дело нужно просто выполнить до результата.',
            ),
            value: useTimer,
            onChanged: (value) => setState(() => useTimer = value),
          ),
          if (useTimer) ...[
            const SizedBox(height: 8),
            const Text(
              'Сколько времени вы готовы уделить?',
              style: TextStyle(fontWeight: FontWeight.w900, fontSize: 17),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [5, 10, 15, 25, 40, 60, 90]
                  .map(
                    (value) => ChoiceChip(
                      label: Text('$value мин'),
                      selected: minutes == value,
                      onSelected: (_) => setState(() => minutes = value),
                    ),
                  )
                  .toList(),
            ),
          ] else ...[
            const SizedBox(height: 8),
            const Card(
              child: Padding(
                padding: EdgeInsets.all(15),
                child: Text(
                  'Действие останется в списке без обратного отсчёта. После выполнения вы отметите результат.',
                ),
              ),
            ),
          ],
          const SizedBox(height: 20),
          if (supportLocked) ...[
            const Text(
              'Выбранный способ',
              style: TextStyle(fontWeight: FontWeight.w900, fontSize: 18),
            ),
            const SizedBox(height: 9),
            SupportTile(type: support, selected: true, onTap: () {}),
          ] else ...[
            const Text(
              'Нужна поддержка?',
              style: TextStyle(fontWeight: FontWeight.w900, fontSize: 18),
            ),
            const SizedBox(height: 9),
            SupportTile(
              type: Support.solo,
              selected: support == Support.solo,
              onTap: () => setState(() => chosen = Support.solo),
            ),
            SupportTile(
              type: Support.together,
              selected: support == Support.together,
              onTap: () => setState(() => chosen = Support.together),
            ),
            TextButton.icon(
              onPressed: () =>
                  setState(() => showMoreSupport = !showMoreSupport),
              icon: Icon(
                showMoreSupport ? Icons.expand_less : Icons.more_horiz,
              ),
              label: Text(
                showMoreSupport
                    ? 'Скрыть другие варианты'
                    : 'Другие варианты поддержки',
              ),
            ),
            if (showMoreSupport) ...[
              SupportTile(
                type: Support.ai,
                selected: support == Support.ai,
                onTap: () => setState(() => chosen = Support.ai),
              ),
              SupportTile(
                type: Support.report,
                selected: support == Support.report,
                onTap: () => setState(() => chosen = Support.report),
              ),
              SupportTile(
                type: Support.curator,
                selected: support == Support.curator,
                onTap: () => setState(() => chosen = Support.curator),
              ),
            ],
          ],
          TextButton.icon(
            onPressed: () => setState(() => showSmall = !showSmall),
            icon: Icon(showSmall ? Icons.expand_less : Icons.compress_rounded),
            label: Text(
              showSmall
                  ? 'Скрыть сокращённый вариант'
                  : 'Добавить минимальный вариант',
            ),
          ),
          if (showSmall) ...[
            const SizedBox(height: 6),
            VoiceField(
              controller: small,
              label: 'Что можно сделать хотя бы частично?',
              hint: 'Например: только открыть проект и записать следующий шаг',
              lines: 3,
            ),
          ],
          if (!widget.goalDefault && widget.app.goal != null) ...[
            const SizedBox(height: 8),
            SwitchListTile.adaptive(
              contentPadding: EdgeInsets.zero,
              title: const Text(
                'Это действие относится к главной цели',
                style: TextStyle(fontWeight: FontWeight.w800),
              ),
              subtitle: Text(widget.app.goal!.title),
              value: linked,
              onChanged: (value) => setState(() => linked = value),
            ),
          ],
          const SizedBox(height: 18),
          FilledButton.icon(
            onPressed: title.text.trim().isEmpty
                ? null
                : () => createAndStart(support),
            icon: Icon(
              support == Support.together
                  ? Icons.people_alt_rounded
                  : useTimer
                  ? Icons.play_arrow_rounded
                  : Icons.save_outlined,
            ),
            label: Text(
              support == Support.together
                  ? useTimer
                        ? 'Позвать человека и начать'
                        : 'Позвать человека и сохранить'
                  : useTimer
                  ? 'Начать'
                  : 'Сохранить действие',
            ),
          ),
        ],
      ),
    );
  }
}''',
)

replace_between(
    'Future<void> shareStartMessage(',
    'Future<void> shareResultMessage(',
    r'''Future<void> shareStartMessage(
  String title,
  int minutes,
  Support support,
) async {
  final duration = minutes > 0 ? ' на $minutes минут' : '';
  final text = switch (support) {
    Support.together =>
      'Начнём одновременно? Я начинаю дело «$title»$duration. Каждый может заниматься своим делом.',
    Support.report =>
      'Я начинаю дело «$title»$duration. Когда закончу, отправлю короткий результат.',
    Support.curator =>
      'Я хочу начать дело «$title»$duration. Напомни мне об этом и спроси потом, что получилось.',
    _ => 'Я начинаю дело «$title»$duration.',
  };

  await SharePlus.instance.share(
    ShareParams(text: text, subject: 'Вместе к цели'),
  );
}''',
)

helpers = r'''String clockTime(DateTime value) =>
    '${value.hour.toString().padLeft(2, '0')}:${value.minute.toString().padLeft(2, '0')}';

String shortDate(DateTime value) {
  final now = DateTime.now();
  final today = DateTime(now.year, now.month, now.day);
  final day = DateTime(value.year, value.month, value.day);
  if (day == today) return 'Сегодня';
  if (day == today.add(const Duration(days: 1))) return 'Завтра';
  return '${value.day.toString().padLeft(2, '0')}.${value.month.toString().padLeft(2, '0')}.${value.year}';
}

String actionMeta(ActionItem item) => switch (item.kind) {
  IntentKind.reminder => item.scheduledAt == null
      ? 'Напоминание'
      : '${shortDate(item.scheduledAt!)} в ${clockTime(item.scheduledAt!)}',
  IntentKind.routine =>
    'Каждый день${item.scheduledAt == null ? '' : ' в ${clockTime(item.scheduledAt!)}'}${item.useTimer ? ' · ${item.minutes} минут' : ' · без таймера'}',
  IntentKind.focus || IntentKind.goalStep =>
    '${item.useTimer ? '${item.minutes} минут' : 'Без таймера'} · ${supportName(item.support)}',
};

IconData intentIcon(IntentKind kind) => switch (kind) {
  IntentKind.reminder => Icons.alarm_rounded,
  IntentKind.focus => Icons.play_circle_outline_rounded,
  IntentKind.routine => Icons.repeat_rounded,
  IntentKind.goalStep => Icons.flag_outlined,
};

Color intentColor(IntentKind kind) => switch (kind) {
  IntentKind.reminder => const Color(0xFFF2E1D0),
  IntentKind.focus => const Color(0xFFD8ECE5),
  IntentKind.routine => const Color(0xFFD8E4F0),
  IntentKind.goalStep => mint,
};

'''
helper_at = text.index('String supportName(Support s)')
text = text[:helper_at] + helpers + text[helper_at:]

# Avoid a misleading 0-minute value in history.
text = text.replace(
    "'${supportName(e.support)} · ${e.minutes} минут · ${e.date.day}.${e.date.month}.${e.date.year}'",
    "'${supportName(e.support)}${e.minutes > 0 ? ' · ${e.minutes} минут' : ''} · ${e.date.day}.${e.date.month}.${e.date.year}'",
)

pubspec = pubspec.replace('version: 0.3.4+8', 'version: 0.4.0+9')
pubspec = pubspec.replace(
    '  share_plus: ^13.2.1\n',
    '''  share_plus: ^13.2.1
  flutter_local_notifications: ^22.1.0
  flutter_timezone: ^5.1.0
  timezone: ^0.11.1
''',
)

main_path.write_text(text, encoding='utf-8')
pubspec_path.write_text(pubspec, encoding='utf-8')
print('Applied v0.4.0 intent architecture')
