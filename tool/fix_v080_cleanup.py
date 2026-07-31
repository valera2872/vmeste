from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

start = text.find('class _HomeSectionTitle extends StatelessWidget')
if start >= 0:
    end = text.find('class _PremiumTodayHeader extends StatelessWidget', start)
    if end < 0:
        raise SystemExit('Next class after _HomeSectionTitle not found')
    text = text[:start] + text[end:]

path.write_text(text, encoding='utf-8')
print('Removed obsolete v0.8.0 workspace helper')
