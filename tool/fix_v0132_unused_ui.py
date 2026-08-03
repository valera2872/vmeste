from pathlib import Path
import re

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')


def remove_one_class(source: str, class_name: str) -> str:
    marker = f'class {class_name}'
    start = source.find(marker)
    if start < 0:
        raise SystemExit(f'cleanup class not found: {class_name}')
    next_class = re.search(r'^class\s+', source[start + len(marker):], flags=re.M)
    if next_class is None:
        raise SystemExit(f'next class not found after: {class_name}')
    end = start + len(marker) + next_class.start()
    return source[:start] + source[end:]


# Remove only the obsolete classes themselves. Later release scripts insert
# challenges, agreements and other product classes near these anchors, so a
# broad range deletion would incorrectly remove active functionality.
obsolete_classes = [
    '_JourneySteps extends StatelessWidget',
    '_JourneyStep extends StatelessWidget',
    '_DottedConnector extends StatelessWidget',
    '_AttentionCard extends StatelessWidget',
    '_ResearchNote extends StatelessWidget',
    '_SupportChoiceGrid extends StatelessWidget',
    '_ActionCenterCard extends StatelessWidget',
    '_OnboardingSupportCard extends StatelessWidget',
    '_QuietStatement extends StatelessWidget',
    '_DigitalActionAssistantCard extends StatelessWidget',
    '_AssistantSuggestion extends StatelessWidget',
]

for class_name in obsolete_classes:
    text = remove_one_class(text, class_name)

path.write_text(text, encoding='utf-8')
print('Removed only obsolete v0.13.2 introduction and assistant classes')
