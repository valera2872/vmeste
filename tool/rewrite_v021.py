from pathlib import Path

main_path = Path("lib/main.dart")
text = main_path.read_text(encoding="utf-8")

def replace_block(source: str, start: str, end: str, replacement: str) -> str:
    i = source.index(start)
    j = source.index(end, i)
    return source[:i] + replacement.rstrip() + "\n\n" + source[j:]

onboarding = r"""
class _OnboardingState extends State<Onboarding> {
  final pages = PageController();
  final name = TextEditingController();
  int page = 0;
  Age age = Age.adult;

  @override
  void dispose() {
    pages.dispose();
    name.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => Scaffold(
        backgroundColor: ink,
        body: SafeArea(
          child: Column(
            children: [
              Padding(
                padding: const EdgeInsets.all(22),
                child: Row(
                  children: [
                    const Logo(),
                    const SizedBox(width: 12),
                    const Text(
                      'Вместе к цели',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 20,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                    const Spacer(),
                    Text(
                      '${page + 1} / 3',
                      style: const TextStyle(color: Colors.white54),
                    ),
                  ],
                ),
              ),
              Expanded(
                child: PageView(
                  controller: pages,
                  onPageChanged: (value) => setState(() => page = value),
                  children: [
                    const IntroPage(
                      icon: Icons.handshake_rounded,
                      kicker: 'КОГДА ОДНОМУ ТРУДНО',
                      title:
                          'Одному бывает трудно довести важную цель до результата.',
                      text:
                          'Это нормально. Человеку часто не хватает не силы воли, а поддержки: понятного следующего действия, напоминания или того, кто заметит его усилия.',
                      points: [
                        'Здесь вас не будут ругать за пропуски',
                        'Приложение поможет начать, а не только записать цель',
                        'После остановки поможет спокойно продолжить',
                      ],
                    ),
                    const IntroPage(
                      icon: Icons.people_alt_rounded,
                      kicker: 'ПОДДЕРЖКА БЫВАЕТ РАЗНОЙ',
                      title: 'Найдём то, что поможет именно вам.',
                      text:
                          'Зарядку можно делать вместе. Результат тренировки — отправлять товарищу. Работу над сайтом — начинать одновременно с напарником. Иногда достаточно точного напоминания или помощи AI.',
                      points: [
                        'Начать одновременно с человеком',
                        'Отправить фото, видео или короткий отчёт',
                        'Попросить куратора напомнить и спросить о результате',
                        'Работать самостоятельно, но не забывать о цели',
                      ],
                    ),
                    ProfilePage(
                      name: name,
                      age: age,
                      onAge: (value) => setState(() => age = value),
                    ),
                  ],
                ),
              ),
              Padding(
                padding: const EdgeInsets.fromLTRB(22, 10, 22, 22),
                child: Column(
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: List.generate(
                        3,
                        (index) => AnimatedContainer(
                          duration: const Duration(milliseconds: 200),
                          margin: const EdgeInsets.all(4),
                          width: index == page ? 28 : 8,
                          height: 8,
                          decoration: BoxDecoration(
                            color: index == page ? mint : Colors.white24,
                            borderRadius: BorderRadius.circular(9),
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),
                    FilledButton(
                      style: FilledButton.styleFrom(
                        backgroundColor: mint,
                        foregroundColor: ink,
                      ),
                      onPressed: () {
                        if (page < 2) {
                          pages.nextPage(
                            duration: const Duration(milliseconds: 350),
                            curve: Curves.easeOut,
                          );
                        } else {
                          widget.app.finish(age, name.text);
                        }
                      },
                      child: Text(page == 2 ? 'Начать' : 'Дальше'),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      );
}
"""

