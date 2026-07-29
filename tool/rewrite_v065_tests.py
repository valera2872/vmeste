from pathlib import Path

path = Path('test/widget_test.dart')
text = path.read_text(encoding='utf-8')


def replace_test(source: str, start_name: str, next_name: str, replacement: str) -> str:
    start = source.index(f"  testWidgets('{start_name}")
    end = source.index(f"  testWidgets('{next_name}", start)
    return source[:start] + replacement.rstrip() + '\n\n' + source[end:]


TODAY_TEST = r'''  testWidgets('today shows goal other work and quick capture together', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(360, 760);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    SharedPreferences.setMockInitialValues({});
    final app = AppState()
      ..onboarded = true
      ..goal = Goal('Запустить приложение «Вместе к цели»', '', 0, ['Тестирование']);
    app.actions.addAll([
      ActionItem(
        id: 'goal-1',
        title: 'Проверить первый пользовательский сценарий',
        small: '',
        minutes: 20,
        support: Support.solo,
        goal: true,
        kind: IntentKind.goalStep,
      ),
      ActionItem(
        id: 'goal-2',
        title: 'Исправить найденные замечания',
        small: '',
        minutes: 30,
        support: Support.solo,
        goal: true,
        kind: IntentKind.goalStep,
      ),
      ActionItem(
        id: 'other-1',
        title: 'Оплатить счёт',
        small: '',
        minutes: 0,
        support: Support.solo,
        goal: false,
        kind: IntentKind.focus,
        useTimer: false,
      ),
      ActionItem(
        id: 'other-2',
        title: 'Позвонить врачу',
        small: '',
        minutes: 0,
        support: Support.solo,
        goal: false,
        kind: IntentKind.focus,
        useTimer: false,
      ),
    ]);

    await tester.pumpWidget(VmesteApp(app: app));
    await tester.pumpAndSettle();

    expect(
      find.descendant(of: find.byType(AppBar), matching: find.text('Сегодня')),
      findsOneWidget,
    );
    expect(find.text('ГЛАВНАЯ ЦЕЛЬ'), findsOneWidget);
    expect(find.text('Запустить приложение «Вместе к цели»'), findsOneWidget);
    expect(find.text('Следующий шаг'), findsOneWidget);
    expect(find.text('Проверить первый пользовательский сценарий'), findsOneWidget);
    expect(find.text('Остальное на сегодня'), findsOneWidget);
    expect(find.text('Оплатить счёт'), findsOneWidget);
    expect(find.byKey(const ValueKey('quick-capture-field')), findsOneWidget);
    expect(find.byKey(const ValueKey('quick-capture-add')), findsOneWidget);
    expect(tester.takeException(), isNull);

    final quickField = find.descendant(
      of: find.byKey(const ValueKey('quick-capture-field')),
      matching: find.byType(TextField),
    );
    await tester.enterText(quickField, 'Купить картриджи');
    await tester.tap(find.byKey(const ValueKey('quick-capture-add')));
    await tester.pumpAndSettle();

    expect(app.actions.any((item) => item.title == 'Купить картриджи'), isTrue);
    expect(find.text('Купить картриджи'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });'''

text = replace_test(
    text,
    'today keeps one main step and makes other work obvious',
    'reminder does not ask for duration',
    TODAY_TEST,
)

# The new editorial primary button replaces the old ActionCard button on Today.
text = text.replace(
    "const ValueKey('action-primary-narrow-action')",
    "const ValueKey('today-primary-action')",
)
text = text.replace(
    "expect(tester.getSize(primary).height, lessThanOrEqualTo(44));",
    "expect(tester.getSize(primary).height, lessThanOrEqualTo(48));",
)

FIRST_CAPTURE_TEST = r'''  testWidgets('new goal offers brain dump before the first step', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(360, 800);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    SharedPreferences.setMockInitialValues({});
    final app = AppState()..onboarded = true;
    await tester.pumpWidget(MaterialApp(home: GoalEditor(app: app)));

    await tester.enterText(find.byType(TextField).first, 'Закончить ремонт');
    await tester.scrollUntilVisible(
      find.byKey(const ValueKey('goal-continue')),
      250,
      scrollable: find.byType(Scrollable).first,
    );
    await tester.tap(find.byKey(const ValueKey('goal-continue')));
    await tester.pumpAndSettle();

    expect(app.goal?.title, 'Закончить ремонт');
    expect(find.text('Главная цель создана'), findsOneWidget);
    expect(find.text('Что ещё сейчас занимает вашу голову?'), findsOneWidget);
    expect(find.byKey(const ValueKey('first-capture-field')), findsOneWidget);

    final captureField = find.descendant(
      of: find.byKey(const ValueKey('first-capture-field')),
      matching: find.byType(TextField),
    );
    await tester.enterText(captureField, 'Оплатить интернет');
    await tester.tap(find.byKey(const ValueKey('first-capture-add')));
    await tester.pumpAndSettle();

    expect(app.actions.any((item) => item.title == 'Оплатить интернет'), isTrue);
    expect(find.text('Напомнить'), findsOneWidget);
    expect(find.text('Запланировать'), findsOneWidget);
    expect(find.text('Повторять'), findsOneWidget);

    await tester.scrollUntilVisible(
      find.byKey(const ValueKey('continue-first-step')),
      260,
      scrollable: find.byType(Scrollable).first,
    );
    await tester.tap(find.byKey(const ValueKey('continue-first-step')));
    await tester.pumpAndSettle();

    expect(find.text('Что вы можете сделать первым?'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });'''

end = text.rindex('\n}')
text = text[:end] + '\n\n' + FIRST_CAPTURE_TEST.rstrip() + text[end:]
path.write_text(text, encoding='utf-8')
print('Applied v0.6.5 tests')
