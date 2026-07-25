from pathlib import Path
import re

main_path = Path('lib/main.dart')
pubspec_path = Path('pubspec.yaml')
text = main_path.read_text(encoding='utf-8')


def replace_class(source: str, name: str, next_name: str, replacement: str) -> str:
    start = source.index(f'class {name}')
    end = source.index(f'class {next_name}', start)
    return source[:start] + replacement.rstrip() + '\n\n' + source[end:]


def replace_section(source: str, start_marker: str, end_marker: str, replacement: str) -> str:
    start = source.index(start_marker)
    end = source.index(end_marker, start)
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
    final nonRoutines = active
        .where((item) => item.kind != IntentKind.routine)
        .toList();
    final due = nonRoutines.where((item) => !isLater(item)).toList();
    final later = nonRoutines.where(isLater).toList()
      ..sort((a, b) => a.scheduledAt!.compareTo(b.scheduledAt!));
    final goalActions = due.where((item) => item.goal).toList();
    final routines = active
        .where((item) => item.kind == IntentKind.routine)
        .toList();
    final reminders = due
        .where((item) => !item.goal && item.kind == IntentKind.reminder)
        .toList();
    final other = due
        .where((item) => !item.goal && item.kind == IntentKind.focus)
        .toList();

    return Scaffold(
      appBar: AppBar(
        title: const Row(
          children: [
            Logo(size: 24),
            SizedBox(width: 8),
            Text(
              'Вместе к цели',
              style: TextStyle(fontSize: 17, fontWeight: FontWeight.w700),
            ),
          ],
        ),
        actions: [
          IconButton(
            key: const ValueKey('today-add'),
            tooltip: 'Добавить',
            icon: const Icon(Icons.add_rounded),
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
        padding: const EdgeInsets.fromLTRB(14, 0, 14, 28),
        children: [
          _PremiumTodayHeader(count: due.length, goalCount: goalActions.length),
          const SizedBox(height: 8),
          if (app.goal == null)
            CreateGoal(app: app)
          else ...[
            GoalHero(app: app, onTap: onOpenGoal),
            const SizedBox(height: 9),
            _GoalActionGroup(
              app: app,
              actions: goalActions,
              onOpenGoal: onOpenGoal,
            ),
          ],
          if (routines.isNotEmpty) ...[
            const SizedBox(height: 14),
            _section('Регулярные практики', routines.length),
            const SizedBox(height: 7),
            ...routines.map(
              (item) => Padding(
                padding: const EdgeInsets.only(bottom: 7),
                child: RoutineCard(app: app, item: item),
              ),
            ),
          ],
          if (reminders.isNotEmpty) ...[
            const SizedBox(height: 14),
            _section('Не забыть', reminders.length),
            const SizedBox(height: 7),
            ...reminders.map(
              (item) => Padding(
                padding: const EdgeInsets.only(bottom: 7),
                child: ActionCard(app: app, item: item),
              ),
            ),
          ],
          if (other.isNotEmpty) ...[
            const SizedBox(height: 14),
            _section('Другие дела', other.length),
            const SizedBox(height: 7),
            ...other.map(
              (item) => Padding(
                padding: const EdgeInsets.only(bottom: 7),
                child: ActionCard(app: app, item: item),
              ),
            ),
          ],
          if (due.isEmpty && routines.isEmpty && app.goal == null) ...[
            const SizedBox(height: 14),
            const _PremiumEmptyState(),
          ],
          if (later.isNotEmpty) ...[
            const SizedBox(height: 15),
            _section('Запланировано позже', later.length),
            const SizedBox(height: 7),
            ...later.take(6).map(
              (item) => Padding(
                padding: const EdgeInsets.only(bottom: 7),
                child: ActionCard(app: app, item: item),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _section(String text, int count) => Row(
    children: [
      Expanded(
        child: Text(
          text,
          style: const TextStyle(
            fontSize: 15.5,
            fontWeight: FontWeight.w700,
            color: ink,
          ),
        ),
      ),
      Container(
        padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2),
        decoration: BoxDecoration(
          color: const Color(0xFFE4EEE9),
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
          const Icon(Icons.route_rounded, color: green, size: 17),
          const SizedBox(width: 6),
          const Expanded(
            child: Text(
              'Следующий шаг',
              style: TextStyle(
                color: ink,
                fontSize: 14.5,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
          if (actions.length > 1)
            Text(
              '${actions.length} в работе',
              style: const TextStyle(color: Color(0xFF64716D), fontSize: 11.5),
            ),
          IconButton(
            onPressed: onOpenGoal,
            tooltip: 'Открыть цель',
            visualDensity: VisualDensity.compact,
            iconSize: 20,
            icon: const Icon(Icons.chevron_right_rounded, color: green),
          ),
        ],
      ),
      const SizedBox(height: 5),
      if (actions.isEmpty)
        EmptyAction(
          onTap: () => Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => ActionEditor(app: app, goalDefault: true),
            ),
          ),
        )
      else
        ...actions.asMap().entries.map(
          (entry) => Padding(
            padding: EdgeInsets.only(
              bottom: entry.key == actions.length - 1 ? 0 : 7,
            ),
            child: ActionCard(
              app: app,
              item: entry.value,
              featured: entry.key == 0,
            ),
          ),
        ),
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
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.symmetric(horizontal: 11, vertical: 8),
    decoration: BoxDecoration(
      color: const Color(0xFFF1F4F2),
      borderRadius: BorderRadius.circular(14),
    ),
    child: Row(
      children: [
        Container(
          width: 29,
          height: 29,
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(9),
          ),
          child: const Icon(Icons.wb_sunny_outlined, color: green, size: 17),
        ),
        const SizedBox(width: 9),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                count == 0 ? 'Сегодня свободно' : '$count ${taskWord(count)} на сегодня',
                style: const TextStyle(
                  color: ink,
                  fontSize: 15.5,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 1),
              Text(
                goalCount == 0
                    ? longToday()
                    : '$goalCount ${taskWord(goalCount)} для главной цели',
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(
                  color: Color(0xFF66736F),
                  fontSize: 11.5,
                ),
              ),
            ],
          ),
        ),
      ],
    ),
  );
}'''
text = replace_class(
    text,
    '_PremiumTodayHeader extends StatelessWidget',
    '_PremiumEmptyState extends StatelessWidget',
    TODAY_HEADER,
)


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
        ? 'Пока без действий'
        : '${app.goalDone} из $total завершено';
    final stages = goal.areas.isEmpty ? '' : '  ·  ${goal.areas.length} этапов';

    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(18),
        child: Ink(
          padding: const EdgeInsets.fromLTRB(14, 13, 14, 12),
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [Color(0xFF173A35), Color(0xFF356D63)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(18),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Text(
                    'ГЛАВНАЯ ЦЕЛЬ',
                    style: TextStyle(
                      color: Color(0xFFD5ECE4),
                      fontSize: 9.5,
                      fontWeight: FontWeight.w700,
                      letterSpacing: 0.9,
                    ),
                  ),
                  const Spacer(),
                  if (onTap != null)
                    Container(
                      width: 28,
                      height: 28,
                      decoration: const BoxDecoration(
                        color: Colors.white10,
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(
                        Icons.arrow_forward_rounded,
                        color: Colors.white,
                        size: 17,
                      ),
                    ),
                ],
              ),
              const SizedBox(height: 7),
              Text(
                goal.title,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 19,
                  height: 1.12,
                  fontWeight: FontWeight.w700,
                ),
              ),
              if (next != null) ...[
                const SizedBox(height: 4),
                Text(
                  'Сейчас · ${next.title}',
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    color: Color(0xFFD7E2DF),
                    fontSize: 12.5,
                  ),
                ),
              ],
              const SizedBox(height: 9),
              ClipRRect(
                borderRadius: BorderRadius.circular(8),
                child: LinearProgressIndicator(
                  value: progress,
                  minHeight: 3,
                  backgroundColor: Colors.white12,
                  valueColor: const AlwaysStoppedAnimation(mint),
                ),
              ),
              const SizedBox(height: 7),
              Text(
                '$progressText$stages',
                style: const TextStyle(color: Colors.white60, fontSize: 10.5),
              ),
            ],
          ),
        ),
      ),
    );
  }
}'''
text = replace_class(text, 'GoalHero extends StatelessWidget', 'EmptyAction extends StatelessWidget', GOAL_HERO)


ACTION_CARD = r'''class ActionCard extends StatelessWidget {
  const ActionCard({
    required this.app,
    required this.item,
    this.featured = false,
    super.key,
  });

  final AppState app;
  final ActionItem item;
  final bool featured;

  Future<void> _startTogether(BuildContext context) async {
    app.setSupport(item, Support.together);
    await shareStartMessage(item.title, item.minutes, Support.together);
    if (!context.mounted || !item.useTimer) return;
    await Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => Session(app: app, item: item)),
    );
  }

  Future<void> _record(BuildContext context) async {
    final state = await showModalBottomSheet<ResultState>(
      context: context,
      showDragHandle: true,
      builder: (sheetContext) =>
          Finish(onFinish: (value) => Navigator.pop(sheetContext, value)),
    );
    if (state == null || !context.mounted) return;

    if (state == ResultState.moved) {
      final when = await showActionSchedule(context, item.scheduledAt);
      if (when != null) await app.reschedule(item, when);
      return;
    }

    app.complete(item, state);
    if (!context.mounted) return;
    await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => ResultPage(app: app, item: item, state: state),
      ),
    );
  }

  Future<void> _primary(BuildContext context) async {
    if (item.kind == IntentKind.reminder || !item.useTimer) {
      await _record(context);
      return;
    }
    await Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => Session(app: app, item: item)),
    );
  }

  Future<void> _menu(BuildContext context, String value) async {
    switch (value) {
      case 'edit':
        await Navigator.push(
          context,
          MaterialPageRoute(
            builder: (_) =>
                ActionEditor(app: app, goalDefault: item.goal, existing: item),
          ),
        );
        return;
      case 'move':
        final when = await showActionSchedule(context, item.scheduledAt);
        if (when != null) await app.reschedule(item, when);
        return;
      case 'delete':
        final confirmed = await showDialog<bool>(
          context: context,
          builder: (dialogContext) => AlertDialog(
            title: const Text('Удалить действие?'),
            content: Text('«${item.title}» будет удалено из текущих дел.'),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(dialogContext, false),
                child: const Text('Отмена'),
              ),
              FilledButton(
                onPressed: () => Navigator.pop(dialogContext, true),
                child: const Text('Удалить'),
              ),
            ],
          ),
        );
        if (confirmed == true) app.deleteAction(item);
        return;
    }
  }

  @override
  Widget build(BuildContext context) {
    final future = isLater(item);
    final primaryLabel = item.useTimer ? 'Начать' : 'Отметить';

    return Card(
      key: ValueKey('action-card-${item.id}'),
      color: featured ? const Color(0xFFFFFDF8) : Colors.white,
      child: Padding(
        padding: const EdgeInsets.fromLTRB(12, 12, 12, 11),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  width: 36,
                  height: 36,
                  decoration: BoxDecoration(
                    color: intentColor(item.kind),
                    borderRadius: BorderRadius.circular(11),
                  ),
                  child: Icon(intentIcon(item.kind), color: ink, size: 20),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        item.title,
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                          fontSize: 15.5,
                          height: 1.16,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      const SizedBox(height: 3),
                      Text(
                        actionMeta(item),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                          color: Color(0xFF65716D),
                          fontSize: 12.5,
                        ),
                      ),
                    ],
                  ),
                ),
                PopupMenuButton<String>(
                  tooltip: 'Действия',
                  padding: EdgeInsets.zero,
                  iconSize: 20,
                  onSelected: (value) => _menu(context, value),
                  itemBuilder: (_) => const [
                    PopupMenuItem(value: 'edit', child: Text('Изменить')),
                    PopupMenuItem(value: 'move', child: Text('Перенести')),
                    PopupMenuItem(value: 'delete', child: Text('Удалить')),
                  ],
                ),
              ],
            ),
            if (item.small.isNotEmpty) ...[
              const SizedBox(height: 8),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                decoration: BoxDecoration(
                  color: cream,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  'Минимум: ${item.small}',
                  style: const TextStyle(fontSize: 12.5),
                ),
              ),
            ],
            const SizedBox(height: 9),
            if (future)
              SizedBox(
                width: double.infinity,
                child: OutlinedButton.icon(
                  onPressed: () => _menu(context, 'move'),
                  icon: const Icon(Icons.event_outlined, size: 18),
                  label: Text(
                    'Запланировано: ${shortDate(item.scheduledAt!)}',
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              )
            else if (item.kind == IntentKind.reminder)
              SizedBox(
                width: double.infinity,
                child: FilledButton.icon(
                  key: ValueKey('action-primary-${item.id}'),
                  onPressed: () => _record(context),
                  icon: const Icon(Icons.check_rounded, size: 19),
                  label: const Text('Отметить', maxLines: 1),
                ),
              )
            else
              Row(
                children: [
                  Expanded(
                    flex: 3,
                    child: FilledButton.icon(
                      key: ValueKey('action-primary-${item.id}'),
                      style: FilledButton.styleFrom(
                        minimumSize: const Size(0, 43),
                        padding: const EdgeInsets.symmetric(horizontal: 10),
                        tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                      ),
                      onPressed: () => _primary(context),
                      icon: Icon(
                        item.useTimer ? Icons.play_arrow : Icons.check_rounded,
                        size: 19,
                      ),
                      label: Text(
                        primaryLabel,
                        maxLines: 1,
                        softWrap: false,
                        overflow: TextOverflow.fade,
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    flex: 2,
                    child: OutlinedButton.icon(
                      key: ValueKey('action-together-${item.id}'),
                      style: OutlinedButton.styleFrom(
                        minimumSize: const Size(0, 43),
                        padding: const EdgeInsets.symmetric(horizontal: 8),
                        tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                      ),
                      onPressed: () => _startTogether(context),
                      icon: const Icon(Icons.people_alt_outlined, size: 18),
                      label: const Text(
                        'Вместе',
                        maxLines: 1,
                        softWrap: false,
                      ),
                    ),
                  ),
                ],
              ),
          ],
        ),
      ),
    );
  }
}'''
text = replace_section(
    text,
    'class ActionCard extends StatelessWidget',
    'Future<DateTime?> showActionSchedule',
    ACTION_CARD,
)

# Soften the shared typography that is most visible across the application.
text = text.replace(
    'fontSize: 26,\n            height: 1.08,\n            fontWeight: FontWeight.w900,',
    'fontSize: 25,\n            height: 1.1,\n            fontWeight: FontWeight.w800,',
)
text = text.replace(
    'fontSize: 20,\n            height: 1.16,\n            fontWeight: FontWeight.w900,',
    'fontSize: 19,\n            height: 1.18,\n            fontWeight: FontWeight.w800,',
)
text = text.replace(
    'fontSize: 17,\n            fontWeight: FontWeight.w900,',
    'fontSize: 16.5,\n            fontWeight: FontWeight.w700,',
)
text = text.replace(
    'fontSize: 15.5,\n            fontWeight: FontWeight.w800,',
    'fontSize: 15,\n            fontWeight: FontWeight.w700,',
)
text = text.replace(
    'fontSize: 14.5,\n              fontWeight: FontWeight.w800,',
    'fontSize: 14,\n              fontWeight: FontWeight.w700,',
)

main_path.write_text(text, encoding='utf-8')

pubspec = pubspec_path.read_text(encoding='utf-8')
pubspec = re.sub(r'^version:\s*.+$', 'version: 0.6.2+15', pubspec, flags=re.MULTILINE)
pubspec_path.write_text(pubspec, encoding='utf-8')
