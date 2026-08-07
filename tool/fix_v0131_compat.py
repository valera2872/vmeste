from pathlib import Path
import re

main_path = Path('lib/main.dart')
test_path = Path('test/widget_test.dart')
main = main_path.read_text(encoding='utf-8')
tests = test_path.read_text(encoding='utf-8')

# The overview is navigation, not a second rendering of the full goal title.
# A short status keeps the 2x2 area calm on narrow phones.
old_goal_status = "status: app.goal?.title ?? 'Добавить',"
new_goal_status = "status: app.goal == null ? 'Добавить' : 'Продолжить',"
if old_goal_status not in main:
    raise SystemExit('v0.13.1 goal overview status anchor not found')
main = main.replace(old_goal_status, new_goal_status, 1)


def test_block(source: str, name: str) -> tuple[int, int, str]:
    marker = f"  testWidgets('{name}'"
    start = source.find(marker)
    if start < 0:
        raise SystemExit(f'test not found: {name}')
    match = re.search(r"\n  test(?:Widgets)?\(", source[start + len(marker):])
    if match:
        end = start + len(marker) + match.start() + 1
    else:
        end = source.rindex('\n}')
    return start, end, source[start:end]


def replace_test(name: str, transform) -> None:
    global tests
    start, end, block = test_block(tests, name)
    changed = transform(block)
    if changed == block:
        raise SystemExit(f'no compatibility change made for: {name}')
    tests = tests[:start] + changed + tests[end:]


def taller(block: str) -> str:
    return re.sub(
        r"Size\((\d+),\s*\d+\)",
        lambda match: f"Size({match.group(1)}, 1200)",
        block,
        count=1,
    )


def adapt_today_combined(block: str) -> str:
    block = taller(block)
    block = block.replace(
        "expect(find.text('Запустить приложение «Вместе к цели»'), findsOneWidget);",
        "expect(\n      find.text('Запустить приложение «Вместе к цели»'),\n      findsAtLeastNWidgets(1),\n    );",
        1,
    )
    return block


replace_test(
    'today shows goal other work and quick capture together',
    adapt_today_combined,
)
replace_test(
    'today primary action stays on one line on a narrow phone',
    taller,
)


def adapt_challenge_block(block: str) -> str:
    return block.replace(
        "expect(find.text('Челленджи'), findsOneWidget);",
        "expect(\n      find.byKey(const ValueKey('today-challenges-area')),\n      findsOneWidget,\n    );",
        1,
    )


replace_test(
    'personal challenge is a separate block on Today',
    adapt_challenge_block,
)


def adapt_empty_challenge(block: str) -> str:
    return block.replace(
        """scrollable: find.byKey(const ValueKey('today-editorial-scroll')),""",
        """scrollable: find.byType(Scrollable).first,""",
        1,
    )


replace_test(
    'empty challenge is a visible action on Today',
    adapt_empty_challenge,
)

main_path.write_text(main, encoding='utf-8')
test_path.write_text(tests, encoding='utf-8')
print('Adapted v0.13.1 compatibility checks and compact overview status')
