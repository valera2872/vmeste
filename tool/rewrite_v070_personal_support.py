from pathlib import Path
import re

main_path = Path('lib/main.dart')
pubspec_path = Path('pubspec.yaml')
text = main_path.read_text(encoding='utf-8')


def replace_class(source: str, name: str, next_name: str, replacement: str) -> str:
    start = source.index(f'class {name}')
    end = source.index(f'class {next_name}', start)
    return source[:start] + replacement.rstrip() + '\n\n' + source[end:]


# Persist whether the selected support actually helped the person start.
text = text.replace(
    'enum ResultState { done, part, moved, missed }\n\nenum RoutineSchedule',
    'enum ResultState { done, part, moved, missed }\n\nenum SupportEffect { yes, partly, no }\n\nenum RoutineSchedule',
    1,
)
text = text.replace(
    'enum BlockerOutcome { continueWork, continueSmall, together, finish }\n\nenum StartProblem',
    'enum BlockerOutcome { continueWork, continueSmall, together, finish }\n\nenum StartDifficultyChoice { clarify, minimum, focus, together, report }\n\nenum StartProblem',
    1,
)

text = text.replace(
    "    this.actionId = '',\n    this.routineResult,\n  })",
    "    this.actionId = '',\n    this.routineResult,\n    this.supportEffect,\n  })",
    1,
)
text = text.replace(
    '  final String actionId;\n  final RoutineResult? routineResult;',
    '  final String actionId;\n  final RoutineResult? routineResult;\n  SupportEffect? supportEffect;',
    1,
)
text = text.replace(
    "    'routineResult': routineResult?.name,\n  };",
    "    'routineResult': routineResult?.name,\n    'supportEffect': supportEffect?.name,\n  };",
    1,
)
text = text.replace(
    "    routineResult: j['routineResult'] == null\n        ? null\n        : RoutineResult.values.firstWhere(\n            (e) => e.name == j['routineResult'],\n            orElse: () => RoutineResult.partial,\n          ),\n  );",
    "    routineResult: j['routineResult'] == null\n        ? null\n        : RoutineResult.values.firstWhere(\n            (e) => e.name == j['routineResult'],\n            orElse: () => RoutineResult.partial,\n          ),\n    supportEffect: j['supportEffect'] == null\n        ? null\n        : SupportEffect.values.firstWhere(\n            (e) => e.name == j['supportEffect'],\n            orElse: () => SupportEffect.partly,\n          ),\n  );",
    1,
)
text = text.replace('static const schemaVersion = 2;', 'static const schemaVersion = 3;', 1)

set_support = '''  void setSupport(ActionItem action, Support support) {
    action.support = support;
    action.updatedAt = DateTime.now();
    notifyListeners();
    save();
  }'''
record_effect = set_support + r'''

  void recordSupportEffect(ActionItem action, SupportEffect effect) {
    HistoryItem? target;
    for (final entry in history) {
      if (entry.actionId == action.id) {
        target = entry;
        break;
      }
    }
    if (target == null) return;
    target.supportEffect = effect;
    notifyListeners();
    save();
  }'''
if set_support not in text:
    raise SystemExit('setSupport anchor not found')
text = text.replace(set_support, record_effect, 1)

# Add a visible help path before the timer starts.
finish_anchor = '  Future<void> finish(ResultState state) async {'
finish_at = text.index(finish_anchor, text.index('class _SessionState'))
start_help_method = r'''  Future<void> openStartDifficulty() async {
    final choice = await showModalBottomSheet<StartDifficultyChoice>(
      context: context,
      isScrollControlled: true,
      useSafeArea: true,
      showDragHandle: true,
      builder: (_) => DraggableScrollableSheet(
        expand: false,
        initialChildSize: .78,
        minChildSize: .56,
        maxChildSize: .94,
        builder: (context, controller) => StartDifficultySheet(
          item: widget.item,
          scrollController: controller,
        ),
      ),
    );
    if (choice == null || !mounted) return;

    switch (choice) {
      case StartDifficultyChoice.clarify:
        widget.app.setSupport(widget.item, Support.ai);
        start();
      case StartDifficultyChoice.minimum:
        if (widget.item.small.isEmpty) {
          widget.item.small = SupportLogic.smallStep(widget.item.title);
          widget.app.updateAction(widget.item);
        }
        if (left > 300) left = 300;
        start();
      case StartDifficultyChoice.focus:
        if (left > 300) left = 300;
        start();
      case StartDifficultyChoice.together:
        widget.app.setSupport(widget.item, Support.together);
        await shareStartMessage(
          widget.item.title,
          widget.item.minutes,
          Support.together,
        );
        if (mounted) start();
      case StartDifficultyChoice.report:
        widget.app.setSupport(widget.item, Support.report);
        await shareStartMessage(
          widget.item.title,
          widget.item.minutes,
          Support.report,
        );
        if (mounted) start();
    }
  }

'''
text = text[:finish_at] + start_help_method + text[finish_at:]

