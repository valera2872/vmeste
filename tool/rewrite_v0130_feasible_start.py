from pathlib import Path

main_path = Path('lib/main.dart')
pubspec_path = Path('pubspec.yaml')
text = main_path.read_text(encoding='utf-8')
pubspec = pubspec_path.read_text(encoding='utf-8')

if 'enum StartBarrier {' in text:
    print('v0.13.0 feasible start already applied')
    raise SystemExit(0)


def replace_once(old: str, new: str, label: str) -> None:
    global text
    if old not in text:
        raise SystemExit(f'{label} anchor not found')
    text = text.replace(old, new, 1)


# Models and transparent decision rules.
start_models = r'''
enum StartBarrier {
  unclear,
  tooBig,
  lowEnergy,
  overload,
  fear,
  perfectionism,
  noMeaning,
  noSupport,
}

enum StartLevel { full, small, contact }

class StartPlan {
  const StartPlan({
    required this.barrier,
    required this.title,
    required this.explanation,
    required this.condition,
    required this.fullStep,
    required this.smallStep,
    required this.contactStep,
    required this.recommendedLevel,
  });

  final StartBarrier barrier;
  final String title;
  final String explanation;
  final String condition;
  final String fullStep;
  final String smallStep;
  final String contactStep;
  final StartLevel recommendedLevel;
}

class StartAttempt {
  StartAttempt({
    required this.actionId,
    required this.barrier,
    required this.level,
    String? id,
    DateTime? createdAt,
    this.startedAt,
    this.completedAt,
    this.helpful,
  }) : id = id ?? DateTime.now().microsecondsSinceEpoch.toString(),
       createdAt = createdAt ?? DateTime.now();

  final String id;
  final String actionId;
  StartBarrier barrier;
  StartLevel level;
  final DateTime createdAt;
  DateTime? startedAt;
  DateTime? completedAt;
  bool? helpful;

  Map<String, dynamic> toJson() => {
    'id': id,
    'actionId': actionId,
    'barrier': barrier.name,
    'level': level.name,
    'createdAt': createdAt.toIso8601String(),
    'startedAt': startedAt?.toIso8601String(),
    'completedAt': completedAt?.toIso8601String(),
    'helpful': helpful,
  };

  factory StartAttempt.fromJson(Map<String, dynamic> json) {
    final now = DateTime.now();
    return StartAttempt(
      id: (json['id'] ?? now.microsecondsSinceEpoch).toString(),
      actionId: (json['actionId'] ?? '').toString(),
      barrier: StartBarrier.values.firstWhere(
        (value) => value.name == json['barrier'],
        orElse: () => StartBarrier.unclear,
      ),
      level: StartLevel.values.firstWhere(
        (value) => value.name == json['level'],
        orElse: () => StartLevel.small,
      ),
      createdAt: DateTime.tryParse((json['createdAt'] ?? '').toString()) ?? now,
      startedAt: DateTime.tryParse((json['startedAt'] ?? '').toString()),
      completedAt: DateTime.tryParse((json['completedAt'] ?? '').toString()),
      helpful: json['helpful'],
    );
  }
}

String startBarrierTitle(StartBarrier barrier) => switch (barrier) {
  StartBarrier.unclear => 'Непонятно, с чего начать',
  StartBarrier.tooBig => 'Действие кажется слишком большим',
  StartBarrier.lowEnergy => 'Сейчас мало сил',
  StartBarrier.overload => 'В голове слишком много всего',
  StartBarrier.fear => 'Страшно ошибиться или получить оценку',
  StartBarrier.perfectionism => 'Хочется сделать идеально',
  StartBarrier.noMeaning => 'Не вижу смысла или не хочу это делать',
  StartBarrier.noSupport => 'Не хватает внешней поддержки',
};

String startBarrierShort(StartBarrier barrier) => switch (barrier) {
  StartBarrier.unclear => 'Сначала найдём одно физическое действие.',
  StartBarrier.tooBig => 'Уменьшим объём без обесценивания результата.',
  StartBarrier.lowEnergy => 'Подберём нагрузку для текущего состояния.',
  StartBarrier.overload => 'Уберём конкуренцию между несколькими делами.',
  StartBarrier.fear => 'Заменим итоговый результат безопасной пробой.',
  StartBarrier.perfectionism => 'Определим достаточно хороший результат.',
  StartBarrier.noMeaning => 'Проверим, нужно ли действие выполнять вообще.',
  StartBarrier.noSupport => 'Добавим человека или короткий отчёт.',
};

IconData startBarrierIcon(StartBarrier barrier) => switch (barrier) {
  StartBarrier.unclear => Icons.route_outlined,
  StartBarrier.tooBig => Icons.compress_rounded,
  StartBarrier.lowEnergy => Icons.battery_2_bar_rounded,
  StartBarrier.overload => Icons.layers_outlined,
  StartBarrier.fear => Icons.shield_outlined,
  StartBarrier.perfectionism => Icons.auto_awesome_outlined,
  StartBarrier.noMeaning => Icons.help_outline_rounded,
  StartBarrier.noSupport => Icons.people_alt_outlined,
};

String startLevelTitle(StartLevel level) => switch (level) {
  StartLevel.full => 'Полный вариант',
  StartLevel.small => 'Малый вариант',
  StartLevel.contact => 'Сохранить контакт',
};

StartPlan buildStartPlan(ActionItem item, StartBarrier barrier) {
  final first = SupportLogic.steps(item.title).first;
  final small = item.small.trim().isNotEmpty
      ? item.small.trim()
      : SupportLogic.smallStep(item.title);
  final contact = switch (barrier) {
    StartBarrier.unclear => 'Открыть нужное место и записать один следующий вопрос.',
    StartBarrier.tooBig => 'Подготовить всё для начала и сделать только первый фрагмент.',
    StartBarrier.lowEnergy => 'Подготовить действие и уделить ему две спокойные минуты.',
    StartBarrier.overload => 'Записать остальные мысли и оставить перед собой только это действие.',
    StartBarrier.fear => 'Создать черновик, который пока никто не увидит.',
    StartBarrier.perfectionism => 'Сделать намеренно несовершенную первую версию.',
    StartBarrier.noMeaning => 'Записать, зачем это нужно, или честно решить отказаться.',
    StartBarrier.noSupport => 'Написать человеку, что вы собираетесь начать.',
  };
  final title = switch (barrier) {
    StartBarrier.unclear => 'Сделаем понятным только первый шаг',
    StartBarrier.tooBig => 'Уменьшим действие до посильного объёма',
    StartBarrier.lowEnergy => 'Подберём вариант под количество сил',
    StartBarrier.overload => 'Сначала освободим место для одного действия',
    StartBarrier.fear => 'Заменим экзамен безопасной пробой',
    StartBarrier.perfectionism => 'Определим достаточно хороший результат',
    StartBarrier.noMeaning => 'Проверим, стоит ли это делать',
    StartBarrier.noSupport => 'Добавим внешнюю опору',
  };
  final explanation = switch (barrier) {
    StartBarrier.unclear => 'Не нужно понимать весь путь. Достаточно действия, после которого станет яснее, что делать дальше.',
    StartBarrier.tooBig => 'Большой результат остаётся целью, но сегодня можно выполнить только честно выбранную часть.',
    StartBarrier.lowEnergy => 'Недостаток сил — это условие задачи, а не недостаток характера. Объём можно временно уменьшить.',
    StartBarrier.overload => 'Несколько конкурирующих обязательств создают постоянное переключение. Сначала оставим одно.',
    StartBarrier.fear => 'Сейчас не требуется окончательный результат. Первая версия может быть пробой или черновиком.',
    StartBarrier.perfectionism => 'Заранее определите, что будет считаться достаточным. Улучшать можно после появления первой версии.',
    StartBarrier.noMeaning => 'Иногда трудность означает, что обязательство нужно пересмотреть, делегировать или удалить.',
    StartBarrier.noSupport => 'Другой человек не обязан контролировать вас. Достаточно знать, что кто-то в курсе вашего старта.',
  };
  final condition = switch (barrier) {
    StartBarrier.unclear => 'Откройте только нужный файл, страницу или место работы.',
    StartBarrier.tooBig => 'Уберите из поля зрения всё, что относится к следующим этапам.',
    StartBarrier.lowEnergy => 'Разрешите себе остановиться после выбранного объёма.',
    StartBarrier.overload => 'Запишите отвлекающие дела, но не начинайте их сейчас.',
    StartBarrier.fear => 'Назовите результат «черновик» или «проба».',
    StartBarrier.perfectionism => 'Выберите один критерий готовности вместо идеального качества.',
    StartBarrier.noMeaning => 'Сначала ответьте: что изменится, если этого не делать?',
    StartBarrier.noSupport => 'Выберите человека и отправьте одно короткое сообщение.',
  };
  final recommended = switch (barrier) {
    StartBarrier.noMeaning => StartLevel.contact,
    StartBarrier.noSupport => StartLevel.contact,
    StartBarrier.lowEnergy => StartLevel.small,
    StartBarrier.tooBig => StartLevel.small,
    StartBarrier.overload => StartLevel.contact,
    StartBarrier.fear => StartLevel.small,
    StartBarrier.perfectionism => StartLevel.small,
    StartBarrier.unclear => StartLevel.small,
  };
  return StartPlan(
    barrier: barrier,
    title: title,
    explanation: explanation,
    condition: condition,
    fullStep: item.title,
    smallStep: small,
    contactStep: contact,
    recommendedLevel: recommended,
  );
}

'''
notification_at = text.index('class NotificationService')
text = text[:notification_at] + start_models + text[notification_at:]

