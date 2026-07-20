from pathlib import Path

Path('test/widget_test.dart').write_text(
    '''import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:vmeste_goal/main.dart';

void main() {
  testWidgets('onboarding starts with the personal-method promise', (
    tester,
  ) async {
    SharedPreferences.setMockInitialValues({});
    final app = AppState();
    await tester.pumpWidget(VmesteApp(app: app));

    expect(find.text('У каждого свой способ достигать целей'), findsOneWidget);
    expect(find.text('Попробуйте разные способы поддержки'), findsOneWidget);
    expect(find.text('Определите, что помогает именно вам'), findsOneWidget);
    expect(find.text('Пропустить'), findsOneWidget);
    expect(find.text('Как к вам обращаться?'), findsNothing);
  });

  testWidgets('today asks for a goal action before choosing support', (
    tester,
  ) async {
    SharedPreferences.setMockInitialValues({});
    final app = AppState()
      ..onboarded = true
      ..goal = Goal('Закончить сайт', 'Сайт опубликован', 20, []);

    await tester.pumpWidget(VmesteApp(app: app));

    expect(find.text('Что вы сделаете сегодня?'), findsOneWidget);
    expect(find.text('Выбрать действие'), findsOneWidget);
    expect(find.text('Как хотите начать?'), findsNothing);
  });

  testWidgets('preselected together mode is not asked twice', (tester) async {
    SharedPreferences.setMockInitialValues({});
    final app = AppState()
      ..onboarded = true
      ..goal = Goal('Навести порядок', '', 20, []);

    await tester.pumpWidget(
      MaterialApp(
        home: ActionEditor(
          app: app,
          goalDefault: true,
          initialSupport: Support.together,
        ),
      ),
    );

    expect(find.text('Начать вместе'), findsWidgets);
    expect(find.text('Выбранный способ'), findsOneWidget);
    expect(find.text('Как хотите начать?'), findsNothing);
    expect(find.text('Самостоятельно'), findsNothing);
  });

  testWidgets('difficulty sheet contains scrollable concrete choices', (
    tester,
  ) async {
    final controller = ScrollController();
    addTearDown(controller.dispose);
    final item = ActionItem(
      id: '1',
      title: 'Убрать комнату',
      small: '',
      minutes: 15,
      support: Support.solo,
      goal: true,
    );

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: Blocker(item: item, scrollController: controller),
        ),
      ),
    );

    expect(find.text('Что сейчас мешает?'), findsOneWidget);
    expect(find.text('Не понимаю, что делать дальше'), findsOneWidget);
    expect(find.text('Действие оказалось слишком большим'), findsOneWidget);
    expect(find.text('Постоянно отвлекаюсь'), findsOneWidget);
  });
}
''',
    encoding='utf-8',
)
