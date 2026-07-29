from pathlib import Path

path = Path('test/widget_test.dart')
text = path.read_text(encoding='utf-8')


def replace_test(source: str, start_name: str, next_name: str, replacement: str) -> str:
    start = source.index(f"  testWidgets('{start_name}")
    end = source.index(f"  testWidgets('{next_name}", start)
    return source[:start] + replacement.rstrip() + '\n\n' + source[end:]


ONBOARDING_TEST = r'''  testWidgets('onboarding uses the rebuilt visual story before goal creation', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(360, 760);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    SharedPreferences.setMockInitialValues({});
    final app = AppState();
    await tester.pumpWidget(VmesteApp(app: app));
    await tester.pumpAndSettle();

    expect(find.byKey(const ValueKey('onboarding-journey-hero')), findsOneWidget);
    expect(find.byKey(const ValueKey('journey-visual')), findsOneWidget);
    expect(find.text('Найдите свой способ двигаться к цели'), findsOneWidget);
    expect(find.text('Цель'), findsOneWidget);
    expect(find.text('Следующий шаг'), findsOneWidget);
    expect(find.text('Поддержка'), findsOneWidget);
    expect(find.byKey(const ValueKey('onboarding-next')), findsOneWidget);
    expect(tester.takeException(), isNull);

    final productScroll = find.descendant(
      of: find.byKey(const ValueKey('product-story-page')),
      matching: find.byType(Scrollable),
    );
    await tester.scrollUntilVisible(
      find.textContaining('С опорой на исследования о планировании действий'),
      220,
      scrollable: productScroll,
    );
    expect(find.textContaining('остальные дела можно быстро записать'), findsOneWidget);

    await tester.tap(find.byKey(const ValueKey('onboarding-next')));
    await tester.pumpAndSettle();

    expect(find.text('Подберите поддержку под конкретное действие'), findsOneWidget);
    expect(find.byKey(const ValueKey('support-orbit')), findsOneWidget);
    expect(find.text('КОНКРЕТНОЕ\nДЕЙСТВИЕ'), findsOneWidget);
    expect(find.byKey(const ValueKey('onboarding-create-goal')), findsOneWidget);
    expect(tester.takeException(), isNull);

    final supportScroll = find.descendant(
      of: find.byKey(const ValueKey('support-story-page')),
      matching: find.byType(Scrollable),
    );
    await tester.scrollUntilVisible(
      find.textContaining('аудио- или видеосвязи'),
      240,
      scrollable: supportScroll,
    );
    expect(find.text('Вместе с человеком'), findsOneWidget);
    expect(
      find.textContaining('Не каждое дело должно становиться большой целью'),
      findsOneWidget,
    );
    expect(tester.takeException(), isNull);
  });'''

text = replace_test(
    text,
    'onboarding explains the product and support before goal creation',
    'add screen separates four kinds of intentions',
    ONBOARDING_TEST,
)

text = text.replace(
    "expect(find.text('Что вы можете сделать первым?'), findsOneWidget);",
    "expect(find.text('Что вы можете сделать в первую очередь?'), findsOneWidget);\n"
    "    expect(find.byKey(const ValueKey('action-goal-context')), findsOneWidget);\n"
    "    expect(find.text('ГЛАВНАЯ ЦЕЛЬ'), findsOneWidget);\n"
    "    expect(find.text('Запустить проект'), findsOneWidget);\n"
    "    expect(find.text('Первое действие для этой цели'), findsOneWidget);",
    1,
)
text = text.replace(
    "expect(find.text('Что вы можете сделать первым?'), findsOneWidget);",
    "expect(find.text('Что вы можете сделать в первую очередь?'), findsOneWidget);",
)

path.write_text(text, encoding='utf-8')
print('Applied v0.6.6 visual and goal-context tests')
