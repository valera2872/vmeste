from pathlib import Path
import re

main_path = Path('lib/main.dart')
pubspec_path = Path('pubspec.yaml')
text = main_path.read_text(encoding='utf-8')


def replace_class(source: str, name: str, next_name: str, replacement: str) -> str:
    start = source.index(f'class {name}')
    end = source.index(f'class {next_name}', start)
    return source[:start] + replacement.rstrip() + '\n\n' + source[end:]


TODAY = r'''class Today extends StatelessWidget {
  const Today({required this.app, required this.onOpenGoal, super.key});
  final AppState app;
  final VoidCallback onOpenGoal;

  void _add(BuildContext context) => Navigator.push(
    context,
    MaterialPageRoute(builder: (_) => IntentChooserPage(app: app)),
  );

  @override
  Widget build(BuildContext context) {
    final active = app.actions.where((item) => item.state == null).toList();
    final goalActions = active
        .where((item) => item.goal && item.kind != IntentKind.routine)
        .toList()
      ..sort((a, b) {
        final aDate = a.scheduledAt;
        final bDate = b.scheduledAt;
        if (aDate == null && bDate == null) return 0;
        if (aDate == null) return -1;
        if (bDate == null) return 1;
        return aDate.compareTo(bDate);
      });
    final nonGoalActions = active
        .where((item) => !item.goal && item.kind != IntentKind.routine)
        .toList();
    final later = nonGoalActions.where(isLater).toList()
      ..sort((a, b) => a.scheduledAt!.compareTo(b.scheduledAt!));
    final due = nonGoalActions.where((item) => !isLater(item)).toList();
    final reminders = due
        .where((item) => item.kind == IntentKind.reminder)
        .toList();
    final other = due.where((item) => item.kind == IntentKind.focus).toList();
    final routines = active
        .where((item) => item.kind == IntentKind.routine)
        .toList();
    final dueGoalCount = goalActions.where((item) => !isLater(item)).length;
    final todayCount = due.length + dueGoalCount +
        routines.where(routineDueToday).length;

    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Сегодня',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700),
        ),
        actions: [
          IconButton(
            key: const ValueKey('today-add'),
            tooltip: 'Добавить',
            icon: const Icon(Icons.add_circle_outline_rounded),
            onPressed: () => _add(context),
          ),
          IconButton(
            tooltip: 'Как работает приложение',
            icon: const Icon(Icons.info_outline_rounded),
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => Onboarding(app: app, preview: true),
              ),
            ),
          ),
        ],
      ),
      body: ListView(
        key: const ValueKey('today-scroll'),
        padding: const EdgeInsets.fromLTRB(16, 0, 16, 28),
        children: [
          _PremiumTodayHeader(count: todayCount, goalCount: dueGoalCount),
          const SizedBox(height: 12),
          if (app.goal == null)
            CreateGoal(app: app)
          else ...[
            GoalHero(app: app, onTap: onOpenGoal),
            const SizedBox(height: 12),
            _GoalActionGroup(
              app: app,
              actions: goalActions,
              onOpenGoal: onOpenGoal,
            ),
          ],
          const SizedBox(height: 18),
          _OtherWorkPanel(
            app: app,
            reminders: reminders,
            actions: other,
            routines: routines,
          ),
          if (later.isNotEmpty) ...[
            const SizedBox(height: 20),
            _HomeSectionTitle(
              title: 'Запланировано позже',
              subtitle: 'Дела, к которым приложение вернёт вас в выбранный день.',
              count: later.length,
            ),
            const SizedBox(height: 8),
            ...later.take(6).map(
              (item) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: ActionCard(app: app, item: item),
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class _OtherWorkPanel extends StatelessWidget {
  const _OtherWorkPanel({
    required this.app,
    required this.reminders,
    required this.actions,
    required this.routines,
  });

  final AppState app;
  final List<ActionItem> reminders;
  final List<ActionItem> actions;
  final List<ActionItem> routines;

  void _add(BuildContext context) => Navigator.push(
    context,
    MaterialPageRoute(builder: (_) => IntentChooserPage(app: app)),
  );

  @override
  Widget build(BuildContext context) {
    final count = reminders.length + actions.length + routines.length;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            const Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Остальные дела',
                    style: TextStyle(
                      color: ink,
                      fontSize: 18,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  SizedBox(height: 2),
                  Text(
                    'Напоминания, разовые дела и регулярные практики.',
                    style: TextStyle(
                      color: Color(0xFF687470),
                      fontSize: 12.5,
                      height: 1.3,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(width: 10),
            FilledButton.tonalIcon(
              key: const ValueKey('add-other-work'),
              style: FilledButton.styleFrom(
                minimumSize: const Size(0, 40),
                padding: const EdgeInsets.symmetric(horizontal: 12),
                backgroundColor: const Color(0xFFE5EFEB),
                foregroundColor: green,
              ),
              onPressed: () => _add(context),
              icon: const Icon(Icons.add_rounded, size: 18),
              label: const Text('Добавить дело'),
            ),
          ],
        ),
        const SizedBox(height: 10),
        if (count == 0)
          Container(
            width: double.infinity,
            padding: const EdgeInsets.fromLTRB(13, 12, 13, 12),
            decoration: BoxDecoration(
              color: const Color(0xFFF0F4F2),
              borderRadius: BorderRadius.circular(14),
            ),
            child: const Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(Icons.inbox_outlined, color: green, size: 20),
                SizedBox(width: 9),
                Expanded(
                  child: Text(
                    'Здесь можно разгрузить голову: записать обычное дело, поставить напоминание или создать практику.',
                    style: TextStyle(fontSize: 12.8, height: 1.35),
                  ),
                ),
              ],
            ),
          )
        else ...[
          if (actions.isNotEmpty) ...[
            _HomeSectionTitle(title: 'Разовые дела', count: actions.length),
            const SizedBox(height: 7),
            ...actions.map(
              (item) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: ActionCard(app: app, item: item),
              ),
            ),
          ],
          if (reminders.isNotEmpty) ...[
            if (actions.isNotEmpty) const SizedBox(height: 8),
            _HomeSectionTitle(title: 'Не забыть', count: reminders.length),
            const SizedBox(height: 7),
            ...reminders.map(
              (item) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: ActionCard(app: app, item: item),
              ),
            ),
          ],
          if (routines.isNotEmpty) ...[
            if (actions.isNotEmpty || reminders.isNotEmpty)
              const SizedBox(height: 8),
            _HomeSectionTitle(
              title: 'Регулярные практики',
              count: routines.length,
            ),
            const SizedBox(height: 7),
            ...routines.map(
              (item) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: RoutineCard(app: app, item: item),
              ),
            ),
          ],
        ],
      ],
    );
  }
}

class _HomeSectionTitle extends StatelessWidget {
  const _HomeSectionTitle({
    required this.title,
    this.subtitle,
    required this.count,
  });

  final String title;
  final String? subtitle;
  final int count;

  @override
  Widget build(BuildContext context) => Row(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Expanded(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: const TextStyle(
                color: ink,
                fontSize: 15.5,
                fontWeight: FontWeight.w700,
              ),
            ),
            if (subtitle != null) ...[
              const SizedBox(height: 2),
              Text(
                subtitle!,
                style: const TextStyle(
                  color: Color(0xFF687470),
                  fontSize: 12,
                  height: 1.3,
                ),
              ),
            ],
          ],
        ),
      ),
      Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
        decoration: BoxDecoration(
          color: const Color(0xFFE5EFEB),
          borderRadius: BorderRadius.circular(20),
        ),
        child: Text(
          '$count',
          style: const TextStyle(
            color: green,
            fontSize: 11.5,
            fontWeight: FontWeight.w700,
          ),
        ),
      ),
    ],
  );
}'''
text = replace_class(text, 'Today extends StatelessWidget', '_GoalActionGroup extends StatelessWidget', TODAY)


