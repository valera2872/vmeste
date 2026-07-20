from pathlib import Path

main_path = Path('lib/main.dart')
pubspec_path = Path('pubspec.yaml')
test_path = Path('test/widget_test.dart')
text = main_path.read_text(encoding='utf-8')


def replace_once(old: str, new: str) -> None:
    global text
    if old in text:
        text = text.replace(old, new, 1)


def replace_block(start: str, end: str, replacement: str) -> None:
    global text
    i = text.index(start)
    j = text.index(end, i)
    text = text[:i] + replacement.rstrip() + '\n\n' + text[j:]


if 'class GoalSupportPanel extends StatelessWidget' not in text:
    replace_once('final Support support;', 'Support support;')

    replace_once(
        """  void add(ActionItem a) {
    actions.insert(0, a);
    notifyListeners();
    save();
  }

  void complete(ActionItem a, ResultState s) {""",
        """  void add(ActionItem a) {
    actions.insert(0, a);
    notifyListeners();
    save();
  }

  void setSupport(ActionItem action, Support support) {
    action.support = support;
    notifyListeners();
    save();
  }

  void complete(ActionItem a, ResultState s) {""",
    )

    replace_once("label: 'Помощь',", "label: 'Вместе',")
    replace_once(
        'icon: Icon(Icons.help_outline_rounded),',
        'icon: Icon(Icons.people_outline_rounded),',
    )
    replace_once(
        'selectedIcon: Icon(Icons.help_rounded),',
        'selectedIcon: Icon(Icons.people_alt_rounded),',
    )

    replace_once("'Начните с одного дела'", "'Начните с важной цели'")
    replace_once(
        "'Запишите, что хотите сделать сегодня. Если не получается начать, выберите, что мешает, и приложение предложит подходящий вариант.'",
        "'Сначала назовите цель. Затем выберите одно действие на сегодня и способ поддержки, с которым вам будет легче его выполнить.'",
    )

    today = r'''class Today extends StatelessWidget {
  const Today({required this.app, super.key});
  final AppState app;

  @override
  Widget build(BuildContext context) {
    final goalAction = app.actions
        .where((item) => item.goal && item.state == null)
        .firstOrNull;
    final otherActions = app.actions
        .where((item) => !item.goal && item.state == null)
        .toList();

    return Scaffold(
      appBar: AppBar(
        title: const Row(
          children: [
            Logo(size: 30),
            SizedBox(width: 10),
            Text('Вместе к цели'),
          ],
        ),
        actions: [
          IconButton(
            tooltip: 'Как это работает',
            icon: const Icon(Icons.info_outline_rounded),
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => const HowItWorksPage()),
            ),
          ),
        ],
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
          Text('Сегодня', style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 5),
          Text(app.hello, style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 18),
          if (app.goal == null) ...[
            CreateGoal(app: app),
            const SizedBox(height: 23),
            section('Другие дела на сегодня'),
          ] else ...[
            GoalHero(app: app),
            const SizedBox(height: 22),
            section('Действие для цели на сегодня'),
            const SizedBox(height: 9),
            if (goalAction == null)
              EmptyAction(
                onTap: () => Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => ActionEditor(app: app, goalDefault: true),
                  ),
                ),
              )
            else
              ActionCard(app: app, item: goalAction, featured: true),
            const SizedBox(height: 13),
            GoalSupportPanel(app: app, item: goalAction),
            const SizedBox(height: 23),
            section('Другие дела на сегодня'),
          ],
          const SizedBox(height: 9),
          if (otherActions.isEmpty)
            const Card(
              child: Padding(
                padding: EdgeInsets.all(18),
                child: Text('Других дел на сегодня пока нет.'),
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

class GoalSupportPanel extends StatelessWidget {
  const GoalSupportPanel({required this.app, required this.item, super.key});

  final AppState app;
  final ActionItem? item;

  Future<void> _open(
    BuildContext context,
    Support support,
  ) async {
    if (item == null) {
      await Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => ActionEditor(
            app: app,
            goalDefault: true,
            initialSupport: support,
          ),
        ),
      );
      return;
    }

    app.setSupport(item!, support);
    if (support == Support.together ||
        support == Support.report ||
        support == Support.curator) {
      await shareStartMessage(item!.title, item!.minutes, support);
    }
    if (!context.mounted) return;
    await Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => Session(app: app, item: item!)),
    );
  }

  @override
  Widget build(BuildContext context) => Card(
    color: const Color(0xFFF0F7F4),
    child: Padding(
      padding: const EdgeInsets.all(18),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Как хотите начать?',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900),
          ),
          const SizedBox(height: 6),
          Text(
            item == null
                ? 'Сначала выберите действие, а затем подходящую поддержку.'
                : 'Поддержку можно выбрать сразу — без дополнительного опроса.',
          ),
          const SizedBox(height: 13),
          _SupportButton(
            icon: Icons.people_alt_rounded,
            label: 'Начать вместе',
            onPressed: () => _open(context, Support.together),
          ),
          const SizedBox(height: 8),
          _SupportButton(
            icon: Icons.auto_awesome_rounded,
            label: 'С цифровым помощником',
            onPressed: () => _open(context, Support.ai),
          ),
          const SizedBox(height: 8),
          _SupportButton(
            icon: Icons.verified_user_outlined,
            label: 'С куратором',
            onPressed: () => _open(context, Support.curator),
          ),
        ],
      ),
    ),
  );
}

class _SupportButton extends StatelessWidget {
  const _SupportButton({
    required this.icon,
    required this.label,
    required this.onPressed,
  });

  final IconData icon;
  final String label;
  final VoidCallback onPressed;

  @override
  Widget build(BuildContext context) => SizedBox(
    width: double.infinity,
    child: OutlinedButton.icon(
      onPressed: onPressed,
      icon: Icon(icon),
      label: Text(label),
    ),
  );
}'''
    replace_block('class Today extends StatelessWidget {', 'class StartHelpCard', today)

    action_card = r'''class ActionCard extends StatelessWidget {
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
    if (!context.mounted) return;
    await Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => Session(app: app, item: item)),
    );
  }

  @override
  Widget build(BuildContext context) => Card(
    color: featured ? const Color(0xFFFFFCF5) : Colors.white,
    child: Padding(
      padding: const EdgeInsets.all(17),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 42,
                height: 42,
                decoration: BoxDecoration(
                  color: supportColor(item.support),
                  borderRadius: BorderRadius.circular(14),
                ),
                child: Icon(
                  item.state == null ? supportIcon(item.support) : Icons.check,
                  color: ink,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      item.title,
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.w900,
                        decoration: item.state == null
                            ? null
                            : TextDecoration.lineThrough,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text('${item.minutes} минут · ${supportName(item.support)}'),
                  ],
                ),
              ),
            ],
          ),
          if (item.small.isNotEmpty && item.state == null) ...[
            const SizedBox(height: 11),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: cream,
                borderRadius: BorderRadius.circular(14),
              ),
              child: Text('Если времени мало: ${item.small}'),
            ),
          ],
          const SizedBox(height: 13),
          if (item.state == null)
            Row(
              children: [
                Expanded(
                  child: FilledButton.icon(
                    onPressed: () => Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (_) => Session(app: app, item: item),
                      ),
                    ),
                    icon: const Icon(Icons.play_arrow),
                    label: const Text('Начать'),
                  ),
                ),
                const SizedBox(width: 9),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => _startTogether(context),
                    icon: const Icon(Icons.people_alt_outlined),
                    label: const Text('Вместе'),
                  ),
                ),
              ],
            )
          else
            Text(
              resultName(item.state!),
              style: const TextStyle(color: green, fontWeight: FontWeight.w900),
            ),
        ],
      ),
    ),
  );
}'''
    replace_block('class ActionCard extends StatelessWidget {', 'class GoalScreen', action_card)

    goal_screen = r'''class GoalScreen extends StatelessWidget {
  const GoalScreen({required this.app, super.key});
  final AppState app;

  @override
  Widget build(BuildContext context) {
    final activeAction = app.actions
        .where((item) => item.goal && item.state == null)
        .firstOrNull;

    return Scaffold(
      appBar: AppBar(title: const Text('Моя цель')),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(18, 4, 18, 90),
        children: [
          if (app.goal == null)
            CreateGoal(app: app)
          else ...[
            Text(
              'Моя главная цель',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
            const SizedBox(height: 6),
            const Text(
              'Здесь видно, к какому результату вы идёте и что можно сделать сегодня.',
            ),
            const SizedBox(height: 18),
            GoalHero(app: app),
            const SizedBox(height: 13),
            GoalSupportPanel(app: app, item: activeAction),
            const SizedBox(height: 16),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(18),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Когда цель будет достигнута?',
                      style: TextStyle(fontWeight: FontWeight.w900, fontSize: 17),
                    ),
                    const SizedBox(height: 7),
                    Text(
                      app.goal!.result.isEmpty
                          ? 'Результат пока не описан. Его можно добавить позже.'
                          : app.goal!.result,
                    ),
                  ],
                ),
              ),
            ),
            if (app.goal!.areas.isNotEmpty) ...[
              const SizedBox(height: 12),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(18),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Части цели',
                        style: TextStyle(
                          fontWeight: FontWeight.w900,
                          fontSize: 17,
                        ),
                      ),
                      const SizedBox(height: 9),
                      ...app.goal!.areas.map(
                        (area) => Padding(
                          padding: const EdgeInsets.only(bottom: 7),
                          child: Row(
                            children: [
                              const Icon(
                                Icons.radio_button_checked,
                                size: 15,
                                color: green,
                              ),
                              const SizedBox(width: 9),
                              Expanded(child: Text(area)),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
            const SizedBox(height: 14),
            FilledButton.icon(
              onPressed: () => Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => ActionEditor(app: app, goalDefault: true),
                ),
              ),
              icon: const Icon(Icons.add_task),
              label: Text(
                activeAction == null
                    ? 'Выбрать действие на сегодня'
                    : 'Добавить другое действие',
              ),
            ),
            const SizedBox(height: 10),
            OutlinedButton.icon(
              onPressed: () => Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => GoalEditor(app: app, existing: app.goal),
                ),
              ),
              icon: const Icon(Icons.edit_outlined),
              label: const Text('Изменить цель'),
            ),
          ],
        ],
      ),
    );
  }
}'''
    replace_block('class GoalScreen extends StatelessWidget {', 'class GoalEditor', goal_screen)

    goal_editor = r'''class GoalEditor extends StatefulWidget {
  const GoalEditor({required this.app, this.existing, super.key});
  final AppState app;
  final Goal? existing;
  @override
  State<GoalEditor> createState() => _GoalEditorState();
}

class _GoalEditorState extends State<GoalEditor> {
  late final TextEditingController title;
  late final TextEditingController result;
  late final TextEditingController areas;
  int minutes = 20;
  bool showDetails = false;

  @override
  void initState() {
    super.initState();
    title = TextEditingController(text: widget.existing?.title ?? '');
    result = TextEditingController(text: widget.existing?.result ?? '');
    areas = TextEditingController(
      text: widget.existing?.areas.join(', ') ?? '',
    );
    minutes = widget.existing?.minutes ?? 20;
    showDetails = widget.existing != null && widget.existing!.areas.isNotEmpty;
    title.addListener(() => setState(() {}));
  }

  @override
  void dispose() {
    title.dispose();
    result.dispose();
    areas.dispose();
    super.dispose();
  }

  void save() {
    widget.app.setGoal(
      Goal(
        title.text.trim(),
        result.text.trim(),
        minutes,
        areas.text
            .split(RegExp(r'[,;\n]'))
            .map((item) => item.trim())
            .where((item) => item.isNotEmpty)
            .toList(),
      ),
    );

    if (widget.existing == null) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (_) => ActionEditor(app: widget.app, goalDefault: true),
        ),
      );
    } else {
      Navigator.pop(context);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Моя цель')),
    body: ListView(
      padding: const EdgeInsets.all(18),
      children: [
        Text(
          'Чего вы хотите добиться?',
          style: Theme.of(context).textTheme.headlineMedium,
        ),
        const SizedBox(height: 7),
        const Text('Сначала достаточно назвать цель. Подробности можно добавить позже.'),
        const SizedBox(height: 18),
        VoiceField(
          controller: title,
          label: 'Моя цель',
          hint: 'Например: навести порядок в доме и закончить ремонт',
          lines: 3,
        ),
        const SizedBox(height: 13),
        VoiceField(
          controller: result,
          label: 'Как вы поймёте, что цель достигнута? Необязательно',
          hint: 'Например: все незаконченные работы выполнены',
          lines: 3,
        ),
        const SizedBox(height: 8),
        TextButton.icon(
          onPressed: () => setState(() => showDetails = !showDetails),
          icon: Icon(showDetails ? Icons.expand_less : Icons.tune_rounded),
          label: Text(showDetails ? 'Скрыть подробности' : 'Добавить подробности'),
        ),
        if (showDetails) ...[
          const SizedBox(height: 8),
          VoiceField(
            controller: areas,
            label: 'На какие части можно разделить цель?',
            hint: 'Например: кухня, документы, ремонт, вещи без места',
            lines: 3,
          ),
          const SizedBox(height: 18),
          const Text(
            'Сколько времени удобно выделять за один раз?',
            style: TextStyle(fontWeight: FontWeight.w900, fontSize: 17),
          ),
          const SizedBox(height: 9),
          Wrap(
            spacing: 8,
            children: [10, 15, 20, 25, 40]
                .map(
                  (value) => ChoiceChip(
                    label: Text('$value мин'),
                    selected: minutes == value,
                    onSelected: (_) => setState(() => minutes = value),
                  ),
                )
                .toList(),
          ),
        ],
        const SizedBox(height: 24),
        FilledButton(
          onPressed: title.text.trim().isEmpty ? null : save,
          child: Text(
            widget.existing == null
                ? 'Сохранить и выбрать действие'
                : 'Сохранить изменения',
          ),
        ),
      ],
    ),
  );
}'''
    replace_block('class GoalEditor extends StatefulWidget {', 'class ActionEditor', goal_editor)

    action_editor = r'''class ActionEditor extends StatefulWidget {
  const ActionEditor({
    required this.app,
    required this.goalDefault,
    this.initialSupport,
    super.key,
  });
  final AppState app;
  final bool goalDefault;
  final Support? initialSupport;
  @override
  State<ActionEditor> createState() => _ActionEditorState();
}

class _ActionEditorState extends State<ActionEditor> {
  final title = TextEditingController(), small = TextEditingController();
  int minutes = 15;
  late bool linked;
  Support? chosen;
  bool showMoreSupport = false;
  bool showSmall = false;

  @override
  void initState() {
    super.initState();
    linked = widget.goalDefault && widget.app.goal != null;
    chosen = widget.initialSupport;
    showMoreSupport = chosen != null &&
        chosen != Support.solo &&
        chosen != Support.together;
    title.addListener(() => setState(() {}));
  }

  @override
  void dispose() {
    title.dispose();
    small.dispose();
    super.dispose();
  }

  Future<void> createAndStart(Support support) async {
    final action = ActionItem(
      id: DateTime.now().microsecondsSinceEpoch.toString(),
      title: title.text.trim(),
      small: small.text.trim(),
      minutes: minutes,
      support: support,
      goal: linked,
    );
    widget.app.add(action);

    if (support == Support.together ||
        support == Support.report ||
        support == Support.curator) {
      await shareStartMessage(action.title, action.minutes, support);
    }
    if (!mounted) return;
    await Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (_) => Session(app: widget.app, item: action)),
    );
  }

  @override
  Widget build(BuildContext context) {
    final recommended = SupportLogic.recommend(title.text);
    final support = chosen ?? recommended.$1;

    return Scaffold(
      appBar: AppBar(title: const Text('Действие на сегодня')),
      body: ListView(
        padding: const EdgeInsets.all(18),
        children: [
          Text(
            'Что вы сделаете сегодня?',
            style: Theme.of(context).textTheme.headlineMedium,
          ),
          if (linked && widget.app.goal != null) ...[
            const SizedBox(height: 7),
            Text(
              'Для цели: ${widget.app.goal!.title}',
              style: const TextStyle(color: Colors.black54),
            ),
          ],
          const SizedBox(height: 17),
          VoiceField(
            controller: title,
            label: 'Конкретное действие',
            hint: 'Например: закрепить полку в ванной',
            lines: 3,
          ),
          const SizedBox(height: 15),
          const Text(
            'Сколько времени вы готовы уделить?',
            style: TextStyle(fontWeight: FontWeight.w900, fontSize: 17),
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            children: [5, 10, 15, 25, 40]
                .map(
                  (value) => ChoiceChip(
                    label: Text('$value мин'),
                    selected: minutes == value,
                    onSelected: (_) => setState(() => minutes = value),
                  ),
                )
                .toList(),
          ),
          const SizedBox(height: 20),
          const Text(
            'Как хотите начать?',
            style: TextStyle(fontWeight: FontWeight.w900, fontSize: 18),
          ),
          const SizedBox(height: 9),
          SupportTile(
            type: Support.solo,
            selected: support == Support.solo,
            onTap: () => setState(() => chosen = Support.solo),
          ),
          SupportTile(
            type: Support.together,
            selected: support == Support.together,
            onTap: () => setState(() => chosen = Support.together),
          ),
          TextButton.icon(
            onPressed: () => setState(() => showMoreSupport = !showMoreSupport),
            icon: Icon(showMoreSupport ? Icons.expand_less : Icons.more_horiz),
            label: Text(
              showMoreSupport
                  ? 'Скрыть другие варианты'
                  : 'Другие варианты поддержки',
            ),
          ),
          if (showMoreSupport) ...[
            SupportTile(
              type: Support.ai,
              selected: support == Support.ai,
              onTap: () => setState(() => chosen = Support.ai),
            ),
            SupportTile(
              type: Support.report,
              selected: support == Support.report,
              onTap: () => setState(() => chosen = Support.report),
            ),
            SupportTile(
              type: Support.curator,
              selected: support == Support.curator,
              onTap: () => setState(() => chosen = Support.curator),
            ),
          ],
          TextButton.icon(
            onPressed: () => setState(() => showSmall = !showSmall),
            icon: Icon(showSmall ? Icons.expand_less : Icons.compress_rounded),
            label: Text(
              showSmall
                  ? 'Скрыть сокращённый вариант'
                  : 'Добавить вариант на случай нехватки времени',
            ),
          ),
          if (showSmall) ...[
            const SizedBox(height: 6),
            VoiceField(
              controller: small,
              label: 'Что можно сделать хотя бы частично?',
              hint: 'Например: только подготовить инструменты',
              lines: 3,
            ),
          ],
          if (!widget.goalDefault && widget.app.goal != null) ...[
            const SizedBox(height: 8),
            SwitchListTile.adaptive(
              contentPadding: EdgeInsets.zero,
              title: const Text(
                'Это действие относится к главной цели',
                style: TextStyle(fontWeight: FontWeight.w800),
              ),
              subtitle: Text(widget.app.goal!.title),
              value: linked,
              onChanged: (value) => setState(() => linked = value),
            ),
          ],
          const SizedBox(height: 18),
          FilledButton.icon(
            onPressed: title.text.trim().isEmpty
                ? null
                : () => createAndStart(support),
            icon: Icon(
              support == Support.together
                  ? Icons.people_alt_rounded
                  : Icons.play_arrow_rounded,
            ),
            label: Text(
              support == Support.together
                  ? 'Позвать человека и начать'
                  : 'Начать',
            ),
          ),
        ],
      ),
    );
  }
}'''
    replace_block('class ActionEditor extends StatefulWidget {', 'class Speech', action_editor)

    support_screen = r'''class SupportScreen extends StatelessWidget {
  const SupportScreen({required this.app, super.key});
  final AppState app;

  @override
  Widget build(BuildContext context) {
    final active = app.actions.where((item) => item.state == null).toList();

    return Scaffold(
      appBar: AppBar(title: const Text('Вместе')),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(18, 4, 18, 90),
        children: [
          Container(
            padding: const EdgeInsets.all(22),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF244F49), Color(0xFF4B7F73)],
              ),
              borderRadius: BorderRadius.circular(28),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(Icons.people_alt_rounded, color: mint, size: 36),
                const SizedBox(height: 12),
                const Text(
                  'Начать вместе',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 28,
                    height: 1.1,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                const SizedBox(height: 9),
                const Text(
                  'Вы и другой человек начинаете в одно время. Можно делать одно и то же или заниматься разными делами.',
                  style: TextStyle(
                    color: Color(0xFFD8E5E1),
                    fontSize: 16,
                    height: 1.4,
                  ),
                ),
                const SizedBox(height: 17),
                if (active.isEmpty)
                  FilledButton.icon(
                    style: FilledButton.styleFrom(
                      backgroundColor: mint,
                      foregroundColor: ink,
                    ),
                    onPressed: () => Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (_) => ActionEditor(
                          app: app,
                          goalDefault: app.goal != null,
                          initialSupport: Support.together,
                        ),
                      ),
                    ),
                    icon: const Icon(Icons.add_task_rounded),
                    label: const Text('Выбрать действие'),
                  )
                else
                  const Text(
                    'Выберите действие ниже и отправьте приглашение через привычный мессенджер.',
                    style: TextStyle(color: Colors.white),
                  ),
              ],
            ),
          ),
          const SizedBox(height: 20),
          if (active.isNotEmpty) ...[
            Text(
              'Что будете делать?',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 9),
            ...active.map(
              (item) => Padding(
                padding: const EdgeInsets.only(bottom: 9),
                child: TogetherActionCard(app: app, item: item),
              ),
            ),
          ],
          const SizedBox(height: 20),
          Text(
            'Другие способы поддержки',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: 9),
          _SimpleSupportCard(
            type: Support.ai,
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => ActionEditor(
                  app: app,
                  goalDefault: app.goal != null,
                  initialSupport: Support.ai,
                ),
              ),
            ),
          ),
          _SimpleSupportCard(
            type: Support.report,
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => ActionEditor(
                  app: app,
                  goalDefault: app.goal != null,
                  initialSupport: Support.report,
                ),
              ),
            ),
          ),
          _SimpleSupportCard(
            type: Support.curator,
            onPressed: () => showModalBottomSheet(
              context: context,
              isScrollControlled: true,
              showDragHandle: true,
              builder: (_) => CuratorSheet(app: app),
            ),
          ),
        ],
      ),
    );
  }
}

class TogetherActionCard extends StatelessWidget {
  const TogetherActionCard({required this.app, required this.item, super.key});

  final AppState app;
  final ActionItem item;

  Future<void> start(BuildContext context) async {
    app.setSupport(item, Support.together);
    await shareStartMessage(item.title, item.minutes, Support.together);
    if (!context.mounted) return;
    await Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => Session(app: app, item: item)),
    );
  }

  @override
  Widget build(BuildContext context) => Card(
    child: Padding(
      padding: const EdgeInsets.all(17),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            item.title,
            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w900),
          ),
          const SizedBox(height: 5),
          Text('${item.minutes} минут'),
          const SizedBox(height: 12),
          FilledButton.icon(
            onPressed: () => start(context),
            icon: const Icon(Icons.send_rounded),
            label: const Text('Позвать человека и начать'),
          ),
        ],
      ),
    ),
  );
}

class _SimpleSupportCard extends StatelessWidget {
  const _SimpleSupportCard({required this.type, required this.onPressed});

  final Support type;
  final VoidCallback onPressed;

  @override
  Widget build(BuildContext context) => Card(
    margin: const EdgeInsets.only(bottom: 9),
    child: ListTile(
      contentPadding: const EdgeInsets.all(14),
      leading: Container(
        width: 44,
        height: 44,
        decoration: BoxDecoration(
          color: supportColor(type),
          borderRadius: BorderRadius.circular(14),
        ),
        child: Icon(supportIcon(type), color: ink),
      ),
      title: Text(
        supportName(type),
        style: const TextStyle(fontWeight: FontWeight.w900),
      ),
      subtitle: Text(supportShort(type)),
      trailing: const Icon(Icons.chevron_right_rounded),
      onTap: onPressed,
    ),
  );
}'''
    replace_block('class SupportScreen extends StatelessWidget {', 'class CuratorSheet', support_screen)

