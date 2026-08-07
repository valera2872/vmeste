from pathlib import Path

path = Path('test/widget_test.dart')
text = path.read_text(encoding='utf-8')
text = text.replace(
    "expect(find.text('Раз в неделю'), findsOneWidget);",
    "expect(find.text('Несколько раз'), findsOneWidget);",
)
path.write_text(text, encoding='utf-8')
print('Aligned final v0.6 test labels')
