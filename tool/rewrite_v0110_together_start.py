from pathlib import Path

main_path = Path('lib/main.dart')
pubspec_path = Path('pubspec.yaml')
text = main_path.read_text(encoding='utf-8')
pubspec = pubspec_path.read_text(encoding='utf-8')

if 'class TogetherStartScreen' in text:
    print('v0.11.0 together start already applied')
    raise SystemExit(0)


def replace_once(old: str, new: str, label: str) -> None:
    global text
    if old not in text:
        raise SystemExit(f'{label} anchor not found')
    text = text.replace(old, new, 1)


replace_once(
    'enum SupportInviteStatus { draft, sent, accepted, completed, cancelled }',
    'enum SupportInviteStatus { draft, sent, accepted, started, completed, cancelled }',
    'support started status',
)

replace_once(
    "    this.partner = '',\n    String? id,\n    DateTime? createdAt,\n    DateTime? updatedAt,",
    "    this.partner = '',\n    this.startedAt,\n    this.completedAt,\n    String? id,\n    DateTime? createdAt,\n    DateTime? updatedAt,",
    'support agreement constructor timestamps',
)
replace_once(
    "  final String partner;\n  final DateTime createdAt;\n  DateTime updatedAt;",
    "  final String partner;\n  final DateTime createdAt;\n  DateTime updatedAt;\n  DateTime? startedAt;\n  DateTime? completedAt;",
    'support agreement timestamp fields',
)
replace_once(
    "    'updatedAt': updatedAt.toIso8601String(),\n  };",
    "    'updatedAt': updatedAt.toIso8601String(),\n    'startedAt': startedAt?.toIso8601String(),\n    'completedAt': completedAt?.toIso8601String(),\n  };",
    'support agreement timestamp json',
)
replace_once(
    "      updatedAt: DateTime.tryParse((json['updatedAt'] ?? '').toString()) ?? now,\n    );",
    "      updatedAt: DateTime.tryParse((json['updatedAt'] ?? '').toString()) ?? now,\n      startedAt: DateTime.tryParse((json['startedAt'] ?? '').toString()),\n      completedAt: DateTime.tryParse((json['completedAt'] ?? '').toString()),\n    );",
    'support agreement timestamp restore',
)

replace_once(
    'static const schemaVersion = 4;',
    'static const schemaVersion = 5;',
    'schema version 5',
)

notification_methods = r'''  Future<bool> scheduleSupportAgreement(
    SupportAgreement agreement,
  ) async {
    if (!ready) return false;
    try {
      if (!await _permissionAllowed()) return false;
      final now = DateTime.now();
      final early = agreement.scheduledAt.subtract(const Duration(minutes: 5));
      final when = early.isAfter(now) ? early : agreement.scheduledAt;
      if (!when.isAfter(now)) return false;
      await cancelSupportAgreement(agreement.id);
      final partner = agreement.partner.trim();
      final suffix = partner.isEmpty ? '' : ' с $partner';
      await _scheduleOne(
        id: _id('support:${agreement.id}'),
        title: 'Скоро совместный старт$suffix: ${agreement.actionTitle}',
        when: when,
        payload: 'support:${agreement.id}',
      );
      return true;
    } catch (_) {
      return false;
    }
  }

  Future<void> cancelSupportAgreement(String agreementId) async {
    if (!ready) return;
    try {
      await plugin.cancel(id: _id('support:$agreementId'));
    } catch (_) {}
  }

'''
replace_once(
    '  Future<void> cancel(String id) async {',
    notification_methods + '  Future<void> cancel(String id) async {',
    'support agreement notification methods',
)

replace_once(
    '''  void setSupportAgreementStatus(
    SupportAgreement agreement,
    SupportInviteStatus status,
  ) {
    agreement.status = status;
    agreement.updatedAt = DateTime.now();
    notifyListeners();
    save();
  }''',
    '''  void setSupportAgreementStatus(
    SupportAgreement agreement,
    SupportInviteStatus status,
  ) {
    final now = DateTime.now();
    agreement.status = status;
    agreement.updatedAt = now;
    if (status == SupportInviteStatus.started) {
      agreement.startedAt ??= now;
    }
    if (status == SupportInviteStatus.completed) {
      agreement.completedAt = now;
    }
    if (status == SupportInviteStatus.sent ||
        status == SupportInviteStatus.accepted) {
      unawaited(
        NotificationService.instance.scheduleSupportAgreement(agreement),
      );
    } else if (status == SupportInviteStatus.started ||
        status == SupportInviteStatus.completed ||
        status == SupportInviteStatus.cancelled) {
      unawaited(
        NotificationService.instance.cancelSupportAgreement(agreement.id),
      );
    }
    notifyListeners();
    save();
  }''',
    'support agreement status lifecycle',
)

