from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')


def replace_class(source: str, name: str, next_name: str, replacement: str) -> str:
    start = source.index(f'class {name}')
    end = source.index(f'class {next_name}', start)
    return source[:start] + replacement.rstrip() + '\n\n' + source[end:]


if 'enum RoutineSchedule' not in text:
    text = text.replace(
        'enum ResultState { done, part, moved, missed }',
        '''enum ResultState { done, part, moved, missed }

enum RoutineSchedule { daily, weekdays, weekends, selectedDays, timesPerWeek }

enum RoutineResult { full, minimum, partial, skipped }''',
        1,
    )

GOAL = r'''class Goal {
  Goal(
    this.title,
    this.result,
    this.minutes,
    this.areas, {
    String? id,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) : id = id ?? DateTime.now().microsecondsSinceEpoch.toString(),
       createdAt = createdAt ?? DateTime.now(),
       updatedAt = updatedAt ?? DateTime.now();

  final String id;
  final String title, result;
  final int minutes;
  final List<String> areas;
  final DateTime createdAt;
  final DateTime updatedAt;

  Map<String, dynamic> toJson() => {
    'id': id,
    'title': title,
    'result': result,
    'minutes': minutes,
    'areas': areas,
    'createdAt': createdAt.toIso8601String(),
    'updatedAt': updatedAt.toIso8601String(),
  };

  factory Goal.fromJson(Map<String, dynamic> j) {
    final now = DateTime.now();
    final title = (j['title'] ?? '').toString();
    final legacyId = 'goal_${title.hashCode.toUnsigned(32)}';
    return Goal(
      title,
      (j['result'] ?? '').toString(),
      j['minutes'] ?? 0,
      List<String>.from(j['areas'] ?? const []),
      id: (j['id'] ?? legacyId).toString(),
      createdAt: DateTime.tryParse((j['createdAt'] ?? '').toString()) ?? now,
      updatedAt: DateTime.tryParse((j['updatedAt'] ?? '').toString()) ?? now,
    );
  }
}'''

ACTION = r'''class ActionItem {
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
    this.routineSchedule = RoutineSchedule.daily,
    List<int>? weekdays,
    this.weeklyTarget = 7,
    this.minimumMinutes = 0,
    this.routinePaused = false,
    this.pausedUntil,
    this.remindersEnabled = true,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) : weekdays = weekdays ?? <int>[],
       createdAt = createdAt ?? DateTime.now(),
       updatedAt = updatedAt ?? DateTime.now();

  final String id;
  String title, small;
  int minutes;
  Support support;
  bool goal;
  IntentKind kind;
  DateTime? scheduledAt;
  bool repeatDaily;
  bool useTimer;
  ResultState? state;
  RoutineSchedule routineSchedule;
  List<int> weekdays;
  int weeklyTarget;
  int minimumMinutes;
  bool routinePaused;
  DateTime? pausedUntil;
  bool remindersEnabled;
  final DateTime createdAt;
  DateTime updatedAt;

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
    'routineSchedule': routineSchedule.name,
    'weekdays': weekdays,
    'weeklyTarget': weeklyTarget,
    'minimumMinutes': minimumMinutes,
    'routinePaused': routinePaused,
    'pausedUntil': pausedUntil?.toIso8601String(),
    'remindersEnabled': remindersEnabled,
    'createdAt': createdAt.toIso8601String(),
    'updatedAt': updatedAt.toIso8601String(),
  };

  factory ActionItem.fromJson(Map<String, dynamic> j) {
    final now = DateTime.now();
    final title = (j['title'] ?? '').toString();
    final legacyId = 'action_${title.hashCode.toUnsigned(32)}_${(j['scheduledAt'] ?? '').hashCode.toUnsigned(32)}';
    return ActionItem(
      id: ((j['id'] ?? '').toString().isEmpty ? legacyId : j['id'].toString()),
      title: title,
      small: (j['small'] ?? '').toString(),
      minutes: j['minutes'] ?? 10,
      support: Support.values.firstWhere(
        (e) => e.name == j['support'],
        orElse: () => Support.ai,
      ),
      goal: j['goal'] ?? false,
      kind: IntentKind.values.firstWhere(
        (e) => e.name == j['kind'],
        orElse: () =>
            (j['goal'] ?? false) ? IntentKind.goalStep : IntentKind.focus,
      ),
      scheduledAt: DateTime.tryParse((j['scheduledAt'] ?? '').toString()),
      repeatDaily: j['repeatDaily'] ?? false,
      useTimer: j['useTimer'] ?? true,
      state: j['state'] == null
          ? null
          : ResultState.values.firstWhere(
              (e) => e.name == j['state'],
              orElse: () => ResultState.missed,
            ),
      routineSchedule: RoutineSchedule.values.firstWhere(
        (e) => e.name == j['routineSchedule'],
        orElse: () => RoutineSchedule.daily,
      ),
      weekdays: List<int>.from(j['weekdays'] ?? const []),
      weeklyTarget: j['weeklyTarget'] ?? ((j['repeatDaily'] ?? false) ? 7 : 3),
      minimumMinutes: j['minimumMinutes'] ?? 0,
      routinePaused: j['routinePaused'] ?? false,
      pausedUntil: DateTime.tryParse((j['pausedUntil'] ?? '').toString()),
      remindersEnabled: j['remindersEnabled'] ?? true,
      createdAt: DateTime.tryParse((j['createdAt'] ?? '').toString()) ?? now,
      updatedAt: DateTime.tryParse((j['updatedAt'] ?? '').toString()) ?? now,
    );
  }
}'''