profile = r"""
class ProfilePage extends StatelessWidget {
  const ProfilePage({
    required this.name,
    required this.age,
    required this.onAge,
    super.key,
  });

  final TextEditingController name;
  final Age age;
  final ValueChanged<Age> onAge;

  @override
  Widget build(BuildContext context) => ListView(
        padding: const EdgeInsets.fromLTRB(22, 25, 22, 20),
        children: [
          Container(
            height: 155,
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF3A7A6E), Color(0xFF1C4540)],
              ),
              borderRadius: BorderRadius.circular(32),
            ),
            child: const Center(child: Logo(size: 88)),
          ),
          const SizedBox(height: 26),
          const Text(
            'Немного о вас',
            style: TextStyle(
              color: Colors.white,
              fontSize: 35,
              height: 1.05,
              fontWeight: FontWeight.w900,
            ),
          ),
          const SizedBox(height: 12),
          const Text(
            'Имя поможет обращаться к вам лично. Его можно не указывать. Возраст нужен, чтобы приложение подбирало понятные слова и примеры.',
            style: TextStyle(
              color: Color(0xFFD5E0DD),
              fontSize: 16,
              height: 1.45,
            ),
          ),
          const SizedBox(height: 22),
          TextField(
            controller: name,
            decoration: const InputDecoration(
              labelText: 'Как к вам обращаться?',
              hintText: 'Например: Валерий',
            ),
          ),
          const SizedBox(height: 20),
          const Text(
            'Сколько вам лет?',
            style: TextStyle(
              color: Colors.white,
              fontSize: 19,
              fontWeight: FontWeight.w900,
            ),
          ),
          const SizedBox(height: 10),
          Wrap(
            spacing: 9,
            runSpacing: 9,
            children: [
              ageChip('10–12', Age.a10),
              ageChip('13–15', Age.a13),
              ageChip('16–17', Age.a16),
              ageChip('18+', Age.adult),
            ],
          ),
        ],
      );

  Widget ageChip(String text, Age value) => ChoiceChip(
        label: Text(text),
        selected: age == value,
        onSelected: (_) => onAge(value),
        selectedColor: mint,
        labelStyle: TextStyle(
          color: age == value ? ink : Colors.white,
          fontWeight: FontWeight.w800,
        ),
        backgroundColor: Colors.white12,
        side: BorderSide(color: age == value ? mint : Colors.white24),
      );
}
"""

shell_state = r"""
class _ShellState extends State<Shell> {
  int index = 0;

  @override
  Widget build(BuildContext context) => Scaffold(
        body: IndexedStack(
          index: index,
          children: [
            Today(app: widget.app),
            GoalScreen(app: widget.app),
            SupportScreen(app: widget.app),
            Progress(app: widget.app),
          ],
        ),
        bottomNavigationBar: NavigationBar(
          selectedIndex: index,
          onDestinationSelected: (value) => setState(() => index = value),
          destinations: const [
            NavigationDestination(
              icon: Icon(Icons.today_outlined),
              selectedIcon: Icon(Icons.today),
              label: 'Сегодня',
            ),
            NavigationDestination(
              icon: Icon(Icons.flag_outlined),
              selectedIcon: Icon(Icons.flag),
              label: 'Цель',
            ),
            NavigationDestination(
              icon: Icon(Icons.help_outline_rounded),
              selectedIcon: Icon(Icons.help_rounded),
              label: 'Помощь',
            ),
            NavigationDestination(
              icon: Icon(Icons.history_rounded),
              selectedIcon: Icon(Icons.history_toggle_off_rounded),
              label: 'История',
            ),
          ],
        ),
      );
}
"""

today = r"""
class Today extends StatelessWidget {
  const Today({required this.app, super.key});
  final AppState app;

  @override
  Widget build(BuildContext context) {
    final goalAction = app.actions
        .where((item) => item.goal && item.state == null)
        .firstOrNull;
    final otherActions =
        app.actions.where((item) => !item.goal && item.state == null).toList();

    return Scaffold(
      appBar: AppBar(
        title: const Row(
          children: [
            Logo(size: 30),
            SizedBox(width: 10),
            Text('Вместе к цели'),
          ],
        ),
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
        padding: const EdgeInsets.fromLTRB(18, 4, 18, 105),
        children: [
          Text(app.hello, style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 5),
          const Text('Что вы хотите сделать сегодня?'),
          const SizedBox(height: 20),
          if (app.goal == null)
            CreateGoal(app: app)
          else ...[
            GoalHero(app: app),
            const SizedBox(height: 22),
            section('Что сделать для главной цели сегодня?'),
            const SizedBox(height: 9),
            if (goalAction == null)
              EmptyAction(
                onTap: () => Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) =>
                        ActionEditor(app: app, goalDefault: true),
                  ),
                ),
              )
            else
              ActionCard(app: app, item: goalAction, featured: true),
          ],
          const SizedBox(height: 23),
          section('Другие дела на сегодня'),
          const SizedBox(height: 9),
          if (otherActions.isEmpty)
            const Card(
              child: Padding(
                padding: EdgeInsets.all(18),
                child: Text(
                  'Запишите сюда дела, которые нужно выполнить сегодня.',
                ),
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
"""

