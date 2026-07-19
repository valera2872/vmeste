from pathlib import Path

path = Path("lib/main.dart")
text = path.read_text(encoding="utf-8")
text = text.replace(
    "listenOptions: const stt.SpeechListenOptions(localeId: 'ru_RU')",
    "listenOptions: stt.SpeechListenOptions(localeId: 'ru_RU')",
)
path.write_text(text, encoding="utf-8")
