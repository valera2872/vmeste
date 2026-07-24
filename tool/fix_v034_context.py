from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')
old = """                          );
                      if (!mounted) return;
                      switch (outcome) {"""
new = """                          );
                      if (!context.mounted) return;
                      switch (outcome) {"""
if old in text:
    text = text.replace(old, new, 1)
elif new not in text:
    raise SystemExit('Session help context guard not found')
path.write_text(text, encoding='utf-8')
