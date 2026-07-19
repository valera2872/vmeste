import 'dart:async';

import 'package:flutter/material.dart';

void main() => runApp(const TogetherGoalApp());

class TogetherGoalApp extends StatefulWidget {
  const TogetherGoalApp({super.key});

  @override
  State<TogetherGoalApp> createState() => _TogetherGoalAppState();
}

class _TogetherGoalAppState extends State<TogetherGoalApp> {
  final AppController controller = AppController();

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: controller,
      builder: (context, _) {
        return MaterialApp(
          debugShowCheckedModeBanner: false,
          title: 'Вместе к цели',
          theme: ThemeData(
            useMaterial3: true,
            colorScheme: ColorScheme.fromSeed(
              seedColor: const Color(0xFF4E7D70),
            ),
            scaffoldBackgroundColor: const Color(0xFFF7F8F5),
            inputDecorationTheme: InputDecorationTheme(
              filled: true,
              fillColor: Colors.white,
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(18),
              ),
            ),
            filledButtonTheme: FilledButtonThemeData(
              style: FilledButton.styleFrom(
                minimumSize: const Size.fromHeight(54),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(18),
                ),
              ),
            ),
          ),
          home: controller.onboardingDone
              ? HomeScreen(controller: controller)
              : OnboardingScreen(controller: controller),
        );
      },
    );
  }
}

enum AgeGroup { child, youngTeen, olderTeen, adult }
enum SupportMode { solo, digital }
enum SessionOutcome { full, minimum, started, missed }

class GoalPlan {
  GoalPlan({
    required this.result,
    required this.regularStep,
    required this.minimumStep,
    required this.duration,
  });

  final String result;
  final String regularStep;
  final String minimumStep;
  final int duration;
}

class SessionRecord {
  SessionRecord({
    required this.task,
    required this.outcome,
    required this.duration,
    required this.createdAt,
  });

  final String task;
  final SessionOutcome outcome;
  final int duration;
  final DateTime createdAt;
}

class AppController extends ChangeNotifier {
  bool onboardingDone = false;
  AgeGroup ageGroup = AgeGroup.adult;
  GoalPlan? activeGoal;
  final List<SessionRecord> history = [];

  void setAge(AgeGroup value) {
    ageGroup = value;
    notifyListeners();
  }

  void finishOnboarding() {
    onboardingDone = true;
    notifyListeners();
  }

  void saveGoal(GoalPlan value) {
    activeGoal = value;
    notifyListeners();
  }

  void addRecord(SessionRecord value) {
    history.insert(0, value);
    notifyListeners();
  }

  String get homeQuestion {
    switch (ageGroup) {
      case AgeGroup.child:
        return 'Что ты хочешь сдвинуть с места сегодня?';
      case AgeGroup.youngTeen:
        return 'Что ты давно хочешь начать, но откладываешь?';
      case AgeGroup.olderTeen:
        return 'Какое важное дело стоит начать сегодня?';
      case AgeGroup.adult:
        return 'Что вы хотите сдвинуть с места сегодня?';
    }
  }
}

class OnboardingScreen extends StatelessWidget {
  const OnboardingScreen({required this.controller, super.key});