GOAL_GROUP = r'''class _GoalActionGroup extends StatelessWidget {
  const _GoalActionGroup({
    required this.app,
    required this.actions,
    required this.onOpenGoal,
  });

  final AppState app;
  final List<ActionItem> actions;
  final VoidCallback onOpenGoal;

  @override
  Widget build(BuildContext context) => Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Row(
        children: [
          const Expanded(
            child: Text(
              'Следующий шаг',
              style: TextStyle(
                color: ink,
                fontSize: 16,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
          TextButton(
            onPressed: onOpenGoal,
            child: const Text('Открыть цель'),
          ),
        ],
      ),
      const SizedBox(height: 5),
      if (actions.isEmpty)
        Container(
          width: double.infinity,
          padding: const EdgeInsets.fromLTRB(13, 12, 13, 12),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(15),
            border: Border.all(color: const Color(0xFFE0E6E2)),
          ),
          child: Row(
            children: [
              const Icon(Icons.route_outlined, color: green, size: 22),
              const SizedBox(width: 10),
              const Expanded(
                child: Text(
                  'Ближайшее действие ещё не выбрано.',
                  style: TextStyle(fontSize: 13.5),
                ),
              ),
              TextButton(
                onPressed: () => Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => ActionEditor(app: app, goalDefault: true),
                  ),
                ),
                child: const Text('Выбрать'),
              ),
            ],
          ),
        )
      else ...[
        ActionCard(app: app, item: actions.first, featured: true),
        if (actions.length > 1)
          Align(
            alignment: Alignment.centerLeft,
            child: TextButton.icon(
              onPressed: onOpenGoal,
              icon: const Icon(Icons.format_list_bulleted_rounded, size: 18),
              label: Text('Ещё ${actions.length - 1} в главной цели'),
            ),
          ),
      ],
    ],
  );
}'''
text = replace_class(
    text,
    '_GoalActionGroup extends StatelessWidget',
    '_PremiumTodayHeader extends StatelessWidget',
    GOAL_GROUP,
)


