from pathlib import Path

main_path = Path('lib/main.dart')
pubspec_path = Path('pubspec.yaml')
text = main_path.read_text(encoding='utf-8')


def replace(old: str, new: str) -> None:
    global text
    if old not in text:
        raise SystemExit(f'Expected fragment not found:\n{old[:240]}')
    text = text.replace(old, new, 1)


replace(
    """class _OnboardingState extends State<Onboarding> {
  final pages = PageController();
  final name = TextEditingController();
  int page = 0;
  Age age = Age.adult;

  @override
  void dispose() {
    pages.dispose();
    name.dispose();
    super.dispose();
  }""",
    """class _OnboardingState extends State<Onboarding> {
  final pages = PageController();
  int page = 0;

  @override
  void dispose() {
    pages.dispose();
    super.dispose();
  }""",
)

replace(
    """                const Spacer(),
                Text(
                  '${page + 1} / 3',
                  style: const TextStyle(color: Colors.white54),
                ),""",
    """                const Spacer(),
                TextButton(
                  onPressed: () => widget.app.finish(Age.adult, ''),
                  child: const Text(
                    'Пропустить',
                    style: TextStyle(color: Colors.white70),
                  ),
                ),""",
)

replace(
    """                ),
                ProfilePage(
                  name: name,
                  age: age,
                  onAge: (value) => setState(() => age = value),
                ),
              ],""",
    """                ),
              ],""",
)

replace("children: List.generate(\n                    3,", "children: List.generate(\n                    2,")
replace("if (page < 2) {", "if (page < 1) {")
replace("widget.app.finish(age, name.text);", "widget.app.finish(Age.adult, '');")
replace(
    "child: Text(page == 2 ? 'Начать' : 'Дальше'),",
    "child: Text(page == 1 ? 'Перейти к цели' : 'Дальше'),",
)

# Remove the unused personal-data screen entirely.
start = text.find('class ProfilePage extends StatelessWidget {')
if start != -1:
    end = text.find('class HowItWorksPage extends StatelessWidget {', start)
    if end == -1:
        raise SystemExit('HowItWorksPage marker not found')
    text = text[:start] + text[end:]

main_path.write_text(text, encoding='utf-8')

pubspec = pubspec_path.read_text(encoding='utf-8')
pubspec = pubspec.replace('version: 0.3.2+6', 'version: 0.3.3+7')
pubspec_path.write_text(pubspec, encoding='utf-8')