replace_once(
    '''    final all = app.supportAgreements
        .where((value) => value.actionId == item.id)
        .toList();
    return Container(''',
    '''    final all = app.supportAgreements
        .where((value) => value.actionId == item.id)
        .toList();
    final readyToStart = agreement != null &&
        (agreement.status == SupportInviteStatus.accepted ||
            agreement.status == SupportInviteStatus.started);
    return Container(''',
    'goal agreement ready state',
)

replace_once(
    '''              onPressed: () => Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => SupportInviteScreen(app: app, item: item),
                ),
              ),
              icon: const Icon(Icons.send_outlined),
              label: Text(
                agreement == null ? 'Позвать человека' : 'Новое приглашение',
              ),''',
    '''              onPressed: () => Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => readyToStart
                      ? TogetherStartScreen(
                          app: app,
                          item: item,
                          agreement: agreement!,
                        )
                      : SupportInviteScreen(app: app, item: item),
                ),
              ),
              icon: Icon(
                readyToStart
                    ? Icons.play_circle_outline_rounded
                    : Icons.send_outlined,
              ),
              label: Text(
                readyToStart
                    ? agreement!.status == SupportInviteStatus.started
                          ? 'Вернуться к совместному действию'
                          : 'Перейти к совместному старту'
                    : agreement == null
                    ? 'Позвать человека'
                    : 'Новое приглашение',
              ),''',
    'goal agreement primary action',
)

replace_once(
    '''    final active = agreement.status == SupportInviteStatus.draft ||
        agreement.status == SupportInviteStatus.sent;
    final accepted = agreement.status == SupportInviteStatus.accepted;
    return Card(''',
    '''    final active = agreement.status == SupportInviteStatus.draft ||
        agreement.status == SupportInviteStatus.sent;
    final accepted = agreement.status == SupportInviteStatus.accepted;
    final started = agreement.status == SupportInviteStatus.started;
    ActionItem? linkedAction;
    for (final item in app.actions) {
      if (item.id == agreement.actionId) {
        linkedAction = item;
        break;
      }
    }
    return Card(''',
    'agreement tile linked action',
)

replace_once(
    '''            ] else if (accepted)
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
              ),''',
    '''            ] else if ((accepted || started) && linkedAction != null)
              SizedBox(
                width: double.infinity,
                child: FilledButton.tonalIcon(
                  key: ValueKey('open-together-${agreement.id}'),
                  onPressed: () => Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) => TogetherStartScreen(
                        app: app,
                        item: linkedAction!,
                        agreement: agreement,
                      ),
                    ),
                  ),
                  icon: Icon(
                    started
                        ? Icons.timelapse_rounded
                        : Icons.play_circle_outline_rounded,
                  ),
                  label: Text(
                    started
                        ? 'Вернуться к совместному действию'
                        : 'Перейти к совместному старту',
                  ),
                ),
              )
            else if (accepted || started)
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
              ),''',
    'agreement tile start action',
)

replace_once(
    "  SupportInviteStatus.accepted => 'Человек согласился быть рядом',\n  SupportInviteStatus.completed => 'Договорённость выполнена',",
    "  SupportInviteStatus.accepted => 'Человек согласился быть рядом',\n  SupportInviteStatus.started => 'Совместное действие началось',\n  SupportInviteStatus.completed => 'Договорённость выполнена',",
    'support started status title',
)
replace_once(
    "  SupportInviteStatus.accepted => const Color(0xFFDDEFE7),\n  SupportInviteStatus.completed => const Color(0xFFDCE9F3),",
    "  SupportInviteStatus.accepted => const Color(0xFFDDEFE7),\n  SupportInviteStatus.started => const Color(0xFFFFE8B8),\n  SupportInviteStatus.completed => const Color(0xFFDCE9F3),",
    'support started status color',
)

