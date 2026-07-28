from pathlib import Path

main_path = Path('lib/main.dart')
main = main_path.read_text(encoding='utf-8')
start = main.index('class _PremiumEditorHeading extends StatelessWidget')
end = main.index('class Speech', start)
main_path.write_text(main[:start] + main[end:], encoding='utf-8')

path = Path('test/widget_test.dart')
text = path.read_text(encoding='utf-8')


def replace_test(source: str, start_name: str, next_name: str, replacement: str) -> str:
    start = source.index(f"  testWidgets('{start_name}")
    end = source.index(f"  testWidgets('{next_name}", start)
    return source[:start] + replacement.rstrip() + '\n\n' + source[end:]


ONBOARDING_TEST = r'''  testWidgets('onboarding explains the product and support before goal creation', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(360, 760);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    SharedPreferences.setMockInitialValues({});
    final app = AppState();
    await tester.pumpWidget(VmesteApp(app: app));
    await tester.pumpAndSettle();

    expect(find.text('Найдите свой способ двигаться к цели'), findsOneWidget);
    expect(
      find.textContaining('С опорой на исследования о планировании действий'),
      findsOneWidget,
    );
    expect(find.textContaining('остальные дела можно быстро записать'), findsOneWidget);
    expect(find.byKey(const ValueKey('onboarding-next')), findsOneWidget);
    expect(tester.takeException(), isNull);

    await tester.tap(find.byKey(const ValueKey('onboarding-next')));
    await tester.pumpAndSettle();

    expect(find.text('Подберите поддержку под конкретное действие'), findsOneWidget);
    expect(find.text('Вместе с человеком'), findsOneWidget);
    expect(find.textContaining('аудио- или видеосвязи'), findsOneWidget);
    expect(find.textContaining('Не каждое дело должно становиться большой целью'), findsOneWidget);
    expect(find.byKey(const ValueKey('onboarding-create-goal')), findsOneWidget);
    expect(tester.takeException(), isNull);
  });'''
start = text.index("  testWidgets('onboarding")
end = text.index("  testWidgets('add screen separates four kinds of intentions", start)
text = text[:start] + ONBOARDING_TEST.rstrip() + '\n\n' + text[end:]

GOAL_TEST = r'''  testWidgets('goal starts with a clear promise and continues to the first action', (
    tester,
  ) async {
    SharedPreferences.setMockInitialValues({});
    final app = AppState()..onboarded = true;

    await tester.pumpWidget(MaterialApp(home: GoalEditor(app: app)));

    expect(find.text('Чего вы хотите добиться?'), findsOneWidget);
    expect(find.text('Уточнить результат и этапы'), findsOneWidget);
    expect(find.text('Продолжить'), findsOneWidget);
    expect(find.text('Что произойдёт дальше'), findsOneWidget);
    expect(find.textContaining('подходящую поддержку'), findsOneWidget);
    expect(find.text('Сохранить цель'), findsNothing);

    await tester.tap(find.text('Уточнить результат и этапы'));
    await tester.pumpAndSettle();
    expect(
      find.text('Какой результат вы хотите получить? · необязательно'),
      findsOneWidget,
    );
  });'''
text = replace_test(
    text,
    'goal starts with only the goal name',
    'goal card is compact clickable and hides result copy',
    GOAL_TEST,
)

text = text.replace(
    "expect(find.text('Запланировать действие'), findsOneWidget);",
    "expect(find.text('Запланировать'), findsOneWidget);",
)

ACTION_FLOW_TEST = r'''  testWidgets('first action separates setup from support choice', (tester) async {
    tester.view.physicalSize = const Size(360, 760);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    final app = AppState()
      ..onboarded = true
      ..goal = Goal('Запустить проект', '', 0, const []);

    await tester.pumpWidget(
      MaterialApp(home: ActionEditor(app: app, goalDefault: true)),
    );
    await tester.pumpAndSettle();

    expect(find.text('Что вы можете сделать первым?'), findsOneWidget);
    expect(find.text('Выбрать поддержку'), findsOneWidget);
    expect(find.text('Вместе с человеком'), findsNothing);

    await tester.enterText(find.byType(TextField).first, 'Составить описание проекта');
    await tester.pump();
    await tester.tap(find.byKey(const ValueKey('choose-support')));
    await tester.pumpAndSettle();

    expect(find.byKey(const ValueKey('action-support-step')), findsOneWidget);
    expect(find.text('Как вам будет легче начать?'), findsOneWidget);
    expect(find.text('Вместе с человеком'), findsOneWidget);
    expect(find.textContaining('аудио- или видеосвязи'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });'''
end = text.rindex('\n}')
text = text[:end] + '\n\n' + ACTION_FLOW_TEST.rstrip() + text[end:]

path.write_text(text, encoding='utf-8')
