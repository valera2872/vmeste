from pathlib import Path

main_path = Path("lib/main.dart")
text = main_path.read_text(encoding="utf-8")

def replace_block(source: str, start: str, end: str, replacement: str) -> str:
    i = source.index(start)
    j = source.index(end, i)
    return source[:i] + replacement.rstrip() + "\n\n" + source[j:]

if "class QuickStartWizard" not in text:
    text = text.replace(
        "import 'package:shared_preferences/shared_preferences.dart';\n",
        "import 'package:shared_preferences/shared_preferences.dart';\n"
        "import 'package:share_plus/share_plus.dart';\n",
        1,
    )
    text = text.replace(
        "enum ResultState { done, part, moved, missed }\n",
        "enum ResultState { done, part, moved, missed }\n"
        "enum StartProblem { unclear, tooBig, noImpulse, distracted, accountability, reminder }\n",
        1,
    )

    today_and_quick = r"""
class Today extends StatelessWidget {
  const Today({required this.app, super.key});
  final AppState app;

  @override
  Widget build(BuildContext context) {
    final goalAction = app.actions
        .where((item) => item.goal && item.state == null)
        .firstOrNull;
    final otherActions =
        app.actions.where((item) => !item.goal && item.state == null).toList();

    return Scaffold(
      appBar: AppBar(
        title: const Row(
          children: [
            Logo(size: 30),
            SizedBox(width: 10),
            Text('Вместе к цели'),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        backgroundColor: ink,
        foregroundColor: Colors.white,
        onPressed: () => Navigator.push(
          context,
          MaterialPageRoute(
            builder: (_) => ActionEditor(app: app, goalDefault: false),
          ),
        ),
        icon: const Icon(Icons.add),
        label: const Text('Добавить дело'),
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(18, 4, 18, 112),
        children: [
          Text(app.hello, style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 5),
          const Text('Выберите дело или получите помощь, если трудно начать.'),
          const SizedBox(height: 18),
          StartHelpCard(app: app),
          const SizedBox(height: 22),
          if (app.goal == null)
            CreateGoal(app: app)
          else ...[
            GoalHero(app: app),
            const SizedBox(height: 22),
            section('Что сделать для главной цели сегодня?'),
            const SizedBox(height: 9),
            if (goalAction == null)
              EmptyAction(
                onTap: () => Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) =>
                        ActionEditor(app: app, goalDefault: true),
                  ),
                ),
              )
            else
              ActionCard(app: app, item: goalAction, featured: true),
          ],
          const SizedBox(height: 23),
          section('Другие дела на сегодня'),
          const SizedBox(height: 9),
          if (otherActions.isEmpty)
            const Card(
              child: Padding(
                padding: EdgeInsets.all(18),
                child: Text(
                  'Здесь появятся обычные дела, которые вы добавите на сегодня.',
                ),
              ),
            )
          else
            ...otherActions.map(
              (item) => Padding(
                padding: const EdgeInsets.only(bottom: 9),
                child: ActionCard(app: app, item: item),
              ),
            ),
        ],
      ),
    );
  }

  Widget section(String text) => Text(
        text,
        style: const TextStyle(
          fontSize: 20,
          fontWeight: FontWeight.w900,
          color: ink,
        ),
      );
}

class StartHelpCard extends StatelessWidget {
  const StartHelpCard({required this.app, super.key});
  final AppState app;

  @override
  Widget build(BuildContext context) => Container(
        padding: const EdgeInsets.all(22),
        decoration: BoxDecoration(
          gradient: const LinearGradient(
            colors: [Color(0xFF244F49), Color(0xFF4B7F73)],
          ),
          borderRadius: BorderRadius.circular(28),
          boxShadow: const [
            BoxShadow(
              color: Color(0x1A132D2A),
              blurRadius: 24,
              offset: Offset(0, 12),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Row(
              children: [
                Icon(Icons.bolt_rounded, color: mint),
                SizedBox(width: 8),
                Text(
                  'БЫСТРАЯ ПОМОЩЬ',
                  style: TextStyle(
                    color: mint,
                    fontSize: 12,
                    fontWeight: FontWeight.w900,
                    letterSpacing: 1.1,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            const Text(
              'Трудно начать конкретное дело?',
              style: TextStyle(
                color: Colors.white,
                fontSize: 25,
                height: 1.15,
                fontWeight: FontWeight.w900,
              ),
            ),
            const SizedBox(height: 9),
            const Text(
              'Назовите дело и выберите, что мешает. Приложение предложит первый шаг и способ помощи.',
              style: TextStyle(
                color: Color(0xFFD8E5E1),
                fontSize: 16,
                height: 1.4,
              ),
            ),
            const SizedBox(height: 17),
            FilledButton.icon(
              style: FilledButton.styleFrom(
                backgroundColor: mint,
                foregroundColor: ink,
              ),
              onPressed: () => Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => QuickStartWizard(app: app),
                ),
              ),
              icon: const Icon(Icons.play_arrow_rounded),
              label: const Text('Помочь мне начать'),
            ),
          ],
        ),
      );
}

class QuickStartWizard extends StatefulWidget {
  const QuickStartWizard({required this.app, super.key});
  final AppState app;

  @override
  State<QuickStartWizard> createState() => _QuickStartWizardState();
}

class _QuickStartWizardState extends State<QuickStartWizard> {
  final title = TextEditingController();
  int stage = 0;
  int minutes = 10;
  StartProblem? problem;
  bool linked = false;

  @override
  void initState() {
    super.initState();
    title.addListener(() => setState(() {}));
  }

  @override
  void dispose() {
    title.dispose();
    super.dispose();
  }

  void next() {
    if (stage == 0 && title.text.trim().isNotEmpty) {
      setState(() => stage = 1);
    } else if (stage == 1 && problem != null) {
      setState(() => stage = 2);
    }
  }

  ActionItem makeItem(StartPlan plan) => ActionItem(
        id: DateTime.now().microsecondsSinceEpoch.toString(),
        title: title.text.trim(),
        small: plan.small,
        minutes: minutes,
        support: plan.support,
        goal: linked,
      );

  void startNow(StartPlan plan) {
    final item = makeItem(plan);
    widget.app.add(item);
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(
        builder: (_) => Session(app: widget.app, item: item),
      ),
    );
  }

  void saveForLater(StartPlan plan) {
    widget.app.add(makeItem(plan));
    Navigator.pop(context);
  }

  @override
  Widget build(BuildContext context) {
    final plan =
        problem == null ? null : StartPlan.forProblem(title.text, problem!);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Помочь начать'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () {
            if (stage == 0) {
              Navigator.pop(context);
            } else {
              setState(() => stage--);
            }
          },
        ),
      ),
      body: AnimatedSwitcher(
        duration: const Duration(milliseconds: 220),
        child: stage == 0
            ? firstStage()
            : stage == 1
                ? problemStage()
                : planStage(plan!),
      ),
    );
  }

  Widget firstStage() => ListView(
        key: const ValueKey('quick-first'),
        padding: const EdgeInsets.all(18),
        children: [
          Text(
            'Что вам нужно начать?',
            style: Theme.of(context).textTheme.headlineMedium,
          ),
          const SizedBox(height: 8),
          const Text(
            'Назовите одно дело, которое вы откладываете прямо сейчас.',
          ),
          const SizedBox(height: 20),
          VoiceField(
            controller: title,
            label: 'Дело',
            hint: 'Например: начать делать страницу сайта',
            lines: 3,
          ),
          const SizedBox(height: 18),
          FilledButton(
            onPressed: title.text.trim().isEmpty ? null : next,
            child: const Text('Дальше'),
          ),
          const SizedBox(height: 10),
          const Text(
            'Это дело можно не добавлять в главную цель. Быстрая помощь работает и для обычных задач.',
            style: TextStyle(fontSize: 13, color: Colors.black54),
          ),
        ],
      );

  Widget problemStage() => ListView(
        key: const ValueKey('quick-problem'),
        padding: const EdgeInsets.all(18),
        children: [
          Text(
            'Что мешает начать?',
            style: Theme.of(context).textTheme.headlineMedium,
          ),
          const SizedBox(height: 8),
          Text(
            'Дело: «${title.text.trim()}»',
            style: const TextStyle(color: Colors.black54),
          ),
          const SizedBox(height: 16),
          ...StartProblem.values.map(
            (value) => ProblemTile(
              problem: value,
              selected: problem == value,
              onTap: () => setState(() => problem = value),
            ),
          ),
          const SizedBox(height: 10),
          FilledButton(
            onPressed: problem == null ? null : next,
            child: const Text('Подобрать помощь'),
          ),
        ],
      );

  Widget planStage(StartPlan plan) => ListView(
        key: const ValueKey('quick-plan'),
        padding: const EdgeInsets.fromLTRB(18, 4, 18, 32),
        children: [
          Text(
            'Вот с чего можно начать',
            style: Theme.of(context).textTheme.headlineMedium,
          ),
          const SizedBox(height: 8),
          Text('Дело: «${title.text.trim()}»'),
          const SizedBox(height: 18),
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: supportColor(plan.support),
              borderRadius: BorderRadius.circular(24),
              border: Border.all(color: green.withValues(alpha: .18)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(supportIcon(plan.support), color: ink),
                    const SizedBox(width: 9),
                    Expanded(
                      child: Text(
                        plan.heading,
                        style: const TextStyle(
                          fontSize: 19,
                          fontWeight: FontWeight.w900,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                Text(plan.explanation),
                const SizedBox(height: 16),
                const Text(
                  'Первое действие',
                  style: TextStyle(fontWeight: FontWeight.w900),
                ),
                const SizedBox(height: 5),
                Text(plan.firstStep),
                const SizedBox(height: 14),
                const Text(
                  'Если сил мало',
                  style: TextStyle(fontWeight: FontWeight.w900),
                ),
                const SizedBox(height: 5),
                Text(plan.small),
              ],
            ),
          ),
          if (plan.needsPerson) ...[
            const SizedBox(height: 12),
            OutlinedButton.icon(
              onPressed: () => shareStartMessage(
                title.text.trim(),
                minutes,
                plan.support,
              ),
              icon: const Icon(Icons.send_rounded),
              label: Text(plan.shareButton),
            ),
          ],
          const SizedBox(height: 18),
          const Text(
            'Сколько времени начать сейчас?',
            style: TextStyle(fontSize: 17, fontWeight: FontWeight.w900),
          ),
          const SizedBox(height: 9),
          Wrap(
            spacing: 8,
            children: [5, 10, 15, 25]
                .map(
                  (value) => ChoiceChip(
                    label: Text('$value мин'),
                    selected: minutes == value,
                    onSelected: (_) => setState(() => minutes = value),
                  ),
                )
                .toList(),
          ),
          if (widget.app.goal != null) ...[
            const SizedBox(height: 12),
            SwitchListTile.adaptive(
              contentPadding: EdgeInsets.zero,
              title: const Text(
                'Это действие для моей главной цели',
                style: TextStyle(fontWeight: FontWeight.w800),
              ),
              subtitle: Text(widget.app.goal!.title),
              value: linked,
              onChanged: (value) => setState(() => linked = value),
            ),
          ],
          const SizedBox(height: 16),
          FilledButton.icon(
            onPressed: () => startNow(plan),
            icon: const Icon(Icons.play_arrow_rounded),
            label: const Text('Начать сейчас'),
          ),
          const SizedBox(height: 9),
          TextButton(
            onPressed: () => saveForLater(plan),
            child: const Text('Сохранить на сегодня'),
          ),
        ],
      );
}

class ProblemTile extends StatelessWidget {
  const ProblemTile({
    required this.problem,
    required this.selected,
    required this.onTap,
    super.key,
  });

  final StartProblem problem;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.only(bottom: 9),
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(18),
          child: Container(
            padding: const EdgeInsets.all(15),
            decoration: BoxDecoration(
              color: selected ? mint : Colors.white,
              borderRadius: BorderRadius.circular(18),
              border: Border.all(
                color: selected ? green : const Color(0xFFE0DDD4),
                width: selected ? 1.5 : 1,
              ),
            ),
            child: Row(
              children: [
                Icon(problemIcon(problem), color: ink),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    problemName(problem),
                    style: const TextStyle(fontWeight: FontWeight.w800),
                  ),
                ),
                Icon(
                  selected
                      ? Icons.check_circle
                      : Icons.radio_button_unchecked,
                  color: selected ? green : Colors.black26,
                ),
              ],
            ),
          ),
        ),
      );
}

class StartPlan {
  const StartPlan({
    required this.support,
    required this.heading,
    required this.explanation,
    required this.firstStep,
    required this.small,
    required this.shareButton,
  });

  final Support support;
  final String heading;
  final String explanation;
  final String firstStep;
  final String small;
  final String shareButton;

  bool get needsPerson =>
      support == Support.together ||
      support == Support.report ||
      support == Support.curator;

  static StartPlan forProblem(String task, StartProblem problem) {
    final steps = SupportLogic.steps(task);
    final first = steps.first;

    return switch (problem) {
      StartProblem.unclear => StartPlan(
          support: Support.ai,
          heading: 'Сначала сделаем задачу понятной',
          explanation:
              'Сейчас вам не нужна дополнительная мотивация. Нужен один ясный первый шаг.',
          firstStep: first,
          small: first,
          shareButton: '',
        ),
      StartProblem.tooBig => StartPlan(
          support: Support.ai,
          heading: 'Уменьшим дело до одной части',
          explanation:
              'Не нужно выполнять всё сразу. Достаточно закончить одну небольшую часть.',
          firstStep: first,
          small: 'Сделать только это: $first',
          shareButton: '',
        ),
      StartProblem.noImpulse => StartPlan(
          support: Support.together,
          heading: 'Создадим внешний повод начать',
          explanation:
              'Позовите знакомого начать одновременно. Каждый может заниматься своим делом.',
          firstStep:
              'Отправьте короткое сообщение и договоритесь начать в одно время.',
          small: 'Начать хотя бы на 5 минут.',
          shareButton: 'Позвать человека',
        ),
      StartProblem.distracted => StartPlan(
          support: Support.solo,
          heading: 'Начнём коротко и без лишнего',
          explanation:
              'Сейчас важнее убрать одно отвлечение и не требовать от себя долгой работы.',
          firstStep:
              'Закройте лишние приложения, положите телефон экраном вниз и начните.',
          small: 'Работать только 5 минут.',
          shareButton: '',
        ),
      StartProblem.accountability => StartPlan(
          support: Support.report,
          heading: 'Пообещаем показать результат',
          explanation:
              'Выберите человека, которому отправите короткий итог после работы.',
          firstStep:
              'Сообщите, что начинаете, и договоритесь отправить результат.',
          small: 'Отправить итог даже после небольшой выполненной части.',
          shareButton: 'Сообщить о начале',
        ),
      StartProblem.reminder => StartPlan(
          support: Support.curator,
          heading: 'Попросим человека напомнить',
          explanation:
              'Подойдёт знакомый, который согласен написать вам в условленное время.',
          firstStep:
              'Выберите человека и попросите напомнить об этом деле.',
          small: 'После напоминания начать хотя бы на 5 минут.',
          shareButton: 'Попросить напомнить',
        ),
    };
  }
}

String problemName(StartProblem problem) => switch (problem) {
      StartProblem.unclear => 'Не понимаю, с чего начать',
      StartProblem.tooBig => 'Дело кажется слишком большим',
      StartProblem.noImpulse =>
        'Понимаю, что делать, но не могу заставить себя начать',
      StartProblem.distracted => 'Постоянно отвлекаюсь',
      StartProblem.accountability =>
        'Нужен человек, которому я пообещаю результат',
      StartProblem.reminder => 'Боюсь снова забыть или отложить',
    };

IconData problemIcon(StartProblem problem) => switch (problem) {
      StartProblem.unclear => Icons.question_mark_rounded,
      StartProblem.tooBig => Icons.account_tree_outlined,
      StartProblem.noImpulse => Icons.people_alt_outlined,
      StartProblem.distracted => Icons.notifications_off_outlined,
      StartProblem.accountability => Icons.verified_outlined,
      StartProblem.reminder => Icons.alarm_rounded,
    };
"""

    text = replace_block(
        text,
        "class Today extends StatelessWidget {",
        "class CreateGoal extends StatelessWidget {",
        today_and_quick,
    )

    session = r"""
class Session extends StatefulWidget {
  const Session({required this.app, required this.item, super.key});
  final AppState app;
  final ActionItem item;

  @override
  State<Session> createState() => _SessionState();
}

class _SessionState extends State<Session> {
  Timer? timer;
  bool started = false;
  bool paused = false;
  late int left;
  int step = 0;

  @override
  void initState() {
    super.initState();
    left = widget.item.minutes * 60;
  }

  @override
  void dispose() {
    timer?.cancel();
    super.dispose();
  }

  void start() {
    setState(() => started = true);
    timer = Timer.periodic(const Duration(seconds: 1), (_) {
      if (!paused && left > 0 && mounted) {
        setState(() => left--);
      }
    });
  }

  void finish(ResultState state) {
    timer?.cancel();
    widget.app.complete(widget.item, state);
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(
        builder: (_) => ResultPage(item: widget.item, state: state),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final steps = SupportLogic.steps(widget.item.title);
    final social = widget.item.support == Support.together ||
        widget.item.support == Support.report ||
        widget.item.support == Support.curator;

    return Scaffold(
      appBar: AppBar(title: const Text('Текущее действие')),
      body: ListView(
        padding: const EdgeInsets.all(18),
        children: [
          Container(
            padding: const EdgeInsets.all(21),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [ink, supportAccent(widget.item.support)],
              ),
              borderRadius: BorderRadius.circular(27),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(supportIcon(widget.item.support), color: mint),
                    const SizedBox(width: 8),
                    Text(
                      supportName(widget.item.support).toUpperCase(),
                      style: const TextStyle(
                        color: mint,
                        fontSize: 12,
                        fontWeight: FontWeight.w900,
                        letterSpacing: 1,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 13),
                Text(
                  widget.item.title,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 27,
                    height: 1.15,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  sessionMessage(widget.item.support, widget.app),
                  style: const TextStyle(
                    color: Color(0xFFD4E0DD),
                    height: 1.4,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          if (widget.item.support == Support.ai)
            Card(
              child: Padding(
                padding: const EdgeInsets.all(18),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Первые понятные действия',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                    const SizedBox(height: 12),
                    ...steps.asMap().entries.map(
                      (entry) => InkWell(
                        onTap: () => setState(() => step = entry.key),
                        child: Padding(
                          padding: const EdgeInsets.only(bottom: 10),
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Icon(
                                step == entry.key
                                    ? Icons.play_circle
                                    : step > entry.key
                                        ? Icons.check_circle
                                        : Icons.radio_button_unchecked,
                                color: step == entry.key
                                    ? green
                                    : Colors.black26,
                              ),
                              const SizedBox(width: 9),
                              Expanded(
                                child: Text(
                                  entry.value,
                                  style: TextStyle(
                                    fontWeight: step == entry.key
                                        ? FontWeight.w800
                                        : FontWeight.w500,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                    if (started && step < steps.length - 1)
                      TextButton(
                        onPressed: () => setState(() => step++),
                        child: const Text('Следующий шаг'),
                      ),
                  ],
                ),
              ),
            ),
          if (social && !started) ...[
            OutlinedButton.icon(
              onPressed: () => shareStartMessage(
                widget.item.title,
                widget.item.minutes,
                widget.item.support,
              ),
              icon: const Icon(Icons.send_rounded),
              label: Text(shareStartButton(widget.item.support)),
            ),
            const SizedBox(height: 12),
          ],
          if (!started) ...[
            Card(
              child: Padding(
                padding: const EdgeInsets.all(18),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Перед началом',
                      style: TextStyle(
                        fontWeight: FontWeight.w900,
                        fontSize: 18,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(preStart(widget.item.support)),
                    if (widget.item.small.isNotEmpty) ...[
                      const SizedBox(height: 10),
                      Text(
                        'Если сегодня трудно, достаточно: ${widget.item.small}',
                        style: const TextStyle(fontWeight: FontWeight.w800),
                      ),
                    ],
                  ],
                ),
              ),
            ),
            const SizedBox(height: 15),
            FilledButton.icon(
              onPressed: start,
              icon: const Icon(Icons.play_arrow),
              label: Text('Начать на ${widget.item.minutes} минут'),
            ),
          ] else ...[
            Center(
              child: Column(
                children: [
                  Text(
                    '${(left ~/ 60).toString().padLeft(2, '0')}:${(left % 60).toString().padLeft(2, '0')}',
                    style: const TextStyle(
                      fontSize: 60,
                      fontWeight: FontWeight.w900,
                      color: ink,
                    ),
                  ),
                  Text(
                    paused ? 'Пауза' : 'Вы уже начали',
                    style: const TextStyle(
                      color: green,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 18),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => setState(() => paused = !paused),
                    icon: Icon(
                      paused ? Icons.play_arrow : Icons.pause,
                    ),
                    label: Text(paused ? 'Продолжить' : 'Пауза'),
                  ),
                ),
                const SizedBox(width: 9),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => showModalBottomSheet(
                      context: context,
                      showDragHandle: true,
                      builder: (_) => Blocker(item: widget.item),
                    ),
                    icon: const Icon(Icons.support),
                    label: const Text('Мне трудно'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            FilledButton.icon(
              onPressed: () => showModalBottomSheet(
                context: context,
                showDragHandle: true,
                builder: (_) => Finish(onFinish: finish),
              ),
              icon: const Icon(Icons.check),
              label: const Text('Закончить и записать результат'),
            ),
          ],
        ],
      ),
    );
  }
}
"""

    text = replace_block(
        text,
        "class Session extends StatefulWidget {",
        "class Blocker extends StatelessWidget {",
        session,
    )

    result_and_share = r"""
class ResultPage extends StatelessWidget {
  const ResultPage({
    required this.item,
    required this.state,
    super.key,
  });

  final ActionItem item;
  final ResultState state;

  @override
  Widget build(BuildContext context) {
    final ok = state == ResultState.done || state == ResultState.part;
    final canShare = item.support == Support.together ||
        item.support == Support.report ||
        item.support == Support.curator;

    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 72,
                height: 72,
                decoration: BoxDecoration(
                  color: ok ? mint : const Color(0xFFE7E1D5),
                  borderRadius: BorderRadius.circular(23),
                ),
                child: Icon(
                  ok ? Icons.check : Icons.refresh,
                  size: 39,
                  color: ink,
                ),
              ),
              const SizedBox(height: 25),
              Text(
                ok
                    ? 'Вы начали и получили результат.'
                    : 'Сегодня не получилось — дело сохранено.',
                style: Theme.of(context).textTheme.headlineLarge,
              ),
              const SizedBox(height: 12),
              Text(
                ok
                    ? 'Результат по делу «${item.title}» записан в истории.'
                    : 'Можно выбрать другое время, уменьшить задачу или попросить человека напомнить.',
              ),
              if (canShare && ok) ...[
                const SizedBox(height: 18),
                OutlinedButton.icon(
                  onPressed: () => shareResultMessage(item, state),
                  icon: const Icon(Icons.send_rounded),
                  label: const Text('Отправить результат'),
                ),
              ],
              const SizedBox(height: 14),
              FilledButton(
                onPressed: () =>
                    Navigator.popUntil(context, (route) => route.isFirst),
                child: const Text('Вернуться на сегодня'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

Future<void> shareStartMessage(
  String title,
  int minutes,
  Support support,
) async {
  final text = switch (support) {
    Support.together =>
      'Начнём одновременно? Я начинаю дело «$title» на $minutes минут. Каждый может заниматься своим делом.',
    Support.report =>
      'Я начинаю дело «$title» на $minutes минут. Когда закончу, отправлю короткий результат.',
    Support.curator =>
      'Я хочу начать дело «$title» на $minutes минут. Напомни мне об этом и спроси потом, что получилось.',
    _ => 'Я начинаю дело «$title» на $minutes минут.',
  };

  await SharePlus.instance.share(
    ShareParams(
      text: text,
      subject: 'Вместе к цели',
    ),
  );
}

Future<void> shareResultMessage(
  ActionItem item,
  ResultState state,
) async {
  final result = switch (state) {
    ResultState.done => 'выполнено',
    ResultState.part => 'сделана важная часть',
    ResultState.moved => 'перенесено',
    ResultState.missed => 'сегодня не получилось',
  };

  await SharePlus.instance.share(
    ShareParams(
      text:
          'Результат по делу «${item.title}»: $result. Время: ${item.minutes} минут.',
      subject: 'Результат — Вместе к цели',
    ),
  );
}

String shareStartButton(Support support) => switch (support) {
      Support.together => 'Позвать начать вместе',
      Support.report => 'Сообщить, что вы начинаете',
      Support.curator => 'Попросить напомнить',
      _ => 'Поделиться',
    };
"""

    text = replace_block(
        text,
        "class ResultPage extends StatelessWidget {",
        "class SupportLogic {",
        result_and_share,
    )

