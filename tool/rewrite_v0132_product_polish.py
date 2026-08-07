from pathlib import Path
import re

main_path = Path('lib/main.dart')
pubspec_path = Path('pubspec.yaml')
text = main_path.read_text(encoding='utf-8')
pubspec = pubspec_path.read_text(encoding='utf-8')

if 'version: 0.13.2+31' in pubspec:
    print('v0.13.2 product polish already applied')
    raise SystemExit(0)


def replace_class(source: str, name: str, next_name: str, replacement: str) -> str:
    start = source.index(f'class {name}')
    end = source.index(f'class {next_name}', start)
    return source[:start] + replacement.rstrip() + '\n\n' + source[end:]


def replace_once(old: str, new: str, label: str) -> None:
    global text
    if old not in text:
        raise SystemExit(f'{label} anchor not found')
    text = text.replace(old, new, 1)


# Existing users see the conceptually updated introduction once. Stored goals,
# challenges, tasks, practices and history remain intact.
replace_once(
    'if (onboarded && onboardingVersion < 6) onboarded = false;',
    'if (onboarded && onboardingVersion < 7) onboarded = false;',
    'onboarding migration 7',
)
replace_once(
    '    onboardingVersion = 6;\n    startChoiceSeen = false;',
    '    onboardingVersion = 7;\n    startChoiceSeen = false;',
    'onboarding completion 7',
)


PRODUCT = r'''class _ProductStoryPage extends StatelessWidget {
  const _ProductStoryPage();

  @override
  Widget build(BuildContext context) => ListView(
    key: const ValueKey('product-story-page'),
    padding: const EdgeInsets.fromLTRB(22, 15, 22, 28),
    children: const [
      Text(
        'ОДНО ПРИЛОЖЕНИЕ — НЕСКОЛЬКО НАПРАВЛЕНИЙ',
        style: TextStyle(
          color: Color(0xFF4A9F78),
          fontSize: 10.2,
          fontWeight: FontWeight.w800,
          letterSpacing: .88,
        ),
      ),
      SizedBox(height: 11),
      Text(
        'Важное бывает разным',
        key: ValueKey('approved-product-title'),
        style: TextStyle(
          color: ink,
          fontSize: 27,
          height: 1.12,
          fontWeight: FontWeight.w800,
          letterSpacing: -.55,
        ),
      ),
      SizedBox(height: 14),
      _IntroLead(
        key: ValueKey('product-intro-lead'),
        text:
            'Большая цель, челлендж, регулярная практика или обычное дело — всё это может быть важно одновременно.',
      ),
      SizedBox(height: 21),
      _IntroAreasPanel(),
      SizedBox(height: 17),
      _IntroQuietNote(
        icon: Icons.layers_outlined,
        text: 'Не нужно выбирать что-то одно. Добавляйте то, что актуально сейчас.',
      ),
    ],
  );
}

class _IntroLead extends StatelessWidget {
  const _IntroLead({required this.text, super.key});
  final String text;

  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.fromLTRB(14, 2, 0, 2),
    decoration: const BoxDecoration(
      border: Border(
        left: BorderSide(color: Color(0xFF72B493), width: 3),
      ),
    ),
    child: Text(
      text,
      style: const TextStyle(
        color: Color(0xFF46544F),
        fontSize: 14.2,
        height: 1.43,
      ),
    ),
  );
}

class _IntroAreasPanel extends StatelessWidget {
  const _IntroAreasPanel();

  @override
  Widget build(BuildContext context) => LayoutBuilder(
    builder: (context, constraints) {
      final width = (constraints.maxWidth - 10) / 2;
      return Wrap(
        spacing: 10,
        runSpacing: 10,
        children: const [
          _IntroAreaCard(
            key: ValueKey('intro-area-goal'),
            widthFactor: 0,
            icon: Icons.flag_outlined,
            title: 'Важная цель',
            text: 'Двигаться к значимому результату шаг за шагом.',
          ),
          _IntroAreaCard(
            key: ValueKey('intro-area-challenge'),
            widthFactor: 0,
            icon: Icons.emoji_events_outlined,
            title: 'Челлендж',
            text: 'Выполнять конкретное обещание выбранный срок.',
            warm: true,
          ),
          _IntroAreaCard(
            key: ValueKey('intro-area-tasks'),
            widthFactor: 0,
            icon: Icons.checklist_rounded,
            title: 'Дела и задачи',
            text: 'Разобрать накопившееся и выбрать главное сейчас.',
          ),
          _IntroAreaCard(
            key: ValueKey('intro-area-routines'),
            widthFactor: 0,
            icon: Icons.repeat_rounded,
            title: 'Регулярные практики',
            text: 'Поддерживать действия, которые важно повторять.',
          ),
        ].map((card) => SizedBox(width: width, child: card)).toList(),
      );
    },
  );
}

class _IntroAreaCard extends StatelessWidget {
  const _IntroAreaCard({
    required this.icon,
    required this.title,
    required this.text,
    required this.widthFactor,
    this.warm = false,
    super.key,
  });

  final IconData icon;
  final String title;
  final String text;
  final double widthFactor;
  final bool warm;

  @override
  Widget build(BuildContext context) => Container(
    constraints: const BoxConstraints(minHeight: 138),
    padding: const EdgeInsets.fromLTRB(12, 12, 11, 12),
    decoration: BoxDecoration(
      color: warm ? const Color(0xFFFFF6DF) : Colors.white,
      borderRadius: BorderRadius.circular(19),
      border: Border.all(
        color: warm ? const Color(0xFFE6D5A9) : const Color(0xFFDEE4E0),
      ),
    ),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: 37,
          height: 37,
          decoration: BoxDecoration(
            color: warm
                ? const Color(0xFFFFE9B9)
                : const Color(0xFFEAF3EF),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Icon(
            icon,
            color: warm ? const Color(0xFF876722) : green,
            size: 20,
          ),
        ),
        const SizedBox(height: 9),
        Text(
          title,
          maxLines: 2,
          softWrap: true,
          overflow: TextOverflow.visible,
          style: const TextStyle(
            color: ink,
            fontSize: 13.2,
            height: 1.15,
            fontWeight: FontWeight.w800,
          ),
        ),
        const SizedBox(height: 5),
        Text(
          text,
          style: const TextStyle(
            color: Color(0xFF66726E),
            fontSize: 11.2,
            height: 1.34,
          ),
        ),
      ],
    ),
  );
}

class _IntroQuietNote extends StatelessWidget {
  const _IntroQuietNote({required this.icon, required this.text});
  final IconData icon;
  final String text;

  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.fromLTRB(13, 12, 13, 12),
    decoration: BoxDecoration(
      color: const Color(0xFFEAF3EF),
      borderRadius: BorderRadius.circular(17),
    ),
    child: Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, color: green, size: 20),
        const SizedBox(width: 9),
        Expanded(
          child: Text(
            text,
            style: const TextStyle(
              color: ink,
              fontSize: 12.8,
              height: 1.38,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
      ],
    ),
  );
}'''


