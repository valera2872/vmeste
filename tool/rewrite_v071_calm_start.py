from pathlib import Path
import re

main_path = Path('lib/main.dart')
pubspec_path = Path('pubspec.yaml')
text = main_path.read_text(encoding='utf-8')

session_start = text.index('class _SessionState extends State<Session>')

text = text.replace(
    '  int step = 0;\n',
    '  int step = 0;\n  StartDifficultyChoice? startAdjustment;\n  BlockerOutcome? activeAdjustment;\n',
    1,
)

method_start = text.index('  Future<void> openStartDifficulty() async {', session_start)
method_end = text.index('  Future<void> finish(ResultState state) async {', method_start)
methods = r'''  Future<void> openStartDifficulty() async {
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

    if (choice == StartDifficultyChoice.minimum && widget.item.small.isEmpty) {
      widget.item.small = SupportLogic.smallStep(widget.item.title);
      widget.app.updateAction(widget.item);
    }
    if (choice == StartDifficultyChoice.clarify) {
      widget.app.setSupport(widget.item, Support.ai);
    } else if (choice == StartDifficultyChoice.together) {
      widget.app.setSupport(widget.item, Support.together);
    } else if (choice == StartDifficultyChoice.report) {
      widget.app.setSupport(widget.item, Support.report);
    }
    if (!mounted) return;
    setState(() {
      startAdjustment = choice;
      if ((choice == StartDifficultyChoice.minimum ||
              choice == StartDifficultyChoice.focus) &&
          left > 300) {
        left = 300;
      }
    });
  }

  String get startButtonLabel {
    final minutes = (left / 60).ceil();
    return switch (startAdjustment) {
      StartDifficultyChoice.together => 'Позвать человека и начать',
      StartDifficultyChoice.report => 'Сообщить и начать',
      _ => 'Начать на $minutes минут',
    };
  }

  Future<void> startWithAdjustment() async {
    final choice = startAdjustment;
    if (choice == StartDifficultyChoice.together) {
      await shareStartMessage(
        widget.item.title,
        (left / 60).ceil(),
        Support.together,
      );
    } else if (choice == StartDifficultyChoice.report) {
      await shareStartMessage(
        widget.item.title,
        (left / 60).ceil(),
        Support.report,
      );
    }
    if (!mounted) return;
    start();
  }

  Future<void> openActiveDifficulty() async {
    setState(() {
      paused = true;
      activeAdjustment = null;
    });
    final outcome = await showModalBottomSheet<BlockerOutcome>(
      context: context,
      isScrollControlled: true,
      useSafeArea: true,
      showDragHandle: true,
      builder: (_) => DraggableScrollableSheet(
        expand: false,
        initialChildSize: .82,
        minChildSize: .58,
        maxChildSize: .96,
        builder: (context, controller) => Blocker(
          item: widget.item,
          scrollController: controller,
        ),
      ),
    );
    if (outcome == null || !mounted) return;

    if (outcome == BlockerOutcome.continueSmall && widget.item.small.isEmpty) {
      widget.item.small = SupportLogic.smallStep(widget.item.title);
      widget.app.updateAction(widget.item);
    }
    if (outcome == BlockerOutcome.together) {
      widget.app.setSupport(widget.item, Support.together);
    }
    if (!mounted) return;
    setState(() {
      activeAdjustment = outcome;
      if (outcome == BlockerOutcome.continueSmall && left > 300) {
        left = 300;
      }
    });
  }

  Future<void> applyActiveAdjustment() async {
    final outcome = activeAdjustment;
    if (outcome == null) return;

    switch (outcome) {
      case BlockerOutcome.continueWork:
        setState(() {
          activeAdjustment = null;
          paused = false;
        });
      case BlockerOutcome.continueSmall:
        setState(() {
          if (left > 300) left = 300;
          activeAdjustment = null;
          paused = false;
        });
      case BlockerOutcome.together:
        await shareStartMessage(
          widget.item.title,
          (left / 60).ceil(),
          Support.together,
        );
        if (!mounted) return;
        setState(() {
          activeAdjustment = null;
          paused = false;
        });
      case BlockerOutcome.finish:
        await showModalBottomSheet(
          context: context,
          showDragHandle: true,
          builder: (_) => Finish(onFinish: finish),
        );
    }
  }

'''
text = text[:method_start] + methods + text[method_end:]

