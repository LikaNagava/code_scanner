"""Подготовка фотографий и безопасный вызов PaddleOCR.

Модуль ничего не знает про HTTP. Он принимает PIL-изображение, увеличивает
слишком мелкий текст, запускает OCR и передаёт распознанные блоки парсеру.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from threading import Lock
from typing import Any

# PaddlePaddle 3.3.x имеет известную ошибку CPU/oneDNN. Отключаем oneDNN
# до импорта PaddleOCR; requirements.txt дополнительно фиксирует 3.2.2.
os.environ.setdefault("FLAGS_use_mkldnn", "0")

import numpy as np
from paddleocr import PaddleOCR
from PIL import Image, ImageOps

from .parser import OcrItem, clean_text, extract_fields


# Один экземпляр PaddleOCR не должен одновременно обслуживаться несколькими
# потоками, поэтому вызов predict защищён блокировкой.
OCR_LOCK = Lock()

# Маленькие фотографии увеличиваются для лучшего чтения букв, а очень большие
# уменьшаются, чтобы не тратить лишнюю память и время процессора.
MIN_LONGEST_SIDE = 1400
MAX_LONGEST_SIDE = 2400


@dataclass(frozen=True)
class PreparedImage:
    """Изображение для OCR и коэффициенты возврата к исходным координатам."""

    array: np.ndarray
    scale_x: float
    scale_y: float


@lru_cache(maxsize=1)
def get_ocr() -> PaddleOCR:
    """Создать OCR при первом запросе и затем переиспользовать его.

    Загрузка моделей занимает заметное время, поэтому lru_cache гарантирует,
    что тяжёлая инициализация произойдёт только один раз за запуск сервера.
    """

    return PaddleOCR(
        text_detection_model_name="PP-OCRv5_mobile_det",
        text_recognition_model_name="eslav_PP-OCRv5_mobile_rec",
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
        text_rec_score_thresh=0.25,
        enable_mkldnn=False,
        device=os.getenv("OCR_DEVICE", "cpu"),
    )


def prepare_image(image: Image.Image) -> PreparedImage:
    """Исправить EXIF-поворот, привести к RGB и подобрать рабочий размер."""

    image = ImageOps.exif_transpose(image).convert("RGB")
    original_width, original_height = image.size
    longest_side = max(image.size)

    if longest_side < MIN_LONGEST_SIDE:
        scale = MIN_LONGEST_SIDE / longest_side
    elif longest_side > MAX_LONGEST_SIDE:
        scale = MAX_LONGEST_SIDE / longest_side
    else:
        scale = 1.0

    if scale != 1.0:
        image = image.resize(
            (
                max(1, round(original_width * scale)),
                max(1, round(original_height * scale)),
            ),
            Image.Resampling.LANCZOS,
        )

    return PreparedImage(
        array=np.asarray(image),
        scale_x=image.width / original_width,
        scale_y=image.height / original_height,
    )


def native_list(value: Any) -> list[Any]:
    """Преобразовать список Paddle/NumPy в обычный список Python."""

    if value is None:
        return []
    if hasattr(value, "tolist"):
        return value.tolist()
    return list(value)


def convert_ocr_result(
    results: list[Any],
    scale_x: float,
    scale_y: float,
) -> list[OcrItem]:
    """Привести результат PaddleOCR к простым OcrItem.

    Координаты PaddleOCR относятся к увеличенной копии. Деление на scale_x и
    scale_y возвращает bbox к размерам оригинального загруженного изображения.
    """

    if not results:
        return []

    raw = results[0].json
    data = raw.get("res", raw)
    texts = native_list(data.get("rec_texts"))
    scores = native_list(data.get("rec_scores"))
    boxes = native_list(data.get("rec_boxes"))

    # Некоторые версии PaddleOCR возвращают полигоны вместо прямоугольников.
    # В этом случае строим минимальный прямоугольник вокруг каждого полигона.
    if not boxes:
        polygons = native_list(data.get("rec_polys"))
        for polygon in polygons:
            xs = [point[0] for point in polygon]
            ys = [point[1] for point in polygon]
            boxes.append([min(xs), min(ys), max(xs), max(ys)])

    items: list[OcrItem] = []
    for text, score, box in zip(texts, scores, boxes):
        text = clean_text(text)
        confidence = float(score)
        # Слабые OCR-гипотезы чаще создают ложные модели и серийные номера.
        if not text or confidence < 0.25:
            continue

        x1, y1, x2, y2 = [float(number) for number in box]
        items.append(
            OcrItem(
                text=text,
                confidence=confidence,
                bbox=[
                    round(x1 / scale_x),
                    round(y1 / scale_y),
                    round(x2 / scale_x),
                    round(y2 / scale_y),
                ],
            )
        )
    return items


def recognize_image(image: Image.Image, debug: bool = False) -> dict[str, Any]:
    """Выполнить полный конвейер: подготовка → OCR → разбор полей."""

    prepared = prepare_image(image)
    with OCR_LOCK:
        raw_results = list(get_ocr().predict(prepared.array))
    items = convert_ocr_result(
        raw_results,
        scale_x=prepared.scale_x,
        scale_y=prepared.scale_y,
    )
    response = extract_fields(items)
    if debug:
        response["ocr"] = [
            {
                "text": item.text,
                "confidence": round(item.confidence, 4),
                "bbox": item.bbox,
            }
            for item in items
        ]
    return response
