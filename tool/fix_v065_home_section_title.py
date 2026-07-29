from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

if 'class _HomeSectionTitle extends StatelessWidget' not in text:
    marker = 'class IntentChooserPage extends StatelessWidget'
    widget = r'''class _HomeSectionTitle extends StatelessWidget {
  const _HomeSectionTitle({
    required this.title,
    this.subtitle,
    required this.count,
  });

  final String title;
  final String? subtitle;
  final int count;

  @override
  Widget build(BuildContext context) => Row(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Expanded(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: const TextStyle(
                color: ink,
                fontSize: 15.5,
                fontWeight: FontWeight.w700,
              ),
            ),
            if (subtitle != null) ...[
              const SizedBox(height: 2),
              Text(
                subtitle!,
                style: const TextStyle(
                  color: Color(0xFF687470),
                  fontSize: 12,
                  height: 1.3,
                ),
              ),
            ],
          ],
        ),
      ),
      Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
        decoration: BoxDecoration(
          color: const Color(0xFFE5EFEB),
          borderRadius: BorderRadius.circular(20),
        ),
        child: Text(
          '$count',
          style: const TextStyle(
            color: green,
            fontSize: 11.5,
            fontWeight: FontWeight.w700,
          ),
        ),
      ),
    ],
  );
}

'''
    text = text.replace(marker, widget + marker, 1)

key_text = "key: const ValueKey('today-primary-action'),"
if key_text in text:
    key_index = text.index(key_text)
    on_pressed = text.index('onPressed:', key_index)
    between = text[key_index:on_pressed]
    if 'style:' not in between:
        indent_start = text.rfind('\n', key_index) + 1
        indent = text[indent_start:key_index]
        style = (
            f"{indent}style: FilledButton.styleFrom(\n"
            f"{indent}  minimumSize: const Size(0, 46),\n"
            f"{indent}  tapTargetSize: MaterialTapTargetSize.shrinkWrap,\n"
            f"{indent}),\n"
        )
        text = text[:on_pressed] + style + text[on_pressed:]

path.write_text(text, encoding='utf-8')
print('Restored shared home section title and compact primary action')