TODAY_HEADER = r'''class _PremiumTodayHeader extends StatelessWidget {
  const _PremiumTodayHeader({required this.count, required this.goalCount});
  final int count, goalCount;

  @override
  Widget build(BuildContext context) => Row(
    children: [
      Expanded(
        child: Text(
          longToday(),
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: const TextStyle(
            color: Color(0xFF687470),
            fontSize: 12.5,
          ),
        ),
      ),
      Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
        decoration: BoxDecoration(
          color: count == 0
              ? const Color(0xFFF0F4F2)
              : const Color(0xFFE5EFEB),
          borderRadius: BorderRadius.circular(20),
        ),
        child: Text(
          count == 0 ? 'День свободен' : '$count ${taskWord(count)} в плане',
          style: const TextStyle(
            color: green,
            fontSize: 11.5,
            fontWeight: FontWeight.w700,
          ),
        ),
      ),
    ],
  );
}'''
text = replace_class(
    text,
    '_PremiumTodayHeader extends StatelessWidget',
    '_PremiumEmptyState extends StatelessWidget',
    TODAY_HEADER,
)


CREATE_GOAL = r'''class CreateGoal extends StatelessWidget {
  const CreateGoal({required this.app, super.key});
  final AppState app;

  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.fromLTRB(16, 15, 16, 14),
    decoration: BoxDecoration(
      color: Colors.white,
      borderRadius: BorderRadius.circular(18),
      border: Border.all(color: const Color(0xFFE0E6E2)),
    ),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: 38,
              height: 38,
              decoration: BoxDecoration(
                color: const Color(0xFFE5EFEB),
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Icon(Icons.flag_outlined, color: green, size: 21),
            ),
            const SizedBox(width: 11),
            const Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Главная цель',
                    style: TextStyle(
                      color: ink,
                      fontSize: 18,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  SizedBox(height: 3),
                  Text(
                    'Выберите одно важное направление. Остальные дела будут храниться отдельно.',
                    style: TextStyle(
                      color: Color(0xFF687470),
                      fontSize: 12.8,
                      height: 1.34,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
        const SizedBox(height: 13),
        FilledButton.icon(
          key: const ValueKey('create-main-goal'),
          onPressed: () => Navigator.push(
            context,
            MaterialPageRoute(builder: (_) => GoalEditor(app: app)),
          ),
          icon: const Icon(Icons.arrow_forward_rounded, size: 19),
          label: const Text('Создать главную цель'),
        ),
        const SizedBox(height: 2),
        TextButton.icon(
          onPressed: () => Navigator.push(
            context,
            MaterialPageRoute(builder: (_) => IntentChooserPage(app: app)),
          ),
          icon: const Icon(Icons.add_rounded, size: 18),
          label: const Text('Добавить обычное дело'),
        ),
      ],
    ),
  );
}'''
text = replace_class(text, 'CreateGoal extends StatelessWidget', 'GoalHero extends StatelessWidget', CREATE_GOAL)


