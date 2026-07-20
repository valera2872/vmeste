import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:share_plus/share_plus.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final app = AppState();
  await app.load();
  runApp(VmesteApp(app: app));
}

const ink = Color(0xFF132D2A),
    green = Color(0xFF39776B),
    mint = Color(0xFFBFE2D6),
    cream = Color(0xFFF7F4EC);

enum Age { a10, a13, a16, adult }

enum Support { solo, ai, together, report, curator }

enum ResultState { done, part, moved, missed }

enum StartProblem {
  unclear,
  tooBig,
  noImpulse,
  distracted,
  accountability,
  reminder,
}

class Goal {
  Goal(this.title, this.result, this.minutes, this.areas);
  final String title, result;
  final int minutes;
  final List<String> areas;
  Map<String, dynamic> toJson() => {
    'title': title,
    'result': result,
    'minutes': minutes,
    'areas': areas,
  };
  factory Goal.fromJson(Map<String, dynamic> j) => Goal(
    j['title'] ?? '',
    j['result'] ?? '',
    j['minutes'] ?? 20,
    List<String>.from(j['areas'] ?? []),
  );
}

class ActionItem {
  ActionItem({
    required this.id,
    required this.title,
    required this.small,
    required this.minutes,
    required this.support,
    required this.goal,
    this.state,
  });
  final String id, title, small;
  final int minutes;
  Support support;
  final bool goal;
  ResultState? state;
  Map<String, dynamic> toJson() => {
    'id': id,
    'title': title,
    'small': small,
    'minutes': minutes,
    'support': support.name,
    'goal': goal,
    'state': state?.name,
  };
  factory ActionItem.fromJson(Map<String, dynamic> j) => ActionItem(
    id: j['id'] ?? '',
    title: j['title'] ?? '',
    small: j['small'] ?? '',
    minutes: j['minutes'] ?? 10,
    support: Support.values.firstWhere(
      (e) => e.name == j['support'],
      orElse: () => Support.ai,
    ),
    goal: j['goal'] ?? false,
    state: j['state'] == null
        ? null
        : ResultState.values.firstWhere((e) => e.name == j['state']),
  );
}

class HistoryItem {
  HistoryItem(
    this.title,
    this.minutes,
    this.support,
    this.state,
    this.date,
    this.goal,
  );
  final String title;
  final int minutes;
  final Support support;
  final ResultState state;
  final DateTime date;
  final bool goal;
  Map<String, dynamic> toJson() => {
    'title': title,
    'minutes': minutes,
    'support': support.name,
    'state': state.name,
    'date': date.toIso8601String(),
    'goal': goal,
  };
  factory HistoryItem.fromJson(Map<String, dynamic> j) => HistoryItem(
    j['title'] ?? '',
    j['minutes'] ?? 0,
    Support.values.firstWhere(
      (e) => e.name == j['support'],
      orElse: () => Support.solo,
    ),
    ResultState.values.firstWhere(
      (e) => e.name == j['state'],
      orElse: () => ResultState.done,
    ),
    DateTime.tryParse(j['date'] ?? '') ?? DateTime.now(),
    j['goal'] ?? false,
  );
}

class AppState extends ChangeNotifier {
  bool onboarded = false;
  String name = '', curator = '';
  Age age = Age.adult;
  Goal? goal;
  final List<ActionItem> actions = [];
  final List<HistoryItem> history = [];
  static const key = 'vmeste02';
  Future<void> load() async {
    final p = await SharedPreferences.getInstance();
    final raw = p.getString(key);
    if (raw == null) return;
    try {
      final j = jsonDecode(raw);
      onboarded = j['onboarded'] ?? false;
      name = j['name'] ?? '';
      curator = j['curator'] ?? '';
      age = Age.values.firstWhere(
        (e) => e.name == j['age'],
        orElse: () => Age.adult,
      );
      if (j['goal'] != null) {
        goal = Goal.fromJson(Map<String, dynamic>.from(j['goal']));
      }
      actions.addAll(
        (j['actions'] ?? []).map<ActionItem>(
          (e) => ActionItem.fromJson(Map<String, dynamic>.from(e)),
        ),
      );
      history.addAll(
        (j['history'] ?? []).map<HistoryItem>(
          (e) => HistoryItem.fromJson(Map<String, dynamic>.from(e)),
        ),
      );
    } catch (_) {}
  }

  Future<void> save() async {
    final p = await SharedPreferences.getInstance();
    await p.setString(
      key,
      jsonEncode({
        'onboarded': onboarded,
        'name': name,
        'curator': curator,
        'age': age.name,
        'goal': goal?.toJson(),
        'actions': actions.map((e) => e.toJson()).toList(),
        'history': history.map((e) => e.toJson()).toList(),
      }),
    );
  }

  void finish(Age a, String n) {
    age = a;
    name = n.trim();
    onboarded = true;
    notifyListeners();
    save();
  }

  void setGoal(Goal g) {
    goal = g;
    notifyListeners();
    save();
  }

  void add(ActionItem a) {
    actions.insert(0, a);
    notifyListeners();
    save();
  }

  void setSupport(ActionItem action, Support support) {
    action.support = support;
    notifyListeners();
    save();
  }

  void complete(ActionItem a, ResultState s) {
    a.state = s;
    history.insert(
      0,
      HistoryItem(a.title, a.minutes, a.support, s, DateTime.now(), a.goal),
    );
    notifyListeners();
    save();
  }

  void setCurator(String value) {
    curator = value.trim();
    notifyListeners();
    save();
  }

  int get goalDone => history
      .where(
        (e) =>
            e.goal &&
            (e.state == ResultState.done || e.state == ResultState.part),
      )
      .length;
  String get hello => name.isEmpty ? 'С чего начнём?' : '$name, с чего начнём?';
}

class VmesteApp extends StatelessWidget {
  const VmesteApp({required this.app, super.key});
  final AppState app;
  @override
  Widget build(BuildContext context) => AnimatedBuilder(
    animation: app,
    builder: (context, child) => MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Вместе к цели',
      theme: ThemeData(
        useMaterial3: true,
        scaffoldBackgroundColor: cream,
        colorScheme: ColorScheme.fromSeed(seedColor: green),
        textTheme: const TextTheme(
          headlineLarge: TextStyle(
            color: ink,
            fontSize: 34,
            height: 1.07,
            fontWeight: FontWeight.w900,
            letterSpacing: -1,
          ),
          headlineMedium: TextStyle(
            color: ink,
            fontSize: 27,
            fontWeight: FontWeight.w900,
          ),
          titleLarge: TextStyle(
            color: ink,
            fontSize: 20,
            fontWeight: FontWeight.w900,
          ),
          bodyLarge: TextStyle(color: ink, fontSize: 17, height: 1.45),
        ),
        cardTheme: CardThemeData(
          color: Colors.white,
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(24),
          ),
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: cream,
          foregroundColor: ink,
          elevation: 0,
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: Colors.white,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(18),
            borderSide: BorderSide.none,
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(18),
            borderSide: const BorderSide(color: Color(0xFFE1DED4)),
          ),
        ),
        filledButtonTheme: FilledButtonThemeData(
          style: FilledButton.styleFrom(
            backgroundColor: ink,
            minimumSize: const Size.fromHeight(56),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(18),
            ),
            textStyle: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w800,
            ),
          ),
        ),
        navigationBarTheme: const NavigationBarThemeData(
          height: 72,
          backgroundColor: Colors.white,
          indicatorColor: mint,
        ),
      ),
      home: app.onboarded ? Shell(app: app) : Onboarding(app: app),
    ),
  );
}

class Logo extends StatelessWidget {
  const Logo({this.size = 44, super.key});
  final double size;
  @override
  Widget build(BuildContext context) => SizedBox(
    width: size,
    height: size,
    child: Stack(
      alignment: Alignment.center,
      children: [
        Transform.rotate(
          angle: .78,
          child: Container(
            width: size * .68,
            height: size * .68,
            decoration: BoxDecoration(
              color: mint,
              borderRadius: BorderRadius.circular(size * .18),
            ),
          ),
        ),
        Container(
          width: size * .34,
          height: size * .34,
          decoration: const BoxDecoration(color: ink, shape: BoxShape.circle),
        ),
      ],
    ),
  );
}

class Onboarding extends StatefulWidget {
  const Onboarding({required this.app, super.key});
  final AppState app;
  @override
  State<Onboarding> createState() => _OnboardingState();
}

class _OnboardingState extends State<Onboarding> {
  final pages = PageController();
  int page = 0;

  @override
  void dispose() {
    pages.dispose();
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
                TextButton(
                  onPressed: () => widget.app.finish(Age.adult, ''),
                  child: const Text(
                    'Пропустить',
                    style: TextStyle(color: Colors.white70),
                  ),
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
                      'Бывает, что цель важна, но одному трудно начать и не бросить.',
                  text:
                      'Это не всегда вопрос силы воли. Иногда не хватает понятного первого действия, напоминания или человека, который поддержит.',
                  points: [
                    'Здесь вас не будут ругать за пропуски',
                    'Приложение поможет начать, а не только записать цель',
                    'Пропуск не считается провалом',
                  ],
                ),
                const IntroPage(
                  icon: Icons.people_alt_rounded,
                  kicker: 'ПОДДЕРЖКА БЫВАЕТ РАЗНОЙ',
                  title: 'Для разных дел нужна разная помощь.',
                  text:
                      'Одно дело легче начать вместе. Для другого достаточно показать результат знакомому. Сложную задачу сначала полезно разобрать с цифровым помощником.',
                  points: [
                    'Начать одновременно с человеком',
                    'Отправить фото, видео или короткий отчёт',
                    'Попросить куратора напомнить и спросить о результате',
                    'Работать самостоятельно, но не забывать о цели',
                  ],
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
                    2,
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
                    if (page < 1) {
                      pages.nextPage(
                        duration: const Duration(milliseconds: 350),
                        curve: Curves.easeOut,
                      );
                    } else {
                      widget.app.finish(Age.adult, '');
                    }
                  },
                  child: Text(page == 1 ? 'Перейти к цели' : 'Дальше'),
                ),
              ],
            ),
          ),
        ],
      ),
    ),
  );
}

