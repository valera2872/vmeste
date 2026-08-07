from pathlib import Path
import re

source_path = Path('tool/rewrite_v0130_feasible_start.py')
source = source_path.read_text(encoding='utf-8')

# v0.9 already owns a digital-assistant model named StartPlan. Keep that model
# untouched and give the new v0.13 barrier plan an explicit product name.
source = re.sub(r'\bStartPlan\b', 'FeasibleStartPlan', source)
source = source.replace('buildStartPlan', 'buildFeasibleStartPlan')
source = source.replace(
    "  final first = SupportLogic.steps(item.title).first;\n",
    "",
    1,
)

# A continuation dialog is asynchronous. Confirm the Session state is still
# mounted before opening another route such as the schedule sheet.
source = source.replace(
    """      if (point != null) {
        widget.app.setContinuationPoint(widget.item.id, point);
      }
    }

    if (state == ResultState.moved) {""",
    """      if (point != null) {
        widget.app.setContinuationPoint(widget.item.id, point);
      }
    }
    if (!mounted) return;

    if (state == ResultState.moved) {""",
    1,
)

# ResultPage became stateful in v0.7. Patch the current state object instead of
# the outer widget class when showing a saved continuation point.
section_start = source.index('# Show the saved return point on the result screen.')
section_end = source.index('# Add a cautious learning card to the goal path.', section_start)

replacement = r"""# Show the saved return point on the current stateful result screen.
result_start = text.index('class _ResultPageState')
result_end = text.index('class ', result_start + len('class _ResultPageState'))
result_block = text[result_start:result_end]
result_block = result_block.replace(
    '''    final canShare =
        item.support == Support.together ||
        item.support == Support.report ||
        item.support == Support.curator;''',
    '''    final canShare =
        item.support == Support.together ||
        item.support == Support.report ||
        item.support == Support.curator;
    final continuation = app.continuationFor(item.id);''',
    1,
)
result_marker = '            if (ok) ...['
if result_marker not in result_block:
    raise SystemExit('stateful result continuation marker not found')
result_block = result_block.replace(
    result_marker,
    '''            if (continuation.isNotEmpty) ...[
              const SizedBox(height: 16),
              Container(
                key: const ValueKey('saved-continuation-point'),
                width: double.infinity,
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: const Color(0xFFEAF4EF),
                  borderRadius: BorderRadius.circular(18),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'ТОЧКА ПРОДОЛЖЕНИЯ',
                      style: TextStyle(
                        color: green,
                        fontSize: 10.5,
                        fontWeight: FontWeight.w900,
                        letterSpacing: .7,
                      ),
                    ),
                    const SizedBox(height: 5),
                    Text(
                      continuation,
                      style: const TextStyle(fontWeight: FontWeight.w800),
                    ),
                  ],
                ),
              ),
            ],
''' + result_marker,
    1,
)
text = text[:result_start] + result_block + text[result_end:]

"""

source = source[:section_start] + replacement + source[section_end:]
exec(compile(source, str(source_path), 'exec'), {'__name__': '__main__'})