# Local persistence and learning history.
replace_once(
    '  final List<Challenge> challenges = [];\n  static const key',
    '  final List<Challenge> challenges = [];\n  final List<StartAttempt> startAttempts = [];\n  final Map<String, String> continuationPoints = {};\n  static const key',
    'start attempt state lists',
)
replace_once('static const schemaVersion = 6;', 'static const schemaVersion = 7;', 'schema version 7')
replace_once(
    '      _restorePausedRoutines();',
    '''      startAttempts.addAll(
        (j['startAttempts'] ?? []).map<StartAttempt>(
          (entry) => StartAttempt.fromJson(Map<String, dynamic>.from(entry)),
        ),
      );
      continuationPoints.addAll(
        Map<String, String>.from(j['continuationPoints'] ?? const {}),
      );
      _restorePausedRoutines();''',
    'start attempt load',
)
replace_once(
    "    'challenges': challenges.map((e) => e.toJson()).toList(),\n  };",
    "    'challenges': challenges.map((e) => e.toJson()).toList(),\n    'startAttempts': startAttempts.map((e) => e.toJson()).toList(),\n    'continuationPoints': continuationPoints,\n  };",
    'start attempt payload',
)

start_methods = r'''  StartAttempt beginStartAttempt(
    ActionItem item,
    StartBarrier barrier,
    StartLevel level,
  ) {
    final attempt = StartAttempt(
      actionId: item.id,
      barrier: barrier,
      level: level,
    );
    startAttempts.insert(0, attempt);
    notifyListeners();
    save();
    return attempt;
  }

  void updateStartAttemptLevel(StartAttempt attempt, StartLevel level) {
    attempt.level = level;
    notifyListeners();
    save();
  }

  void markStartAttemptStarted(StartAttempt? attempt) {
    if (attempt == null || attempt.startedAt != null) return;
    attempt.startedAt = DateTime.now();
    notifyListeners();
    save();
  }

  void finishStartAttempt(String actionId, ResultState state) {
    StartAttempt? attempt;
    for (final value in startAttempts) {
      if (value.actionId == actionId && value.completedAt == null) {
        attempt = value;
        break;
      }
    }
    if (attempt == null) return;
    attempt.completedAt = DateTime.now();
    attempt.helpful = switch (state) {
      ResultState.done || ResultState.part => true,
      ResultState.missed => false,
      ResultState.moved => null,
    };
    notifyListeners();
    save();
  }

  void setContinuationPoint(String actionId, String value) {
    final point = value.trim();
    if (point.isEmpty) {
      continuationPoints.remove(actionId);
    } else {
      continuationPoints[actionId] = point;
    }
    notifyListeners();
    save();
  }

  String continuationFor(String actionId) =>
      continuationPoints[actionId]?.trim() ?? '';

  String get feasibleStartInsight {
    if (startAttempts.isEmpty) {
      return 'После нескольких попыток здесь появится наблюдение о том, что чаще мешает начать и какой объём помогает.';
    }
    final counts = <StartBarrier, int>{};
    for (final attempt in startAttempts) {
      counts[attempt.barrier] = (counts[attempt.barrier] ?? 0) + 1;
    }
    final barrier = counts.entries.reduce(
      (a, b) => a.value >= b.value ? a : b,
    ).key;
    final started = startAttempts.where((value) => value.startedAt != null).length;
    return 'Чаще всего отмечалось: «${startBarrierTitle(barrier)}». После подбора варианта действие началось в $started из ${startAttempts.length} случаев.';
  }

'''
challenge_methods_at = text.index('  void addChallenge(')
text = text[:challenge_methods_at] + start_methods + text[challenge_methods_at:]

