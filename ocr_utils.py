import json
import os
import re
import shutil
from copy import deepcopy
from dataclasses import dataclass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_CONFIG_NAME = "config.local.json"
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


def deep_update(base, updates):
    for key, value in (updates or {}).items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            deep_update(base[key], value)
        else:
            base[key] = value
    return base


def find_adb_path(configured_path=None):
    candidates = []

    env_path = os.environ.get("ADB_PATH")
    if env_path:
        candidates.append(env_path)

    if configured_path:
        candidates.append(configured_path)

    path_adb = shutil.which("adb")
    if path_adb:
        candidates.append(path_adb)

    candidates.extend(
        [
            r"C:\Netease\MuMu\nx_main\adb.exe",
            r"C:\Program Files\Netease\MuMuPlayerGlobal-12.0\shell\adb.exe",
            r"C:\Program Files\Netease\MuMuPlayer-12.0\shell\adb.exe",
            r"C:\Program Files\BlueStacks_nxt\HD-Adb.exe",
            r"C:\Program Files\BlueStacks\HD-Adb.exe",
            r"C:\Program Files\Microvirt\MEmu\adb.exe",
            r"C:\LDPlayer\LDPlayer9\adb.exe",
            r"C:\Program Files\dnplayerext2\adb.exe",
        ]
    )

    seen = set()
    for candidate in candidates:
        if not candidate:
            continue
        normalized = os.path.abspath(os.path.expandvars(os.path.expanduser(candidate)))
        if normalized.lower() in seen:
            continue
        seen.add(normalized.lower())
        if os.path.exists(normalized):
            return normalized

    return configured_path or "adb"


def load_app_config(path=None):
    config = deepcopy(DEFAULT_CONFIG)
    config_path = path or os.path.join(BASE_DIR, "config.json")
    file_config = load_json(config_path, {})

    if file_config:
        deep_update(config, file_config)

    # config.local.json is for per-machine deployment overrides. It is ignored
    # by git and should contain local adb_path/device_id changes.
    if path is None or os.path.abspath(config_path) == os.path.abspath(os.path.join(BASE_DIR, "config.json")):
        local_config = load_json(os.path.join(BASE_DIR, LOCAL_CONFIG_NAME), {})
        if local_config:
            deep_update(config, local_config)

    config["adb_path"] = find_adb_path(config.get("adb_path"))

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
