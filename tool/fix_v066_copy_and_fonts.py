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
ignore = '// ignore_for_file: prefer_const_constructors, prefer_const_literals_to_create_immutables\n\n'
if not text.startswith('// ignore_for_file: prefer_const_constructors'):
    text = ignore + text
path.write_text(text, encoding='utf-8')
print('Normalized v0.6.6 typography and preserved approved copy')