# Replace the pre-start choice with the richer barrier flow. Active-session help stays pause-first.
session_start = text.index('class _SessionState extends State<Session>')
replace_once(
    '  StartDifficultyChoice? startAdjustment;\n  BlockerOutcome? activeAdjustment;',
    '  StartPlan? startPlan;\n  StartAttempt? startAttempt;\n  StartLevel startLevel = StartLevel.full;\n  BlockerOutcome? activeAdjustment;',
    'session feasible start fields',
)

method_start = text.index('  Future<void> openStartDifficulty() async {', session_start)
method_end = text.index('  Future<void> openActiveDifficulty() async {', method_start)
new_start_methods = r'''  Future<void> openStartDifficulty() async {
    final barrier = await showModalBottomSheet<StartBarrier>(
      context: context,
      isScrollControlled: true,
      useSafeArea: true,
      showDragHandle: true,
      builder: (_) => DraggableScrollableSheet(
        expand: false,
        initialChildSize: .86,
        minChildSize: .62,
        maxChildSize: .96,
        builder: (context, controller) => StartBarrierSheet(
          scrollController: controller,
        ),
      ),
    );
    if (barrier == null || !mounted) return;
    final plan = buildStartPlan(widget.item, barrier);
    final attempt = widget.app.beginStartAttempt(
      widget.item,
      barrier,
      plan.recommendedLevel,
    );
    setState(() {
      startPlan = plan;
      startAttempt = attempt;
      startLevel = plan.recommendedLevel;
      _applyStartLevel(plan.recommendedLevel);
    });
  }

  void _applyStartLevel(StartLevel level) {
    startLevel = level;
    final fullSeconds = widget.item.minutes * 60;
    left = switch (level) {
      StartLevel.full => fullSeconds,
      StartLevel.small => fullSeconds > 300 ? 300 : fullSeconds,
      StartLevel.contact => fullSeconds > 120 ? 120 : fullSeconds,
    };
  }

  void selectStartLevel(StartLevel level) {
    setState(() => _applyStartLevel(level));
    final attempt = startAttempt;
    if (attempt != null) {
      widget.app.updateStartAttemptLevel(attempt, level);
    }
  }

  String get startButtonLabel => switch (startLevel) {
    StartLevel.full => 'Начать действие',
    StartLevel.small => 'Начать малый вариант',
    StartLevel.contact => 'Сделать сохранительный шаг',
  };

  Future<void> startWithAdjustment() async {
    if (startPlan?.barrier == StartBarrier.noSupport) {
      await shareStartMessage(
        widget.item.title,
        (left / 60).ceil(),
        Support.together,
      );
    }
    if (!mounted) return;
    widget.app.markStartAttemptStarted(startAttempt);
    start();
  }

'''
text = text[:method_start] + new_start_methods + text[method_end:]

