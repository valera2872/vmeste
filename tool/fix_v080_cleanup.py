from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

start = text.find('class _HomeSectionTitle extends StatelessWidget')
if start >= 0:
    brace = text.find('{', start)
    if brace < 0:
        raise SystemExit('Opening brace for _HomeSectionTitle not found')

    depth = 0
    end = None
    for index in range(brace, len(text)):
        char = text[index]
        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0:
                end = index + 1
                break

    if end is None:
        raise SystemExit('Closing brace for _HomeSectionTitle not found')

    while end < len(text) and text[end] in '\r\n':
        end += 1
    text = text[:start] + text[end:]

path.write_text(text, encoding='utf-8')
print('Removed obsolete v0.8.0 workspace helper')