HISTORY = r'''class HistoryItem {
  HistoryItem(
    this.title,
    this.minutes,
    this.support,
    this.state,
    this.date,
    this.goal, {
    String? id,
    this.actionId = '',
    this.routineResult,
  }) : id = id ?? DateTime.now().microsecondsSinceEpoch.toString();

  final String id;
  final String title;
  final int minutes;
  final Support support;
  final ResultState state;
  final DateTime date;
  final bool goal;
  final String actionId;
  final RoutineResult? routineResult;

  Map<String, dynamic> toJson() => {
    'id': id,
    'title': title,
    'minutes': minutes,
    'support': support.name,
    'state': state.name,
    'date': date.toIso8601String(),
    'goal': goal,
    'actionId': actionId,
    'routineResult': routineResult?.name,
  };

  factory HistoryItem.fromJson(Map<String, dynamic> j) => HistoryItem(
    (j['title'] ?? '').toString(),
    j['minutes'] ?? 0,
    Support.values.firstWhere(
      (e) => e.name == j['support'],
      orElse: () => Support.solo,
    ),
    ResultState.values.firstWhere(
      (e) => e.name == j['state'],
      orElse: () => ResultState.done,
    ),
    DateTime.tryParse((j['date'] ?? '').toString()) ?? DateTime.now(),
    j['goal'] ?? false,
    id: (j['id'] ?? DateTime.now().microsecondsSinceEpoch.toString()).toString(),
    actionId: (j['actionId'] ?? '').toString(),
    routineResult: j['routineResult'] == null
        ? null
        : RoutineResult.values.firstWhere(
            (e) => e.name == j['routineResult'],
            orElse: () => RoutineResult.partial,
          ),
  );
}'''

NOTIFICATIONS = r'''class NotificationService {
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

  Future<bool> _permissionAllowed() async {
    final android = plugin
        .resolvePlatformSpecificImplementation<
          AndroidFlutterLocalNotificationsPlugin
        >();
    final allowed = await android?.requestNotificationsPermission();
    return allowed != false;
  }

  Future<void> _scheduleOne({
    required int id,
    required String title,
    required DateTime when,
    required String payload,
  }) async {
    await plugin.zonedSchedule(
      id: id,
      title: 'Вместе к цели',
      body: title,
      scheduledDate: tz.TZDateTime.from(when, tz.local),
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
      payload: payload,
    );
  }

  Future<bool> schedule(ActionItem item) async {
    if (item.kind == IntentKind.routine) return scheduleRoutine(item);
    if (!ready || item.scheduledAt == null) return false;
    try {
      if (!await _permissionAllowed()) return false;
      final when = item.scheduledAt!;
      if (!when.isAfter(DateTime.now())) return false;
      await cancel(item.id);
      await _scheduleOne(
        id: _id(item.id),
        title: item.title,
        when: when,
        payload: item.id,
      );
      return true;
    } catch (_) {
      return false;
    }
  }

  Future<bool> scheduleRoutine(ActionItem item) async {
    if (!ready || !item.remindersEnabled || item.routinePaused) return false;
    try {
      if (!await _permissionAllowed()) return false;
      await cancel(item.id);
      final occurrences = routineOccurrences(item, DateTime.now(), 42);
      for (final when in occurrences) {
        final key = '${item.id}:${when.toIso8601String()}';
        await _scheduleOne(
          id: _id(key),
          title: item.title,
          when: when,
          payload: item.id,
        );
      }
      return occurrences.isNotEmpty;
    } catch (_) {
      return false;
    }
  }

  Future<void> cancel(String id) async {
    if (!ready) return;
    try {
      await plugin.cancel(id: _id(id));
      final pending = await plugin.pendingNotificationRequests();
      for (final request in pending) {
        if (request.payload == id) await plugin.cancel(id: request.id);
      }
    } catch (_) {}
  }
}'''