button_key = text.index("              key: const ValueKey('start-difficulty-button')", session_start)
pre_start_begin = text.rfind('            if (startAdjustment != null) ...[', session_start, button_key)
if pre_start_begin < 0:
    raise SystemExit('pre-start feasible plan anchor not found')
pre_start_end = text.index('          ] else ...[', button_key)
new_pre_start = r'''            if (startPlan != null) ...[
              _FeasibleStartPlanCard(
                plan: startPlan!,
                level: startLevel,
                onLevel: selectStartLevel,
                onChange: openStartDifficulty,
              ),
              const SizedBox(height: 13),
            ],
            FilledButton.icon(
              key: const ValueKey('start-confirm-button'),
              onPressed: startWithAdjustment,
              icon: const Icon(Icons.play_arrow_rounded),
              label: Text(startButtonLabel),
            ),
            const SizedBox(height: 9),
            OutlinedButton.icon(
              key: const ValueKey('start-difficulty-button'),
              onPressed: openStartDifficulty,
              icon: const Icon(Icons.tune_rounded),
              label: Text(
                startPlan == null
                    ? 'Трудно начать'
                    : 'Выбрать другое препятствие',
              ),
            ),
'''
text = text[:pre_start_begin] + new_pre_start + text[pre_start_end:]

# Replace the old pre-start card, preserving the accepted active-session card.
card_start = text.index('class _StartAdjustmentPlanCard')
card_end = text.index('class _ActiveAdjustmentPlanCard', card_start)
new_cards = r'''class StartBarrierSheet extends StatelessWidget {
  const StartBarrierSheet({required this.scrollController, super.key});
  final ScrollController scrollController;

  @override
  Widget build(BuildContext context) => ListView(
    key: const ValueKey('start-barrier-sheet'),
    controller: scrollController,
    padding: const EdgeInsets.fromLTRB(18, 2, 18, 32),
    children: [
      const Text(
        'Что делает начало трудным?',
        style: TextStyle(fontSize: 24, fontWeight: FontWeight.w900),
      ),
      const SizedBox(height: 7),
      const Text(
        'Это не диагноз. Выберите ближайшее описание текущей ситуации — условия можно изменить.',
        style: TextStyle(color: Color(0xFF66736E), height: 1.4),
      ),
      const SizedBox(height: 16),
      ...StartBarrier.values.map(
        (barrier) => _StartBarrierOption(
          barrier: barrier,
          onTap: () => Navigator.pop(context, barrier),
        ),
      ),
    ],
  );
}

class _StartBarrierOption extends StatelessWidget {
  const _StartBarrierOption({required this.barrier, required this.onTap});
  final StartBarrier barrier;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.only(bottom: 10),
    child: Material(
      color: Colors.white,
      clipBehavior: Clip.antiAlias,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
        side: const BorderSide(color: Color(0xFFE0E5E1)),
      ),
      child: InkWell(
        key: ValueKey('start-barrier-${barrier.name}'),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(13),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 42,
                height: 42,
                decoration: BoxDecoration(
                  color: const Color(0xFFE7F2ED),
                  borderRadius: BorderRadius.circular(14),
                ),
                child: Icon(startBarrierIcon(barrier), color: green, size: 21),
              ),
              const SizedBox(width: 11),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      startBarrierTitle(barrier),
                      style: const TextStyle(fontWeight: FontWeight.w900),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      startBarrierShort(barrier),
                      style: const TextStyle(
                        color: Color(0xFF66736E),
                        fontSize: 12.5,
                        height: 1.35,
                      ),
                    ),
                  ],
                ),
              ),
              const Padding(
                padding: EdgeInsets.only(top: 10),
                child: Icon(Icons.chevron_right_rounded, color: Color(0xFF8B9691)),
              ),
            ],
          ),
        ),
      ),
    ),
  );
}

class _FeasibleStartPlanCard extends StatelessWidget {
  const _FeasibleStartPlanCard({
    required this.plan,
    required this.level,
    required this.onLevel,
    required this.onChange,
  });

  final StartPlan plan;
  final StartLevel level;
  final ValueChanged<StartLevel> onLevel;
  final VoidCallback onChange;

  String valueFor(StartLevel value) => switch (value) {
    StartLevel.full => plan.fullStep,
    StartLevel.small => plan.smallStep,
    StartLevel.contact => plan.contactStep,
  };

  @override
  Widget build(BuildContext context) => Container(
    key: const ValueKey('feasible-start-plan'),
    padding: const EdgeInsets.all(18),
    decoration: BoxDecoration(
      color: const Color(0xFFEAF4EF),
      borderRadius: BorderRadius.circular(24),
      border: Border.all(color: const Color(0x4939776B)),
    ),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Row(
          children: [
            Icon(Icons.tune_rounded, color: green),
            SizedBox(width: 8),
            Expanded(
              child: Text(
                'ТАЙМЕР ЕЩЁ НЕ ЗАПУЩЕН',
                style: TextStyle(
                  color: green,
                  fontSize: 10.5,
                  fontWeight: FontWeight.w900,
                  letterSpacing: .75,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 13),
        Text(
          plan.title,
          style: const TextStyle(fontSize: 19, fontWeight: FontWeight.w900),
        ),
        const SizedBox(height: 7),
        Text(plan.explanation, style: const TextStyle(height: 1.42)),
        const SizedBox(height: 12),
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(16),
          ),
          child: Text(
            'Изменить условие: ${plan.condition}',
            style: const TextStyle(fontWeight: FontWeight.w700, height: 1.35),
          ),
        ),
        const SizedBox(height: 13),
        const Text(
          'Какой объём подходит сейчас?',
          style: TextStyle(fontWeight: FontWeight.w900),
        ),
        const SizedBox(height: 8),
        Wrap(
          spacing: 7,
          runSpacing: 7,
          children: StartLevel.values
              .map(
                (value) => ChoiceChip(
                  key: ValueKey('start-level-${value.name}'),
                  label: Text(startLevelTitle(value)),
                  selected: level == value,
                  onSelected: (_) => onLevel(value),
                ),
              )
              .toList(),
        ),
        const SizedBox(height: 10),
        Container(
          key: const ValueKey('selected-start-level'),
          width: double.infinity,
          padding: const EdgeInsets.all(13),
          decoration: BoxDecoration(
            color: const Color(0xFFFFFCF4),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: const Color(0xFFE7DDBE)),
          ),
          child: Text(
            valueFor(level),
            style: const TextStyle(fontWeight: FontWeight.w800, height: 1.38),
          ),
        ),
        Align(
          alignment: Alignment.centerLeft,
          child: TextButton(
            onPressed: onChange,
            child: const Text('Выбрать другое препятствие'),
          ),
        ),
      ],
    ),
  );
}

'''
text = text[:card_start] + new_cards + text[card_end:]

