from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')


def replace_class(source: str, name: str, next_name: str, replacement: str) -> str:
    start = source.index(f'class {name}')
    end = source.index(f'class {next_name}', start)
    return source[:start] + replacement.rstrip() + '\n\n' + source[end:]


CREATE_GOAL = r'''class CreateGoal extends StatelessWidget {
  const CreateGoal({required this.app, super.key});
  final AppState app;

  @override
  Widget build(BuildContext context) => Container(
    key: const ValueKey('focus-empty-card'),
    padding: const EdgeInsets.all(23),
    decoration: BoxDecoration(
      gradient: const LinearGradient(
        colors: [Color(0xFF102E2A), Color(0xFF356A61)],
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
      ),
      borderRadius: BorderRadius.circular(28),
      boxShadow: const [
        BoxShadow(
          color: Color(0x26132D2A),
          blurRadius: 20,
          offset: Offset(0, 10),
        ),
      ],
    ),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Row(
          children: [
            Icon(Icons.flag_outlined, color: mint, size: 19),
            SizedBox(width: 7),
            Text(
              'ГЛАВНЫЙ ФОКУС · 90 ДНЕЙ',
              style: TextStyle(
                color: mint,
                fontSize: 11,
                fontWeight: FontWeight.w900,
                letterSpacing: 1,
              ),
            ),
          ],
        ),
        const SizedBox(height: 11),
        const Text(
          'Что действительно стоит изменить?',
          style: TextStyle(
            color: Colors.white,
            fontSize: 27,
            height: 1.12,
            fontWeight: FontWeight.w900,
          ),
        ),
        const SizedBox(height: 11),
        const Text(
          'Выберите одно направление, которому дадите преимущество в ближайшие 90 дней. Остальные дела и области жизни никуда не исчезают.',
          style: TextStyle(
            color: Color(0xFFD7E2DF),
            fontSize: 15.5,
            height: 1.42,
          ),
        ),
        const SizedBox(height: 18),
        FilledButton.icon(
          key: const ValueKey('focus-start-entry'),
          style: FilledButton.styleFrom(
            backgroundColor: mint,
            foregroundColor: ink,
          ),
          onPressed: () => Navigator.push(
            context,
            MaterialPageRoute(builder: (_) => GoalFocusEntryPage(app: app)),
          ),
          icon: const Icon(Icons.explore_outlined),
          label: const Text('Выбрать главный фокус'),
        ),
      ],
    ),
  );
}'''


