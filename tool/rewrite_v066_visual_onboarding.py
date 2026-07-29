from pathlib import Path
import re

main_path = Path('lib/main.dart')
pubspec_path = Path('pubspec.yaml')
text = main_path.read_text(encoding='utf-8')


def replace_class(source: str, name: str, next_name: str, replacement: str) -> str:
    start = source.index(f'class {name}')
    end = source.index(f'class {next_name}', start)
    return source[:start] + replacement.rstrip() + '\n\n' + source[end:]


# Existing users see the rebuilt visual introduction once while all stored data remains intact.
text = text.replace(
    'if (onboarded && onboardingVersion < 3) onboarded = false;',
    'if (onboarded && onboardingVersion < 4) onboarded = false;',
    1,
)
text = text.replace('onboardingVersion = 3;', 'onboardingVersion = 4;', 1)


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
      duration: const Duration(milliseconds: 320),
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
    backgroundColor: const Color(0xFFF7F5EE),
    body: SafeArea(
      child: Column(
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 13, 12, 4),
            child: Row(
              children: [
                const _OnboardingBrandMark(),
                const SizedBox(width: 10),
                const Text(
                  'Вместе к цели',
                  style: TextStyle(
                    color: ink,
                    fontSize: 15.5,
                    fontWeight: FontWeight.w700,
                    letterSpacing: -.15,
                  ),
                ),
                const Spacer(),
                AnimatedSwitcher(
                  duration: const Duration(milliseconds: 180),
                  child: Text(
                    page == 0 ? '01 / 02' : '02 / 02',
                    key: ValueKey(page),
                    style: const TextStyle(
                      color: Color(0xFF78837F),
                      fontSize: 11.5,
                      fontWeight: FontWeight.w600,
                      letterSpacing: .5,
                    ),
                  ),
                ),
                const SizedBox(width: 5),
                TextButton(
                  onPressed: close,
                  child: Text(widget.preview ? 'Закрыть' : 'Пропустить'),
                ),
              ],
            ),
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
          Container(
            decoration: const BoxDecoration(
              color: Color(0xFFF7F5EE),
              border: Border(
                top: BorderSide(color: Color(0xFFE6E2D8)),
              ),
            ),
            padding: const EdgeInsets.fromLTRB(20, 11, 20, 16),
            child: Column(
              children: [
                Row(
                  children: List.generate(
                    2,
                    (index) => Expanded(
                      child: AnimatedContainer(
                        duration: const Duration(milliseconds: 220),
                        height: 3,
                        margin: EdgeInsets.only(right: index == 0 ? 5 : 0),
                        decoration: BoxDecoration(
                          color: index <= page
                              ? green
                              : const Color(0xFFD9DDD9),
                          borderRadius: BorderRadius.circular(8),
                        ),
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 11),
                FilledButton(
                  key: ValueKey(
                    page == 0
                        ? 'onboarding-next'
                        : 'onboarding-create-goal',
                  ),
                  style: FilledButton.styleFrom(
                    minimumSize: const Size.fromHeight(54),
                    backgroundColor: ink,
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(18),
                    ),
                  ),
                  onPressed: page == 0 ? next : createGoal,
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        page == 0
                            ? 'Дальше'
                            : widget.preview
                            ? 'Закрыть'
                            : widget.app.goal == null
                            ? 'Создать первую цель'
                            : 'Продолжить',
                      ),
                      const SizedBox(width: 8),
                      const Icon(Icons.arrow_forward_rounded, size: 19),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    ),
  );
}

class _OnboardingBrandMark extends StatelessWidget {
  const _OnboardingBrandMark();

  @override
  Widget build(BuildContext context) => SizedBox(
    width: 27,
    height: 27,
    child: Stack(
      alignment: Alignment.center,
      children: [
        Container(
          width: 27,
          height: 27,
          decoration: BoxDecoration(
            color: ink,
            borderRadius: BorderRadius.circular(9),
          ),
        ),
        Transform.rotate(
          angle: -.48,
          child: Container(
            width: 13,
            height: 3,
            decoration: BoxDecoration(
              color: mint,
              borderRadius: BorderRadius.circular(4),
            ),
          ),
        ),
        Positioned(
          right: 5,
          top: 5,
          child: Container(
            width: 5,
            height: 5,
            decoration: const BoxDecoration(
              color: mint,
              shape: BoxShape.circle,
            ),
          ),
        ),
      ],
    ),
  );
}

class _ProductStoryPage extends StatelessWidget {
  const _ProductStoryPage();

  @override
  Widget build(BuildContext context) => ListView(
    key: const ValueKey('product-story-page'),
    padding: const EdgeInsets.fromLTRB(20, 8, 20, 22),
    children: [
      Container(
        key: const ValueKey('onboarding-journey-hero'),
        height: 286,
        clipBehavior: Clip.antiAlias,
        decoration: BoxDecoration(
          gradient: const LinearGradient(
            colors: [Color(0xFF0E2B27), Color(0xFF285D53)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: BorderRadius.circular(32),
          boxShadow: const [
            BoxShadow(
              color: Color(0x24132D2A),
              blurRadius: 26,
              offset: Offset(0, 14),
            ),
          ],
        ),
        child: Stack(
          children: [
            const Positioned(
              right: -38,
              top: -55,
              child: _SoftCircle(size: 168, opacity: .07),
            ),
            const Positioned(
              left: -52,
              bottom: -82,
              child: _SoftCircle(size: 190, opacity: .055),
            ),
            const Padding(
              padding: EdgeInsets.fromLTRB(22, 20, 22, 0),
              child: Text(
                'НЕ ПРОСТО СПИСОК ДЕЛ',
                style: TextStyle(
                  color: mint,
                  fontSize: 10.5,
                  fontWeight: FontWeight.w700,
                  letterSpacing: 1.15,
                ),
              ),
            ),
            const Positioned(
              left: 12,
              right: 12,
              top: 45,
              child: _JourneyVisual(),
            ),
            const Positioned(
              left: 22,
              right: 22,
              bottom: 23,
              child: Text(
                'Найдите свой способ\nдвигаться к цели',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 27,
                  height: 1.03,
                  fontWeight: FontWeight.w700,
                  letterSpacing: -.65,
                ),
              ),
            ),
          ],
        ),
      ),
      const SizedBox(height: 24),
      const Text(
        '«Вместе к цели» помогает превратить важную цель в конкретные действия, подобрать подходящую поддержку и постепенно понять, какие условия помогают именно вам начинать и доводить дела до результата.',
        style: TextStyle(
          color: Color(0xFF3F4C48),
          fontSize: 14.5,
          height: 1.47,
        ),
      ),
      const SizedBox(height: 20),
      const _EditorialFeature(
        icon: Icons.all_inclusive_rounded,
        title: 'Освободите внимание',
        text:
            'А остальные дела можно быстро записать, запланировать или сохранить как регулярную практику — чтобы не держать всё в голове.',
      ),
      const SizedBox(height: 16),
      const Divider(height: 1, color: Color(0xFFDCDDD7)),
      const SizedBox(height: 13),
      const Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.science_outlined, color: Color(0xFF77817D), size: 18),
          SizedBox(width: 9),
          Expanded(
            child: Text(
              'С опорой на исследования о планировании действий, формировании привычек, обратной связи и социальной поддержке.',
              style: TextStyle(
                color: Color(0xFF69736F),
                fontSize: 11.8,
                height: 1.38,
              ),
            ),
          ),
        ],
      ),
    ],
  );
}

class _JourneyVisual extends StatelessWidget {
  const _JourneyVisual();

  @override
  Widget build(BuildContext context) => SizedBox(
    key: const ValueKey('journey-visual'),
    height: 125,
    child: LayoutBuilder(
      builder: (context, constraints) => Stack(
        children: [
          Positioned.fill(
            child: CustomPaint(painter: _JourneyPainter()),
          ),
          const Positioned(
            left: 4,
            top: 54,
            child: _JourneyNode(
              icon: Icons.flag_outlined,
              label: 'Цель',
              emphasized: true,
            ),
          ),
          Positioned(
            left: constraints.maxWidth * .39,
            top: 12,
            child: const _JourneyNode(
              icon: Icons.arrow_outward_rounded,
              label: 'Следующий шаг',
            ),
          ),
          Positioned(
            right: 2,
            top: 60,
            child: const _JourneyNode(
              icon: Icons.favorite_border_rounded,
              label: 'Поддержка',
              emphasized: true,
            ),
          ),
        ],
      ),
    ),
  );
}

class _JourneyPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final path = Path()
      ..moveTo(48, 81)
      ..cubicTo(
        size.width * .28,
        14,
        size.width * .58,
        15,
        size.width - 48,
        82,
      );
    final shadow = Paint()
      ..color = const Color(0x3313D8AA)
      ..strokeWidth = 8
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;
    final line = Paint()
      ..color = mint.withValues(alpha: .78)
      ..strokeWidth = 2.4
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;
    canvas.drawPath(path, shadow);
    canvas.drawPath(path, line);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

class _JourneyNode extends StatelessWidget {
  const _JourneyNode({
    required this.icon,
    required this.label,
    this.emphasized = false,
  });

  final IconData icon;
  final String label;
  final bool emphasized;

  @override
  Widget build(BuildContext context) => Container(
    constraints: const BoxConstraints(minWidth: 74),
    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
    decoration: BoxDecoration(
      color: emphasized ? mint : Colors.white.withValues(alpha: .12),
      borderRadius: BorderRadius.circular(16),
      border: Border.all(
        color: emphasized
            ? Colors.transparent
            : Colors.white.withValues(alpha: .14),
      ),
    ),
    child: Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(
          icon,
          color: emphasized ? ink : Colors.white,
          size: 16,
        ),
        const SizedBox(width: 6),
        Text(
          label,
          style: TextStyle(
            color: emphasized ? ink : Colors.white,
            fontSize: 11.5,
            fontWeight: FontWeight.w650,
          ),
        ),
      ],
    ),
  );
}

