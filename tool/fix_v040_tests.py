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
    expect(find.text('Пропустить'), findsOneWidget);
    expect(find.text('Как к вам обращаться?'), findsNothing);
  });

  testWidgets('add screen separates four kinds of intentions', (tester) async {
    SharedPreferences.setMockInitialValues({});
    final app = AppState()..onboarded = true;
    await tester.pumpWidget(VmesteApp(app: app));

    await tester.tap(find.text('Добавить'));
    await tester.pumpAndSettle();

    expect(find.text('Просто напомнить'), findsOneWidget);
    expect(find.text('Сделать дело'), findsOneWidget);
    expect(find.text('Повторять регулярно'), findsOneWidget);
    expect(find.text('Дойти до цели'), findsOneWidget);
  });

  testWidgets('reminder does not ask for duration', (tester) async {
    SharedPreferences.setMockInitialValues({});
    final app = AppState()..onboarded = true;

    await tester.pumpWidget(
      MaterialApp(home: ReminderEditor(app: app)),
    );

    expect(find.text('О чём напомнить?'), findsOneWidget);
    expect(find.text('День'), findsOneWidget);
    expect(find.text('Время'), findsOneWidget);
    expect(find.text('Использовать таймер'), findsNothing);
  });

  testWidgets('focus action can be saved without timer', (tester) async {
    SharedPreferences.setMockInitialValues({});
    final app = AppState()..onboarded = true;

    await tester.pumpWidget(
      MaterialApp(home: ActionEditor(app: app, goalDefault: false)),
    );

    expect(find.text('Использовать таймер'), findsOneWidget);
    await tester.tap(find.byType(Switch));
    await tester.pumpAndSettle();

    expect(
      find.text(
        'Действие останется в списке без обратного отсчёта. После выполнения вы отметите результат.',
      ),
      findsOneWidget,
    );
  });

  testWidgets('routine is clearly daily in first version', (tester) async {
    SharedPreferences.setMockInitialValues({});
    final app = AppState()..onboarded = true;

    await tester.pumpWidget(
      MaterialApp(home: RoutineEditor(app: app)),
    );

    expect(find.text('Что хотите повторять?'), findsOneWidget);
    expect(find.text('Каждый день'), findsOneWidget);
    expect(find.text('Использовать таймер'), findsOneWidget);
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
  });
}
''',
    encoding='utf-8',
)
