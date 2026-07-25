from pathlib import Path

path = Path('test/widget_test.dart')
text = path.read_text(encoding='utf-8')

text = text.replace(
    "    await tester.tap(find.text('Добавить'));",
    "    await tester.tap(find.byKey(const ValueKey('today-add')));",
)
text = text.replace(
    "expect(find.text('Сейчас: Купить материал'), findsOneWidget);",
    "expect(find.text('Сейчас · Купить материал'), findsOneWidget);",
)
text = text.replace(
    "    expect(find.text('Доделать ремонт · 2 в работе'), findsOneWidget);\n    expect(find.textContaining('2 в работе'), findsWidgets);",
    "    expect(find.text('Следующий шаг'), findsOneWidget);\n    expect(find.text('Доделать ремонт'), findsOneWidget);\n    expect(find.textContaining('2 в работе'), findsOneWidget);",
)

NARROW_TEST = r'''  testWidgets('today primary action stays on one line on a narrow phone', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(360, 760);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    SharedPreferences.setMockInitialValues({});
    final app = AppState()
      ..onboarded = true
      ..goal = Goal('Доделать ремонт', '', 0, const []);
    app.actions.add(
      ActionItem(
        id: 'narrow-action',
        title: 'Купить строительные материалы',
        small: '',
        minutes: 0,
        support: Support.solo,
        goal: true,
        kind: IntentKind.goalStep,
        useTimer: false,
      ),
    );

    await tester.pumpWidget(VmesteApp(app: app));
    await tester.pumpAndSettle();

    final primary = find.byKey(
      const ValueKey('action-primary-narrow-action'),
    );
    expect(primary, findsOneWidget);
    expect(find.descendant(of: primary, matching: find.text('Отметить')), findsOneWidget);
    expect(find.text('Записать результат'), findsNothing);
    expect(find.byKey(const ValueKey('today-add')), findsOneWidget);
    expect(tester.getSize(primary).height, lessThanOrEqualTo(44));
    expect(tester.takeException(), isNull);
  });'''

end = text.rindex('\n}')
text = text[:end] + '\n\n' + NARROW_TEST.rstrip() + text[end:]
path.write_text(text, encoding='utf-8')
