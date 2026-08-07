from pathlib import Path

main_path = Path('lib/main.dart')
pubspec_path = Path('pubspec.yaml')
text = main_path.read_text(encoding='utf-8')
pubspec = pubspec_path.read_text(encoding='utf-8')

if 'class _DigitalActionAssistantCard' in text:
    print('v0.9.0 digital assistant already applied')
    raise SystemExit(0)

editor_marker = '''          TextButton.icon(
            onPressed: () => setState(() => showSmall = !showSmall),'''
if editor_marker not in text:
    raise SystemExit('Action editor minimum marker not found')

editor_block = '''          if (support == Support.ai) ...[
            const SizedBox(height: 12),
            _DigitalActionAssistantCard(
              title: title.text,
              currentMinimum: small.text,
              onUseFirstStep: (value) {
                title.text = value;
                title.selection = TextSelection.collapsed(offset: value.length);
                setState(() {});
              },
              onUseMinimum: (value) {
                small.text = value;
                small.selection = TextSelection.collapsed(offset: value.length);
                setState(() => showSmall = true);
              },
            ),
            const SizedBox(height: 8),
          ],
'''
text = text.replace(editor_marker, editor_block + editor_marker, 1)

class_start = text.index('class _CurrentGoalStepCard extends StatelessWidget')
class_end = text.index('class _EmptyCurrentGoalStep', class_start)
segment = text[class_start:class_end]
button_marker = '''          SizedBox(
            width: double.infinity,
            child: FilledButton.icon(
              key: const ValueKey('goal-start-button'),'''
if button_marker not in segment:
    raise SystemExit('Current goal narrow action button marker not found')
entry = '''          if (item.support == Support.ai) ...[
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                key: const ValueKey('open-digital-assistant'),
                style: OutlinedButton.styleFrom(
                  foregroundColor: mint,
                  side: const BorderSide(color: Color(0x66D4FFF2)),
                ),
                onPressed: () => Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => ActionEditor(
                      app: app,
                      goalDefault: true,
                      existing: item,
                    ),
                  ),
                ),
                icon: const Icon(Icons.auto_awesome_outlined),
                label: const Text('Разобрать действие с помощником'),
              ),
            ),
            const SizedBox(height: 8),
          ],
'''
segment = segment.replace(button_marker, entry + button_marker, 1)
text = text[:class_start] + segment + text[class_end:]

