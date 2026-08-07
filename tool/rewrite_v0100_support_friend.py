from pathlib import Path

main_path = Path('lib/main.dart')
pubspec_path = Path('pubspec.yaml')
text = main_path.read_text(encoding='utf-8')
pubspec = pubspec_path.read_text(encoding='utf-8')

if 'class SupportInviteScreen' in text:
    print('v0.10.0 support friend already applied')
    raise SystemExit(0)


def replace_once(old: str, new: str, label: str) -> None:
    global text
    if old not in text:
        raise SystemExit(f'{label} anchor not found')
    text = text.replace(old, new, 1)


replace_once(
    'enum StartDifficultyChoice { clarify, minimum, focus, together, report }\n\nenum StartProblem',
    '''enum StartDifficultyChoice { clarify, minimum, focus, together, report }

enum SupportInviteMode { together, simultaneous, report, impulse }

enum SupportInviteStatus { draft, sent, accepted, completed, cancelled }

enum StartProblem''',
    'support invite enums',
)

agreement_model = r'''class SupportAgreement {
  SupportAgreement({
    required this.actionId,
    required this.actionTitle,
    required this.mode,
    required this.status,
    required this.scheduledAt,
    required this.minutes,
    this.partner = '',
    String? id,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) : id = id ?? DateTime.now().microsecondsSinceEpoch.toString(),
       createdAt = createdAt ?? DateTime.now(),
       updatedAt = updatedAt ?? DateTime.now();

  final String id;
  final String actionId;
  final String actionTitle;
  final SupportInviteMode mode;
  SupportInviteStatus status;
  final DateTime scheduledAt;
  final int minutes;
  final String partner;
  final DateTime createdAt;
  DateTime updatedAt;

  Map<String, dynamic> toJson() => {
    'id': id,
    'actionId': actionId,
    'actionTitle': actionTitle,
    'mode': mode.name,
    'status': status.name,
    'scheduledAt': scheduledAt.toIso8601String(),
    'minutes': minutes,
    'partner': partner,
    'createdAt': createdAt.toIso8601String(),
    'updatedAt': updatedAt.toIso8601String(),
  };

  factory SupportAgreement.fromJson(Map<String, dynamic> json) {
    final now = DateTime.now();
    return SupportAgreement(
      id: (json['id'] ?? now.microsecondsSinceEpoch).toString(),
      actionId: (json['actionId'] ?? '').toString(),
      actionTitle: (json['actionTitle'] ?? '').toString(),
      mode: SupportInviteMode.values.firstWhere(
        (value) => value.name == json['mode'],
        orElse: () => SupportInviteMode.simultaneous,
      ),
      status: SupportInviteStatus.values.firstWhere(
        (value) => value.name == json['status'],
        orElse: () => SupportInviteStatus.draft,
      ),
      scheduledAt:
          DateTime.tryParse((json['scheduledAt'] ?? '').toString()) ?? now,
      minutes: json['minutes'] ?? 15,
      partner: (json['partner'] ?? '').toString(),
      createdAt: DateTime.tryParse((json['createdAt'] ?? '').toString()) ?? now,
      updatedAt: DateTime.tryParse((json['updatedAt'] ?? '').toString()) ?? now,
    );
  }
}

'''
notification_at = text.index('class NotificationService')
text = text[:notification_at] + agreement_model + text[notification_at:]

replace_once(
    '  final List<HistoryItem> history = [];\n  static const key',
    '  final List<HistoryItem> history = [];\n  final List<SupportAgreement> supportAgreements = [];\n  static const key',
    'AppState support agreement list',
)
replace_once(
    'static const schemaVersion = 3;',
    'static const schemaVersion = 4;',
    'schema version',
)
replace_once(
    '      _restorePausedRoutines();',
    '''      supportAgreements.addAll(
        (j['supportAgreements'] ?? []).map<SupportAgreement>(
          (entry) => SupportAgreement.fromJson(
            Map<String, dynamic>.from(entry),
          ),
        ),
      );
      _restorePausedRoutines();''',
    'support agreement load',
)
replace_once(
    "    'history': history.map((e) => e.toJson()).toList(),\n  };",
    "    'history': history.map((e) => e.toJson()).toList(),\n    'supportAgreements': supportAgreements.map((e) => e.toJson()).toList(),\n  };",
    'support agreement payload',
)