class _EditorialFeature extends StatelessWidget {
  const _EditorialFeature({
    required this.icon,
    required this.title,
    required this.text,
  });

  final IconData icon;
  final String title;
  final String text;

  @override
  Widget build(BuildContext context) => Row(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Container(
        width: 45,
        height: 45,
        decoration: BoxDecoration(
          color: const Color(0xFFE1EEE9),
          borderRadius: BorderRadius.circular(15),
        ),
        child: Icon(icon, color: green, size: 23),
      ),
      const SizedBox(width: 13),
      Expanded(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: const TextStyle(
                color: ink,
                fontSize: 14,
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              text,
              style: const TextStyle(
                color: Color(0xFF55625E),
                fontSize: 12.8,
                height: 1.4,
              ),
            ),
          ],
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
    padding: const EdgeInsets.fromLTRB(20, 8, 20, 24),
    children: const [
      Text(
        'НЕ ВСЕМ ПОМОГАЕТ ОДИН И ТОТ ЖЕ СПОСОБ',
        style: TextStyle(
          color: green,
          fontSize: 10.5,
          fontWeight: FontWeight.w700,
          letterSpacing: .95,
        ),
      ),
      SizedBox(height: 9),
      Text(
        'Подберите поддержку\nпод конкретное действие',
        style: TextStyle(
          color: ink,
          fontSize: 27,
          height: 1.05,
          fontWeight: FontWeight.w700,
          letterSpacing: -.6,
        ),
      ),
      SizedBox(height: 11),
      Text(
        'Одно дело легче начать самостоятельно. Для другого может понадобиться цифровой помощник, совместное присутствие или человек, перед которым вы договорились отчитаться.',
        style: TextStyle(
          color: Color(0xFF4A5753),
          fontSize: 14,
          height: 1.43,
        ),
      ),
      SizedBox(height: 18),
      _SupportOrbitVisual(),
      SizedBox(height: 20),
      _SupportEditorialRow(
        number: '01',
        title: 'Самостоятельно',
        text:
            'Выполнить действие без дополнительной поддержки — с таймером или без него.',
      ),
      _SupportEditorialRow(
        number: '02',
        title: 'С цифровым помощником',
        text:
            'Разобрать слишком большую или непонятную задачу и выбрать выполнимый первый шаг.',
      ),
      _SupportEditorialRow(
        number: '03',
        title: 'Вместе с человеком',
        text:
            'Договориться начать одновременно или оставаться на аудио- или видеосвязи, пока каждый занимается своим делом.',
      ),
      _SupportEditorialRow(
        number: '04',
        title: 'С отчётом или куратором',
        text:
            'Показать результат, попросить напомнить или договориться, что человек поддержит после выполнения или пропуска.',
        last: true,
      ),
      SizedBox(height: 16),
      _QuietStatement(
        icon: Icons.layers_outlined,
        text:
            'Не каждое дело должно становиться большой целью. Обычное напоминание, разовое дело или регулярную практику можно добавить отдельно. Приложение сохранит их рядом, но не смешает с движением к главной цели.',
      ),
      SizedBox(height: 13),
      Text(
        'Приложение будет постепенно замечать, какие способы чаще помогают именно вам.',
        style: TextStyle(
          color: green,
          fontSize: 13,
          height: 1.38,
          fontWeight: FontWeight.w650,
        ),
      ),
    ],
  );
}