button_key = text.index("              key: const ValueKey('start-difficulty-button')", session_start)
pre_start_begin = text.rfind('            FilledButton.icon(', session_start, button_key)
pre_start_end = text.index('          ] else ...[', button_key)
pre_start = r'''            if (startAdjustment != null) ...[
              _StartAdjustmentPlanCard(
                choice: startAdjustment!,
                item: widget.item,
                onChange: openStartDifficulty,
              ),
              const SizedBox(height: 13),
            ],
            FilledButton.icon(
              key: const ValueKey('start-confirm-button'),
              onPressed: startWithAdjustment,
              icon: Icon(
                startAdjustment == StartDifficultyChoice.together ||
                        startAdjustment == StartDifficultyChoice.report
                    ? Icons.send_rounded
                    : Icons.play_arrow_rounded,
              ),
              label: Text(startButtonLabel),
            ),
            const SizedBox(height: 9),
            OutlinedButton.icon(
              key: const ValueKey('start-difficulty-button'),
              onPressed: openStartDifficulty,
              icon: const Icon(Icons.support_rounded),
              label: Text(
                startAdjustment == null
                    ? 'Трудно начать'
                    : 'Выбрать другую трудность',
              ),
            ),
'''
text = text[:pre_start_begin] + pre_start + text[pre_start_end:]

hard_label = text.index("label: const Text('Мне трудно')", session_start)
active_row_begin = text.rfind('            Row(', session_start, hard_label)
active_row_end = text.index('            const SizedBox(height: 12),', hard_label)
active_row = r'''            if (activeAdjustment != null) ...[
              _ActiveAdjustmentPlanCard(
                outcome: activeAdjustment!,
                item: widget.item,
                onApply: applyActiveAdjustment,
                onChange: openActiveDifficulty,
              ),
            ] else
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () => setState(() => paused = !paused),
                      icon: Icon(paused ? Icons.play_arrow : Icons.pause),
                      label: Text(paused ? 'Продолжить' : 'Пауза'),
                    ),
                  ),
                  const SizedBox(width: 9),
                  Expanded(
                    child: OutlinedButton.icon(
                      key: const ValueKey('active-difficulty-button'),
                      onPressed: openActiveDifficulty,
                      icon: const Icon(Icons.support),
                      label: const Text('Мне трудно'),
                    ),
                  ),
                ],
              ),
'''
text = text[:active_row_begin] + active_row + text[active_row_end:]

