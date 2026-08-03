from pathlib import Path
import re

main_path = Path('lib/main.dart')
test_path = Path('test/widget_test.dart')
pubspec_path = Path('pubspec.yaml')
text = main_path.read_text(encoding='utf-8')
tests = test_path.read_text(encoding='utf-8')
pubspec = pubspec_path.read_text(encoding='utf-8')


def remove_one_class(source: str, class_name: str) -> str:
    marker = f'class {class_name}'
    start = source.find(marker)
    if start < 0:
        raise SystemExit(f'cleanup class not found: {class_name}')
    next_class = re.search(r'^class\s+', source[start + len(marker):], flags=re.M)
    if next_class is None:
        raise SystemExit(f'next class not found after: {class_name}')
    end = start + len(marker) + next_class.start()
    return source[:start] + source[end:]


def replace_required(old: str, new: str, label: str) -> None:
    global text
    if old not in text:
        raise SystemExit(f'{label} not found')
    text = text.replace(old, new, 1)


# Remove obsolete v0.13.2 helper classes without deleting later product code.
for class_name in [
    '_JourneySteps extends StatelessWidget',
    '_JourneyStep extends StatelessWidget',
    '_DottedConnector extends StatelessWidget',
    '_AttentionCard extends StatelessWidget',
    '_ResearchNote extends StatelessWidget',
    '_SupportChoiceGrid extends StatelessWidget',
    '_ActionCenterCard extends StatelessWidget',
    '_OnboardingSupportCard extends StatelessWidget',
    '_QuietStatement extends StatelessWidget',
    '_DigitalActionAssistantCard extends StatelessWidget',
    '_AssistantSuggestion extends StatelessWidget',
]:
    text = remove_one_class(text, class_name)


# Remove every live UI route to the postponed digital assistant. Some blocks
# may already be removed by the preceding product-polish step, so these edits
# are intentionally idempotent; the final assertions remain strict.
for block in [
    r'''              SupportTile(
                type: Support.ai,
                selected: support == Support.ai,
                onTap: () => setState(() => chosen = Support.ai),
              ),
''',
    r'''          _SupportButton(
            icon: Icons.auto_awesome_rounded,
            label: 'С цифровым помощником',
            onPressed: () => _open(context, Support.ai),
          ),
          const SizedBox(height: 8),
''',
    r'''          _SimpleSupportCard(
            type: Support.ai,
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => ActionEditor(
                  app: app,
                  goalDefault: app.goal != null,
                  initialSupport: Support.ai,
                ),
              ),
            ),
          ),
''',
]:
    if block in text:
        text = text.replace(block, '', 1)

# Correctly filter any enum-driven picker. The previous regex was over-escaped
# and therefore matched nothing.
text = re.sub(
    r'Support\.values\s*\.map\(',
    'Support.values.where((value) => value != Support.ai).map(',
    text,
)
text = text.replace(
    'widget.app.setSupport(widget.item, Support.ai);',
    'widget.app.setSupport(widget.item, Support.solo);',
)

# Automatic recommendations must not silently recreate Support.ai.
support_logic_start = text.index('class SupportLogic {')
support_logic_end = text.index(
    '  static List<String> steps(String task) {',
    support_logic_start,
)
support_logic = text[support_logic_start:support_logic_end]
support_logic = support_logic.replace('Support.ai,', 'Support.solo,')
support_logic = support_logic.replace(
    'Цифровой помощник предложит один понятный первый шаг.',
    'Приложение поможет определить один понятный первый шаг.',
)
text = text[:support_logic_start] + support_logic + text[support_logic_end:]

# Migrate old saved actions from ai to solo while preserving all other data.
replace_required(
    r'''      support: Support.values.firstWhere(
        (e) => e.name == j['support'],
        orElse: () => Support.solo,
      ),''',
    r'''      support: j['support'] == Support.ai.name
          ? Support.solo
          : Support.values.firstWhere(
              (e) => e.name == j['support'],
              orElse: () => Support.solo,
            ),''',
    'ActionItem legacy support parser',
)
replace_required(
    "Support.ai => 'С цифровым помощником',",
    "Support.ai => 'Самостоятельно',",
    'visible Support.ai label',
)

# Editing an action opened from "Путь к цели" must return one route back to the
# goal path, rather than clearing the stack to the root "Сегодня" screen.
replace_required(
    r'''    if (scheduleAction) {
      await NotificationService.instance.schedule(action);
      if (!mounted) return;
      Navigator.popUntil(context, (route) => route.isFirst);
      return;
    }''',
    r'''    if (scheduleAction) {
      await NotificationService.instance.schedule(action);
      if (!mounted) return;
      if (existing != null) {
        Navigator.pop(context);
      } else {
        Navigator.popUntil(context, (route) => route.isFirst);
      }
      return;
    }''',
    'scheduled action return block',
)
replace_required(
    r'''    if (existing != null || !useTimer) {
      Navigator.popUntil(context, (route) => route.isFirst);
      return;
    }''',
    r'''    if (existing != null) {
      Navigator.pop(context);
      return;
    }

    if (!useTimer) {
      Navigator.popUntil(context, (route) => route.isFirst);
      return;
    }''',
    'editing action return block',
)