start_screen = r'''class TogetherStartScreen extends StatefulWidget {
  const TogetherStartScreen({
    required this.app,
    required this.item,
    required this.agreement,
    super.key,
  });

  final AppState app;
  final ActionItem item;
  final SupportAgreement agreement;

  @override
  State<TogetherStartScreen> createState() => _TogetherStartScreenState();
}

class _TogetherStartScreenState extends State<TogetherStartScreen> {
  Timer? ticker;

  @override
  void initState() {
    super.initState();
    ticker = Timer.periodic(const Duration(seconds: 30), (_) {
      if (mounted) setState(() {});
    });
  }

  @override
  void dispose() {
    ticker?.cancel();
    super.dispose();
  }

  Future<void> sendReady() async {
    final partner = widget.agreement.partner.trim();
    final greeting = partner.isEmpty ? 'Я готов.' : '$partner, я готов.';
    final text = switch (widget.agreement.mode) {
      SupportInviteMode.together =>
        '$greeting Можем выходить на связь и начинать: ${widget.item.title}',
      SupportInviteMode.simultaneous =>
        '$greeting Начинаем одновременно: ${widget.item.title}',
      SupportInviteMode.report =>
        '$greeting Начинаю: ${widget.item.title}. Спроси меня о результате через ${widget.agreement.minutes} мин.',
      SupportInviteMode.impulse =>
        '$greeting Я на месте. Напиши мне коротко: «Начинай».',
    };
    try {
      await SharePlus.instance.share(
        ShareParams(text: text, subject: 'Начинаем вместе'),
      );
    } catch (_) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Не удалось открыть отправку.')),
      );
    }
  }

  Future<void> openAction() async {
    if (widget.item.useTimer && widget.item.minutes > 0) {
      await Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => Session(
            app: widget.app,
            item: widget.item,
            agreement: widget.agreement,
          ),
        ),
      );
      if (mounted) setState(() {});
      return;
    }
    widget.app.setSupportAgreementStatus(
      widget.agreement,
      SupportInviteStatus.started,
    );
    setState(() {});
  }

  Future<void> recordResult() async {
    final state = await showModalBottomSheet<ResultState>(
      context: context,
      showDragHandle: true,
      builder: (sheetContext) =>
          Finish(onFinish: (value) => Navigator.pop(sheetContext, value)),
    );
    if (state == null || !mounted) return;
    if (state == ResultState.moved) {
      final when = await showActionSchedule(context, widget.item.scheduledAt);
      if (when == null || !mounted) return;
      await widget.app.reschedule(widget.item, when);
    } else {
      widget.app.complete(widget.item, state);
    }
    widget.app.setSupportAgreementStatus(
      widget.agreement,
      SupportInviteStatus.completed,
    );
    if (!mounted) return;
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(
        builder: (_) => ResultPage(
          app: widget.app,
          item: widget.item,
          state: state,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final started = widget.agreement.status == SupportInviteStatus.started;
    final partner = widget.agreement.partner.trim();
    return Scaffold(
      appBar: AppBar(title: const Text('Начать вместе')),
      body: ListView(
        key: const ValueKey('together-start-scroll'),
        padding: const EdgeInsets.fromLTRB(16, 2, 16, 30),
        children: [
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: const Color(0xFF173C36),
              borderRadius: BorderRadius.circular(25),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(Icons.people_alt_rounded, color: mint),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        started ? 'ВЫ УЖЕ НАЧАЛИ' : 'ДОГОВОРЁННОСТЬ ГОТОВА',
                        style: const TextStyle(
                          color: mint,
                          fontSize: 10.5,
                          fontWeight: FontWeight.w900,
                          letterSpacing: .8,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Text(
                  widget.item.title,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 24,
                    height: 1.18,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                const SizedBox(height: 9),
                Text(
                  supportInviteModeTitle(widget.agreement.mode),
                  style: const TextStyle(
                    color: Color(0xFFD6E3DF),
                    height: 1.35,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),
          Container(
            padding: const EdgeInsets.all(17),
            decoration: BoxDecoration(
              color: const Color(0xFFFFFBF2),
              borderRadius: BorderRadius.circular(21),
              border: Border.all(color: const Color(0xFFE9DFC8)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  started
                      ? 'Совместный старт отмечен'
                      : supportStartCountdown(widget.agreement.scheduledAt),
                  key: const ValueKey('together-countdown'),
                  style: const TextStyle(
                    color: ink,
                    fontSize: 18,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  '${supportInviteWhen(widget.agreement.scheduledAt)} · ${widget.agreement.minutes} мин${partner.isEmpty ? '' : ' · $partner'}',
                  style: const TextStyle(
                    color: Color(0xFF65716D),
                    height: 1.35,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),
          OutlinedButton.icon(
            key: const ValueKey('send-ready-message'),
            onPressed: sendReady,
            icon: const Icon(Icons.send_outlined),
            label: const Text('Написать: «Я готов»'),
          ),
          const SizedBox(height: 8),
          FilledButton.icon(
            key: const ValueKey('open-together-action'),
            onPressed: openAction,
            icon: Icon(
              started ? Icons.play_arrow_rounded : Icons.play_circle_rounded,
            ),
            label: Text(
              widget.item.useTimer && widget.item.minutes > 0
                  ? started
                        ? 'Продолжить действие'
                        : 'Открыть действие и начать'
                  : started
                  ? 'Действие начато'
                  : 'Мы начали',
            ),
          ),
          if (started && (!widget.item.useTimer || widget.item.minutes <= 0)) ...[
            const SizedBox(height: 8),
            FilledButton.tonalIcon(
              key: const ValueKey('record-together-result'),
              onPressed: recordResult,
              icon: const Icon(Icons.check_circle_outline_rounded),
              label: const Text('Записать результат'),
            ),
          ],
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(15),
            decoration: BoxDecoration(
              color: const Color(0xFFF0ECF8),
              borderRadius: BorderRadius.circular(20),
            ),
            child: const Text(
              'Аудио или видео остаётся в привычном мессенджере. Приложение хранит только договорённость и результат действия — переписку оно не читает.',
              style: TextStyle(
                color: Color(0xFF615A6B),
                fontSize: 12.5,
                height: 1.42,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

String supportStartCountdown(DateTime scheduledAt) {
  final difference = scheduledAt.difference(DateTime.now());
  if (difference.inMinutes > 90) {
    return 'Старт ${supportInviteWhen(scheduledAt)}';
  }
  if (difference.inMinutes > 1) {
    return 'До старта около ${difference.inMinutes} мин';
  }
  if (difference.inSeconds > 0) return 'Пора приготовиться к старту';
  if (difference.inMinutes >= -15) return 'Можно начинать сейчас';
  return 'Запланированное время уже наступило';
}

'''
speech_at = text.index('class Speech {')
text = text[:speech_at] + start_screen + text[speech_at:]

