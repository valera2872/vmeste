from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')
start = text.index('class Today extends StatelessWidget')
end = text.index('class _GoalActionGroup extends StatelessWidget', start)
today = text[start:end]

appbar_add = r'''          IconButton(
            key: const ValueKey('today-add'),
            tooltip: 'Добавить',
            icon: const Icon(Icons.add_rounded),
            onPressed: () => _add(context),
          ),
'''
if appbar_add not in today:
    raise SystemExit('v0.6.2 app bar add button not found')
today = today.replace(appbar_add, '', 1)

marker = '''        ],
      ),
    );
  }

  Widget _section'''
inline_add = r'''          const SizedBox(height: 10),
          Align(
            alignment: Alignment.centerRight,
            child: FilledButton.tonalIcon(
              key: const ValueKey('today-add'),
              style: FilledButton.styleFrom(
                minimumSize: const Size(0, 40),
                padding: const EdgeInsets.symmetric(horizontal: 13),
                backgroundColor: const Color(0xFFE1ECE8),
                foregroundColor: ink,
                tapTargetSize: MaterialTapTargetSize.shrinkWrap,
              ),
              onPressed: () => _add(context),
              icon: const Icon(Icons.add_rounded, size: 18),
              label: const Text('Добавить'),
            ),
          ),
        ],
      ),
    );
  }

  Widget _section'''
if marker not in today:
    raise SystemExit('v0.6.2 today children end marker not found')
today = today.replace(marker, inline_add, 1)
path.write_text(text[:start] + today + text[end:], encoding='utf-8')
