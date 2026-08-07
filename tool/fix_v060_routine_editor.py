from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

old = """    title.addListener(() => setState(() {}));
  }

  @override
  void dispose() {
    title.dispose();
    minimum.dispose();"""
new = """    title.addListener(() => setState(() {}));
    minimum.addListener(() => setState(() {}));
  }

  @override
  void dispose() {
    title.dispose();
    minimum.dispose();"""

if old in text:
    text = text.replace(old, new, 1)

text = text.replace(
    "_scheduleChip(RoutineSchedule.timesPerWeek, 'Раз в неделю')",
    "_scheduleChip(RoutineSchedule.timesPerWeek, 'Несколько раз')",
    1,
)

path.write_text(text, encoding='utf-8')
print('Applied final v0.6 routine editor polish')
