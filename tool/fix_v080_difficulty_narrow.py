from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

start = text.index('class _StartDifficultyOption extends StatelessWidget')
end = text.index('class Blocker extends StatelessWidget', start)

replacement = r'''class _StartDifficultyOption extends StatelessWidget {
  const _StartDifficultyOption({
    required this.title,
    required this.text,
    required this.icon,
    required this.onTap,
  });

  final String title;
  final String text;
  final IconData icon;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.only(bottom: 10),
    child: Material(
      color: Colors.white,
      clipBehavior: Clip.antiAlias,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
        side: const BorderSide(color: Color(0xFFE0E5E1)),
      ),
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.fromLTRB(12, 12, 10, 12),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: const Color(0xFFE7F2ED),
                  borderRadius: BorderRadius.circular(13),
                ),
                child: Icon(icon, color: green, size: 21),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: const TextStyle(
                        fontWeight: FontWeight.w800,
                        height: 1.25,
                      ),
                    ),
                    const SizedBox(height: 5),
                    Text(
                      text,
                      style: const TextStyle(
                        color: Color(0xFF66736E),
                        fontSize: 12.5,
                        height: 1.35,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 4),
              const Padding(
                padding: EdgeInsets.only(top: 9),
                child: Icon(
                  Icons.chevron_right_rounded,
                  size: 19,
                  color: Color(0xFF8B9691),
                ),
              ),
            ],
          ),
        ),
      ),
    ),
  );
}'''

text = text[:start] + replacement + '\n\n' + text[end:]

old_session_support = r'''                Row(
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
                ),'''
new_session_support = r'''                Row(
                  children: [
                    Icon(
                      supportIcon(widget.item.support),
                      color: mint,
                      size: 20,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        supportName(widget.item.support).toUpperCase(),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                          color: mint,
                          fontSize: 11.5,
                          fontWeight: FontWeight.w900,
                          letterSpacing: .8,
                        ),
                      ),
                    ),
                  ],
                ),'''
if old_session_support not in text:
    raise SystemExit('Session support heading anchor not found')
text = text.replace(old_session_support, new_session_support, 1)

path.write_text(text, encoding='utf-8')
print('Adapted start difficulty and session support labels to narrow phones')

# Keep the historical build chain intact while materializing the next releases.
exec(
    Path('tool/rewrite_v090_digital_assistant.py').read_text(encoding='utf-8'),
    {'__name__': '__main__'},
)
exec(
    Path('tool/rewrite_v090_tests.py').read_text(encoding='utf-8'),
    {'__name__': '__main__'},
)
exec(
    Path('tool/rewrite_v0100_support_friend.py').read_text(encoding='utf-8'),
    {'__name__': '__main__'},
)
exec(
    Path('tool/rewrite_v0100_tests.py').read_text(encoding='utf-8'),
    {'__name__': '__main__'},
)
exec(
    Path('tool/run_v0110_together_start.py').read_text(encoding='utf-8'),
    {'__name__': '__main__'},
)
exec(
    Path('tool/fix_v0110_scoped_timestamps.py').read_text(encoding='utf-8'),
    {'__name__': '__main__'},
)
exec(
    Path('tool/rewrite_v0110_tests.py').read_text(encoding='utf-8'),
    {'__name__': '__main__'},
)