FOCUS_FLOW = r'''class GoalFocusEntryPage extends StatelessWidget {
  const GoalFocusEntryPage({required this.app, super.key});
  final AppState app;

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Главный фокус')),
    body: ListView(
      padding: const EdgeInsets.fromLTRB(18, 4, 18, 32),
      children: [
        Text(
          'Что вы хотите изменить за ближайшие 90 дней?',
          style: Theme.of(context).textTheme.headlineMedium,
        ),
        const SizedBox(height: 8),
        const Text(
          'Можно сразу сформулировать результат или сначала разобраться, какая ситуация действительно требует вашего внимания.',
          style: TextStyle(height: 1.42),
        ),
        const SizedBox(height: 20),
        _FocusRouteCard(
          key: const ValueKey('focus-quick-route'),
          icon: Icons.flag_outlined,
          color: const Color(0xFFDCEEE7),
          title: 'Я уже знаю, чего хочу',
          text: 'Короткий путь: результат, личный смысл, зона влияния и первый реальный шаг.',
          badge: '5 вопросов',
          onTap: () => Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => GoalFocusWizard(app: app, guided: false),
            ),
          ),
        ),
        const SizedBox(height: 12),
        _FocusRouteCard(
          key: const ValueKey('focus-guided-route'),
          icon: Icons.psychology_alt_outlined,
          color: const Color(0xFFF2E8D8),
          title: 'Помочь мне разобраться',
          text: 'Глубокий разбор: что беспокоит, что удерживает на месте и что вы готовы изменить.',
          badge: '10 вопросов',
          onTap: () => Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => GoalFocusWizard(app: app, guided: true),
            ),
          ),
        ),
        const SizedBox(height: 17),
        Container(
          padding: const EdgeInsets.all(15),
          decoration: BoxDecoration(
            color: const Color(0xFFF0F5F2),
            borderRadius: BorderRadius.circular(20),
          ),
          child: const Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(Icons.info_outline_rounded, color: green, size: 21),
              SizedBox(width: 10),
              Expanded(
                child: Text(
                  'Это не выбор единственной цели в жизни. Главный фокус лишь защищает одно важное направление от постоянного откладывания и перескакивания.',
                  style: TextStyle(height: 1.4),
                ),
              ),
            ],
          ),
        ),
      ],
    ),
  );
}

class _FocusRouteCard extends StatelessWidget {
  const _FocusRouteCard({
    required this.icon,
    required this.color,
    required this.title,
    required this.text,
    required this.badge,
    required this.onTap,
    super.key,
  });

  final IconData icon;
  final Color color;
  final String title, text, badge;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) => Material(
    color: Colors.transparent,
    child: InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(24),
      child: Ink(
        padding: const EdgeInsets.all(17),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(24),
          border: Border.all(color: const Color(0x18132D2A)),
          boxShadow: const [
            BoxShadow(
              color: Color(0x0D132D2A),
              blurRadius: 14,
              offset: Offset(0, 7),
            ),
          ],
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: 52,
              height: 52,
              decoration: BoxDecoration(
                color: color,
                borderRadius: BorderRadius.circular(17),
              ),
              child: Icon(icon, color: ink, size: 27),
            ),
            const SizedBox(width: 13),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          title,
                          style: const TextStyle(
                            color: ink,
                            fontSize: 17,
                            fontWeight: FontWeight.w900,
                          ),
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 8,
                          vertical: 4,
                        ),
                        decoration: BoxDecoration(
                          color: const Color(0xFFF0F4F2),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Text(
                          badge,
                          style: const TextStyle(
                            color: green,
                            fontSize: 10.5,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  Text(
                    text,
                    style: const TextStyle(
                      color: Color(0xFF5B6964),
                      height: 1.38,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(width: 5),
            const Padding(
              padding: EdgeInsets.only(top: 15),
              child: Icon(Icons.arrow_forward_rounded, color: green),
            ),
          ],
        ),
      ),
    ),
  );
}

class GoalFocusWizard extends StatefulWidget {
  const GoalFocusWizard({
    required this.app,
    required this.guided,
    super.key,
  });

  final AppState app;
  final bool guided;

  @override
  State<GoalFocusWizard> createState() => _GoalFocusWizardState();
}

class _GoalFocusWizardState extends State<GoalFocusWizard> {
  int step = 0;
  int confidence = 7;

  final title = TextEditingController();
  final result = TextEditingController();
  final why = TextEditingController();
  final influence = TextEditingController();
  final firstStep = TextEditingController();
  final situation = TextEditingController();
  final outsideControl = TextEditingController();
  final avoidance = TextEditingController();
  final protection = TextEditingController();
  final cost = TextEditingController();
  final whenWhere = TextEditingController();
  final reducedStep = TextEditingController();

  List<TextEditingController> get _controllers => [
    title,
    result,
    why,
    influence,
    firstStep,
    situation,
    outsideControl,
    avoidance,
    protection,
    cost,
    whenWhere,
    reducedStep,
  ];

  int get total => widget.guided ? 10 : 5;

  String get effectiveFirstStep {
    if (confidence < 7 && reducedStep.text.trim().isNotEmpty) {
      return reducedStep.text.trim();
    }
    return firstStep.text.trim();
  }

  @override
  void initState() {
    super.initState();
    for (final controller in _controllers) {
      controller.addListener(_refresh);
    }
  }

  void _refresh() {
    if (mounted) setState(() {});
  }

  @override
  void dispose() {
    for (final controller in _controllers) {
      controller.removeListener(_refresh);
      controller.dispose();
    }
    super.dispose();
  }

  bool get canContinue {
    if (widget.guided) {
      return switch (step) {
        0 => situation.text.trim().isNotEmpty,
        1 => influence.text.trim().isNotEmpty,
        2 => true,
        3 => true,
        4 => cost.text.trim().isNotEmpty,
        5 => title.text.trim().isNotEmpty && result.text.trim().isNotEmpty,
        6 => why.text.trim().isNotEmpty,
        7 => firstStep.text.trim().isNotEmpty,
        8 => whenWhere.text.trim().isNotEmpty,
        _ => confidence >= 7 || reducedStep.text.trim().isNotEmpty,
      };
    }
    return switch (step) {
      0 => title.text.trim().isNotEmpty && result.text.trim().isNotEmpty,
      1 => why.text.trim().isNotEmpty,
      2 => influence.text.trim().isNotEmpty,
      3 => firstStep.text.trim().isNotEmpty,
      _ => confidence >= 7 || reducedStep.text.trim().isNotEmpty,
    };
  }

  bool get optionalSensitiveStep =>
      widget.guided && (step == 2 || step == 3);

  void previous() {
    FocusScope.of(context).unfocus();
    if (step == 0) {
      Navigator.pop(context);
    } else {
      setState(() => step -= 1);
    }
  }

  void next() {
    if (!canContinue) return;
    FocusScope.of(context).unfocus();
    if (step < total - 1) {
      setState(() => step += 1);
      return;
    }
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(
        builder: (_) => GoalFocusReviewPage(
          app: widget.app,
          guided: widget.guided,
          title: title.text.trim(),
          result: result.text.trim(),
          why: why.text.trim(),
          influence: influence.text.trim(),
          firstStep: effectiveFirstStep,
          confidence: confidence,
          situation: situation.text.trim(),
          outsideControl: outsideControl.text.trim(),
          avoidance: avoidance.text.trim(),
          protection: protection.text.trim(),
          cost: cost.text.trim(),
          whenWhere: whenWhere.text.trim(),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(
      leading: IconButton(
        tooltip: step == 0 ? 'Назад' : 'Предыдущий вопрос',
        onPressed: previous,
        icon: const Icon(Icons.arrow_back_rounded),
      ),
      title: Text(widget.guided ? 'Разобраться в ситуации' : 'Выбрать фокус'),
      bottom: PreferredSize(
        preferredSize: const Size.fromHeight(35),
        child: Padding(
          padding: const EdgeInsets.fromLTRB(18, 0, 18, 11),
          child: Row(
            children: [
              Expanded(
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: LinearProgressIndicator(
                    value: (step + 1) / total,
                    minHeight: 6,
                    backgroundColor: const Color(0xFFE4EBE8),
                    valueColor: const AlwaysStoppedAnimation(green),
                  ),
                ),
              ),
              const SizedBox(width: 10),
              Text(
                '${step + 1} / $total',
                style: const TextStyle(
                  color: green,
                  fontWeight: FontWeight.w900,
                ),
              ),
            ],
          ),
        ),
      ),
    ),
    body: AnimatedSwitcher(
      duration: const Duration(milliseconds: 180),
      child: KeyedSubtree(
        key: ValueKey('focus-question-$step'),
        child: widget.guided ? _guidedPage() : _quickPage(),
      ),
    ),
    bottomNavigationBar: SafeArea(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(18, 8, 18, 14),
        child: FilledButton.icon(
          key: const ValueKey('focus-wizard-next'),
          onPressed: canContinue ? next : null,
          icon: Icon(
            step == total - 1
                ? Icons.fact_check_outlined
                : Icons.arrow_forward_rounded,
          ),
          label: Text(
            step == total - 1
                ? 'Посмотреть фокус'
                : optionalSensitiveStep &&
                      ((step == 2 && avoidance.text.trim().isEmpty) ||
                          (step == 3 && protection.text.trim().isEmpty))
                ? 'Пропустить'
                : 'Продолжить',
          ),
        ),
      ),
    ),
  );

  Widget _quickPage() => switch (step) {
    0 => _question(
      eyebrow: 'РЕЗУЛЬТАТ',
      titleText: 'Что должно измениться за 90 дней?',
      subtitle:
          'Назовите направление коротко, а затем опишите результат, который можно будет увидеть или проверить.',
      children: [
        _field(
          keyName: 'focus-title-field',
          controller: title,
          label: 'Короткое название фокуса',
          hint: 'Например: выпустить приложение',
          lines: 2,
        ),
        const SizedBox(height: 13),
        _field(
          keyName: 'focus-result-field',
          controller: result,
          label: 'Конкретный результат через 90 дней',
          hint: 'Например: рабочая версия опубликована и доступна пользователям',
          lines: 3,
        ),
      ],
    ),
    1 => _question(
      eyebrow: 'ЛИЧНЫЙ СМЫСЛ',
      titleText: 'Почему это важно именно вам?',
      subtitle:
          'Не то, что правильно или произведёт впечатление, а то, ради чего вы действительно готовы действовать.',
      children: [
        _field(
          keyName: 'focus-why-field',
          controller: why,
          label: 'Моя причина',
          hint: 'Что изменится для вас, когда результат будет достигнут?',
          lines: 4,
        ),
      ],
    ),
    2 => _question(
      eyebrow: 'ЗОНА ВЛИЯНИЯ',
      titleText: 'Что здесь зависит от вас?',
      subtitle:
          'Сформулируйте действия и решения, которыми вы можете управлять, даже если итог частично зависит от других.',
      children: [
        _field(
          keyName: 'focus-influence-field',
          controller: influence,
          label: 'Я могу повлиять на…',
          hint: 'Например: закончить версию, показать её людям и собрать обратную связь',
          lines: 4,
        ),
      ],
    ),
    3 => _question(
      eyebrow: 'ПРОВЕРКА ДЕЙСТВИЕМ',
      titleText: 'Какой первый шаг даст реальный факт?',
      subtitle:
          'Лучше отправить, показать, позвонить, попробовать или закончить маленький результат, чем ещё раз долго планировать.',
      children: [
        _field(
          keyName: 'focus-first-step-field',
          controller: firstStep,
          label: 'Первый реальный шаг',
          hint: 'Например: дать прототип трём людям и попросить пройти первый сценарий',
          lines: 4,
        ),
      ],
    ),
    _ => _confidencePage(),
  };

  Widget _guidedPage() => switch (step) {
    0 => _question(
      eyebrow: 'СИТУАЦИЯ',
      titleText: 'Что сейчас больше всего забирает ваши силы или внимание?',
      subtitle:
          'Опишите одну ситуацию. Не нужно сразу придумывать идеальную цель или решение.',
      children: [
        _field(
          keyName: 'focus-situation-field',
          controller: situation,
          label: 'Что происходит?',
          hint: 'Например: важный проект месяцами не двигается с места',
          lines: 5,
        ),
      ],
    ),
    1 => _question(
      eyebrow: 'ГРАНИЦЫ И ВЛИЯНИЕ',
      titleText: 'Что не зависит от вас, а на что вы можете повлиять?',
      subtitle:
          'Сначала отделим внешние обстоятельства от вашей реальной зоны действий — без лишней вины.',
      children: [
        _field(
          keyName: 'focus-outside-field',
          controller: outsideControl,
          label: 'Я не могу напрямую изменить… Необязательно',
          hint: 'Чужое решение, прошлое, внешние ограничения',
          lines: 3,
        ),
        const SizedBox(height: 13),
        _field(
          keyName: 'focus-influence-field',
          controller: influence,
          label: 'Но я могу повлиять на…',
          hint: 'Свои действия, разговор, подготовку, количество попыток',
          lines: 4,
        ),
      ],
    ),
    2 => _question(
      eyebrow: 'ЧЕСТНЫЙ ВЗГЛЯД',
      titleText: 'Какое решение или факт вы, возможно, откладываете?',
      subtitle:
          'Этот вопрос можно пропустить. Иногда ясность появляется позже, уже после первого действия.',
      children: [
        _field(
          keyName: 'focus-avoidance-field',
          controller: avoidance,
          label: 'Возможно, я не хочу замечать или признавать…',
          hint: 'Например: старый способ больше не работает',
          lines: 5,
        ),
      ],
    ),
    3 => _question(
      eyebrow: 'ЗАЩИТНАЯ ФУНКЦИЯ',
      titleText: 'От чего вас защищает сохранение нынешней ситуации?',
      subtitle:
          'Бездействие редко бессмысленно. Оно может защищать от риска, критики, конфликта или слишком большой нагрузки.',
      children: [
        _field(
          keyName: 'focus-protection-field',
          controller: protection,
          label: 'Пока ничего не меняется, мне не приходится…',
          hint: 'Рисковать, выбирать, вступать в конфликт, сталкиваться с оценкой',
          lines: 5,
        ),
      ],
    ),
    4 => _question(
      eyebrow: 'ЦЕНА БЕЗДЕЙСТВИЯ',
      titleText: 'Какую цену вы платите уже сейчас?',
      subtitle:
          'Что станет хуже или останется потерянным, если следующие 90 дней ничего не менять?',
      children: [
        _field(
          keyName: 'focus-cost-field',
          controller: cost,
          label: 'Цена сохранения ситуации',
          hint: 'Время, деньги, энергия, отношения, уверенность, упущенные возможности',
          lines: 5,
        ),
      ],
    ),
    5 => _question(
      eyebrow: 'ЖЕЛАЕМОЕ ИЗМЕНЕНИЕ',
      titleText: 'Чего вы на самом деле хотите за 90 дней?',
      subtitle:
          'Назовите фокус коротко и опишите наблюдаемый результат, а не общее намерение «заниматься» или «стараться».',
      children: [
        _field(
          keyName: 'focus-title-field',
          controller: title,
          label: 'Короткое название фокуса',
          hint: 'Например: вернуть проект в движение',
          lines: 2,
        ),
        const SizedBox(height: 13),
        _field(
          keyName: 'focus-result-field',
          controller: result,
          label: 'Что конкретно будет готово или изменится?',
          hint: 'Например: первая версия опубликована и проверена пользователями',
          lines: 4,
        ),
      ],
    ),
    6 => _question(
      eyebrow: 'ЛИЧНЫЙ СМЫСЛ',
      titleText: 'Почему этот результат важен именно вам?',
      subtitle:
          'Это проверка, не является ли цель только чужим ожиданием, красивой идеей или попыткой что-то доказать.',
      children: [
        _field(
          keyName: 'focus-why-field',
          controller: why,
          label: 'Моя настоящая причина',
          hint: 'Что ценного появится в вашей жизни?',
          lines: 5,
        ),
      ],
    ),
    7 => _question(
      eyebrow: 'ПЕРВЫЙ ФАКТ',
      titleText: 'Какой шаг проверит цель реальностью?',
      subtitle:
          'Выберите действие, после которого появится новая информация, обратная связь или маленький законченный результат.',
      children: [
        _field(
          keyName: 'focus-first-step-field',
          controller: firstStep,
          label: 'Первый проверочный шаг',
          hint: 'Позвонить, отправить, записаться, показать прототип, провести пробу',
          lines: 4,
        ),
      ],
    ),
    8 => _question(
      eyebrow: 'КОНКРЕТНЫЙ МОМЕНТ',
      titleText: 'Когда и где вы предпримете этот шаг?',
      subtitle:
          'Не просто «завтра», а после какого события, примерно в какое время и в каком месте.',
      children: [
        _field(
          keyName: 'focus-when-field',
          controller: whenWhere,
          label: 'Когда и где',
          hint: 'Например: завтра после завтрака, за рабочим столом',
          lines: 4,
        ),
      ],
    ),
    _ => _confidencePage(),
  };

  Widget _confidencePage() => _question(
    eyebrow: 'ПРОВЕРКА РЕАЛИСТИЧНОСТИ',
    titleText: 'Какова вероятность, что вы действительно сделаете этот шаг?',
    subtitle:
        'Оцените не своё желание получить результат, а вероятность конкретного действия в реальной жизни.',
    children: [
      Container(
        padding: const EdgeInsets.all(17),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(22),
          border: Border.all(color: const Color(0x1A132D2A)),
        ),
        child: Column(
          children: [
            Row(
              children: [
                const Text('0', style: TextStyle(color: Colors.black54)),
                Expanded(
                  child: Slider(
                    key: const ValueKey('focus-confidence-slider'),
                    value: confidence.toDouble(),
                    min: 0,
                    max: 10,
                    divisions: 10,
                    label: '$confidence',
                    onChanged: (value) =>
                        setState(() => confidence = value.round()),
                  ),
                ),
                const Text('10', style: TextStyle(color: Colors.black54)),
              ],
            ),
            Text(
              '$confidence из 10',
              style: const TextStyle(
                color: ink,
                fontSize: 28,
                fontWeight: FontWeight.w900,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              confidence >= 7
                  ? 'Шаг выглядит достаточно реалистичным.'
                  : 'Сейчас вероятность низкая — уменьшим действие, а не будем обвинять себя.',
              textAlign: TextAlign.center,
              style: const TextStyle(color: Color(0xFF5B6964)),
            ),
          ],
        ),
      ),
      if (confidence < 7) ...[
        const SizedBox(height: 14),
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: const Color(0xFFFFF4DE),
            borderRadius: BorderRadius.circular(18),
          ),
          child: const Text(
            'Что можно уменьшить, чтобы вероятность стала хотя бы 7? Новый вариант заменит первоначальный первый шаг.',
            style: TextStyle(height: 1.4),
          ),
        ),
        const SizedBox(height: 12),
        _field(
          keyName: 'focus-reduced-step-field',
          controller: reducedStep,
          label: 'Более посильный шаг',
          hint: 'Например: не тестировать всё приложение, а показать только первый экран одному человеку',
          lines: 4,
        ),
      ],
    ],
  );

  Widget _question({
    required String eyebrow,
    required String titleText,
    required String subtitle,
    required List<Widget> children,
  }) => ListView(
    padding: const EdgeInsets.fromLTRB(18, 14, 18, 32),
    children: [
      Text(
        eyebrow,
        style: const TextStyle(
          color: green,
          fontSize: 11,
          fontWeight: FontWeight.w900,
          letterSpacing: 1.05,
        ),
      ),
      const SizedBox(height: 8),
      Text(
        titleText,
        style: const TextStyle(
          color: ink,
          fontSize: 25,
          height: 1.14,
          fontWeight: FontWeight.w900,
        ),
      ),
      const SizedBox(height: 10),
      Text(
        subtitle,
        style: const TextStyle(
          color: Color(0xFF5B6964),
          fontSize: 14.5,
          height: 1.42,
        ),
      ),
      const SizedBox(height: 19),
      ...children,
    ],
  );

  Widget _field({
    required String keyName,
    required TextEditingController controller,
    required String label,
    required String hint,
    required int lines,
  }) => VoiceField(
    key: ValueKey(keyName),
    controller: controller,
    label: label,
    hint: hint,
    lines: lines,
  );
}

class GoalFocusReviewPage extends StatelessWidget {
  const GoalFocusReviewPage({
    required this.app,
    required this.guided,
    required this.title,
    required this.result,
    required this.why,
    required this.influence,
    required this.firstStep,
    required this.confidence,
    required this.situation,
    required this.outsideControl,
    required this.avoidance,
    required this.protection,
    required this.cost,
    required this.whenWhere,
    super.key,
  });

  final AppState app;
  final bool guided;
  final String title, result, why, influence, firstStep;
  final int confidence;
  final String situation, outsideControl, avoidance, protection, cost, whenWhere;

  void start(BuildContext context) {
    final now = DateTime.now();
    app.setGoal(
      Goal(
        title,
        result,
        0,
        const [],
        why: why,
        influence: influence,
        firstStep: firstStep,
        confidence: confidence,
        guided: guided,
        focusStartedAt: now,
        situation: situation,
        outsideControl: outsideControl,
        avoidance: avoidance,
        protection: protection,
        cost: cost,
        whenWhere: whenWhere,
      ),
    );

    final duplicate = app.actions.any(
      (item) =>
          item.goal &&
          item.state == null &&
          item.title.trim().toLowerCase() == firstStep.trim().toLowerCase(),
    );
    if (!duplicate) {
      app.add(
        ActionItem(
          id: 'focus_${now.microsecondsSinceEpoch}',
          title: firstStep,
          small: '',
          minutes: 0,
          support: Support.solo,
          goal: true,
          kind: IntentKind.goalStep,
          useTimer: false,
        ),
      );
    }
    Navigator.popUntil(context, (route) => route.isFirst);
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Предварительный фокус')),
    body: ListView(
      padding: const EdgeInsets.fromLTRB(18, 4, 18, 32),
      children: [
        Container(
          padding: const EdgeInsets.all(21),
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [Color(0xFF173C36), Color(0xFF356A60)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(27),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Icon(Icons.explore_outlined, color: mint, size: 19),
                  const SizedBox(width: 7),
                  const Text(
                    'ВАШ ПРЕДВАРИТЕЛЬНЫЙ ФОКУС',
                    style: TextStyle(
                      color: mint,
                      fontSize: 10.5,
                      fontWeight: FontWeight.w900,
                      letterSpacing: .9,
                    ),
                  ),
                  const Spacer(),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: Colors.white12,
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Text(
                      '$confidence/10',
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Text(
                title,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 25,
                  height: 1.12,
                  fontWeight: FontWeight.w900,
                ),
              ),
              const SizedBox(height: 9),
              Text(
                result,
                style: const TextStyle(
                  color: Color(0xFFD6E1DE),
                  fontSize: 14.5,
                  height: 1.42,
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 15),
        _FocusSummaryBlock(
          icon: Icons.favorite_border_rounded,
          label: 'ПОЧЕМУ ЭТО ВАЖНО',
          text: why,
        ),
        const SizedBox(height: 10),
        _FocusSummaryBlock(
          icon: Icons.control_point_duplicate_outlined,
          label: 'В ВАШЕЙ ЗОНЕ ВЛИЯНИЯ',
          text: influence,
        ),
        const SizedBox(height: 10),
        _FocusSummaryBlock(
          icon: Icons.play_circle_outline_rounded,
          label: 'ПЕРВЫЙ ШАГ В РЕАЛЬНОСТИ',
          text: firstStep,
          accent: true,
        ),
        if (whenWhere.isNotEmpty) ...[
          const SizedBox(height: 10),
          _FocusSummaryBlock(
            icon: Icons.schedule_rounded,
            label: 'КОГДА И ГДЕ',
            text: whenWhere,
          ),
        ],
        const SizedBox(height: 15),
        Container(
          padding: const EdgeInsets.all(15),
          decoration: BoxDecoration(
            color: const Color(0xFFF0F5F2),
            borderRadius: BorderRadius.circular(20),
          ),
          child: const Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(Icons.science_outlined, color: green, size: 22),
              SizedBox(width: 10),
              Expanded(
                child: Text(
                  'Сейчас вы не даёте обещание на 90 дней. Сначала цель проверяется реальным действием. Путь и масштаб можно будет уточнять.',
                  style: TextStyle(height: 1.42),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 19),
        FilledButton.icon(
          key: const ValueKey('start-focus-trial'),
          onPressed: () => start(context),
          icon: const Icon(Icons.flag_rounded),
          label: const Text('Начать проверку цели'),
        ),
        const SizedBox(height: 8),
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Вернуться и уточнить ответы'),
        ),
      ],
    ),
  );
}

class _FocusSummaryBlock extends StatelessWidget {
  const _FocusSummaryBlock({
    required this.icon,
    required this.label,
    required this.text,
    this.accent = false,
  });

  final IconData icon;
  final String label, text;
  final bool accent;

  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.all(15),
    decoration: BoxDecoration(
      color: accent ? const Color(0xFFE5F1EC) : Colors.white,
      borderRadius: BorderRadius.circular(20),
      border: Border.all(
        color: accent ? const Color(0xFFBDD9CD) : const Color(0x18132D2A),
      ),
    ),
    child: Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: 39,
          height: 39,
          decoration: BoxDecoration(
            color: accent ? mint : const Color(0xFFF0F4F2),
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
                label,
                style: const TextStyle(
                  color: green,
                  fontSize: 10.5,
                  fontWeight: FontWeight.w900,
                  letterSpacing: .75,
                ),
              ),
              const SizedBox(height: 5),
              Text(
                text,
                style: const TextStyle(
                  color: ink,
                  fontSize: 14,
                  height: 1.4,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ],
          ),
        ),
      ],
    ),
  );
}

class _FocusFoundationCard extends StatelessWidget {
  const _FocusFoundationCard({required this.goal});
  final Goal goal;

  @override
  Widget build(BuildContext context) {
    if (goal.why.isEmpty && goal.influence.isEmpty && goal.firstStep.isEmpty) {
      return const SizedBox.shrink();
    }
    return Container(
      key: const ValueKey('focus-foundation-card'),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFFF5F2E9),
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: const Color(0xFFE2DAC7)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.explore_outlined, color: green, size: 19),
              const SizedBox(width: 7),
              const Expanded(
                child: Text(
                  'ОСНОВА ФОКУСА',
                  style: TextStyle(
                    color: green,
                    fontSize: 10.5,
                    fontWeight: FontWeight.w900,
                    letterSpacing: .85,
                  ),
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.white70,
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  goal.confidence > 0
                      ? 'готовность ${goal.confidence}/10'
                      : 'предварительный',
                  style: const TextStyle(
                    color: green,
                    fontSize: 10.5,
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ),
            ],
          ),
          if (goal.why.isNotEmpty) ...[
            const SizedBox(height: 10),
            Text(
              'Почему важно: ${goal.why}',
              style: const TextStyle(color: ink, height: 1.38),
            ),
          ],
          if (goal.influence.isNotEmpty) ...[
            const SizedBox(height: 7),
            Text(
              'В зоне влияния: ${goal.influence}',
              style: const TextStyle(color: Color(0xFF596762), height: 1.38),
            ),
          ],
          const SizedBox(height: 10),
          const Row(
            children: [
              Icon(Icons.science_outlined, color: green, size: 17),
              SizedBox(width: 7),
              Expanded(
                child: Text(
                  'Первые 7 дней — проверка фокуса действием.',
                  style: TextStyle(
                    color: green,
                    fontSize: 12.5,
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class GoalEditor extends StatefulWidget {
  const GoalEditor({required this.app, this.existing, super.key});
  final AppState app;
  final Goal? existing;

  @override
  State<GoalEditor> createState() => _GoalEditorState();
}

class _GoalEditorState extends State<GoalEditor> {
  late final TextEditingController title;
  late final TextEditingController result;
  late final TextEditingController why;
  late final TextEditingController influence;

  @override
  void initState() {
    super.initState();
    title = TextEditingController(text: widget.existing?.title ?? '');
    result = TextEditingController(text: widget.existing?.result ?? '');
    why = TextEditingController(text: widget.existing?.why ?? '');
    influence = TextEditingController(text: widget.existing?.influence ?? '');
    for (final controller in [title, result, why, influence]) {
      controller.addListener(_refresh);
    }
  }

  void _refresh() {
    if (mounted) setState(() {});
  }

  @override
  void dispose() {
    for (final controller in [title, result, why, influence]) {
      controller.removeListener(_refresh);
      controller.dispose();
    }
    super.dispose();
  }

  void save() {
    final old = widget.existing!;
    widget.app.setGoal(
      Goal(
        title.text.trim(),
        result.text.trim(),
        old.minutes,
        old.areas,
        id: old.id,
        why: why.text.trim(),
        influence: influence.text.trim(),
        firstStep: old.firstStep,
        confidence: old.confidence,
        guided: old.guided,
        focusStartedAt: old.focusStartedAt,
        situation: old.situation,
        outsideControl: old.outsideControl,
        avoidance: old.avoidance,
        protection: old.protection,
        cost: old.cost,
        whenWhere: old.whenWhere,
        createdAt: old.createdAt,
        updatedAt: DateTime.now(),
      ),
    );
    Navigator.pop(context);
  }

  @override
  Widget build(BuildContext context) {
    if (widget.existing == null) {
      return GoalFocusEntryPage(app: widget.app);
    }
    return Scaffold(
      appBar: AppBar(title: const Text('Уточнить главный фокус')),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(18, 4, 18, 32),
        children: [
          Text(
            'Уточняйте формулировку, не начиная всё заново',
            style: Theme.of(context).textTheme.headlineMedium,
          ),
          const SizedBox(height: 8),
          const Text(
            'Маршрут, масштаб и следующий шаг можно менять. Здесь сохраняется само направление, которому вы решили дать преимущество.',
            style: TextStyle(height: 1.42),
          ),
          const SizedBox(height: 18),
          VoiceField(
            controller: title,
            label: 'Короткое название фокуса',
            hint: 'Например: выпустить приложение',
            lines: 2,
          ),
          const SizedBox(height: 13),
          VoiceField(
            controller: result,
            label: 'Результат через 90 дней',
            hint: 'Что конкретно будет готово или изменится?',
            lines: 4,
          ),
          const SizedBox(height: 13),
          VoiceField(
            controller: why,
            label: 'Почему это важно',
            hint: 'Ваша личная причина',
            lines: 4,
          ),
          const SizedBox(height: 13),
          VoiceField(
            controller: influence,
            label: 'Что находится в вашей зоне влияния',
            hint: 'Действия и решения, которыми вы можете управлять',
            lines: 4,
          ),
          const SizedBox(height: 22),
          FilledButton(
            onPressed:
                title.text.trim().isEmpty || result.text.trim().isEmpty
                ? null
                : save,
            child: const Text('Сохранить уточнения'),
          ),
        ],
      ),
    );
  }
}'''