# Continuation point when the action is not fully finished.
finish_start = text.index('  Future<void> finish(ResultState state) async {', session_start)
finish_end = text.index('  @override\n  Widget build', finish_start)
new_finish = r'''  Future<void> finish(ResultState state) async {
    timer?.cancel();
    Navigator.pop(context);

    if (state != ResultState.done && mounted) {
      final point = await showContinuationPointSheet(
        context,
        initial: widget.app.continuationFor(widget.item.id),
      );
      if (point != null) {
        widget.app.setContinuationPoint(widget.item.id, point);
      }
    }

    if (state == ResultState.moved) {
      final when = await showActionSchedule(context, widget.item.scheduledAt);
      if (when == null || !mounted) return;
      await widget.app.reschedule(widget.item, when);
    } else {
      widget.app.complete(widget.item, state);
    }
    widget.app.finishStartAttempt(widget.item.id, state);
    if (widget.agreement != null) {
      widget.app.setSupportAgreementStatus(
        widget.agreement!,
        SupportInviteStatus.completed,
      );
    }
    if (!mounted) return;
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(
        builder: (_) => ResultPage(
          app: widget.app,
          item: widget.item,
          state: state,
        ),
      ),
    );
  }

'''
text = text[:finish_start] + new_finish + text[finish_end:]

