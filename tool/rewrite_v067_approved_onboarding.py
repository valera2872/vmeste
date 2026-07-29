from pathlib import Path
import re

main_path = Path('lib/main.dart')
pubspec_path = Path('pubspec.yaml')
text = main_path.read_text(encoding='utf-8')


def replace_class(source: str, name: str, next_name: str, replacement: str) -> str:
    start = source.index(f'class {name}')
    end = source.index(f'class {next_name}', start)
    return source[:start] + replacement.rstrip() + '\n\n' + source[end:]


# Existing users see the approved composition once; stored goals and tasks remain intact.
text = text.replace(
    'if (onboarded && onboardingVersion < 4) onboarded = false;',
    'if (onboarded && onboardingVersion < 5) onboarded = false;',
    1,
)
text = text.replace('onboardingVersion = 4;', 'onboardingVersion = 5;', 1)


ONBOARDING = r'''class Onboarding extends StatefulWidget {
  const Onboarding({required this.app, this.preview = false, super.key});
  final AppState app;
  final bool preview;

  @override
  State<Onboarding> createState() => _OnboardingState();
}

class _OnboardingState extends State<Onboarding> {
  final pages = PageController();
  int page = 0;

  void close() {
    if (widget.preview) {
      Navigator.pop(context);
    } else {
      widget.app.finish(Age.adult, '');
    }
  }

  void next() {
    pages.nextPage(
      duration: const Duration(milliseconds: 300),
      curve: Curves.easeOutCubic,
    );
  }

  void createGoal() {
    if (widget.preview) {
      Navigator.pop(context);
      return;
    }
    final hasGoal = widget.app.goal != null;
    widget.app.finish(Age.adult, '');
    if (!hasGoal) {
      Navigator.of(context).push(
        MaterialPageRoute(builder: (_) => GoalEditor(app: widget.app)),
      );
    }
  }

  @override
  void dispose() {
    pages.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    backgroundColor: const Color(0xFFFBF9F4),
    body: SafeArea(
      child: Column(
        children: [
          _OnboardingHeader(
            page: page,
            preview: widget.preview,
            onSkip: close,
          ),
          Expanded(
            child: PageView(
              controller: pages,
              onPageChanged: (value) => setState(() => page = value),
              children: const [
                _ProductStoryPage(),
                _SupportStoryPage(),
              ],
            ),
          ),
          _OnboardingPrimaryButton(
            key: ValueKey(
              page == 0 ? 'onboarding-next' : 'onboarding-create-goal',
            ),
            label: page == 0
                ? 'Дальше'
                : widget.preview
                ? 'Закрыть'
                : widget.app.goal == null
                ? 'Создать первую цель'
                : 'Продолжить',
            onPressed: page == 0 ? next : createGoal,
          ),
        ],
      ),
    ),
  );
}

class _OnboardingHeader extends StatelessWidget {
  const _OnboardingHeader({
    required this.page,
    required this.preview,
    required this.onSkip,
  });

  final int page;
  final bool preview;
  final VoidCallback onSkip;

  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.fromLTRB(22, 12, 14, 5),
    child: Column(
      children: [
        Row(
          children: [
            const _OnboardingBrandMark(),
            const SizedBox(width: 11),
            const Expanded(
              child: Text(
                'Вместе к цели',
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(
                  color: ink,
                  fontSize: 17,
                  fontWeight: FontWeight.w700,
                  letterSpacing: -.25,
                ),
              ),
            ),
            TextButton(
              style: TextButton.styleFrom(
                foregroundColor: green,
                minimumSize: Size.zero,
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
                tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                textStyle: const TextStyle(
                  fontSize: 13.5,
                  fontWeight: FontWeight.w600,
                ),
              ),
              onPressed: onSkip,
              child: Text(preview ? 'Закрыть' : 'Пропустить'),
            ),
          ],
        ),
        const SizedBox(height: 12),
        SizedBox(
          width: 132,
          child: Column(
            children: [
              Row(
                children: [
                  _ProgressDot(active: page == 0),
                  Expanded(
                    child: AnimatedContainer(
                      duration: const Duration(milliseconds: 220),
                      height: 2,
                      color: page == 1
                          ? const Color(0xFF73B896)
                          : const Color(0xFFD7DDD8),
                    ),
                  ),
                  _ProgressDot(active: page == 1),
                ],
              ),
              const SizedBox(height: 7),
              AnimatedSwitcher(
                duration: const Duration(milliseconds: 180),
                child: Text(
                  '${page + 1} из 2',
                  key: ValueKey(page),
                  style: const TextStyle(
                    color: Color(0xFF68736F),
                    fontSize: 12.5,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
    ),
  );
}

class _ProgressDot extends StatelessWidget {
  const _ProgressDot({required this.active});
  final bool active;

  @override
  Widget build(BuildContext context) => AnimatedContainer(
    duration: const Duration(milliseconds: 220),
    width: 14,
    height: 14,
    decoration: BoxDecoration(
      color: active ? const Color(0xFF4BA47B) : const Color(0xFFFBF9F4),
      shape: BoxShape.circle,
      border: Border.all(
        color: active ? const Color(0xFF4BA47B) : const Color(0xFFD2D8D4),
        width: 2,
      ),
    ),
  );
}

class _OnboardingPrimaryButton extends StatelessWidget {
  const _OnboardingPrimaryButton({
    required this.label,
    required this.onPressed,
    super.key,
  });

  final String label;
  final VoidCallback onPressed;

  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.fromLTRB(22, 10, 22, 16),
    decoration: const BoxDecoration(
      color: Color(0xFFFBF9F4),
      border: Border(top: BorderSide(color: Color(0xFFEAE7E0))),
    ),
    child: FilledButton(
      style: FilledButton.styleFrom(
        minimumSize: const Size.fromHeight(56),
        backgroundColor: const Color(0xFF4A9F78),
        foregroundColor: Colors.white,
        elevation: 0,
        textStyle: const TextStyle(
          fontSize: 16,
          fontWeight: FontWeight.w700,
          letterSpacing: -.1,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
        ),
      ),
      onPressed: onPressed,
      child: Text(label, maxLines: 1, overflow: TextOverflow.ellipsis),
    ),
  );
}

class _OnboardingBrandMark extends StatelessWidget {
  const _OnboardingBrandMark();

  @override
  Widget build(BuildContext context) => Container(
    width: 38,
    height: 38,
    decoration: BoxDecoration(
      gradient: const LinearGradient(
        colors: [Color(0xFF0F4037), Color(0xFF31745F)],
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
      ),
      borderRadius: BorderRadius.circular(13),
    ),
    child: const Icon(Icons.eco_outlined, color: Colors.white, size: 23),
  );
}

class _ProductStoryPage extends StatelessWidget {
  const _ProductStoryPage();

  @override
  Widget build(BuildContext context) => ListView(
    key: const ValueKey('product-story-page'),
    padding: const EdgeInsets.fromLTRB(24, 18, 24, 28),
    children: const [
      Text(
        'НЕ ПРОСТО СПИСОК ДЕЛ',
        style: TextStyle(
          color: Color(0xFF4A9F78),
          fontSize: 11,
          fontWeight: FontWeight.w700,
          letterSpacing: 1.05,
        ),
      ),
      SizedBox(height: 15),
      Text(
        'Найдите свой способ двигаться к цели',
        key: ValueKey('approved-product-title'),
        style: TextStyle(
          color: ink,
          fontSize: 36,
          height: 1.07,
          fontWeight: FontWeight.w700,
          letterSpacing: -1.15,
        ),
      ),
      SizedBox(height: 18),
      Text(
        '«Вместе к цели» помогает превратить важную цель в конкретные действия, подобрать подходящую поддержку и постепенно понять, какие условия помогают именно вам начинать и доводить дела до результата.',
        style: TextStyle(
          color: Color(0xFF42504C),
          fontSize: 15.2,
          height: 1.5,
        ),
      ),
      SizedBox(height: 25),
      _JourneySteps(),
      SizedBox(height: 25),
      _AttentionCard(),
      SizedBox(height: 18),
      _ResearchNote(),
    ],
  );
}

class _JourneySteps extends StatelessWidget {
  const _JourneySteps();

  @override
  Widget build(BuildContext context) => Container(
    key: const ValueKey('onboarding-journey-hero'),
    child: Row(
      key: const ValueKey('journey-visual'),
      crossAxisAlignment: CrossAxisAlignment.start,
      children: const [
        Expanded(
          child: _JourneyStep(
            number: '01',
            icon: Icons.flag_rounded,
            label: 'Цель',
            tint: Color(0xFFE8F2ED),
          ),
        ),
        _DottedConnector(),
        Expanded(
          child: _JourneyStep(
            number: '02',
            icon: Icons.checklist_rounded,
            label: 'Следующий\nшаг',
            tint: Color(0xFFFFF2D7),
          ),
        ),
        _DottedConnector(),
        Expanded(
          child: _JourneyStep(
            number: '03',
            icon: Icons.favorite_rounded,
            label: 'Поддержка',
            tint: Color(0xFFE7F1ED),
          ),
        ),
      ],
    ),
  );
}

class _JourneyStep extends StatelessWidget {
  const _JourneyStep({
    required this.number,
    required this.icon,
    required this.label,
    required this.tint,
  });

  final String number;
  final IconData icon;
  final String label;
  final Color tint;

  @override
  Widget build(BuildContext context) => Column(
    children: [
      Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        decoration: BoxDecoration(
          color: const Color(0xFF4A9F78),
          borderRadius: BorderRadius.circular(20),
        ),
        child: Text(
          number,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 10.5,
            fontWeight: FontWeight.w700,
          ),
        ),
      ),
      const SizedBox(height: 7),
      Container(
        width: 68,
        height: 68,
        decoration: BoxDecoration(color: tint, shape: BoxShape.circle),
        child: Icon(icon, color: green, size: 31),
      ),
      const SizedBox(height: 9),
      Text(
        label,
        textAlign: TextAlign.center,
        style: const TextStyle(
          color: ink,
          fontSize: 12.4,
          height: 1.15,
          fontWeight: FontWeight.w700,
        ),
      ),
    ],
  );
}

class _DottedConnector extends StatelessWidget {
  const _DottedConnector();

  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.only(top: 57),
    child: SizedBox(
      width: 20,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: List.generate(
          3,
          (_) => Container(
            width: 3,
            height: 3,
            decoration: const BoxDecoration(
              color: Color(0xFF64AF8A),
              shape: BoxShape.circle,
            ),
          ),
        ),
      ),
    ),
  );
}

class _AttentionCard extends StatelessWidget {
  const _AttentionCard();

  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.fromLTRB(16, 17, 17, 17),
    decoration: BoxDecoration(
      color: const Color(0xFFEAF4EF),
      borderRadius: BorderRadius.circular(24),
    ),
    child: Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: 48,
          height: 48,
          decoration: const BoxDecoration(
            color: Color(0xFFD7EBE1),
            shape: BoxShape.circle,
          ),
          child: const Icon(
            Icons.inventory_2_outlined,
            color: green,
            size: 24,
          ),
        ),
        const SizedBox(width: 13),
        const Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Освободите внимание',
                style: TextStyle(
                  color: ink,
                  fontSize: 15,
                  fontWeight: FontWeight.w700,
                ),
              ),
              SizedBox(height: 5),
              Text(
                'А остальные дела можно быстро записать, запланировать или сохранить как регулярную практику — чтобы не держать всё в голове.',
                style: TextStyle(
                  color: Color(0xFF4E5D58),
                  fontSize: 12.8,
                  height: 1.42,
                ),
              ),
            ],
          ),
        ),
      ],
    ),
  );
}

class _ResearchNote extends StatelessWidget {
  const _ResearchNote();

  @override
  Widget build(BuildContext context) => Row(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Container(
        width: 34,
        height: 34,
        decoration: const BoxDecoration(
          color: Color(0xFFF0F0EA),
          shape: BoxShape.circle,
        ),
        child: const Icon(Icons.science_outlined, color: green, size: 19),
      ),
      const SizedBox(width: 10),
      const Expanded(
        child: Text(
          'С опорой на исследования о планировании действий, формировании привычек, обратной связи и социальной поддержке.',
          style: TextStyle(
            color: Color(0xFF68736F),
            fontSize: 11.8,
            height: 1.4,
          ),
        ),
      ),
    ],
  );
}

class _SupportStoryPage extends StatelessWidget {
  const _SupportStoryPage();

  @override
  Widget build(BuildContext context) => ListView(
    key: const ValueKey('support-story-page'),
    padding: const EdgeInsets.fromLTRB(22, 18, 22, 28),
    children: const [
      Text(
        'НЕ ВСЕМ ПОМОГАЕТ ОДИН И ТОТ ЖЕ СПОСОБ',
        style: TextStyle(
          color: Color(0xFF4A9F78),
          fontSize: 10.6,
          fontWeight: FontWeight.w700,
          letterSpacing: .95,
        ),
      ),
      SizedBox(height: 13),
      Text(
        'Подберите поддержку под конкретное действие',
        key: ValueKey('approved-support-title'),
        style: TextStyle(
          color: ink,
          fontSize: 31,
          height: 1.08,
          fontWeight: FontWeight.w700,
          letterSpacing: -.8,
        ),
      ),
      SizedBox(height: 13),
      Text(
        'Одно дело легче начать самостоятельно. Для другого может понадобиться цифровой помощник, совместное присутствие или человек, перед которым вы договорились отчитаться.',
        style: TextStyle(
          color: Color(0xFF465550),
          fontSize: 14.4,
          height: 1.46,
        ),
      ),
      SizedBox(height: 23),
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
}

class _SupportChoiceGrid extends StatelessWidget {
  const _SupportChoiceGrid();

  @override
  Widget build(BuildContext context) => Container(
    key: const ValueKey('support-orbit'),
    child: Column(
      key: const ValueKey('support-choice-grid'),
      children: [
        IntrinsicHeight(
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: const [
              Expanded(
                child: _OnboardingSupportCard(
                  icon: Icons.person_outline_rounded,
                  title: 'Самостоятельно',
                  text: 'Двигайтесь в своём темпе и так, как удобно вам.',
                  background: Color(0xFFEAF4EF),
                  iconColor: Color(0xFF55A27D),
                ),
              ),
              SizedBox(width: 12),
              Expanded(
                child: _OnboardingSupportCard(
                  icon: Icons.auto_awesome_outlined,
                  title: 'С цифровым помощником',
                  text: 'Получайте подсказки, разбирайте шаги и находите решение.',
                  background: Color(0xFFFFF4DF),
                  iconColor: Color(0xFFDAA64C),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 13),
        const _ActionCenterCard(),
        const SizedBox(height: 13),
        IntrinsicHeight(
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: const [
              Expanded(
                child: _OnboardingSupportCard(
                  icon: Icons.people_alt_outlined,
                  title: 'Вместе с человеком',
                  text:
                      'Начинайте одновременно или оставайтесь на аудио- или видеосвязи.',
                  background: Color(0xFFF0ECF7),
                  iconColor: Color(0xFF7465A9),
                ),
              ),
              SizedBox(width: 12),
              Expanded(
                child: _OnboardingSupportCard(
                  icon: Icons.fact_check_outlined,
                  title: 'С отчётом или куратором',
                  text:
                      'Делитесь результатом и получайте обратную связь или поддержку.',
                  background: Color(0xFFEAF2F7),
                  iconColor: Color(0xFF39789A),
                ),
              ),
            ],
          ),
        ),
      ],
    ),
  );
}

class _ActionCenterCard extends StatelessWidget {
  const _ActionCenterCard();

  @override
  Widget build(BuildContext context) => Container(
    width: 190,
    padding: const EdgeInsets.fromLTRB(15, 14, 15, 15),
    decoration: BoxDecoration(
      color: Colors.white,
      borderRadius: BorderRadius.circular(24),
      border: Border.all(color: const Color(0xFFE5EAE6)),
      boxShadow: const [
        BoxShadow(
          color: Color(0x121B4A3E),
          blurRadius: 18,
          offset: Offset(0, 8),
        ),
      ],
    ),
    child: const Column(
      children: [
        CircleAvatar(
          radius: 21,
          backgroundColor: Color(0xFF63B28C),
          child: Icon(Icons.check_rounded, color: Colors.white, size: 24),
        ),
        SizedBox(height: 9),
        Text(
          'ВАШЕ ДЕЙСТВИЕ',
          textAlign: TextAlign.center,
          style: TextStyle(
            color: green,
            fontSize: 10.8,
            fontWeight: FontWeight.w700,
            letterSpacing: .65,
          ),
        ),
        SizedBox(height: 4),
        Text(
          'Конкретный шаг к вашей цели',
          textAlign: TextAlign.center,
          style: TextStyle(
            color: Color(0xFF45534F),
            fontSize: 12.2,
            height: 1.32,
          ),
        ),
      ],
    ),
  );
}

class _OnboardingSupportCard extends StatelessWidget {
  const _OnboardingSupportCard({
    required this.icon,
    required this.title,
    required this.text,
    required this.background,
    required this.iconColor,
  });

  final IconData icon;
  final String title;
  final String text;
  final Color background;
  final Color iconColor;

  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.fromLTRB(13, 14, 13, 15),
    decoration: BoxDecoration(
      color: background,
      borderRadius: BorderRadius.circular(23),
    ),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: 43,
          height: 43,
          decoration: BoxDecoration(
            color: Colors.white.withValues(alpha: .72),
            shape: BoxShape.circle,
          ),
          child: Icon(icon, color: iconColor, size: 23),
        ),
        const SizedBox(height: 12),
        Text(
          title,
          style: const TextStyle(
            color: ink,
            fontSize: 13.2,
            height: 1.18,
            fontWeight: FontWeight.w700,
          ),
        ),
        const SizedBox(height: 7),
        Text(
          text,
          style: const TextStyle(
            color: Color(0xFF53615D),
            fontSize: 11.5,
            height: 1.38,
          ),
        ),
      ],
    ),
  );
}

class _QuietStatement extends StatelessWidget {
  const _QuietStatement({required this.icon, required this.text});
  final IconData icon;
  final String text;

  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.fromLTRB(15, 14, 15, 14),
    decoration: BoxDecoration(
      color: const Color(0xFFF0F5ED),
      borderRadius: BorderRadius.circular(22),
    ),
    child: Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: 37,
          height: 37,
          decoration: const BoxDecoration(
            color: Colors.white,
            shape: BoxShape.circle,
          ),
          child: Icon(icon, color: green, size: 20),
        ),
        const SizedBox(width: 11),
        Expanded(
          child: Text(
            text,
            style: const TextStyle(
              color: Color(0xFF46544F),
              fontSize: 12.5,
              height: 1.42,
            ),
          ),
        ),
      ],
    ),
  );
}'''

text = replace_class(
    text,
    'Onboarding extends StatefulWidget',
    'HowItWorksPage extends StatelessWidget',
    ONBOARDING,
)

main_path.write_text(text, encoding='utf-8')

pubspec = pubspec_path.read_text(encoding='utf-8')
pubspec = re.sub(r'^version:\s*[^\n]+', 'version: 0.6.7+20', pubspec, count=1, flags=re.M)
pubspec_path.write_text(pubspec, encoding='utf-8')
print('Applied approved v0.6.7 onboarding composition')
