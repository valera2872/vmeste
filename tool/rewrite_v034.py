from pathlib import Path

main_path = Path('lib/main.dart')
pubspec_path = Path('pubspec.yaml')
text = main_path.read_text(encoding='utf-8')


def replace(old: str, new: str) -> None:
    global text
    if old not in text:
        raise SystemExit(f'Expected fragment not found:\n{old[:320]}')
    text = text.replace(old, new, 1)


# First-launch message: personal method rather than generic motivation.
replace(
    """                IntroPage(
                  icon: Icons.handshake_rounded,
                  kicker: 'КОГДА ОДНОМУ ТРУДНО',
                  title:
                      'Бывает, что цель важна, но одному трудно начать и не бросить.',
                  text:
                      'Это не всегда вопрос силы воли. Иногда не хватает понятного первого действия, напоминания или человека, который поддержит.',
                  points: [
                    'Здесь вас не будут ругать за пропуски',
                    'Приложение поможет начать, а не только записать цель',
                    'Пропуск не считается провалом',
                  ],
                ),""",
    """                IntroPage(
                  icon: Icons.route_rounded,
                  kicker: 'ВАШ СПОСОБ ДВИГАТЬСЯ К ЦЕЛИ',
                  title: 'У каждого свой способ достигать целей',
                  text:
                      'Кому-то помогает ясный план. Кому-то — короткие действия, совместный старт или человек, который ждёт результата.',
                  points: [
                    'Попробуйте разные способы поддержки',
                    'Определите, что помогает именно вам',
                  ],
                ),""",
)

# Less poster-like onboarding composition.
replace('        height: 210,', '        height: 150,')
replace('            width: 105,', '            width: 78,')
replace('            height: 105,', '            height: 78,')
replace('            child: Icon(icon, size: 52, color: ink),', '            child: Icon(icon, size: 38, color: ink),')
replace('      const SizedBox(height: 28),', '      const SizedBox(height: 20),')
replace('          fontSize: 37,', '          fontSize: 30,')
replace('          height: 1.04,', '          height: 1.12,')
replace('          letterSpacing: -1.3,', '          letterSpacing: -0.7,')

# The goal remains the center of the Today screen.
replace("section('Действие для цели на сегодня')", "section('Что вы сделаете сегодня?')")
replace(
    "'Выберите одно конкретное действие, которое приблизит вас к цели.'",
    "'Выберите одно конкретное действие, которое поможет продвинуться к цели.'",
)
replace(
    "'Для него можно выбрать напоминание, помощь AI, совместный старт, отчёт знакомому или куратора.'",
    "'Достаточно небольшого шага, который реально выполнить сегодня.'",
)
replace("child: const Text('Добавить действие'),", "child: const Text('Выбрать действие'),")

# Do not ask about support until an action exists.
replace(
    """            if (goalAction == null)
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
            GoalSupportPanel(app: app, item: goalAction),""",
    """            if (goalAction == null)
              EmptyAction(
                onTap: () => Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => ActionEditor(app: app, goalDefault: true),
                  ),
                ),
              )
            else ...[
              ActionCard(app: app, item: goalAction, featured: true),
              const SizedBox(height: 13),
              GoalSupportPanel(app: app, item: goalAction),
            ],""",
)
replace(
    """            GoalHero(app: app),
            const SizedBox(height: 13),
            GoalSupportPanel(app: app, item: activeAction),
            const SizedBox(height: 16),""",
    """            GoalHero(app: app),
            if (activeAction != null) ...[
              const SizedBox(height: 13),
              GoalSupportPanel(app: app, item: activeAction),
            ],
            const SizedBox(height: 16),""",
)

# When a support mode was chosen before opening the editor, do not ask again.
replace(
    """  bool showMoreSupport = false;
  bool showSmall = false;
""",
    """  bool showMoreSupport = false;
  bool showSmall = false;

  bool get supportLocked => widget.initialSupport != null;
""",
)
replace(
    """    return Scaffold(
      appBar: AppBar(title: const Text('Действие на сегодня')),""",
    """    final pageTitle = switch (widget.initialSupport) {
      Support.together => 'Начать вместе',
      Support.ai => 'С цифровым помощником',
      Support.report => 'Показать результат',
      Support.curator => 'С куратором',
      _ => 'Действие на сегодня',
    };

    return Scaffold(
      appBar: AppBar(title: Text(pageTitle)),""",
)
replace(
    """          const SizedBox(height: 20),
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
          ],""",
    """          const SizedBox(height: 20),
          if (supportLocked) ...[
            const Text(
              'Выбранный способ',
              style: TextStyle(fontWeight: FontWeight.w900, fontSize: 18),
            ),
            const SizedBox(height: 9),
            SupportTile(type: support, selected: true, onTap: () {}),
          ] else ...[
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
              onPressed: () =>
                  setState(() => showMoreSupport = !showMoreSupport),
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
          ],""",
)

