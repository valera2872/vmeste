from pathlib import Path

path = Path('test/widget_test.dart')
text = path.read_text(encoding='utf-8')

if 'feasible start waits for an explicit start' in text:
    print('v0.13.0 tests already applied')
    raise SystemExit(0)

insert_at = text.rindex('\n}')

tests = r'''
  test('start attempt and continuation survive restore', () {
    final app = AppState();
    final action = ActionItem(
      id: 'feasible-json-action',
      title: 'Подготовить описание приложения',
      small: 'Написать один абзац',
      minutes: 20,
      support: Support.ai,
      goal: true,
      kind: IntentKind.goalStep,
    );
    final attempt = app.beginStartAttempt(
      action,
      StartBarrier.tooBig,
      StartLevel.small,
    );
    app.markStartAttemptStarted(attempt);
    app.setContinuationPoint(action.id, 'Открыть второй абзац');
    app.finishStartAttempt(action.id, ResultState.part);

    final restored = StartAttempt.fromJson(attempt.toJson());
    expect(restored.barrier, StartBarrier.tooBig);
    expect(restored.level, StartLevel.small);
    expect(restored.startedAt, isNotNull);
    expect(restored.completedAt, isNotNull);
    expect(restored.helpful, isTrue);
    expect(app.continuationFor(action.id), 'Открыть второй абзац');
  });

  testWidgets('feasible start waits for an explicit start', (tester) async {
    tester.view.physicalSize = const Size(360, 760);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    SharedPreferences.setMockInitialValues({});
    final app = AppState()..onboarded = true;
    final action = ActionItem(
      id: 'feasible-start-action',
      title: 'Проверить карточку приложения',
      small: 'Проверить только заголовок',
      minutes: 20,
      support: Support.ai,
      goal: true,
      kind: IntentKind.goalStep,
    );
    app.actions.add(action);

    await tester.pumpWidget(
      MaterialApp(home: Session(app: app, item: action)),
    );
    await tester.pumpAndSettle();

    await tester.tap(find.byKey(const ValueKey('start-difficulty-button')));
    await tester.pumpAndSettle();
    expect(find.byKey(const ValueKey('start-barrier-sheet')), findsOneWidget);

    await tester.tap(
      find.byKey(const ValueKey('start-barrier-tooBig')),
    );
    await tester.pumpAndSettle();

    expect(find.byKey(const ValueKey('feasible-start-plan')), findsOneWidget);
    expect(app.startAttempts, hasLength(1));
    expect(app.startAttempts.first.startedAt, isNull);
    expect(find.text('Таймер ещё не запущен'), findsNothing);
    expect(find.text('ТАЙМЕР ЕЩЁ НЕ ЗАПУЩЕН'), findsOneWidget);

    await tester.tap(find.byKey(const ValueKey('start-level-contact')));
    await tester.pump();
    expect(app.startAttempts.first.level, StartLevel.contact);
    expect(app.startAttempts.first.startedAt, isNull);

    await tester.tap(find.byKey(const ValueKey('start-confirm-button')));
    await tester.pump();
    expect(app.startAttempts.first.startedAt, isNotNull);
    expect(find.text('Вы уже начали'), findsOneWidget);
    expect(tester.takeException(), isNull);

    await tester.pumpWidget(const MaterialApp(home: SizedBox()));
    await tester.pump();
  });

  testWidgets('feasible start offers eight non-shaming barriers', (tester) async {
    tester.view.physicalSize = const Size(360, 760);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: StartBarrierSheet(scrollController: ScrollController()),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Что делает начало трудным?'), findsOneWidget);
    for (final barrier in StartBarrier.values.take(4)) {
      expect(
        find.byKey(ValueKey('start-barrier-${barrier.name}')),
        findsOneWidget,
      );
    }
    expect(find.textContaining('Это не диагноз'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('goal path shows cautious start learning', (tester) async {
    tester.view.physicalSize = const Size(360, 760);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    SharedPreferences.setMockInitialValues({});
    final app = AppState()
      ..onboarded = true
      ..goal = Goal('Выпустить приложение', 'Стабильная сборка', 20, ['Тест']);
    final action = ActionItem(
      id: 'insight-action',
      title: 'Проверить первый сценарий',
      small: 'Открыть первый экран',
      minutes: 15,
      support: Support.ai,
      goal: true,
      kind: IntentKind.goalStep,
    );
    app.actions.add(action);
    app.startAttempts.add(
      StartAttempt(
        actionId: action.id,
        barrier: StartBarrier.unclear,
        level: StartLevel.small,
        startedAt: DateTime.now(),
      ),
    );

    await tester.pumpWidget(MaterialApp(home: GoalScreen(app: app)));
    await tester.pumpAndSettle();
    await tester.scrollUntilVisible(
      find.byKey(const ValueKey('feasible-start-insight')),
      300,
      scrollable: find.byType(Scrollable).first,
    );

    expect(find.byKey(const ValueKey('feasible-start-insight')), findsOneWidget);
    expect(find.textContaining('Непонятно, с чего начать'), findsOneWidget);
    expect(find.textContaining('не диагноз'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
'''

text = text[:insert_at] + tests + text[insert_at:]
path.write_text(text, encoding='utf-8')
print('Applied v0.13.0 feasible start tests')
