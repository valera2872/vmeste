from pathlib import Path

path = Path("test/widget_test.dart")
text = path.read_text(encoding="utf-8")

if "voice field keeps long hints readable" not in text:
    insert = r'''
  testWidgets('voice field keeps long hints readable', (tester) async {
    final controller = TextEditingController();
    addTearDown(controller.dispose);

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: VoiceField(
            controller: controller,
            label: 'Минимальный вариант',
            hint: 'Что можно сделать хотя бы частично, если сегодня трудно начать?',
            lines: 3,
          ),
        ),
      ),
    );

    final field = tester.widget<TextField>(find.byType(TextField));
    expect(field.decoration?.suffixIcon, isNull);
    expect(field.decoration?.hintMaxLines, 3);
    expect(find.text('Надиктовать'), findsOneWidget);
  });
'''
    at = text.rfind('\n}')
    if at == -1:
        raise SystemExit("Test file closing brace not found")
    text = text[:at] + insert + text[at:]

path.write_text(text, encoding="utf-8")
print("Applied v0.5.1 voice field test")
