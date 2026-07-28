from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')
start = text.index('class _PremiumEditorHeading extends StatelessWidget')
end = text.index('class Speech', start)
text = text[:start] + text[end:]
path.write_text(text, encoding='utf-8')