assistant_class = r'''class _DigitalActionAssistantCard extends StatelessWidget {
  const _DigitalActionAssistantCard({
    required this.title,
    required this.currentMinimum,
    required this.onUseFirstStep,
    required this.onUseMinimum,
  });

  final String title;
  final String currentMinimum;
  final ValueChanged<String> onUseFirstStep;
  final ValueChanged<String> onUseMinimum;

  String get cleanTitle => title.trim().isEmpty ? 'это действие' : title.trim();

  String get firstStep {
    final lower = cleanTitle.toLowerCase();
    if (lower.startsWith('написать') || lower.startsWith('подготовить текст')) {
      return 'Открыть документ и написать первый рабочий абзац';
    }
    if (lower.startsWith('проверить') || lower.startsWith('протестировать')) {
      return 'Открыть нужный экран и проверить один основной сценарий';
    }
    if (lower.startsWith('позвонить') || lower.startsWith('написать ')) {
      return 'Открыть контакт и составить первое короткое сообщение';
    }
    if (lower.startsWith('убрать') || lower.startsWith('разобрать')) {
      return 'Выбрать один небольшой участок и убрать первые пять вещей';
    }
    if (lower.startsWith('изучить') || lower.startsWith('разобраться')) {
      return 'Открыть один источник и записать первый конкретный вопрос';
    }
    return 'Подготовить всё необходимое и выполнить первый видимый фрагмент: $cleanTitle';
  }

  String get generatedMinimum {
    final lower = cleanTitle.toLowerCase();
    if (lower.startsWith('написать') || lower.contains('текст')) {
      return 'Написать только один черновой абзац';
    }
    if (lower.startsWith('проверить') || lower.startsWith('протестировать')) {
      return 'Проверить только один основной сценарий и записать результат';
    }
    if (lower.startsWith('убрать') || lower.startsWith('разобрать')) {
      return 'Потратить пять минут только на один небольшой участок';
    }
    if (lower.startsWith('изучить') || lower.startsWith('разобраться')) {
      return 'Прочитать один короткий материал и записать один вывод';
    }
    return 'Заниматься пять минут и завершить один небольшой фрагмент';
  }

  @override
  Widget build(BuildContext context) {
    final minimum = currentMinimum.trim().isEmpty
        ? generatedMinimum
        : currentMinimum.trim();
    final plan = [
      'Подготовить место, материалы или нужный экран',
      firstStep,
      'Зафиксировать результат и определить следующий шаг',
    ];
    return Container(
      key: const ValueKey('digital-action-assistant'),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFFEAF3EF),
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: const Color(0xFFD0E1DA)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.auto_awesome_outlined, color: green, size: 20),
              const SizedBox(width: 8),
              const Expanded(
                child: Text(
                  'ЦИФРОВОЙ ПОМОЩНИК',
                  style: TextStyle(
                    color: green,
                    fontSize: 10.5,
                    fontWeight: FontWeight.w900,
                    letterSpacing: .8,
                  ),
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                ),
                child: const Text(
                  'ЛОКАЛЬНО',
                  style: TextStyle(
                    color: Color(0xFF65736E),
                    fontSize: 8,
                    fontWeight: FontWeight.w900,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          const Text(
            'Сделаем действие легче для старта',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900),
          ),
          const SizedBox(height: 5),
          const Text(
            'Это локальная подсказка. Вы сами выбираете, что сохранить.',
            style: TextStyle(color: Color(0xFF65736E), height: 1.4),
          ),
          const SizedBox(height: 13),
          _AssistantSuggestion(
            title: 'Первый физический шаг',
            text: firstStep,
            button: 'Сделать текущим действием',
            buttonKey: const ValueKey('use-first-physical-step'),
            onPressed: () => onUseFirstStep(firstStep),
          ),
          const SizedBox(height: 10),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(13),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(17),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'РАЗЛОЖЕНИЕ НА ТРИ ЧАСТИ',
                  style: TextStyle(
                    color: Color(0xFF65736E),
                    fontSize: 10,
                    fontWeight: FontWeight.w900,
                    letterSpacing: .6,
                  ),
                ),
                const SizedBox(height: 9),
                ...plan.asMap().entries.map(
                  (entry) => Padding(
                    padding: const EdgeInsets.only(bottom: 7),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        CircleAvatar(
                          radius: 11,
                          backgroundColor: const Color(0xFFEAF3EF),
                          child: Text(
                            '${entry.key + 1}',
                            style: const TextStyle(
                              color: green,
                              fontSize: 10,
                              fontWeight: FontWeight.w900,
                            ),
                          ),
                        ),
                        const SizedBox(width: 9),
                        Expanded(
                          child: Text(
                            entry.value,
                            style: const TextStyle(
                              fontSize: 12.5,
                              height: 1.35,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 10),
          _AssistantSuggestion(
            title: 'Минимальный вариант',
            text: minimum,
            button: currentMinimum.trim().isEmpty
                ? 'Использовать этот минимум'
                : 'Обновить минимальный вариант',
            buttonKey: const ValueKey('use-generated-minimum'),
            onPressed: () => onUseMinimum(minimum),
          ),
        ],
      ),
    );
  }
}

class _AssistantSuggestion extends StatelessWidget {
  const _AssistantSuggestion({
    required this.title,
    required this.text,
    required this.button,
    required this.buttonKey,
    required this.onPressed,
  });

  final String title, text, button;
  final Key buttonKey;
  final VoidCallback onPressed;

  @override
  Widget build(BuildContext context) => Container(
    width: double.infinity,
    padding: const EdgeInsets.all(13),
    decoration: BoxDecoration(
      color: Colors.white,
      borderRadius: BorderRadius.circular(17),
    ),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title, style: const TextStyle(fontWeight: FontWeight.w900)),
        const SizedBox(height: 5),
        Text(text, style: const TextStyle(color: Color(0xFF53615C), height: 1.4)),
        const SizedBox(height: 7),
        TextButton.icon(
          key: buttonKey,
          onPressed: onPressed,
          icon: const Icon(Icons.arrow_forward_rounded, size: 17),
          label: Text(button),
        ),
      ],
    ),
  );
}

'''
insert_at = text.index('class Speech {')
text = text[:insert_at] + assistant_class + text[insert_at:]

if 'version: 0.8.0+24' not in pubspec:
    raise SystemExit('Expected v0.8.0 version not found')
pubspec = pubspec.replace('version: 0.8.0+24', 'version: 0.9.0+25', 1)

main_path.write_text(text, encoding='utf-8')
pubspec_path.write_text(pubspec, encoding='utf-8')
print('Applied v0.9.0 digital action assistant')