text = replace_class(
    text,
    'CreateGoal extends StatelessWidget',
    'GoalHero extends StatelessWidget',
    CREATE_GOAL,
)
text = replace_class(
    text,
    'GoalEditor extends StatefulWidget',
    'ActionEditor extends StatefulWidget',
    FOCUS_FLOW,
)

foundation_marker = '''          _GoalPathHeader(app: app),
          const SizedBox(height: 18),'''
if foundation_marker not in text:
    raise SystemExit('Goal path header insertion point not found')
text = text.replace(
    foundation_marker,
    '''          _GoalPathHeader(app: app),
          if (goal.why.isNotEmpty ||
              goal.influence.isNotEmpty ||
              goal.firstStep.isNotEmpty) ...[
            const SizedBox(height: 12),
            _FocusFoundationCard(goal: goal),
          ],
          const SizedBox(height: 18),''',
    1,
)

# Product language: one protected focus, while the route remains flexible.
text = text.replace("'ГЛАВНАЯ ЦЕЛЬ'", "'ГЛАВНЫЙ ФОКУС · 90 ДНЕЙ'")
text = text.replace("'Главная цель'", "'Главный фокус'")
text = text.replace("label: 'Цель',", "label: 'Фокус',")
text = text.replace("tooltip: 'Изменить цель'", "tooltip: 'Уточнить фокус'")
text = text.replace('к главной цели', 'к главному фокусу')
text = text.replace('главной цели', 'главному фокусу')

for required in [
    "ValueKey('focus-quick-route')",
    "ValueKey('focus-guided-route')",
    "ValueKey('focus-confidence-slider')",
    "ValueKey('start-focus-trial')",
    'class GoalFocusReviewPage',
    'Первые 7 дней — проверка фокуса действием.',
]:
    if required not in text:
        raise SystemExit(f'focus flow fragment missing: {required}')

path.write_text(text, encoding='utf-8')
print('Added quick and guided 90-day focus selection flow')