create_goal = r"""
class CreateGoal extends StatelessWidget {
  const CreateGoal({required this.app, super.key});
  final AppState app;

  @override
  Widget build(BuildContext context) => Container(
        padding: const EdgeInsets.all(23),
        decoration: BoxDecoration(
          gradient: const LinearGradient(
            colors: [ink, Color(0xFF35685F)],
          ),
          borderRadius: BorderRadius.circular(28),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'ВАША ВАЖНАЯ ЦЕЛЬ',
              style: TextStyle(
                color: mint,
                fontSize: 12,
                fontWeight: FontWeight.w900,
                letterSpacing: 1.1,
              ),
            ),
            const SizedBox(height: 10),
            const Text(
              'Чего вам пока не удаётся добиться?',
              style: TextStyle(
                color: Colors.white,
                fontSize: 27,
                height: 1.12,
                fontWeight: FontWeight.w900,
              ),
            ),
            const SizedBox(height: 11),
            const Text(
              'Выберите одну цель, которую хотите довести до результата. Приложение поможет понять, что делать дальше, и подобрать помощь, с которой вам будет легче продолжать.',
              style: TextStyle(
                color: Color(0xFFD7E2DF),
                fontSize: 16,
                height: 1.4,
              ),
            ),
            const SizedBox(height: 18),
            FilledButton(
              style: FilledButton.styleFrom(
                backgroundColor: mint,
                foregroundColor: ink,
              ),
              onPressed: () => Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => GoalEditor(app: app)),
              ),
              child: const Text('Выбрать цель'),
            ),
          ],
        ),
      );
}
"""

empty_action = r"""
class EmptyAction extends StatelessWidget {
  const EmptyAction({required this.onTap, super.key});
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) => Card(
        child: Padding(
          padding: const EdgeInsets.all(18),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Выберите одно конкретное действие, которое приблизит вас к цели.',
                style: TextStyle(fontWeight: FontWeight.w800),
              ),
              const SizedBox(height: 7),
              const Text(
                'Для него можно выбрать напоминание, помощь AI, совместный старт, отчёт знакомому или куратора.',
              ),
              const SizedBox(height: 13),
              OutlinedButton(
                onPressed: onTap,
                child: const Text('Добавить действие'),
              ),
            ],
          ),
        ),
      );
}
"""

goal_screen = r"""
class GoalScreen extends StatelessWidget {
  const GoalScreen({required this.app, super.key});
  final AppState app;

  @override
  Widget build(BuildContext context) => Scaffold(
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
                'Здесь собраны желаемый результат и части работы, которые к нему ведут.',
              ),
              const SizedBox(height: 18),
              GoalHero(app: app),
              const SizedBox(height: 16),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(18),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Какой результат я хочу получить?',
                        style: TextStyle(
                          fontWeight: FontWeight.w900,
                          fontSize: 17,
                        ),
                      ),
                      const SizedBox(height: 7),
                      Text(
                        app.goal!.result.isEmpty
                            ? 'Добавьте конкретный результат, чтобы понимать, когда цель достигнута.'
                            : app.goal!.result,
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 12),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(18),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Что нужно сделать?',
                        style: TextStyle(
                          fontWeight: FontWeight.w900,
                          fontSize: 17,
                        ),
                      ),
                      const SizedBox(height: 9),
                      if (app.goal!.areas.isEmpty)
                        const Text(
                          'Разделите цель на части. Так будет легче выбирать конкретные действия на каждый день.',
                        )
                      else
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
              const SizedBox(height: 14),
              OutlinedButton.icon(
                onPressed: () => Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) =>
                        GoalEditor(app: app, existing: app.goal),
                  ),
                ),
                icon: const Icon(Icons.edit_outlined),
                label: const Text('Изменить цель'),
              ),
              const SizedBox(height: 10),
              FilledButton.icon(
                onPressed: () => Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) =>
                        ActionEditor(app: app, goalDefault: true),
                  ),
                ),
                icon: const Icon(Icons.add_task),
                label: const Text('Добавить действие на сегодня'),
              ),
            ],
          ],
        ),
      );
}
"""

