from pathlib import Path

path = Path('test/widget_test.dart')
text = path.read_text(encoding='utf-8')

text = text.replace(
    """    expect(find.text('Найдите свой способ двигаться к цели'), findsOneWidget);
    expect(
      find.textContaining('С опорой на исследования о планировании действий'),
      findsOneWidget,
    );
    expect(find.textContaining('остальные дела можно быстро записать'), findsOneWidget);""",
    """    expect(find.text('Найдите свой способ двигаться к цели'), findsOneWidget);
    await tester.drag(
      find.byKey(const ValueKey('product-story-page')),
      const Offset(0, -340),
    );
    await tester.pumpAndSettle();
    expect(
      find.textContaining('С опорой на исследования о планировании действий'),
      findsOneWidget,
    );
    expect(find.textContaining('остальные дела можно быстро записать'), findsOneWidget);""",
    1,
)

text = text.replace(
    """    expect(find.text('Подберите поддержку под конкретное действие'), findsOneWidget);
    expect(find.text('Вместе с человеком'), findsOneWidget);
    expect(find.textContaining('аудио- или видеосвязи'), findsOneWidget);
    expect(find.textContaining('Не каждое дело должно становиться большой целью'), findsOneWidget);
    expect(find.byKey(const ValueKey('onboarding-create-goal')), findsOneWidget);""",
    """    expect(find.text('Подберите поддержку под конкретное действие'), findsOneWidget);
    expect(find.text('Вместе с человеком'), findsOneWidget);
    expect(find.textContaining('аудио- или видеосвязи'), findsOneWidget);
    await tester.drag(
      find.byKey(const ValueKey('support-story-page')),
      const Offset(0, -300),
    );
    await tester.pumpAndSettle();
    expect(find.textContaining('Не каждое дело должно становиться большой целью'), findsOneWidget);
    expect(find.byKey(const ValueKey('onboarding-create-goal')), findsOneWidget);""",
    1,
)

text = text.replace(
    """    expect(find.text('1 ч'), findsOneWidget);
    expect(find.text('1 ч 30 мин'), findsOneWidget);
    expect(find.text('2 ч'), findsOneWidget);
    expect(find.text('Запланировать'), findsOneWidget);""",
    """    expect(find.text('1 ч'), findsOneWidget);
    expect(find.text('1 ч 30 мин'), findsOneWidget);
    expect(find.text('2 ч'), findsOneWidget);
    await tester.scrollUntilVisible(
      find.text('Запланировать'),
      260,
      scrollable: find.byType(Scrollable).first,
    );
    expect(find.text('Запланировать'), findsOneWidget);""",
    1,
)

text = text.replace(
    """    expect(find.text('Что вы можете сделать первым?'), findsOneWidget);
    expect(find.text('Выбрать поддержку'), findsOneWidget);
    expect(find.text('Вместе с человеком'), findsNothing);

    await tester.enterText(find.byType(TextField).first, 'Составить описание проекта');
    await tester.pump();
    await tester.tap(find.byKey(const ValueKey('choose-support')));""",
    """    expect(find.text('Что вы можете сделать первым?'), findsOneWidget);
    expect(find.text('Вместе с человеком'), findsNothing);

    await tester.enterText(find.byType(TextField).first, 'Составить описание проекта');
    await tester.pump();
    await tester.scrollUntilVisible(
      find.byKey(const ValueKey('choose-support')),
      300,
      scrollable: find.byType(Scrollable).first,
    );
    expect(find.text('Выбрать поддержку'), findsOneWidget);
    await tester.tap(find.byKey(const ValueKey('choose-support')));""",
    1,
)

path.write_text(text, encoding='utf-8')
