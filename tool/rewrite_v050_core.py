from pathlib import Path

main_path = Path('lib/main.dart')
pubspec_path = Path('pubspec.yaml')
text = main_path.read_text(encoding='utf-8')
pubspec = pubspec_path.read_text(encoding='utf-8')

if 'version: 0.5.0+11' in pubspec and 'Future<void> reschedule(ActionItem action' in text:
    print('v0.5.0 core already applied')
    raise SystemExit(0)


def replace(old: str, new: str) -> None:
    global text
    if old not in text:
        raise SystemExit(f'Expected fragment not found:\n{old[:500]}')
    text = text.replace(old, new, 1)


replace(
    '''  final String id, title, small;
  final int minutes;
  Support support;
  final bool goal;
  final IntentKind kind;
  DateTime? scheduledAt;
  final bool repeatDaily;
  final bool useTimer;
  ResultState? state;''',
    '''  final String id;
  String title, small;
  int minutes;
  Support support;
  bool goal;
  IntentKind kind;
  DateTime? scheduledAt;
  final bool repeatDaily;
  bool useTimer;
  ResultState? state;''',
)

replace(
    '''  void add(ActionItem a) {
    actions.insert(0, a);
    notifyListeners();
    save();
  }

  void setSupport(ActionItem action, Support support) {
    action.support = support;
    notifyListeners();
    save();
  }

  void complete(ActionItem a, ResultState s) {''',
    '''  void add(ActionItem a) {
    actions.insert(0, a);
    notifyListeners();
    save();
  }

  void updateAction(ActionItem action) {
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
    await NotificationService.instance.cancel(action.id);
    await NotificationService.instance.schedule(action);
    notifyListeners();
    save();
  }

  void setSupport(ActionItem action, Support support) {
    action.support = support;
    notifyListeners();
    save();
  }

  void complete(ActionItem a, ResultState s) {''',
)

replace(
    '''  int get goalDone => history
      .where(
        (e) =>
            e.goal &&
            (e.state == ResultState.done || e.state == ResultState.part),
      )
      .length;
  String get hello => name.isEmpty ? 'С чего начнём?' : '$name, с чего начнём?';''',
    '''  int get goalDone => history
      .where(
        (e) =>
            e.goal &&
            (e.state == ResultState.done || e.state == ResultState.part),
      )
      .length;

  int get goalActive =>
      actions.where((e) => e.goal && e.state == null).length;

  String get hello => name.isEmpty ? 'С чего начнём?' : '$name, с чего начнём?';''',
)

helpers = r'''DateTime roundedHour(DateTime value) =>
    DateTime(value.year, value.month, value.day, value.hour, 0);

bool isLater(ActionItem item) {
  if (item.scheduledAt == null) return false;
  final now = DateTime.now();
  final today = DateTime(now.year, now.month, now.day);
  final day = DateTime(
    item.scheduledAt!.year,
    item.scheduledAt!.month,
    item.scheduledAt!.day,
  );
  return day.isAfter(today);
}

String durationLabel(int minutes) {
  if (minutes == 60) return '1 ч';
  if (minutes == 90) return '1 ч 30 мин';
  if (minutes == 120) return '2 ч';
  if (minutes > 120 && minutes % 60 == 0) return '${minutes ~/ 60} ч';
  return '$minutes мин';
}

String longToday() {
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
  final now = DateTime.now();
  return '${weekdays[now.weekday - 1]}, ${now.day} ${months[now.month - 1]}';
}

String taskWord(int count) {
  final n = count.abs() % 100;
  final n1 = n % 10;
  if (n > 10 && n < 20) return 'дел';
  if (n1 == 1) return 'дело';
  if (n1 >= 2 && n1 <= 4) return 'дела';
  return 'дел';
}

'''
insert_at = text.index('String clockTime(DateTime value)')
text = text[:insert_at] + helpers + text[insert_at:]

pubspec = pubspec.replace('version: 0.4.1+10', 'version: 0.5.0+11')
main_path.write_text(text, encoding='utf-8')
pubspec_path.write_text(pubspec, encoding='utf-8')
print('Applied v0.5.0 core')
