from pathlib import Path

path = Path('test/widget_test.dart')
path.write_text(r'''import 'package:flutter/material.dart';
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
    expect(find.text('01'), findsOneWidget);
    expect(find.text('04'), findsOneWidget);
  });

  testWidgets('goal starts with only the goal name', (tester) async {
    SharedPreferences.setMockInitialValues({});
    final app = AppState()..onboarded = true;

    await tester.pumpWidget(MaterialApp(home: GoalEditor(app: app)));

    expect(find.text('Чего вы хотите добиться?'), findsOneWidget);
    expect(find.text('Уточнить результат и этапы'), findsOneWidget);
    expect(find.textContaining('Сколько времени удобно'), findsNothing);

    await tester.tap(find.text('Уточнить результат и этапы'));
    await tester.pumpAndSettle();

    expect(
      find.text('Что должно измениться или быть готово? Необязательно'),
      findsOneWidget,
    );
    expect(
      find.text('На какие этапы можно разделить цель? Необязательно'),
      findsOneWidget,
    );
  });

  testWidgets('goal card shows journey metrics without global duration', (
    tester,
  ) async {
    final app = AppState()
      ..onboarded = true
      ..goal = Goal('Доделать ремонт', '', 0, ['Ванная', 'Кухня']);

    await tester.pumpWidget(
      MaterialApp(home: Scaffold(body: GoalHero(app: app))),
    );

    expect(find.text('за один раз'), findsNothing);
    expect(find.text('завершено'), findsOneWidget);
    expect(find.text('в работе'), findsOneWidget);
    expect(find.text('этапов'), findsOneWidget);
  });

  testWidgets('today shows several active actions for one goal', (tester) async {
    SharedPreferences.setMockInitialValues({});
    final app = AppState()
      ..onboarded = true
      ..goal = Goal('Доделать ремонт', '', 0, ['Ванная']);
    app.actions.addAll([
      ActionItem(
        id: '1',
        title: 'Купить плитку',
        small: '',
        minutes: 0,
        support: Support.solo,
        goal: true,
        kind: IntentKind.goalStep,
        useTimer: false,
      ),
      ActionItem(
        id: '2',
        title: 'Подготовить стену',
        small: '',
        minutes: 60,
        support: Support.solo,
        goal: true,
        kind: IntentKind.goalStep,
      ),
    ]);

    await tester.pumpWidget(VmesteApp(app: app));

    expect(find.text('Купить плитку'), findsOneWidget);
    expect(find.text('Подготовить стену'), findsOneWidget);
    expect(find.text('Движение к цели'), findsOneWidget);
  });

  testWidgets('reminder does not ask for duration', (tester) async {
    SharedPreferences.setMockInitialValues({});
    final app = AppState()..onboarded = true;

    await tester.pumpWidget(MaterialApp(home: ReminderEditor(app: app)));

    expect(find.text('О чём напомнить?'), findsOneWidget);
    expect(find.text('День'), findsOneWidget);
    expect(find.text('Время'), findsOneWidget);
    expect(find.text('Использовать таймер'), findsNothing);
  });

  testWidgets('focus action supports long custom and scheduled work', (
    tester,
  ) async {
    SharedPreferences.setMockInitialValues({});
    final app = AppState()..onboarded = true;

    await tester.pumpWidget(
      MaterialApp(home: ActionEditor(app: app, goalDefault: false)),
    );

    expect(find.text('1 ч'), findsOneWidget);
    expect(find.text('1 ч 30 мин'), findsOneWidget);
    expect(find.text('2 ч'), findsOneWidget);
    expect(find.text('Своё'), findsOneWidget);
    expect(find.text('Запланировать действие'), findsOneWidget);

    await tester.tap(find.text('Своё'));
    await tester.pumpAndSettle();

    expect(find.text('Своя длительность в минутах'), findsOneWidget);
    expect(find.text('От 1 минуты до 12 часов'), findsOneWidget);
  });

  testWidgets('focus action can work to result without timer', (tester) async {
    SharedPreferences.setMockInitialValues({});
    final app = AppState()..onboarded = true;

    await tester.pumpWidget(
      MaterialApp(home: ActionEditor(app: app, goalDefault: false)),
    );

    await tester.tap(find.byType(Switch).first);
    await tester.pumpAndSettle();

    expect(find.text('Сохранить действие'), findsOneWidget);
    expect(find.text('10 мин'), findsNothing);
  });

  testWidgets('schedule sheet offers quick transfer choices', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(body: ActionScheduleSheet()),
      ),
    );

    expect(find.text('Когда вернуться к делу?'), findsOneWidget);
    expect(find.text('Сегодня позже'), findsOneWidget);
    expect(find.text('Завтра утром'), findsOneWidget);
    expect(find.text('Сохранить время'), findsOneWidget);
  });

  testWidgets('routine is clearly daily in first version', (tester) async {
    SharedPreferences.setMockInitialValues({});
    final app = AppState()..onboarded = true;

    await tester.pumpWidget(MaterialApp(home: RoutineEditor(app: app)));

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
''', encoding='utf-8')
print('Applied v0.5.0 tests')