class _SupportOrbitVisual extends StatelessWidget {
  const _SupportOrbitVisual();

  @override
  Widget build(BuildContext context) => Container(
    key: const ValueKey('support-orbit'),
    height: 218,
    clipBehavior: Clip.antiAlias,
    decoration: BoxDecoration(
      gradient: const LinearGradient(
        colors: [Color(0xFF173A34), Color(0xFF315F56)],
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
      ),
      borderRadius: BorderRadius.circular(30),
    ),
    child: LayoutBuilder(
      builder: (context, constraints) {
        final width = constraints.maxWidth;
        return Stack(
          children: [
            Positioned.fill(
              child: CustomPaint(painter: _SupportOrbitPainter()),
            ),
            Positioned(
              left: (width - 92) / 2,
              top: 78,
              child: const _OrbitCenter(),
            ),
            const Positioned(
              left: 12,
              top: 18,
              child: _OrbitNode(
                icon: Icons.person_outline_rounded,
                label: 'Самостоятельно',
              ),
            ),
            const Positioned(
              right: 12,
              top: 18,
              child: _OrbitNode(
                icon: Icons.auto_awesome_outlined,
                label: 'Помощник',
              ),
            ),
            const Positioned(
              left: 12,
              bottom: 18,
              child: _OrbitNode(
                icon: Icons.video_call_outlined,
                label: 'Вместе',
              ),
            ),
            const Positioned(
              right: 12,
              bottom: 18,
              child: _OrbitNode(
                icon: Icons.verified_outlined,
                label: 'Отчёт',
              ),
            ),
          ],
        );
      },
    ),
  );
}

