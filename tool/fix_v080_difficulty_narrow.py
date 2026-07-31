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
path.write_text(text, encoding='utf-8')
print('Adapted start difficulty cards to narrow phones')
