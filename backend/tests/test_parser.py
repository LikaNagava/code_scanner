from __future__ import annotations

import unittest

from app.parser import OcrItem, extract_fields


def item(text: str, confidence: float, bbox: list[int]) -> OcrItem:
    return OcrItem(text=text, confidence=confidence, bbox=bbox)


class ParserTests(unittest.TestCase):
    def assert_fields(self, items, model, serial):
        result = extract_fields(items)
        self.assertEqual(model, result["model"])
        self.assertEqual(serial, result["serial_number"])

    def test_1_separate_factory_number_label(self):
        self.assert_fields(
            [
                item("МОДЕЛЬ", 0.99, [49, 328, 159, 358]),
                item("2H118", 0.99, [207, 329, 280, 353]),
                item("ЗАВОДСКОЙ", 0.95, [386, 327, 537, 356]),
                item("N", 0.55, [548, 331, 575, 352]),
                item("19424", 0.99, [626, 330, 693, 354]),
            ],
            "2H118",
            "19424",
        )

    def test_2_inline_fields_and_cyrillic_model(self):
        self.assert_fields(
            [
                item("МОДЕЛЬ 2Б125", 0.99, [70, 259, 324, 296]),
                item("№ 6560", 0.88, [365, 259, 495, 296]),
            ],
            "2Б125",
            "6560",
        )

    def test_2_corrects_common_letter_b_confusion(self):
        self.assert_fields(
            [
                item("МОДЕЛЬ", 0.99, [70, 259, 211, 296]),
                item("25125", 0.90, [222, 260, 324, 294]),
                item("№", 0.80, [365, 262, 410, 291]),
                item("6560", 0.99, [414, 259, 495, 291]),
            ],
            "2Б125",
            "6560",
        )

    def test_3_table_values(self):
        self.assert_fields(
            [
                item("Модель", 0.99, [29, 95, 99, 119]),
                item("OC-3015GT", 0.99, [368, 94, 469, 117]),
                item("Серийный №", 0.99, [31, 122, 139, 143]),
                item("JY202408020001-5", 0.99, [336, 120, 496, 141]),
            ],
            "OC-3015GT",
            "JY202408020001-5",
        )

    def test_4_joins_split_model(self):
        self.assert_fields(
            [
                item("МОДЕЛЬ", 0.99, [14, 137, 81, 158]),
                item("KP", 0.97, [130, 134, 160, 158]),
                item("120", 0.99, [159, 134, 201, 158]),
                item("СЕРИЙНЫЙ", 0.99, [15, 165, 119, 189]),
                item("№", 0.78, [112, 165, 126, 189]),
                item("0509114063157", 0.99, [130, 165, 248, 189]),
            ],
            "KP 120",
            "0509114063157",
        )

    def test_5_large_modern_plate(self):
        self.assert_fields(
            [
                item("Модель", 0.99, [129, 329, 328, 390]),
                item("3200×175", 0.98, [820, 328, 1064, 380]),
                item("Серийный", 0.99, [134, 582, 393, 637]),
                item("N", 0.75, [399, 584, 462, 630]),
                item("BM275436", 0.99, [821, 581, 1071, 632]),
            ],
            "3200×175",
            "BM275436",
        )


if __name__ == "__main__":
    unittest.main()
