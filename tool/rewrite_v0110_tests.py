from pathlib import Path

path = Path('test/widget_test.dart')
text = path.read_text(encoding='utf-8')

if "together start waits for an explicit start" in text:
    print('v0.11.0 tests already applied')
    raise SystemExit(0)

insert_at = text.rindex('\n}')

tests = r'''
  test('support agreement keeps start and completion timestamps', () {
    final app = AppState();
    final agreement = SupportAgreement(
      id: 'agreement-lifecycle',
      actionId: 'action-lifecycle',
      actionTitle: 'Подготовить публикацию',
      mode: SupportInviteMode.simultaneous,
      status: SupportInviteStatus.accepted,
      scheduledAt: DateTime.now().add(const Duration(hours: 1)),
      minutes: 20,
    );
    app.supportAgreements.add(agreement);

    app.setSupportAgreementStatus(
      agreement,
      SupportInviteStatus.started,
    );
    expect(agreement.status, SupportInviteStatus.started);
    expect(agreement.startedAt, isNotNull);

    app.setSupportAgreementStatus(
      agreement,
      SupportInviteStatus.completed,
    );
    expect(agreement.status, SupportInviteStatus.completed);
    expect(agreement.completedAt, isNotNull);

    final restored = SupportAgreement.fromJson(agreement.toJson());
    expect(restored.status, SupportInviteStatus.completed);
    expect(restored.startedAt, isNotNull);
    expect(restored.completedAt, isNotNull);
  });

  testWidgets('together start waits for an explicit start', (tester) async {
    tester.view.physicalSize = const Size(360, 760);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    SharedPreferences.setMockInitialValues({});
    final app = AppState()..onboarded = true;
    final action = ActionItem(
      id: 'together-action',
      title: 'Проверить карточку совместного старта',
      small: 'Открыть только карточку',
      minutes: 0,
      support: Support.ai,
      goal: true,
      kind: IntentKind.goalStep,
      useTimer: false,
    );
    final agreement = SupportAgreement(
      id: 'together-agreement',
      actionId: action.id,
      actionTitle: action.title,
      mode: SupportInviteMode.simultaneous,
      status: SupportInviteStatus.accepted,
      scheduledAt: DateTime.now().add(const Duration(minutes: 10)),
      minutes: 15,
      partner: 'Матвей',
    );
    app.actions.add(action);
    app.supportAgreements.add(agreement);

    await tester.pumpWidget(
      MaterialApp(home: SupportAgreementsScreen(app: app)),
    );
    await tester.pumpAndSettle();

    expect(agreement.status, SupportInviteStatus.accepted);
    await tester.tap(
      find.byKey(const ValueKey('open-together-together-agreement')),
    );
    await tester.pumpAndSettle();

    expect(find.text('Начать вместе'), findsOneWidget);
    expect(find.byKey(const ValueKey('together-countdown')), findsOneWidget);
    expect(agreement.status, SupportInviteStatus.accepted);
    expect(find.byKey(const ValueKey('record-together-result')), findsNothing);

    await tester.tap(find.byKey(const ValueKey('open-together-action')));
    await tester.pumpAndSettle();

    expect(agreement.status, SupportInviteStatus.started);
    expect(agreement.startedAt, isNotNull);
    expect(find.byKey(const ValueKey('record-together-result')), findsOneWidget);
    expect(action.support, Support.ai);
    expect(tester.takeException(), isNull);
  });

  testWidgets('together tab exposes saved agreements', (tester) async {
    tester.view.physicalSize = const Size(360, 760);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    SharedPreferences.setMockInitialValues({});
    final app = AppState()..onboarded = true;
    app.supportAgreements.add(
      SupportAgreement(
        id: 'tab-agreement',
        actionId: 'tab-action',
        actionTitle: 'Подготовить один экран',
        mode: SupportInviteMode.report,
        status: SupportInviteStatus.sent,
        scheduledAt: DateTime.now().add(const Duration(hours: 2)),
        minutes: 15,
      ),
    );

    await tester.pumpWidget(MaterialApp(home: SupportScreen(app: app)));
    await tester.pumpAndSettle();

    expect(
      find.byKey(const ValueKey('open-all-support-agreements')),
      findsOneWidget,
    );
    expect(find.text('Договорённости (1)'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
'''

text = text[:insert_at] + tests + text[insert_at:]
path.write_text(text, encoding='utf-8')
print('Applied v0.11.0 together start tests')
