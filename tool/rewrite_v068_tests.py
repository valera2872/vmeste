from pathlib import Path

path = Path('test/widget_test.dart')
text = path.read_text(encoding='utf-8')


def replace_test(source: str, start_name: str, next_name: str, replacement: str) -> str:
    start = source.index(f"  testWidgets('{start_name}")
    end = source.index(f"  testWidgets('{next_name}", start)
    return source[:start] + replacement.rstrip() + '\n\n' + source[end:]


TEST = r'''  testWidgets('onboarding opens with compact premium introductions', (
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

    final productTitle = tester.widget<Text>(
      find.byKey(const ValueKey('approved-product-title')),
    );
    expect(productTitle.style?.fontSize, lessThanOrEqualTo(26));
    expect(find.byKey(const ValueKey('product-intro-lead')), findsOneWidget);
    expect(
      find.textContaining('Превратите важную цель в конкретный следующий шаг'),
      findsOneWidget,
    );
    expect(find.byKey(const ValueKey('journey-visual')), findsOneWidget);
    expect(tester.takeException(), isNull);

    await tester.tap(find.byKey(const ValueKey('onboarding-next')));
    await tester.pumpAndSettle();

    final supportTitle = tester.widget<Text>(
      find.byKey(const ValueKey('approved-support-title')),
    );
    expect(supportTitle.style?.fontSize, lessThanOrEqualTo(26));
    expect(find.byKey(const ValueKey('support-intro-lead')), findsOneWidget);
    expect(
      find.text('Разным действиям может требоваться разная поддержка.'),
      findsOneWidget,
    );
    expect(find.byKey(const ValueKey('support-choice-grid')), findsOneWidget);
    expect(tester.takeException(), isNull);
  });'''

text = replace_test(
    text,
    'onboarding uses the approved clean visual direction',
    'add screen separates four kinds of intentions',
    TEST,
)

path.write_text(text, encoding='utf-8')
print('Applied v0.6.8 compact introduction tests')