class IntroPage extends StatelessWidget {
  const IntroPage({
    required this.icon,
    required this.kicker,
    required this.title,
    required this.text,
    required this.points,
    super.key,
  });
  final IconData icon;
  final String kicker, title, text;
  final List<String> points;
  @override
  Widget build(BuildContext context) => ListView(
    padding: const EdgeInsets.fromLTRB(22, 12, 22, 20),
    children: [
      Container(
        height: 210,
        decoration: BoxDecoration(
          gradient: const LinearGradient(
            colors: [Color(0xFF3A7A6E), Color(0xFF1C4540)],
          ),
          borderRadius: BorderRadius.circular(34),
        ),
        child: Center(
          child: Container(
            width: 105,
            height: 105,
            decoration: const BoxDecoration(
              color: mint,
              shape: BoxShape.circle,
            ),
            child: Icon(icon, size: 52, color: ink),
          ),
        ),
      ),
      const SizedBox(height: 28),
      Text(
        kicker,
        style: const TextStyle(
          color: mint,
          fontSize: 12,
          fontWeight: FontWeight.w900,
          letterSpacing: 1.2,
        ),
      ),
      const SizedBox(height: 12),
      Text(
        title,
        style: const TextStyle(
          color: Colors.white,
          fontSize: 37,
          height: 1.04,
          fontWeight: FontWeight.w900,
          letterSpacing: -1.3,
        ),
      ),
      const SizedBox(height: 15),
      Text(
        text,
        style: const TextStyle(
          color: Color(0xFFD5E0DD),
          fontSize: 17,
          height: 1.45,
        ),
      ),
      const SizedBox(height: 20),
      ...points.map(
        (p) => Padding(
          padding: const EdgeInsets.only(bottom: 11),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Icon(Icons.check_circle_rounded, color: mint, size: 19),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  p,
                  style: const TextStyle(color: Colors.white, fontSize: 15.5),
                ),
              ),
            ],
          ),
        ),
      ),
    ],
  );
}

class HowItWorksPage extends StatelessWidget {
  const HowItWorksPage({super.key});

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Как это работает')),
    body: ListView(
      padding: const EdgeInsets.fromLTRB(18, 4, 18, 32),
      children: [
        Text(
          'Не обязательно справляться в одиночку',
          style: Theme.of(context).textTheme.headlineMedium,
        ),
        const SizedBox(height: 9),
        const Text(
          'Бывает, что цель важна, но начать или продолжать одному трудно. Это не всегда вопрос силы воли: иногда не хватает ясного первого действия, напоминания или человека рядом.',
        ),
        const SizedBox(height: 18),
        const _InfoCard(
          icon: Icons.auto_awesome_rounded,
          title: 'Разобраться с делом',
          text:
              'Если задача непонятна или кажется слишком большой, цифровой помощник предложит первый шаг или небольшую часть.',
        ),
        const _InfoCard(
          icon: Icons.people_alt_rounded,
          title: 'Начать вместе',
          text:
              'Можно договориться с человеком начать одновременно, даже если каждый занимается своим делом.',
        ),
        const _InfoCard(
          icon: Icons.ios_share_rounded,
          title: 'Показать результат',
          text:
              'После дела можно отправить знакомому фото, видео, ссылку или короткий итог.',
        ),
        const _InfoCard(
          icon: Icons.verified_user_outlined,
          title: 'Попросить куратора',
          text:
              'Знакомый может напомнить, спросить о результате и поддержать после пропуска.',
        ),
        const SizedBox(height: 8),
        const Text(
          'Начните с важной цели',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.w900),
        ),
        const SizedBox(height: 8),
        const Text(
          'Сначала назовите цель. Затем выберите одно действие на сегодня и способ поддержки, с которым вам будет легче его выполнить.',
        ),
      ],
    ),
  );
}

class _InfoCard extends StatelessWidget {
  const _InfoCard({
    required this.icon,
    required this.title,
    required this.text,
  });

  final IconData icon;
  final String title;
  final String text;

  @override
  Widget build(BuildContext context) => Card(
    margin: const EdgeInsets.only(bottom: 10),
    child: Padding(
      padding: const EdgeInsets.all(17),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 44,
            height: 44,
            decoration: BoxDecoration(
              color: mint,
              borderRadius: BorderRadius.circular(14),
            ),
            child: Icon(icon, color: ink),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 17,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                const SizedBox(height: 4),
                Text(text),
              ],
            ),
          ),
        ],
      ),
    ),
  );
}

class Shell extends StatefulWidget {
  const Shell({required this.app, super.key});
  final AppState app;
  @override
  State<Shell> createState() => _ShellState();
}

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
          icon: Icon(Icons.people_outline_rounded),
          selectedIcon: Icon(Icons.people_alt_rounded),
          label: 'Вместе',
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

class Today extends StatelessWidget {
  const Today({required this.app, super.key});
  final AppState app;

  @override
  Widget build(BuildContext context) {
    final goalAction = app.actions
        .where((item) => item.goal && item.state == null)
        .firstOrNull;
    final otherActions = app.actions
        .where((item) => !item.goal && item.state == null)
        .toList();

    return Scaffold(
      appBar: AppBar(
        title: const Row(
          children: [
            Logo(size: 30),
            SizedBox(width: 10),
            Text('Вместе к цели'),
          ],
        ),
        actions: [
          IconButton(
            tooltip: 'Как это работает',
            icon: const Icon(Icons.info_outline_rounded),
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => const HowItWorksPage()),
            ),
          ),
        ],
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
        padding: const EdgeInsets.fromLTRB(18, 4, 18, 112),
        children: [
          Text('Сегодня', style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 5),
          Text(app.hello, style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 18),
          if (app.goal == null) ...[
            CreateGoal(app: app),
            const SizedBox(height: 23),
            section('Другие дела на сегодня'),
          ] else ...[
            GoalHero(app: app),
            const SizedBox(height: 22),
            section('Действие для цели на сегодня'),
            const SizedBox(height: 9),
            if (goalAction == null)
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
            GoalSupportPanel(app: app, item: goalAction),
            const SizedBox(height: 23),
            section('Другие дела на сегодня'),
          ],
          const SizedBox(height: 9),
          if (otherActions.isEmpty)
            const Card(
              child: Padding(
                padding: EdgeInsets.all(18),
                child: Text('Других дел на сегодня пока нет.'),
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

class GoalSupportPanel extends StatelessWidget {
  const GoalSupportPanel({required this.app, required this.item, super.key});

  final AppState app;
  final ActionItem? item;

  Future<void> _open(BuildContext context, Support support) async {
    if (item == null) {
      await Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => ActionEditor(
            app: app,
            goalDefault: true,
            initialSupport: support,
          ),
        ),
      );
      return;
    }

    app.setSupport(item!, support);
    if (support == Support.together ||
        support == Support.report ||
        support == Support.curator) {
      await shareStartMessage(item!.title, item!.minutes, support);
    }
    if (!context.mounted) return;
    await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => Session(app: app, item: item!),
      ),
    );
  }

  @override
  Widget build(BuildContext context) => Card(
    color: const Color(0xFFF0F7F4),
    child: Padding(
      padding: const EdgeInsets.all(18),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Как хотите начать?',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900),
          ),
          const SizedBox(height: 6),
          Text(
            item == null
                ? 'Сначала выберите действие, а затем подходящую поддержку.'
                : 'Поддержку можно выбрать сразу — без дополнительного опроса.',
          ),
          const SizedBox(height: 13),
          _SupportButton(
            icon: Icons.people_alt_rounded,
            label: 'Начать вместе',
            onPressed: () => _open(context, Support.together),
          ),
          const SizedBox(height: 8),
          _SupportButton(
            icon: Icons.auto_awesome_rounded,
            label: 'С цифровым помощником',
            onPressed: () => _open(context, Support.ai),
          ),
          const SizedBox(height: 8),
          _SupportButton(
            icon: Icons.verified_user_outlined,
            label: 'С куратором',
            onPressed: () => _open(context, Support.curator),
          ),
        ],
      ),
    ),
  );
}

class _SupportButton extends StatelessWidget {
  const _SupportButton({
    required this.icon,
    required this.label,
    required this.onPressed,
  });

  final IconData icon;
  final String label;
  final VoidCallback onPressed;

  @override
  Widget build(BuildContext context) => SizedBox(
    width: double.infinity,
    child: OutlinedButton.icon(
      onPressed: onPressed,
      icon: Icon(icon),
      label: Text(label),
    ),
  );
}