GOAL_HERO = r'''class GoalHero extends StatelessWidget {
  const GoalHero({required this.app, this.onTap, super.key});
  final AppState app;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final goal = app.goal!;
    final total = app.goalDone + app.goalActive;
    final progress = total == 0 ? 0.0 : app.goalDone / total;
    final next = app.actions
        .where((item) => item.goal && item.state == null)
        .firstOrNull;
    final progressText = total == 0
        ? 'Путь начнётся с первого действия'
        : '${app.goalDone} из $total действий завершено';

    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(18),
        child: Ink(
          padding: const EdgeInsets.fromLTRB(15, 14, 14, 13),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(18),
            border: Border.all(color: const Color(0xFFDCE5E1)),
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 4,
                height: 92,
                decoration: BoxDecoration(
                  color: green,
                  borderRadius: BorderRadius.circular(4),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'ГЛАВНАЯ ЦЕЛЬ',
                      style: TextStyle(
                        color: green,
                        fontSize: 10,
                        fontWeight: FontWeight.w700,
                        letterSpacing: .9,
                      ),
                    ),
                    const SizedBox(height: 5),
                    Text(
                      goal.title,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        color: ink,
                        fontSize: 20,
                        height: 1.12,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    if (next != null) ...[
                      const SizedBox(height: 5),
                      Text(
                        'Сейчас · ${next.title}',
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                          color: Color(0xFF596762),
                          fontSize: 12.5,
                        ),
                      ),
                    ],
                    const SizedBox(height: 9),
                    ClipRRect(
                      borderRadius: BorderRadius.circular(8),
                      child: LinearProgressIndicator(
                        value: progress,
                        minHeight: 4,
                        backgroundColor: const Color(0xFFE8EEEB),
                        valueColor: const AlwaysStoppedAnimation(green),
                      ),
                    ),
                    const SizedBox(height: 5),
                    Text(
                      progressText,
                      style: const TextStyle(
                        color: Color(0xFF73807B),
                        fontSize: 10.8,
                      ),
                    ),
                  ],
                ),
              ),
              if (onTap != null) ...[
                const SizedBox(width: 8),
                const Icon(
                  Icons.arrow_forward_rounded,
                  color: green,
                  size: 20,
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}'''
text = replace_class(text, 'GoalHero extends StatelessWidget', 'EmptyAction extends StatelessWidget', GOAL_HERO)


