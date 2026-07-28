from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')
marker = 'class _PremiumEmptyState extends StatelessWidget'
if marker in text:
    start = text.index(marker)
    end = text.index('class IntentChooserPage extends StatelessWidget', start)
    text = text[:start] + text[end:]
path.write_text(text, encoding='utf-8')
