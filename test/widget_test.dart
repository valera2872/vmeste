import 'package:flutter_test/flutter_test.dart';
import 'package:vmeste_goal/main.dart';

void main() {
  testWidgets('first launch explains the product promise', (tester) async {
    final app = AppState();
    await tester.pumpWidget(VmesteApp(app: app));

    expect(find.text('Вместе к цели'), findsOneWidget);
    expect(find.text('Большая цель требует места в каждом дне.'), findsOneWidget);
    expect(find.text('Дальше'), findsOneWidget);
  });
}
