from pathlib import Path

exec(
    Path('tool/run_v0130_feasible_start_v2.py').read_text(encoding='utf-8'),
    {'__name__': '__main__'},
)
