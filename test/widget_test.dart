import 'package:flutter_test/flutter_test.dart';
import 'package:vmeste_goal/main.dart';

void main() {
  testWidgets('first launch explains the product promise', (tester) async {
    final app = AppState();
    await tester.pumpWidget(VmesteApp(app: app));

    expect(find.text('Вместе к цели'), findsOneWidget);
    expect(find.text('Одному бывает трудно довести важную цель до результата.'), findsOneWidget);
    expect(find.text('Дальше'), findsOneWidget);
  });
}
