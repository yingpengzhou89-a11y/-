import sys
import os

# 确保能加载当前路径下的模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ocr_utils import load_app_config
from actions import adb_swipe
from adb_client import ensure_adb_device

def main():
    print("====================================================")
    print("        日常任务划屏测试与参数微调工具")
    print("====================================================")
    
    # 1. 加载配置
    try:
        app_config = load_app_config()
        adb_path = app_config.get("adb_path", "adb")
        configured_device_id = app_config.get("device_id", "127.0.0.1:16384")
    except Exception as e:
        print(f"[错误] 加载项目配置 config.json 失败: {e}")
        return
        
    # 2. 检测并连接设备
    print(f"正在连接设备: {configured_device_id} ...")
    try:
        device_id = ensure_adb_device(adb_path, configured_device_id)
        print(f"[成功] 已成功连接到运行中的设备 ID: {device_id}")
    except Exception as e:
        print(f"[错误] ADB 设备初始化失败: {e}")
        return

    # 默认滑动参数
    DEFAULT_X1 = 700
    DEFAULT_Y1 = 550
    DEFAULT_X2 = 700
    DEFAULT_Y2 = 360
    DEFAULT_DURATION = 1000

    print("\n[使用说明]")
    print("- 直接回车或输入 'd': 执行默认滑动参数 (700 550 -> 700 360, 持续 1000ms)")
    print("- 输入单个数字 (如 '400'): 自定义滑屏终点 y2 (y1默认为550, 持续1000ms)")
    print("- 输入两个数字 (如 '400 600'): 自定义终点 y2 和滑动时长 duration_ms")
    print("- 输入三个数字 (如 '550 360 1000'): 自定义 y1 y2 和 duration_ms")
    print("- 输入五个数字 (如 '700 550 700 360 1000'): 完整指定 x1 y1 x2 y2 duration_ms")
    print("- 输入 'q' 或 'exit': 退出程序\n")

    while True:
        try:
            user_input = input("请输入滑动参数 >> ").strip().lower()
        except KeyboardInterrupt:
            print("\n程序已安全退出。")
            break

        if user_input in {"q", "exit", "quit"}:
            print("程序退出。")
            break

        # 默认参数情况
        if not user_input or user_input == "d" or user_input == "default":
            x1, y1, x2, y2, duration = DEFAULT_X1, DEFAULT_Y1, DEFAULT_X2, DEFAULT_Y2, DEFAULT_DURATION
            print(f"[滑屏指令] 执行默认滑动: ({x1}, {y1}) -> ({x2}, {y2}), 时长: {duration}ms")
            adb_swipe(adb_path, device_id, x1, y1, x2, y2, duration)
            continue

        parts = user_input.split()
        
        try:
            # 1 个数字：输入 y2
            if len(parts) == 1:
                y2 = int(parts[0])
                x1, y1, x2, duration = DEFAULT_X1, DEFAULT_Y1, DEFAULT_X2, DEFAULT_DURATION
                print(f"[滑屏指令] 执行自定义滑动: ({x1}, {y1}) -> ({x2}, {y2}), 时长: {duration}ms")
                adb_swipe(adb_path, device_id, x1, y1, x2, y2, duration)
                
            # 2 个数字：输入 y2 duration
            elif len(parts) == 2:
                y2 = int(parts[0])
                duration = int(parts[1])
                x1, y1, x2 = DEFAULT_X1, DEFAULT_Y1, DEFAULT_X2
                print(f"[滑屏指令] 执行自定义滑动: ({x1}, {y1}) -> ({x2}, {y2}), 时长: {duration}ms")
                adb_swipe(adb_path, device_id, x1, y1, x2, y2, duration)
                
            # 3 个数字：输入 y1 y2 duration
            elif len(parts) == 3:
                y1 = int(parts[0])
                y2 = int(parts[1])
                duration = int(parts[2])
                x1, x2 = DEFAULT_X1, DEFAULT_X2
                print(f"[滑屏指令] 执行自定义滑动: ({x1}, {y1}) -> ({x2}, {y2}), 时长: {duration}ms")
                adb_swipe(adb_path, device_id, x1, y1, x2, y2, duration)
                
            # 5 个数字：完整参数 x1 y1 x2 y2 duration
            elif len(parts) == 5:
                x1 = int(parts[0])
                y1 = int(parts[1])
                x2 = int(parts[2])
                y2 = int(parts[3])
                duration = int(parts[4])
                print(f"[滑屏指令] 执行自定义滑动: ({x1}, {y1}) -> ({x2}, {y2}), 时长: {duration}ms")
                adb_swipe(adb_path, device_id, x1, y1, x2, y2, duration)
                
            else:
                print("[错误] 输入数字个数不匹配，请按说明输入（支持1个、2个、3个、5个数字，空格分隔）。")
        except ValueError:
            print("[错误] 输入中含有非数字字符，请输入有效的整数参数或指令。")
        except Exception as e:
            print(f"[滑屏异常] 执行滑动失败: {e}")

if __name__ == "__main__":
    main()