session_start_anchor = '''            FilledButton.icon(
              onPressed: start,
              icon: const Icon(Icons.play_arrow),
              label: Text('Начать на ${widget.item.minutes} минут'),
            ),
          ] else ...['''
session_start_replacement = '''            FilledButton.icon(
              onPressed: start,
              icon: const Icon(Icons.play_arrow),
              label: Text('Начать на ${widget.item.minutes} минут'),
            ),
            const SizedBox(height: 9),
            OutlinedButton.icon(
              key: const ValueKey('start-difficulty-button'),
              onPressed: openStartDifficulty,
              icon: const Icon(Icons.support_rounded),
              label: const Text('Трудно начать'),
            ),
          ] else ...['''
if session_start_anchor not in text:
    raise SystemExit('Session start anchor not found')
text = text.replace(session_start_anchor, session_start_replacement, 1)

START_DIFFICULTY = r'''class StartDifficultySheet extends StatelessWidget {
  const StartDifficultySheet({
    required this.item,
    required this.scrollController,
    super.key,
  });

  final ActionItem item;
  final ScrollController scrollController;

  @override
  Widget build(BuildContext context) {
    final minimum = item.small.isNotEmpty
        ? item.small
        : SupportLogic.smallStep(item.title);
    final firstStep = SupportLogic.steps(item.title).first;

    return ListView(
      key: const ValueKey('start-difficulty-sheet'),
      controller: scrollController,
      padding: const EdgeInsets.fromLTRB(18, 2, 18, 30),
      children: [
        const Text(
          'Что мешает начать?',
          style: TextStyle(fontSize: 24, fontWeight: FontWeight.w900),
        ),
        const SizedBox(height: 7),
        const Text(
          'Выберите ближайшую трудность. Приложение сразу изменит одно условие, а не даст общий совет.',
        ),
        const SizedBox(height: 15),
        _StartDifficultyOption(
          title: 'Не понимаю, с чего начать',
          text: firstStep,
          icon: Icons.route_outlined,
          onTap: () => Navigator.pop(
            context,
            StartDifficultyChoice.clarify,
          ),
        ),
        _StartDifficultyOption(
          title: 'Действие слишком большое',
          text: 'Начните с минимального варианта: $minimum',
          icon: Icons.compress_rounded,
          onTap: () => Navigator.pop(
            context,
            StartDifficultyChoice.minimum,
          ),
        ),
        _StartDifficultyOption(
          title: 'Нет сил или постоянно отвлекаюсь',
          text: 'Оставьте только пять минут и уберите одно отвлечение.',
          icon: Icons.hourglass_bottom_rounded,
          onTap: () => Navigator.pop(
            context,
            StartDifficultyChoice.focus,
          ),
        ),
        _StartDifficultyOption(
          title: 'Нужен человек рядом',
          text: 'Позовите знакомого начать одновременно или остаться на связи.',
          icon: Icons.people_alt_outlined,
          onTap: () => Navigator.pop(
            context,
            StartDifficultyChoice.together,
          ),
        ),
        _StartDifficultyOption(
          title: 'Тревожно начинать или нужен внешний импульс',
          text: 'Сообщите знакомому, что начинаете, и договоритесь отправить результат.',
          icon: Icons.verified_outlined,
          onTap: () => Navigator.pop(
            context,
            StartDifficultyChoice.report,
          ),
        ),
      ],
    );
  }
}

class _StartDifficultyOption extends StatelessWidget {
  const _StartDifficultyOption({
    required this.title,
    required this.text,
    required this.icon,
    required this.onTap,
  });

  final String title;
  final String text;
  final IconData icon;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) => Container(
    margin: const EdgeInsets.only(bottom: 10),
    decoration: BoxDecoration(
      color: Colors.white,
      borderRadius: BorderRadius.circular(20),
      border: Border.all(color: const Color(0xFFE0E5E1)),
    ),
    child: ListTile(
      contentPadding: const EdgeInsets.fromLTRB(14, 10, 12, 10),
      leading: Container(
        width: 44,
        height: 44,
        decoration: BoxDecoration(
          color: const Color(0xFFE7F2ED),
          borderRadius: BorderRadius.circular(14),
        ),
        child: Icon(icon, color: green),
      ),
      title: Text(title, style: const TextStyle(fontWeight: FontWeight.w800)),
      subtitle: Padding(
        padding: const EdgeInsets.only(top: 5),
        child: Text(text),
      ),
      trailing: const Icon(Icons.chevron_right_rounded),
      onTap: onTap,
    ),
  );
}'''

