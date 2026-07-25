from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')
old = r'''                    child: OutlinedButton.icon(
                      key: ValueKey('action-together-${item.id}'),
                      style: OutlinedButton.styleFrom(
                        minimumSize: const Size(0, 43),
                        padding: const EdgeInsets.symmetric(horizontal: 8),
                        tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                      ),
                      onPressed: () => _startTogether(context),
                      icon: const Icon(Icons.people_alt_outlined, size: 18),
                      label: const Text(
                        'Вместе',
                        maxLines: 1,
                        softWrap: false,
                      ),
                    ),'''
new = r'''                    child: OutlinedButton(
                      key: ValueKey('action-together-${item.id}'),
                      style: OutlinedButton.styleFrom(
                        minimumSize: const Size(0, 43),
                        padding: const EdgeInsets.symmetric(horizontal: 8),
                        tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                      ),
                      onPressed: () => _startTogether(context),
                      child: const Text(
                        'Вместе',
                        maxLines: 1,
                        softWrap: false,
                      ),
                    ),'''
if old not in text:
    raise SystemExit('v0.6.2 together button block not found')
path.write_text(text.replace(old, new, 1), encoding='utf-8')