goal_editor_state = r"""
class _GoalEditorState extends State<GoalEditor> {
  late final TextEditingController title;
  late final TextEditingController result;
  late final TextEditingController areas;
  int minutes = 20;

  @override
  void initState() {
    super.initState();
    title = TextEditingController(text: widget.existing?.title ?? '');
    result = TextEditingController(text: widget.existing?.result ?? '');
    areas = TextEditingController(
      text: widget.existing?.areas.join(', ') ?? '',
    );
    minutes = widget.existing?.minutes ?? 20;
    title.addListener(() => setState(() {}));
  }

  @override
  void dispose() {
    title.dispose();
    result.dispose();
    areas.dispose();
    super.dispose();
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
              'Выберите одну важную цель, которую хотите довести до результата.',
            ),
            const SizedBox(height: 18),
            VoiceField(
              controller: title,
              label: 'Моя цель',
              hint:
                  'Например: закончить все недоделки и навести порядок в доме',
              lines: 3,
            ),
            const SizedBox(height: 13),
            VoiceField(
              controller: result,
              label: 'Какой результат вы хотите получить?',
              hint:
                  'Например: все незаконченные работы выполнены, а у каждой вещи есть место',
              lines: 3,
            ),
            const SizedBox(height: 13),
            VoiceField(
              controller: areas,
              label: 'На какие части можно разделить эту цель?',
              hint: 'Например: кухня, документы, ремонт, вещи без места',
              lines: 3,
            ),
            const SizedBox(height: 18),
            const Text(
              'Сколько времени вы готовы уделять ей за один раз?',
              style: TextStyle(
                fontWeight: FontWeight.w900,
                fontSize: 17,
              ),
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
            const SizedBox(height: 24),
            FilledButton(
              onPressed: title.text.trim().isEmpty
                  ? null
                  : () {
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
                      Navigator.pop(context);
                    },
              child: const Text('Сохранить цель'),
            ),
          ],
        ),
      );
}
"""

text = replace_block(text, "class _OnboardingState", "class IntroPage", onboarding)
text = replace_block(text, "class ProfilePage", "class Shell", profile)
text = replace_block(text, "class _ShellState", "class Today", shell_state)
text = replace_block(text, "class Today", "class CreateGoal", today)
text = replace_block(text, "class CreateGoal", "class GoalHero", create_goal)
text = replace_block(text, "class EmptyAction", "class ActionCard", empty_action)
text = replace_block(text, "class GoalScreen", "class GoalEditor", goal_screen)
text = replace_block(text, "class _GoalEditorState", "class ActionEditor", goal_editor_state)