SUPPORT = r'''class _SupportStoryPage extends StatelessWidget {
  const _SupportStoryPage();

  @override
  Widget build(BuildContext context) => ListView(
    key: const ValueKey('support-story-page'),
    padding: const EdgeInsets.fromLTRB(22, 15, 22, 28),
    children: const [
      Text(
        'НЕ ТОЛЬКО ПЛАНИРОВАТЬ',
        style: TextStyle(
          color: Color(0xFF4A9F78),
          fontSize: 10.4,
          fontWeight: FontWeight.w800,
          letterSpacing: .92,
        ),
      ),
      SizedBox(height: 11),
      Text(
        'Помогаем перейти\nк действию',
        key: ValueKey('approved-support-title'),
        style: TextStyle(
          color: ink,
          fontSize: 26,
          height: 1.12,
          fontWeight: FontWeight.w800,
          letterSpacing: -.52,
        ),
      ),
      SizedBox(height: 14),
      _IntroLead(
        key: ValueKey('support-intro-lead'),
        text:
            '«Вместе к цели» помогает увидеть ближайшее действие, сделать его посильным и получить поддержку, когда трудно начать или продолжить.',
      ),
      SizedBox(height: 20),
      _ActionBridgeCard(
        key: ValueKey('intro-action-step'),
        number: '01',
        icon: Icons.route_outlined,
        title: 'Ближайший шаг',
        text: 'Не весь путь сразу, а конкретное действие, которое можно сделать сейчас.',
      ),
      SizedBox(height: 9),
      _ActionBridgeCard(
        key: ValueKey('intro-action-feasible'),
        number: '02',
        icon: Icons.compress_rounded,
        title: 'Посильный вариант',
        text: 'Полный шаг, малый объём или сохранение контакта в сложный день.',
      ),
      SizedBox(height: 9),
      _ActionBridgeCard(
        key: ValueKey('intro-action-support'),
        number: '03',
        icon: Icons.people_alt_outlined,
        title: 'Поддержка',
        text: 'Самостоятельно или вместе с человеком — только когда это действительно помогает.',
      ),
      SizedBox(height: 18),
      _IntroFlowLine(),
    ],
  );
}

class _ActionBridgeCard extends StatelessWidget {
  const _ActionBridgeCard({
    required this.number,
    required this.icon,
    required this.title,
    required this.text,
    super.key,
  });

  final String number;
  final IconData icon;
  final String title;
  final String text;

  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.fromLTRB(13, 12, 13, 12),
    decoration: BoxDecoration(
      color: Colors.white,
      borderRadius: BorderRadius.circular(18),
      border: Border.all(color: const Color(0xFFDFE4E0)),
    ),
    child: Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: 41,
          height: 41,
          decoration: BoxDecoration(
            color: const Color(0xFFEAF3EF),
            borderRadius: BorderRadius.circular(13),
          ),
          child: Icon(icon, color: green, size: 21),
        ),
        const SizedBox(width: 11),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                '$number · $title',
                style: const TextStyle(
                  color: ink,
                  fontSize: 14.2,
                  height: 1.2,
                  fontWeight: FontWeight.w800,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                text,
                style: const TextStyle(
                  color: Color(0xFF63706B),
                  fontSize: 12.2,
                  height: 1.36,
                ),
              ),
            ],
          ),
        ),
      ],
    ),
  );
}

class _IntroFlowLine extends StatelessWidget {
  const _IntroFlowLine();

  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.fromLTRB(13, 12, 13, 12),
    decoration: BoxDecoration(
      color: ink,
      borderRadius: BorderRadius.circular(18),
    ),
    child: const Text(
      'Намерение  →  действие  →  поддержка  →  продвижение',
      textAlign: TextAlign.center,
      style: TextStyle(
        color: Colors.white,
        fontSize: 12.2,
        height: 1.35,
        fontWeight: FontWeight.w700,
      ),
    ),
  );
}'''