continuation_ui = r'''Future<String?> showContinuationPointSheet(
  BuildContext context, {
  String initial = '',
}) async {
  final controller = TextEditingController(text: initial);
  final result = await showModalBottomSheet<String>(
    context: context,
    isScrollControlled: true,
    useSafeArea: true,
    showDragHandle: true,
    builder: (sheetContext) => Padding(
      padding: EdgeInsets.fromLTRB(
        18,
        2,
        18,
        22 + MediaQuery.viewInsetsOf(sheetContext).bottom,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'С какого места продолжить?',
            style: TextStyle(fontSize: 23, fontWeight: FontWeight.w900),
          ),
          const SizedBox(height: 7),
          const Text(
            'Запишите одно конкретное действие, чтобы в следующий раз не разбираться заново.',
          ),
          const SizedBox(height: 14),
          TextField(
            key: const ValueKey('continuation-point-field'),
            controller: controller,
            autofocus: true,
            maxLines: 3,
            decoration: const InputDecoration(
              labelText: 'Точка продолжения',
              hintText: 'Например: открыть экран оплаты и проверить восстановление покупки',
            ),
          ),
          const SizedBox(height: 13),
          Row(
            children: [
              Expanded(
                child: TextButton(
                  onPressed: () => Navigator.pop(sheetContext, ''),
                  child: const Text('Не сохранять'),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: FilledButton(
                  key: const ValueKey('save-continuation-point'),
                  onPressed: () => Navigator.pop(
                    sheetContext,
                    controller.text.trim(),
                  ),
                  child: const Text('Сохранить'),
                ),
              ),
            ],
          ),
        ],
      ),
    ),
  );
  controller.dispose();
  return result;
}

'''
result_page_at = text.index('class ResultPage')
text = text[:result_page_at] + continuation_ui + text[result_page_at:]

