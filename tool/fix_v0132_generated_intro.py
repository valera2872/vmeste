from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

# The width is supplied by the surrounding SizedBox. Remove the temporary
# constructor marker so the generated Dart has no unused field.
for fragment in [
    '            widthFactor: 0,\n',
    '    required this.widthFactor,\n',
    '  final double widthFactor;\n',
]:
    text = text.replace(fragment, '')

path.write_text(text, encoding='utf-8')
print('Cleaned v0.13.2 generated introduction fields')
