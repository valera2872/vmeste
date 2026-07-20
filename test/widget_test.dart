import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:vmeste_goal/main.dart';

void main() {
  testWidgets('onboarding has no personal data step', (tester) async {
    SharedPreferences.setMockInitialValues({});
    final app = AppState();
    await tester.pumpWidget(VmesteApp(app: app));

    expect(find.text('Вместе к цели'), findsOneWidget);
    expect(find.text('Пропустить'), findsOneWidget);
    expect(find.text('Как к вам обращаться?'), findsNothing);
    expect(find.text('Сколько вам лет?'), findsNothing);

    await tester.tap(find.text('Пропустить'));
    await tester.pumpAndSettle();

    expect(find.text('Чего вы хотите добиться?'), findsOneWidget);
    expect(find.text('Добавить главную цель'), findsOneWidget);
  });

  testWidgets('second intro screen leads directly to the goal', (tester) async {
    SharedPreferences.setMockInitialValues({});
    final app = AppState();
    await tester.pumpWidget(VmesteApp(app: app));

    await tester.tap(find.text('Дальше'));
    await tester.pumpAndSettle();

    expect(find.text('Для разных дел нужна разная помощь.'), findsOneWidget);
    expect(find.text('Перейти к цели'), findsOneWidget);
  });

  testWidgets('working together is visible for an active goal action', (
    tester,
  ) async {
    SharedPreferences.setMockInitialValues({});
    final app = AppState()
      ..onboarded = true
      ..goal = Goal('Закончить сайт', 'Сайт опубликован', 20, []);
    app.actions.add(
      ActionItem(
        id: '1',
        title: 'Написать первый экран',
        small: '',
        minutes: 15,
        support: Support.solo,
        goal: true,
      ),
    );

    await tester.pumpWidget(VmesteApp(app: app));

    expect(find.text('Действие для цели на сегодня'), findsOneWidget);
    expect(find.text('Написать первый экран'), findsOneWidget);
    expect(find.text('Вместе'), findsWidgets);
    expect(find.byIcon(Icons.people_alt_outlined), findsOneWidget);
  });
}
