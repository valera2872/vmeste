from pathlib import Path

main_path = Path('lib/main.dart')
pubspec_path = Path('pubspec.yaml')
text = main_path.read_text(encoding='utf-8')
pubspec = pubspec_path.read_text(encoding='utf-8')

if 'version: 0.4.1+10' in pubspec and 'Своя длительность в минутах' in text:
    print('v0.4.1 already applied')
    raise SystemExit(0)


def replace(old: str, new: str) -> None:
    global text
    if old not in text:
        raise SystemExit(f'Expected fragment not found:\n{old[:500]}')
    text = text.replace(old, new, 1)


def replace_between(start_marker: str, end_marker: str, new_block: str) -> None:
    global text
    start = text.index(start_marker)
    end = text.index(end_marker, start)
    text = text[:start] + new_block.rstrip() + '\n\n' + text[end:]


if 'version: 0.4.0+9' not in pubspec:
    raise SystemExit('Expected v0.4.0 pubspec version')
pubspec = pubspec.replace('version: 0.4.0+9', 'version: 0.4.1+10', 1)

replace(
    """          Row(
            children: [
              _metric('${app.goalDone}', 'сделано'),
              const SizedBox(width: 9),
              _metric('${g.minutes} мин', 'за один раз'),
              const SizedBox(width: 9),
              _metric('${g.areas.length}', 'частей цели'),
            ],
          ),""",
    """          Row(
            children: [
              _metric('${app.goalDone}', 'завершено'),
              const SizedBox(width: 9),
              _metric(
                '${app.actions.where((item) => item.goal && item.state == null).length}',
                'в работе',
              ),
              const SizedBox(width: 9),
              _metric(g.areas.isEmpty ? '—' : '${g.areas.length}', 'этапов'),
            ],
          ),""",
)

