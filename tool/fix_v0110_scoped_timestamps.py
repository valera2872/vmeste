from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

wrong = """    'updatedAt': updatedAt.toIso8601String(),
    'startedAt': startedAt?.toIso8601String(),
    'completedAt': completedAt?.toIso8601String(),
  };"""
plain = """    'updatedAt': updatedAt.toIso8601String(),
  };"""
if wrong not in text:
    raise SystemExit('Mis-scoped support timestamps were not found')
text = text.replace(wrong, plain, 1)

start = text.index('class SupportAgreement')
end = text.index('class NotificationService', start)
block = text[start:end]
if wrong not in block:
    if plain not in block:
        raise SystemExit('SupportAgreement toJson anchor not found')
    block = block.replace(plain, wrong, 1)
text = text[:start] + block + text[end:]

path.write_text(text, encoding='utf-8')
print('Scoped v0.11.0 lifecycle timestamps to SupportAgreement')