class StartHelpCard extends StatelessWidget {
  const StartHelpCard({required this.app, super.key});
  final AppState app;

  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.all(22),
    decoration: BoxDecoration(
      gradient: const LinearGradient(
        colors: [Color(0xFF244F49), Color(0xFF4B7F73)],
      ),
      borderRadius: BorderRadius.circular(28),
      boxShadow: const [
        BoxShadow(
          color: Color(0x1A132D2A),
          blurRadius: 24,
          offset: Offset(0, 12),
        ),
      ],
    ),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Row(
          children: [
            Icon(Icons.bolt_rounded, color: mint),
            SizedBox(width: 8),
            Text(
              'КОГДА НЕ ПОЛУЧАЕТСЯ НАЧАТЬ',
              style: TextStyle(
                color: mint,
                fontSize: 12,
                fontWeight: FontWeight.w900,
                letterSpacing: 1.1,
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        const Text(
          'Есть дело, которое вы откладываете?',
          style: TextStyle(
            color: Colors.white,
            fontSize: 25,
            height: 1.15,
            fontWeight: FontWeight.w900,
          ),
        ),
        const SizedBox(height: 9),
        const Text(
          'Напишите, что нужно сделать, и выберите, почему вы не начинаете. Приложение предложит один конкретный способ начать.',
          style: TextStyle(color: Color(0xFFD8E5E1), fontSize: 16, height: 1.4),
        ),
        const SizedBox(height: 17),
        FilledButton.icon(
          style: FilledButton.styleFrom(
            backgroundColor: mint,
            foregroundColor: ink,
          ),
          onPressed: () => Navigator.push(
            context,
            MaterialPageRoute(builder: (_) => QuickStartWizard(app: app)),
          ),
          icon: const Icon(Icons.play_arrow_rounded),
          label: const Text('Разобраться, что мешает'),
        ),
      ],
    ),
  );
}

class QuickStartWizard extends StatefulWidget {
  const QuickStartWizard({required this.app, super.key});
  final AppState app;

  @override
  State<QuickStartWizard> createState() => _QuickStartWizardState();
}

class _QuickStartWizardState extends State<QuickStartWizard> {
  final title = TextEditingController();
  int stage = 0;
  int minutes = 10;
  StartProblem? problem;
  bool linked = false;

  @override
  void initState() {
    super.initState();
    title.addListener(() => setState(() {}));
  }

  @override
  void dispose() {
    title.dispose();
    super.dispose();
  }

  void next() {
    if (stage == 0 && title.text.trim().isNotEmpty) {
      setState(() => stage = 1);
    } else if (stage == 1 && problem != null) {
      setState(() => stage = 2);
    }
  }

  ActionItem makeItem(StartPlan plan) => ActionItem(
    id: DateTime.now().microsecondsSinceEpoch.toString(),
    title: title.text.trim(),
    small: plan.small,
    minutes: minutes,
    support: plan.support,
    goal: linked,
  );

  void startNow(StartPlan plan) {
    final item = makeItem(plan);
    widget.app.add(item);
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(
        builder: (_) => Session(app: widget.app, item: item),
      ),
    );
  }

  void saveForLater(StartPlan plan) {
    widget.app.add(makeItem(plan));
    Navigator.pop(context);
  }

  @override
  Widget build(BuildContext context) {
    final plan = problem == null
        ? null
        : StartPlan.forProblem(title.text, problem!);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Как начать это дело'),
        leading: IconButton(
          tooltip: 'Назад',
          icon: const Icon(Icons.arrow_back),
          onPressed: () {
            if (stage == 0) {
              Navigator.pop(context);
            } else {
              setState(() => stage--);
            }
          },
        ),
        actions: [
          IconButton(
            tooltip: 'Вернуться к делам',
            icon: const Icon(Icons.close_rounded),
            onPressed: () => Navigator.pop(context),
          ),
        ],
      ),
      body: AnimatedSwitcher(
        duration: const Duration(milliseconds: 220),
        child: stage == 0
            ? firstStage()
            : stage == 1
            ? problemStage()
            : planStage(plan!),
      ),
    );
  }

  Widget firstStage() => ListView(
    key: const ValueKey('quick-first'),
    padding: const EdgeInsets.all(18),
    children: [
      Text(
        'Какое дело вы откладываете?',
        style: Theme.of(context).textTheme.headlineMedium,
      ),
      const SizedBox(height: 8),
      const Text('Запишите одно конкретное дело.'),
      const SizedBox(height: 20),
      VoiceField(
        controller: title,
        label: 'Дело',
        hint: 'Например: написать текст для первого экрана сайта',
        lines: 3,
      ),
      const SizedBox(height: 18),
      FilledButton(
        onPressed: title.text.trim().isEmpty ? null : next,
        child: const Text('Дальше'),
      ),
      const SizedBox(height: 10),
      const Text(
        'Это может быть и обычное дело, не связанное с главной целью.',
        style: TextStyle(fontSize: 13, color: Colors.black54),
      ),
    ],
  );

  Widget problemStage() => ListView(
    key: const ValueKey('quick-problem'),
    padding: const EdgeInsets.all(18),
    children: [
      Text(
        'Почему вы не начинаете?',
        style: Theme.of(context).textTheme.headlineMedium,
      ),
      const SizedBox(height: 8),
      Text(
        'Дело: «${title.text.trim()}»',
        style: const TextStyle(color: Colors.black54),
      ),
      const SizedBox(height: 16),
      ...StartProblem.values.map(
        (value) => ProblemTile(
          problem: value,
          selected: problem == value,
          onTap: () => setState(() => problem = value),
        ),
      ),
      const SizedBox(height: 10),
      FilledButton(
        onPressed: problem == null ? null : next,
        child: const Text('Показать, что можно сделать'),
      ),
    ],
  );

  Widget planStage(StartPlan plan) => ListView(
    key: const ValueKey('quick-plan'),
    padding: const EdgeInsets.fromLTRB(18, 4, 18, 32),
    children: [
      Text(
        'Что можно сделать сейчас',
        style: Theme.of(context).textTheme.headlineMedium,
      ),
      const SizedBox(height: 8),
      Text('Дело: «${title.text.trim()}»'),
      const SizedBox(height: 18),
      Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: supportColor(plan.support),
          borderRadius: BorderRadius.circular(24),
          border: Border.all(color: green.withValues(alpha: .18)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(supportIcon(plan.support), color: ink),
                const SizedBox(width: 9),
                Expanded(
                  child: Text(
                    plan.heading,
                    style: const TextStyle(
                      fontSize: 19,
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Text(plan.explanation),
            const SizedBox(height: 16),
            const Text(
              'Сделайте сначала',
              style: TextStyle(fontWeight: FontWeight.w900),
            ),
            const SizedBox(height: 5),
            Text(plan.firstStep),
            const SizedBox(height: 14),
            const Text(
              'Если совсем нет сил',
              style: TextStyle(fontWeight: FontWeight.w900),
            ),
            const SizedBox(height: 5),
            Text(plan.small),
          ],
        ),
      ),
      if (plan.needsPerson) ...[
        const SizedBox(height: 12),
        OutlinedButton.icon(
          onPressed: () =>
              shareStartMessage(title.text.trim(), minutes, plan.support),
          icon: const Icon(Icons.send_rounded),
          label: Text(plan.shareButton),
        ),
      ],
      const SizedBox(height: 18),
      const Text(
        'Сколько времени вы готовы уделить сейчас?',
        style: TextStyle(fontSize: 17, fontWeight: FontWeight.w900),
      ),
      const SizedBox(height: 9),
      Wrap(
        spacing: 8,
        children: [5, 10, 15, 25]
            .map(
              (value) => ChoiceChip(
                label: Text('$value мин'),
                selected: minutes == value,
                onSelected: (_) => setState(() => minutes = value),
              ),
            )
            .toList(),
      ),
      if (widget.app.goal != null) ...[
        const SizedBox(height: 12),
        SwitchListTile.adaptive(
          contentPadding: EdgeInsets.zero,
          title: const Text(
            'Это действие для моей главной цели',
            style: TextStyle(fontWeight: FontWeight.w800),
          ),
          subtitle: Text(widget.app.goal!.title),
          value: linked,
          onChanged: (value) => setState(() => linked = value),
        ),
      ],
      const SizedBox(height: 16),
      FilledButton.icon(
        onPressed: () => startNow(plan),
        icon: const Icon(Icons.play_arrow_rounded),
        label: const Text('Начать сейчас'),
      ),
      const SizedBox(height: 9),
      TextButton(
        onPressed: () => saveForLater(plan),
        child: const Text('Добавить в дела на сегодня'),
      ),
    ],
  );
}

class ProblemTile extends StatelessWidget {
  const ProblemTile({
    required this.problem,
    required this.selected,
    required this.onTap,
    super.key,
  });

  final StartProblem problem;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.only(bottom: 9),
    child: InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(18),
      child: Container(
        padding: const EdgeInsets.all(15),
        decoration: BoxDecoration(
          color: selected ? mint : Colors.white,
          borderRadius: BorderRadius.circular(18),
          border: Border.all(
            color: selected ? green : const Color(0xFFE0DDD4),
            width: selected ? 1.5 : 1,
          ),
        ),
        child: Row(
          children: [
            Icon(problemIcon(problem), color: ink),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                problemName(problem),
                style: const TextStyle(fontWeight: FontWeight.w800),
              ),
            ),
            Icon(
              selected ? Icons.check_circle : Icons.radio_button_unchecked,
              color: selected ? green : Colors.black26,
            ),
          ],
        ),
      ),
    ),
  );
}

class StartPlan {
  const StartPlan({
    required this.support,
    required this.heading,
    required this.explanation,
    required this.firstStep,
    required this.small,
    required this.shareButton,
  });

