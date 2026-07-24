import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:vmeste_goal/main.dart';

void main() {
  testWidgets('onboarding is compact and can explain the product again', (
    tester,
  ) async {
    SharedPreferences.setMockInitialValues({});
    final app = AppState();
    await tester.pumpWidget(VmesteApp(app: app));

    expect(
      find.text('Видеть не весь путь, а то, что важно сейчас'),
      findsOneWidget,
    );
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
  });

  testWidgets('goal card is compact clickable and hides result copy', (
    tester,
  ) async {
    var opened = false;
    final app = AppState()
      ..onboarded = true
      ..goal = Goal('Доделать ремонт', 'Стена покрыта материалом', 0, [
        'Ванная',
      ]);
    app.actions.add(
      ActionItem(
        id: 'a1',
        title: 'Купить материал',
        small: '',
        minutes: 0,
        support: Support.solo,
        goal: true,
        kind: IntentKind.goalStep,
        useTimer: false,
      ),
    );

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: GoalHero(app: app, onTap: () => opened = true),
        ),
      ),
    );

    expect(find.text('Ближайший шаг: Купить материал'), findsOneWidget);
    expect(find.text('Стена покрыта материалом'), findsNothing);
    await tester.tap(find.text('Доделать ремонт'));
    expect(opened, isTrue);
  });

  testWidgets('today visually groups actions under the main goal', (
    tester,
  ) async {
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

    expect(find.text('ДВИЖЕНИЕ К ЦЕЛИ'), findsOneWidget);
    expect(find.textContaining('2 в работе'), findsWidgets);
    expect(find.text('Купить плитку'), findsWidgets);
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
    expect(find.text('Запланировать действие'), findsOneWidget);
  });

  testWidgets('schedule sheet offers quick transfer choices', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(home: Scaffold(body: ActionScheduleSheet())),
    );

    expect(find.text('Когда вернуться к делу?'), findsOneWidget);
    expect(find.text('Сегодня позже'), findsOneWidget);
    expect(find.text('Завтра утром'), findsOneWidget);
  });

  testWidgets('routine editor supports flexible rhythm and minimum', (
    tester,
  ) async {
    SharedPreferences.setMockInitialValues({});
    final app = AppState()..onboarded = true;
    await tester.pumpWidget(MaterialApp(home: RoutineEditor(app: app)));

    expect(find.text('Каждый день'), findsOneWidget);
    expect(find.text('Будни'), findsOneWidget);
    expect(find.text('Выходные'), findsOneWidget);
    expect(find.text('Выбрать дни'), findsOneWidget);
    expect(find.text('Раз в неделю'), findsOneWidget);
    await tester.scrollUntilVisible(
      find.text('Минимальный вариант'),
      350,
      scrollable: find.byType(Scrollable).first,
    );
    expect(find.text('Минимальный вариант'), findsOneWidget);
    expect(find.text('Напоминать'), findsOneWidget);
  });

  test('routine data survives json migration fields', () {
    final item = ActionItem(
      id: 'routine-1',
      title: 'Английский',
      small: 'Повторить десять слов',
      minutes: 20,
      minimumMinutes: 3,
      support: Support.solo,
      goal: false,
      kind: IntentKind.routine,
      routineSchedule: RoutineSchedule.selectedDays,
      weekdays: [1, 3, 5],
      weeklyTarget: 3,
    );

    final restored = ActionItem.fromJson(item.toJson());
    expect(restored.id, 'routine-1');
    expect(restored.routineSchedule, RoutineSchedule.selectedDays);
    expect(restored.weekdays, [1, 3, 5]);
    expect(restored.minimumMinutes, 3);
    expect(restored.createdAt, isA<DateTime>());
  });

  testWidgets('routine card distinguishes full and minimum progress', (
    tester,
  ) async {
    final app = AppState()..onboarded = true;
    final item = ActionItem(
      id: 'routine-2',
      title: 'Дыхательная практика',
      small: 'Три минуты',
      minutes: 20,
      minimumMinutes: 3,
      support: Support.solo,
      goal: false,
      kind: IntentKind.routine,
      routineSchedule: RoutineSchedule.timesPerWeek,
      weeklyTarget: 4,
    );
    app.actions.add(item);
    app.history.add(
      HistoryItem(
        item.title,
        3,
        Support.solo,
        ResultState.part,
        DateTime.now(),
        false,
        actionId: item.id,
        routineResult: RoutineResult.minimum,
      ),
    );

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: RoutineCard(app: app, item: item),
        ),
      ),
    );

    expect(find.text('1 из 4'), findsOneWidget);
    expect(find.text('Полностью: 0 · минимум: 1'), findsOneWidget);
    expect(find.textContaining('4 раза в неделю'), findsOneWidget);
  });

  testWidgets('difficulty sheet contains concrete choices', (tester) async {
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
  });

  testWidgets('voice field keeps long hints readable', (tester) async {
    final controller = TextEditingController();
    addTearDown(controller.dispose);

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: VoiceField(
            controller: controller,
            label: 'Минимальный вариант',
            hint:
                'Что можно сделать хотя бы частично, если сегодня трудно начать?',
            lines: 3,
          ),
        ),
      ),
    );

    final field = tester.widget<TextField>(find.byType(TextField));
    expect(field.decoration?.suffixIcon, isNull);
    expect(field.decoration?.hintMaxLines, 3);
    expect(find.text('Надиктовать'), findsOneWidget);
  });
}
