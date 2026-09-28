"""HTTP-слой приложения.

Здесь находятся веб-интерфейс, служебная проверка состояния и основной
POST /recognize. Сам OCR и разбор полей вынесены в отдельные модули, чтобы
API-код было проще читать, тестировать и изменять независимо.
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image, UnidentifiedImageError
from fastapi.middleware.cors import CORSMiddleware

from .ocr_engine import recognize_image


# Все пути считаются от папки app, поэтому запуск не зависит от текущей папки.
BASE_DIR = Path(__file__).resolve().parent
MAX_FILE_SIZE = 20 * 1024 * 1024
ALLOWED_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/bmp",
    "image/tiff",
}

app = FastAPI(
    title="Распознавание шильдиков оборудования",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CSS и JavaScript отдаются самим FastAPI по адресу /static/...
app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    """Показать мобильную страницу загрузки фотографии."""

    return (BASE_DIR / "static" / "index.html").read_text(encoding="utf-8")


@app.get("/health")
def health() -> dict[str, str]:
    """Быстрая проверка, что процесс сервера запущен."""

    return {"status": "ok"}


@app.post("/recognize")
async def recognize(
    file: UploadFile = File(...),
    debug: bool = Query(False, description="Добавить распознанные OCR-блоки"),
) -> dict:
    """Проверить изображение, распознать текст и вернуть нужные поля.

    Параметр debug=true добавляет в ответ все OCR-блоки. Он полезен при
    настройке новых форматов шильдиков, но обычному интерфейсу не нужен.
    """

    # Сразу отклоняем форматы, которые Pillow и OCR не должны обрабатывать.
    if file.content_type and file.content_type not in ALLOWED_TYPES and file.content_type != "application/octet-stream":
        raise HTTPException(
            status_code=415,
            detail="Поддерживаются JPG, PNG, WEBP, BMP и TIFF",
        )

    # Читаем на один байт больше лимита: так размер проверяется без сохранения
    # потенциально огромного файла на диск.
    image_bytes = await file.read(MAX_FILE_SIZE + 1)
    if len(image_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Размер изображения превышает 20 МБ",
        )

    # Проверяем не только расширение, но и реальное содержимое изображения.
    try:
        image = Image.open(BytesIO(image_bytes))
        image.load()
    except (UnidentifiedImageError, OSError) as error:
        raise HTTPException(
            status_code=400,
            detail="Не удалось прочитать изображение",
        ) from error

    # OCR нагружает процессор, поэтому переносим его из асинхронного цикла
    # FastAPI в рабочий поток. Веб-интерфейс при этом остаётся отзывчивым.
    try:
        return await run_in_threadpool(recognize_image, image, debug)
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка распознавания: {error}",
        ) from error