  final Support support;
  final String heading;
  final String explanation;
  final String firstStep;
  final String small;
  final String shareButton;

  bool get needsPerson =>
      support == Support.together ||
      support == Support.report ||
      support == Support.curator;

  static StartPlan forProblem(String task, StartProblem problem) {
    final first = SupportLogic.steps(task).first;

    return switch (problem) {
      StartProblem.unclear => StartPlan(
        support: Support.ai,
        heading: 'Сначала уточните, что должно получиться',
        explanation:
            'Когда результат непонятен, трудно выбрать первое действие.',
        firstStep: first,
        small: SupportLogic.smallStep(task),
        shareButton: '',
      ),
      StartProblem.tooBig => StartPlan(
        support: Support.ai,
        heading: 'Выберите одну небольшую часть',
        explanation:
            'Не нужно выполнять всё дело сразу. Выберите часть, которую можно закончить за 10–15 минут.',
        firstStep: SupportLogic.smallPart(task),
        small: 'Потратьте на выбранную часть только 5 минут.',
        shareButton: '',
      ),
      StartProblem.noImpulse => const StartPlan(
        support: Support.together,
        heading: 'Начните одновременно с другим человеком',
        explanation:
            'Каждый может заниматься своим делом. Важно договориться об одном времени начала.',
        firstStep:
            'Отправьте знакомому сообщение и предложите начать одновременно.',
        small: 'Отправьте сообщение и начните сами хотя бы на 5 минут.',
        shareButton: 'Позвать человека',
      ),
      StartProblem.distracted => const StartPlan(
        support: Support.solo,
        heading: 'Уберите одно отвлечение и начните на 5 минут',
        explanation:
            'Не нужно обещать себе долгую работу. Сначала создайте пять спокойных минут.',
        firstStep:
            'Закройте лишнее приложение или уберите телефон подальше.',
        small: 'Сделайте только первые 5 минут дела.',
        shareButton: '',
      ),
      StartProblem.accountability => const StartPlan(
        support: Support.report,
        heading: 'Договоритесь, кому покажете результат',
        explanation:
            'Когда другой человек ждёт короткий итог, начать бывает легче.',
        firstStep:
            'Напишите знакомому, что начинаете и после дела отправите результат.',
        small: 'Отправьте итог даже после небольшой выполненной части.',
        shareButton: 'Сообщить о начале',
      ),
      StartProblem.reminder => const StartPlan(
        support: Support.curator,
        heading: 'Попросите знакомого напомнить',
        explanation:
            'Выберите человека и договоритесь, когда он напишет вам.',
        firstStep:
            'Отправьте просьбу и укажите точное время, когда нужно напомнить.',
        small: 'После напоминания начните хотя бы на 5 минут.',
        shareButton: 'Попросить напомнить',
      ),
    };
  }
}

String problemName(StartProblem problem) => switch (problem) {
  StartProblem.unclear => 'Не понимаю, с чего начать',
  StartProblem.tooBig => 'Дело кажется слишком большим',
  StartProblem.noImpulse => 'Понимаю, что делать, но всё равно откладываю',
  StartProblem.distracted => 'Постоянно отвлекаюсь',
  StartProblem.accountability =>
    'Мне легче, когда кто-то ждёт от меня результат',
  StartProblem.reminder => 'Без напоминания я снова отложу',
};

IconData problemIcon(StartProblem problem) => switch (problem) {
  StartProblem.unclear => Icons.question_mark_rounded,
  StartProblem.tooBig => Icons.account_tree_outlined,
  StartProblem.noImpulse => Icons.people_alt_outlined,
  StartProblem.distracted => Icons.notifications_off_outlined,
  StartProblem.accountability => Icons.verified_outlined,
  StartProblem.reminder => Icons.alarm_rounded,
};

class CreateGoal extends StatelessWidget {
  const CreateGoal({required this.app, super.key});
  final AppState app;

  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.all(23),
    decoration: BoxDecoration(
      gradient: const LinearGradient(colors: [ink, Color(0xFF35685F)]),
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
          'Чего вы хотите добиться?',
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
          style: TextStyle(color: Color(0xFFD7E2DF), fontSize: 16, height: 1.4),
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
          child: const Text('Добавить главную цель'),
        ),
      ],
    ),
  );
}

class GoalHero extends StatelessWidget {
  const GoalHero({required this.app, super.key});
  final AppState app;

  @override
  Widget build(BuildContext context) {
    final g = app.goal!;
    return Container(
      padding: const EdgeInsets.all(22),
      decoration: BoxDecoration(
        gradient: const LinearGradient(colors: [ink, Color(0xFF315F57)]),
        borderRadius: BorderRadius.circular(28),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'МОЯ ГЛАВНАЯ ЦЕЛЬ',
            style: TextStyle(
              color: mint,
              fontSize: 12,
              fontWeight: FontWeight.w900,
              letterSpacing: 1.1,
            ),
          ),
          const SizedBox(height: 12),
          Text(
            g.title,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 25,
              height: 1.15,
              fontWeight: FontWeight.w900,
            ),
          ),
          if (g.result.isNotEmpty) ...[
            const SizedBox(height: 8),
            Text(g.result, style: const TextStyle(color: Color(0xFFD4E0DD))),
          ],
          const SizedBox(height: 16),
          Row(
            children: [
              _metric('${app.goalDone}', 'сделано'),
              const SizedBox(width: 9),
              _metric('${g.minutes} мин', 'за один раз'),
              const SizedBox(width: 9),
              _metric('${g.areas.length}', 'частей цели'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _metric(String value, String label) => Expanded(
    child: Container(
      padding: const EdgeInsets.symmetric(vertical: 11, horizontal: 5),
      decoration: BoxDecoration(
        color: Colors.white10,
        borderRadius: BorderRadius.circular(15),
      ),
      child: Column(
        children: [
          Text(
            value,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 16,
              fontWeight: FontWeight.w900,
            ),
          ),
          Text(
            label,
            textAlign: TextAlign.center,
            style: const TextStyle(color: Colors.white60, fontSize: 11),
          ),
        ],
      ),
    ),
  );
}

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

class ActionCard extends StatelessWidget {
  const ActionCard({
    required this.app,
    required this.item,
    this.featured = false,
    super.key,
  });
  final AppState app;
  final ActionItem item;
  final bool featured;

  Future<void> _startTogether(BuildContext context) async {
    app.setSupport(item, Support.together);
    await shareStartMessage(item.title, item.minutes, Support.together);
    if (!context.mounted) return;
    await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => Session(app: app, item: item),
      ),
    );
  }

  @override
  Widget build(BuildContext context) => Card(
    color: featured ? const Color(0xFFFFFCF5) : Colors.white,
    child: Padding(
      padding: const EdgeInsets.all(17),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 42,
                height: 42,
                decoration: BoxDecoration(
                  color: supportColor(item.support),
                  borderRadius: BorderRadius.circular(14),
                ),
                child: Icon(
                  item.state == null ? supportIcon(item.support) : Icons.check,
                  color: ink,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      item.title,
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.w900,
                        decoration: item.state == null
                            ? null
                            : TextDecoration.lineThrough,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '${item.minutes} минут · ${supportName(item.support)}',
                    ),
                  ],
                ),
              ),
            ],
          ),
          if (item.small.isNotEmpty && item.state == null) ...[
            const SizedBox(height: 11),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: cream,
                borderRadius: BorderRadius.circular(14),
              ),
              child: Text('Если времени мало: ${item.small}'),
            ),
          ],
          const SizedBox(height: 13),
          if (item.state == null)
            Row(
              children: [
                Expanded(
                  child: FilledButton.icon(
                    onPressed: () => Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (_) => Session(app: app, item: item),
                      ),
                    ),
                    icon: const Icon(Icons.play_arrow),
                    label: const Text('Начать'),
                  ),
                ),
                const SizedBox(width: 9),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => _startTogether(context),
                    icon: const Icon(Icons.people_alt_outlined),
                    label: const Text('Вместе'),
                  ),
                ),
              ],
            )
          else
            Text(
              resultName(item.state!),
              style: const TextStyle(color: green, fontWeight: FontWeight.w900),
            ),
        ],
      ),
    ),
  );
}

class GoalScreen extends StatelessWidget {
  const GoalScreen({required this.app, super.key});
  final AppState app;

