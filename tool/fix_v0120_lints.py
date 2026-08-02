from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

old = """    final text =
        '${greeting}день ${widget.challenge.dayNumber()} из ${widget.challenge.durationDays}: '
        '${challengeResultTitle(entry.result).toLowerCase()} — ${entry.amount} ${widget.challenge.unit}. '
        'Текущая серия: ${widget.challenge.currentStreak}.';"""
new = r"""    final text =
        '$greeting\u0434ень ${widget.challenge.dayNumber()} из ${widget.challenge.durationDays}: '
        '${challengeResultTitle(entry.result).toLowerCase()} — ${entry.amount} ${widget.challenge.unit}. '
        'Текущая серия: ${widget.challenge.currentStreak}.';"""

if old not in text:
    raise SystemExit('Challenge report interpolation anchor not found')
text = text.replace(old, new, 1)
path.write_text(text, encoding='utf-8')
print('Fixed v0.12.0 strict interpolation lint')
