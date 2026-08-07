from pathlib import Path

exec(
    Path('tool/rewrite_v0130_tests_base.py').read_text(encoding='utf-8'),
    {'__name__': '__main__'},
)
exec(
    Path('tool/fix_v0130_test_compat.py').read_text(encoding='utf-8'),
    {'__name__': '__main__'},
)
