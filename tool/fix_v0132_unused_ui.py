from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')


def remove_range(source: str, start_class: str, end_class: str) -> str:
    start_marker = f'class {start_class}'
    end_marker = f'class {end_class}'
    if start_marker not in source:
        raise SystemExit(f'cleanup start not found: {start_class}')
    start = source.index(start_marker)
    end = source.index(end_marker, start)
    return source[:start] + source[end:]


# Old first-page visual helpers are no longer used by the expanded concept
# introduction. The new support page has its own compact cards.
text = remove_range(
    text,
    '_JourneySteps extends StatelessWidget',
    '_SupportStoryPage extends StatelessWidget',
)

# Remove the complete old support-grid helper family. The next unrelated class
# is the settings/help page retained by the application.
text = remove_range(
    text,
    '_SupportChoiceGrid extends StatelessWidget',
    'HowItWorksPage extends StatelessWidget',
)

# The postponed deterministic assistant is kept in its historical rewrite file,
# but is deliberately absent from the materialized application until a later AI
# experiment is designed and approved.
text = remove_range(
    text,
    '_DigitalActionAssistantCard extends StatelessWidget',
    'Speech',
)

path.write_text(text, encoding='utf-8')
print('Removed obsolete v0.13.2 introduction and assistant UI classes')