main_path.write_text(text, encoding="utf-8")

pubspec = Path("pubspec.yaml")
pub = pubspec.read_text(encoding="utf-8")
pub = pub.replace("version: 0.2.1+3", "version: 0.3.0+4")
if "  share_plus:" not in pub:
    pub = pub.replace(
        "  speech_to_text: ^7.4.0\n",
        "  speech_to_text: ^7.4.0\n  share_plus: ^13.2.1\n",
    )
pubspec.write_text(pub, encoding="utf-8")

test_path = Path("test/widget_test.dart")
test_path.write_text(
    """import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:vmeste_goal/main.dart';

void main() {
  testWidgets('first launch explains the product promise', (tester) async {
    SharedPreferences.setMockInitialValues({});
    final app = AppState();
    await tester.pumpWidget(VmesteApp(app: app));

    expect(find.text('Вместе к цели'), findsOneWidget);
    expect(
      find.text('Одному бывает трудно довести важную цель до результата.'),
      findsOneWidget,
    );
    expect(find.text('Дальше'), findsOneWidget);
  });

  testWidgets('today screen offers quick help and simple task tracking',
      (tester) async {
    SharedPreferences.setMockInitialValues({});
    final app = AppState();
    app.onboarded = true;

    await tester.pumpWidget(VmesteApp(app: app));

    expect(find.text('Помочь мне начать'), findsOneWidget);
    expect(find.text('Добавить дело'), findsOneWidget);
  });
}
""",
    encoding="utf-8",
)