main_path.write_text(text, encoding='utf-8')

pubspec = pubspec_path.read_text(encoding='utf-8')
pubspec = pubspec.replace('version: 0.3.1+5', 'version: 0.3.2+6')
pubspec_path.write_text(pubspec, encoding='utf-8')

test_path.write_text(
    '''import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:vmeste_goal/main.dart';

void main() {
  testWidgets('first launch explains the product promise', (tester) async {
    SharedPreferences.setMockInitialValues({});
    final app = AppState();
    await tester.pumpWidget(VmesteApp(app: app));

    expect(find.text('Вместе к цели'), findsOneWidget);
    expect(
      find.text('Бывает, что цель важна, но одному трудно начать и не бросить.'),
      findsOneWidget,
    );
  });

  testWidgets('today starts with the main goal', (tester) async {
    SharedPreferences.setMockInitialValues({});
    final app = AppState()..onboarded = true;
    await tester.pumpWidget(VmesteApp(app: app));

    expect(find.text('Чего вы хотите добиться?'), findsOneWidget);
    expect(find.text('Добавить главную цель'), findsOneWidget);
    expect(find.text('Добавить дело'), findsOneWidget);
  });

  testWidgets('working together is visible for an active goal action', (
    tester,
  ) async {
    SharedPreferences.setMockInitialValues({});
    final app = AppState()
      ..onboarded = true
      ..goal = Goal('Закончить сайт', 'Сайт опубликован', 20, []);
    app.actions.add(
      ActionItem(
        id: '1',
        title: 'Написать первый экран',
        small: '',
        minutes: 15,
        support: Support.solo,
        goal: true,
      ),
    );

    await tester.pumpWidget(VmesteApp(app: app));

    expect(find.text('Действие для цели на сегодня'), findsOneWidget);
    expect(find.text('Начать вместе'), findsOneWidget);
    expect(find.text('Вместе'), findsWidgets);
  });
}
''',
    encoding='utf-8',
)