  @override
  Widget build(BuildContext context) {
    final activeAction = app.actions
        .where((item) => item.goal && item.state == null)
        .firstOrNull;

    return Scaffold(
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
              'Здесь видно, к какому результату вы идёте и что можно сделать сегодня.',
            ),
            const SizedBox(height: 18),
            GoalHero(app: app),
            const SizedBox(height: 13),
            GoalSupportPanel(app: app, item: activeAction),
            const SizedBox(height: 16),
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
            ),
            if (app.goal!.areas.isNotEmpty) ...[
              const SizedBox(height: 12),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(18),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Части цели',
                        style: TextStyle(
                          fontWeight: FontWeight.w900,
                          fontSize: 17,
                        ),
                      ),
                      const SizedBox(height: 9),
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
            ],
            const SizedBox(height: 14),
            FilledButton.icon(
              onPressed: () => Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => ActionEditor(app: app, goalDefault: true),
                ),
              ),
              icon: const Icon(Icons.add_task),
              label: Text(
                activeAction == null
                    ? 'Выбрать действие на сегодня'
                    : 'Добавить другое действие',
              ),
            ),
            const SizedBox(height: 10),
            OutlinedButton.icon(
              onPressed: () => Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => GoalEditor(app: app, existing: app.goal),
                ),
              ),
              icon: const Icon(Icons.edit_outlined),
              label: const Text('Изменить цель'),
            ),
          ],
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
  late final TextEditingController areas;
  int minutes = 20;
  bool showDetails = false;

  @override
  void initState() {
    super.initState();
    title = TextEditingController(text: widget.existing?.title ?? '');
    result = TextEditingController(text: widget.existing?.result ?? '');
    areas = TextEditingController(
      text: widget.existing?.areas.join(', ') ?? '',
    );
    minutes = widget.existing?.minutes ?? 20;
    showDetails = widget.existing != null && widget.existing!.areas.isNotEmpty;
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
        minutes,
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
          'Сначала достаточно назвать цель. Подробности можно добавить позже.',
        ),
        const SizedBox(height: 18),
        VoiceField(
          controller: title,
          label: 'Моя цель',
          hint: 'Например: навести порядок в доме и закончить ремонт',
          lines: 3,
        ),
        const SizedBox(height: 13),
        VoiceField(
          controller: result,
          label: 'Как вы поймёте, что цель достигнута? Необязательно',
          hint: 'Например: все незаконченные работы выполнены',
          lines: 3,
        ),
        const SizedBox(height: 8),
        TextButton.icon(
          onPressed: () => setState(() => showDetails = !showDetails),
          icon: Icon(showDetails ? Icons.expand_less : Icons.tune_rounded),
          label: Text(
            showDetails ? 'Скрыть подробности' : 'Добавить подробности',
          ),
        ),
        if (showDetails) ...[
          const SizedBox(height: 8),
          VoiceField(
            controller: areas,
            label: 'На какие части можно разделить цель?',
            hint: 'Например: кухня, документы, ремонт, вещи без места',
            lines: 3,
          ),
          const SizedBox(height: 18),
          const Text(
            'Сколько времени удобно выделять за один раз?',
            style: TextStyle(fontWeight: FontWeight.w900, fontSize: 17),
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
}

class ActionEditor extends StatefulWidget {
  const ActionEditor({
    required this.app,
    required this.goalDefault,
    this.initialSupport,
    super.key,
  });
  final AppState app;
  final bool goalDefault;
  final Support? initialSupport;
  @override
  State<ActionEditor> createState() => _ActionEditorState();
}

class _ActionEditorState extends State<ActionEditor> {
  final title = TextEditingController(), small = TextEditingController();
  int minutes = 15;
  late bool linked;
  Support? chosen;
  bool showMoreSupport = false;
  bool showSmall = false;

  @override
  void initState() {
    super.initState();
    linked = widget.goalDefault && widget.app.goal != null;
    chosen = widget.initialSupport;
    showMoreSupport =
        chosen != null && chosen != Support.solo && chosen != Support.together;
    title.addListener(() => setState(() {}));
  }

  @override
  void dispose() {
    title.dispose();
    small.dispose();
    super.dispose();
  }

  Future<void> createAndStart(Support support) async {
    final action = ActionItem(
      id: DateTime.now().microsecondsSinceEpoch.toString(),
      title: title.text.trim(),
      small: small.text.trim(),
      minutes: minutes,
      support: support,
      goal: linked,
    );
    widget.app.add(action);

    if (support == Support.together ||
        support == Support.report ||
        support == Support.curator) {
      await shareStartMessage(action.title, action.minutes, support);
    }
    if (!mounted) return;
    await Navigator.pushReplacement(
      context,
      MaterialPageRoute(
        builder: (_) => Session(app: widget.app, item: action),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final recommended = SupportLogic.recommend(title.text);
    final support = chosen ?? recommended.$1;

    return Scaffold(
      appBar: AppBar(title: const Text('Действие на сегодня')),
      body: ListView(
        padding: const EdgeInsets.all(18),
        children: [
          Text(
            'Что вы сделаете сегодня?',
            style: Theme.of(context).textTheme.headlineMedium,
          ),
          if (linked && widget.app.goal != null) ...[
            const SizedBox(height: 7),
            Text(
              'Для цели: ${widget.app.goal!.title}',
              style: const TextStyle(color: Colors.black54),
            ),
          ],
          const SizedBox(height: 17),
          VoiceField(
            controller: title,
            label: 'Конкретное действие',
            hint: 'Например: закрепить полку в ванной',
            lines: 3,
          ),
          const SizedBox(height: 15),
          const Text(
            'Сколько времени вы готовы уделить?',
            style: TextStyle(fontWeight: FontWeight.w900, fontSize: 17),
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            children: [5, 10, 15, 25, 40]
                .map(
                  (value) => ChoiceChip(
                    label: Text('$value мин'),
                    selected: minutes == value,
                    onSelected: (_) => setState(() => minutes = value),
                  ),
                )
                .toList(),
          ),
          const SizedBox(height: 20),
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
          ],
          TextButton.icon(
            onPressed: () => setState(() => showSmall = !showSmall),
            icon: Icon(showSmall ? Icons.expand_less : Icons.compress_rounded),
            label: Text(
              showSmall
                  ? 'Скрыть сокращённый вариант'
                  : 'Добавить вариант на случай нехватки времени',
            ),
          ),
          if (showSmall) ...[
            const SizedBox(height: 6),
            VoiceField(
              controller: small,
              label: 'Что можно сделать хотя бы частично?',
              hint: 'Например: только подготовить инструменты',
              lines: 3,
            ),
          ],
          if (!widget.goalDefault && widget.app.goal != null) ...[
            const SizedBox(height: 8),
            SwitchListTile.adaptive(
              contentPadding: EdgeInsets.zero,
              title: const Text(
                'Это действие относится к главной цели',
                style: TextStyle(fontWeight: FontWeight.w800),
              ),
              subtitle: Text(widget.app.goal!.title),
              value: linked,
              onChanged: (value) => setState(() => linked = value),
            ),
          ],
          const SizedBox(height: 18),
          FilledButton.icon(
            onPressed: title.text.trim().isEmpty
                ? null
                : () => createAndStart(support),
            icon: Icon(
              support == Support.together
                  ? Icons.people_alt_rounded
                  : Icons.play_arrow_rounded,
            ),
            label: Text(
              support == Support.together
                  ? 'Позвать человека и начать'
                  : 'Начать',
            ),
          ),
        ],
      ),
    );
  }
}

class Speech {
  Speech._();
  static final i = Speech._();
  final engine = stt.SpeechToText();
  bool ready = false;
  Future<bool> init() async {
    if (ready) return true;
    ready = await engine.initialize();
    return ready;
  }
}

class VoiceField extends StatefulWidget {
  const VoiceField({
    required this.controller,
    required this.label,
    required this.hint,
    this.lines = 1,
    super.key,
  });
  final TextEditingController controller;
  final String label, hint;
  final int lines;
  @override
  State<VoiceField> createState() => _VoiceFieldState();
}

class _VoiceFieldState extends State<VoiceField> {
  bool listening = false;
  Future<void> mic() async {
    if (listening) {
      await Speech.i.engine.stop();
      setState(() => listening = false);
      return;
    }
    if (!await Speech.i.init()) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text(
              'Голосовой ввод недоступен. Проверьте разрешение микрофона.',
            ),
          ),
        );
      }
      return;
    }
    setState(() => listening = true);
    await Speech.i.engine.listen(
      listenOptions: stt.SpeechListenOptions(localeId: 'ru_RU'),
      onResult: (r) {
        widget.controller.text = r.recognizedWords;
        widget.controller.selection = TextSelection.collapsed(
          offset: widget.controller.text.length,
        );
        if (r.finalResult && mounted) setState(() => listening = false);
      },
    );
  }

  @override
  Widget build(BuildContext context) => TextField(
    controller: widget.controller,
    maxLines: widget.lines,
    decoration: InputDecoration(
      labelText: widget.label,
      hintText: widget.hint,
      suffixIcon: IconButton(
        onPressed: mic,
        icon: Icon(listening ? Icons.mic : Icons.mic_none),
        color: listening ? Colors.red : green,
        tooltip: 'Продиктовать',
      ),
    ),
  );
}

class SupportTile extends StatelessWidget {
  const SupportTile({
    required this.type,
    required this.selected,
    required this.onTap,
    super.key,
  });
  final Support type;
  final bool selected;
  final VoidCallback onTap;
  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.only(bottom: 8),
    child: InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(17),
      child: Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: selected ? supportColor(type) : Colors.white,
          borderRadius: BorderRadius.circular(17),
          border: Border.all(
            color: selected ? green : const Color(0xFFE0DDD4),
            width: selected ? 1.5 : 1,
          ),
        ),
        child: Row(
          children: [
            Icon(supportIcon(type), color: ink),
            const SizedBox(width: 11),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    supportName(type),
                    style: const TextStyle(fontWeight: FontWeight.w900),
                  ),
                  Text(
                    supportShort(type),
                    style: const TextStyle(fontSize: 13),
                  ),
                ],
              ),
            ),
            Icon(
              selected ? Icons.check_circle : Icons.radio_button_unchecked,
              color: selected ? green : Colors.black26,
            ),
          ],
        ),
      ),
    ),
  );
}

class SupportScreen extends StatelessWidget {
  const SupportScreen({required this.app, super.key});
  final AppState app;