# A real, scrollable help sheet during an active session.
replace(
    "enum ResultState { done, part, moved, missed }",
    "enum ResultState { done, part, moved, missed }\n\nenum BlockerOutcome { continueWork, continueSmall, together, finish }",
)
replace(
    """                    onPressed: () => showModalBottomSheet(
                      context: context,
                      showDragHandle: true,
                      builder: (_) => Blocker(item: widget.item),
                    ),""",
    """                    onPressed: () async {
                      setState(() => paused = true);
                      final outcome =
                          await showModalBottomSheet<BlockerOutcome>(
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
                      if (!mounted) return;
                      switch (outcome) {
                        case BlockerOutcome.continueWork:
                          setState(() => paused = false);
                        case BlockerOutcome.continueSmall:
                          setState(() {
                            if (left > 300) left = 300;
                            paused = false;
                          });
                        case BlockerOutcome.together:
                          widget.app.setSupport(widget.item, Support.together);
                          await shareStartMessage(
                            widget.item.title,
                            widget.item.minutes,
                            Support.together,
                          );
                          if (mounted) setState(() => paused = false);
                        case BlockerOutcome.finish:
                          await showModalBottomSheet(
                            context: context,
                            showDragHandle: true,
                            builder: (_) => Finish(onFinish: finish),
                          );
                        case null:
                          setState(() => paused = false);
                      }
                    },""",
)

start = text.index('class Blocker extends StatelessWidget {')
end = text.index('\nclass Finish extends StatelessWidget {', start)
new_blocker = '''class Blocker extends StatelessWidget {
  const Blocker({
    required this.item,
    required this.scrollController,
    super.key,
  });

  final ActionItem item;
  final ScrollController scrollController;

  @override
  Widget build(BuildContext context) {
    final firstStep = SupportLogic.steps(item.title).first;
    final small = item.small.isNotEmpty
        ? item.small
        : SupportLogic.smallStep(item.title);

    return ListView(
      controller: scrollController,
      padding: const EdgeInsets.fromLTRB(18, 2, 18, 32),
      children: [
        const Text(
          'Что сейчас мешает?',
          style: TextStyle(fontSize: 24, fontWeight: FontWeight.w900),
        ),
        const SizedBox(height: 7),
        const Text(
          'Выберите ближайшую трудность. Приложение предложит конкретное действие, а не общий совет.',
        ),
        const SizedBox(height: 16),
        _BlockerOption(
          title: 'Не понимаю, что делать дальше',
          text: firstStep,
          icon: Icons.route_outlined,
          onTap: () => Navigator.pop(context, BlockerOutcome.continueWork),
        ),
        _BlockerOption(
          title: 'Действие оказалось слишком большим',
          text: 'Сократите его до пяти минут: $small',
          icon: Icons.compress_rounded,
          onTap: () => Navigator.pop(context, BlockerOutcome.continueSmall),
        ),
        _BlockerOption(
          title: 'Постоянно отвлекаюсь',
          text: 'Уберите одно отвлечение и продолжите ещё пять минут.',
          icon: Icons.notifications_off_outlined,
          onTap: () => Navigator.pop(context, BlockerOutcome.continueWork),
        ),
        _BlockerOption(
          title: 'Хочу продолжить вместе с кем-то',
          text: 'Отправьте приглашение и продолжите одновременно с человеком.',
          icon: Icons.people_alt_outlined,
          onTap: () => Navigator.pop(context, BlockerOutcome.together),
        ),
        _BlockerOption(
          title: 'Сегодня лучше остановиться',
          text: 'Запишите, что получилось, чтобы действие не потерялось.',
          icon: Icons.stop_circle_outlined,
          onTap: () => Navigator.pop(context, BlockerOutcome.finish),
        ),
      ],
    );
  }
}

class _BlockerOption extends StatelessWidget {
  const _BlockerOption({
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
  Widget build(BuildContext context) => Card(
    margin: const EdgeInsets.only(bottom: 10),
    child: ListTile(
      contentPadding: const EdgeInsets.all(14),
      leading: Container(
        width: 44,
        height: 44,
        decoration: BoxDecoration(
          color: mint,
          borderRadius: BorderRadius.circular(14),
        ),
        child: Icon(icon, color: ink),
      ),
      title: Text(title, style: const TextStyle(fontWeight: FontWeight.w900)),
      subtitle: Padding(
        padding: const EdgeInsets.only(top: 5),
        child: Text(text),
      ),
      trailing: const Icon(Icons.chevron_right_rounded),
      onTap: onTap,
    ),
  );
}
'''
text = text[:start] + new_blocker + text[end:]

main_path.write_text(text, encoding='utf-8')

pubspec = pubspec_path.read_text(encoding='utf-8')
pubspec = pubspec.replace('version: 0.3.3+7', 'version: 0.3.4+8')
pubspec_path.write_text(pubspec, encoding='utf-8')
