import json
import os
import re
from dataclasses import dataclass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_RAPIDOCR_ENGINE = None

DEFAULT_CONFIG = {
    "adb_path": r"C:\Netease\MuMu\nx_main\adb.exe",
    "device_id": "127.0.0.1:7555",
    "ocr_backend": "rapidocr",
    "scan_mode": "fast_fullscreen",
    "ocr_min_score": 0.5,
    "resolution": {
        "width": 1280,
        "height": 720
    }
}


@dataclass(frozen=True)
class Box:
    x1: int
    y1: int
    x2: int
    y2: int


def load_json(path, default=None):
    if not os.path.exists(path):
        return default

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_app_config(path=None):
    config = dict(DEFAULT_CONFIG)
    file_config = load_json(path or os.path.join(BASE_DIR, "config.json"), {})

    if file_config:
        config.update(file_config)

    return config


def normalize_box(box):
    return Box(
        int(box["x1"]),
        int(box["y1"]),
        int(box["x2"]),
        int(box["y2"])
    )


def normalize_text(text):
    if not text:
        return ""

    return re.sub(r"\W+", "", text).upper()


def image_to_numpy(image):
    if hasattr(image, "size") and not hasattr(image, "shape"):
        import numpy as np

        return np.array(image.convert("RGB"))

    return image


def create_rapidocr_engine():
    global _RAPIDOCR_ENGINE

    if _RAPIDOCR_ENGINE is not None:
        return _RAPIDOCR_ENGINE

    try:
        from rapidocr_onnxruntime import RapidOCR
    except ImportError:
        try:
            from rapidocr import RapidOCR
        except ImportError as exc:
            raise RuntimeError(
                "未安装 RapidOCR，请先安装 rapidocr-onnxruntime"
            ) from exc

    _RAPIDOCR_ENGINE = RapidOCR()
    return _RAPIDOCR_ENGINE


def rapidocr_items(image, app_config):
    engine = create_rapidocr_engine()
    result, _ = engine(
        image_to_numpy(image),
        use_det=True,
        use_cls=False,
        use_rec=True
    )
    items = []

    for item in result or []:
        if len(item) < 3:
            continue

        box, text, score = item[:3]

        if score < app_config.get("ocr_min_score", 0.5):
            continue

        x = sum(point[0] for point in box) / len(box)
        y = sum(point[1] for point in box) / len(box)
        items.append(
            {
                "box": box,
                "text": text,
                "score": score,
                "x": x,
                "y": y
            }
        )

    return items