  @override
  Widget build(BuildContext context) {
    final active = app.actions.where((item) => item.state == null).toList();

    return Scaffold(
      appBar: AppBar(title: const Text('Вместе')),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(18, 4, 18, 90),
        children: [
          Container(
            padding: const EdgeInsets.all(22),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF244F49), Color(0xFF4B7F73)],
              ),
              borderRadius: BorderRadius.circular(28),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(Icons.people_alt_rounded, color: mint, size: 36),
                const SizedBox(height: 12),
                const Text(
                  'Начать вместе',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 28,
                    height: 1.1,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                const SizedBox(height: 9),
                const Text(
                  'Вы и другой человек начинаете в одно время. Можно делать одно и то же или заниматься разными делами.',
                  style: TextStyle(
                    color: Color(0xFFD8E5E1),
                    fontSize: 16,
                    height: 1.4,
                  ),
                ),
                const SizedBox(height: 17),
                if (active.isEmpty)
                  FilledButton.icon(
                    style: FilledButton.styleFrom(
                      backgroundColor: mint,
                      foregroundColor: ink,
                    ),
                    onPressed: () => Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (_) => ActionEditor(
                          app: app,
                          goalDefault: app.goal != null,
                          initialSupport: Support.together,
                        ),
                      ),
                    ),
                    icon: const Icon(Icons.add_task_rounded),
                    label: const Text('Выбрать действие'),
                  )
                else
                  const Text(
                    'Выберите действие ниже и отправьте приглашение через привычный мессенджер.',
                    style: TextStyle(color: Colors.white),
                  ),
              ],
            ),
          ),
          const SizedBox(height: 20),
          if (active.isNotEmpty) ...[
            Text(
              'Что будете делать?',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 9),
            ...active.map(
              (item) => Padding(
                padding: const EdgeInsets.only(bottom: 9),
                child: TogetherActionCard(app: app, item: item),
              ),
            ),
          ],
          const SizedBox(height: 20),
          Text(
            'Другие способы поддержки',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: 9),
          _SimpleSupportCard(
            type: Support.ai,
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => ActionEditor(
                  app: app,
                  goalDefault: app.goal != null,
                  initialSupport: Support.ai,
                ),
              ),
            ),
          ),
          _SimpleSupportCard(
            type: Support.report,
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => ActionEditor(
                  app: app,
                  goalDefault: app.goal != null,
                  initialSupport: Support.report,
                ),
              ),
            ),
          ),
          _SimpleSupportCard(
            type: Support.curator,
            onPressed: () => showModalBottomSheet(
              context: context,
              isScrollControlled: true,
              showDragHandle: true,
              builder: (_) => CuratorSheet(app: app),
            ),
          ),
        ],
      ),
    );
  }
}

class TogetherActionCard extends StatelessWidget {
  const TogetherActionCard({required this.app, required this.item, super.key});

  final AppState app;
  final ActionItem item;

  Future<void> start(BuildContext context) async {
    app.setSupport(item, Support.together);
    await shareStartMessage(item.title, item.minutes, Support.together);
    if (!context.mounted) return;
    await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => Session(app: app, item: item),
      ),
    );
  }

  @override
  Widget build(BuildContext context) => Card(
    child: Padding(
      padding: const EdgeInsets.all(17),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            item.title,
            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w900),
          ),
          const SizedBox(height: 5),
          Text('${item.minutes} минут'),
          const SizedBox(height: 12),
          FilledButton.icon(
            onPressed: () => start(context),
            icon: const Icon(Icons.send_rounded),
            label: const Text('Позвать человека и начать'),
          ),
        ],
      ),
    ),
  );
}

class _SimpleSupportCard extends StatelessWidget {
  const _SimpleSupportCard({required this.type, required this.onPressed});

  final Support type;
  final VoidCallback onPressed;

  @override
  Widget build(BuildContext context) => Card(
    margin: const EdgeInsets.only(bottom: 9),
    child: ListTile(
      contentPadding: const EdgeInsets.all(14),
      leading: Container(
        width: 44,
        height: 44,
        decoration: BoxDecoration(
          color: supportColor(type),
          borderRadius: BorderRadius.circular(14),
        ),
        child: Icon(supportIcon(type), color: ink),
      ),
      title: Text(
        supportName(type),
        style: const TextStyle(fontWeight: FontWeight.w900),
      ),
      subtitle: Text(supportShort(type)),
      trailing: const Icon(Icons.chevron_right_rounded),
      onTap: onPressed,
    ),
  );
}

class CuratorSheet extends StatefulWidget {
  const CuratorSheet({required this.app, super.key});
  final AppState app;
  @override
  State<CuratorSheet> createState() => _CuratorSheetState();
}

class _CuratorSheetState extends State<CuratorSheet> {
  late final TextEditingController name;
  @override
  void initState() {
    super.initState();
    name = TextEditingController(text: widget.app.curator);
    name.addListener(() => setState(() {}));
  }

  @override
  void dispose() {
    name.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => Padding(
    padding: EdgeInsets.fromLTRB(
      18,
      4,
      18,
      MediaQuery.of(context).viewInsets.bottom + 22,
    ),
    child: Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Куратор',
          style: TextStyle(fontSize: 24, fontWeight: FontWeight.w900),
        ),
        const SizedBox(height: 7),
        const Text(
          'Выберите знакомого, который согласен напоминать и спрашивать о результате. Куратор не контролирует вас: его задача — напомнить и поддержать.',
        ),
        const SizedBox(height: 15),
        VoiceField(
          controller: name,
          label: 'Имя куратора',
          hint: 'Например: Андрей',
        ),
        const SizedBox(height: 15),
        FilledButton(
          onPressed: name.text.trim().isEmpty
              ? null
              : () {
                  widget.app.setCurator(name.text);
                  Navigator.pop(context);
                },
          child: const Text('Сохранить'),
        ),
        const SizedBox(height: 7),
        const Text(
          'Пока приложение не отправляет сообщения автоматически. Связаться с куратором можно через привычный мессенджер.',
          style: TextStyle(fontSize: 12, color: Colors.black54),
        ),
      ],
    ),
  );
}