cards = r'''class _StartAdjustmentPlanCard extends StatelessWidget {
  const _StartAdjustmentPlanCard({
    required this.choice,
    required this.item,
    required this.onChange,
  });

  final StartDifficultyChoice choice;
  final ActionItem item;
  final VoidCallback onChange;

  @override
  Widget build(BuildContext context) {
    final firstStep = SupportLogic.steps(item.title).first;
    final minimum = item.small.isNotEmpty
        ? item.small
        : SupportLogic.smallStep(item.title);
    final icon = switch (choice) {
      StartDifficultyChoice.clarify => Icons.route_outlined,
      StartDifficultyChoice.minimum => Icons.compress_rounded,
      StartDifficultyChoice.focus => Icons.hourglass_bottom_rounded,
      StartDifficultyChoice.together => Icons.people_alt_outlined,
      StartDifficultyChoice.report => Icons.verified_outlined,
    };
    final title = switch (choice) {
      StartDifficultyChoice.clarify => 'Сделайте понятным только первый шаг',
      StartDifficultyChoice.minimum => 'Разрешите себе минимальный вариант',
      StartDifficultyChoice.focus => 'Оставьте только пять спокойных минут',
      StartDifficultyChoice.together => 'Начните рядом с другим человеком',
      StartDifficultyChoice.report => 'Договоритесь о коротком отчёте',
    };
    final text = switch (choice) {
      StartDifficultyChoice.clarify =>
        'Не нужно сейчас понимать весь путь. Достаточно одного действия, после которого станет яснее, что делать дальше.',
      StartDifficultyChoice.minimum =>
        'Минимальный вариант считается началом, а не неудачей. После него можно остановиться или продолжить.',
      StartDifficultyChoice.focus =>
        'Таймер закончится через пять минут. Продолжать после этого необязательно.',
      StartDifficultyChoice.together =>
        'Другой человек может заниматься своим делом. Важно только начать одновременно или остаться на связи.',
      StartDifficultyChoice.report =>
        'Сообщите, что начинаете, и договоритесь отправить короткий результат после работы.',
    };
    final detail = switch (choice) {
      StartDifficultyChoice.clarify => firstStep,
      StartDifficultyChoice.minimum => minimum,
      StartDifficultyChoice.focus =>
        'Уберите одно отвлечение и сделайте только первые пять минут.',
      StartDifficultyChoice.together =>
        'Сначала отправьте приглашение. Отсчёт начнётся только после вашего подтверждения.',
      StartDifficultyChoice.report =>
        'Сначала выберите человека для отчёта. Отсчёт начнётся только после вашего подтверждения.',
    };

    return Container(
      key: const ValueKey('start-adjustment-card'),
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: const Color(0xFFEAF4EF),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: const Color(0x4939776B)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 42,
                height: 42,
                decoration: const BoxDecoration(
                  color: Colors.white,
                  shape: BoxShape.circle,
                ),
                child: Icon(icon, color: green),
              ),
              const SizedBox(width: 11),
              const Expanded(
                child: Text(
                  'ТАЙМЕР ЕЩЁ НЕ ЗАПУЩЕН',
                  style: TextStyle(
                    color: green,
                    fontSize: 11,
                    fontWeight: FontWeight.w900,
                    letterSpacing: .75,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          const Text(
            'Что поможет сейчас',
            style: TextStyle(fontSize: 21, fontWeight: FontWeight.w900),
          ),
          const SizedBox(height: 9),
          Text(
            title,
            style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w900),
          ),
          const SizedBox(height: 6),
          Text(text, style: const TextStyle(height: 1.42)),
          const SizedBox(height: 12),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(13),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
            ),
            child: Text(
              detail,
              style: const TextStyle(fontWeight: FontWeight.w700, height: 1.38),
            ),
          ),
          Align(
            alignment: Alignment.centerLeft,
            child: TextButton(
              onPressed: onChange,
              child: const Text('Выбрать другую трудность'),
            ),
          ),
        ],
      ),
    );
  }
}

class _ActiveAdjustmentPlanCard extends StatelessWidget {
  const _ActiveAdjustmentPlanCard({
    required this.outcome,
    required this.item,
    required this.onApply,
    required this.onChange,
  });

  final BlockerOutcome outcome;
  final ActionItem item;
  final VoidCallback onApply;
  final VoidCallback onChange;

  @override
  Widget build(BuildContext context) {
    final firstStep = SupportLogic.steps(item.title).first;
    final minimum = item.small.isNotEmpty
        ? item.small
        : SupportLogic.smallStep(item.title);
    final title = switch (outcome) {
      BlockerOutcome.continueWork => 'Сначала изменим только ближайший шаг',
      BlockerOutcome.continueSmall => 'Сократим оставшуюся работу до пяти минут',
      BlockerOutcome.together => 'Продолжим рядом с другим человеком',
      BlockerOutcome.finish => 'Можно остановиться без обнуления результата',
    };
    final detail = switch (outcome) {
      BlockerOutcome.continueWork =>
        '$firstStep Уберите одно отвлечение и возвращайтесь только после готовности.',
      BlockerOutcome.continueSmall =>
        'Минимальный вариант: $minimum После пяти минут можно закончить.',
      BlockerOutcome.together =>
        'Сначала отправьте приглашение. Таймер останется на паузе, пока вы сами не продолжите.',
      BlockerOutcome.finish =>
        'Запишите выполненную часть, перенос или то, что сегодня не получилось.',
    };
    final button = switch (outcome) {
      BlockerOutcome.continueWork => 'Продолжить с изменением',
      BlockerOutcome.continueSmall => 'Сделать минимальный вариант',
      BlockerOutcome.together => 'Позвать человека и продолжить',
      BlockerOutcome.finish => 'Закончить на сегодня',
    };

    return Container(
      key: const ValueKey('active-adjustment-card'),
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: const Color(0xFFFFF3DE),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: const Color(0x55C7973F)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.pause_circle_outline_rounded, color: green),
              SizedBox(width: 8),
              Text(
                'ТАЙМЕР НА ПАУЗЕ',
                style: TextStyle(
                  color: green,
                  fontSize: 11,
                  fontWeight: FontWeight.w900,
                  letterSpacing: .75,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            title,
            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w900),
          ),
          const SizedBox(height: 8),
          Text(detail, style: const TextStyle(height: 1.42)),
          const SizedBox(height: 14),
          FilledButton.icon(
            key: const ValueKey('active-adjustment-apply'),
            onPressed: onApply,
            icon: Icon(
              outcome == BlockerOutcome.finish
                  ? Icons.stop_circle_outlined
                  : outcome == BlockerOutcome.together
                  ? Icons.people_alt_outlined
                  : Icons.play_arrow_rounded,
            ),
            label: Text(button),
          ),
          Align(
            alignment: Alignment.centerLeft,
            child: TextButton(
              key: const ValueKey('active-adjustment-change'),
              onPressed: onChange,
              child: const Text('Выбрать другую трудность'),
            ),
          ),
        ],
      ),
    );
  }
}

'''
insert_at = text.index('class StartDifficultySheet extends StatelessWidget')
text = text[:insert_at] + cards + text[insert_at:]

main_path.write_text(text, encoding='utf-8')

pubspec = pubspec_path.read_text(encoding='utf-8')
pubspec = re.sub(r'^version:\s*[^\n]+', 'version: 0.7.1+23', pubspec, count=1, flags=re.M)
pubspec_path.write_text(pubspec, encoding='utf-8')
print('Applied v0.7.1 calm start and pause-first support flow')
