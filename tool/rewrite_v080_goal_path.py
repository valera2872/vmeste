from pathlib import Path
import re

main_path = Path('lib/main.dart')
pubspec_path = Path('pubspec.yaml')
text = main_path.read_text(encoding='utf-8')


def replace_class(source: str, name: str, next_name: str, replacement: str) -> str:
    start = source.index(f'class {name}')
    end = source.index(f'class {next_name}', start)
    return source[:start] + replacement.rstrip() + '\n\n' + source[end:]


GOAL_SCREEN = r'''class GoalScreen extends StatelessWidget {
  const GoalScreen({required this.app, super.key});
  final AppState app;

  @override
  Widget build(BuildContext context) {
    final goal = app.goal;
    if (goal == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Путь к цели')),
        body: ListView(
          padding: const EdgeInsets.fromLTRB(16, 4, 16, 24),
          children: [CreateGoal(app: app)],
        ),
      );
    }

    final active = app.actions
        .where((item) => item.goal && item.state == null)
        .toList()
      ..sort((a, b) {
        final aDate = a.scheduledAt;
        final bDate = b.scheduledAt;
        if (aDate == null && bDate == null) return 0;
        if (aDate == null) return -1;
        if (bDate == null) return 1;
        return aDate.compareTo(bDate);
      });
    final current = active.isEmpty ? null : active.first;
    final upcoming = active.length < 2 ? <ActionItem>[] : active.sublist(1);
    final completed = app.history.where((item) => item.goal).take(6).toList();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Путь к цели'),
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
        padding: const EdgeInsets.fromLTRB(16, 0, 16, 30),
        children: [
          _GoalPathHeader(app: app),
          const SizedBox(height: 18),
          if (current == null)
            _EmptyCurrentGoalStep(app: app)
          else
            _CurrentGoalStepCard(app: app, item: current),
          const SizedBox(height: 22),
          _GoalSectionHeader(
            title: 'Дальше',
            subtitle: upcoming.isEmpty
                ? 'Следующий шаг можно добавить, когда он станет понятен.'
                : 'Не нужно выполнять всё сразу. Это ориентиры после текущего шага.',
            count: upcoming.length,
          ),
          const SizedBox(height: 9),
          if (upcoming.isEmpty)
            _GoalQuietMessage(
              icon: Icons.route_outlined,
              text: current == null
                  ? 'Сначала выберите ближайшее выполнимое действие.'
                  : 'Пока достаточно текущего шага. Продолжение можно определить после результата.',
            )
          else
            ...upcoming.asMap().entries.map(
              (entry) => _FutureGoalStepRow(
                app: app,
                item: entry.value,
                number: entry.key + 2,
              ),
            ),
          const SizedBox(height: 9),
          FilledButton.tonalIcon(
            key: const ValueKey('add-goal-step'),
            style: FilledButton.styleFrom(
              backgroundColor: const Color(0xFFE5EFEB),
              foregroundColor: green,
            ),
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => ActionEditor(app: app, goalDefault: true),
              ),
            ),
            icon: const Icon(Icons.add_rounded),
            label: const Text('Добавить следующий шаг'),
          ),
          const SizedBox(height: 22),
          _GoalInsightCard(app: app),
          if (completed.isNotEmpty) ...[
            const SizedBox(height: 22),
            _GoalSectionHeader(
              title: 'Что уже сделано',
              subtitle: 'Результаты остаются частью пути, даже если выполнена только важная часть.',
              count: completed.length,
            ),
            const SizedBox(height: 9),
            ...completed.map((item) => _GoalHistoryRow(item: item)),
          ],
          const SizedBox(height: 22),
          _OtherIntentFromGoal(app: app),
        ],
      ),
    );
  }
}

class _GoalPathHeader extends StatelessWidget {
  const _GoalPathHeader({required this.app});
  final AppState app;

  @override
  Widget build(BuildContext context) {
    final goal = app.goal!;
    final total = app.goalDone + app.goalActive;
    final progress = total == 0 ? 0.0 : app.goalDone / total;

    return Container(
      key: const ValueKey('goal-path-header'),
      padding: const EdgeInsets.fromLTRB(18, 17, 18, 17),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: const Color(0xFFDCE5E1)),
        boxShadow: const [
          BoxShadow(
            color: Color(0x10172E29),
            blurRadius: 18,
            offset: Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.flag_outlined, color: green, size: 19),
              SizedBox(width: 7),
              Text(
                'ГЛАВНАЯ ЦЕЛЬ',
                style: TextStyle(
                  color: green,
                  fontSize: 10.5,
                  fontWeight: FontWeight.w900,
                  letterSpacing: .9,
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Text(
            goal.title,
            style: const TextStyle(
              color: ink,
              fontSize: 24,
              height: 1.12,
              fontWeight: FontWeight.w900,
            ),
          ),
          if (goal.result.isNotEmpty) ...[
            const SizedBox(height: 8),
            Text(
              goal.result,
              style: const TextStyle(
                color: Color(0xFF596762),
                fontSize: 13.5,
                height: 1.4,
              ),
            ),
          ],
          if (goal.areas.isNotEmpty) ...[
            const SizedBox(height: 12),
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
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  )
                  .toList(),
            ),
          ],
          const SizedBox(height: 15),
          ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: LinearProgressIndicator(
              value: progress,
              minHeight: 6,
              backgroundColor: const Color(0xFFE8EEEB),
              valueColor: const AlwaysStoppedAnimation(green),
            ),
          ),
          const SizedBox(height: 9),
          Row(
            children: [
              _GoalMetric(value: '${app.goalDone}', label: 'завершено'),
              const SizedBox(width: 8),
              _GoalMetric(value: '${app.goalActive}', label: 'в пути'),
              const Spacer(),
              Text(
                total == 0 ? 'Начните с одного шага' : 'Двигайтесь по одному шагу',
                style: const TextStyle(
                  color: Color(0xFF75817D),
                  fontSize: 11.5,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _GoalMetric extends StatelessWidget {
  const _GoalMetric({required this.value, required this.label});
  final String value, label;

  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
    decoration: BoxDecoration(
      color: const Color(0xFFEAF3EF),
      borderRadius: BorderRadius.circular(14),
    ),
    child: Text.rich(
      TextSpan(
        children: [
          TextSpan(
            text: value,
            style: const TextStyle(fontWeight: FontWeight.w900, color: green),
          ),
          TextSpan(
            text: ' $label',
            style: const TextStyle(color: Color(0xFF65726D), fontSize: 11.5),
          ),
        ],
      ),
    ),
  );
}

class _CurrentGoalStepCard extends StatelessWidget {
  const _CurrentGoalStepCard({required this.app, required this.item});
  final AppState app;
  final ActionItem item;

  void _open(BuildContext context, {bool difficulty = false}) => Navigator.push(
    context,
    MaterialPageRoute(
      builder: (_) => Session(
        app: app,
        item: item,
        openDifficultyOnEnter: difficulty,
      ),
    ),
  );

  @override
  Widget build(BuildContext context) {
    final minimum = item.small.trim();
    return Container(
      key: const ValueKey('current-goal-step'),
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF173C36), Color(0xFF356A60)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(25),
        boxShadow: const [
          BoxShadow(
            color: Color(0x25172E29),
            blurRadius: 20,
            offset: Offset(0, 10),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Text(
                'СЕЙЧАС',
                style: TextStyle(
                  color: mint,
                  fontSize: 11,
                  fontWeight: FontWeight.w900,
                  letterSpacing: 1,
                ),
              ),
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 5),
                decoration: BoxDecoration(
                  color: Colors.white12,
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(supportIcon(item.support), color: mint, size: 15),
                    const SizedBox(width: 5),
                    Text(
                      supportName(item.support),
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 11,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 13),
          Text(
            item.title,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 23,
              height: 1.14,
              fontWeight: FontWeight.w900,
            ),
          ),
          if (item.scheduledAt != null) ...[
            const SizedBox(height: 8),
            Text(
              '${shortDate(item.scheduledAt!)} · ${clockTime(item.scheduledAt!)}',
              style: const TextStyle(color: Color(0xFFD4E0DD), fontSize: 12.5),
            ),
          ],
          const SizedBox(height: 14),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(13),
            decoration: BoxDecoration(
              color: Colors.white10,
              borderRadius: BorderRadius.circular(17),
              border: Border.all(color: Colors.white12),
            ),
            child: minimum.isEmpty
                ? Row(
                    children: [
                      const Expanded(
                        child: Text(
                          'Минимальный вариант пока не выбран.',
                          style: TextStyle(color: Color(0xFFD7E2DF), fontSize: 12.5),
                        ),
                      ),
                      TextButton(
                        style: TextButton.styleFrom(foregroundColor: mint),
                        onPressed: () => Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (_) => ActionEditor(
                              app: app,
                              goalDefault: true,
                              existing: item,
                            ),
                          ),
                        ),
                        child: const Text('Добавить'),
                      ),
                    ],
                  )
                : Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'МИНИМАЛЬНЫЙ ВАРИАНТ',
                        style: TextStyle(
                          color: mint,
                          fontSize: 10,
                          fontWeight: FontWeight.w900,
                          letterSpacing: .75,
                        ),
                      ),
                      const SizedBox(height: 5),
                      Text(
                        minimum,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 13,
                          height: 1.35,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ],
                  ),
          ),
          const SizedBox(height: 14),
          Row(
            children: [
              Expanded(
                child: FilledButton.icon(
                  key: const ValueKey('goal-start-button'),
                  style: FilledButton.styleFrom(
                    backgroundColor: mint,
                    foregroundColor: ink,
                  ),
                  onPressed: () => _open(context),
                  icon: const Icon(Icons.play_arrow_rounded),
                  label: const Text('Начать'),
                ),
              ),
              const SizedBox(width: 9),
              Expanded(
                child: OutlinedButton.icon(
                  key: const ValueKey('goal-difficulty-button'),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: Colors.white,
                    side: const BorderSide(color: Color(0x99FFFFFF)),
                  ),
                  onPressed: () => _open(context, difficulty: true),
                  icon: const Icon(Icons.support_rounded),
                  label: const Text('Трудно начать'),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _EmptyCurrentGoalStep extends StatelessWidget {
  const _EmptyCurrentGoalStep({required this.app});
  final AppState app;

  @override
  Widget build(BuildContext context) => Container(
    key: const ValueKey('empty-current-goal-step'),
    padding: const EdgeInsets.all(18),
    decoration: BoxDecoration(
      color: const Color(0xFFEAF3EF),
      borderRadius: BorderRadius.circular(22),
      border: Border.all(color: const Color(0xFFD2E2DB)),
    ),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'СЕЙЧАС',
          style: TextStyle(
            color: green,
            fontSize: 11,
            fontWeight: FontWeight.w900,
            letterSpacing: 1,
          ),
        ),
        const SizedBox(height: 9),
        const Text(
          'Выберите один ближайший шаг',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.w900),
        ),
        const SizedBox(height: 6),
        const Text(
          'Не весь план целиком — только действие, которое реально начать следующим.',
          style: TextStyle(height: 1.4),
        ),
        const SizedBox(height: 13),
        FilledButton.icon(
          onPressed: () => Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => ActionEditor(app: app, goalDefault: true),
            ),
          ),
          icon: const Icon(Icons.add_task_rounded),
          label: const Text('Выбрать ближайший шаг'),
        ),
      ],
    ),
  );
}

class _GoalSectionHeader extends StatelessWidget {
  const _GoalSectionHeader({
    required this.title,
    required this.subtitle,
    required this.count,
  });
  final String title, subtitle;
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
                fontSize: 19,
                fontWeight: FontWeight.w900,
              ),
            ),
            const SizedBox(height: 3),
            Text(
              subtitle,
              style: const TextStyle(
                color: Color(0xFF697570),
                fontSize: 12.5,
                height: 1.35,
              ),
            ),
          ],
        ),
      ),
      if (count > 0) ...[
        const SizedBox(width: 10),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 5),
          decoration: BoxDecoration(
            color: const Color(0xFFE5EFEB),
            borderRadius: BorderRadius.circular(20),
          ),
          child: Text(
            '$count',
            style: const TextStyle(color: green, fontWeight: FontWeight.w900),
          ),
        ),
      ],
    ],
  );
}

class _FutureGoalStepRow extends StatelessWidget {
  const _FutureGoalStepRow({
    required this.app,
    required this.item,
    required this.number,
  });
  final AppState app;
  final ActionItem item;
  final int number;

  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.only(bottom: 8),
    child: Material(
      color: Colors.white,
      clipBehavior: Clip.antiAlias,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(18),
        side: const BorderSide(color: Color(0xFFE0E6E2)),
      ),
      child: InkWell(
        onTap: () => Navigator.push(
          context,
          MaterialPageRoute(builder: (_) => Session(app: app, item: item)),
        ),
        child: Padding(
          padding: const EdgeInsets.fromLTRB(13, 12, 11, 12),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 34,
                height: 34,
                alignment: Alignment.center,
                decoration: BoxDecoration(
                  color: const Color(0xFFEAF3EF),
                  borderRadius: BorderRadius.circular(11),
                ),
                child: Text(
                  '$number',
                  style: const TextStyle(color: green, fontWeight: FontWeight.w900),
                ),
              ),
              const SizedBox(width: 11),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      item.title,
                      style: const TextStyle(fontWeight: FontWeight.w800, height: 1.3),
                    ),
                    const SizedBox(height: 5),
                    Row(
                      children: [
                        Icon(supportIcon(item.support), size: 15, color: green),
                        const SizedBox(width: 5),
                        Expanded(
                          child: Text(
                            item.small.isNotEmpty
                                ? '${supportName(item.support)} · минимум: ${item.small}'
                                : supportName(item.support),
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                            style: const TextStyle(
                              color: Color(0xFF6B7772),
                              fontSize: 11.5,
                              height: 1.3,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 5),
              const Icon(Icons.chevron_right_rounded, color: Color(0xFF8B9691)),
            ],
          ),
        ),
      ),
    ),
  );
}

class _GoalInsightCard extends StatelessWidget {
  const _GoalInsightCard({required this.app});
  final AppState app;

  @override
  Widget build(BuildContext context) {
    final rated = app.history
        .where((item) => item.goal && item.supportEffect != null)
        .toList();
    final scores = <Support, int>{};
    for (final item in rated) {
      final points = switch (item.supportEffect!) {
        SupportEffect.yes => 2,
        SupportEffect.partly => 1,
        SupportEffect.no => 0,
      };
      scores[item.support] = (scores[item.support] ?? 0) + points;
    }
    Support? best;
    var bestScore = 0;
    for (final entry in scores.entries) {
      if (entry.value > bestScore) {
        best = entry.key;
        bestScore = entry.value;
      }
    }

    final title = rated.isEmpty
        ? 'Наблюдение появится после нескольких действий'
        : best == null
        ? 'Пока ни один способ не выделился'
        : 'Пока чаще помогает: ${supportName(best)}';
    final text = rated.isEmpty
        ? 'После выполнения приложение спросит, помогла ли выбранная поддержка начать. Ответы постепенно соберутся здесь.'
        : best == null
        ? 'Это нормально. Попробуйте разные условия и оценивайте их после действия.'
        : 'Основано на ${rated.length} ${_ratingWord(rated.length)}. Это предварительное наблюдение, а не жёсткое правило.';

    return Container(
      key: const ValueKey('goal-insight-card'),
      padding: const EdgeInsets.all(17),
      decoration: BoxDecoration(
        color: const Color(0xFFFFF5E4),
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: const Color(0x55C89B4A)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.auto_graph_rounded, color: Color(0xFF966F2C), size: 20),
              SizedBox(width: 7),
              Text(
                'ЧТО ПОМОГАЕТ ВАМ ДВИГАТЬСЯ',
                style: TextStyle(
                  color: Color(0xFF966F2C),
                  fontSize: 10.5,
                  fontWeight: FontWeight.w900,
                  letterSpacing: .7,
                ),
              ),
            ],
          ),
          const SizedBox(height: 11),
          Text(title, style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w900)),
          const SizedBox(height: 6),
          Text(text, style: const TextStyle(height: 1.4)),
        ],
      ),
    );
  }

  static String _ratingWord(int count) {
    final last = count % 10;
    final lastTwo = count % 100;
    if (last == 1 && lastTwo != 11) return 'оценке';
    if (last >= 2 && last <= 4 && (lastTwo < 12 || lastTwo > 14)) {
      return 'оценках';
    }
    return 'оценках';
  }
}

class _GoalQuietMessage extends StatelessWidget {
  const _GoalQuietMessage({required this.icon, required this.text});
  final IconData icon;
  final String text;

  @override
  Widget build(BuildContext context) => Container(
    width: double.infinity,
    padding: const EdgeInsets.all(14),
    decoration: BoxDecoration(
      color: const Color(0xFFF0F4F2),
      borderRadius: BorderRadius.circular(16),
    ),
    child: Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, color: green, size: 20),
        const SizedBox(width: 9),
        Expanded(child: Text(text, style: const TextStyle(fontSize: 12.8, height: 1.38))),
      ],
    ),
  );
}

class _GoalHistoryRow extends StatelessWidget {
  const _GoalHistoryRow({required this.item});
  final HistoryItem item;

  @override
  Widget build(BuildContext context) {
    final result = switch (item.state) {
      ResultState.done => 'Выполнено',
      ResultState.part => 'Сделана важная часть',
      ResultState.moved => 'Перенесено',
      ResultState.missed => 'Не получилось',
    };
    final effect = switch (item.supportEffect) {
      SupportEffect.yes => 'поддержка помогла',
      SupportEffect.partly => 'помогла частично',
      SupportEffect.no => 'не помогла',
      null => '',
    };

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.fromLTRB(12, 11, 11, 11),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE3E8E5)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 34,
            height: 34,
            decoration: BoxDecoration(
              color: supportColor(item.support),
              borderRadius: BorderRadius.circular(11),
            ),
            child: Icon(resultIcon(item.state), color: ink, size: 19),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  item.title,
                  style: const TextStyle(fontSize: 13.5, fontWeight: FontWeight.w800),
                ),
                const SizedBox(height: 4),
                Text(
                  '$result · ${supportName(item.support)}${effect.isEmpty ? '' : ' · $effect'}',
                  style: const TextStyle(
                    color: Color(0xFF6F7B76),
                    fontSize: 11.5,
                    height: 1.3,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _OtherIntentFromGoal extends StatelessWidget {
  const _OtherIntentFromGoal({required this.app});
  final AppState app;

  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.fromLTRB(15, 14, 13, 14),
    decoration: BoxDecoration(
      color: const Color(0xFFF2F4F3),
      borderRadius: BorderRadius.circular(18),
    ),
    child: Row(
      children: [
        const Icon(Icons.inbox_outlined, color: green),
        const SizedBox(width: 10),
        const Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Не всё должно становиться целью', style: TextStyle(fontWeight: FontWeight.w800)),
              SizedBox(height: 3),
              Text(
                'Напоминания, обычные дела и практики хранятся отдельно.',
                style: TextStyle(color: Color(0xFF6C7873), fontSize: 11.8, height: 1.3),
              ),
            ],
          ),
        ),
        TextButton(
          key: const ValueKey('add-other-from-goal'),
          onPressed: () => Navigator.push(
            context,
            MaterialPageRoute(builder: (_) => IntentChooserPage(app: app)),
          ),
          child: const Text('Добавить'),
        ),
      ],
    ),
  );
}'''