  final AppController controller;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(24),
          children: [
            const SizedBox(height: 24),
            const Icon(Icons.route_rounded, size: 60, color: Color(0xFF4E7D70)),
            const SizedBox(height: 28),
            const Text(
              'Вместе к цели',
              style: TextStyle(fontSize: 36, fontWeight: FontWeight.w800),
            ),
            const SizedBox(height: 16),
            const Text(
              'Не ждите идеальной мотивации. Выберите один шаг, начните и сохраните движение к важному результату.',
              style: TextStyle(fontSize: 18, height: 1.45),
            ),
            const SizedBox(height: 28),
            const ProductPoint(
              icon: Icons.adjust_rounded,
              text: 'Одно конкретное действие вместо большой абстрактной цели.',
            ),
            const ProductPoint(
              icon: Icons.schedule_rounded,
              text: 'Короткая сессия, которую реально начать.',
            ),
            const ProductPoint(
              icon: Icons.refresh_rounded,
              text: 'Возвращение после остановки без обнуления и стыда.',
            ),
            const SizedBox(height: 22),
            const Text(
              'Как лучше обращаться к вам?',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 8),
            const Text(
              'Возраст нужен только для языка и примеров. Он не ограничивает доступ.',
            ),
            const SizedBox(height: 14),
            Wrap(
              spacing: 10,
              runSpacing: 10,
              children: [
                ageChip(controller, '10–12', AgeGroup.child),
                ageChip(controller, '13–15', AgeGroup.youngTeen),
                ageChip(controller, '16–17', AgeGroup.olderTeen),
                ageChip(controller, '18+', AgeGroup.adult),
              ],
            ),
            const SizedBox(height: 28),
            FilledButton(
              onPressed: controller.finishOnboarding,
              child: const Text('Продолжить'),
            ),
          ],
        ),
      ),
    );
  }

  Widget ageChip(AppController c, String label, AgeGroup value) {
    return ChoiceChip(
      label: Text(label),
      selected: c.ageGroup == value,
      onSelected: (_) => c.setAge(value),
    );
  }
}

class ProductPoint extends StatelessWidget {
  const ProductPoint({required this.icon, required this.text, super.key});

  final IconData icon;
  final String text;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 14),
      child: Row(
        children: [
          Icon(icon, color: const Color(0xFF4E7D70)),
          const SizedBox(width: 12),
          Expanded(child: Text(text)),
        ],
      ),
    );
  }
}

class HomeScreen extends StatelessWidget {
  const HomeScreen({required this.controller, super.key});

  final AppController controller;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Вместе к цели')),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(18, 8, 18, 32),
        children: [
          Text(
            controller.homeQuestion,
            style: const TextStyle(fontSize: 28, fontWeight: FontWeight.w800),
          ),
          const SizedBox(height: 20),
          FilledButton.icon(
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => QuickStartScreen(controller: controller),
              ),
            ),
            icon: const Icon(Icons.play_arrow_rounded),
            label: const Padding(
              padding: EdgeInsets.symmetric(vertical: 8),
              child: Text('Помочь мне начать сейчас'),
            ),
          ),
          const SizedBox(height: 12),
          OutlinedButton.icon(
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => GoalEditorScreen(controller: controller),
              ),
            ),
            icon: const Icon(Icons.flag_rounded),
            label: Text(controller.activeGoal == null ? 'Создать цель' : 'Изменить цель'),
          ),
          const SizedBox(height: 12),
          OutlinedButton.icon(
            onPressed: () => showModalBottomSheet(
              context: context,
              showDragHandle: true,
              builder: (_) => const Padding(
                padding: EdgeInsets.all(24),
                child: Text(
                  'Совместный старт со знакомым человеком появится в версии 0.2: приглашение по ссылке, статусы готовности, страховка от неявки и реакция «Ты помог мне начать».',
                  style: TextStyle(fontSize: 17, height: 1.4),
                ),
              ),
            ),
            icon: const Icon(Icons.people_alt_rounded),
            label: const Text('Меня пригласили'),
          ),
          if (controller.activeGoal != null) ...[
            const SizedBox(height: 28),
            const Text('Моя цель', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700)),
            const SizedBox(height: 10),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(18),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      controller.activeGoal!.result,
                      style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w800),
                    ),
                    const SizedBox(height: 12),
                    Text('Обычный шаг: ${controller.activeGoal!.regularStep}'),
                    const SizedBox(height: 6),
                    Text('Минимум: ${controller.activeGoal!.minimumStep}'),
                    const SizedBox(height: 14),
                    FilledButton(
                      onPressed: () => Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (_) => SessionScreen(
                            controller: controller,
                            task: controller.activeGoal!.regularStep,
                            minimumTask: controller.activeGoal!.minimumStep,
                            duration: controller.activeGoal!.duration,
                            support: SupportMode.digital,
                          ),
                        ),
                      ),
                      child: const Text('Начать сегодняшний шаг'),
                    ),
                  ],
                ),
              ),
            ),
          ],
          const SizedBox(height: 28),
          const Text('Последние действия', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700)),
          const SizedBox(height: 10),
          if (controller.history.isEmpty)
            const Card(
              child: Padding(
                padding: EdgeInsets.all(18),
                child: Text('Здесь появятся реальные действия, минимальные шаги и возвращения.'),
              ),
            )
          else
            ...controller.history.take(5).map(
              (record) => Card(
                child: ListTile(
                  leading: Icon(outcomeIcon(record.outcome)),
                  title: Text(record.task),
                  subtitle: Text('${outcomeLabel(record.outcome)} · ${record.duration} минут'),
                ),
              ),
            ),
        ],
      ),
    );
  }
}

