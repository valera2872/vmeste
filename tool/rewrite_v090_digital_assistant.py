from pathlib import Path

main_path = Path('lib/main.dart')
pubspec_path = Path('pubspec.yaml')
text = main_path.read_text(encoding='utf-8')
pubspec = pubspec_path.read_text(encoding='utf-8')

if 'class _DigitalActionAssistantCard' in text:
    print('v0.9.0 digital assistant already applied')
    raise SystemExit(0)

# Add the assistant directly before the existing optional minimum editor.
marker = '''          TextButton.icon(
            onPressed: () => setState(() => showSmall = !showSmall),'''
if marker not in text:
    raise SystemExit('Action editor minimum marker not found')

assistant_block = '''          if (support == Support.ai) ...[
            const SizedBox(height: 12),
            _DigitalActionAssistantCard(
              title: title.text,
              currentMinimum: small.text,
              onUseFirstStep: (value) {
                title.text = value;
                title.selection = TextSelection.collapsed(
                  offset: title.text.length,
                );
                setState(() {});
              },
              onUseMinimum: (value) {
                small.text = value;
                small.selection = TextSelection.collapsed(
                  offset: small.text.length,
                );
                setState(() => showSmall = true);
              },
            ),
            const SizedBox(height: 8),
          ],
'''
text = text.replace(marker, assistant_block + marker, 1)

# Add a direct entry point from the current goal step when AI support is selected.
class_start = text.index('class _CurrentGoalStepCard extends StatelessWidget')
class_end = text.index('class _EmptyCurrentGoalStep', class_start)
segment = text[class_start:class_end]
row_marker = '''          const SizedBox(height: 14),
          Row(
            children: ['''
if row_marker not in segment:
    raise SystemExit('Current goal step action row marker not found')
assistant_entry = '''          if (item.support == Support.ai) ...[
            OutlinedButton.icon(
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
            const SizedBox(height: 10),
          ],
'''
segment = segment.replace(row_marker, assistant_entry + row_marker, 1)
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

  String get normalizedTitle {
    final value = title.trim();
    return value.isEmpty ? 'это действие' : value;
  }

  String get firstPhysicalStep {
    final value = normalizedTitle;
    final lower = value.toLowerCase();
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
      return 'Выбрать один небольшой участок и убрать с него первые пять вещей';
    }
    if (lower.startsWith('изучить') || lower.startsWith('разобраться')) {
      return 'Открыть один надёжный источник и выписать первый конкретный вопрос';
    }
    return 'Подготовить всё необходимое и выполнить первый видимый фрагмент: $value';
  }

  String get generatedMinimum {
    final value = normalizedTitle;
    final lower = value.toLowerCase();
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
    return 'Заниматься пять минут и завершить хотя бы один небольшой фрагмент';
  }

  List<String> get plan => [
    'Подготовить место, материалы или нужный экран',
    firstPhysicalStep,
    'Зафиксировать результат и определить следующий шаг',
  ];

  @override
  Widget build(BuildContext context) {
    final minimum = currentMinimum.trim().isEmpty
        ? generatedMinimum
        : currentMinimum.trim();
    return Container(
      key: const ValueKey('digital-action-assistant'),
      padding: const EdgeInsets.all(17),
      decoration: BoxDecoration(
        color: const Color(0xFFEAF3EF),
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: const Color(0xFFD0E1DA)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.auto_awesome_outlined, color: green, size: 20),
              SizedBox(width: 8),
              Expanded(
                child: Text(
                  'ЦИФРОВОЙ ПОМОЩНИК',
                  style: TextStyle(
                    color: green,
                    fontSize: 10.5,
                    fontWeight: FontWeight.w900,
                    letterSpacing: .85,
                  ),
                ),
              ),
              _LocalHintBadge(),
            ],
          ),
          const SizedBox(height: 12),
          const Text(
            'Сделаем действие легче для старта',
            style: TextStyle(
              color: ink,
              fontSize: 18,
              height: 1.2,
              fontWeight: FontWeight.w900,
            ),
          ),
          const SizedBox(height: 6),
          const Text(
            'Это локальная подсказка, а не автоматическое решение. Вы сами выбираете, что сохранить.',
            style: TextStyle(
              color: Color(0xFF65736E),
              fontSize: 12.5,
              height: 1.4,
            ),
          ),
          const SizedBox(height: 15),
          _AssistantSuggestion(
            number: '1',
            title: 'Первый физический шаг',
            text: firstPhysicalStep,
            button: 'Сделать текущим действием',
            buttonKey: const ValueKey('use-first-physical-step'),
            onPressed: () => onUseFirstStep(firstPhysicalStep),
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
                    letterSpacing: .65,
                  ),
                ),
                const SizedBox(height: 9),
                ...plan.asMap().entries.map(
                  (entry) => Padding(
                    padding: const EdgeInsets.only(bottom: 7),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Container(
                          width: 22,
                          height: 22,
                          alignment: Alignment.center,
                          decoration: const BoxDecoration(
                            color: Color(0xFFEAF3EF),
                            shape: BoxShape.circle,
                          ),
                          child: Text(
                            '${entry.key + 1}',
                            style: const TextStyle(
                              color: green,
                              fontSize: 10.5,
                              fontWeight: FontWeight.w900,
                            ),
                          ),
                        ),
                        const SizedBox(width: 9),
                        Expanded(
                          child: Text(
                            entry.value,
                            style: const TextStyle(
                              color: ink,
                              fontSize: 12.5,
                              height: 1.36,
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
            number: '2',
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

class _LocalHintBadge extends StatelessWidget {
  const _LocalHintBadge();

  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
    decoration: BoxDecoration(
      color: Colors.white,
      borderRadius: BorderRadius.circular(20),
    ),
    child: const Text(
      'ЛОКАЛЬНО',
      style: TextStyle(
        color: Color(0xFF65736E),
        fontSize: 8.5,
        fontWeight: FontWeight.w900,
        letterSpacing: .55,
      ),
    ),
  );
}

class _AssistantSuggestion extends StatelessWidget {
  const _AssistantSuggestion({
    required this.number,
    required this.title,
    required this.text,
    required this.button,
    required this.buttonKey,
    required this.onPressed,
  });

  final String number, title, text, button;
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
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: 25,
              height: 25,
              alignment: Alignment.center,
              decoration: const BoxDecoration(
                color: ink,
                shape: BoxShape.circle,
              ),
              child: Text(
                number,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 11,
                  fontWeight: FontWeight.w900,
                ),
              ),
            ),
            const SizedBox(width: 9),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(
                      color: ink,
                      fontSize: 13.5,
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                  const SizedBox(height: 5),
                  Text(
                    text,
                    style: const TextStyle(
                      color: Color(0xFF53615C),
                      fontSize: 12.5,
                      height: 1.4,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
        const SizedBox(height: 9),
        Align(
          alignment: Alignment.centerLeft,
          child: TextButton.icon(
            key: buttonKey,
            onPressed: onPressed,
            icon: const Icon(Icons.arrow_forward_rounded, size: 17),
            label: Text(button),
          ),
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