text = replace_class(
    text,
    '_ProductStoryPage extends StatelessWidget',
    '_JourneySteps extends StatelessWidget',
    PRODUCT,
)
text = replace_class(
    text,
    '_SupportStoryPage extends StatelessWidget',
    '_SupportChoiceGrid extends StatelessWidget',
    SUPPORT,
)


# Temporarily hide the deterministic digital assistant. The implementation is
# retained in source for a later, separately designed AI experiment.
assistant_editor = r'''          if (support == Support.ai) ...[
            const SizedBox(height: 12),
            _DigitalActionAssistantCard(
              title: title.text,
              currentMinimum: small.text,
              onUseFirstStep: (value) {
                title.text = value;
                title.selection = TextSelection.collapsed(offset: value.length);
                setState(() {});
              },
              onUseMinimum: (value) {
                small.text = value;
                small.selection = TextSelection.collapsed(offset: value.length);
                setState(() => showSmall = true);
              },
            ),
            const SizedBox(height: 8),
          ],
'''
if assistant_editor not in text:
    raise SystemExit('digital assistant editor block not found')
text = text.replace(assistant_editor, '', 1)

assistant_goal_entry = r'''          if (item.support == Support.ai) ...[
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                key: const ValueKey('open-digital-assistant'),
                style: OutlinedButton.styleFrom(
                  foregroundColor: mint,
                  side: const BorderSide(color: Color(0x66D4FFF2)),
                ),
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
                icon: const Icon(Icons.auto_awesome_outlined),
                label: const Text('Разобрать действие с помощником'),
              ),
            ),
            const SizedBox(height: 8),
          ],
'''
if assistant_goal_entry not in text:
    raise SystemExit('digital assistant goal entry not found')
text = text.replace(assistant_goal_entry, '', 1)

support_button = r'''          _SupportButton(
            icon: Icons.auto_awesome_rounded,
            label: 'С цифровым помощником',
            onPressed: () => _open(context, Support.ai),
          ),
          const SizedBox(height: 8),
'''
if support_button in text:
    text = text.replace(support_button, '', 1)