class _SupportOrbitPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final points = [
      const Offset(66, 44),
      Offset(size.width - 66, 44),
      Offset(66, size.height - 44),
      Offset(size.width - 66, size.height - 44),
    ];
    final line = Paint()
      ..color = Colors.white.withValues(alpha: .22)
      ..strokeWidth = 1.4
      ..style = PaintingStyle.stroke;
    final glow = Paint()
      ..color = mint.withValues(alpha: .08)
      ..style = PaintingStyle.fill;
    canvas.drawCircle(center, 60, glow);
    for (final point in points) {
      canvas.drawLine(center, point, line);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

class _OrbitCenter extends StatelessWidget {
  const _OrbitCenter();

  @override
  Widget build(BuildContext context) => Container(
    width: 92,
    height: 62,
    alignment: Alignment.center,
    decoration: BoxDecoration(
      color: mint,
      borderRadius: BorderRadius.circular(22),
      boxShadow: const [
        BoxShadow(
          color: Color(0x3313D8AA),
          blurRadius: 20,
          spreadRadius: 2,
        ),
      ],
    ),
    child: const Text(
      'КОНКРЕТНОЕ\nДЕЙСТВИЕ',
      textAlign: TextAlign.center,
      style: TextStyle(
        color: ink,
        fontSize: 10.5,
        height: 1.18,
        fontWeight: FontWeight.w800,
        letterSpacing: .45,
      ),
    ),
  );
}

class _OrbitNode extends StatelessWidget {
  const _OrbitNode({required this.icon, required this.label});
  final IconData icon;
  final String label;

  @override
  Widget build(BuildContext context) => Container(
    constraints: const BoxConstraints(minWidth: 104),
    padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 8),
    decoration: BoxDecoration(
      color: Colors.white.withValues(alpha: .1),
      borderRadius: BorderRadius.circular(16),
      border: Border.all(color: Colors.white.withValues(alpha: .12)),
    ),
    child: Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, color: mint, size: 16),
        const SizedBox(width: 6),
        Text(
          label,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 10.8,
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    ),
  );
}