# Regression coverage for the exact mobile scenario reported by the tester.
if 'digital assistant stays absent from action support choices' not in tests:
    insert_at = tests.rindex('\n}')
    regression_tests = r'''
  testWidgets('digital assistant stays absent from action support choices', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(360, 1100);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    SharedPreferences.setMockInitialValues({});
    final app = AppState()
      ..onboarded = true
      ..startChoiceSeen = true
      ..goal = Goal(
        'Запустить приложение',
        'Получить рабочую версию',
        0,
        ['Проверка'],
      );

    final legacy = ActionItem.fromJson({
      'title': 'Старое действие',
      'support': 'ai',
    });
    expect(legacy.support, Support.solo);
    expect(supportName(Support.ai), 'Самостоятельно');
    expect(SupportLogic.recommend('Собрать проект').$1, Support.solo);

    await tester.pumpWidget(
      MaterialApp(
        home: ActionEditor(
          app: app,
          goalDefault: true,
          initialTitle: 'Собрать проект',
        ),
      ),
    );
    await tester.pumpAndSettle();

    await tester.tap(find.text('Другие варианты поддержки'));
    await tester.pumpAndSettle();

    expect(find.text('С цифровым помощником'), findsNothing);
    expect(find.text('Отправить результат'), findsOneWidget);
    expect(find.text('С куратором'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('support screen does not expose digital assistant', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(360, 1100);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    SharedPreferences.setMockInitialValues({});
    final app = AppState()
      ..onboarded = true
      ..startChoiceSeen = true;

    await tester.pumpWidget(MaterialApp(home: SupportScreen(app: app)));
    await tester.pumpAndSettle();

    expect(find.text('С цифровым помощником'), findsNothing);
    expect(find.text('Отправить результат'), findsOneWidget);
    expect(find.text('С куратором'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('editing a goal action returns to the goal path', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(360, 1100);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    SharedPreferences.setMockInitialValues({});
    final app = AppState()
      ..onboarded = true
      ..startChoiceSeen = true
      ..goal = Goal(
        'Запустить приложение',
        'Получить рабочую версию',
        0,
        ['Проверка'],
      );
    final action = ActionItem(
      id: 'goal-action-return-test',
      title: 'Проверить сценарий',
      small: '',
      minutes: 15,
      support: Support.solo,
      goal: true,
      kind: IntentKind.goalStep,
    );
    app.actions.add(action);

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          key: const ValueKey('today-root-test'),
          body: Builder(
            builder: (rootContext) => FilledButton(
              key: const ValueKey('open-goal-path-test'),
              onPressed: () => Navigator.push(
                rootContext,
                MaterialPageRoute(
                  builder: (goalContext) => Scaffold(
                    key: const ValueKey('goal-path-test'),
                    body: FilledButton(
                      key: const ValueKey('edit-goal-action-test'),
                      onPressed: () => Navigator.push(
                        goalContext,
                        MaterialPageRoute(
                          builder: (_) => ActionEditor(
                            app: app,
                            goalDefault: true,
                            existing: action,
                          ),
                        ),
                      ),
                      child: const Text('Изменить действие'),
                    ),
                  ),
                ),
              ),
              child: const Text('Открыть путь к цели'),
            ),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    await tester.tap(find.byKey(const ValueKey('open-goal-path-test')));
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const ValueKey('edit-goal-action-test')));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Сохранить изменения'));
    await tester.pumpAndSettle();

    expect(find.byKey(const ValueKey('goal-path-test')), findsOneWidget);
    expect(find.byKey(const ValueKey('today-root-test')), findsNothing);
    expect(tester.takeException(), isNull);
  });
'''
    tests = tests[:insert_at] + regression_tests + tests[insert_at:]


# Fail the build if any postponed-assistant route, label or default returns.
for forbidden in [
    "label: 'С цифровым помощником'",
    'type: Support.ai,',
    'initialSupport: Support.ai',
    'chosen = Support.ai',
    '_open(context, Support.ai)',
    'widget.app.setSupport(widget.item, Support.ai)',
    "Support.ai => 'С цифровым помощником'",
]:
    if forbidden in text:
        raise SystemExit(f'hidden assistant path remains: {forbidden}')

if re.search(r'Support\.values\s*\.map\(', text):
    raise SystemExit('unfiltered Support.values picker remains')
if 'Support.ai,' in text[support_logic_start:support_logic_end]:
    raise SystemExit('SupportLogic still recommends the hidden assistant')

if 'version: 0.13.2+31' not in pubspec:
    raise SystemExit('Expected v0.13.2+31 version not found')
pubspec = pubspec.replace('version: 0.13.2+31', 'version: 0.13.2+32', 1)

main_path.write_text(text, encoding='utf-8')
test_path.write_text(tests, encoding='utf-8')
pubspec_path.write_text(pubspec, encoding='utf-8')
print('Removed all assistant paths, preserved goal navigation and bumped build 32')
