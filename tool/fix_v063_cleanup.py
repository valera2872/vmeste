from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

# The product title must yield width to the close/skip action on narrow phones.
old = r'''                const Text(
                  'Вместе к цели',
                  style: TextStyle(
                    color: ink,
                    fontSize: 16,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const Spacer(),
                TextButton(
                  onPressed: close,
                  child: Text(widget.preview ? 'Закрыть' : 'Пропустить'),
                ),'''
new = r'''                const Expanded(
                  child: Text(
                    'Вместе к цели',
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(
                      color: ink,
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
                TextButton(
                  style: TextButton.styleFrom(
                    padding: const EdgeInsets.symmetric(horizontal: 8),
                    minimumSize: const Size(0, 40),
                  ),
                  onPressed: close,
                  child: Text(widget.preview ? 'Закрыть' : 'Пропустить'),
                ),'''
if old not in text:
    raise SystemExit('v0.6.3 onboarding header block not found')
text = text.replace(old, new, 1)
path.write_text(text, encoding='utf-8')
