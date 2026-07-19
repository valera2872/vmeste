import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:vmeste_goal/main.dart';

void main() {
  testWidgets('first launch explains the product promise', (tester) async {
    SharedPreferences.setMockInitialValues({});
    final app = AppState();
    await tester.pumpWidget(VmesteApp(app: app));

    expect(find.text('Вместе к цели'), findsOneWidget);
    expect(
      find.text('Одному бывает трудно довести важную цель до результата.'),
      findsOneWidget,
    );
    expect(find.text('Дальше'), findsOneWidget);
  });

  testWidgets('today screen offers quick help and simple task tracking',
      (tester) async {
    SharedPreferences.setMockInitialValues({});
    final app = AppState();
    app.onboarded = true;

    await tester.pumpWidget(VmesteApp(app: app));

    expect(find.text('Помочь мне начать'), findsOneWidget);
    expect(find.text('Добавить дело'), findsOneWidget);
  });
}
