from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

old_metrics = r'''          Row(
            children: [
              _GoalMetric(value: '${app.goalDone}', label: 'завершено'),
              const SizedBox(width: 8),
              _GoalMetric(value: '${app.goalActive}', label: 'в пути'),
              const Spacer(),
              Text(
                total == 0 ? 'Начните с одного шага' : 'Двигайтесь по одному шагу',
                style: const TextStyle(
                  color: Color(0xFF75817D),
                  fontSize: 11.5,
                ),
              ),
            ],
          ),'''
new_metrics = r'''          Wrap(
            spacing: 8,
            runSpacing: 7,
            crossAxisAlignment: WrapCrossAlignment.center,
            children: [
              _GoalMetric(value: '${app.goalDone}', label: 'завершено'),
              _GoalMetric(value: '${app.goalActive}', label: 'в пути'),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            total == 0 ? 'Начните с одного шага' : 'Двигайтесь по одному шагу',
            style: const TextStyle(
              color: Color(0xFF75817D),
              fontSize: 11.5,
            ),
          ),'''
if old_metrics not in text:
    raise SystemExit('Goal metrics row anchor not found')
text = text.replace(old_metrics, new_metrics, 1)

old_support = r'''          Row(
            children: [
              const Text(
                'СЕЙЧАС',
                style: TextStyle(
                  color: mint,
                  fontSize: 11,
                  fontWeight: FontWeight.w900,
                  letterSpacing: 1,
                ),
              ),
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 5),
                decoration: BoxDecoration(
                  color: Colors.white12,
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(supportIcon(item.support), color: mint, size: 15),
                    const SizedBox(width: 5),
                    Text(
                      supportName(item.support),
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 11,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),'''
new_support = r'''          Row(
            children: [
              const Text(
                'СЕЙЧАС',
                style: TextStyle(
                  color: mint,
                  fontSize: 11,
                  fontWeight: FontWeight.w900,
                  letterSpacing: 1,
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Align(
                  alignment: Alignment.centerRight,
                  child: Container(
                    constraints: const BoxConstraints(maxWidth: 190),
                    padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 5),
                    decoration: BoxDecoration(
                      color: Colors.white12,
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(supportIcon(item.support), color: mint, size: 15),
                        const SizedBox(width: 5),
                        Flexible(
                          child: Text(
                            supportName(item.support),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 11,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),'''
if old_support not in text:
    raise SystemExit('Current goal support row anchor not found')
text = text.replace(old_support, new_support, 1)

old_buttons = r'''          Row(
            children: [
              Expanded(
                child: FilledButton.icon(
                  key: const ValueKey('goal-start-button'),
                  style: FilledButton.styleFrom(
                    backgroundColor: mint,
                    foregroundColor: ink,
                  ),
                  onPressed: () => _open(context),
                  icon: const Icon(Icons.play_arrow_rounded),
                  label: const Text('Начать'),
                ),
              ),
              const SizedBox(width: 9),
              Expanded(
                child: OutlinedButton.icon(
                  key: const ValueKey('goal-difficulty-button'),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: Colors.white,
                    side: const BorderSide(color: Color(0x99FFFFFF)),
                  ),
                  onPressed: () => _open(context, difficulty: true),
                  icon: const Icon(Icons.support_rounded),
                  label: const Text('Трудно начать'),
                ),
              ),
            ],
          ),'''
new_buttons = r'''          SizedBox(
            width: double.infinity,
            child: FilledButton.icon(
              key: const ValueKey('goal-start-button'),
              style: FilledButton.styleFrom(
                backgroundColor: mint,
                foregroundColor: ink,
              ),
              onPressed: () => _open(context),
              icon: const Icon(Icons.play_arrow_rounded),
              label: const Text('Начать действие'),
            ),
          ),
          const SizedBox(height: 8),
          SizedBox(
            width: double.infinity,
            child: OutlinedButton.icon(
              key: const ValueKey('goal-difficulty-button'),
              style: OutlinedButton.styleFrom(
                foregroundColor: Colors.white,
                side: const BorderSide(color: Color(0x99FFFFFF)),
              ),
              onPressed: () => _open(context, difficulty: true),
              icon: const Icon(Icons.support_rounded),
              label: const Text('Трудно начать'),
            ),
          ),'''
if old_buttons not in text:
    raise SystemExit('Current goal action buttons anchor not found')
text = text.replace(old_buttons, new_buttons, 1)

path.write_text(text, encoding='utf-8')
print('Adapted v0.8.0 goal path to narrow phones')