# Any support picker generated from all enum values must not expose the hidden
# assistant. Historical Support.ai values remain readable but are presented as
# solo support until the future AI module is deliberately restored.
text = re.sub(
    r'Support\.values\s*\.map\(',
    'Support.values.where((value) => value != Support.ai).map(',
    text,
)
text = text.replace(
    'widget.app.setSupport(widget.item, Support.ai);',
    'widget.app.setSupport(widget.item, Support.solo);',
)
text = text.replace(
    "Support.ai => 'Цифровой помощник'",
    "Support.ai => 'Самостоятельно'",
)
text = text.replace(
    'orElse: () => Support.ai,',
    'orElse: () => Support.solo,',
)

start_plan_start = text.find('class StartPlan {')
if start_plan_start >= 0:
    next_class = text.find('\nclass ', start_plan_start + 12)
    if next_class < 0:
        next_class = len(text)
    block = text[start_plan_start:next_class]
    block = block.replace('support: Support.ai,', 'support: Support.solo,')
    text = text[:start_plan_start] + block + text[next_class:]


# Rebuild the compact 2 × 2 overview so fixed navigation titles wrap instead
# of being shortened with an ellipsis on narrow phones and larger font scales.
TODAY_TILE = r'''class _TodayAreaTile extends StatelessWidget {
  const _TodayAreaTile({
    required this.icon,
    required this.title,
    required this.status,
    required this.onTap,
    this.warm = false,
    super.key,
  });

  final IconData icon;
  final String title;
  final String status;
  final VoidCallback onTap;
  final bool warm;

  @override
  Widget build(BuildContext context) => Material(
    color: warm ? const Color(0xFFFFF7E3) : Colors.white,
    clipBehavior: Clip.antiAlias,
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(18),
      side: BorderSide(
        color: warm
            ? const Color(0xFFE8D8AE)
            : const Color(0xFFDFE4E0),
      ),
    ),
    child: InkWell(
      onTap: onTap,
      child: ConstrainedBox(
        constraints: const BoxConstraints(minHeight: 102),
        child: Padding(
          padding: const EdgeInsets.fromLTRB(11, 10, 11, 10),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 34,
                height: 34,
                decoration: BoxDecoration(
                  color: warm
                      ? const Color(0xFFFFEBC1)
                      : const Color(0xFFEAF3EF),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(
                  icon,
                  color: warm ? const Color(0xFF866623) : green,
                  size: 19,
                ),
              ),
              const SizedBox(height: 7),
              Text(
                title,
                maxLines: 2,
                softWrap: true,
                overflow: TextOverflow.visible,
                style: const TextStyle(
                  color: ink,
                  fontSize: 13,
                  height: 1.12,
                  fontWeight: FontWeight.w800,
                ),
              ),
              const SizedBox(height: 3),
              Text(
                status,
                maxLines: 2,
                softWrap: true,
                overflow: TextOverflow.visible,
                style: TextStyle(
                  color: warm
                      ? const Color(0xFF806321)
                      : const Color(0xFF64716C),
                  fontSize: 11.2,
                  height: 1.16,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        ),
      ),
    ),
  );
}'''
text = replace_class(
    text,
    '_TodayAreaTile extends StatelessWidget',
    '_TodayGoalArea',
    TODAY_TILE,
)

session_support_old = r'''                    Expanded(
                      child: Text(
                        supportName(widget.item.support).toUpperCase(),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                          color: mint,
                          fontSize: 11.5,
                          fontWeight: FontWeight.w900,
                          letterSpacing: .8,
                        ),
                      ),
                    ),'''
session_support_new = r'''                    Expanded(
                      child: Text(
                        supportName(widget.item.support).toUpperCase(),
                        maxLines: 2,
                        softWrap: true,
                        overflow: TextOverflow.visible,
                        style: const TextStyle(
                          color: mint,
                          fontSize: 11.2,
                          height: 1.16,
                          fontWeight: FontWeight.w900,
                          letterSpacing: .55,
                        ),
                      ),
                    ),'''
if session_support_old in text:
    text = text.replace(session_support_old, session_support_new, 1)


# Sanity checks: no visible entry point to the postponed assistant remains.
for forbidden in [
    "key: const ValueKey('open-digital-assistant')",
    "label: 'С цифровым помощником'",
]:
    if forbidden in text:
        raise SystemExit(f'hidden assistant entry remains: {forbidden}')

if 'version: 0.13.1+30' not in pubspec:
    raise SystemExit('Expected v0.13.1 version not found')
pubspec = pubspec.replace('version: 0.13.1+30', 'version: 0.13.2+31', 1)

main_path.write_text(text, encoding='utf-8')
pubspec_path.write_text(pubspec, encoding='utf-8')
print('Applied v0.13.2 concept introduction, full labels and hidden assistant')