blocker_start = text.index('class Blocker extends StatelessWidget')
text = text[:blocker_start] + START_DIFFICULTY + '\n\n' + text[blocker_start:]

RESULT_PAGE = r'''class ResultPage extends StatefulWidget {
  const ResultPage({
    required this.app,
    required this.item,
    required this.state,
    super.key,
  });

  final AppState app;
  final ActionItem item;
  final ResultState state;

  @override
  State<ResultPage> createState() => _ResultPageState();
}

class _ResultPageState extends State<ResultPage> {
  SupportEffect? selected;

  @override
  void initState() {
    super.initState();
    for (final entry in widget.app.history) {
      if (entry.actionId == widget.item.id) {
        selected = entry.supportEffect;
        break;
      }
    }
  }

  void chooseEffect(SupportEffect effect) {
    widget.app.recordSupportEffect(widget.item, effect);
    setState(() => selected = effect);
  }

  @override
  Widget build(BuildContext context) {
    final state = widget.state;
    final item = widget.item;
    final app = widget.app;
    final ok = state == ResultState.done || state == ResultState.part;
    final moved = state == ResultState.moved;
    final canShare =
        item.support == Support.together ||
        item.support == Support.report ||
        item.support == Support.curator;

    return Scaffold(
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.fromLTRB(24, 28, 24, 30),
          children: [
            Container(
              width: 74,
              height: 74,
              alignment: Alignment.center,
              decoration: BoxDecoration(
                color: ok
                    ? mint
                    : moved
                    ? const Color(0xFFDCE7F2)
                    : const Color(0xFFE7E1D5),
                borderRadius: BorderRadius.circular(24),
              ),
              child: Icon(
                ok
                    ? Icons.check_rounded
                    : moved
                    ? Icons.event_available_outlined
                    : Icons.refresh_rounded,
                size: 39,
                color: ink,
              ),
            ),
            const SizedBox(height: 22),
            Text(
              state == ResultState.done
                  ? 'Действие завершено.'
                  : state == ResultState.part
                  ? 'Важная часть уже сделана.'
                  : moved
                  ? 'Дело осталось в вашем плане.'
                  : 'Сегодня не получилось — это не конец пути.',
              style: Theme.of(context).textTheme.headlineLarge,
            ),
            const SizedBox(height: 10),
            Text(
              moved && item.scheduledAt != null
                  ? 'Вернёмся к делу «${item.title}» ${shortDate(item.scheduledAt!)} в ${clockTime(item.scheduledAt!)}.'
                  : ok
                  ? 'Результат по делу «${item.title}» записан. Теперь можно выбрать следующий шаг.'
                  : 'Действие сохранено в истории. Позже можно изменить условия и попробовать снова.',
            ),
            if (ok) ...[
              const SizedBox(height: 20),
              Container(
                key: const ValueKey('support-feedback-card'),
                padding: const EdgeInsets.fromLTRB(17, 16, 17, 16),
                decoration: BoxDecoration(
                  color: const Color(0xFFEAF4EF),
                  borderRadius: BorderRadius.circular(22),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Этот способ помог вам начать?',
                      style: TextStyle(
                        color: ink,
                        fontSize: 17,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      supportName(item.support),
                      style: const TextStyle(color: Color(0xFF5D6B66)),
                    ),
                    const SizedBox(height: 12),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: [
                        _effectChip('Да', SupportEffect.yes),
                        _effectChip('Частично', SupportEffect.partly),
                        _effectChip('Нет', SupportEffect.no),
                      ],
                    ),
                    if (selected != null) ...[
                      const SizedBox(height: 10),
                      Text(
                        supportEffectMessage(selected!),
                        key: const ValueKey('support-feedback-saved'),
                        style: const TextStyle(
                          color: green,
                          fontSize: 12.5,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ],
            if (canShare && ok) ...[
              const SizedBox(height: 14),
              OutlinedButton.icon(
                onPressed: () => shareResultMessage(item, state),
                icon: const Icon(Icons.send_rounded),
                label: const Text('Отправить результат'),
              ),
            ],
            if (item.goal && ok) ...[
              const SizedBox(height: 10),
              OutlinedButton.icon(
                onPressed: () => Navigator.pushReplacement(
                  context,
                  MaterialPageRoute(
                    builder: (_) => ActionEditor(
                      app: app,
                      goalDefault: true,
                      initialTitle: state == ResultState.part
                          ? 'Продолжить: ${item.title}'
                          : null,
                    ),
                  ),
                ),
                icon: const Icon(Icons.add_task_rounded),
                label: Text(
                  state == ResultState.part
                      ? 'Записать, что осталось'
                      : 'Добавить следующий шаг',
                ),
              ),
            ],
            const SizedBox(height: 14),
            FilledButton(
              onPressed: () => Navigator.popUntil(context, (route) => route.isFirst),
              child: const Text('Вернуться к плану'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _effectChip(String label, SupportEffect effect) => ChoiceChip(
    key: ValueKey('support-effect-${effect.name}'),
    label: Text(label),
    selected: selected == effect,
    onSelected: (_) => chooseEffect(effect),
  );
}'''