GOAL_SCREEN = r'''class GoalScreen extends StatelessWidget {
  const GoalScreen({required this.app, super.key});
  final AppState app;

  @override
  Widget build(BuildContext context) {
    final goal = app.goal;
    if (goal == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Главная цель')),
        body: ListView(
          padding: const EdgeInsets.fromLTRB(16, 4, 16, 24),
          children: [CreateGoal(app: app)],
        ),
      );
    }

    final active = app.actions
        .where((item) => item.goal && item.state == null)
        .toList();
    final completed = app.history.where((item) => item.goal).take(6).toList();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Главная цель'),
        actions: [
          IconButton(
            tooltip: 'Изменить цель',
            icon: const Icon(Icons.edit_outlined),
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => GoalEditor(app: app, existing: goal),
              ),
            ),
          ),
        ],
      ),
      body: ListView(
        key: const ValueKey('goal-screen-scroll'),
        padding: const EdgeInsets.fromLTRB(16, 0, 16, 28),
        children: [
          _GoalOverviewCard(app: app),
          const SizedBox(height: 13),
          FilledButton.icon(
            key: const ValueKey('add-goal-step'),
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => ActionEditor(app: app, goalDefault: true),
              ),
            ),
            icon: const Icon(Icons.add_task_rounded, size: 19),
            label: const Text('Добавить следующий шаг'),
          ),
          const SizedBox(height: 8),
          OutlinedButton.icon(
            key: const ValueKey('add-other-from-goal'),
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => IntentChooserPage(app: app)),
            ),
            icon: const Icon(Icons.playlist_add_rounded, size: 19),
            label: const Text('Добавить другое дело'),
          ),
          const SizedBox(height: 20),
          _HomeSectionTitle(
            title: 'Активные шаги',
            subtitle: 'Здесь хранится весь путь. На экране «Сегодня» показывается только ближайшее действие.',
            count: active.length,
          ),
          const SizedBox(height: 8),
          if (active.isEmpty)
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: const Color(0xFFF0F4F2),
                borderRadius: BorderRadius.circular(14),
              ),
              child: const Text(
                'Сейчас активных шагов нет. Добавьте действие, которое можно выполнить следующим.',
                style: TextStyle(fontSize: 13, height: 1.35),
              ),
            )
          else
            ...active.map(
              (item) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: ActionCard(app: app, item: item),
              ),
            ),
          if (completed.isNotEmpty) ...[
            const SizedBox(height: 18),
            _HomeSectionTitle(
              title: 'Что уже сделано',
              count: completed.length,
            ),
            const SizedBox(height: 8),
            ...completed.map((item) => _GoalHistoryRow(item: item)),
          ],
        ],
      ),
    );
  }
}

class _GoalOverviewCard extends StatelessWidget {
  const _GoalOverviewCard({required this.app});
  final AppState app;

  @override
  Widget build(BuildContext context) {
    final goal = app.goal!;
    final total = app.goalDone + app.goalActive;
    final progress = total == 0 ? 0.0 : app.goalDone / total;
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 15, 16, 15),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: const Color(0xFFDCE5E1)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'ВАШЕ НАПРАВЛЕНИЕ',
            style: TextStyle(
              color: green,
              fontSize: 10,
              fontWeight: FontWeight.w700,
              letterSpacing: .9,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            goal.title,
            style: const TextStyle(
              color: ink,
              fontSize: 23,
              height: 1.1,
              fontWeight: FontWeight.w700,
            ),
          ),
          if (goal.result.isNotEmpty) ...[
            const SizedBox(height: 8),
            Text(
              goal.result,
              style: const TextStyle(
                color: Color(0xFF596762),
                fontSize: 13.5,
                height: 1.36,
              ),
            ),
          ],
          if (goal.areas.isNotEmpty) ...[
            const SizedBox(height: 11),
            Wrap(
              spacing: 6,
              runSpacing: 6,
              children: goal.areas
                  .map(
                    (area) => Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 9,
                        vertical: 5,
                      ),
                      decoration: BoxDecoration(
                        color: const Color(0xFFF0F4F2),
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Text(
                        area,
                        style: const TextStyle(
                          color: Color(0xFF596762),
                          fontSize: 11.5,
                        ),
                      ),
                    ),
                  )
                  .toList(),
            ),
          ],
          const SizedBox(height: 13),
          ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: LinearProgressIndicator(
              value: progress,
              minHeight: 5,
              backgroundColor: const Color(0xFFE8EEEB),
              valueColor: const AlwaysStoppedAnimation(green),
            ),
          ),
          const SizedBox(height: 7),
          Text(
            total == 0
                ? 'Первый шаг ещё не выбран'
                : '${app.goalDone} завершено · ${app.goalActive} в работе',
            style: const TextStyle(
              color: Color(0xFF687470),
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }
}

class _GoalHistoryRow extends StatelessWidget {
  const _GoalHistoryRow({required this.item});
  final HistoryItem item;

  @override
  Widget build(BuildContext context) {
    final result = switch (item.state) {
      ResultState.done => 'Выполнено',
      ResultState.part => 'Сделана часть',
      ResultState.moved => 'Перенесено',
      ResultState.missed => 'Не получилось',
    };
    return Container(
      margin: const EdgeInsets.only(bottom: 7),
      padding: const EdgeInsets.fromLTRB(12, 10, 10, 10),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFFE4E8E5)),
      ),
      child: Row(
        children: [
          Icon(resultIcon(item.state), color: green, size: 20),
          const SizedBox(width: 9),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  item.title,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    fontSize: 13.5,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                Text(
                  '$result · ${item.date.day}.${item.date.month}.${item.date.year}',
                  style: const TextStyle(
                    color: Color(0xFF75817D),
                    fontSize: 11.5,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}'''
text = replace_class(text, 'GoalScreen extends StatelessWidget', 'GoalEditor extends StatefulWidget', GOAL_SCREEN)

main_path.write_text(text, encoding='utf-8')

pubspec = pubspec_path.read_text(encoding='utf-8')
pubspec = re.sub(r'^version:\s*[^\n]+', 'version: 0.6.4+17', pubspec, count=1, flags=re.M)
pubspec_path.write_text(pubspec, encoding='utf-8')
