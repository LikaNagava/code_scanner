"""Интеграционная проверка OCR на пяти контрольных фотографиях.

В отличие от модульных тестов этот файл действительно загружает модели
PaddleOCR и прогоняет изображения из samples. Результат сохраняется в JSON.
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

from app.ocr_engine import recognize_image


BASE_DIR = Path(__file__).resolve().parent
SAMPLES_DIR = BASE_DIR / "samples"


def main() -> int:
    """Сравнить фактические поля с samples/expected.json."""

    expected = json.loads(
        (SAMPLES_DIR / "expected.json").read_text(encoding="utf-8")
    )
    report = {}
    passed = 0

    # Один экземпляр OCR переиспользуется внутри recognize_image благодаря кэшу.
    for name, wanted in expected.items():
        with Image.open(SAMPLES_DIR / name) as image:
            actual = recognize_image(image)
        ok = all(actual.get(key) == value for key, value in wanted.items())
        passed += int(ok)
        report[name] = {"ok": ok, "expected": wanted, "actual": actual}
        marker = "OK" if ok else "FAIL"
        print(
            f"{marker:4} {name:10}  model={actual['model']!r}  "
            f"serial={actual['serial_number']!r}"
        )

    # Отчёт удобно прикладывать к ревью или публиковать вместе с проектом.
    (BASE_DIR / "verification_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\nПройдено: {passed}/{len(expected)}")
    return 0 if passed == len(expected) else 1


if __name__ == "__main__":
    raise SystemExit(main())
