from pathlib import Path

fix_path = Path('tool/fix_v065_home_section_title.py')
exec(compile(fix_path.read_text(encoding='utf-8'), str(fix_path), 'exec'))

source_path = Path('tool/rewrite_v065_first_capture.py')
source = source_path.read_text(encoding='utf-8')

start = source.index('# Editing a regular practice should return to the screen that opened it.')
end = source.index("main_path.write_text(text, encoding='utf-8')", start)

robust_fix = r"""# Editing a regular practice should return to the screen that opened it.
routine_start = text.index('class _RoutineEditorState extends State<RoutineEditor>')
routine_end = text.index('class RoutineCard extends StatelessWidget', routine_start)
routine_section = text[routine_start:routine_end]
needle = '    Navigator.popUntil(context, (route) => route.isFirst);'
if needle not in routine_section:
    raise SystemExit('Routine save navigation not found')
replacement = "    if (existing == null) {\n      Navigator.popUntil(context, (route) => route.isFirst);\n    } else {\n      Navigator.pop(context);\n    }"
routine_section = routine_section.replace(needle, replacement, 1)
text = text[:routine_start] + routine_section + text[routine_end:]

"""

patched = source[:start] + robust_fix + source[end:]
exec(compile(patched, str(source_path), 'exec'))
