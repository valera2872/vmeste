from pathlib import Path
import re

path = Path('test/widget_test.dart')
text = path.read_text(encoding='utf-8')


def test_block(source: str, name: str) -> tuple[int, int]:
    marker = f"  testWidgets('{name}'"
    start = source.find(marker)
    if start < 0:
        raise SystemExit(f'test not found: {name}')
    match = re.search(r"\n  test(?:Widgets)?\(", source[start + len(marker):])
    if match:
        end = start + len(marker) + match.start() + 1
    else:
        end = source.rindex('\n}')
    return start, end


def replace_test(name: str, replacement: str) -> None:
    global text
    start, end = test_block(text, name)
    text = text[:start] + replacement.rstrip() + '\n\n' + text[end:]


ONBOARDING_TEST = r'''  testWidgets('onboarding explains the expanded product concept', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(360, 900);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    SharedPreferences.setMockInitialValues({});
    final app = AppState();
    await tester.pumpWidget(VmesteApp(app: app));
    await tester.pumpAndSettle();

    expect(
      find.text(
        'Хотите чего-то добиться, но не получается начать или продолжать?',
      ),
      findsOneWidget,
    );
    expect(find.byKey(const ValueKey('intro-area-goal')), findsOneWidget);
    expect(find.byKey(const ValueKey('intro-area-challenge')), findsOneWidget);
    expect(find.byKey(const ValueKey('intro-area-tasks')), findsOneWidget);
    expect(find.byKey(const ValueKey('intro-area-routines')), findsOneWidget);
    expect(find.text('1 из 2'), findsNothing);
    expect(find.text('2 из 2'), findsNothing);
    expect(find.text('ЦИФРОВОЙ ПОМОЩНИК'), findsNothing);

    await tester.tap(find.byKey(const ValueKey('onboarding-next')));
    await tester.pumpAndSettle();

    expect(find.text('Помогаем перейти\nк действию'), findsOneWidget);
    expect(find.byKey(const ValueKey('intro-action-step')), findsOneWidget);
    expect(find.byKey(const ValueKey('intro-action-feasible')), findsOneWidget);
    expect(find.byKey(const ValueKey('intro-action-support')), findsOneWidget);
    expect(
      find.textContaining('Подход опирается на исследования'),
      findsOneWidget,
    );
    expect(tester.takeException(), isNull);
  });'''

replace_test('onboarding explains the expanded product concept', ONBOARDING_TEST)

START_TEST = r'''  testWidgets('start choice keeps several contours active together', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(390, 900);
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
      find.textContaining('сразу поможет создать первый элемент'),
      findsOneWidget,
    );

    await tester.ensureVisible(
      find.byKey(const ValueKey('start-area-tasks')),
    );
    await tester.tap(find.byKey(const ValueKey('start-area-tasks')));
    await tester.pump();
    await tester.tap(find.byKey(const ValueKey('continue-start-choice')));
    await tester.pumpAndSettle();

    expect(find.byType(ActionEditor), findsOneWidget);
    expect(app.startChoiceSeen, isFalse);
    expect(tester.takeException(), isNull);
  });'''

replace_test('start choice keeps several contours active together', START_TEST)

FOCUS_ENTRY_TEST = r'''  testWidgets('goal starts with a 90-day focus choice', (tester) async {
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

    expect(find.text('Как сформулируем важную цель?'), findsOneWidget);
    expect(find.byKey(const ValueKey('focus-quick-route')), findsOneWidget);
    expect(find.byKey(const ValueKey('focus-guided-route')), findsOneWidget);
    expect(
      find.textContaining('90 дней относятся только к важной цели'),
      findsOneWidget,
    );

    await tester.tap(find.byKey(const ValueKey('focus-quick-route')));
    await tester.pumpAndSettle();

    expect(
      find.text('Как коротко назовём важную цель?'),
      findsOneWidget,
    );
    expect(find.byKey(const ValueKey('focus-title-field')), findsOneWidget);
    expect(find.text('1 / 5'), findsOneWidget);
    expect(find.textContaining('предваритель'), findsNothing);
    expect(tester.takeException(), isNull);
  });'''

replace_test('goal starts with a 90-day focus choice', FOCUS_ENTRY_TEST)

REVIEW_TEST = r'''  testWidgets('focus review creates the first real action', (tester) async {
    tester.view.physicalSize = const Size(360, 1100);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    SharedPreferences.setMockInitialValues({});
    final app = AppState()..onboarded = true;

    await tester.pumpWidget(
      MaterialApp(
        home: GoalFocusReviewPage(
          app: app,
          guided: false,
          title: 'Выпустить приложение',
          result: 'Рабочая версия опубликована и доступна пользователям',
          why: 'Хочу превратить идеи в работающий продукт',
          influence: '',
          firstStep: 'Проверить первый пользовательский сценарий',
          confidence: 0,
          situation: '',
          outsideControl: '',
          avoidance: '',
          protection: '',
          cost: '',
          whenWhere: 'Завтра после завтрака',
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('ВАША ВАЖНАЯ ЦЕЛЬ'), findsOneWidget);
    expect(find.text('Выпустить приложение'), findsOneWidget);
    expect(find.byKey(const ValueKey('save-important-goal')), findsOneWidget);
    expect(find.textContaining('предваритель'), findsNothing);
    expect(find.textContaining('7 дней'), findsNothing);

    await tester.tap(find.byKey(const ValueKey('save-important-goal')));
    await tester.pumpAndSettle();

    expect(app.goal, isNotNull);
    expect(app.goal!.title, 'Выпустить приложение');
    expect(app.goal!.confidence, 0);
    expect(app.goal!.why, 'Хочу превратить идеи в работающий продукт');
    expect(app.actions.length, 1);
    expect(app.actions.first.goal, isTrue);
    expect(
      app.actions.first.title,
      'Проверить первый пользовательский сценарий',
    );
    expect(tester.takeException(), isNull);
  });'''

replace_test('focus review creates the first real action', REVIEW_TEST)

text = text.replace(
    "find.text('ГЛАВНЫЙ ФОКУС · 90 ДНЕЙ')",
    "find.text('ВАЖНАЯ ЦЕЛЬ')",
)
text = text.replace("find.text('Главный фокус')", "find.text('Важная цель')")

for required in [
    "find.text('1 из 2'), findsNothing",
    "find.byType(ActionEditor)",
    "ValueKey('save-important-goal')",
    "find.text('1 / 5')",
]:
    if required not in text:
        raise SystemExit(f'updated test fragment missing: {required}')

path.write_text(text, encoding='utf-8')
print('Updated tests for executable onboarding and simplified important goal')
