from pathlib import Path

Path('test/widget_test.dart').write_text(
    '''import 'package:flutter/material.dart';
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
      find.text('Бывает, что цель важна, но одному трудно начать и не бросить.'),
      findsOneWidget,
    );
  });

  testWidgets('today starts with the main goal', (tester) async {
    SharedPreferences.setMockInitialValues({});
    final app = AppState()..onboarded = true;
    await tester.pumpWidget(VmesteApp(app: app));

    expect(find.text('Чего вы хотите добиться?'), findsOneWidget);
    expect(find.text('Добавить главную цель'), findsOneWidget);
    expect(find.text('Добавить дело'), findsOneWidget);
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
''',
    encoding='utf-8',
)
