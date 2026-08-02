from pathlib import Path

path = Path('test/widget_test.dart')
text = path.read_text(encoding='utf-8')

if 'start choice keeps several contours active together' in text:
    print('v0.13.1 tests already applied')
    raise SystemExit(0)

insert_at = text.rindex('\n}')

tests = r'''
  testWidgets('start choice keeps several contours active together', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(390, 844);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    SharedPreferences.setMockInitialValues({});
    final app = AppState()
      ..onboarded = true
      ..startChoiceSeen = false;

    await tester.pumpWidget(
      MaterialApp(home: StartChoiceScreen(app: app)),
    );
    await tester.pumpAndSettle();

    expect(find.text('С чего начнём?'), findsOneWidget);
    expect(
      find.textContaining('Можно выбрать несколько вариантов'),
      findsOneWidget,
    );

    await tester.tap(find.byKey(const ValueKey('start-area-goal')));
    await tester.tap(find.byKey(const ValueKey('start-area-challenge')));
    await tester.ensureVisible(
      find.byKey(const ValueKey('start-area-tasks')),
    );
    await tester.tap(find.byKey(const ValueKey('start-area-tasks')));
    await tester.pump();

    expect(app.startChoiceSeen, isFalse);
    await tester.tap(find.byKey(const ValueKey('continue-start-choice')));
    await tester.pump();

    expect(app.startChoiceSeen, isTrue);
    expect(
      app.startAreas,
      containsAll(<StartArea>[
        StartArea.goal,
        StartArea.challenge,
        StartArea.tasks,
      ]),
    );
    expect(app.startAreas, hasLength(3));
    expect(tester.takeException(), isNull);
  });

  testWidgets('onboarded user is routed to start choice once', (tester) async {
    SharedPreferences.setMockInitialValues({});
    final app = AppState()
      ..onboarded = true
      ..startChoiceSeen = false;

    await tester.pumpWidget(VmesteApp(app: app));
    await tester.pumpAndSettle();

    expect(find.byKey(const ValueKey('start-choice-screen')), findsOneWidget);
    expect(find.byKey(const ValueKey('start-choice-title')), findsOneWidget);
    expect(find.byType(Shell), findsNothing);
    expect(tester.takeException(), isNull);
  });

  testWidgets('today exposes all four contours above the detailed lists', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(360, 760);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    SharedPreferences.setMockInitialValues({});
    final app = AppState()
      ..onboarded = true
      ..startChoiceSeen = true
      ..goal = Goal(
        'Выпустить приложение',
        'Стабильная версия опубликована',
        20,
        ['Проверка'],
      );
    app.actions.addAll([
      ActionItem(
        id: 'today-task',
        title: 'Позвонить мастеру',
        small: '',
        minutes: 0,
        support: Support.solo,
        goal: false,
        kind: IntentKind.focus,
        useTimer: false,
      ),
      ActionItem(
        id: 'today-routine',
        title: 'Сербский язык',
        small: 'Повторить пять слов',
        minutes: 15,
        support: Support.solo,
        goal: false,
        kind: IntentKind.routine,
        scheduledAt: DateTime.now(),
        routineSchedule: RoutineSchedule.daily,
      ),
    ]);
    app.challenges.add(
      Challenge(
        title: 'Работать над приложением',
        rule: 'Не менее двадцати минут',
        dailyTarget: 20,
        unit: 'минут',
        startDate: DateTime.now(),
        durationDays: 30,
        goalId: app.goal!.id,
      ),
    );

    await tester.pumpWidget(
      MaterialApp(
        home: Today(app: app, onOpenGoal: () {}),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.byKey(const ValueKey('today-area-overview')), findsOneWidget);
    expect(find.byKey(const ValueKey('home-goal-entry')), findsOneWidget);
    expect(find.byKey(const ValueKey('home-challenge-entry')), findsOneWidget);
    expect(find.byKey(const ValueKey('home-tasks-entry')), findsOneWidget);
    expect(find.byKey(const ValueKey('home-routines-entry')), findsOneWidget);
    expect(find.text('1 активных'), findsOneWidget);
    expect(find.text('1 на сегодня'), findsNWidgets(2));
    expect(tester.takeException(), isNull);
  });

  test('challenge can remain linked to the current important goal', () {
    final challenge = Challenge(
      title: 'Писать каждый день',
      rule: 'Не менее одной страницы',
      dailyTarget: 1,
      unit: 'страница',
      startDate: DateTime(2026, 8, 3),
      durationDays: 30,
      goalId: 'goal-42',
    );

    final restored = Challenge.fromJson(challenge.toJson());
    expect(restored.goalId, 'goal-42');
    expect(restored.title, challenge.title);
    expect(restored.durationDays, 30);
  });

  testWidgets('empty challenge is a visible action on Today', (tester) async {
    tester.view.physicalSize = const Size(360, 760);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    SharedPreferences.setMockInitialValues({});
    final app = AppState()
      ..onboarded = true
      ..startChoiceSeen = true;

    await tester.pumpWidget(
      MaterialApp(home: Today(app: app, onOpenGoal: () {})),
    );
    await tester.pumpAndSettle();
    await tester.scrollUntilVisible(
      find.byKey(const ValueKey('empty-challenge-card')),
      260,
      scrollable: find.byKey(const ValueKey('today-editorial-scroll')),
    );

    expect(find.text('Начать челлендж'), findsOneWidget);
    expect(find.textContaining('7, 21, 30, 60 или 90 дней'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
'''

text = text[:insert_at] + tests + text[insert_at:]
path.write_text(text, encoding='utf-8')
print('Applied v0.13.1 unified home tests')
