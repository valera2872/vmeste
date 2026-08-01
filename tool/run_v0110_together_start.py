from pathlib import Path

source_path = Path('tool/rewrite_v0110_together_start.py')
source = source_path.read_text(encoding='utf-8')

old_constructor_patch = r"""replace_once(
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
)"""

new_constructor_patch = r"""replace_once(
    '''class Session extends StatefulWidget {
  const Session({
    required this.app,
    required this.item,
    this.openDifficultyOnEnter = false,
    super.key,
  });
  final AppState app;
  final ActionItem item;
  final bool openDifficultyOnEnter;''',
    '''class Session extends StatefulWidget {
  const Session({
    required this.app,
    required this.item,
    this.openDifficultyOnEnter = false,
    this.agreement,
    super.key,
  });
  final AppState app;
  final ActionItem item;
  final bool openDifficultyOnEnter;
  final SupportAgreement? agreement;''',
    'session support agreement constructor',
)"""

if old_constructor_patch not in source:
    raise SystemExit('Original v0.11 Session patch block not found')
source = source.replace(old_constructor_patch, new_constructor_patch, 1)

# A periodic timer is unnecessary for this release and leaves an active timer in
# widget tests. The time hint is refreshed whenever the screen is opened or its
# state changes.
old_ticker = r"""class _TogetherStartScreenState extends State<TogetherStartScreen> {
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

  Future<void> sendReady() async {"""
new_ticker = r"""class _TogetherStartScreenState extends State<TogetherStartScreen> {
  Future<void> sendReady() async {"""
if old_ticker not in source:
    raise SystemExit('Original v0.11 countdown ticker block not found')
source = source.replace(old_ticker, new_ticker, 1)

exec(compile(source, str(source_path), 'exec'), {'__name__': '__main__'})
