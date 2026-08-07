from pathlib import Path

main_path = Path('lib/main.dart')
pubspec_path = Path('pubspec.yaml')
text = main_path.read_text(encoding='utf-8')
pubspec = pubspec_path.read_text(encoding='utf-8')

if 'class Challenge {' in text:
    print('v0.12.0 challenges already applied')
    raise SystemExit(0)


def replace_once(old: str, new: str, label: str) -> None:
    global text
    if old not in text:
        raise SystemExit(f'{label} anchor not found')
    text = text.replace(old, new, 1)


replace_once(
    'enum SupportInviteStatus { draft, sent, accepted, started, completed, cancelled }',
    '''enum SupportInviteStatus { draft, sent, accepted, started, completed, cancelled }

enum ChallengeMode { solo, partner }

enum ChallengeDayResult { full, partial, skipped }''',
    'challenge enums',
)

challenge_models = r'''class ChallengeEntry {
  ChallengeEntry({
    required this.date,
    required this.result,
    this.amount = 0,
    this.note = '',
  });

  final DateTime date;
  final ChallengeDayResult result;
  final int amount;
  final String note;

  Map<String, dynamic> toJson() => {
    'date': date.toIso8601String(),
    'result': result.name,
    'amount': amount,
    'note': note,
  };

  factory ChallengeEntry.fromJson(Map<String, dynamic> json) => ChallengeEntry(
    date: challengeDay(
      DateTime.tryParse((json['date'] ?? '').toString()) ?? DateTime.now(),
    ),
    result: ChallengeDayResult.values.firstWhere(
      (value) => value.name == json['result'],
      orElse: () => ChallengeDayResult.partial,
    ),
    amount: json['amount'] ?? 0,
    note: (json['note'] ?? '').toString(),
  );
}

class Challenge {
  Challenge({
    required this.title,
    required this.rule,
    required this.dailyTarget,
    required this.unit,
    required DateTime startDate,
    required this.durationDays,
    this.mode = ChallengeMode.solo,
    this.partner = '',
    this.allowedSkips = 0,
    this.consequence = '',
    List<ChallengeEntry>? entries,
    String? id,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) : id = id ?? DateTime.now().microsecondsSinceEpoch.toString(),
       startDate = challengeDay(startDate),
       entries = entries ?? <ChallengeEntry>[],
       createdAt = createdAt ?? DateTime.now(),
       updatedAt = updatedAt ?? DateTime.now();

  final String id;
  String title;
  String rule;
  int dailyTarget;
  String unit;
  DateTime startDate;
  int durationDays;
  ChallengeMode mode;
  String partner;
  int allowedSkips;
  String consequence;
  List<ChallengeEntry> entries;
  final DateTime createdAt;
  DateTime updatedAt;

  DateTime get endDate => startDate.add(Duration(days: durationDays - 1));
  int get fullDays => entries
      .where((entry) => entry.result == ChallengeDayResult.full)
      .length;
  int get partialDays => entries
      .where((entry) => entry.result == ChallengeDayResult.partial)
      .length;
  int get skippedDays => entries
      .where((entry) => entry.result == ChallengeDayResult.skipped)
      .length;
  int get markedDays => entries.length;
  bool get isActive => !challengeDay(DateTime.now()).isAfter(endDate);
  bool get isCompleted => challengeDay(DateTime.now()).isAfter(endDate);

  int dayNumber([DateTime? value]) {
    final day = challengeDay(value ?? DateTime.now());
    if (day.isBefore(startDate)) return 0;
    final number = day.difference(startDate).inDays + 1;
    return number.clamp(1, durationDays);
  }

  ChallengeEntry? entryFor(DateTime value) {
    final day = challengeDay(value);
    for (final entry in entries) {
      if (challengeSameDay(entry.date, day)) return entry;
    }
    return null;
  }

  int get currentStreak {
    if (entries.isEmpty) return 0;
    var cursor = challengeDay(DateTime.now());
    if (cursor.isAfter(endDate)) cursor = endDate;
    if (entryFor(cursor) == null) {
      cursor = cursor.subtract(const Duration(days: 1));
    }
    var value = 0;
    while (!cursor.isBefore(startDate)) {
      final entry = entryFor(cursor);
      if (entry == null || entry.result != ChallengeDayResult.full) break;
      value += 1;
      cursor = cursor.subtract(const Duration(days: 1));
    }
    return value;
  }

  double get progress => durationDays <= 0
      ? 0
      : (markedDays / durationDays).clamp(0.0, 1.0);

  Map<String, dynamic> toJson() => {
    'id': id,
    'title': title,
    'rule': rule,
    'dailyTarget': dailyTarget,
    'unit': unit,
    'startDate': startDate.toIso8601String(),
    'durationDays': durationDays,
    'mode': mode.name,
    'partner': partner,
    'allowedSkips': allowedSkips,
    'consequence': consequence,
    'entries': entries.map((entry) => entry.toJson()).toList(),
    'createdAt': createdAt.toIso8601String(),
    'updatedAt': updatedAt.toIso8601String(),
  };

  factory Challenge.fromJson(Map<String, dynamic> json) {
    final now = DateTime.now();
    return Challenge(
      id: (json['id'] ?? now.microsecondsSinceEpoch).toString(),
      title: (json['title'] ?? '').toString(),
      rule: (json['rule'] ?? '').toString(),
      dailyTarget: json['dailyTarget'] ?? 1,
      unit: (json['unit'] ?? 'раз').toString(),
      startDate:
          DateTime.tryParse((json['startDate'] ?? '').toString()) ?? now,
      durationDays: json['durationDays'] ?? 30,
      mode: ChallengeMode.values.firstWhere(
        (value) => value.name == json['mode'],
        orElse: () => ChallengeMode.solo,
      ),
      partner: (json['partner'] ?? '').toString(),
      allowedSkips: json['allowedSkips'] ?? 0,
      consequence: (json['consequence'] ?? '').toString(),
      entries: (json['entries'] ?? const [])
          .map<ChallengeEntry>(
            (entry) => ChallengeEntry.fromJson(
              Map<String, dynamic>.from(entry),
            ),
          )
          .toList(),
      createdAt: DateTime.tryParse((json['createdAt'] ?? '').toString()) ?? now,
      updatedAt: DateTime.tryParse((json['updatedAt'] ?? '').toString()) ?? now,
    );
  }
}

DateTime challengeDay(DateTime value) =>
    DateTime(value.year, value.month, value.day);

bool challengeSameDay(DateTime first, DateTime second) =>
    first.year == second.year &&
    first.month == second.month &&
    first.day == second.day;

String challengeResultTitle(ChallengeDayResult result) => switch (result) {
  ChallengeDayResult.full => 'Выполнено',
  ChallengeDayResult.partial => 'Частично',
  ChallengeDayResult.skipped => 'Пропуск',
};

'''
notification_at = text.index('class NotificationService')
text = text[:notification_at] + challenge_models + text[notification_at:]