agreement_methods = r'''  void upsertSupportAgreement(SupportAgreement agreement) {
    final index = supportAgreements.indexWhere(
      (item) => item.id == agreement.id,
    );
    agreement.updatedAt = DateTime.now();
    if (index < 0) {
      supportAgreements.insert(0, agreement);
    } else {
      supportAgreements[index] = agreement;
    }
    notifyListeners();
    save();
  }

  void setSupportAgreementStatus(
    SupportAgreement agreement,
    SupportInviteStatus status,
  ) {
    agreement.status = status;
    agreement.updatedAt = DateTime.now();
    notifyListeners();
    save();
  }

  SupportAgreement? latestSupportAgreementFor(String actionId) {
    for (final agreement in supportAgreements) {
      if (agreement.actionId == actionId &&
          agreement.status != SupportInviteStatus.cancelled &&
          agreement.status != SupportInviteStatus.completed) {
        return agreement;
      }
    }
    return null;
  }

'''
set_curator_at = text.index('  void setCurator(String value) {')
text = text[:set_curator_at] + agreement_methods + text[set_curator_at:]

# Add a calm social-support card to the goal route, directly after the current step.
goal_marker = '''          const SizedBox(height: 22),
          _GoalSectionHeader(
            title: 'Дальше','''
if goal_marker not in text:
    raise SystemExit('goal path social support insertion anchor not found')
text = text.replace(
    goal_marker,
    '''          if (current != null) ...[
            const SizedBox(height: 12),
            _GoalSupportAgreementCard(app: app, item: current),
          ],
          const SizedBox(height: 22),
          _GoalSectionHeader(
            title: 'Дальше',''',
    1,
)