replace_once(
    '''class Session extends StatefulWidget {
  const Session({required this.app, required this.item, super.key});
  final AppState app;
  final ActionItem item;''',
    '''class Session extends StatefulWidget {
  const Session({
    required this.app,
    required this.item,
    this.agreement,
    super.key,
  });
  final AppState app;
  final ActionItem item;
  final SupportAgreement? agreement;''',
    'session support agreement constructor',
)
replace_once(
    '''  void start() {
    setState(() => started = true);
    timer = Timer.periodic(const Duration(seconds: 1), (_) {''',
    '''  void start() {
    if (widget.agreement != null) {
      widget.app.setSupportAgreementStatus(
        widget.agreement!,
        SupportInviteStatus.started,
      );
    }
    setState(() => started = true);
    timer = Timer.periodic(const Duration(seconds: 1), (_) {''',
    'session mark agreement started',
)
replace_once(
    '''    } else {
      widget.app.complete(widget.item, state);
    }
    if (!mounted) return;''',
    '''    } else {
      widget.app.complete(widget.item, state);
    }
    if (widget.agreement != null) {
      widget.app.setSupportAgreementStatus(
        widget.agreement!,
        SupportInviteStatus.completed,
      );
    }
    if (!mounted) return;''',
    'session mark agreement completed',
)

support_start = text.index('class SupportScreen extends StatelessWidget')
support_end = text.index('class TogetherActionCard', support_start)
support_block = text[support_start:support_end]
support_anchor = "          const SizedBox(height: 20),\n          if (active.isNotEmpty) ...["
if support_anchor not in support_block:
    raise SystemExit('Support screen agreement entry anchor not found')
support_block = support_block.replace(
    support_anchor,
    '''          if (app.supportAgreements.isNotEmpty) ...[
            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                key: const ValueKey('open-all-support-agreements'),
                onPressed: () => Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => SupportAgreementsScreen(app: app),
                  ),
                ),
                icon: const Icon(Icons.event_available_outlined),
                label: Text(
                  'Договорённости (${app.supportAgreements.length})',
                ),
              ),
            ),
          ],
          const SizedBox(height: 20),
          if (active.isNotEmpty) ...[''',
    1,
)
text = text[:support_start] + support_block + text[support_end:]

if 'version: 0.10.0+26' not in pubspec:
    raise SystemExit('Expected v0.10.0 version not found')
pubspec = pubspec.replace('version: 0.10.0+26', 'version: 0.11.0+27', 1)

main_path.write_text(text, encoding='utf-8')
pubspec_path.write_text(pubspec, encoding='utf-8')
print('Applied v0.11.0 together start flow')