class _SupportEditorialRow extends StatelessWidget {
  const _SupportEditorialRow({
    required this.number,
    required this.title,
    required this.text,
    this.last = false,
  });

  final String number;
  final String title;
  final String text;
  final bool last;

  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.symmetric(vertical: 13),
    decoration: BoxDecoration(
      border: last
          ? null
          : const Border(
              bottom: BorderSide(color: Color(0xFFDCDDD7)),
            ),
    ),
    child: Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          width: 38,
          child: Text(
            number,
            style: const TextStyle(
              color: Color(0xFF9EAAA5),
              fontSize: 12,
              fontWeight: FontWeight.w700,
              letterSpacing: .55,
            ),
          ),
        ),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: const TextStyle(
                  color: ink,
                  fontSize: 14.2,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                text,
                style: const TextStyle(
                  color: Color(0xFF56635F),
                  fontSize: 12.5,
                  height: 1.38,
                ),
              ),
            ],
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
    padding: const EdgeInsets.fromLTRB(14, 13, 14, 13),
    decoration: BoxDecoration(
      color: const Color(0xFFE7EFEB),
      borderRadius: BorderRadius.circular(18),
    ),
    child: Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, color: green, size: 20),
        const SizedBox(width: 10),
        Expanded(
          child: Text(
            text,
            style: const TextStyle(
              color: Color(0xFF46544F),
              fontSize: 12.4,
              height: 1.4,
            ),
          ),
        ),
      ],
    ),
  );
}

class _SoftCircle extends StatelessWidget {
  const _SoftCircle({required this.size, required this.opacity});
  final double size;
  final double opacity;

  @override
  Widget build(BuildContext context) => Container(
    width: size,
    height: size,
    decoration: BoxDecoration(
      color: Colors.white.withValues(alpha: opacity),
      shape: BoxShape.circle,
    ),
  );
}'''

text = replace_class(
    text,
    'Onboarding extends StatefulWidget',
    'HowItWorksPage extends StatelessWidget',
    ONBOARDING,
)


# Make the parent goal unmistakable on the first-action screen.
action_key = "key: const ValueKey('action-details-step')"
action_start = text.index(action_key)
children_at = text.index('        children: [', action_start)
insert_at = children_at + len('        children: [')
goal_context = r'''
          if (linked && widget.app.goal != null) ...[
            Container(
              key: const ValueKey('action-goal-context'),
              width: double.infinity,
              padding: const EdgeInsets.fromLTRB(13, 12, 13, 12),
              decoration: BoxDecoration(
                color: const Color(0xFFE6EFEB),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    width: 34,
                    height: 34,
                    decoration: BoxDecoration(
                      color: green,
                      borderRadius: BorderRadius.circular(11),
                    ),
                    child: const Icon(
                      Icons.flag_outlined,
                      color: Colors.white,
                      size: 19,
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'ГЛАВНАЯ ЦЕЛЬ',
                          style: TextStyle(
                            color: green,
                            fontSize: 9.8,
                            fontWeight: FontWeight.w750,
                            letterSpacing: .95,
                          ),
                        ),
                        const SizedBox(height: 3),
                        Text(
                          widget.app.goal!.title,
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                          style: const TextStyle(
                            color: ink,
                            fontSize: 14,
                            height: 1.25,
                            fontWeight: FontWeight.w650,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 17),
          ],'''
text = text[:insert_at] + goal_context + text[insert_at:]
text = text.replace(
    "linked ? 'Что вы можете сделать первым?' : 'Что вы хотите сделать?'",
    "linked ? 'Что вы можете сделать в первую очередь?' : 'Что вы хотите сделать?'",
    1,
)
text = text.replace(
    "label: linked ? 'Первое действие' : 'Действие',",
    "label: linked ? 'Первое действие для этой цели' : 'Действие',",
    1,
)

main_path.write_text(text, encoding='utf-8')

pubspec = pubspec_path.read_text(encoding='utf-8')
pubspec = re.sub(r'^version:\s*[^\n]+', 'version: 0.6.6+19', pubspec, count=1, flags=re.M)
pubspec_path.write_text(pubspec, encoding='utf-8')
print('Applied v0.6.6 visual onboarding and explicit goal context')