APP_STATE = r'''class AppState extends ChangeNotifier {
  bool onboarded = false;
  String name = '', curator = '';
  Age age = Age.adult;
  Goal? goal;
  final List<ActionItem> actions = [];
  final List<HistoryItem> history = [];
  static const key = 'vmeste02';
  static const schemaVersion = 2;

  Future<void> load() async {
    final p = await SharedPreferences.getInstance();
    final raw = p.getString(key);
    if (raw == null) return;
    try {
      final j = jsonDecode(raw);
      onboarded = j['onboarded'] ?? false;
      name = j['name'] ?? '';
      curator = j['curator'] ?? '';
      age = Age.values.firstWhere(
        (e) => e.name == j['age'],
        orElse: () => Age.adult,
      );
      if (j['goal'] != null) {
        goal = Goal.fromJson(Map<String, dynamic>.from(j['goal']));
      }
      actions.addAll(
        (j['actions'] ?? []).map<ActionItem>(
          (e) => ActionItem.fromJson(Map<String, dynamic>.from(e)),
        ),
      );
      history.addAll(
        (j['history'] ?? []).map<HistoryItem>(
          (e) => HistoryItem.fromJson(Map<String, dynamic>.from(e)),
        ),
      );
      _restorePausedRoutines();
    } catch (_) {}
  }

  Map<String, dynamic> _payload() => {
    'schemaVersion': schemaVersion,
    'onboarded': onboarded,
    'name': name,
    'curator': curator,
    'age': age.name,
    'goal': goal?.toJson(),
    'actions': actions.map((e) => e.toJson()).toList(),
    'history': history.map((e) => e.toJson()).toList(),
  };

  String exportData() => jsonEncode(_payload());

  Future<void> save() async {
    final p = await SharedPreferences.getInstance();
    await p.setString(key, jsonEncode(_payload()));
  }

  void _restorePausedRoutines() {
    final now = DateTime.now();
    for (final item in actions.where((e) => e.kind == IntentKind.routine)) {
      if (item.routinePaused &&
          item.pausedUntil != null &&
          !item.pausedUntil!.isAfter(now)) {
        item.routinePaused = false;
        item.pausedUntil = null;
        item.updatedAt = now;
      }
    }
  }

  void finish(Age a, String n) {
    age = a;
    name = n.trim();
    onboarded = true;
    notifyListeners();
    save();
  }

  void setGoal(Goal g) {
    goal = g;
    notifyListeners();
    save();
  }

  void add(ActionItem a) {
    actions.insert(0, a);
    notifyListeners();
    save();
  }

  void updateAction(ActionItem action) {
    action.updatedAt = DateTime.now();
    notifyListeners();
    save();
  }

  void deleteAction(ActionItem action) {
    actions.remove(action);
    unawaited(NotificationService.instance.cancel(action.id));
    notifyListeners();
    save();
  }

  Future<void> reschedule(ActionItem action, DateTime when) async {
    action.scheduledAt = when;
    action.state = null;
    action.updatedAt = DateTime.now();
    await NotificationService.instance.cancel(action.id);
    await NotificationService.instance.schedule(action);
    notifyListeners();
    save();
  }

  void setSupport(ActionItem action, Support support) {
    action.support = support;
    action.updatedAt = DateTime.now();
    notifyListeners();
    save();
  }

  void complete(ActionItem a, ResultState s) {
    if (a.kind == IntentKind.routine) {
      final routineResult = switch (s) {
        ResultState.done => RoutineResult.full,
        ResultState.part => RoutineResult.partial,
        ResultState.missed => RoutineResult.skipped,
        ResultState.moved => RoutineResult.skipped,
      };
      completeRoutine(a, routineResult);
      return;
    }

    history.insert(
      0,
      HistoryItem(
        a.title,
        a.minutes,
        a.support,
        s,
        DateTime.now(),
        a.goal,
        actionId: a.id,
      ),
    );
    a.state = s;
    a.updatedAt = DateTime.now();
    unawaited(NotificationService.instance.cancel(a.id));
    notifyListeners();
    save();
  }

  void completeRoutine(ActionItem item, RoutineResult result) {
    final mappedState = switch (result) {
      RoutineResult.full => ResultState.done,
      RoutineResult.minimum => ResultState.part,
      RoutineResult.partial => ResultState.part,
      RoutineResult.skipped => ResultState.missed,
    };
    final recordedMinutes = result == RoutineResult.minimum
        ? item.minimumMinutes
        : item.minutes;
    history.insert(
      0,
      HistoryItem(
        item.title,
        recordedMinutes,
        item.support,
        mappedState,
        DateTime.now(),
        false,
        actionId: item.id,
        routineResult: result,
      ),
    );
    item.updatedAt = DateTime.now();
    item.scheduledAt = nextRoutineDate(item, DateTime.now());
    unawaited(NotificationService.instance.scheduleRoutine(item));
    notifyListeners();
    save();
  }

  Future<void> pauseRoutine(ActionItem item, DateTime? until) async {
    item.routinePaused = true;
    item.pausedUntil = until;
    item.updatedAt = DateTime.now();
    await NotificationService.instance.cancel(item.id);
    notifyListeners();
    save();
  }

  Future<void> resumeRoutine(ActionItem item) async {
    item.routinePaused = false;
    item.pausedUntil = null;
    item.scheduledAt = nextRoutineDate(item, DateTime.now());
    item.updatedAt = DateTime.now();
    await NotificationService.instance.scheduleRoutine(item);
    notifyListeners();
    save();
  }

  void setCurator(String value) {
    curator = value.trim();
    notifyListeners();
    save();
  }

  int routineFullThisWeek(ActionItem item) => routineHistoryThisWeek(item)
      .where((e) => e.routineResult == RoutineResult.full)
      .length;

  int routineMinimumThisWeek(ActionItem item) => routineHistoryThisWeek(item)
      .where((e) => e.routineResult == RoutineResult.minimum)
      .length;

  List<HistoryItem> routineHistoryThisWeek(ActionItem item) {
    final now = DateTime.now();
    final start = DateTime(now.year, now.month, now.day)
        .subtract(Duration(days: now.weekday - 1));
    return history
        .where((e) => e.actionId == item.id && !e.date.isBefore(start))
        .toList();
  }

  int get goalDone => history
      .where(
        (e) =>
            e.goal &&
            (e.state == ResultState.done || e.state == ResultState.part),
      )
      .length;

  int get goalActive => actions.where((e) => e.goal && e.state == null).length;

  String get hello => name.isEmpty ? 'С чего начнём?' : '$name, с чего начнём?';
}'''

