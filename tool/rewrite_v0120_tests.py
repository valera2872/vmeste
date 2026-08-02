from pathlib import Path

path = Path('test/widget_test.dart')
text = path.read_text(encoding='utf-8')

if 'challenge stores daily progress and survives restore' in text:
    print('v0.12.0 challenge tests already applied')
    raise SystemExit(0)

insert_at = text.rindex('\n}')

tests = r'''
  test('challenge stores daily progress and survives restore', () {
    final app = AppState();
    final challenge = Challenge(
      id: 'challenge-model',
      title: 'Подтягивания каждый день',
      rule: 'Не менее пяти повторений',
      dailyTarget: 5,
      unit: 'раз',
      startDate: DateTime.now(),
      durationDays: 90,
      mode: ChallengeMode.solo,
    );
    app.addChallenge(challenge);
    app.markChallengeDay(
      challenge,
      ChallengeDayResult.full,
      amount: 5,
    );

    expect(challenge.fullDays, 1);
    expect(challenge.currentStreak, 1);
    expect(challenge.dayNumber(), 1);
    expect(challenge.entryFor(DateTime.now())?.amount, 5);

    final restored = Challenge.fromJson(challenge.toJson());
    expect(restored.title, 'Подтягивания каждый день');
    expect(restored.durationDays, 90);
    expect(restored.mode, ChallengeMode.solo);
    expect(restored.fullDays, 1);
    expect(restored.entryFor(DateTime.now())?.result, ChallengeDayResult.full);
  });

  testWidgets('personal challenge is a separate block on Today', (tester) async {
    tester.view.physicalSize = const Size(360, 760);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    SharedPreferences.setMockInitialValues({});
    final app = AppState()..onboarded = true;
    app.challenges.add(
      Challenge(
        id: 'today-challenge',
        title: '100 отжиманий каждый день',
        rule: 'Сделать за день суммарно',
        dailyTarget: 100,
        unit: 'раз',
        startDate: DateTime.now(),
        durationDays: 30,
      ),
    );

    await tester.pumpWidget(
      MaterialApp(home: Today(app: app, onOpenGoal: () {})),
    );
    await tester.pumpAndSettle();

    expect(find.byKey(const ValueKey('today-challenges-area')), findsOneWidget);
    expect(find.text('Челленджи'), findsOneWidget);
    expect(find.text('100 отжиманий каждый день'), findsOneWidget);
    expect(find.textContaining('День 1 из 30'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('challenge waits for an explicit daily mark', (tester) async {
    tester.view.physicalSize = const Size(360, 760);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    SharedPreferences.setMockInitialValues({});
    final app = AppState()..onboarded = true;
    final challenge = Challenge(
      id: 'mark-challenge',
      title: 'Читать каждый день',
      rule: 'Не менее двадцати страниц',
      dailyTarget: 20,
      unit: 'страниц',
      startDate: DateTime.now(),
      durationDays: 21,
    );
    app.challenges.add(challenge);

    await tester.pumpWidget(
      MaterialApp(
        home: ChallengeDetailScreen(app: app, challenge: challenge),
      ),
    );
    await tester.pumpAndSettle();

    expect(challenge.entryFor(DateTime.now()), isNull);
    expect(find.text('Сегодня ещё не отмечено'), findsOneWidget);

    await tester.ensureVisible(
      find.byKey(const ValueKey('challenge-mark-full')),
    );
    await tester.tap(find.byKey(const ValueKey('challenge-mark-full')));
    await tester.pumpAndSettle();

    expect(challenge.entryFor(DateTime.now())?.result, ChallengeDayResult.full);
    expect(challenge.entryFor(DateTime.now())?.amount, 20);
    expect(find.text('Сегодня: Выполнено'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('partner challenge is visible in Together without replacing support', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(360, 760);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    SharedPreferences.setMockInitialValues({});
    final app = AppState()..onboarded = true;
    app.challenges.add(
      Challenge(
        id: 'partner-challenge',
        title: 'Пять подтягиваний',
        rule: 'Каждый отмечает свой результат',
        dailyTarget: 5,
        unit: 'раз',
        startDate: DateTime.now(),
        durationDays: 90,
        mode: ChallengeMode.partner,
        partner: 'Друг',
      ),
    );
    final action = ActionItem(
      id: 'support-stays',
      title: 'Подготовить экран',
      small: 'Открыть файл',
      minutes: 15,
      support: Support.ai,
      goal: true,
    );
    app.actions.add(action);

    await tester.pumpWidget(MaterialApp(home: SupportScreen(app: app)));
    await tester.pumpAndSettle();

    expect(
      find.byKey(const ValueKey('together-partner-challenges')),
      findsOneWidget,
    );
    expect(find.text('СОВМЕСТНЫЕ ЧЕЛЛЕНДЖИ'), findsOneWidget);
    expect(action.support, Support.ai);
    expect(tester.takeException(), isNull);
  });
'''

text = text[:insert_at] + tests + text[insert_at:]
path.write_text(text, encoding='utf-8')
print('Applied v0.12.0 challenge tests')
