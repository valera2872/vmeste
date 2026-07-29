from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')
text = text.replace('FontWeight.w650', 'FontWeight.w600')
text = text.replace('FontWeight.w750', 'FontWeight.w700')
text = text.replace(
    "'Найдите свой способ\\nдвигаться к цели'",
    "'Найдите свой способ двигаться к цели'",
)
text = text.replace(
    "'Подберите поддержку\\nпод конкретное действие'",
    "'Подберите поддержку под конкретное действие'",
)

old = '''                const Text(
                  'Вместе к цели',
                  style: TextStyle(
                    color: ink,
                    fontSize: 15.5,
                    fontWeight: FontWeight.w700,
                    letterSpacing: -.15,
                  ),
                ),
                const Spacer(),'''
new = '''                const Expanded(
                  child: Text(
                    'Вместе к цели',
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(
                      color: ink,
                      fontSize: 15.5,
                      fontWeight: FontWeight.w700,
                      letterSpacing: -.15,
                    ),
                  ),
                ),
                const SizedBox(width: 8),'''
if old not in text:
    raise SystemExit('Onboarding brand row not found')
text = text.replace(old, new, 1)

old_button = '''                TextButton(
                  onPressed: close,
                  child: Text(widget.preview ? 'Закрыть' : 'Пропустить'),
                ),'''
new_button = '''                TextButton(
                  style: TextButton.styleFrom(
                    minimumSize: Size.zero,
                    padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 7),
                    tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                  ),
                  onPressed: close,
                  child: Text(widget.preview ? 'Закрыть' : 'Пропустить'),
                ),'''
if old_button not in text:
    raise SystemExit('Onboarding close button not found')
text = text.replace(old_button, new_button, 1)

ignore = '// ignore_for_file: prefer_const_constructors, prefer_const_literals_to_create_immutables\n\n'
if not text.startswith('// ignore_for_file: prefer_const_constructors'):
    text = ignore + text
path.write_text(text, encoding='utf-8')
print('Normalized v0.6.6 copy, typography and narrow layout')