text = replace_class(text, 'Goal', 'ActionItem', GOAL)
text = replace_class(text, 'ActionItem', 'HistoryItem', ACTION)
text = replace_class(text, 'HistoryItem', 'NotificationService', HISTORY)
text = replace_class(text, 'NotificationService', 'AppState', NOTIFICATIONS)
text = replace_class(text, 'AppState', 'VmesteApp', APP_STATE)

HELPERS = r'''List<int> routineDays(ActionItem item) => switch (item.routineSchedule) {
  RoutineSchedule.daily => const [1, 2, 3, 4, 5, 6, 7],
  RoutineSchedule.weekdays => const [1, 2, 3, 4, 5],
  RoutineSchedule.weekends => const [6, 7],
  RoutineSchedule.selectedDays => item.weekdays.isEmpty
      ? const [1, 3, 5]
      : item.weekdays,
  RoutineSchedule.timesPerWeek => const [1, 3, 5, 7, 2, 4, 6]
      .take(item.weeklyTarget.clamp(1, 7))
      .toList(),
};

int routineWeeklyGoal(ActionItem item) => switch (item.routineSchedule) {
  RoutineSchedule.daily => 7,
  RoutineSchedule.weekdays => 5,
  RoutineSchedule.weekends => 2,
  RoutineSchedule.selectedDays => item.weekdays.isEmpty ? 3 : item.weekdays.length,
  RoutineSchedule.timesPerWeek => item.weeklyTarget.clamp(1, 7),
};

bool routineDueToday(ActionItem item) {
  if (item.routinePaused) return false;
  return routineDays(item).contains(DateTime.now().weekday);
}

DateTime nextRoutineDate(ActionItem item, DateTime from) {
  final base = item.scheduledAt ?? from.add(const Duration(hours: 1));
  final days = routineDays(item).toSet();
  for (var offset = 0; offset < 21; offset++) {
    final day = from.add(Duration(days: offset));
    final candidate = DateTime(
      day.year,
      day.month,
      day.day,
      base.hour,
      base.minute,
    );
    if (days.contains(candidate.weekday) && candidate.isAfter(from)) {
      return candidate;
    }
  }
  return from.add(const Duration(days: 1));
}

List<DateTime> routineOccurrences(ActionItem item, DateTime from, int horizonDays) {
  final result = <DateTime>[];
  final base = item.scheduledAt ?? from.add(const Duration(hours: 1));
  final days = routineDays(item).toSet();
  for (var offset = 0; offset <= horizonDays; offset++) {
    final day = from.add(Duration(days: offset));
    final candidate = DateTime(
      day.year,
      day.month,
      day.day,
      base.hour,
      base.minute,
    );
    if (days.contains(candidate.weekday) && candidate.isAfter(from)) {
      result.add(candidate);
    }
  }
  return result;
}

String routineScheduleLabel(ActionItem item) => switch (item.routineSchedule) {
  RoutineSchedule.daily => 'Каждый день',
  RoutineSchedule.weekdays => 'По будням',
  RoutineSchedule.weekends => 'По выходным',
  RoutineSchedule.selectedDays => item.weekdays.isEmpty
      ? 'Выбранные дни'
      : item.weekdays.map(shortWeekday).join(', '),
  RoutineSchedule.timesPerWeek => '${item.weeklyTarget} ${timesWord(item.weeklyTarget)} в неделю',
};

String shortWeekday(int value) => const {
  1: 'пн',
  2: 'вт',
  3: 'ср',
  4: 'чт',
  5: 'пт',
  6: 'сб',
  7: 'вс',
}[value] ?? '';

String timesWord(int count) {
  if (count == 1) return 'раз';
  if (count >= 2 && count <= 4) return 'раза';
  return 'раз';
}

String routineResultName(RoutineResult value) => switch (value) {
  RoutineResult.full => 'Выполнено полностью',
  RoutineResult.minimum => 'Выполнен минимум',
  RoutineResult.partial => 'Сделана часть',
  RoutineResult.skipped => 'Пропущено',
};
'''

marker = 'DateTime roundedHour(DateTime value)'
if 'List<int> routineDays(ActionItem item)' not in text:
    text = text.replace(marker, HELPERS + '\n' + marker, 1)

old_goal_save = '''        areas.text
            .split(RegExp(r'[,;\\n]'))
            .map((item) => item.trim())
            .where((item) => item.isNotEmpty)
            .toList(),
      ),'''
new_goal_save = '''        areas.text
            .split(RegExp(r'[,;\\n]'))
            .map((item) => item.trim())
            .where((item) => item.isNotEmpty)
            .toList(),
        id: widget.existing?.id,
        createdAt: widget.existing?.createdAt,
        updatedAt: DateTime.now(),
      ),'''
if old_goal_save in text:
    text = text.replace(old_goal_save, new_goal_save, 1)

pubspec = Path('pubspec.yaml')
pub = pubspec.read_text(encoding='utf-8')
pub = pub.replace('version: 0.5.1+12', 'version: 0.6.0+13')
pubspec.write_text(pub, encoding='utf-8')
path.write_text(text, encoding='utf-8')
print('Applied v0.6 data model and routine scheduling')
