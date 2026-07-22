from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

# The routine keeps its own duration. A broad replacement in the first rewrite
# must not point it at ActionEditor's custom-duration variable.
text = text.replace(
    '''      minutes: useTimer ? selectedMinutes : 0,
      support: Support.solo,
      goal: false,
      kind: IntentKind.routine,''',
    '''      minutes: useTimer ? minutes : 0,
      support: Support.solo,
      goal: false,
      kind: IntentKind.routine,''',
    1,
)

# Custom duration belongs only to ActionEditor.
action_marker = '''  Future<void> createAndStart(Support support) async {
    final selectedMinutes = customTime'''
if action_marker in text:
    start = text.index(action_marker)
    old = '      minutes: useTimer ? minutes : 0,'
    pos = text.find(old, start)
    if pos != -1:
        text = text[:pos] + '      minutes: useTimer ? selectedMinutes : 0,' + text[pos + len(old):]

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

if 'String clockTime(DateTime value)' not in text:
    marker = 'String supportName(Support s)'
    if marker not in text:
        raise SystemExit('supportName marker not found')
    at = text.index(marker)
    text = text[:at] + helpers + text[at:]

path.write_text(text, encoding='utf-8')
print('Applied v0.4.1 context fixes')
