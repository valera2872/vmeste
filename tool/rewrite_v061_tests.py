from pathlib import Path

path = Path('test/widget_test.dart')
text = path.read_text(encoding='utf-8')


def replace_test(source: str, start_name: str, next_name: str, replacement: str) -> str:
    start = source.index(f"  testWidgets('{start_name}")
    end = source.index(f"  testWidgets('{next_name}", start)
    return source[:start] + replacement.rstrip() + '\n\n' + source[end:]


ONBOARDING_TEST = r'''  testWidgets('onboarding preview card advances instead of looking broken', (
    tester,
  ) async {
    SharedPreferences.setMockInitialValues({});
    final app = AppState();
    await tester.pumpWidget(VmesteApp(app: app));

    expect(find.text('Видеть то, что важно сейчас'), findsOneWidget);
    expect(find.text('Пропустить'), findsOneWidget);
    expect(find.byKey(const ValueKey('onboarding-goal-preview')), findsOneWidget);

    await tester.tap(find.byKey(const ValueKey('onboarding-goal-preview')));
    await tester.pumpAndSettle();

    expect(find.text('Подбирать условия, которые помогают'), findsOneWidget);
  });'''
text = replace_test(
    text,
    'onboarding',
    'add screen separates four kinds of intentions',
    ONBOARDING_TEST,
)

# The final v0.6 test-fix script may already have changed this label.
text = text.replace(
    "expect(find.text('Раз в неделю'), findsOneWidget);",
    "expect(find.text('Несколько раз'), findsOneWidget);",
)

# Compact copy introduced by the visual cleanup.
text = text.replace(
    "find.text('Что должно измениться или быть готово? Необязательно')",
    "find.text('Желаемый результат · необязательно')",
)
text = text.replace(
    "find.text('Ближайший шаг: Купить материал')",
    "find.text('Сейчас: Купить материал')",
)
text = text.replace(
    "expect(find.text('ДВИЖЕНИЕ К ЦЕЛИ'), findsOneWidget);",
    "expect(find.text('Доделать ремонт · 2 в работе'), findsOneWidget);",
)

VOICE_TEST = r'''  testWidgets('voice field keeps the microphone inside the white field', (
    tester,
  ) async {
    final controller = TextEditingController();
    addTearDown(controller.dispose);

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: VoiceField(
            controller: controller,
            label: 'Минимальный вариант',
            hint:
                'Что можно сделать хотя бы частично, если сегодня трудно начать?',
            lines: 3,
          ),
        ),
      ),
    );

    final field = tester.widget<TextField>(find.byType(TextField));
    expect(field.decoration?.suffixIcon, isNotNull);
    expect(field.decoration?.hintMaxLines, 3);
    expect(find.byIcon(Icons.mic_none_rounded), findsOneWidget);
    expect(find.text('Надиктовать'), findsNothing);
    expect(find.text('Остановить запись'), findsNothing);
  });'''
start = text.index("  testWidgets('voice field")
end = text.rindex('\n}')
text = text[:start] + VOICE_TEST.rstrip() + '\n' + text[end:]

# Compact goal editor uses a shorter, cleaner action label.
text = text.replace(
    "    expect(find.textContaining('Сколько времени удобно'), findsNothing);",
    "    expect(find.textContaining('Сколько времени удобно'), findsNothing);\n    expect(find.text('Сохранить цель'), findsOneWidget);\n    expect(find.text('Сохранить и выбрать действие'), findsNothing);",
)

path.write_text(text, encoding='utf-8')
