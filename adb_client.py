import os
import subprocess


def adb_command(adb_path, args, capture_output=True, text=True):
    return subprocess.run(
        [adb_path, *args],
        capture_output=capture_output,
        text=text,
        encoding="utf-8" if text else None,
        errors="replace" if text else None,
        check=False
    )


def adb_devices(adb_path):
    result = adb_command(adb_path, ["devices"])
    return result.stdout


def is_tcp_device(device_id):
    return ":" in device_id and device_id.replace(".", "").replace(":", "").isdigit()


def connect_adb_device(adb_path, device_id, extra_ports=None):
    targets = []

    if is_tcp_device(device_id):
        targets.append(device_id)

    for port in extra_ports or []:
        target = f"127.0.0.1:{port}"

        if target not in targets:
            targets.append(target)

    for target in targets:
        adb_command(adb_path, ["connect", target])


def ensure_adb_device(adb_path, device_id):
    """Start ADB and verify that the configured emulator is connected."""
    adb_command(adb_path, ["start-server"])
    connect_adb_device(adb_path, device_id, [7555, 5557, 16384, 16416])

    stdout = adb_devices(adb_path)

    # 1. 尝试直接检测配置的设备是否在线且正常
    if f"{device_id}\tdevice" in stdout:
        return device_id

    # 2. 如果不在线，解析所有当前在线的活跃设备
    active_devices = []
    for line in stdout.strip().split("\n"):
        if not line or "List of devices attached" in line:
            continue
        parts = line.split("\t")
        if len(parts) == 2 and parts[1] == "device":
            active_devices.append(parts[0])

    if not active_devices:
        raise RuntimeError(
            f"未检测到任何处于运行状态的模拟器设备。\n\nADB devices:\n{stdout}"
        )

    # 3. 如果有在线设备，自动选择一个并记录日志提醒
    # 如果只有一个，直接选它
    if len(active_devices) == 1:
        fallback_id = active_devices[0]
        print(f"[ADB] 配置设备 {device_id} 不在线，自动切换到唯一活跃设备: {fallback_id}")
        return fallback_id

    # 如果有多个，优先匹配含有我们指定 IP 或常用模拟器端口的设备，否则直接选第一个
    preferred_ports = ["7555", "16416", "5557", "16384"]
    for port in preferred_ports:
        for dev in active_devices:
            if port in dev:
                print(f"[ADB] 配置设备 {device_id} 不在线，根据优先级自动切换到活跃设备: {dev}")
                return dev

    fallback_id = active_devices[0]
    print(f"[ADB] 配置设备 {device_id} 不在线，自动切换到首个活跃设备: {fallback_id}")
    return fallback_id


def capture_screenshot(adb_path, device_id, save_path=None):
    """Capture a PNG screenshot from MuMu through ADB and return a BGR image."""
    import cv2
    import numpy as np

    # 自动获取并使用当前物理连接状态良好的设备 ID
    device_id = ensure_adb_device(adb_path, device_id)

    result = subprocess.run(
        [
            adb_path,
            "-s",
            device_id,
            "exec-out",
            "screencap",
            "-p"
        ],
        capture_output=True,
        check=False
    )

    if not result.stdout:
        error_msg = result.stderr.decode(errors="ignore")
        raise RuntimeError(f"ADB截图失败:\n{error_msg}")

    img_array = np.frombuffer(result.stdout, dtype=np.uint8)
    image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    if image is None:
        raise RuntimeError("OpenCV 图片解码失败")

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        cv2.imwrite(save_path, image)

    return image