replace_once(
    '  final List<SupportAgreement> supportAgreements = [];\n  static const key',
    '  final List<SupportAgreement> supportAgreements = [];\n  final List<Challenge> challenges = [];\n  static const key',
    'AppState challenge list',
)
replace_once(
    'static const schemaVersion = 5;',
    'static const schemaVersion = 6;',
    'challenge schema version',
)
replace_once(
    '      _restorePausedRoutines();',
    '''      challenges.addAll(
        (j['challenges'] ?? []).map<Challenge>(
          (entry) => Challenge.fromJson(Map<String, dynamic>.from(entry)),
        ),
      );
      _restorePausedRoutines();''',
    'challenge load',
)
replace_once(
    "    'supportAgreements': supportAgreements.map((e) => e.toJson()).toList(),\n  };",
    "    'supportAgreements': supportAgreements.map((e) => e.toJson()).toList(),\n    'challenges': challenges.map((e) => e.toJson()).toList(),\n  };",
    'challenge payload',
)

challenge_methods = r'''  void addChallenge(Challenge challenge) {
    challenges.insert(0, challenge);
    notifyListeners();
    save();
  }

  void updateChallenge(Challenge challenge) {
    challenge.updatedAt = DateTime.now();
    notifyListeners();
    save();
  }

  void deleteChallenge(Challenge challenge) {
    challenges.remove(challenge);
    notifyListeners();
    save();
  }

  void markChallengeDay(
    Challenge challenge,
    ChallengeDayResult result, {
    DateTime? date,
    int amount = 0,
    String note = '',
  }) {
    final day = challengeDay(date ?? DateTime.now());
    if (day.isBefore(challenge.startDate) || day.isAfter(challenge.endDate)) {
      return;
    }
    final entry = ChallengeEntry(
      date: day,
      result: result,
      amount: amount,
      note: note.trim(),
    );
    final index = challenge.entries.indexWhere(
      (value) => challengeSameDay(value.date, day),
    );
    if (index < 0) {
      challenge.entries.add(entry);
    } else {
      challenge.entries[index] = entry;
    }
    challenge.entries.sort((a, b) => a.date.compareTo(b.date));
    challenge.updatedAt = DateTime.now();
    notifyListeners();
    save();
  }

  void removeChallengeDay(Challenge challenge, DateTime date) {
    challenge.entries.removeWhere(
      (entry) => challengeSameDay(entry.date, date),
    );
    challenge.updatedAt = DateTime.now();
    notifyListeners();
    save();
  }

'''
methods_at = text.index('  void upsertSupportAgreement(')
text = text[:methods_at] + challenge_methods + text[methods_at:]

# Put challenges between the main goal and ordinary daily load.
today_anchor = '''          _TodayGoalArea(
            app: widget.app,
            actions: goalActions,
            onOpenGoal: widget.onOpenGoal,
          ),
          const SizedBox(height: 19),
          const Divider(height: 1, color: Color(0xFFDDE2DF)),'''
if today_anchor not in text:
    raise SystemExit('Today challenge block anchor not found')
text = text.replace(
    today_anchor,
    '''          _TodayGoalArea(
            app: widget.app,
            actions: goalActions,
            onOpenGoal: widget.onOpenGoal,
          ),
          const SizedBox(height: 20),
          _TodayChallengesArea(app: widget.app),
          const SizedBox(height: 19),
          const Divider(height: 1, color: Color(0xFFDDE2DF)),''',
    1,
)

# Add partner challenges to the Together tab without changing existing agreements.
support_start = text.index('class SupportScreen extends StatelessWidget')
support_end = text.index('class TogetherActionCard', support_start)
support_block = text[support_start:support_end]
support_marker = '          if (active.isNotEmpty) ...['
if support_marker not in support_block:
    raise SystemExit('Together partner challenge anchor not found')