support_ui = r'''class _GoalSupportAgreementCard extends StatelessWidget {
  const _GoalSupportAgreementCard({required this.app, required this.item});

  final AppState app;
  final ActionItem item;

  @override
  Widget build(BuildContext context) {
    final agreement = app.latestSupportAgreementFor(item.id);
    final all = app.supportAgreements
        .where((value) => value.actionId == item.id)
        .toList();
    return Container(
      key: const ValueKey('goal-support-agreement-card'),
      padding: const EdgeInsets.all(17),
      decoration: BoxDecoration(
        color: const Color(0xFFF0ECF8),
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: const Color(0xFFDDD4EF)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.people_alt_outlined, color: Color(0xFF66528A)),
              SizedBox(width: 8),
              Expanded(
                child: Text(
                  'ПОДДЕРЖКА ЗНАКОМОГО',
                  style: TextStyle(
                    color: Color(0xFF66528A),
                    fontSize: 10.5,
                    fontWeight: FontWeight.w900,
                    letterSpacing: .75,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Text(
            agreement == null
                ? 'Позовите человека именно для этого действия'
                : supportInviteStatusTitle(agreement.status),
            style: const TextStyle(
              color: ink,
              fontSize: 17,
              height: 1.25,
              fontWeight: FontWeight.w900,
            ),
          ),
          const SizedBox(height: 5),
          Text(
            agreement == null
                ? 'Знакомому не требуется приложение. Он получит обычное сообщение с понятной просьбой.'
                : '${supportInviteModeTitle(agreement.mode)} · ${supportInviteWhen(agreement.scheduledAt)}',
            style: const TextStyle(
              color: Color(0xFF655F6F),
              fontSize: 12.5,
              height: 1.4,
            ),
          ),
          const SizedBox(height: 12),
          SizedBox(
            width: double.infinity,
            child: FilledButton.tonalIcon(
              key: const ValueKey('goal-support-invite'),
              style: FilledButton.styleFrom(
                backgroundColor: const Color(0xFFE2D8F2),
                foregroundColor: const Color(0xFF4D3D6C),
              ),
              onPressed: () => Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => SupportInviteScreen(app: app, item: item),
                ),
              ),
              icon: const Icon(Icons.send_outlined),
              label: Text(
                agreement == null ? 'Позвать человека' : 'Новое приглашение',
              ),
            ),
          ),
          if (all.isNotEmpty) ...[
            const SizedBox(height: 7),
            SizedBox(
              width: double.infinity,
              child: TextButton.icon(
                key: const ValueKey('open-support-agreements'),
                onPressed: () => Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => SupportAgreementsScreen(
                      app: app,
                      actionId: item.id,
                    ),
                  ),
                ),
                icon: const Icon(Icons.history_rounded),
                label: const Text('Открыть договорённости'),
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class SupportInviteScreen extends StatefulWidget {
  const SupportInviteScreen({required this.app, required this.item, super.key});

  final AppState app;
  final ActionItem item;

  @override
  State<SupportInviteScreen> createState() => _SupportInviteScreenState();
}

class _SupportInviteScreenState extends State<SupportInviteScreen> {
  late SupportInviteMode mode;
  late DateTime scheduledAt;
  late int minutes;
  final partner = TextEditingController();
  bool sharing = false;

  @override
  void initState() {
    super.initState();
    mode = switch (widget.item.support) {
      Support.report => SupportInviteMode.report,
      Support.curator => SupportInviteMode.impulse,
      Support.together => SupportInviteMode.together,
      _ => SupportInviteMode.simultaneous,
    };
    final proposed = widget.item.scheduledAt;
    scheduledAt = proposed != null && proposed.isAfter(DateTime.now())
        ? proposed
        : DateTime.now().add(const Duration(minutes: 15));
    minutes = widget.item.minutes > 0 ? widget.item.minutes : 15;
  }

  @override
  void dispose() {
    partner.dispose();
    super.dispose();
  }

  SupportAgreement buildAgreement(SupportInviteStatus status) =>
      SupportAgreement(
        actionId: widget.item.id,
        actionTitle: widget.item.title,
        mode: mode,
        status: status,
        scheduledAt: scheduledAt,
        minutes: minutes,
        partner: partner.text.trim(),
      );

  Future<void> chooseDate() async {
    final value = await showDatePicker(
      context: context,
      initialDate: scheduledAt,
      firstDate: DateTime.now(),
      lastDate: DateTime.now().add(const Duration(days: 365)),
    );
    if (value == null) return;
    setState(() {
      scheduledAt = DateTime(
        value.year,
        value.month,
        value.day,
        scheduledAt.hour,
        scheduledAt.minute,
      );
    });
  }

  Future<void> chooseTime() async {
    final value = await showTimePicker(
      context: context,
      initialTime: TimeOfDay.fromDateTime(scheduledAt),
    );
    if (value == null) return;
    setState(() {
      scheduledAt = DateTime(
        scheduledAt.year,
        scheduledAt.month,
        scheduledAt.day,
        value.hour,
        value.minute,
      );
    });
  }

  void useQuickTime(Duration offset) {
    setState(() => scheduledAt = DateTime.now().add(offset));
  }

  Future<void> saveDraft() async {
    widget.app.upsertSupportAgreement(
      buildAgreement(SupportInviteStatus.draft),
    );
    if (!mounted) return;
    Navigator.pop(context);
  }

  Future<void> shareInvitation() async {
    if (sharing) return;
    final agreement = buildAgreement(SupportInviteStatus.draft);
    widget.app.upsertSupportAgreement(agreement);
    setState(() => sharing = true);
    try {
      await SharePlus.instance.share(
        ShareParams(
          text: supportInviteMessage(agreement),
          subject: 'Поддержка для действия',
        ),
      );
      widget.app.setSupportAgreementStatus(
        agreement,
        SupportInviteStatus.sent,
      );
      if (!mounted) return;
      Navigator.pop(context);
    } catch (_) {
      if (!mounted) return;
      setState(() => sharing = false);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Не удалось открыть отправку. Черновик сохранён.'),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final preview = buildAgreement(SupportInviteStatus.draft);
    return Scaffold(
      appBar: AppBar(title: const Text('Поддержка знакомого')),
      body: ListView(
        key: const ValueKey('support-invite-scroll'),
        padding: const EdgeInsets.fromLTRB(16, 2, 16, 30),
        children: [
          const Text(
            'О чём попросить?',
            style: TextStyle(
              color: ink,
              fontSize: 25,
              height: 1.14,
              fontWeight: FontWeight.w900,
            ),
          ),
          const SizedBox(height: 6),
          const Text(
            'Выберите небольшой и понятный формат. Знакомому не нужно устанавливать приложение или регистрироваться.',
            style: TextStyle(color: Color(0xFF64716D), height: 1.42),
          ),
          const SizedBox(height: 14),
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: const Color(0xFF173C36),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'ДЕЙСТВИЕ',
                  style: TextStyle(
                    color: mint,
                    fontSize: 10,
                    fontWeight: FontWeight.w900,
                    letterSpacing: .8,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  widget.item.title,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 17,
                    height: 1.3,
                    fontWeight: FontWeight.w900,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 17),
          _InviteModeTile(
            key: const ValueKey('invite-mode-together'),
            mode: SupportInviteMode.together,
            selected: mode == SupportInviteMode.together,
            onTap: () => setState(() => mode = SupportInviteMode.together),
          ),
          _InviteModeTile(
            key: const ValueKey('invite-mode-simultaneous'),
            mode: SupportInviteMode.simultaneous,
            selected: mode == SupportInviteMode.simultaneous,
            onTap: () =>
                setState(() => mode = SupportInviteMode.simultaneous),
          ),
          _InviteModeTile(
            key: const ValueKey('invite-mode-report'),
            mode: SupportInviteMode.report,
            selected: mode == SupportInviteMode.report,
            onTap: () => setState(() => mode = SupportInviteMode.report),
          ),
          _InviteModeTile(
            key: const ValueKey('invite-mode-impulse'),
            mode: SupportInviteMode.impulse,
            selected: mode == SupportInviteMode.impulse,
            onTap: () => setState(() => mode = SupportInviteMode.impulse),
          ),
          const SizedBox(height: 15),
          const Text(
            'Когда и на сколько',
            style: TextStyle(fontSize: 17, fontWeight: FontWeight.w900),
          ),
          const SizedBox(height: 9),
          Wrap(
            spacing: 7,
            runSpacing: 7,
            children: [
              ActionChip(
                label: const Text('Через 5 минут'),
                onPressed: () => useQuickTime(const Duration(minutes: 5)),
              ),
              ActionChip(
                label: const Text('Через 15 минут'),
                onPressed: () => useQuickTime(const Duration(minutes: 15)),
              ),
              ActionChip(
                label: const Text('Через час'),
                onPressed: () => useQuickTime(const Duration(hours: 1)),
              ),
            ],
          ),
          const SizedBox(height: 9),
          Card(
            child: Column(
              children: [
                ListTile(
                  leading: const Icon(Icons.calendar_today_outlined),
                  title: const Text('День'),
                  subtitle: Text(shortDate(scheduledAt)),
                  trailing: const Icon(Icons.chevron_right_rounded),
                  onTap: chooseDate,
                ),
                const Divider(height: 1),
                ListTile(
                  leading: const Icon(Icons.schedule_rounded),
                  title: const Text('Время'),
                  subtitle: Text(clockTime(scheduledAt)),
                  trailing: const Icon(Icons.chevron_right_rounded),
                  onTap: chooseTime,
                ),
              ],
            ),
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 7,
            runSpacing: 7,
            children: [5, 10, 15, 25, 45, 60]
                .map(
                  (value) => ChoiceChip(
                    label: Text('$value мин'),
                    selected: minutes == value,
                    onSelected: (_) => setState(() => minutes = value),
                  ),
                )
                .toList(),
          ),
          const SizedBox(height: 15),
          TextField(
            key: const ValueKey('support-partner-name'),
            controller: partner,
            onChanged: (_) => setState(() {}),
            decoration: const InputDecoration(
              labelText: 'Имя человека — необязательно',
              hintText: 'Например: Матвей',
            ),
          ),
          const SizedBox(height: 17),
          Container(
            padding: const EdgeInsets.all(15),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: const Color(0xFFE1DDD4)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'СООБЩЕНИЕ',
                  style: TextStyle(
                    color: green,
                    fontSize: 10,
                    fontWeight: FontWeight.w900,
                    letterSpacing: .8,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  supportInviteMessage(preview),
                  key: const ValueKey('support-invite-preview'),
                  style: const TextStyle(fontSize: 12.5, height: 1.42),
                ),
              ],
            ),
          ),
          const SizedBox(height: 15),
          FilledButton.icon(
            key: const ValueKey('share-support-invite'),
            onPressed: sharing ? null : shareInvitation,
            icon: const Icon(Icons.send_rounded),
            label: Text(sharing ? 'Открываем отправку…' : 'Отправить приглашение'),
          ),
          const SizedBox(height: 7),
          OutlinedButton.icon(
            key: const ValueKey('save-support-draft'),
            onPressed: sharing ? null : saveDraft,
            icon: const Icon(Icons.bookmark_border_rounded),
            label: const Text('Сохранить договорённость без отправки'),
          ),
          const SizedBox(height: 10),
          const Text(
            'Ответ знакомого пока отмечается вручную. Автоматическое подтверждение появится после подключения защищённой синхронизации.',
            textAlign: TextAlign.center,
            style: TextStyle(
              color: Color(0xFF77827E),
              fontSize: 11.5,
              height: 1.4,
            ),
          ),
        ],
      ),
    );
  }
}

class _InviteModeTile extends StatelessWidget {
  const _InviteModeTile({
    required this.mode,
    required this.selected,
    required this.onTap,
    super.key,
  });

  final SupportInviteMode mode;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.only(bottom: 9),
    child: Material(
      color: selected ? const Color(0xFFE8E0F4) : Colors.white,
      clipBehavior: Clip.antiAlias,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(19),
        side: BorderSide(
          color: selected
              ? const Color(0xFF765F9A)
              : const Color(0xFFE0DDD4),
          width: selected ? 1.5 : 1,
        ),
      ),
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(13),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 42,
                height: 42,
                decoration: BoxDecoration(
                  color: selected
                      ? const Color(0xFFD8C9EC)
                      : const Color(0xFFF1EEE8),
                  borderRadius: BorderRadius.circular(14),
                ),
                child: Icon(
                  supportInviteModeIcon(mode),
                  color: selected ? const Color(0xFF594374) : ink,
                ),
              ),
              const SizedBox(width: 11),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      supportInviteModeTitle(mode),
                      style: const TextStyle(
                        color: ink,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      supportInviteModeDescription(mode),
                      style: const TextStyle(
                        color: Color(0xFF65716D),
                        fontSize: 12.5,
                        height: 1.35,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 5),
              Icon(
                selected
                    ? Icons.check_circle_rounded
                    : Icons.radio_button_unchecked_rounded,
                color: selected
                    ? const Color(0xFF66528A)
                    : const Color(0xFFA7AEA9),
              ),
            ],
          ),
        ),
      ),
    ),
  );
}

class SupportAgreementsScreen extends StatelessWidget {
  const SupportAgreementsScreen({
    required this.app,
    this.actionId,
    super.key,
  });

  final AppState app;
  final String? actionId;

  Future<void> resend(BuildContext context, SupportAgreement agreement) async {
    try {
      await SharePlus.instance.share(
        ShareParams(
          text: supportInviteMessage(agreement),
          subject: 'Поддержка для действия',
        ),
      );
      app.setSupportAgreementStatus(agreement, SupportInviteStatus.sent);
    } catch (_) {
      if (!context.mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Не удалось открыть отправку.')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final agreements = app.supportAgreements
        .where((value) => actionId == null || value.actionId == actionId)
        .toList();
    return Scaffold(
      appBar: AppBar(title: const Text('Договорённости')),
      body: agreements.isEmpty
          ? const Center(
              child: Padding(
                padding: EdgeInsets.all(28),
                child: Text(
                  'Пока нет приглашений. Создайте его для ближайшего действия.',
                  textAlign: TextAlign.center,
                ),
              ),
            )
          : ListView(
              padding: const EdgeInsets.fromLTRB(16, 2, 16, 30),
              children: [
                const Text(
                  'Поддержка остаётся конкретной',
                  style: TextStyle(
                    color: ink,
                    fontSize: 23,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                const SizedBox(height: 5),
                const Text(
                  'Приложение хранит договорённость, но не читает переписку. Ответ знакомого отметьте вручную.',
                  style: TextStyle(color: Color(0xFF65716D), height: 1.4),
                ),
                const SizedBox(height: 14),
                ...agreements.map(
                  (agreement) => _SupportAgreementTile(
                    app: app,
                    agreement: agreement,
                    onResend: () => resend(context, agreement),
                  ),
                ),
              ],
            ),
    );
  }
}

class _SupportAgreementTile extends StatelessWidget {
  const _SupportAgreementTile({
    required this.app,
    required this.agreement,
    required this.onResend,
  });

  final AppState app;
  final SupportAgreement agreement;
  final VoidCallback onResend;

  @override
  Widget build(BuildContext context) {
    final active = agreement.status == SupportInviteStatus.draft ||
        agreement.status == SupportInviteStatus.sent;
    final accepted = agreement.status == SupportInviteStatus.accepted;
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: Padding(
        padding: const EdgeInsets.all(15),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  width: 40,
                  height: 40,
                  decoration: BoxDecoration(
                    color: const Color(0xFFE8E0F4),
                    borderRadius: BorderRadius.circular(13),
                  ),
                  child: Icon(
                    supportInviteModeIcon(agreement.mode),
                    color: const Color(0xFF66528A),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        agreement.actionTitle,
                        style: const TextStyle(
                          color: ink,
                          fontSize: 15.5,
                          height: 1.3,
                          fontWeight: FontWeight.w900,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '${supportInviteModeTitle(agreement.mode)} · ${supportInviteWhen(agreement.scheduledAt)}',
                        style: const TextStyle(
                          color: Color(0xFF65716D),
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ),
                PopupMenuButton<String>(
                  onSelected: (value) {
                    if (value == 'cancel') {
                      app.setSupportAgreementStatus(
                        agreement,
                        SupportInviteStatus.cancelled,
                      );
                    }
                  },
                  itemBuilder: (_) => const [
                    PopupMenuItem(
                      value: 'cancel',
                      child: Text('Отменить договорённость'),
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 10),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
              decoration: BoxDecoration(
                color: supportInviteStatusColor(agreement.status),
                borderRadius: BorderRadius.circular(20),
              ),
              child: Text(
                supportInviteStatusTitle(agreement.status),
                style: const TextStyle(
                  color: ink,
                  fontSize: 11.5,
                  fontWeight: FontWeight.w800,
                ),
              ),
            ),
            const SizedBox(height: 11),
            if (active) ...[
              SizedBox(
                width: double.infinity,
                child: OutlinedButton.icon(
                  onPressed: onResend,
                  icon: const Icon(Icons.send_outlined),
                  label: Text(
                    agreement.status == SupportInviteStatus.draft
                        ? 'Отправить приглашение'
                        : 'Отправить ещё раз',
                  ),
                ),
              ),
              const SizedBox(height: 6),
              SizedBox(
                width: double.infinity,
                child: FilledButton.tonalIcon(
                  key: ValueKey('accept-support-${agreement.id}'),
                  onPressed: () => app.setSupportAgreementStatus(
                    agreement,
                    SupportInviteStatus.accepted,
                  ),
                  icon: const Icon(Icons.check_circle_outline_rounded),
                  label: const Text('Человек ответил: «Я рядом»'),
                ),
              ),
            ] else if (accepted)
              SizedBox(
                width: double.infinity,
                child: FilledButton.tonalIcon(
                  onPressed: () => app.setSupportAgreementStatus(
                    agreement,
                    SupportInviteStatus.completed,
                  ),
                  icon: const Icon(Icons.done_all_rounded),
                  label: const Text('Договорённость выполнена'),
                ),
              ),
          ],
        ),
      ),
    );
  }
}

String supportInviteModeTitle(SupportInviteMode mode) => switch (mode) {
  SupportInviteMode.together => 'Побыть рядом на аудио или видео',
  SupportInviteMode.simultaneous => 'Начать одновременно',
  SupportInviteMode.report => 'Спросить о результате',
  SupportInviteMode.impulse => 'Дать короткий внешний толчок',
};

String supportInviteModeDescription(SupportInviteMode mode) => switch (mode) {
  SupportInviteMode.together =>
    'Вы остаётесь на связи, даже если каждый занимается своим делом.',
  SupportInviteMode.simultaneous =>
    'Достаточно договориться об одном времени начала.',
  SupportInviteMode.report =>
    'Знакомый пишет после выбранного времени и спрашивает, что получилось.',
  SupportInviteMode.impulse =>
    'В нужный момент человек отправляет короткое сообщение: «Начинай».',
};

IconData supportInviteModeIcon(SupportInviteMode mode) => switch (mode) {
  SupportInviteMode.together => Icons.video_call_outlined,
  SupportInviteMode.simultaneous => Icons.play_circle_outline_rounded,
  SupportInviteMode.report => Icons.fact_check_outlined,
  SupportInviteMode.impulse => Icons.bolt_outlined,
};

String supportInviteStatusTitle(SupportInviteStatus status) => switch (status) {
  SupportInviteStatus.draft => 'Черновик договорённости',
  SupportInviteStatus.sent => 'Приглашение отправлено',
  SupportInviteStatus.accepted => 'Человек согласился быть рядом',
  SupportInviteStatus.completed => 'Договорённость выполнена',
  SupportInviteStatus.cancelled => 'Договорённость отменена',
};

Color supportInviteStatusColor(SupportInviteStatus status) => switch (status) {
  SupportInviteStatus.draft => const Color(0xFFF1EEE8),
  SupportInviteStatus.sent => const Color(0xFFE8E0F4),
  SupportInviteStatus.accepted => const Color(0xFFDDEFE7),
  SupportInviteStatus.completed => const Color(0xFFDCE9F3),
  SupportInviteStatus.cancelled => const Color(0xFFE9E7E2),
};

bool _sameSupportInviteDay(DateTime a, DateTime b) =>
    a.year == b.year && a.month == b.month && a.day == b.day;

String supportInviteWhen(DateTime value) {
  final now = DateTime.now();
  if (_sameSupportInviteDay(value, now)) return 'сегодня в ${clockTime(value)}';
  final tomorrow = now.add(const Duration(days: 1));
  if (_sameSupportInviteDay(value, tomorrow)) {
    return 'завтра в ${clockTime(value)}';
  }
  return '${shortDate(value)} в ${clockTime(value)}';
}

String supportInviteMessage(SupportAgreement agreement) {
  final greeting = agreement.partner.trim().isEmpty
      ? 'Привет!'
      : '${agreement.partner.trim()}, привет!';
  final request = switch (agreement.mode) {
    SupportInviteMode.together =>
      'Побудешь со мной на аудио или видео, пока я занимаюсь своим делом? Ты можешь в это время делать что-то своё.',
    SupportInviteMode.simultaneous =>
      'Давай начнём одновременно: каждый занимается своим делом, но стартуем в одно время.',
    SupportInviteMode.report =>
      'Сможешь после этого времени спросить меня, что получилось?',
    SupportInviteMode.impulse =>
      'Сможешь в это время написать мне коротко: «Начинай»?',
  };
  final reply = switch (agreement.mode) {
    SupportInviteMode.together => 'Ответь, пожалуйста: «Я рядом» или «Сейчас не могу».',
    SupportInviteMode.simultaneous =>
      'Ответь, пожалуйста: «Начинаем» или предложи другое время.',
    SupportInviteMode.report =>
      'Ответь, пожалуйста: «Спрошу» или «Сейчас не получится».',
    SupportInviteMode.impulse =>
      'Ответь, пожалуйста: «Напомню» или «Сейчас не получится».',
  };
  return '$greeting\n\n'
      'Мне нужна небольшая поддержка, чтобы начать конкретное действие.\n\n'
      'Действие: ${agreement.actionTitle}\n'
      'Когда: ${supportInviteWhen(agreement.scheduledAt)}\n'
      'Время: ${agreement.minutes} мин\n\n'
      '$request\n\n'
      '$reply\n\n'
      'Устанавливать приложение не нужно.';
}

'''
speech_at = text.index('class Speech {')
text = text[:speech_at] + support_ui + text[speech_at:]

if 'version: 0.9.0+25' not in pubspec:
    raise SystemExit('Expected v0.9.0 version not found')
pubspec = pubspec.replace('version: 0.9.0+25', 'version: 0.10.0+26', 1)

main_path.write_text(text, encoding='utf-8')
pubspec_path.write_text(pubspec, encoding='utf-8')
print('Applied v0.10.0 support friend flow')