text = replace_class(
    text,
    'GoalScreen extends StatelessWidget',
    'GoalEditor extends StatefulWidget',
    GOAL_SCREEN,
)

# Let the goal workspace open the existing calm difficulty flow directly.
old_session = '''class Session extends StatefulWidget {
  const Session({required this.app, required this.item, super.key});
  final AppState app;
  final ActionItem item;'''
new_session = '''class Session extends StatefulWidget {
  const Session({
    required this.app,
    required this.item,
    this.openDifficultyOnEnter = false,
    super.key,
  });
  final AppState app;
  final ActionItem item;
  final bool openDifficultyOnEnter;'''
if old_session not in text:
    raise SystemExit('Session constructor anchor not found')
text = text.replace(old_session, new_session, 1)

old_init = '''  void initState() {
    super.initState();
    left = widget.item.minutes * 60;
  }'''
new_init = '''  void initState() {
    super.initState();
    left = widget.item.minutes * 60;
    if (widget.openDifficultyOnEnter) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted && !started) openStartDifficulty();
      });
    }
  }'''
if old_init not in text:
    raise SystemExit('Session initState anchor not found')
text = text.replace(old_init, new_init, 1)

main_path.write_text(text, encoding='utf-8')

pubspec = pubspec_path.read_text(encoding='utf-8')
pubspec = re.sub(
    r'^version:\s*[^\n]+',
    'version: 0.8.0+24',
    pubspec,
    count=1,
    flags=re.M,
)
pubspec_path.write_text(pubspec, encoding='utf-8')
print('Applied v0.8.0 premium goal path workspace')