replace(
    """            const SizedBox(height: 16),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(18),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Когда цель будет достигнута?',
                      style: TextStyle(
                        fontWeight: FontWeight.w900,
                        fontSize: 17,
                      ),
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
            ),""",
    """            if (app.goal!.result.isNotEmpty) ...[
              const SizedBox(height: 16),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(18),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Что должно быть готово?',
                        style: TextStyle(
                          fontWeight: FontWeight.w900,
                          fontSize: 17,
                        ),
                      ),
                      const SizedBox(height: 7),
                      Text(app.goal!.result),
                    ],
                  ),
                ),
              ),
            ],""",
)

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
  bool showDetails = false;

  @override
  void initState() {
    super.initState();
    title = TextEditingController(text: widget.existing?.title ?? '');
    result = TextEditingController(text: widget.existing?.result ?? '');
    areas = TextEditingController(
      text: widget.existing?.areas.join(', ') ?? '',
    );
    showDetails = widget.existing != null &&
        (widget.existing!.result.isNotEmpty || widget.existing!.areas.isNotEmpty);
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
        widget.existing?.minutes ?? 0,
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
        const Text(
          'Сначала достаточно назвать цель. Следующее конкретное действие выберем отдельно.',
        ),
        const SizedBox(height: 18),
        VoiceField(
          controller: title,
          label: 'Моя цель',
          hint: 'Например: доделать ремонт в доме',
          lines: 3,
        ),
        const SizedBox(height: 8),
        TextButton.icon(
          onPressed: () => setState(() => showDetails = !showDetails),
          icon: Icon(showDetails ? Icons.expand_less : Icons.tune_rounded),
          label: Text(
            showDetails
                ? 'Скрыть результат и этапы'
                : 'Уточнить результат и этапы',
          ),
        ),
        if (showDetails) ...[
          const SizedBox(height: 8),
          VoiceField(
            controller: result,
            label: 'Что должно измениться или быть готово? Необязательно',
            hint: 'Например: ванная, кухня и коридор полностью закончены',
            lines: 3,
          ),
          const SizedBox(height: 13),
          VoiceField(
            controller: areas,
            label: 'На какие этапы можно разделить цель? Необязательно',
            hint: 'Например: ванная, кухня, электрика, стены',
            lines: 3,
          ),
          const SizedBox(height: 8),
          const Text(
            'Продолжительность выбирается отдельно для каждого действия.',
            style: TextStyle(fontSize: 13, color: Colors.black54),
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

replace_between('class GoalEditor extends StatefulWidget {', 'class ActionEditor extends StatefulWidget {', goal_editor)

replace(
    """  final title = TextEditingController(), small = TextEditingController();
  int minutes = 15;
  bool useTimer = true;""",
    """  final title = TextEditingController(), small = TextEditingController();
  final customMinutes = TextEditingController();
  int minutes = 15;
  bool useTimer = true;
  bool customTime = false;""",
)

replace(
    """  bool get supportLocked => widget.initialSupport != null;

  @override""",
    """  bool get supportLocked => widget.initialSupport != null;

  bool get durationReady {
    if (!useTimer) return true;
    if (!customTime) return minutes > 0;
    final value = int.tryParse(customMinutes.text.trim());
    return value != null && value > 0 && value <= 720;
  }

  @override""",
)

replace(
    """    title.dispose();
    small.dispose();
    super.dispose();""",
    """    title.dispose();
    small.dispose();
    customMinutes.dispose();
    super.dispose();""",
)

replace(
    """  Future<void> createAndStart(Support support) async {
    final action = ActionItem(""",
    """  Future<void> createAndStart(Support support) async {
    final selectedMinutes = customTime
        ? int.tryParse(customMinutes.text.trim()) ?? minutes
        : minutes;
    final action = ActionItem(""",
)

replace(
    """      minutes: useTimer ? minutes : 0,""",
    """      minutes: useTimer ? selectedMinutes : 0,""",
)

replace(
    """    final recommended = SupportLogic.recommend(title.text);
    final support = chosen ?? recommended.$1;

    final pageTitle""",
    """    final recommended = SupportLogic.recommend(title.text);
    final support = chosen ?? recommended.$1;
    const durationOptions = [10, 15, 30, 45, 60, 90, 120];

    final pageTitle""",
)

replace(
    """            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [5, 10, 15, 25, 40, 60, 90]
                  .map(
                    (value) => ChoiceChip(
                      label: Text('$value мин'),
                      selected: minutes == value,
                      onSelected: (_) => setState(() => minutes = value),
                    ),
                  )
                  .toList(),
            ),""",
    """            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                ...durationOptions.map(
                  (value) => ChoiceChip(
                    label: Text(
                      value == 60
                          ? '1 ч'
                          : value == 90
                          ? '1 ч 30 мин'
                          : value == 120
                          ? '2 ч'
                          : '$value мин',
                    ),
                    selected: !customTime && minutes == value,
                    onSelected: (_) => setState(() {
                      customTime = false;
                      minutes = value;
                      customMinutes.clear();
                    }),
                  ),
                ),
                ChoiceChip(
                  label: const Text('Своё'),
                  selected: customTime,
                  onSelected: (_) => setState(() => customTime = true),
                ),
              ],
            ),
            if (customTime) ...[
              const SizedBox(height: 12),
              TextField(
                controller: customMinutes,
                keyboardType: TextInputType.number,
                onChanged: (_) => setState(() {}),
                decoration: const InputDecoration(
                  labelText: 'Своя длительность в минутах',
                  hintText: 'Например: 80',
                  helperText: 'От 1 минуты до 12 часов',
                ),
              ),
            ],""",
)

replace(
    """            onPressed: title.text.trim().isEmpty
                ? null
                : () => createAndStart(support),""",
    """            onPressed: title.text.trim().isEmpty || !durationReady
                ? null
                : () => createAndStart(support),""",
)

main_path.write_text(text, encoding='utf-8')
pubspec_path.write_text(pubspec, encoding='utf-8')
print('Applied v0.4.1 goal and duration cleanup')
