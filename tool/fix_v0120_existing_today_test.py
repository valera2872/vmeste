from pathlib import Path

path = Path('test/widget_test.dart')
text = path.read_text(encoding='utf-8')

old = """    await tester.tap(find.byKey(const ValueKey('quick-capture-add')));
    await tester.pumpAndSettle();"""
new = """    await tester.ensureVisible(
      find.byKey(const ValueKey('quick-capture-add')),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const ValueKey('quick-capture-add')));
    await tester.pumpAndSettle();"""

if old not in text:
    if "tester.ensureVisible(\n      find.byKey(const ValueKey('quick-capture-add'))" in text:
        print('Existing Today test already adapted for v0.12.0')
        raise SystemExit(0)
    raise SystemExit('Existing quick-capture test tap anchor not found')

text = text.replace(old, new, 1)
path.write_text(text, encoding='utf-8')
print('Adapted existing Today quick-capture test for challenge block')
