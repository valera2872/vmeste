from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

review_old = '''                  const Text(
                    'ВАШ ПРЕДВАРИТЕЛЬНЫЙ ФОКУС',
                    style: TextStyle(
                      color: mint,
                      fontSize: 10.5,
                      fontWeight: FontWeight.w900,
                      letterSpacing: .9,
                    ),
                  ),
                  const Spacer(),'''
review_new = '''                  const Expanded(
                    child: Text(
                      'ВАШ ПРЕДВАРИТЕЛЬНЫЙ ФОКУС',
                      maxLines: 2,
                      overflow: TextOverflow.visible,
                      style: TextStyle(
                        color: mint,
                        fontSize: 10.5,
                        fontWeight: FontWeight.w900,
                        letterSpacing: .75,
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),'''
if review_old not in text:
    raise SystemExit('Review focus header layout not found')
text = text.replace(review_old, review_new, 1)

empty_old = '''            Text(
              'ГЛАВНЫЙ ФОКУС · 90 ДНЕЙ',
              style: TextStyle(
                color: mint,
                fontSize: 11,
                fontWeight: FontWeight.w900,
                letterSpacing: 1,
              ),
            ),'''
empty_new = '''            Expanded(
              child: Text(
                'ГЛАВНЫЙ ФОКУС · 90 ДНЕЙ',
                maxLines: 2,
                overflow: TextOverflow.visible,
                style: TextStyle(
                  color: mint,
                  fontSize: 11,
                  fontWeight: FontWeight.w900,
                  letterSpacing: .8,
                ),
              ),
            ),'''
if empty_old not in text:
    raise SystemExit('Empty focus header layout not found')
text = text.replace(empty_old, empty_new, 1)

path.write_text(text, encoding='utf-8')
print('Adapted v0.14.0 focus cards to narrow phones')