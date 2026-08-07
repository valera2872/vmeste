from pathlib import Path
import re

main_path = Path('lib/main.dart')
pubspec_path = Path('pubspec.yaml')
text = main_path.read_text(encoding='utf-8')


def replace_class(source: str, name: str, next_name: str, replacement: str) -> str:
    start = source.index(f'class {name}')
    end = source.index(f'class {next_name}', start)
    return source[:start] + replacement.rstrip() + '\n\n' + source[end:]


# Existing users see the refined introduction once; stored data is untouched.
text = text.replace(
    'if (onboarded && onboardingVersion < 5) onboarded = false;',
    'if (onboarded && onboardingVersion < 6) onboarded = false;',
    1,
)
text = text.replace('onboardingVersion = 5;', 'onboardingVersion = 6;', 1)

PRODUCT = r'''class _ProductStoryPage extends StatelessWidget {
  const _ProductStoryPage();

  @override
  Widget build(BuildContext context) => ListView(
    key: const ValueKey('product-story-page'),
    padding: const EdgeInsets.fromLTRB(24, 16, 24, 28),
    children: const [
      Text(
        'НЕ ПРОСТО СПИСОК ДЕЛ',
        style: TextStyle(
          color: Color(0xFF4A9F78),
          fontSize: 10.6,
          fontWeight: FontWeight.w700,
          letterSpacing: 1.02,
        ),
      ),
      SizedBox(height: 11),
      Text(
        'Найдите свой способ\nдвигаться к цели',
        key: ValueKey('approved-product-title'),
        style: TextStyle(
          color: ink,
          fontSize: 26,
          height: 1.12,
          fontWeight: FontWeight.w700,
          letterSpacing: -.55,
        ),
      ),
      SizedBox(height: 14),
      _IntroLead(
        key: ValueKey('product-intro-lead'),
        text:
            'Превратите важную цель в конкретный следующий шаг — и подберите поддержку, с которой легче начать.',
      ),
      SizedBox(height: 23),
      _JourneySteps(),
      SizedBox(height: 25),
      _AttentionCard(),
      SizedBox(height: 18),
      _ResearchNote(),
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
}'''

SUPPORT = r'''class _SupportStoryPage extends StatelessWidget {
  const _SupportStoryPage();

  @override
  Widget build(BuildContext context) => ListView(
    key: const ValueKey('support-story-page'),
    padding: const EdgeInsets.fromLTRB(22, 16, 22, 28),
    children: const [
      Text(
        'НЕ ВСЕМ ПОМОГАЕТ ОДИН И ТОТ ЖЕ СПОСОБ',
        style: TextStyle(
          color: Color(0xFF4A9F78),
          fontSize: 10.4,
          fontWeight: FontWeight.w700,
          letterSpacing: .9,
        ),
      ),
      SizedBox(height: 11),
      Text(
        'Подберите поддержку\nпод конкретное действие',
        key: ValueKey('approved-support-title'),
        style: TextStyle(
          color: ink,
          fontSize: 25.5,
          height: 1.12,
          fontWeight: FontWeight.w700,
          letterSpacing: -.5,
        ),
      ),
      SizedBox(height: 14),
      _IntroLead(
        key: ValueKey('support-intro-lead'),
        text: 'Разным действиям может требоваться разная поддержка.',
      ),
      SizedBox(height: 21),
      _SupportChoiceGrid(),
      SizedBox(height: 20),
      _QuietStatement(
        icon: Icons.eco_outlined,
        text:
            'Не каждое дело должно становиться большой целью. Обычное напоминание, разовое дело или регулярную практику можно добавить отдельно.',
      ),
      SizedBox(height: 14),
      Text(
        'Приложение будет постепенно замечать, какие способы чаще помогают именно вам.',
        style: TextStyle(
          color: green,
          fontSize: 13,
          height: 1.4,
          fontWeight: FontWeight.w600,
        ),
      ),
    ],
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

main_path.write_text(text, encoding='utf-8')

pubspec = pubspec_path.read_text(encoding='utf-8')
pubspec = re.sub(r'^version:\s*[^\n]+', 'version: 0.6.8+21', pubspec, count=1, flags=re.M)
pubspec_path.write_text(pubspec, encoding='utf-8')
print('Applied compact premium onboarding intros for v0.6.8')
