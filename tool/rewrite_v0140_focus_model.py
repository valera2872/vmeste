from pathlib import Path
import re

main_path = Path('lib/main.dart')
pubspec_path = Path('pubspec.yaml')
text = main_path.read_text(encoding='utf-8')
pubspec = pubspec_path.read_text(encoding='utf-8')


def replace_class(source: str, name: str, next_name: str, replacement: str) -> str:
    start = source.index(f'class {name}')
    end = source.index(f'class {next_name}', start)
    return source[:start] + replacement.rstrip() + '\n\n' + source[end:]


GOAL = r'''class Goal {
  Goal(
    this.title,
    this.result,
    this.minutes,
    this.areas, {
    String? id,
    this.why = '',
    this.influence = '',
    this.firstStep = '',
    this.confidence = 0,
    this.guided = false,
    DateTime? focusStartedAt,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) : id = id ?? DateTime.now().microsecondsSinceEpoch.toString(),
       focusStartedAt = focusStartedAt ?? createdAt ?? DateTime.now(),
       createdAt = createdAt ?? DateTime.now(),
       updatedAt = updatedAt ?? DateTime.now();

  final String id;
  final String title, result;
  final int minutes;
  final List<String> areas;
  final String why;
  final String influence;
  final String firstStep;
  final int confidence;
  final bool guided;
  final DateTime focusStartedAt;
  final DateTime createdAt;
  final DateTime updatedAt;

  Map<String, dynamic> toJson() => {
    'id': id,
    'title': title,
    'result': result,
    'minutes': minutes,
    'areas': areas,
    'why': why,
    'influence': influence,
    'firstStep': firstStep,
    'confidence': confidence,
    'guided': guided,
    'focusStartedAt': focusStartedAt.toIso8601String(),
    'createdAt': createdAt.toIso8601String(),
    'updatedAt': updatedAt.toIso8601String(),
  };

  factory Goal.fromJson(Map<String, dynamic> j) {
    final now = DateTime.now();
    final title = (j['title'] ?? '').toString();
    final legacyId = 'goal_${title.hashCode.toUnsigned(32)}';
    final createdAt =
        DateTime.tryParse((j['createdAt'] ?? '').toString()) ?? now;
    return Goal(
      title,
      (j['result'] ?? '').toString(),
      j['minutes'] ?? 0,
      List<String>.from(j['areas'] ?? const []),
      id: (j['id'] ?? legacyId).toString(),
      why: (j['why'] ?? '').toString(),
      influence: (j['influence'] ?? '').toString(),
      firstStep: (j['firstStep'] ?? '').toString(),
      confidence: (j['confidence'] as num?)?.toInt() ?? 0,
      guided: j['guided'] == true,
      focusStartedAt:
          DateTime.tryParse((j['focusStartedAt'] ?? '').toString()) ?? createdAt,
      createdAt: createdAt,
      updatedAt: DateTime.tryParse((j['updatedAt'] ?? '').toString()) ?? now,
    );
  }
}'''

text = replace_class(text, 'Goal {', 'ActionItem {', GOAL)

schema_pattern = re.compile(r'static const schemaVersion = \d+;')
if not schema_pattern.search(text):
    raise SystemExit('schemaVersion not found')
text = schema_pattern.sub('static const schemaVersion = 9;', text, count=1)

if 'version: 0.13.2+32' not in pubspec:
    raise SystemExit('Expected v0.13.2+32 version not found')
pubspec = pubspec.replace('version: 0.13.2+32', 'version: 0.14.0+33', 1)

main_path.write_text(text, encoding='utf-8')
pubspec_path.write_text(pubspec, encoding='utf-8')
print('Added 90-day focus metadata and bumped schema/version')