result_start = text.index('class ResultPage extends StatelessWidget')
result_end = text.index('Future<void> shareStartMessage', result_start)
text = text[:result_start] + RESULT_PAGE + '\n\n' + text[result_end:]

PROGRESS = r'''class Progress extends StatelessWidget {
  const Progress({required this.app, super.key});
  final AppState app;

  @override
  Widget build(BuildContext context) {
    final done = app.history.where((e) => e.state == ResultState.done).length;
    final part = app.history.where((e) => e.state == ResultState.part).length;
    final stops = app.history
        .where(
          (e) => e.state == ResultState.moved || e.state == ResultState.missed,
        )
        .length;
    final weekStart = DateTime.now().subtract(const Duration(days: 7));
    final week = app.history.where((e) => !e.date.isBefore(weekStart)).toList();
    final feedback = app.history.where((e) => e.supportEffect != null).toList();
    final best = strongestSupport(feedback);
    ActionItem? nextAction;
    for (final item in app.actions) {
      if (item.state == null && item.goal) {
        nextAction = item;
        break;
      }
    }

    return Scaffold(
      appBar: AppBar(title: const Text('История')),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(18, 4, 18, 90),
        children: [
          Text(
            'Что уже сделано',
            style: Theme.of(context).textTheme.headlineMedium,
          ),
          const SizedBox(height: 7),
          const Text(
            'Здесь сохраняются результаты и постепенно становится видно, какие условия помогают вам начинать.',
          ),
          const SizedBox(height: 17),
          WeeklyReviewCard(week: week, nextAction: nextAction),
          const SizedBox(height: 12),
          PersonalInsightCard(feedback: feedback, best: best),
          const SizedBox(height: 16),
          Row(
            children: [
              stat('$done', 'выполнено'),
              const SizedBox(width: 8),
              stat('$part', 'частично'),
              const SizedBox(width: 8),
              stat('$stops', 'перенесено'),
            ],
          ),
          const SizedBox(height: 20),
          const Text(
            'История действий',
            style: TextStyle(fontWeight: FontWeight.w900, fontSize: 20),
          ),
          const SizedBox(height: 9),
          if (app.history.isEmpty)
            const Card(
              child: Padding(
                padding: EdgeInsets.all(18),
                child: Text(
                  'После первого действия здесь появятся результат и выбранный способ поддержки.',
                ),
              ),
            )
          else
            ...app.history.map(
              (e) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Card(
                  child: ListTile(
                    leading: CircleAvatar(
                      backgroundColor: supportColor(e.support),
                      child: Icon(supportIcon(e.support), color: ink),
                    ),
                    title: Text(
                      e.title,
                      style: const TextStyle(fontWeight: FontWeight.w800),
                    ),
                    subtitle: Text(
                      '${supportName(e.support)}${e.minutes > 0 ? ' · ${e.minutes} минут' : ''} · ${e.date.day}.${e.date.month}.${e.date.year}${e.supportEffect == null ? '' : ' · ${supportEffectShort(e.supportEffect!)}'}',
                    ),
                    trailing: Icon(resultIcon(e.state), color: green),
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget stat(String value, String label) => Expanded(
    child: Container(
      padding: const EdgeInsets.symmetric(vertical: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(19),
      ),
      child: Column(
        children: [
          Text(
            value,
            style: const TextStyle(fontSize: 24, fontWeight: FontWeight.w900),
          ),
          Text(label, style: const TextStyle(fontSize: 11)),
        ],
      ),
    ),
  );
}

class WeeklyReviewCard extends StatelessWidget {
  const WeeklyReviewCard({required this.week, required this.nextAction, super.key});
  final List<HistoryItem> week;
  final ActionItem? nextAction;

  @override
  Widget build(BuildContext context) {
    final movement = week
        .where((e) => e.state == ResultState.done || e.state == ResultState.part)
        .length;
    final postponed = week
        .where((e) => e.state == ResultState.moved || e.state == ResultState.missed)
        .length;

    return Container(
      key: const ValueKey('weekly-review-card'),
      padding: const EdgeInsets.fromLTRB(17, 16, 17, 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(23),
        border: Border.all(color: const Color(0xFFE1E6E2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.calendar_view_week_outlined, color: green, size: 21),
              SizedBox(width: 8),
              Text(
                'Недельный обзор',
                style: TextStyle(fontSize: 17, fontWeight: FontWeight.w800),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Text(
            week.isEmpty
                ? 'На этой неделе пока нет записанных результатов.'
                : '$movement действий продвинули вас вперёд. $postponed потребовали переноса или нового подхода.',
            style: const TextStyle(color: Color(0xFF4E5C57), height: 1.4),
          ),
          const SizedBox(height: 10),
          Text(
            nextAction == null
                ? 'Следующий шаг можно выбрать, когда появится готовность.'
                : 'Ближайший шаг: ${nextAction!.title}',
            style: const TextStyle(color: green, fontWeight: FontWeight.w700),
          ),
        ],
      ),
    );
  }
}

class PersonalInsightCard extends StatelessWidget {
  const PersonalInsightCard({
    required this.feedback,
    required this.best,
    super.key,
  });
  final List<HistoryItem> feedback;
  final Support? best;

  @override
  Widget build(BuildContext context) {
    final text = feedback.isEmpty
        ? 'После нескольких действий приложение покажет, какие способы чаще помогают вам начать.'
        : feedback.length == 1
        ? 'Пока есть одно наблюдение: ${supportName(feedback.first.support)} ${feedback.first.supportEffect == SupportEffect.no ? 'не помог начать' : 'помог начать хотя бы частично'}.'
        : best == null
        ? 'Пока нет одного явно подходящего способа. Продолжайте отмечать, что помогло.'
        : 'Сейчас чаще всего помогает: ${supportName(best!)}. Это предварительное наблюдение, а не жёсткое правило.';

    return Container(
      key: const ValueKey('personal-insight-card'),
      padding: const EdgeInsets.fromLTRB(17, 15, 17, 15),
      decoration: BoxDecoration(
        color: const Color(0xFFEAF4EF),
        borderRadius: BorderRadius.circular(22),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.auto_graph_rounded, color: green, size: 23),
          const SizedBox(width: 11),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Что помогает вам начинать',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800),
                ),
                const SizedBox(height: 5),
                Text(text, style: const TextStyle(height: 1.4)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}'''

