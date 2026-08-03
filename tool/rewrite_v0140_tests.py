from pathlib import Path
import re

path = Path('test/widget_test.dart')
text = path.read_text(encoding='utf-8')


def test_block_containing(source: str, needle: str) -> tuple[int, int]:
    position = source.find(needle)
    if position < 0:
        raise SystemExit(f'test fragment not found: {needle}')
    start = source.rfind("\n  testWidgets(", 0, position)
    if start < 0:
        raise SystemExit(f'test start not found for: {needle}')
    start += 1
    match = re.search(r"\n  test(?:Widgets)?\(", source[position:])
    if match:
        end = position + match.start() + 1
    else:
        end = source.rindex('\n}')
    return start, end


FOCUS_TEST = r'''  testWidgets('goal starts with a 90-day focus choice', (tester) async {
    tester.view.physicalSize = const Size(360, 900);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    SharedPreferences.setMockInitialValues({});
    final app = AppState()..onboarded = true;

    await tester.pumpWidget(
      MaterialApp(home: GoalFocusEntryPage(app: app)),
    );
    await tester.pumpAndSettle();

    expect(
      find.text('Что вы хотите изменить за ближайшие 90 дней?'),
      findsOneWidget,
    );
    expect(find.byKey(const ValueKey('focus-quick-route')), findsOneWidget);
    expect(find.byKey(const ValueKey('focus-guided-route')), findsOneWidget);

    await tester.tap(find.byKey(const ValueKey('focus-quick-route')));
    await tester.pumpAndSettle();

    Finder field(String key) => find.descendant(
      of: find.byKey(ValueKey(key)),
      matching: find.byType(TextField),
    );

    await tester.enterText(field('focus-title-field'), 'Выпустить приложение');
    await tester.enterText(
      field('focus-result-field'),
      'Рабочая версия опубликована и доступна пользователям',
    );
    await tester.tap(find.byKey(const ValueKey('focus-wizard-next')));
    await tester.pumpAndSettle();

    await tester.enterText(
      field('focus-why-field'),
      'Хочу превратить идеи в работающий продукт',
    );
    await tester.tap(find.byKey(const ValueKey('focus-wizard-next')));
    await tester.pumpAndSettle();

    await tester.enterText(
      field('focus-influence-field'),
      'Закончить сборку, проверить и опубликовать её',
    );
    await tester.tap(find.byKey(const ValueKey('focus-wizard-next')));
    await tester.pumpAndSettle();

    await tester.enterText(
      field('focus-first-step-field'),
      'Проверить первый пользовательский сценарий',
    );
    await tester.tap(find.byKey(const ValueKey('focus-wizard-next')));
    await tester.pumpAndSettle();

    expect(find.byKey(const ValueKey('focus-confidence-slider')), findsOneWidget);
    await tester.tap(find.byKey(const ValueKey('focus-wizard-next')));
    await tester.pumpAndSettle();

    expect(find.text('ВАШ ПРЕДВАРИТЕЛЬНЫЙ ФОКУС'), findsOneWidget);
    expect(find.text('Выпустить приложение'), findsOneWidget);
    expect(
      find.text('Проверить первый пользовательский сценарий'),
      findsOneWidget,
    );

    await tester.tap(find.byKey(const ValueKey('start-focus-trial')));
    await tester.pumpAndSettle();

    expect(app.goal, isNotNull);
    expect(app.goal!.title, 'Выпустить приложение');
    expect(app.goal!.confidence, 7);
    expect(app.goal!.why, 'Хочу превратить идеи в работающий продукт');
    expect(app.actions.length, 1);
    expect(app.actions.first.goal, isTrue);
    expect(
      app.actions.first.title,
      'Проверить первый пользовательский сценарий',
    );
    expect(tester.takeException(), isNull);
  });'''

start, end = test_block_containing(text, 'GoalEditor(app: app)')
text = text[:start] + FOCUS_TEST.rstrip() + '\n\n' + text[end:]

# Keep copy assertions aligned with the 90-day focus language.
text = text.replace("find.text('ГЛАВНАЯ ЦЕЛЬ')", "find.text('ГЛАВНЫЙ ФОКУС · 90 ДНЕЙ')")
text = text.replace("find.text('Главная цель')", "find.text('Главный фокус')")

if 'goal focus metadata survives json' not in text:
    insert_at = text.rindex('\n}')
    MODEL_TEST = r'''
  test('goal focus metadata survives json', () {
    final original = Goal(
      'Выпустить приложение',
      'Рабочая версия опубликована',
      0,
      const [],
      why: 'Хочу создать самостоятельный продукт',
      influence: 'Закончить, проверить и опубликовать',
      firstStep: 'Показать первый сценарий трём людям',
      confidence: 8,
      guided: true,
      situation: 'Проект долго не двигался',
      outsideControl: 'Решения магазинов приложений',
      avoidance: 'Нужно завершать, а не улучшать бесконечно',
      protection: 'Не сталкиваться с оценкой пользователей',
      cost: 'Теряю время и мотивацию',
      whenWhere: 'Завтра утром за рабочим столом',
    );

    final restored = Goal.fromJson(original.toJson());
    expect(restored.title, original.title);
    expect(restored.why, original.why);
    expect(restored.influence, original.influence);
    expect(restored.firstStep, original.firstStep);
    expect(restored.confidence, 8);
    expect(restored.guided, isTrue);
    expect(restored.protection, original.protection);
    expect(restored.whenWhere, original.whenWhere);
    expect(restored.focusStartedAt, isA<DateTime>());
  });
'''
    text = text[:insert_at] + MODEL_TEST + text[insert_at:]

path.write_text(text, encoding='utf-8')
print('Applied v0.14.0 focus flow and persistence tests')