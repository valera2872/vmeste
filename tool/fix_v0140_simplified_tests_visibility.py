from pathlib import Path

path = Path('test/widget_test.dart')
text = path.read_text(encoding='utf-8')

onboarding_old = '''    expect(find.byKey(const ValueKey('intro-action-support')), findsOneWidget);
    expect(
      find.textContaining('Подход опирается на исследования'),
      findsOneWidget,
    );'''
onboarding_new = '''    expect(find.byKey(const ValueKey('intro-action-support')), findsOneWidget);
    final secondPageScroll = find.descendant(
      of: find.byKey(const ValueKey('support-story-page')),
      matching: find.byType(Scrollable),
    );
    await tester.scrollUntilVisible(
      find.textContaining('Подход опирается на исследования'),
      180,
      scrollable: secondPageScroll,
    );
    expect(
      find.textContaining('Подход опирается на исследования'),
      findsOneWidget,
    );'''
if onboarding_old not in text:
    raise SystemExit('Onboarding research expectation anchor not found')
text = text.replace(onboarding_old, onboarding_new, 1)

goal_old = '''    expect(
      find.textContaining('90 дней относятся только к важной цели'),
      findsOneWidget,
    );

    await tester.tap(find.byKey(const ValueKey('focus-quick-route')));'''
goal_new = '''    final goalEntryScroll = find.byType(Scrollable);
    await tester.scrollUntilVisible(
      find.textContaining('90 дней относятся только к важной цели'),
      180,
      scrollable: goalEntryScroll,
    );
    expect(
      find.textContaining('90 дней относятся только к важной цели'),
      findsOneWidget,
    );

    await tester.scrollUntilVisible(
      find.byKey(const ValueKey('focus-quick-route')),
      -180,
      scrollable: goalEntryScroll,
    );
    await tester.tap(find.byKey(const ValueKey('focus-quick-route')));'''
if goal_old not in text:
    raise SystemExit('Important-goal horizon expectation anchor not found')
text = text.replace(goal_old, goal_new, 1)

path.write_text(text, encoding='utf-8')
print('Made simplified onboarding tests scroll to off-screen explanatory blocks')
