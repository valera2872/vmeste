from pathlib import Path

path = Path('test/widget_test.dart')
text = path.read_text(encoding='utf-8')

if "support agreement survives json migration" in text:
    print('v0.10.0 tests already applied')
    raise SystemExit(0)

insert_at = text.rindex('\n}')

tests = r'''
  test('support agreement survives json migration', () {
    final source = SupportAgreement(
      id: 'agreement-1',
      actionId: 'action-1',
      actionTitle: 'Проверить первый экран',
      mode: SupportInviteMode.report,
      status: SupportInviteStatus.sent,
      scheduledAt: DateTime(2026, 8, 2, 10, 30),
      minutes: 25,
      partner: 'Матвей',
      createdAt: DateTime(2026, 8, 1, 20),
      updatedAt: DateTime(2026, 8, 1, 20, 5),
    );

    final restored = SupportAgreement.fromJson(source.toJson());
    expect(restored.id, 'agreement-1');
    expect(restored.actionId, 'action-1');
    expect(restored.mode, SupportInviteMode.report);
    expect(restored.status, SupportInviteStatus.sent);
    expect(restored.minutes, 25);
    expect(restored.partner, 'Матвей');
    expect(
      supportInviteMessage(restored),
      contains('Устанавливать приложение не нужно'),
    );
  });

  testWidgets('goal path creates a support agreement without starting timer', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(360, 800);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    SharedPreferences.setMockInitialValues({});
    final app = AppState()
      ..onboarded = true
      ..goal = Goal(
        'Подготовить приложение к публикации',
        'Рабочая сборка проверена',
        0,
        ['Проверка', 'Публикация'],
      );
    final action = ActionItem(
      id: 'support-action',
      title: 'Проверить первый пользовательский сценарий',
      small: 'Пройти только первый экран',
      minutes: 20,
      support: Support.ai,
      goal: true,
      kind: IntentKind.goalStep,
    );
    app.actions.add(action);

    await tester.pumpWidget(MaterialApp(home: GoalScreen(app: app)));
    await tester.pumpAndSettle();

    final goalScroll = find.byType(Scrollable).first;
    await tester.scrollUntilVisible(
      find.byKey(const ValueKey('goal-support-invite')),
      260,
      scrollable: goalScroll,
    );
    await tester.pumpAndSettle();
    expect(
      find.byKey(const ValueKey('goal-support-agreement-card')),
      findsOneWidget,
    );

    await tester.tap(find.byKey(const ValueKey('goal-support-invite')));
    await tester.pumpAndSettle();
    expect(find.text('Поддержка знакомого'), findsOneWidget);
    expect(find.byKey(const ValueKey('start-confirm-button')), findsNothing);

    final inviteScroll = find.byType(Scrollable).first;
    await tester.scrollUntilVisible(
      find.byKey(const ValueKey('invite-mode-report')),
      220,
      scrollable: inviteScroll,
    );
    await tester.tap(find.byKey(const ValueKey('invite-mode-report')));
    await tester.pumpAndSettle();

    await tester.scrollUntilVisible(
      find.byKey(const ValueKey('support-partner-name')),
      300,
      scrollable: inviteScroll,
    );
    await tester.enterText(
      find.byKey(const ValueKey('support-partner-name')),
      'Матвей',
    );
    await tester.pumpAndSettle();

    await tester.scrollUntilVisible(
      find.byKey(const ValueKey('save-support-draft')),
      360,
      scrollable: inviteScroll,
    );
    await tester.tap(find.byKey(const ValueKey('save-support-draft')));
    await tester.pumpAndSettle();

    expect(app.supportAgreements, hasLength(1));
    final agreement = app.supportAgreements.single;
    expect(agreement.actionId, action.id);
    expect(agreement.mode, SupportInviteMode.report);
    expect(agreement.status, SupportInviteStatus.draft);
    expect(agreement.partner, 'Матвей');
    expect(action.support, Support.ai);
    expect(tester.takeException(), isNull);

    app.setSupportAgreementStatus(
      agreement,
      SupportInviteStatus.accepted,
    );
    expect(agreement.status, SupportInviteStatus.accepted);
  });
'''

text = text[:insert_at] + tests + text[insert_at:]
path.write_text(text, encoding='utf-8')
print('Applied v0.10.0 support friend tests')
