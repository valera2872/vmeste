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
      child: ListTile(
        contentPadding: const EdgeInsets.fromLTRB(14, 10, 12, 10),
        leading: Container(
          width: 44,
          height: 44,
          decoration: BoxDecoration(
            color: const Color(0xFFE7F2ED),
            borderRadius: BorderRadius.circular(14),
          ),
          child: Icon(icon, color: green),
        ),
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.w800)),
        subtitle: Padding(
          padding: const EdgeInsets.only(top: 5),
          child: Text(text),
        ),
        trailing: const Icon(Icons.chevron_right_rounded),
        onTap: onTap,
      ),
    ),
  );
}'''
text = text[:start] + replacement + '\n\n' + text[end:]
path.write_text(text, encoding='utf-8')
print('Fixed v0.7 start help material surface')
