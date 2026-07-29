from pathlib import Path

path = Path('test/widget_test.dart')
text = path.read_text(encoding='utf-8')

start = text.index("  testWidgets('session offers help before the timer starts'")
end = text.index("  testWidgets('result feedback creates a cautious personal insight'", start)
replacement = r'''  testWidgets('start difficulty waits for an explicit start', (tester) async {
    SharedPreferences.setMockInitialValues({});
    final app = AppState()..onboarded = true;
    final item = ActionItem(
      id: 'start-help',
      title: 'Подготовить первый экран',
      small: '',
      minutes: 20,
      support: Support.solo,
      goal: true,
    );
    app.actions.add(item);

    await tester.pumpWidget(MaterialApp(home: Session(app: app, item: item)));

    await tester.tap(find.byKey(const ValueKey('start-difficulty-button')));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Действие слишком большое'));
    await tester.pumpAndSettle();

    expect(find.byKey(const ValueKey('start-adjustment-card')), findsOneWidget);
    expect(find.text('Что поможет сейчас'), findsOneWidget);
    expect(find.text('ТАЙМЕР ЕЩЁ НЕ ЗАПУЩЕН'), findsOneWidget);
    expect(find.text('Вы уже начали'), findsNothing);
    expect(find.byKey(const ValueKey('start-confirm-button')), findsOneWidget);
    expect(tester.takeException(), isNull);

    await tester.tap(find.byKey(const ValueKey('start-confirm-button')));
    await tester.pump();
    expect(find.text('Вы уже начали'), findsOneWidget);

    await tester.pumpWidget(const SizedBox.shrink());
    await tester.pump();
  });

  testWidgets('active difficulty pauses until the user chooses to continue', (
    tester,
  ) async {
    SharedPreferences.setMockInitialValues({});
    final app = AppState()..onboarded = true;
    final item = ActionItem(
      id: 'active-help',
      title: 'Подготовить первый экран',
      small: '',
      minutes: 20,
      support: Support.solo,
      goal: true,
    );
    app.actions.add(item);

    await tester.pumpWidget(MaterialApp(home: Session(app: app, item: item)));
    await tester.tap(find.byKey(const ValueKey('start-confirm-button')));
    await tester.pump();
    await tester.tap(find.byKey(const ValueKey('active-difficulty-button')));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Действие оказалось слишком большим'));
    await tester.pumpAndSettle();

    expect(find.byKey(const ValueKey('active-adjustment-card')), findsOneWidget);
    expect(find.text('ТАЙМЕР НА ПАУЗЕ'), findsOneWidget);
    expect(find.text('Пауза'), findsOneWidget);

    final timerFinder = find.byWidgetPredicate(
      (widget) =>
          widget is Text &&
          RegExp(r'^\d{2}:\d{2}$').hasMatch(widget.data ?? ''),
    );
    expect(timerFinder, findsOneWidget);
    final before = tester.widget<Text>(timerFinder).data;
    await tester.pump(const Duration(seconds: 2));
    final after = tester.widget<Text>(timerFinder).data;
    expect(after, before);

    await tester.tap(find.byKey(const ValueKey('active-adjustment-apply')));
    await tester.pump();
    expect(find.text('Вы уже начали'), findsOneWidget);
    expect(find.byKey(const ValueKey('active-adjustment-card')), findsNothing);
    expect(tester.takeException(), isNull);

    await tester.pumpWidget(const SizedBox.shrink());
    await tester.pump();
  });

'''
text = text[:start] + replacement + text[end:]
path.write_text(text, encoding='utf-8')
print('Applied v0.7.1 calm support flow tests')
