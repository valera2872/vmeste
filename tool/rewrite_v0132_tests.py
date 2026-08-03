from pathlib import Path
import re

path = Path('test/widget_test.dart')
text = path.read_text(encoding='utf-8')


def test_block(source: str, name: str) -> tuple[int, int, str]:
    marker = f"  testWidgets('{name}'"
    start = source.find(marker)
    if start < 0:
        raise SystemExit(f'test not found: {name}')
    match = re.search(r"\n  test(?:Widgets)?\(", source[start + len(marker):])
    if match:
        end = start + len(marker) + match.start() + 1
    else:
        end = source.rindex('\n}')
    return start, end, source[start:end]


def replace_test(name: str, replacement: str) -> None:
    global text
    start, end, _ = test_block(text, name)
    text = text[:start] + replacement.rstrip() + '\n\n' + text[end:]


def make_test_taller(name: str, height: int) -> None:
    global text
    start, end, block = test_block(text, name)
    changed = re.sub(
        r'physicalSize\s*=\s*const Size\((\d+),\s*\d+\)',
        lambda match: f'physicalSize = const Size({match.group(1)}, {height})',
        block,
        count=1,
    )
    if changed == block:
        raise SystemExit(f'physical size not changed for: {name}')
    text = text[:start] + changed + text[end:]


ONBOARDING_TEST = r'''  testWidgets('onboarding explains the expanded product concept', (
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

    expect(find.text('Важное бывает разным'), findsOneWidget);
    expect(find.byKey(const ValueKey('intro-area-goal')), findsOneWidget);
    expect(find.byKey(const ValueKey('intro-area-challenge')), findsOneWidget);
    expect(find.byKey(const ValueKey('intro-area-tasks')), findsOneWidget);
    expect(find.byKey(const ValueKey('intro-area-routines')), findsOneWidget);

    final firstPageScroll = find.descendant(
      of: find.byKey(const ValueKey('product-story-page')),
      matching: find.byType(Scrollable),
    );
    await tester.scrollUntilVisible(
      find.text(
        'Не нужно выбирать что-то одно. Добавляйте то, что актуально сейчас.',
      ),
      220,
      scrollable: firstPageScroll,
    );
    expect(
      find.text(
        'Не нужно выбирать что-то одно. Добавляйте то, что актуально сейчас.',
      ),
      findsOneWidget,
    );
    expect(find.text('ЦИФРОВОЙ ПОМОЩНИК'), findsNothing);
    expect(tester.takeException(), isNull);

    await tester.tap(find.byKey(const ValueKey('onboarding-next')));
    await tester.pumpAndSettle();

    expect(find.text('Помогаем перейти\nк действию'), findsOneWidget);
    expect(find.byKey(const ValueKey('intro-action-step')), findsOneWidget);
    expect(find.byKey(const ValueKey('intro-action-feasible')), findsOneWidget);

    final secondPageScroll = find.descendant(
      of: find.byKey(const ValueKey('support-story-page')),
      matching: find.byType(Scrollable),
    );
    await tester.scrollUntilVisible(
      find.byKey(const ValueKey('intro-action-support')),
      180,
      scrollable: secondPageScroll,
    );
    expect(find.byKey(const ValueKey('intro-action-support')), findsOneWidget);
    await tester.scrollUntilVisible(
      find.textContaining('Намерение  →  действие  →  поддержка'),
      180,
      scrollable: secondPageScroll,
    );
    expect(
      find.textContaining('Намерение  →  действие  →  поддержка'),
      findsOneWidget,
    );
    expect(find.text('С цифровым помощником'), findsNothing);
    expect(tester.takeException(), isNull);
  });'''

replace_test(
    'onboarding opens with compact premium introductions',
    ONBOARDING_TEST,
)


ASSISTANT_HIDDEN_TEST = r'''  testWidgets('digital assistant is temporarily hidden', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(360, 800);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    SharedPreferences.setMockInitialValues({});
    final app = AppState()
      ..onboarded = true
      ..startChoiceSeen = true
      ..goal = Goal(
        'Запустить приложение',
        'Получить первую рабочую версию',
        0,
        ['Прототип', 'Проверка'],
      );
    final action = ActionItem(
      id: 'assistant-action',
      title: 'Проверить пользовательский сценарий',
      small: '',
      minutes: 20,
      support: Support.ai,
      goal: true,
      kind: IntentKind.goalStep,
    );
    app.actions.add(action);

    await tester.pumpWidget(
      MaterialApp(
        home: ActionEditor(
          app: app,
          goalDefault: true,
          existing: action,
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.byKey(const ValueKey('digital-action-assistant')), findsNothing);
    expect(find.byKey(const ValueKey('use-first-physical-step')), findsNothing);
    expect(find.byKey(const ValueKey('use-generated-minimum')), findsNothing);
    expect(find.text('ЦИФРОВОЙ ПОМОЩНИК'), findsNothing);
    expect(find.text('С цифровым помощником'), findsNothing);
    expect(tester.takeException(), isNull);
  });'''

replace_test(
    'digital assistant applies first step and minimum',
    ASSISTANT_HIDDEN_TEST,
)

# v0.8 expected the goal insight to advertise the assistant. In v0.13.2 this
# is deliberately forbidden; the insight card remains, but the old label must
# be absent even when legacy in-memory fixtures still contain Support.ai.
old_goal_expectation = "    expect(find.textContaining('цифров'), findsAtLeastNWidgets(1));"
if old_goal_expectation not in text:
    raise SystemExit('legacy goal-path digital assistant expectation not found')
text = text.replace(
    old_goal_expectation,
    "    expect(find.textContaining('цифров'), findsNothing);",
    1,
)

# The overview tests target a narrow width, not a short viewport. A taller
# virtual phone prevents Flutter's test-only accessibility assertion from
# treating the much lower quick-capture microphone as an invisible node.
make_test_taller('today exposes all four contours above the detailed lists', 1400)


if 'today overview keeps full fixed labels on narrow phones' not in text:
    insert_at = text.rindex('\n}')
    NARROW_TEST = r'''
  testWidgets('today overview keeps full fixed labels on narrow phones', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(320, 1500);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    SharedPreferences.setMockInitialValues({});
    final app = AppState()
      ..onboarded = true
      ..startChoiceSeen = true;

    await tester.pumpWidget(
      MaterialApp(
        builder: (context, child) => MediaQuery(
          data: MediaQuery.of(context).copyWith(
            textScaler: const TextScaler.linear(1.2),
          ),
          child: child!,
        ),
        home: Today(app: app, onOpenGoal: () {}),
      ),
    );
    await tester.pumpAndSettle();

    for (final entry in <String, String>{
      'home-goal-entry': 'Важная цель',
      'home-challenge-entry': 'Челленджи',
      'home-tasks-entry': 'Дела',
      'home-routines-entry': 'Практики',
    }.entries) {
      final titleFinder = find.descendant(
        of: find.byKey(ValueKey(entry.key)),
        matching: find.text(entry.value),
      );
      expect(titleFinder, findsOneWidget);
      final title = tester.widget<Text>(titleFinder);
      expect(title.maxLines, 2);
      expect(title.softWrap, isTrue);
      expect(title.overflow, TextOverflow.visible);
    }

    expect(find.text('Важная ...'), findsNothing);
    expect(find.textContaining('Челленд...'), findsNothing);
    expect(tester.takeException(), isNull);
  });
'''
    text = text[:insert_at] + NARROW_TEST + text[insert_at:]

path.write_text(text, encoding='utf-8')
print('Applied v0.13.2 introduction, full-label and hidden-assistant tests')