class QuickStartScreen extends StatefulWidget {
  const QuickStartScreen({required this.controller, super.key});

  final AppController controller;

  @override
  State<QuickStartScreen> createState() => _QuickStartScreenState();
}

class _QuickStartScreenState extends State<QuickStartScreen> {
  final task = TextEditingController();
  final minimum = TextEditingController();
  int duration = 10;
  SupportMode support = SupportMode.digital;

  @override
  void dispose() {
    task.dispose();
    minimum.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Начать сейчас')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          const Text('Какое дело нужно сдвинуть?', style: TextStyle(fontSize: 27, fontWeight: FontWeight.w800)),
          const SizedBox(height: 10),
          const Text('Назовите результат, который можно увидеть через несколько минут.'),
          const SizedBox(height: 18),
          TextField(
            controller: task,
            maxLines: 3,
            decoration: const InputDecoration(
              labelText: 'Что вы сделаете?',
              hintText: 'Например: разобрать одну папку с документами',
            ),
            onChanged: (_) => setState(() {}),
          ),
          const SizedBox(height: 14),
          TextField(
            controller: minimum,
            decoration: const InputDecoration(
              labelText: 'Минимальный шаг — необязательно',
              hintText: 'Например: убрать 5 файлов',
            ),
          ),
          const SizedBox(height: 24),
          const Text('Сколько времени реально выделить?', style: TextStyle(fontSize: 19, fontWeight: FontWeight.w700)),
          const SizedBox(height: 10),
          Wrap(
            spacing: 8,
            children: [5, 10, 15, 25].map((value) {
              return ChoiceChip(
                label: Text('$value минут'),
                selected: duration == value,
                onSelected: (_) => setState(() => duration = value),
              );
            }).toList(),
          ),
          const SizedBox(height: 24),
          const Text('Как начнём?', style: TextStyle(fontSize: 19, fontWeight: FontWeight.w700)),
          RadioListTile<SupportMode>(
            value: SupportMode.digital,
            groupValue: support,
            onChanged: (value) => setState(() => support = value!),
            title: const Text('С цифровым компаньоном'),
            subtitle: const Text('Короткая подготовка и помощь при затруднении.'),
          ),
          RadioListTile<SupportMode>(
            value: SupportMode.solo,
            groupValue: support,
            onChanged: (value) => setState(() => support = value!),
            title: const Text('Самостоятельно'),
            subtitle: const Text('Только задача, таймер и честный результат.'),
          ),
          const ListTile(
            enabled: false,
            leading: Icon(Icons.people_alt_outlined),
            title: Text('С человеком'),
            subtitle: Text('Появится в версии 0.2.'),
          ),
          const SizedBox(height: 18),
          FilledButton(
            onPressed: task.text.trim().isEmpty
                ? null
                : () => Navigator.pushReplacement(
                      context,
                      MaterialPageRoute(
                        builder: (_) => SessionScreen(
                          controller: widget.controller,
                          task: task.text.trim(),
                          minimumTask: minimum.text.trim().isEmpty
                              ? 'Сделать хотя бы 2 минуты'
                              : minimum.text.trim(),
                          duration: duration,
                          support: support,
                        ),
                      ),
                    ),
            child: const Text('Перейти к старту'),
          ),
        ],
      ),
    );
  }
}

class GoalEditorScreen extends StatefulWidget {
  const GoalEditorScreen({required this.controller, super.key});

  final AppController controller;

  @override
  State<GoalEditorScreen> createState() => _GoalEditorScreenState();
}

class _GoalEditorScreenState extends State<GoalEditorScreen> {
  late final TextEditingController result;
  late final TextEditingController regular;
  late final TextEditingController minimum;
  int duration = 15;

