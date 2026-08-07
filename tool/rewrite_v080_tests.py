from pathlib import Path
import re

path = Path('test/widget_test.dart')
text = path.read_text(encoding='utf-8')

start_marker = "  testWidgets('goal workspace separates next steps from other work'"
start = text.find(start_marker)
if start < 0:
    raise SystemExit('Old goal workspace test not found')

match = re.search(r"\n  test(?:Widgets)?\(", text[start + len(start_marker):])
if match:
    end = start + len(start_marker) + match.start() + 1
else:
    end = text.rindex('\n}')

replacement = r'''  testWidgets('goal path makes the next action and support visible', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(360, 760);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    SharedPreferences.setMockInitialValues({});
    final app = AppState()
      ..onboarded = true
      ..goal = Goal(
        'Запустить полезное приложение',
        'Рабочая версия доступна первым пользователям',
        0,
        ['Прототип', 'Проверка', 'Публикация'],
      );
    app.actions.addAll([
      ActionItem(
        id: 'current-step',
        title: 'Проверить первый пользовательский сценарий',
        small: 'Открыть приложение и пройти только первый экран',
        minutes: 20,
        support: Support.ai,
        goal: true,
        kind: IntentKind.goalStep,
      ),
      ActionItem(
        id: 'next-step',
        title: 'Исправить найденные неточности',
        small: '',
        minutes: 15,
        support: Support.solo,
        goal: true,
        kind: IntentKind.goalStep,
      ),
      ActionItem(
        id: 'third-step',
        title: 'Подготовить описание для публикации',
        small: 'Написать только один абзац',
        minutes: 25,
        support: Support.report,
        goal: true,
        kind: IntentKind.goalStep,
      ),
    ]);
    app.history.addAll([
      HistoryItem(
        'Собрать прототип',
        20,
        Support.ai,
        ResultState.done,
        DateTime.now(),
        true,
        actionId: 'history-1',
        supportEffect: SupportEffect.yes,
      ),
      HistoryItem(
        'Проверить навигацию',
        15,
        Support.solo,
        ResultState.part,
        DateTime.now().subtract(const Duration(days: 1)),
        true,
        actionId: 'history-2',
        supportEffect: SupportEffect.partly,
      ),
    ]);

    await tester.pumpWidget(MaterialApp(home: GoalScreen(app: app)));
    await tester.pumpAndSettle();
    final scrollable = find.byType(Scrollable).first;

    expect(find.text('Путь к цели'), findsOneWidget);
    expect(find.byKey(const ValueKey('goal-path-header')), findsOneWidget);
    expect(find.byKey(const ValueKey('current-goal-step')), findsOneWidget);
    expect(find.text('СЕЙЧАС'), findsOneWidget);
    expect(find.text('Проверить первый пользовательский сценарий'), findsOneWidget);
    expect(find.text('МИНИМАЛЬНЫЙ ВАРИАНТ'), findsOneWidget);
    expect(find.byKey(const ValueKey('goal-start-button')), findsOneWidget);
    expect(find.byKey(const ValueKey('goal-difficulty-button')), findsOneWidget);
    expect(tester.takeException(), isNull);

    await tester.scrollUntilVisible(
      find.text('Дальше'),
      240,
      scrollable: scrollable,
    );
    await tester.pumpAndSettle();
    expect(find.text('Дальше'), findsOneWidget);
    expect(find.text('Исправить найденные неточности'), findsOneWidget);
    expect(tester.takeException(), isNull);

    await tester.scrollUntilVisible(
      find.byKey(const ValueKey('goal-insight-card')),
      260,
      scrollable: scrollable,
    );
    await tester.pumpAndSettle();
    expect(find.byKey(const ValueKey('goal-insight-card')), findsOneWidget);
    expect(find.text('ЧТО ПОМОГАЕТ ВАМ ДВИГАТЬСЯ'), findsOneWidget);
    expect(find.textContaining('цифров'), findsAtLeastNWidgets(1));

    await tester.scrollUntilVisible(
      find.text('Что уже сделано'),
      240,
      scrollable: scrollable,
    );
    await tester.pumpAndSettle();
    expect(find.text('Что уже сделано'), findsOneWidget);
    expect(find.text('Собрать прототип'), findsOneWidget);
    expect(tester.takeException(), isNull);

    await tester.scrollUntilVisible(
      find.byKey(const ValueKey('goal-difficulty-button')),
      -280,
      scrollable: scrollable,
    );
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const ValueKey('goal-difficulty-button')));
    await tester.pumpAndSettle();

    expect(find.text('Что мешает начать?'), findsOneWidget);
    expect(find.text('Вы уже начали'), findsNothing);
    expect(tester.takeException(), isNull);
  });'''

text = text[:start] + replacement.rstrip() + '\n\n' + text[end:]
path.write_text(text, encoding='utf-8')
print('Applied v0.8.0 goal path tests')