replacements = {
    "'Что именно вы сделаете?'": "'Что вы сделаете сегодня?'",
    "'Запишите действие так, чтобы его можно было начать и увидеть результат.'": "'Выберите одно конкретное действие, которое можно начать без долгой подготовки.'",
    "label:'Конкретное действие'": "label:'Действие'",
    "label:'Что будет достаточным результатом на трудный день?'": "label:'Если времени или сил будет мало, что вы всё равно сможете сделать?'",
    "'Это действие для главной цели'": "'Это действие относится к главной цели'",
    "'Сколько времени?'": "'Сколько времени вы готовы потратить?'",
    "'Какая поддержка подходит?'": "'Что поможет вам выполнить это действие?'",
    "'Рекомендация: ${supportName(rec.$1)}. ${rec.$2}'": "'Можно попробовать: ${supportName(rec.$1)}. ${rec.$2}'",
    "'Сохранить и перейти к старту'": "'Добавить и начать'",
    "appBar: AppBar(title: const Text('Поддержка'))": "appBar: AppBar(title: const Text('Помощь'))",
    "'Для разных шагов — разная помощь'": "'Как приложение может помочь?'",
    "'«Вместе» — это не обязанность делать всё вдвоём, а возможность не оставаться без нужной поддержки.'": "'Для каждого действия можно выбрать свой способ помощи. Его можно менять, если он не подходит.'",
    "'Добровольный куратор'": "'Куратор'",
    "'Вы выбираете человека, который может напомнить, спросить о результате и поддержать возвращение. Он не управляет вашей целью.'": "'Выберите человека, который согласен напоминать, спрашивать, что получилось, и помогать продолжить после пропуска. Он не управляет вашей целью.'",
    "'Сохранить договорённость'": "'Сохранить имя куратора'",
    "appBar: AppBar(title: const Text('Прогресс'))": "appBar: AppBar(title: const Text('История'))",
    "'Доказательства движения'": "'Что уже сделано'",
    "'История реальных действий, частичных результатов и возвращений.'": "'Здесь сохраняются выполненные действия, частичные результаты и переносы.'",
    "stat('$stops', 'остановок')": "stat('$stops', 'перенесено')",
    "'После первой сессии здесь появится действие, вид поддержки и результат.'": "'После первого действия здесь появятся его результат и выбранный способ помощи.'",
    "'Цель получила реальное действие.'": "'Сегодня вы сделали то, что приближает вас к цели.'",
    "'Путь не обнулился.'": "'Сегодня не получилось — это не конец.'",
    "'Вы создали подтверждённый шаг: «${item.title}».'": "'Готово: «${item.title}».'",
    "'Действие сохранено в истории. Возвращение станет следующим важным шагом.'": "'Действие сохранено. Вы сможете назначить другое время или выбрать меньший вариант.'",
    "'Вернуться к сегодняшнему дню'": "'Вернуться на экран «Сегодня»'",
    "Support.solo=>'Точное напоминание и спокойный старт.'": "Support.solo=>'Приложение напомнит и сохранит результат.'",
    "Support.ai=>'Разобрать действие и получить следующий шаг.'": "Support.ai=>'Поможет понять, с чего начать и что делать дальше.'",
    "Support.together=>'Начать одновременно: одинаковые или разные дела.'": "Support.together=>'Начать одновременно, даже если у вас разные дела.'",
    "Support.report=>'Отправить фото, видео, цифру или текст.'": "Support.report=>'Показать знакомому, что вы действительно сделали.'",
    "Support.curator=>'Человек напоминает и спрашивает о результате.'": "Support.curator=>'Человек напомнит, спросит и поможет продолжить.'",
}
for old, new in replacements.items():
    if old not in text:
        raise SystemExit(f"Expected text not found: {old}")
    text = text.replace(old, new)

main_path.write_text(text, encoding="utf-8")

pubspec = Path("pubspec.yaml")
pub_text = pubspec.read_text(encoding="utf-8")
pub_text = pub_text.replace("version: 0.2.0+2", "version: 0.2.1+3")
pub_text = pub_text.replace(
    "description: Вместе к цели — интеллектуальная система достижения главной цели.",
    "description: Вместе к цели — приложение, которое помогает получить поддержку и довести важную цель до результата.",
)
pubspec.write_text(pub_text, encoding="utf-8")

test_path = Path("test/widget_test.dart")
test_text = test_path.read_text(encoding="utf-8")
test_text = test_text.replace(
    "expect(find.text('Большая цель требует места в каждом дне.'), findsOneWidget);",
    "expect(find.text('Одному бывает трудно довести важную цель до результата.'), findsOneWidget);",
)
test_path.write_text(test_text, encoding="utf-8")