text = replace_class(
    text,
    'Progress extends StatelessWidget',
    'Session extends StatefulWidget',
    PROGRESS,
)

# Shared cautious inference helpers.
helper_anchor = 'List<int> routineDays(ActionItem item)'
helper_at = text.index(helper_anchor)
HELPERS = r'''String supportEffectShort(SupportEffect effect) => switch (effect) {
  SupportEffect.yes => 'помогло',
  SupportEffect.partly => 'частично помогло',
  SupportEffect.no => 'не помогло',
};

String supportEffectMessage(SupportEffect effect) => switch (effect) {
  SupportEffect.yes => 'Сохранили: этот способ помог начать.',
  SupportEffect.partly => 'Сохранили: способ помог только частично.',
  SupportEffect.no => 'Сохранили: в следующий раз стоит изменить поддержку.',
};

Support? strongestSupport(List<HistoryItem> feedback) {
  if (feedback.isEmpty) return null;
  final scores = <Support, int>{};
  for (final entry in feedback) {
    final points = switch (entry.supportEffect) {
      SupportEffect.yes => 2,
      SupportEffect.partly => 1,
      SupportEffect.no => 0,
      null => 0,
    };
    scores[entry.support] = (scores[entry.support] ?? 0) + points;
  }
  Support? best;
  var bestScore = 0;
  for (final entry in scores.entries) {
    if (entry.value > bestScore) {
      best = entry.key;
      bestScore = entry.value;
    }
  }
  return best;
}

'''
text = text[:helper_at] + HELPERS + text[helper_at:]

main_path.write_text(text, encoding='utf-8')

pubspec = pubspec_path.read_text(encoding='utf-8')
pubspec = re.sub(r'^version:\s*[^\n]+', 'version: 0.7.0+22', pubspec, count=1, flags=re.M)
pubspec_path.write_text(pubspec, encoding='utf-8')
print('Applied v0.7 personal support learning core')
