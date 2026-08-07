from pathlib import Path

path = Path('test/widget_test.dart')
text = path.read_text(encoding='utf-8')

insert = r'''

  test('support feedback survives json migration', () {
    final item = HistoryItem(
      'Подготовить экран',
      15,
      Support.ai,
      ResultState.done,
      DateTime.now(),
      true,
      actionId: 'action-feedback',
      supportEffect: SupportEffect.yes,
    );

    final restored = HistoryItem.fromJson(item.toJson());
    expect(restored.actionId, 'action-feedback');
    expect(restored.supportEffect, SupportEffect.yes);
  });

  testWidgets('session offers help before the timer starts', (tester) async {
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

    expect(find.byKey(const ValueKey('start-difficulty-button')), findsOneWidget);
    await tester.tap(find.byKey(const ValueKey('start-difficulty-button')));
    await tester.pumpAndSettle();

    expect(find.byKey(const ValueKey('start-difficulty-sheet')), findsOneWidget);
    expect(find.text('Что мешает начать?'), findsOneWidget);
    expect(find.text('Действие слишком большое'), findsOneWidget);
    expect(find.text('Нужен человек рядом'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('result feedback creates a cautious personal insight', (
    tester,
  ) async {
    SharedPreferences.setMockInitialValues({});
    final app = AppState()..onboarded = true;
    final item = ActionItem(
      id: 'feedback-action',
      title: 'Сделать первый шаг',
      small: 'Открыть документ',
      minutes: 10,
      support: Support.ai,
      goal: true,
    );
    app.actions.add(item);
    app.complete(item, ResultState.done);

    await tester.pumpWidget(
      MaterialApp(
        home: ResultPage(app: app, item: item, state: ResultState.done),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.byKey(const ValueKey('support-feedback-card')), findsOneWidget);
    expect(find.text('Этот способ помог вам начать?'), findsOneWidget);
    await tester.tap(find.byKey(const ValueKey('support-effect-yes')));
    await tester.pumpAndSettle();
    expect(app.history.first.supportEffect, SupportEffect.yes);
    expect(find.byKey(const ValueKey('support-feedback-saved')), findsOneWidget);

    await tester.pumpWidget(MaterialApp(home: Progress(app: app)));
    await tester.pumpAndSettle();
    expect(find.byKey(const ValueKey('weekly-review-card')), findsOneWidget);
    expect(find.byKey(const ValueKey('personal-insight-card')), findsOneWidget);
    expect(find.text('Что помогает вам начинать'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
'''

end = text.rfind('\n}')
if end < 0:
    raise SystemExit('test main closing brace not found')
text = text[:end] + insert + text[end:]
path.write_text(text, encoding='utf-8')
print('Applied v0.7 personal support tests')