partner_block = '''          if (app.challenges.any(
            (challenge) =>
                challenge.mode == ChallengeMode.partner && challenge.isActive,
          )) ...[
            Container(
              key: const ValueKey('together-partner-challenges'),
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFFFFF4D8),
                borderRadius: BorderRadius.circular(21),
                border: Border.all(color: const Color(0xFFEBD9A8)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'СОВМЕСТНЫЕ ЧЕЛЛЕНДЖИ',
                    style: TextStyle(
                      color: Color(0xFF806321),
                      fontSize: 10.5,
                      fontWeight: FontWeight.w900,
                      letterSpacing: .8,
                    ),
                  ),
                  const SizedBox(height: 7),
                  Text(
                    '${app.challenges.where((challenge) => challenge.mode == ChallengeMode.partner && challenge.isActive).length} активных договорённостей на дистанцию',
                    style: const TextStyle(
                      color: ink,
                      fontSize: 16,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  const SizedBox(height: 9),
                  SizedBox(
                    width: double.infinity,
                    child: OutlinedButton.icon(
                      onPressed: () => Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (_) => ChallengesScreen(app: app),
                        ),
                      ),
                      icon: const Icon(Icons.emoji_events_outlined),
                      label: const Text('Открыть челленджи'),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 12),
          ],
'''
support_block = support_block.replace(
    support_marker,
    partner_block + support_marker,
    1,
)
text = text[:support_start] + support_block + text[support_end:]

