from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

old = '''      SizedBox(height: 16),
      _IntroQuietNote(
        icon: Icons.science_outlined,'''
new = '''      SizedBox(height: 16),
      _IntroFlowLine(),
      SizedBox(height: 16),
      _IntroQuietNote(
        icon: Icons.science_outlined,'''

if old not in text:
    raise SystemExit('Simplified support-screen research note anchor not found')
text = text.replace(old, new, 1)
path.write_text(text, encoding='utf-8')
print('Restored the useful action flow line in simplified onboarding')
