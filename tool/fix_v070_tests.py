from pathlib import Path

path = Path('test/widget_test.dart')
text = path.read_text(encoding='utf-8')
old = """    expect(find.byKey(const ValueKey('start-difficulty-sheet')), findsOneWidget);
    expect(find.text('Что мешает начать?'), findsOneWidget);
    expect(find.text('Действие слишком большое'), findsOneWidget);
    expect(find.text('Нужен человек рядом'), findsOneWidget);
    expect(tester.takeException(), isNull);"""
new = """    expect(find.byKey(const ValueKey('start-difficulty-sheet')), findsOneWidget);
    expect(find.text('Что мешает начать?'), findsOneWidget);
    expect(find.text('Действие слишком большое'), findsOneWidget);
    final sheetScroll = find.descendant(
      of: find.byKey(const ValueKey('start-difficulty-sheet')),
      matching: find.byType(Scrollable),
    );
    await tester.scrollUntilVisible(
      find.text('Нужен человек рядом'),
      220,
      scrollable: sheetScroll,
    );
    expect(find.text('Нужен человек рядом'), findsOneWidget);
    expect(tester.takeException(), isNull);"""
if old not in text:
    raise SystemExit('v0.7 test anchor not found')
text = text.replace(old, new, 1)
path.write_text(text, encoding='utf-8')
print('Fixed v0.7 start help scroll test')
