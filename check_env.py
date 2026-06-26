import argparse
import importlib
import os
import shutil
import socket
import subprocess
import sys

from ocr_utils import BASE_DIR, find_adb_path, load_app_config


REQUIRED_MODULES = [
    ("cv2", "opencv-python"),
    ("numpy", "numpy"),
]

OCR_MODULES = [
    ("rapidocr_onnxruntime", "rapidocr-onnxruntime"),
    ("rapidocr", "rapidocr"),
]


def print_result(level, message):
    print(f"[{level}] {message}")


def module_available(name):
    try:
        importlib.import_module(name)
        return True
    except Exception:
        return False


def check_python():
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        print_result("OK", f"Python {version.major}.{version.minor}.{version.micro}: {sys.executable}")
        return True

    print_result("FAIL", f"Python 版本过低：{version.major}.{version.minor}.{version.micro}，建议 Python 3.9+")
    return False


def check_modules():
    ok = True
    for module_name, package_name in REQUIRED_MODULES:
        if module_available(module_name):
            print_result("OK", f"依赖已安装：{package_name}")
        else:
            print_result("FAIL", f"缺少依赖：{package_name}，请运行 install.bat 或 python -m pip install -r requirements.txt")
            ok = False

    if any(module_available(module_name) for module_name, _ in OCR_MODULES):
        print_result("OK", "OCR 依赖已安装：rapidocr")
    else:
        print_result("FAIL", "缺少 OCR 依赖：rapidocr-onnxruntime")
        ok = False

    return ok


def check_config():
    try:
        config = load_app_config()
    except Exception as exc:
        print_result("FAIL", f"配置读取失败：{exc}")
        return None

    print_result("OK", "配置读取成功：config.json" + (" + config.local.json" if os.path.exists(os.path.join(BASE_DIR, "config.local.json")) else ""))
    print_result("OK", f"当前设备配置：{config.get('device_id')}")
    return config


def check_adb(config):
    adb_path = find_adb_path((config or {}).get("adb_path"))
    if not adb_path or (adb_path == "adb" and not shutil.which("adb")):
        print_result("FAIL", "未找到 adb")
        return False

    if adb_path != "adb" and not os.path.exists(adb_path):
        print_result("FAIL", f"ADB 路径不存在：{adb_path}")
        return False

    print_result("OK", f"ADB 路径：{adb_path}")

    try:
        result = subprocess.run(
            [adb_path, "devices"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=8,
            check=False,
        )
    except Exception as exc:
        print_result("WARN", f"ADB 可执行但暂时无法读取设备列表：{exc}")
        return True

    devices = []
    for line in result.stdout.splitlines()[1:]:
        if line.strip() and "\tdevice" in line:
            devices.append(line.split("\t", 1)[0])

    if devices:
        print_result("OK", "在线设备：" + ", ".join(devices))
    else:
        print_result("WARN", "暂未检测到在线设备；请先启动模拟器，再在网页里扫描/绑定设备")

    return True


def check_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        busy = sock.connect_ex(("127.0.0.1", port)) == 0

    if busy:
        print_result("WARN", f"端口 {port} 已被占用；如果 dashboard 已打开可忽略，否则请关闭旧进程")
    else:
        print_result("OK", f"端口 {port} 可用")


def main():
    parser = argparse.ArgumentParser(description="Daily Dashboard deployment environment checker")
    parser.add_argument("--port", type=int, default=7556, help="Dashboard 端口")
    args = parser.parse_args()

    print("Daily Dashboard environment check")
    print("=" * 40)

    ok = check_python()
    ok = check_modules() and ok
    config = check_config()
    ok = (config is not None) and ok
    if config is not None:
        ok = check_adb(config) and ok
    check_port(args.port)

    print("=" * 40)
    if ok:
        print_result("OK", "基础环境检查通过")
        return 0

    print_result("FAIL", "基础环境检查未通过，请先修复上面的 FAIL 项")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
