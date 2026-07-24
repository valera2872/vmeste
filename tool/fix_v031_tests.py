from pathlib import Path

Path('test/widget_test.dart').write_text(
    '''import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:vmeste_goal/main.dart';

void main() {
  testWidgets('first launch explains the product promise', (tester) async {
    SharedPreferences.setMockInitialValues({});
    final app = AppState();
    await tester.pumpWidget(VmesteApp(app: app));

    expect(find.text('Вместе к цели'), findsOneWidget);
    expect(
      find.text('Бывает, что цель важна, но одному трудно начать и не бросить.'),
      findsOneWidget,
    );
    expect(find.text('Дальше'), findsOneWidget);
  });

  testWidgets('today screen offers quick help and simple task tracking', (
    tester,
  ) async {
    SharedPreferences.setMockInitialValues({});
    final app = AppState();
    app.onboarded = true;

    await tester.pumpWidget(VmesteApp(app: app));

    expect(find.text('Разобраться, что мешает'), findsOneWidget);
    expect(find.text('Добавить дело'), findsOneWidget);
    expect(find.byTooltip('Как это работает'), findsOneWidget);
  });
}
''',
    encoding='utf-8',
)
