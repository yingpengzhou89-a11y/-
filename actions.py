import subprocess
import time

from adb_client import ensure_adb_device


def adb_tap(adb_path, device_id, x, y):
    device_id = ensure_adb_device(adb_path, device_id)
    subprocess.run(
        [
            adb_path,
            "-s",
            device_id,
            "shell",
            "input",
            "tap",
            str(int(x)),
            str(int(y))
        ],
        check=False
    )


def adb_back(adb_path, device_id):
    device_id = ensure_adb_device(adb_path, device_id)
    subprocess.run(
        [
            adb_path,
            "-s",
            device_id,
            "shell",
            "input",
            "keyevent",
            "4"
        ],
        check=False
    )


def adb_swipe(adb_path, device_id, x1, y1, x2, y2, duration_ms=400):
    device_id = ensure_adb_device(adb_path, device_id)
    subprocess.run(
        [
            adb_path,
            "-s",
            device_id,
            "shell",
            "input",
            "swipe",
            str(int(x1)),
            str(int(y1)),
            str(int(x2)),
            str(int(y2)),
            str(int(duration_ms))
        ],
        check=False
    )


def tap_slot(adb_path, device_id, slot):
    box = slot["full_box"]
    x = (box["x1"] + box["x2"]) / 2
    y = (box["y1"] + box["y2"]) / 2
    adb_tap(adb_path, device_id, x, y)


def wait_after_tap(seconds=0.6):
    time.sleep(seconds)