  @override
  void initState() {
    super.initState();
    result = TextEditingController(text: widget.controller.activeGoal?.result ?? '');
    regular = TextEditingController(text: widget.controller.activeGoal?.regularStep ?? '');
    minimum = TextEditingController(text: widget.controller.activeGoal?.minimumStep ?? '');
    duration = widget.controller.activeGoal?.duration ?? 15;
  }

  @override
  void dispose() {
    result.dispose();
    regular.dispose();
    minimum.dispose();
    super.dispose();
  }

  bool get valid => result.text.trim().isNotEmpty && regular.text.trim().isNotEmpty && minimum.text.trim().isNotEmpty;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Одна цель')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          const Text('Какой результат важен сейчас?', style: TextStyle(fontSize: 27, fontWeight: FontWeight.w800)),
          const SizedBox(height: 18),
          TextField(
            controller: result,
            decoration: const InputDecoration(labelText: 'Результат', hintText: 'Например: подтянуться 12 раз'),
            onChanged: (_) => setState(() {}),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: regular,
            decoration: const InputDecoration(labelText: 'Обычный шаг', hintText: 'Например: сделать три подхода'),
            onChanged: (_) => setState(() {}),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: minimum,
            decoration: const InputDecoration(labelText: 'Минимальный шаг', hintText: 'Например: сделать один подход'),
            onChanged: (_) => setState(() {}),
          ),
          const SizedBox(height: 18),
          Wrap(
            spacing: 8,
            children: [5, 10, 15, 25].map((value) {
              return ChoiceChip(
                label: Text('$value минут'),
                selected: duration == value,
                onSelected: (_) => setState(() => duration = value),
              );
            }).toList(),
          ),
          const SizedBox(height: 24),
          FilledButton(
            onPressed: valid
                ? () {
                    widget.controller.saveGoal(
                      GoalPlan(
                        result: result.text.trim(),
                        regularStep: regular.text.trim(),
                        minimumStep: minimum.text.trim(),
                        duration: duration,
                      ),
                    );
                    Navigator.pop(context);
                  }
                : null,
            child: const Text('Сохранить маршрут'),
          ),
        ],
      ),
    );
  }
}

class SessionScreen extends StatefulWidget {
  const SessionScreen({
    required this.controller,
    required this.task,
    required this.minimumTask,
    required this.duration,
    required this.support,
    super.key,
  });

  final AppController controller;
  final String task;
  final String minimumTask;
  final int duration;
  final SupportMode support;

  @override
  State<SessionScreen> createState() => _SessionScreenState();
}

class _SessionScreenState extends State<SessionScreen> {
  Timer? timer;
  late int seconds;
  bool running = false;
  bool minimumMode = false;

  @override
  void initState() {
    super.initState();
    seconds = widget.duration * 60;
  }

  @override
  void dispose() {
    timer?.cancel();
    super.dispose();
  }

  void start() {
    timer?.cancel();
    setState(() => running = true);
    timer = Timer.periodic(const Duration(seconds: 1), (_) {
      if (seconds <= 1) {
        timer?.cancel();
        setState(() {
          seconds = 0;
          running = false;
        });
        complete();
      } else {
        setState(() => seconds--);
      }
    });
  }

  void enableMinimum() {
    timer?.cancel();
    setState(() {
      minimumMode = true;
      seconds = seconds > 120 ? 120 : seconds;
      running = false;
    });
  }

