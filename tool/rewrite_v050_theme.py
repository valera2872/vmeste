from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

old = '''        cardTheme: CardThemeData(
          color: Colors.white,
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(24),
          ),
        ),'''
new = '''        cardTheme: CardThemeData(
          color: Colors.white,
          elevation: 0.7,
          shadowColor: const Color(0x160A2A26),
          surfaceTintColor: Colors.white,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(22),
            side: const BorderSide(color: Color(0x0F132D2A)),
          ),
        ),'''

if new in text:
    print('already applied')
    raise SystemExit(0)
if old not in text:
    raise SystemExit('Card theme fragment not found')
text = text.replace(old, new, 1)
path.write_text(text, encoding='utf-8')
print('Applied v0.5 visual theme')