# Show the saved return point on the result screen.
result_start = text.index('class ResultPage')
result_end = text.index('class ', result_start + len('class ResultPage'))
result_block = text[result_start:result_end]
result_block = result_block.replace(
    '''    final canShare =
        item.support == Support.together ||
        item.support == Support.report ||
        item.support == Support.curator;''',
    '''    final canShare =
        item.support == Support.together ||
        item.support == Support.report ||
        item.support == Support.curator;
    final continuation = app.continuationFor(item.id);''',
    1,
)
result_marker = '              if (canShare && ok) ...['
if result_marker not in result_block:
    raise SystemExit('result continuation marker not found')
result_block = result_block.replace(
    result_marker,
    '''              if (continuation.isNotEmpty) ...[
                const SizedBox(height: 16),
                Container(
                  key: const ValueKey('saved-continuation-point'),
                  width: double.infinity,
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: const Color(0xFFEAF4EF),
                    borderRadius: BorderRadius.circular(18),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'ТОЧКА ПРОДОЛЖЕНИЯ',
                        style: TextStyle(
                          color: green,
                          fontSize: 10.5,
                          fontWeight: FontWeight.w900,
                          letterSpacing: .7,
                        ),
                      ),
                      const SizedBox(height: 5),
                      Text(
                        continuation,
                        style: const TextStyle(fontWeight: FontWeight.w800),
                      ),
                    ],
                  ),
                ),
              ],
''' + result_marker,
    1,
)
text = text[:result_start] + result_block + text[result_end:]

# Add a cautious learning card to the goal path.
replace_once(
    '          _GoalInsightCard(app: app),\n          if (completed.isNotEmpty)',
    '''          _GoalInsightCard(app: app),
          if (app.startAttempts.isNotEmpty) ...[
            const SizedBox(height: 12),
            _FeasibleStartInsightCard(app: app),
          ],
          if (completed.isNotEmpty)''',
    'goal feasible start insight insertion',
)
insight_class = r'''class _FeasibleStartInsightCard extends StatelessWidget {
  const _FeasibleStartInsightCard({required this.app});
  final AppState app;

  @override
  Widget build(BuildContext context) => Container(
    key: const ValueKey('feasible-start-insight'),
    width: double.infinity,
    padding: const EdgeInsets.all(16),
    decoration: BoxDecoration(
      color: const Color(0xFFFFF8E8),
      borderRadius: BorderRadius.circular(21),
      border: Border.all(color: const Color(0xFFE8D9AE)),
    ),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Row(
          children: [
            Icon(Icons.psychology_alt_outlined, color: Color(0xFF8B6B20)),
            SizedBox(width: 8),
            Expanded(
              child: Text(
                'ЧТО МЕШАЕТ НАЧАТЬ',
                style: TextStyle(
                  color: Color(0xFF8B6B20),
                  fontSize: 10.5,
                  fontWeight: FontWeight.w900,
                  letterSpacing: .75,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Text(
          app.feasibleStartInsight,
          style: const TextStyle(color: ink, height: 1.42),
        ),
        const SizedBox(height: 6),
        const Text(
          'Это предварительное наблюдение по вашим отметкам, а не диагноз.',
          style: TextStyle(color: Color(0xFF746B58), fontSize: 11.5),
        ),
      ],
    ),
  );
}

'''
history_at = text.index('class _GoalHistoryRow')
text = text[:history_at] + insight_class + text[history_at:]

if 'version: 0.12.0+28' not in pubspec:
    raise SystemExit('Expected materialized v0.12.0 version not found')
pubspec = pubspec.replace('version: 0.12.0+28', 'version: 0.13.0+29', 1)

main_path.write_text(text, encoding='utf-8')
pubspec_path.write_text(pubspec, encoding='utf-8')
print('Applied v0.13.0 feasible start')
