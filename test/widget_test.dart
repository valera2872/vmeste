import 'package:flutter_test/flutter_test.dart';
import 'package:vmeste_goal/main.dart';

void main() {
  testWidgets('first launch shows project promise', (tester) async {
    await tester.pumpWidget(const TogetherGoalApp());

    expect(find.text('Вместе к цели'), findsOneWidget);
    expect(find.text('Продолжить'), findsOneWidget);
  });
}
