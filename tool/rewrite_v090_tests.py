from pathlib import Path

path = Path('test/widget_test.dart')
text = path.read_text(encoding='utf-8')

if "digital assistant applies first step and minimum" in text:
    print('v0.9.0 tests already applied')
    raise SystemExit(0)

# The assistant makes the editor taller, so an old test must not depend on a
# lazily built duration chip remaining in the widget tree after scrolling.
text = text.replace(
    "    expect(find.text('1 ч'), findsOneWidget);\n",
    "",
    1,
)

insert_at = text.rindex('\n}')

test = r'''
  testWidgets('digital assistant applies first step and minimum', (
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

    final scrollable = find.byType(Scrollable).first;
    await tester.scrollUntilVisible(
      find.byKey(const ValueKey('digital-action-assistant')),
      260,
      scrollable: scrollable,
    );
    await tester.pumpAndSettle();

    expect(find.byKey(const ValueKey('digital-action-assistant')), findsOneWidget);
    expect(find.text('ЦИФРОВОЙ ПОМОЩНИК'), findsOneWidget);
    expect(find.text('Первый физический шаг'), findsOneWidget);
    expect(find.text('РАЗЛОЖЕНИЕ НА ТРИ ЧАСТИ'), findsOneWidget);
    expect(find.text('Минимальный вариант'), findsAtLeastNWidgets(1));
    expect(
      find.text('Открыть нужный экран и проверить один основной сценарий'),
      findsAtLeastNWidgets(1),
    );
    expect(tester.takeException(), isNull);

    await tester.ensureVisible(
      find.byKey(const ValueKey('use-first-physical-step')),
    );
    await tester.tap(find.byKey(const ValueKey('use-first-physical-step')));
    await tester.pumpAndSettle();
    expect(
      action.title,
      'Проверить пользовательский сценарий',
      reason: 'Changes are saved only after the explicit save action.',
    );
    expect(tester.takeException(), isNull);

    await tester.ensureVisible(
      find.byKey(const ValueKey('use-generated-minimum')),
    );
    await tester.tap(find.byKey(const ValueKey('use-generated-minimum')));
    await tester.pumpAndSettle();
    expect(tester.takeException(), isNull);
  });
'''

text = text[:insert_at] + test + text[insert_at:]
path.write_text(text, encoding='utf-8')
print('Applied v0.9.0 digital assistant tests')