  Future<void> complete() async {
    timer?.cancel();
    final result = await Navigator.push<SessionOutcome>(
      context,
      MaterialPageRoute(
        builder: (_) => CompletionScreen(
          controller: widget.controller,
          task: widget.task,
          duration: widget.duration,
          support: widget.support,
        ),
      ),
    );
    if (!mounted || result == null) return;
    Navigator.pop(context);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.support == SupportMode.digital ? 'Цифровой компаньон' : 'Самостоятельная сессия'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            Card(
              child: Padding(
                padding: const EdgeInsets.all(18),
                child: Text(
                  widget.support == SupportMode.digital
                      ? 'Я помогу удержать рамку сессии и не буду отвлекать лишними сообщениями.'
                      : 'Задача и время уже определены. Осталось сделать первый физический шаг.',
                ),
              ),
            ),
            const SizedBox(height: 28),
            Text(
              minimumMode ? widget.minimumTask : widget.task,
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 25, fontWeight: FontWeight.w800),
            ),
            const SizedBox(height: 28),
            Text(
              formatDuration(seconds),
              style: const TextStyle(fontSize: 62, fontWeight: FontWeight.w800),
            ),
            const SizedBox(height: 24),
            if (!running)
              FilledButton.icon(
                onPressed: start,
                icon: const Icon(Icons.play_arrow_rounded),
                label: Text(seconds == widget.duration * 60 ? 'Начать' : 'Продолжить'),
              )
            else
              OutlinedButton.icon(
                onPressed: () {
                  timer?.cancel();
                  setState(() => running = false);
                },
                icon: const Icon(Icons.pause_rounded),
                label: const Text('Пауза'),
              ),
            const SizedBox(height: 10),
            if (!minimumMode)
              OutlinedButton.icon(
                onPressed: enableMinimum,
                icon: const Icon(Icons.spa_outlined),
                label: const Text('Перейти к минимальному шагу'),
              ),
            TextButton.icon(
              onPressed: () => showModalBottomSheet(
                context: context,
                showDragHandle: true,
                builder: (_) => Padding(
                  padding: const EdgeInsets.all(22),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('Что сейчас мешает?', style: TextStyle(fontSize: 23, fontWeight: FontWeight.w800)),
                      const SizedBox(height: 14),
                      ListTile(
                        title: const Text('Не понимаю, с чего начать'),
                        subtitle: const Text('Назовите один физический шаг: открыть файл, достать форму, подготовить инструменты.'),
                        onTap: () => Navigator.pop(context),
                      ),
                      ListTile(
                        title: const Text('Задача слишком большая'),
                        subtitle: const Text('Перейдите к заранее выбранному минимуму.'),
                        onTap: () {
                          Navigator.pop(context);
                          enableMinimum();
                        },
                      ),
                      ListTile(
                        title: const Text('Отвлёкся или устал'),
                        subtitle: const Text('Вернитесь к делу только на две минуты.'),
                        onTap: () {
                          Navigator.pop(context);
                          enableMinimum();
                        },
                      ),
                    ],
                  ),
                ),
              ),
              icon: const Icon(Icons.help_outline_rounded),
              label: const Text('Застрял'),
            ),
            const Spacer(),
            TextButton(
              onPressed: complete,
              child: const Text('Завершить и записать результат'),
            ),
          ],
        ),
      ),
    );
  }
}

class CompletionScreen extends StatefulWidget {
  const CompletionScreen({
    required this.controller,
    required this.task,
    required this.duration,
    required this.support,
    super.key,
  });

  final AppController controller;
  final String task;
  final int duration;
  final SupportMode support;

  @override
  State<CompletionScreen> createState() => _CompletionScreenState();
}

class _CompletionScreenState extends State<CompletionScreen> {
  SessionOutcome? selected;
  bool saved = false;

