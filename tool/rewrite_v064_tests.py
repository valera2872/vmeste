from pathlib import Path

path = Path('test/widget_test.dart')
text = path.read_text(encoding='utf-8')


def replace_test(source: str, start_name: str, next_name: str, replacement: str) -> str:
    start = source.index(f"  testWidgets('{start_name}")
    end = source.index(f"  testWidgets('{next_name}", start)
    return source[:start] + replacement.rstrip() + '\n\n' + source[end:]


TODAY_TEST = r'''  testWidgets('today keeps one main step and makes other work obvious', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(360, 760);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    SharedPreferences.setMockInitialValues({});
    final app = AppState()
      ..onboarded = true
      ..goal = Goal('Доделать ремонт', '', 0, ['Ванная']);
    app.actions.addAll([
      ActionItem(
        id: '1',
        title: 'Купить плитку',
        small: '',
        minutes: 0,
        support: Support.solo,
        goal: true,
        kind: IntentKind.goalStep,
        useTimer: false,
      ),
      ActionItem(
        id: '2',
        title: 'Подготовить стену',
        small: '',
        minutes: 60,
        support: Support.solo,
        goal: true,
        kind: IntentKind.goalStep,
      ),
    ]);

    await tester.pumpWidget(VmesteApp(app: app));
    await tester.pumpAndSettle();

    expect(find.text('Сегодня'), findsOneWidget);
    expect(find.text('ГЛАВНАЯ ЦЕЛЬ'), findsOneWidget);
    expect(find.text('Следующий шаг'), findsOneWidget);
    expect(find.text('Купить плитку'), findsWidgets);
    expect(find.text('Ещё 1 в главной цели'), findsOneWidget);

    await tester.drag(
      find.byKey(const ValueKey('today-scroll')),
      const Offset(0, -360),
    );
    await tester.pumpAndSettle();

    expect(find.text('Остальные дела'), findsOneWidget);
    expect(find.byKey(const ValueKey('add-other-work')), findsOneWidget);
    expect(find.textContaining('разгрузить голову'), findsOneWidget);
    expect(tester.takeException(), isNull);

    await tester.tap(find.byKey(const ValueKey('add-other-work')));
    await tester.pumpAndSettle();
    expect(find.text('Просто напомнить'), findsOneWidget);
    expect(find.text('Повторять регулярно'), findsOneWidget);
  });'''
text = replace_test(
    text,
    'today visually groups actions under the main goal',
    'reminder does not ask for duration',
    TODAY_TEST,
)

GOAL_WORKSPACE_TEST = r'''  testWidgets('goal workspace separates next steps from other work', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(360, 760);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    final app = AppState()
      ..onboarded = true
      ..goal = Goal(
        'Запустить новое приложение с очень длинным названием',
        'Рабочая версия опубликована и доступна первым пользователям',
        0,
        ['Прототип', 'Тестирование', 'Публикация'],
      );
    app.actions.add(
      ActionItem(
        id: 'goal-step',
        title: 'Проверить первый пользовательский сценарий',
        small: '',
        minutes: 20,
        support: Support.solo,
        goal: true,
        kind: IntentKind.goalStep,
      ),
    );

    await tester.pumpWidget(MaterialApp(home: GoalScreen(app: app)));
    await tester.pumpAndSettle();

    expect(find.text('ВАШЕ НАПРАВЛЕНИЕ'), findsOneWidget);
    expect(find.byKey(const ValueKey('add-goal-step')), findsOneWidget);
    expect(find.byKey(const ValueKey('add-other-from-goal')), findsOneWidget);
    expect(find.text('Активные шаги'), findsOneWidget);
    expect(tester.takeException(), isNull);

    await tester.tap(find.byKey(const ValueKey('add-other-from-goal')));
    await tester.pumpAndSettle();
    expect(find.text('Что добавить?'), findsOneWidget);
    expect(find.text('Дойти до цели'), findsOneWidget);
  });'''

end = text.rindex('\n}')
text = text[:end] + '\n\n' + GOAL_WORKSPACE_TEST.rstrip() + text[end:]
path.write_text(text, encoding='utf-8')