challenge_ui = r'''class _TodayChallengesArea extends StatefulWidget {
  const _TodayChallengesArea({required this.app});
  final AppState app;

  @override
  State<_TodayChallengesArea> createState() => _TodayChallengesAreaState();
}

class _TodayChallengesAreaState extends State<_TodayChallengesArea> {
  Future<void> openAll() async {
    await Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => ChallengesScreen(app: widget.app)),
    );
    if (mounted) setState(() {});
  }

  Future<void> create() async {
    await Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => ChallengeEditor(app: widget.app)),
    );
    if (mounted) setState(() {});
  }

  Future<void> open(Challenge challenge) async {
    await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => ChallengeDetailScreen(
          app: widget.app,
          challenge: challenge,
        ),
      ),
    );
    if (mounted) setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    final active = widget.app.challenges
        .where((challenge) => challenge.isActive)
        .toList()
      ..sort((a, b) => a.endDate.compareTo(b.endDate));
    return Column(
      key: const ValueKey('today-challenges-area'),
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            const Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Челленджи',
                    style: TextStyle(
                      color: ink,
                      fontSize: 19,
                      fontWeight: FontWeight.w700,
                      letterSpacing: -.2,
                    ),
                  ),
                  SizedBox(height: 2),
                  Text(
                    'Обещания на ограниченный срок.',
                    style: TextStyle(
                      color: Color(0xFF6C7773),
                      fontSize: 12.5,
                    ),
                  ),
                ],
              ),
            ),
            IconButton(
              key: const ValueKey('add-challenge'),
              tooltip: 'Создать челлендж',
              onPressed: create,
              icon: const Icon(Icons.add_rounded, color: green),
            ),
          ],
        ),
        const SizedBox(height: 8),
        if (active.isEmpty)
          InkWell(
            key: const ValueKey('empty-challenge-card'),
            borderRadius: BorderRadius.circular(18),
            onTap: create,
            child: Container(
              width: double.infinity,
              padding: const EdgeInsets.fromLTRB(14, 13, 14, 13),
              decoration: BoxDecoration(
                color: const Color(0xFFFFF8E7),
                borderRadius: BorderRadius.circular(18),
                border: Border.all(color: const Color(0xFFE9DDBD)),
              ),
              child: const Row(
                children: [
                  Icon(Icons.emoji_events_outlined, color: Color(0xFF8A6B25)),
                  SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      'Дайте себе конкретное обещание на 7, 30 или 90 дней.',
                      style: TextStyle(
                        color: ink,
                        fontSize: 13,
                        height: 1.35,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                  Icon(Icons.chevron_right_rounded, color: Color(0xFF8A6B25)),
                ],
              ),
            ),
          )
        else ...[
          ...active.take(2).map(
            (challenge) => Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: _ChallengeCompactCard(
                challenge: challenge,
                onTap: () => open(challenge),
              ),
            ),
          ),
          if (active.length > 2 || widget.app.challenges.length > active.length)
            Align(
              alignment: Alignment.centerLeft,
              child: TextButton.icon(
                key: const ValueKey('open-all-challenges'),
                onPressed: openAll,
                icon: const Icon(Icons.grid_view_rounded, size: 18),
                label: Text('Все челленджи (${widget.app.challenges.length})'),
              ),
            ),
        ],
      ],
    );
  }
}

class _ChallengeCompactCard extends StatelessWidget {
  const _ChallengeCompactCard({required this.challenge, required this.onTap});
  final Challenge challenge;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final today = challenge.entryFor(DateTime.now());
    return Material(
      color: Colors.white,
      clipBehavior: Clip.antiAlias,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(18),
        side: const BorderSide(color: Color(0xFFE0E5E2)),
      ),
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.fromLTRB(14, 12, 12, 12),
          child: Row(
            children: [
              Container(
                width: 42,
                height: 42,
                decoration: BoxDecoration(
                  color: today?.result == ChallengeDayResult.full
                      ? const Color(0xFFDDEFE7)
                      : const Color(0xFFFFF1C8),
                  borderRadius: BorderRadius.circular(14),
                ),
                child: Icon(
                  today?.result == ChallengeDayResult.full
                      ? Icons.check_rounded
                      : Icons.emoji_events_outlined,
                  color: today?.result == ChallengeDayResult.full
                      ? green
                      : const Color(0xFF8A6B25),
                ),
              ),
              const SizedBox(width: 11),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      challenge.title,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        color: ink,
                        fontSize: 14.5,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'День ${challenge.dayNumber()} из ${challenge.durationDays} · серия ${challenge.currentStreak}',
                      style: const TextStyle(
                        color: Color(0xFF68736F),
                        fontSize: 11.8,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 6),
              Text(
                today == null ? 'Отметить' : challengeResultTitle(today.result),
                style: TextStyle(
                  color: today == null ? green : const Color(0xFF68736F),
                  fontSize: 11.5,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const Icon(Icons.chevron_right_rounded, color: Color(0xFF8A9490)),
            ],
          ),
        ),
      ),
    );
  }
}

class ChallengesScreen extends StatefulWidget {
  const ChallengesScreen({required this.app, super.key});
  final AppState app;

  @override
  State<ChallengesScreen> createState() => _ChallengesScreenState();
}

class _ChallengesScreenState extends State<ChallengesScreen> {
  Future<void> create() async {
    await Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => ChallengeEditor(app: widget.app)),
    );
    if (mounted) setState(() {});
  }

  Future<void> open(Challenge challenge) async {
    await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => ChallengeDetailScreen(
          app: widget.app,
          challenge: challenge,
        ),
      ),
    );
    if (mounted) setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    final active = widget.app.challenges
        .where((challenge) => challenge.isActive)
        .toList();
    final completed = widget.app.challenges
        .where((challenge) => challenge.isCompleted)
        .toList();
    return Scaffold(
      appBar: AppBar(
        title: const Text('Челленджи'),
        actions: [
          IconButton(
            key: const ValueKey('challenge-screen-add'),
            onPressed: create,
            icon: const Icon(Icons.add_rounded),
          ),
        ],
      ),
      body: ListView(
        key: const ValueKey('challenges-scroll'),
        padding: const EdgeInsets.fromLTRB(16, 2, 16, 30),
        children: [
          Container(
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(
              color: const Color(0xFFFFF4D8),
              borderRadius: BorderRadius.circular(23),
            ),
            child: const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'ОБЕЩАНИЕ НА ДИСТАНЦИЮ',
                  style: TextStyle(
                    color: Color(0xFF806321),
                    fontSize: 10.5,
                    fontWeight: FontWeight.w900,
                    letterSpacing: .8,
                  ),
                ),
                SizedBox(height: 8),
                Text(
                  'Не бесконечная привычка, а конкретное правило с началом и финишем.',
                  style: TextStyle(
                    color: ink,
                    fontSize: 20,
                    height: 1.24,
                    fontWeight: FontWeight.w900,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 18),
          _ChallengeSectionTitle(title: 'Активные', count: active.length),
          const SizedBox(height: 8),
          if (active.isEmpty)
            _ChallengeEmpty(onCreate: create)
          else
            ...active.map(
              (challenge) => Padding(
                padding: const EdgeInsets.only(bottom: 9),
                child: _ChallengeListCard(
                  challenge: challenge,
                  onTap: () => open(challenge),
                ),
              ),
            ),
          if (completed.isNotEmpty) ...[
            const SizedBox(height: 20),
            _ChallengeSectionTitle(
              title: 'Завершённые',
              count: completed.length,
            ),
            const SizedBox(height: 8),
            ...completed.map(
              (challenge) => Padding(
                padding: const EdgeInsets.only(bottom: 9),
                child: _ChallengeListCard(
                  challenge: challenge,
                  onTap: () => open(challenge),
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class _ChallengeSectionTitle extends StatelessWidget {
  const _ChallengeSectionTitle({required this.title, required this.count});
  final String title;
  final int count;

  @override
  Widget build(BuildContext context) => Row(
    children: [
      Expanded(
        child: Text(
          title,
          style: const TextStyle(
            color: ink,
            fontSize: 18,
            fontWeight: FontWeight.w800,
          ),
        ),
      ),
      Text(
        '$count',
        style: const TextStyle(
          color: green,
          fontSize: 13,
          fontWeight: FontWeight.w800,
        ),
      ),
    ],
  );
}

class _ChallengeEmpty extends StatelessWidget {
  const _ChallengeEmpty({required this.onCreate});
  final VoidCallback onCreate;

  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.all(17),
    decoration: BoxDecoration(
      color: Colors.white,
      borderRadius: BorderRadius.circular(20),
      border: Border.all(color: const Color(0xFFE0E5E2)),
    ),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Первого челленджа пока нет',
          style: TextStyle(
            color: ink,
            fontSize: 16,
            fontWeight: FontWeight.w800,
          ),
        ),
        const SizedBox(height: 5),
        const Text(
          'Например: 5 подтягиваний ежедневно в течение 90 дней.',
          style: TextStyle(color: Color(0xFF68736F), height: 1.4),
        ),
        const SizedBox(height: 12),
        FilledButton.icon(
          key: const ValueKey('create-first-challenge'),
          onPressed: onCreate,
          icon: const Icon(Icons.add_rounded),
          label: const Text('Создать челлендж'),
        ),
      ],
    ),
  );
}

class _ChallengeListCard extends StatelessWidget {
  const _ChallengeListCard({required this.challenge, required this.onTap});
  final Challenge challenge;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) => Card(
    margin: EdgeInsets.zero,
    child: InkWell(
      borderRadius: BorderRadius.circular(20),
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.all(15),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    challenge.title,
                    style: const TextStyle(
                      color: ink,
                      fontSize: 16,
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                ),
                if (challenge.mode == ChallengeMode.partner)
                  const Icon(Icons.people_alt_outlined, color: Color(0xFF66528A)),
              ],
            ),
            const SizedBox(height: 5),
            Text(
              '${challenge.dailyTarget} ${challenge.unit} · ${challenge.durationDays} дней',
              style: const TextStyle(color: Color(0xFF68736F), fontSize: 12.5),
            ),
            const SizedBox(height: 11),
            ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: LinearProgressIndicator(
                value: challenge.progress,
                minHeight: 6,
                backgroundColor: const Color(0xFFE8EEEB),
                valueColor: const AlwaysStoppedAnimation(green),
              ),
            ),
            const SizedBox(height: 8),
            Text(
              '${challenge.fullDays} выполнено · ${challenge.skippedDays} пропусков · серия ${challenge.currentStreak}',
              style: const TextStyle(color: Color(0xFF68736F), fontSize: 11.8),
            ),
          ],
        ),
      ),
    ),
  );
}

class ChallengeEditor extends StatefulWidget {
  const ChallengeEditor({required this.app, this.existing, super.key});
  final AppState app;
  final Challenge? existing;

  @override
  State<ChallengeEditor> createState() => _ChallengeEditorState();
}

class _ChallengeEditorState extends State<ChallengeEditor> {
  late final TextEditingController title;
  late final TextEditingController rule;
  late final TextEditingController target;
  late final TextEditingController unit;
  late final TextEditingController partner;
  late final TextEditingController consequence;
  late final TextEditingController skips;
  late int duration;
  late ChallengeMode mode;

  @override
  void initState() {
    super.initState();
    final value = widget.existing;
    title = TextEditingController(text: value?.title ?? '');
    rule = TextEditingController(text: value?.rule ?? '');
    target = TextEditingController(text: '${value?.dailyTarget ?? 5}');
    unit = TextEditingController(text: value?.unit ?? 'раз');
    partner = TextEditingController(text: value?.partner ?? '');
    consequence = TextEditingController(text: value?.consequence ?? '');
    skips = TextEditingController(text: '${value?.allowedSkips ?? 0}');
    duration = value?.durationDays ?? 30;
    mode = value?.mode ?? ChallengeMode.solo;
  }

  @override
  void dispose() {
    title.dispose();
    rule.dispose();
    target.dispose();
    unit.dispose();
    partner.dispose();
    consequence.dispose();
    skips.dispose();
    super.dispose();
  }

  void save() {
    final name = title.text.trim();
    final daily = int.tryParse(target.text.trim()) ?? 0;
    if (name.isEmpty || daily <= 0 || duration <= 0) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Укажите название, норму и срок.')),
      );
      return;
    }
    final existing = widget.existing;
    if (existing == null) {
      widget.app.addChallenge(
        Challenge(
          title: name,
          rule: rule.text.trim(),
          dailyTarget: daily,
          unit: unit.text.trim().isEmpty ? 'раз' : unit.text.trim(),
          startDate: DateTime.now(),
          durationDays: duration,
          mode: mode,
          partner: mode == ChallengeMode.partner ? partner.text.trim() : '',
          allowedSkips: int.tryParse(skips.text.trim()) ?? 0,
          consequence: consequence.text.trim(),
        ),
      );
    } else {
      existing.title = name;
      existing.rule = rule.text.trim();
      existing.dailyTarget = daily;
      existing.unit = unit.text.trim().isEmpty ? 'раз' : unit.text.trim();
      existing.durationDays = duration;
      existing.mode = mode;
      existing.partner = mode == ChallengeMode.partner ? partner.text.trim() : '';
      existing.allowedSkips = int.tryParse(skips.text.trim()) ?? 0;
      existing.consequence = consequence.text.trim();
      widget.app.updateChallenge(existing);
    }
    Navigator.pop(context);
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(
      title: Text(widget.existing == null ? 'Новый челлендж' : 'Изменить челлендж'),
    ),
    body: ListView(
      key: const ValueKey('challenge-editor-scroll'),
      padding: const EdgeInsets.fromLTRB(16, 2, 16, 30),
      children: [
        const Text(
          'Какое обещание вы даёте?',
          style: TextStyle(
            color: ink,
            fontSize: 24,
            height: 1.15,
            fontWeight: FontWeight.w900,
          ),
        ),
        const SizedBox(height: 6),
        const Text(
          'Челлендж имеет конкретную ежедневную норму, начало и финиш.',
          style: TextStyle(color: Color(0xFF68736F), height: 1.4),
        ),
        const SizedBox(height: 16),
        TextField(
          key: const ValueKey('challenge-title-field'),
          controller: title,
          decoration: const InputDecoration(
            labelText: 'Название',
            hintText: '5 подтягиваний каждый день',
          ),
        ),
        const SizedBox(height: 11),
        TextField(
          controller: rule,
          maxLines: 2,
          decoration: const InputDecoration(
            labelText: 'Правило',
            hintText: 'Что именно считается выполнением',
          ),
        ),
        const SizedBox(height: 11),
        Row(
          children: [
            Expanded(
              child: TextField(
                key: const ValueKey('challenge-target-field'),
                controller: target,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(labelText: 'Норма в день'),
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: TextField(
                controller: unit,
                decoration: const InputDecoration(
                  labelText: 'Единица',
                  hintText: 'раз, минут, страниц',
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        const Text(
          'Срок',
          style: TextStyle(color: ink, fontWeight: FontWeight.w800),
        ),
        const SizedBox(height: 8),
        Wrap(
          spacing: 7,
          runSpacing: 7,
          children: [7, 21, 30, 60, 90].map((value) => ChoiceChip(
            label: Text('$value дней'),
            selected: duration == value,
            onSelected: (_) => setState(() => duration = value),
          )).toList(),
        ),
        const SizedBox(height: 16),
        const Text(
          'Формат',
          style: TextStyle(color: ink, fontWeight: FontWeight.w800),
        ),
        const SizedBox(height: 8),
        SegmentedButton<ChallengeMode>(
          segments: const [
            ButtonSegment(
              value: ChallengeMode.solo,
              icon: Icon(Icons.person_outline_rounded),
              label: Text('Личный'),
            ),
            ButtonSegment(
              value: ChallengeMode.partner,
              icon: Icon(Icons.people_alt_outlined),
              label: Text('С партнёром'),
            ),
          ],
          selected: {mode},
          onSelectionChanged: (value) => setState(() => mode = value.first),
        ),
        if (mode == ChallengeMode.partner) ...[
          const SizedBox(height: 11),
          TextField(
            key: const ValueKey('challenge-partner-field'),
            controller: partner,
            decoration: const InputDecoration(
              labelText: 'Имя партнёра',
              hintText: 'Необязательно',
            ),
          ),
        ],
        const SizedBox(height: 11),
        TextField(
          controller: skips,
          keyboardType: TextInputType.number,
          decoration: const InputDecoration(
            labelText: 'Допустимо пропусков за весь срок',
          ),
        ),
        const SizedBox(height: 11),
        TextField(
          controller: consequence,
          maxLines: 2,
          decoration: const InputDecoration(
            labelText: 'Добровольное последствие за пропуск',
            hintText: 'Например: перевести 10 € в общий фонд',
          ),
        ),
        const SizedBox(height: 18),
        FilledButton.icon(
          key: const ValueKey('save-challenge'),
          onPressed: save,
          icon: const Icon(Icons.emoji_events_outlined),
          label: const Text('Сохранить челлендж'),
        ),
      ],
    ),
  );
}

class ChallengeDetailScreen extends StatefulWidget {
  const ChallengeDetailScreen({
    required this.app,
    required this.challenge,
    super.key,
  });
  final AppState app;
  final Challenge challenge;

  @override
  State<ChallengeDetailScreen> createState() => _ChallengeDetailScreenState();
}

class _ChallengeDetailScreenState extends State<ChallengeDetailScreen> {
  late final TextEditingController amount;
  late final TextEditingController note;

  @override
  void initState() {
    super.initState();
    final entry = widget.challenge.entryFor(DateTime.now());
    amount = TextEditingController(
      text: '${entry?.amount ?? widget.challenge.dailyTarget}',
    );
    note = TextEditingController(text: entry?.note ?? '');
  }

  @override
  void dispose() {
    amount.dispose();
    note.dispose();
    super.dispose();
  }

  void mark(ChallengeDayResult result) {
    final value = result == ChallengeDayResult.skipped
        ? 0
        : int.tryParse(amount.text.trim()) ?? 0;
    widget.app.markChallengeDay(
      widget.challenge,
      result,
      amount: result == ChallengeDayResult.full
          ? widget.challenge.dailyTarget
          : value,
      note: note.text,
    );
    setState(() {
      final current = widget.challenge.entryFor(DateTime.now());
      amount.text = '${current?.amount ?? widget.challenge.dailyTarget}';
    });
  }

  Future<void> shareReport() async {
    final entry = widget.challenge.entryFor(DateTime.now());
    if (entry == null) return;
    final partner = widget.challenge.partner.trim();
    final greeting = partner.isEmpty ? '' : '$partner, ';
    final text =
        '${greeting}день ${widget.challenge.dayNumber()} из ${widget.challenge.durationDays}: '
        '${challengeResultTitle(entry.result).toLowerCase()} — ${entry.amount} ${widget.challenge.unit}. '
        'Текущая серия: ${widget.challenge.currentStreak}.';
    try {
      await SharePlus.instance.share(
        ShareParams(text: text, subject: widget.challenge.title),
      );
    } catch (_) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Не удалось открыть отправку.')),
      );
    }
  }

  Future<void> edit() async {
    await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => ChallengeEditor(
          app: widget.app,
          existing: widget.challenge,
        ),
      ),
    );
    if (mounted) setState(() {});
  }

  Future<void> remove() async {
    final yes = await showDialog<bool>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Удалить челлендж?'),
        content: const Text('Все ежедневные отметки этого челленджа исчезнут.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(dialogContext, false),
            child: const Text('Отмена'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(dialogContext, true),
            child: const Text('Удалить'),
          ),
        ],
      ),
    );
    if (yes != true || !mounted) return;
    widget.app.deleteChallenge(widget.challenge);
    Navigator.pop(context);
  }

  void continueAsRoutine() {
    widget.app.add(
      ActionItem(
        id: DateTime.now().microsecondsSinceEpoch.toString(),
        title: widget.challenge.title,
        small: widget.challenge.rule,
        minutes: 0,
        support: Support.solo,
        goal: false,
        kind: IntentKind.routine,
        repeatDaily: true,
        useTimer: false,
        routineSchedule: RoutineSchedule.daily,
        weeklyTarget: 7,
      ),
    );
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Добавлено в регулярные практики.')),
    );
  }

  @override
  Widget build(BuildContext context) {
    final challenge = widget.challenge;
    final today = challenge.entryFor(DateTime.now());
    final canMarkToday = !challengeDay(DateTime.now()).isBefore(challenge.startDate) &&
        !challengeDay(DateTime.now()).isAfter(challenge.endDate);
    return Scaffold(
      appBar: AppBar(
        title: const Text('Челлендж'),
        actions: [
          IconButton(onPressed: edit, icon: const Icon(Icons.edit_outlined)),
          PopupMenuButton<String>(
            onSelected: (value) {
              if (value == 'delete') remove();
            },
            itemBuilder: (_) => const [
              PopupMenuItem(value: 'delete', child: Text('Удалить челлендж')),
            ],
          ),
        ],
      ),
      body: ListView(
        key: const ValueKey('challenge-detail-scroll'),
        padding: const EdgeInsets.fromLTRB(16, 2, 16, 30),
        children: [
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF173C36), Color(0xFF426F65)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(25),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  challenge.mode == ChallengeMode.solo
                      ? 'ЛИЧНЫЙ ЧЕЛЛЕНДЖ'
                      : 'С ПАРТНЁРОМ${challenge.partner.trim().isEmpty ? '' : ' · ${challenge.partner}'}',
                  style: const TextStyle(
                    color: mint,
                    fontSize: 10.5,
                    fontWeight: FontWeight.w900,
                    letterSpacing: .8,
                  ),
                ),
                const SizedBox(height: 9),
                Text(
                  challenge.title,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 24,
                    height: 1.15,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  '${challenge.dailyTarget} ${challenge.unit} каждый день · ${challenge.durationDays} дней',
                  style: const TextStyle(color: Color(0xFFD4E1DD), height: 1.4),
                ),
                const SizedBox(height: 14),
                ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: LinearProgressIndicator(
                    value: challenge.progress,
                    minHeight: 7,
                    backgroundColor: Colors.white12,
                    valueColor: const AlwaysStoppedAnimation(mint),
                  ),
                ),
                const SizedBox(height: 9),
                Text(
                  challenge.isActive
                      ? 'День ${challenge.dayNumber()} из ${challenge.durationDays}'
                      : 'Дистанция завершена',
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),
          Row(
            children: [
              Expanded(child: _ChallengeMetric(value: '${challenge.fullDays}', label: 'выполнено')),
              const SizedBox(width: 8),
              Expanded(child: _ChallengeMetric(value: '${challenge.currentStreak}', label: 'серия')),
              const SizedBox(width: 8),
              Expanded(child: _ChallengeMetric(value: '${challenge.skippedDays}', label: 'пропуски')),
            ],
          ),
          if (canMarkToday) ...[
            const SizedBox(height: 18),
            Container(
              key: const ValueKey('challenge-today-card'),
              padding: const EdgeInsets.all(17),
              decoration: BoxDecoration(
                color: const Color(0xFFFFFBF2),
                borderRadius: BorderRadius.circular(22),
                border: Border.all(color: const Color(0xFFE9DFC8)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    today == null ? 'Сегодня ещё не отмечено' : 'Сегодня: ${challengeResultTitle(today.result)}',
                    style: const TextStyle(
                      color: ink,
                      fontSize: 17,
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                  const SizedBox(height: 11),
                  TextField(
                    key: const ValueKey('challenge-amount-field'),
                    controller: amount,
                    keyboardType: TextInputType.number,
                    decoration: InputDecoration(
                      labelText: 'Сделано сегодня, ${challenge.unit}',
                    ),
                  ),
                  const SizedBox(height: 9),
                  TextField(
                    controller: note,
                    maxLines: 2,
                    decoration: const InputDecoration(
                      labelText: 'Комментарий — необязательно',
                    ),
                  ),
                  const SizedBox(height: 12),
                  SizedBox(
                    width: double.infinity,
                    child: FilledButton.icon(
                      key: const ValueKey('challenge-mark-full'),
                      onPressed: () => mark(ChallengeDayResult.full),
                      icon: const Icon(Icons.check_rounded),
                      label: const Text('Выполнил полностью'),
                    ),
                  ),
                  const SizedBox(height: 7),
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton(
                          key: const ValueKey('challenge-mark-partial'),
                          onPressed: () => mark(ChallengeDayResult.partial),
                          child: const Text('Частично'),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: TextButton(
                          key: const ValueKey('challenge-mark-skipped'),
                          onPressed: () => mark(ChallengeDayResult.skipped),
                          child: const Text('Пропуск'),
                        ),
                      ),
                    ],
                  ),
                  if (today != null) ...[
                    const SizedBox(height: 5),
                    Align(
                      alignment: Alignment.centerLeft,
                      child: TextButton(
                        onPressed: () {
                          widget.app.removeChallengeDay(challenge, DateTime.now());
                          setState(() {});
                        },
                        child: const Text('Убрать сегодняшнюю отметку'),
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ],
          if (challenge.mode == ChallengeMode.partner && today != null) ...[
            const SizedBox(height: 10),
            OutlinedButton.icon(
              key: const ValueKey('share-challenge-report'),
              onPressed: shareReport,
              icon: const Icon(Icons.send_outlined),
              label: const Text('Отправить отчёт партнёру'),
            ),
          ],
          const SizedBox(height: 20),
          const Text(
            'Дистанция',
            style: TextStyle(
              color: ink,
              fontSize: 18,
              fontWeight: FontWeight.w900,
            ),
          ),
          const SizedBox(height: 9),
          _ChallengeCalendar(challenge: challenge),
          if (challenge.rule.isNotEmpty || challenge.consequence.isNotEmpty) ...[
            const SizedBox(height: 18),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFFF0F4F2),
                borderRadius: BorderRadius.circular(20),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (challenge.rule.isNotEmpty) ...[
                    const Text('Правило', style: TextStyle(fontWeight: FontWeight.w900)),
                    const SizedBox(height: 4),
                    Text(challenge.rule),
                  ],
                  if (challenge.consequence.isNotEmpty) ...[
                    if (challenge.rule.isNotEmpty) const SizedBox(height: 12),
                    const Text('При пропуске', style: TextStyle(fontWeight: FontWeight.w900)),
                    const SizedBox(height: 4),
                    Text(challenge.consequence),
                  ],
                  const SizedBox(height: 8),
                  Text(
                    'Допустимо пропусков: ${challenge.allowedSkips}',
                    style: const TextStyle(color: Color(0xFF68736F), fontSize: 12.5),
                  ),
                ],
              ),
            ),
          ],
          if (challenge.isCompleted) ...[
            const SizedBox(height: 14),
            FilledButton.tonalIcon(
              onPressed: continueAsRoutine,
              icon: const Icon(Icons.repeat_rounded),
              label: const Text('Продолжить как регулярную практику'),
            ),
          ],
        ],
      ),
    );
  }
}

class _ChallengeMetric extends StatelessWidget {
  const _ChallengeMetric({required this.value, required this.label});
  final String value;
  final String label;

  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 11),
    decoration: BoxDecoration(
      color: Colors.white,
      borderRadius: BorderRadius.circular(17),
      border: Border.all(color: const Color(0xFFE0E5E2)),
    ),
    child: Column(
      children: [
        Text(
          value,
          style: const TextStyle(
            color: green,
            fontSize: 18,
            fontWeight: FontWeight.w900,
          ),
        ),
        const SizedBox(height: 2),
        Text(
          label,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: const TextStyle(color: Color(0xFF68736F), fontSize: 10.8),
        ),
      ],
    ),
  );
}

class _ChallengeCalendar extends StatelessWidget {
  const _ChallengeCalendar({required this.challenge});
  final Challenge challenge;

  @override
  Widget build(BuildContext context) => Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      GridView.builder(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        itemCount: challenge.durationDays,
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 7,
          crossAxisSpacing: 5,
          mainAxisSpacing: 5,
        ),
        itemBuilder: (_, index) {
          final day = challenge.startDate.add(Duration(days: index));
          final entry = challenge.entryFor(day);
          final future = day.isAfter(challengeDay(DateTime.now()));
          final color = switch (entry?.result) {
            ChallengeDayResult.full => const Color(0xFFD6EADF),
            ChallengeDayResult.partial => const Color(0xFFFFE9B7),
            ChallengeDayResult.skipped => const Color(0xFFE5E5E1),
            null => future ? const Color(0xFFF4F4F1) : Colors.white,
          };
          final foreground = switch (entry?.result) {
            ChallengeDayResult.full => green,
            ChallengeDayResult.partial => const Color(0xFF8A681D),
            ChallengeDayResult.skipped => const Color(0xFF7A7A73),
            null => const Color(0xFF929A96),
          };
          return Container(
            alignment: Alignment.center,
            decoration: BoxDecoration(
              color: color,
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: const Color(0xFFE3E6E3)),
            ),
            child: Text(
              '${index + 1}',
              style: TextStyle(
                color: foreground,
                fontSize: 10.5,
                fontWeight: FontWeight.w800,
              ),
            ),
          );
        },
      ),
      const SizedBox(height: 9),
      const Wrap(
        spacing: 12,
        runSpacing: 5,
        children: [
          _ChallengeLegend(color: Color(0xFFD6EADF), label: 'выполнено'),
          _ChallengeLegend(color: Color(0xFFFFE9B7), label: 'частично'),
          _ChallengeLegend(color: Color(0xFFE5E5E1), label: 'пропуск'),
        ],
      ),
    ],
  );
}

class _ChallengeLegend extends StatelessWidget {
  const _ChallengeLegend({required this.color, required this.label});
  final Color color;
  final String label;

  @override
  Widget build(BuildContext context) => Row(
    mainAxisSize: MainAxisSize.min,
    children: [
      Container(
        width: 10,
        height: 10,
        decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(3)),
      ),
      const SizedBox(width: 5),
      Text(label, style: const TextStyle(color: Color(0xFF68736F), fontSize: 11)),
    ],
  );
}

'''
speech_at = text.index('class Speech {')
text = text[:speech_at] + challenge_ui + text[speech_at:]

if 'version: 0.11.0+27' not in pubspec:
    raise SystemExit('Expected v0.11.0 version not found')
pubspec = pubspec.replace('version: 0.11.0+27', 'version: 0.12.0+28', 1)

main_path.write_text(text, encoding='utf-8')
pubspec_path.write_text(pubspec, encoding='utf-8')
print('Applied v0.12.0 challenge product contour')