class Progress extends StatelessWidget {
  const Progress({required this.app, super.key});
  final AppState app;
  @override
  Widget build(BuildContext context) {
    final done = app.history.where((e) => e.state == ResultState.done).length;
    final part = app.history.where((e) => e.state == ResultState.part).length;
    final stops = app.history
        .where(
          (e) => e.state == ResultState.moved || e.state == ResultState.missed,
        )
        .length;
    return Scaffold(
      appBar: AppBar(title: const Text('История')),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(18, 4, 18, 90),
        children: [
          Text(
            'Что уже сделано',
            style: Theme.of(context).textTheme.headlineMedium,
          ),
          const SizedBox(height: 7),
          const Text(
            'Здесь сохраняются выполненные действия, частичные результаты и переносы.',
          ),
          const SizedBox(height: 18),
          Row(
            children: [
              stat('$done', 'выполнено'),
              const SizedBox(width: 8),
              stat('$part', 'частично'),
              const SizedBox(width: 8),
              stat('$stops', 'перенесено'),
            ],
          ),
          const SizedBox(height: 20),
          const Text(
            'История действий',
            style: TextStyle(fontWeight: FontWeight.w900, fontSize: 20),
          ),
          const SizedBox(height: 9),
          if (app.history.isEmpty)
            const Card(
              child: Padding(
                padding: EdgeInsets.all(18),
                child: Text(
                  'После первого действия здесь появятся его результат и выбранный способ помощи.',
                ),
              ),
            )
          else
            ...app.history.map(
              (e) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Card(
                  child: ListTile(
                    leading: CircleAvatar(
                      backgroundColor: supportColor(e.support),
                      child: Icon(supportIcon(e.support), color: ink),
                    ),
                    title: Text(
                      e.title,
                      style: const TextStyle(fontWeight: FontWeight.w800),
                    ),
                    subtitle: Text(
                      '${supportName(e.support)} · ${e.minutes} минут · ${e.date.day}.${e.date.month}.${e.date.year}',
                    ),
                    trailing: Icon(resultIcon(e.state), color: green),
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget stat(String value, String label) => Expanded(
    child: Container(
      padding: const EdgeInsets.symmetric(vertical: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(19),
      ),
      child: Column(
        children: [
          Text(
            value,
            style: const TextStyle(fontSize: 24, fontWeight: FontWeight.w900),
          ),
          Text(label, style: const TextStyle(fontSize: 11)),
        ],
      ),
    ),
  );
}

class Session extends StatefulWidget {
  const Session({required this.app, required this.item, super.key});
  final AppState app;
  final ActionItem item;

  @override
  State<Session> createState() => _SessionState();
}

class _SessionState extends State<Session> {
  Timer? timer;
  bool started = false;
  bool paused = false;
  late int left;
  int step = 0;

  @override
  void initState() {
    super.initState();
    left = widget.item.minutes * 60;
  }

  @override
  void dispose() {
    timer?.cancel();
    super.dispose();
  }

  void start() {
    setState(() => started = true);
    timer = Timer.periodic(const Duration(seconds: 1), (_) {
      if (!paused && left > 0 && mounted) {
        setState(() => left--);
      }
    });
  }

  void finish(ResultState state) {
    timer?.cancel();
    widget.app.complete(widget.item, state);
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(
        builder: (_) => ResultPage(item: widget.item, state: state),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final steps = SupportLogic.steps(widget.item.title);
    final social =
        widget.item.support == Support.together ||
        widget.item.support == Support.report ||
        widget.item.support == Support.curator;

    return Scaffold(
      appBar: AppBar(title: const Text('Текущее действие')),
      body: ListView(
        padding: const EdgeInsets.all(18),
        children: [
          Container(
            padding: const EdgeInsets.all(21),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [ink, supportAccent(widget.item.support)],
              ),
              borderRadius: BorderRadius.circular(27),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(supportIcon(widget.item.support), color: mint),
                    const SizedBox(width: 8),
                    Text(
                      supportName(widget.item.support).toUpperCase(),
                      style: const TextStyle(
                        color: mint,
                        fontSize: 12,
                        fontWeight: FontWeight.w900,
                        letterSpacing: 1,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 13),
                Text(
                  widget.item.title,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 27,
                    height: 1.15,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  sessionMessage(widget.item.support, widget.app),
                  style: const TextStyle(color: Color(0xFFD4E0DD), height: 1.4),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          if (widget.item.support == Support.ai)
            Card(
              child: Padding(
                padding: const EdgeInsets.all(18),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'С чего начать',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                    const SizedBox(height: 12),
                    ...steps.asMap().entries.map(
                      (entry) => InkWell(
                        onTap: () => setState(() => step = entry.key),
                        child: Padding(
                          padding: const EdgeInsets.only(bottom: 10),
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Icon(
                                step == entry.key
                                    ? Icons.play_circle
                                    : step > entry.key
                                    ? Icons.check_circle
                                    : Icons.radio_button_unchecked,
                                color: step == entry.key
                                    ? green
                                    : Colors.black26,
                              ),
                              const SizedBox(width: 9),
                              Expanded(
                                child: Text(
                                  entry.value,
                                  style: TextStyle(
                                    fontWeight: step == entry.key
                                        ? FontWeight.w800
                                        : FontWeight.w500,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                    if (started && step < steps.length - 1)
                      TextButton(
                        onPressed: () => setState(() => step++),
                        child: const Text('Следующий шаг'),
                      ),
                  ],
                ),
              ),
            ),
          if (social && !started) ...[
            OutlinedButton.icon(
              onPressed: () => shareStartMessage(
                widget.item.title,
                widget.item.minutes,
                widget.item.support,
              ),
              icon: const Icon(Icons.send_rounded),
              label: Text(shareStartButton(widget.item.support)),
            ),
            const SizedBox(height: 12),
          ],
          if (!started) ...[
            Card(
              child: Padding(
                padding: const EdgeInsets.all(18),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Перед началом',
                      style: TextStyle(
                        fontWeight: FontWeight.w900,
                        fontSize: 18,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(preStart(widget.item.support)),
                    if (widget.item.small.isNotEmpty) ...[
                      const SizedBox(height: 10),
                      Text(
                        'Если сегодня трудно, достаточно: ${widget.item.small}',
                        style: const TextStyle(fontWeight: FontWeight.w800),
                      ),
                    ],
                  ],
                ),
              ),
            ),
            const SizedBox(height: 15),
            FilledButton.icon(
              onPressed: start,
              icon: const Icon(Icons.play_arrow),
              label: Text('Начать на ${widget.item.minutes} минут'),
            ),
          ] else ...[
            Center(
              child: Column(
                children: [
                  Text(
                    '${(left ~/ 60).toString().padLeft(2, '0')}:${(left % 60).toString().padLeft(2, '0')}',
                    style: const TextStyle(
                      fontSize: 60,
                      fontWeight: FontWeight.w900,
                      color: ink,
                    ),
                  ),
                  Text(
                    paused ? 'Пауза' : 'Вы уже начали',
                    style: const TextStyle(
                      color: green,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 18),
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
                    onPressed: () => showModalBottomSheet(
                      context: context,
                      showDragHandle: true,
                      builder: (_) => Blocker(item: widget.item),
                    ),
                    icon: const Icon(Icons.support),
                    label: const Text('Мне трудно'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            FilledButton.icon(
              onPressed: () => showModalBottomSheet(
                context: context,
                showDragHandle: true,
                builder: (_) => Finish(onFinish: finish),
              ),
              icon: const Icon(Icons.check),
              label: const Text('Закончить и записать результат'),
            ),
          ],
        ],
      ),
    );
  }
}

class Blocker extends StatelessWidget {
  const Blocker({required this.item, super.key});
  final ActionItem item;
  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.fromLTRB(18, 2, 18, 24),
    child: Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Что мешает продолжить?',
          style: TextStyle(fontSize: 23, fontWeight: FontWeight.w900),
        ),
        const SizedBox(height: 6),
        const Text('Выберите, что мешает именно сейчас.'),
        const SizedBox(height: 12),
        ...SupportLogic.blockers(item.title).map(
          (e) => ListTile(
            contentPadding: EdgeInsets.zero,
            leading: const Icon(Icons.arrow_forward, color: green),
            title: Text(e),
            onTap: () {
              Navigator.pop(context);
              ScaffoldMessenger.of(
                context,
              ).showSnackBar(SnackBar(content: Text(e)));
            },
          ),
        ),
        if (item.small.isNotEmpty)
          FilledButton.tonal(
            onPressed: () {
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text('Сейчас достаточно: ${item.small}')),
              );
            },
            child: const Text('Перейти к небольшому варианту'),
          ),
      ],
    ),
  );
}

class Finish extends StatelessWidget {
  const Finish({required this.onFinish, super.key});
  final ValueChanged<ResultState> onFinish;
  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.fromLTRB(18, 2, 18, 24),
    child: Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Что получилось?',
          style: TextStyle(fontSize: 23, fontWeight: FontWeight.w900),
        ),
        opt('Действие выполнено', Icons.check_circle, ResultState.done),
        opt('Сделана важная часть', Icons.timelapse, ResultState.part),
        opt('Отложить на потом', Icons.event_repeat, ResultState.moved),
        opt(
          'Сегодня не получилось',
          Icons.remove_circle_outline,
          ResultState.missed,
        ),
      ],
    ),
  );
  Widget opt(String t, IconData i, ResultState s) => ListTile(
    contentPadding: EdgeInsets.zero,
    leading: Icon(i, color: green),
    title: Text(t, style: const TextStyle(fontWeight: FontWeight.w800)),
    trailing: const Icon(Icons.chevron_right),
    onTap: () => onFinish(s),
  );
}

class ResultPage extends StatelessWidget {
  const ResultPage({required this.item, required this.state, super.key});

  final ActionItem item;
  final ResultState state;

  @override
  Widget build(BuildContext context) {
    final ok = state == ResultState.done || state == ResultState.part;
    final canShare =
        item.support == Support.together ||
        item.support == Support.report ||
        item.support == Support.curator;

    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 72,
                height: 72,
                decoration: BoxDecoration(
                  color: ok ? mint : const Color(0xFFE7E1D5),
                  borderRadius: BorderRadius.circular(23),
                ),
                child: Icon(
                  ok ? Icons.check : Icons.refresh,
                  size: 39,
                  color: ink,
                ),
              ),
              const SizedBox(height: 25),
              Text(
                ok
                    ? 'Вы начали и получили результат.'
                    : 'Сегодня не получилось — дело сохранено.',
                style: Theme.of(context).textTheme.headlineLarge,
              ),
              const SizedBox(height: 12),
              Text(
                ok
                    ? 'Результат по делу «${item.title}» записан в истории.'
                    : 'Можно выбрать другое время, уменьшить задачу или попросить человека напомнить.',
              ),
              if (canShare && ok) ...[
                const SizedBox(height: 18),
                OutlinedButton.icon(
                  onPressed: () => shareResultMessage(item, state),
                  icon: const Icon(Icons.send_rounded),
                  label: const Text('Отправить результат'),
                ),
              ],
              const SizedBox(height: 14),
              FilledButton(
                onPressed: () =>
                    Navigator.popUntil(context, (route) => route.isFirst),
                child: const Text('Вернуться к делам на сегодня'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

Future<void> shareStartMessage(
  String title,
  int minutes,
  Support support,
) async {
  final text = switch (support) {
    Support.together =>
      'Начнём одновременно? Я начинаю дело «$title» на $minutes минут. Каждый может заниматься своим делом.',
    Support.report =>
      'Я начинаю дело «$title» на $minutes минут. Когда закончу, отправлю короткий результат.',
    Support.curator =>
      'Я хочу начать дело «$title» на $minutes минут. Напомни мне об этом и спроси потом, что получилось.',
    _ => 'Я начинаю дело «$title» на $minutes минут.',
  };

  await SharePlus.instance.share(
    ShareParams(text: text, subject: 'Вместе к цели'),
  );
}

Future<void> shareResultMessage(ActionItem item, ResultState state) async {
  final result = switch (state) {
    ResultState.done => 'выполнено',
    ResultState.part => 'сделана важная часть',
    ResultState.moved => 'перенесено',
    ResultState.missed => 'сегодня не получилось',
  };

  await SharePlus.instance.share(
    ShareParams(
      text:
          'Результат по делу «${item.title}»: $result. Время: ${item.minutes} минут.',
      subject: 'Результат — Вместе к цели',
    ),
  );
}

String shareStartButton(Support support) => switch (support) {
  Support.together => 'Позвать начать вместе',
  Support.report => 'Сообщить, что вы начинаете',
  Support.curator => 'Попросить напомнить',
  _ => 'Поделиться',
};

class SupportLogic {
  static String n(String value) => value.toLowerCase().replaceAll('ё', 'е');

  static bool has(String value, List<String> words) =>
      words.any(value.contains);

  static (Support, String) recommend(String task) {
    final normalized = n(task);

    if (normalized.trim().isEmpty) {
      return (
        Support.ai,
        'После описания действия рекомендация станет точнее.',
      );
    }
    if (has(normalized, ['заряд', 'тренир', 'подтяг', 'бег', 'спорт'])) {
      return (
        Support.together,
        'Физические действия часто легче сохранять при одновременном старте или обмене результатами.',
      );
    }
    if (has(normalized, ['доход', 'заработ', 'клиент', 'продаж'])) {
      return (
        Support.curator,
        'Для долгой финансовой цели полезна регулярная подотчётность по конкретным действиям.',
      );
    }
    if (has(normalized, [
      'сайт',
      'страниц',
      'код',
      'приложен',
      'книга',
      'проект',
    ])) {
      return (
        Support.ai,
        'Сложную работу полезно сначала разложить на ближайшие понятные действия.',
      );
    }
    if (has(normalized, ['убрать комнат', 'уборк', 'порядок'])) {
      return (
        Support.together,
        'Простую уборку можно выполнять параллельно и подтвердить результат.',
      );
    }
    if (has(normalized, ['ремонт', 'почин', 'закреп', 'прикрут'])) {
      return (
        Support.ai,
        'Ремонт чаще выполняется самостоятельно, но выигрывает от подготовки и последовательности.',
      );
    }
    if (has(normalized, ['позвон', 'забрать', 'купить', 'оплатить'])) {
      return (
        Support.solo,
        'Здесь обычно достаточно точного напоминания и ясного результата.',
      );
    }

    return (
      Support.ai,
      'Цифровой помощник предложит один понятный первый шаг.',
    );
  }

  static List<String> steps(String task) {
    final normalized = n(task);

    if (has(normalized, ['убир', 'комнат', 'вещ', 'порядок', 'шкаф'])) {
      return [
        'Выберите одну конкретную зону, а не всё помещение.',
        'Подготовьте пакет для мусора и место для вещей без постоянного места.',
        'Начните с пяти предметов, решение по которым очевидно.',
      ];
    }
    if (has(normalized, ['ремонт', 'почин', 'закреп', 'прикрут'])) {
      return [
        'Назовите видимый результат работы.',
        'Соберите инструменты и материалы в одной точке.',
        'Сделайте первый необратимый шаг: снять, очистить или разметить.',
      ];
    }
    if (has(normalized, ['сайт', 'страниц', 'код', 'приложен'])) {
      return [
        'Откройте нужный проект или страницу.',
        'Определите один готовый результат этой сессии.',
        'Сделайте первый самостоятельный блок, не редактируя всё сразу.',
      ];
    }
    if (has(normalized, ['заряд', 'тренир', 'спорт', 'подтяг'])) {
      return [
        'Подготовьте место и всё необходимое.',
        'Начните с короткой разминки или первого лёгкого подхода.',
        'Зафиксируйте повторения, время или другой результат.',
      ];
    }
    if (has(normalized, ['доход', 'заработ', 'клиент'])) {
      return [
        'Выберите действие, которое может привести к доходу.',
        'Определите объём: один звонок, три предложения или готовый блок.',
        'После выполнения отправьте короткий отчёт.',
      ];
    }

    return [
      'Запишите, что должно быть готово в конце этого дела.',
      'Выберите первое действие, которое можно выполнить без подготовки.',
      'Начните с него и пока не планируйте остальное.',
    ];
  }

  static String smallStep(String task) {
    final normalized = n(task);
    if (has(normalized, ['убир', 'комнат', 'вещ', 'порядок', 'шкаф'])) {
      return 'Уберите только пять предметов.';
    }
    if (has(normalized, ['ремонт', 'почин', 'закреп', 'прикрут'])) {
      return 'Принесите один нужный инструмент.';
    }
    if (has(normalized, ['сайт', 'страниц', 'код', 'приложен'])) {
      return 'Откройте нужную страницу или проект.';
    }
    if (has(normalized, ['заряд', 'тренир', 'спорт', 'подтяг'])) {
      return 'Переоденьтесь и сделайте короткую разминку.';
    }
    if (has(normalized, ['доход', 'заработ', 'клиент'])) {
      return 'Запишите одно действие, которое может привести к доходу.';
    }
    return 'Откройте нужное место, файл или материал.';
  }

  static String smallPart(String task) {
    final normalized = n(task);
    if (has(normalized, ['убир', 'комнат', 'вещ', 'порядок', 'шкаф'])) {
      return 'Выберите одну полку, ящик или небольшой участок.';
    }
    if (has(normalized, ['ремонт', 'почин', 'закреп', 'прикрут'])) {
      return 'Сделайте только подготовку: осмотрите место и соберите инструменты.';
    }
    if (has(normalized, ['сайт', 'страниц', 'код', 'приложен'])) {
      return 'Сделайте только один блок страницы.';
    }
    if (has(normalized, ['заряд', 'тренир', 'спорт', 'подтяг'])) {
      return 'Выполните только разминку или один подход.';
    }
    if (has(normalized, ['доход', 'заработ', 'клиент'])) {
      return 'Сделайте один звонок, одно письмо или одно предложение.';
    }
    return 'Выберите одну часть, которую можно закончить за 10 минут.';
  }

  static List<String> blockers(String task) {
    final first = steps(task).first;
    return [
      'Неясно, с чего начать — попробуйте: «$first»',
      'Действие слишком большое — сократите его до первой завершённой части.',
      'Не хватает предмета или информации — запишите, что нужно получить.',
      'Отвлекают другие дела — запишите их одной строкой и вернитесь к текущему.',
    ];
  }
}

String supportName(Support s) => switch (s) {
  Support.solo => 'Самостоятельно',
  Support.ai => 'С цифровым помощником',
  Support.together => 'Начать вместе',
  Support.report => 'Отправить результат',
  Support.curator => 'С куратором',
};
String supportShort(Support s) => switch (s) {
  Support.solo =>
    'Запустить таймер и сохранить результат без участия других людей.',
  Support.ai => 'Помощник предложит первый шаг и короткий план.',
  Support.together =>
    'Вы и другой человек начинаете одновременно. Делать можно разные дела.',
  Support.report =>
    'После дела отправить знакомому фото, видео или короткий итог.',
  Support.curator =>
    'Знакомый напоминает, спрашивает о результате и поддерживает.',
};
String supportLong(Support s) => switch (s) {
  Support.solo =>
    'Для звонков, ремонта, конфиденциальных и коротких задач, где общение только отвлекает.',
  Support.ai =>
    'Помогает разложить сложное действие, подготовиться и перестроить задачу при затруднении.',
  Support.together =>
    'Можно делать одно и то же или разные дела. Важен подтверждённый совместный старт.',
  Support.report =>
    'Подходит для тренировки, уборки, текста и других результатов, которые удобно подтвердить.',
  Support.curator =>
    'Выбранный вами человек напоминает, спрашивает и поддерживает, но не становится контролёром.',
};
IconData supportIcon(Support s) => switch (s) {
  Support.solo => Icons.person,
  Support.ai => Icons.auto_awesome,
  Support.together => Icons.people_alt,
  Support.report => Icons.ios_share,
  Support.curator => Icons.verified_user,
};
Color supportColor(Support s) => switch (s) {
  Support.solo => const Color(0xFFE7E4DC),
  Support.ai => const Color(0xFFD8ECE5),
  Support.together => const Color(0xFFD8E4F0),
  Support.report => const Color(0xFFF2E1D0),
  Support.curator => const Color(0xFFE8DCF0),
};
Color supportAccent(Support s) => switch (s) {
  Support.solo => const Color(0xFF4A5653),
  Support.ai => const Color(0xFF2F6F62),
  Support.together => const Color(0xFF365B7B),
  Support.report => const Color(0xFF8A5935),
  Support.curator => const Color(0xFF684A78),
};
String sessionMessage(Support s, AppState a) => switch (s) {
  Support.solo =>
    'Работайте самостоятельно. Таймер покажет время, а результат сохранится в истории.',
  Support.ai =>
    'Помощник показывает ближайшие действия и помогает перестроить задачу.',
  Support.together =>
    'Вы и другой человек начинаете одновременно. Делать можно одно и то же или разные дела.',
  Support.report =>
    'После завершения сохраните и отправьте подтверждение результата.',
  Support.curator =>
    a.curator.isEmpty
        ? 'Вы сможете выбрать человека, который добровольно напоминает и спрашивает о результате.'
        : 'Ваш куратор: ${a.curator}.',
};
String preStart(Support s) => switch (s) {
  Support.solo =>
    'Подготовьте всё необходимое, уберите одно отвлечение и начинайте.',
  Support.ai => 'Посмотрите предложенные шаги. Достаточно начать с первого.',
  Support.together =>
    'Договоритесь о времени. Каждый может выполнять своё действие.',
  Support.report =>
    'Решите, что отправите после дела: фото, видео, ссылку или короткий итог.',
  Support.curator =>
    'Договоритесь, когда куратор напомнит и какой вопрос задаст после.',
};
String resultName(ResultState s) => switch (s) {
  ResultState.done => 'Выполнено',
  ResultState.part => 'Сделана важная часть',
  ResultState.moved => 'Отложено на потом',
  ResultState.missed => 'Сегодня не получилось',
};
IconData resultIcon(ResultState s) => switch (s) {
  ResultState.done => Icons.check_circle,
  ResultState.part => Icons.timelapse,
  ResultState.moved => Icons.event_repeat,
  ResultState.missed => Icons.remove_circle_outline,
};

extension FirstOrNull<T> on Iterable<T> {
  T? get firstOrNull => isEmpty ? null : first;
}
