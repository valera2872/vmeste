from pathlib import Path

path = Path('test/widget_test.dart')
text = path.read_text(encoding='utf-8')

text = text.replace(
    "expect(find.text('Что мешает начать?'), findsOneWidget);",
    "expect(find.text('Что делает начало трудным?'), findsOneWidget);",
    1,
)
text = text.replace(
    "await tester.tap(find.text('Действие слишком большое'));",
    "await tester.tap(find.byKey(const ValueKey('start-barrier-tooBig')));",
    1,
)
text = text.replace(
    "find.byKey(const ValueKey('start-adjustment-card'))",
    "find.byKey(const ValueKey('feasible-start-plan'))",
    1,
)
text = text.replace(
    "expect(find.text('Что поможет сейчас'), findsOneWidget);",
    "expect(find.text('Уменьшим действие до посильного объёма'), findsOneWidget);",
    1,
)

marker = """    await tester.pumpAndSettle();

    await tester.tap(find.byKey(const ValueKey('start-difficulty-button')));
    await tester.pumpAndSettle();
    expect(find.byKey(const ValueKey('start-barrier-sheet')), findsOneWidget);"""
replacement = """    await tester.pumpAndSettle();
    await tester.drag(
      find.byType(ListView).first,
      const Offset(0, -380),
    );
    await tester.pumpAndSettle();

    await tester.tap(find.byKey(const ValueKey('start-difficulty-button')));
    await tester.pumpAndSettle();
    expect(find.byKey(const ValueKey('start-barrier-sheet')), findsOneWidget);"""
if marker not in text:
    raise SystemExit('v0.13 narrow Session test marker not found')
text = text.replace(marker, replacement, 1)

level_marker = """    expect(find.text('ТАЙМЕР ЕЩЁ НЕ ЗАПУЩЕН'), findsOneWidget);

    await tester.tap(find.byKey(const ValueKey('start-level-contact')));
    await tester.pump();"""
level_replacement = """    expect(find.text('ТАЙМЕР ЕЩЁ НЕ ЗАПУЩЕН'), findsOneWidget);

    await tester.ensureVisible(
      find.byKey(const ValueKey('start-level-contact')),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const ValueKey('start-level-contact')));
    await tester.pump();"""
if level_marker not in text:
    raise SystemExit('v0.13 start level visibility marker not found')
text = text.replace(level_marker, level_replacement, 1)

start_marker = """    expect(app.startAttempts.first.level, StartLevel.contact);
    expect(app.startAttempts.first.startedAt, isNull);

    await tester.tap(find.byKey(const ValueKey('start-confirm-button')));
    await tester.pump();"""
start_replacement = """    expect(app.startAttempts.first.level, StartLevel.contact);
    expect(app.startAttempts.first.startedAt, isNull);

    await tester.ensureVisible(
      find.byKey(const ValueKey('start-confirm-button')),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const ValueKey('start-confirm-button')));
    await tester.pump();"""
if start_marker not in text:
    raise SystemExit('v0.13 explicit start visibility marker not found')
text = text.replace(start_marker, start_replacement, 1)

path.write_text(text, encoding='utf-8')
print('Adapted legacy and narrow tests to v0.13.0 feasible start')