  @override
  Widget build(BuildContext context) {
    if (saved && selected != null) {
      return Scaffold(
        body: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SizedBox(height: 30),
                Icon(outcomeIcon(selected!), size: 70, color: const Color(0xFF4E7D70)),
                const SizedBox(height: 28),
                Text(
                  outcomeTitle(selected!),
                  style: const TextStyle(fontSize: 34, fontWeight: FontWeight.w800),
                ),
                const SizedBox(height: 14),
                Text(outcomeMessage(selected!), style: const TextStyle(fontSize: 18, height: 1.4)),
                const Spacer(),
                if (selected == SessionOutcome.missed)
                  FilledButton(
                    onPressed: () => Navigator.pushReplacement(
                      context,
                      MaterialPageRoute(
                        builder: (_) => SessionScreen(
                          controller: widget.controller,
                          task: widget.task,
                          minimumTask: 'Сделать только 2 минуты',
                          duration: 5,
                          support: SupportMode.digital,
                        ),
                      ),
                    ),
                    child: const Text('Вернуться с малого шага'),
                  )
                else
                  FilledButton(
                    onPressed: () => Navigator.pushReplacement(
                      context,
                      MaterialPageRoute(
                        builder: (_) => SessionScreen(
                          controller: widget.controller,
                          task: widget.task,
                          minimumTask: 'Сделать только 2 минуты',
                          duration: widget.duration,
                          support: widget.support,
                        ),
                      ),
                    ),
                    child: const Text('Повторить эту сессию'),
                  ),
                const SizedBox(height: 10),
                OutlinedButton(
                  onPressed: () => Navigator.pop(context, selected),
                  child: const Text('На главный экран'),
                ),
              ],
            ),
          ),
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(title: const Text('Результат сессии')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          const Text('Что получилось?', style: TextStyle(fontSize: 28, fontWeight: FontWeight.w800)),
          const SizedBox(height: 8),
          const Text('Нужен честный факт, чтобы следующий шаг стал точнее.'),
          const SizedBox(height: 18),
          outcomeTile(SessionOutcome.full, 'Выполнил обычный шаг', 'Запланированное действие сделано.'),
          outcomeTile(SessionOutcome.minimum, 'Выполнил минимальный шаг', 'Связь с целью сохранена.'),
          outcomeTile(SessionOutcome.started, 'Начал, но не закончил', 'Начало состоялось.'),
          outcomeTile(SessionOutcome.missed, 'Сегодня не получилось', 'Цель остаётся.'),
          const SizedBox(height: 18),
          FilledButton(
            onPressed: selected == null
                ? null
                : () {
                    widget.controller.addRecord(
                      SessionRecord(
                        task: widget.task,
                        outcome: selected!,
                        duration: widget.duration,
                        createdAt: DateTime.now(),
                      ),
                    );
                    setState(() => saved = true);
                  },
            child: const Text('Сохранить результат'),
          ),
        ],
      ),
    );
  }

  Widget outcomeTile(SessionOutcome value, String title, String subtitle) {
    return Card(
      child: RadioListTile<SessionOutcome>(
        value: value,
        groupValue: selected,
        onChanged: (newValue) => setState(() => selected = newValue),
        title: Text(title),
        subtitle: Text(subtitle),
      ),
    );
  }
}

IconData outcomeIcon(SessionOutcome outcome) {
  switch (outcome) {
    case SessionOutcome.full:
      return Icons.check_circle_rounded;
    case SessionOutcome.minimum:
      return Icons.spa_rounded;
    case SessionOutcome.started:
      return Icons.play_circle_fill_rounded;
    case SessionOutcome.missed:
      return Icons.refresh_rounded;
  }
}

String outcomeLabel(SessionOutcome outcome) {
  switch (outcome) {
    case SessionOutcome.full:
      return 'Выполнено';
    case SessionOutcome.minimum:
      return 'Минимальный шаг';
    case SessionOutcome.started:
      return 'Начало состоялось';
    case SessionOutcome.missed:
      return 'Нужно вернуться';
  }
}

String outcomeTitle(SessionOutcome outcome) {
  switch (outcome) {
    case SessionOutcome.full:
      return 'Сегодня цель получила действие';
    case SessionOutcome.minimum:
      return 'Связь с целью сохранена';
    case SessionOutcome.started:
      return 'Начало состоялось';
    case SessionOutcome.missed:
      return 'Цель остаётся';
  }
}

String outcomeMessage(SessionOutcome outcome) {
  switch (outcome) {
    case SessionOutcome.full:
      return 'Вы сделали запланированный шаг. Это реальный след, а не просто отметка в приложении.';
    case SessionOutcome.minimum:
      return 'Вместо полного отказа вы выполнили заранее выбранный минимум.';
    case SessionOutcome.started:
      return 'Следующую сессию можно сделать короче или продолжить с текущего места.';
    case SessionOutcome.missed:
      return 'Один неудачный день не отменяет направление. Вернуться можно с минимального шага.';
  }
}

String formatDuration(int totalSeconds) {
  final minutes = totalSeconds ~/ 60;
  final seconds = totalSeconds % 60;
  return '${minutes.toString().padLeft(2, '0')}:${seconds.toString().padLeft(2, '0')}';
}
