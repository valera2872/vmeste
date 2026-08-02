from pathlib import Path

main_path = Path('lib/main.dart')
text = main_path.read_text(encoding='utf-8')

old = """    final text =
        '${greeting}день ${widget.challenge.dayNumber()} из ${widget.challenge.durationDays}: '
        '${challengeResultTitle(entry.result).toLowerCase()} — ${entry.amount} ${widget.challenge.unit}. '
        'Текущая серия: ${widget.challenge.currentStreak}.';"""
new = r"""    final text =
        '$greeting\u0434ень ${widget.challenge.dayNumber()} из ${widget.challenge.durationDays}: '
        '${challengeResultTitle(entry.result).toLowerCase()} — ${entry.amount} ${widget.challenge.unit}. '
        'Текущая серия: ${widget.challenge.currentStreak}.';"""

if old in text:
    text = text.replace(old, new, 1)
elif "'$greeting\\u0434ень ${widget.challenge.dayNumber()}" not in text:
    raise SystemExit('Challenge report interpolation anchor not found')
main_path.write_text(text, encoding='utf-8')

# The new challenge block makes Today taller. Keep the historical quick-capture
# test meaningful by scrolling its button into view before the physical tap.
test_path = Path('test/widget_test.dart')
tests = test_path.read_text(encoding='utf-8')
old_tap = """    await tester.tap(find.byKey(const ValueKey('quick-capture-add')));
    await tester.pumpAndSettle();"""
new_tap = """    await tester.ensureVisible(
      find.byKey(const ValueKey('quick-capture-add')),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const ValueKey('quick-capture-add')));
    await tester.pumpAndSettle();"""
if old_tap in tests:
    tests = tests.replace(old_tap, new_tap, 1)
elif "tester.ensureVisible(\n      find.byKey(const ValueKey('quick-capture-add'))" not in tests:
    raise SystemExit('Existing quick-capture test tap anchor not found')
test_path.write_text(tests, encoding='utf-8')

print('Fixed v0.12.0 strict lint and adapted existing Today test')
