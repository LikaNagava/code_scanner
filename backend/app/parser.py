"""Извлечение модели и серийного номера из блоков PaddleOCR.

OCR возвращает отдельные фрагменты текста с координатами. Парсер сначала
ищет подписи «Модель», «Серийный», «Заводской №», а затем берёт значение
из того же блока или ближайший подходящий фрагмент справа от подписи.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Iterable, Literal


FieldName = Literal["model", "serial"]


@dataclass(frozen=True)
class OcrItem:
    """Один распознанный текстовый фрагмент и его положение на фотографии."""

    text: str
    confidence: float
    bbox: list[int]

    @property
    def center_y(self) -> float:
        return (self.bbox[1] + self.bbox[3]) / 2

    @property
    def height(self) -> int:
        return max(1, self.bbox[3] - self.bbox[1])


@dataclass(frozen=True)
class FoundValue:
    """Уже найденное и нормализованное значение нужного поля."""

    value: str
    confidence: float
    bbox: list[int]


# Регулярные выражения допускают частые OCR-подмены: 0 вместо О,
# латинскую H вместо кириллической Н и разные варианты знака номера.
MODEL_LABEL_RE = re.compile(
    r"(?:\bМ[О0]ДЕ[ЛI1][ЬБ]?\b|\bMODEL\b)",
    re.IGNORECASE,
)
SERIAL_LABEL_RE = re.compile(
    r"(?:"
    r"\bСЕРИ[ЙИ1][НH]Ы[ЙИ1]\b"
    r"|\bЗАВОДСК[ОO]Й\b"
    r"|\bSERIAL(?:\s+(?:NO|NUMBER))?\b"
    r"|\bS[\\/]?N\b"
    r")",
    re.IGNORECASE,
)
NUMBER_SIGN_RE = re.compile(
    r"(?:№|#|\bN(?:[OОº°]\.?)*\b)",
    re.IGNORECASE,
)

MODEL_TOKEN_RE = re.compile(
    r"[A-ZА-ЯЁ0-9]"
    r"[A-ZА-ЯЁ0-9./×XХxх*\-]*"
    r"(?:\s+[A-ZА-ЯЁ0-9][A-ZА-ЯЁ0-9./×XХxх*\-]*){0,2}",
    re.IGNORECASE,
)
SERIAL_TOKEN_RE = re.compile(
    r"[A-ZА-ЯЁ0-9][A-ZА-ЯЁ0-9./\-]{2,49}",
    re.IGNORECASE,
)

STOP_WORD_RE = re.compile(
    r"\b(?:КЛАСС|МОЩНОСТЬ|НАПРЯЖЕНИЕ|ЧАСТОТА|ГОД|ДАТА|"
    r"ВЫПУСКА|МАССА|ВЕС|СКОРОСТЬ|ДАВЛЕНИЕ|MODEL|SERIAL)\b",
    re.IGNORECASE,
)


def clean_text(text: str) -> str:
    """Убрать переносы и повторяющиеся пробелы из OCR-текста."""

    return re.sub(r"\s+", " ", str(text).replace("\n", " ")).strip()


def find_model_label(text: str) -> re.Match[str] | None:
    return MODEL_LABEL_RE.search(clean_text(text))


def find_serial_label(text: str) -> re.Match[str] | None:
    return SERIAL_LABEL_RE.search(clean_text(text))


def find_number_sign(text: str) -> re.Match[str] | None:
    return NUMBER_SIGN_RE.search(clean_text(text))


def is_number_sign_only(text: str) -> bool:
    value = re.sub(r"[\s.:;\-]", "", clean_text(text).upper())
    return value in {"№", "#", "N", "NO", "NО", "Nº", "N°"}


def canonical_model(value: str) -> str:
    """Привести обозначение модели к единому виду для ответа API."""

    value = clean_text(value).upper()
    value = value.replace("–", "-").replace("—", "-")
    value = re.sub(r"(?<=\d)[XХxх*](?=\d)", "×", value)
    value = re.sub(r"\s*×\s*", "×", value)
    value = re.sub(r"\s*-\s*", "-", value)
    value = re.sub(r"\s+", " ", value).strip(" .,:;|_")

    # Типичная OCR-ошибка на советской модели 2Б125: буква Б похожа на 5.
    if re.fullmatch(r"2[5Б]125", value):
        return "2Б125"

    return value


def canonical_serial(value: str) -> str:
    """Очистить серийный номер и исправить очевидные OCR-подмены."""

    value = clean_text(value).upper()
    value = value.replace("–", "-").replace("—", "-")
    value = re.sub(r"\s+", "", value).strip(" .,:;|_")
    chars = list(value)

    # O/0 и I/1 исправляются только внутри цифровых последовательностей.
    for index, char in enumerate(chars):
        left_digit = index > 0 and chars[index - 1].isdigit()
        right_digit = index + 1 < len(chars) and chars[index + 1].isdigit()
        if char in {"O", "О"} and (left_digit or right_digit):
            chars[index] = "0"
        elif char in {"I", "L", "І"} and left_digit and right_digit:
            chars[index] = "1"

    return "".join(chars)


def valid_model(value: str) -> bool:
    """Отсеять даты, чистые числа и случайный текст вместо модели."""

    if not 2 <= len(value) <= 32:
        return False
    if not any(char.isdigit() for char in value):
        return False
    if value.isdigit() or re.fullmatch(r"(?:19|20)\d{2}", value):
        return False
    return bool(re.fullmatch(r"[A-ZА-ЯЁ0-9./×\- ]+", value))


def valid_serial(value: str) -> bool:
    """Проверить, что кандидат похож на серийный номер, а не на дату."""

    if not 3 <= len(value) <= 50:
        return False
    if not any(char.isdigit() for char in value):
        return False
    if re.fullmatch(r"(?:19|20)\d{2}", value):
        return False
    if re.fullmatch(r"(?:19|20)\d{2}[.\-/]\d{1,2}", value):
        return False
    return bool(re.fullmatch(r"[A-ZА-ЯЁ0-9./\-]+", value))


def slice_bbox(item: OcrItem, start: int, end: int) -> list[int]:
    """Оценить bbox значения, если подпись и значение склеены OCR."""

    text_length = max(1, len(item.text))
    x1, y1, x2, y2 = item.bbox
    width = x2 - x1
    return [
        x1 + round(width * start / text_length),
        y1,
        x1 + round(width * end / text_length),
        y2,
    ]


def inline_model(item: OcrItem) -> FoundValue | None:
    """Извлечь модель из единой строки вида «Модель OC-3015GT»."""

    label = find_model_label(item.text)
    if not label:
        return None

    tail_start = label.end()
    tail = item.text[tail_start:]

    stop_positions = []
    for pattern in (SERIAL_LABEL_RE, NUMBER_SIGN_RE, STOP_WORD_RE):
        stop = pattern.search(tail)
        if stop:
            stop_positions.append(stop.start())
    if stop_positions:
        tail = tail[: min(stop_positions)]

    match = MODEL_TOKEN_RE.search(tail)
    if not match:
        return None

    value = canonical_model(match.group())
    if not valid_model(value):
        return None

    start = tail_start + match.start()
    end = tail_start + match.end()
    return FoundValue(value, item.confidence, slice_bbox(item, start, end))


def inline_serial(item: OcrItem) -> FoundValue | None:
    """Извлечь номер из единой строки вида «Серийный № A12345»."""

    label = find_serial_label(item.text)
    if label:
        tail_start = label.end()
    else:
        number_sign = find_number_sign(item.text)
        if not number_sign:
            return None
        tail_start = number_sign.end()

    tail = re.sub(
        r"^\s*(?:№|#|N(?:[OОº°]\.?)?)?\s*[:\-]?\s*",
        "",
        item.text[tail_start:],
        flags=re.IGNORECASE,
    )
    match = SERIAL_TOKEN_RE.search(tail)
    if not match:
        return None

    raw_value = match.group()
    value = canonical_serial(raw_value)
    if not valid_serial(value):
        return None

    start = item.text.upper().find(raw_value.upper(), tail_start)
    if start < 0:
        start = tail_start + match.start()
    return FoundValue(
        value,
        item.confidence,
        slice_bbox(item, start, start + len(raw_value)),
    )


def is_label_item(item: OcrItem) -> bool:
    return bool(
        find_model_label(item.text)
        or find_serial_label(item.text)
        or is_number_sign_only(item.text)
    )


def same_row(left: OcrItem, right: OcrItem) -> bool:
    """Определить по координатам, находятся ли два блока в одной строке."""

    tolerance = max(left.height, right.height) * 0.85
    return abs(left.center_y - right.center_y) <= tolerance


def right_side_candidates(
    items: Iterable[OcrItem],
    label: OcrItem,
) -> list[OcrItem]:
    """Найти справа от подписи блоки, которые могут содержать значение."""

    candidates = [
        item
        for item in items
        if item is not label
        and same_row(label, item)
        and item.bbox[0] >= label.bbox[2] - label.height * 0.35
        and not is_label_item(item)
        and not STOP_WORD_RE.search(item.text)
    ]
    return sorted(candidates, key=lambda item: (item.bbox[0], item.bbox[1]))


def value_right_of_label(
    items: list[OcrItem],
    label: OcrItem,
    field: FieldName,
) -> FoundValue | None:
    """Собрать значение из одного или нескольких соседних OCR-блоков.

    Модель вроде «KP 120» может распознаться двумя блоками. Поэтому модель
    накапливается по частям, пока объединённая строка не пройдёт проверку.
    """

    candidates = right_side_candidates(items, label)
    if not candidates:
        return None

    if field == "serial":
        for item in candidates:
            value = canonical_serial(item.text)
            if valid_serial(value):
                return FoundValue(value, item.confidence, item.bbox)
        return None

    combined: list[OcrItem] = []
    for item in candidates:
        if combined:
            previous = combined[-1]
            gap = item.bbox[0] - previous.bbox[2]
            gap_limit = max(label.height, previous.height, item.height) * 2.0
            if gap > gap_limit:
                break
        combined.append(item)
        value = canonical_model(" ".join(part.text for part in combined))
        if valid_model(value):
            return FoundValue(
                value=value,
                confidence=min(part.confidence for part in combined),
                bbox=[
                    min(part.bbox[0] for part in combined),
                    min(part.bbox[1] for part in combined),
                    max(part.bbox[2] for part in combined),
                    max(part.bbox[3] for part in combined),
                ],
            )
    return None


def find_by_geometry(
    items: list[OcrItem],
    field: FieldName,
) -> FoundValue | None:
    """Найти поле по взаимному расположению подписи и значения."""

    if field == "model":
        labels = [item for item in items if find_model_label(item.text)]
    else:
        labels = [item for item in items if find_serial_label(item.text)]
        if not labels:
            labels = [item for item in items if is_number_sign_only(item.text)]

    results = [
        result
        for label in labels
        if (result := value_right_of_label(items, label, field))
    ]
    if not results:
        return None
    return max(results, key=lambda result: result.confidence)


def union_bbox(values: list[FoundValue]) -> list[int]:
    """Построить общий прямоугольник модели и серийного номера."""

    return [
        min(value.bbox[0] for value in values),
        min(value.bbox[1] for value in values),
        max(value.bbox[2] for value in values),
        max(value.bbox[3] for value in values),
    ]


def extract_fields(items: list[OcrItem]) -> dict[str, Any]:
    """Сформировать окончательный ответ API из списка OCR-блоков."""

    # Сначала используем самый точный вариант: подпись и значение уже попали
    # в один OCR-блок. Геометрический поиск включается как запасной путь.
    inline_models = [
        result for item in items if (result := inline_model(item))
    ]
    inline_serials = [
        result for item in items if (result := inline_serial(item))
    ]

    model = (
        max(inline_models, key=lambda result: result.confidence)
        if inline_models
        else find_by_geometry(items, "model")
    )
    serial = (
        max(inline_serials, key=lambda result: result.confidence)
        if inline_serials
        else find_by_geometry(items, "serial")
    )

    found = [value for value in (model, serial) if value]
    status = "success" if len(found) == 2 else "partial" if found else "not_found"
    confidence = min((value.confidence for value in found), default=0.0)

    return {
        "status": status,
        "serial_number": serial.value if serial else None,
        "model": model.value if model else None,
        "confidence": round(confidence, 4),
        "code_type": "text",
        "bbox": union_bbox(found) if found else [],
    }
