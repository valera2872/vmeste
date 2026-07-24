from pathlib import Path

main_path = Path("lib/main.dart")
text = main_path.read_text(encoding="utf-8")

old = """  @override
  Widget build(BuildContext context) => TextField(
    controller: widget.controller,
    maxLines: widget.lines,
    decoration: InputDecoration(
      labelText: widget.label,
      hintText: widget.hint,
      suffixIcon: IconButton(
        onPressed: mic,
        icon: Icon(listening ? Icons.mic : Icons.mic_none),
        color: listening ? Colors.red : green,
        tooltip: 'Продиктовать',
      ),
    ),
  );
"""

new = """  @override
  Widget build(BuildContext context) => Column(
    crossAxisAlignment: CrossAxisAlignment.stretch,
    children: [
      TextField(
        controller: widget.controller,
        maxLines: widget.lines,
        decoration: InputDecoration(
          labelText: widget.label,
          hintText: widget.hint,
          hintMaxLines: widget.lines > 1 ? widget.lines : 2,
          alignLabelWithHint: widget.lines > 1,
        ),
      ),
      const SizedBox(height: 6),
      Align(
        alignment: Alignment.centerRight,
        child: TextButton.icon(
          onPressed: mic,
          icon: Icon(
            listening ? Icons.stop_circle_outlined : Icons.mic_none_rounded,
            size: 20,
          ),
          label: Text(listening ? 'Остановить запись' : 'Надиктовать'),
          style: TextButton.styleFrom(
            foregroundColor: listening ? Colors.red : green,
            backgroundColor: listening
                ? Colors.red.withValues(alpha: .08)
                : mint.withValues(alpha: .42),
            visualDensity: VisualDensity.compact,
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(13),
            ),
          ),
        ),
      ),
    ],
  );
"""

if "Остановить запись" not in text:
    if old not in text:
        raise SystemExit("VoiceField block not found")
    text = text.replace(old, new, 1)

main_path.write_text(text, encoding="utf-8")

pubspec_path = Path("pubspec.yaml")
pubspec = pubspec_path.read_text(encoding="utf-8")
pubspec = pubspec.replace("version: 0.5.0+11", "version: 0.5.1+12", 1)
pubspec_path.write_text(pubspec, encoding="utf-8")

print("Applied v0.5.1 voice field layout")
