import argparse
import os
import sys

# 添加当前工作区路径到系统路径中
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from ocr_utils import load_app_config
from task_runner import TaskRunner

def parse_args():
    parser = argparse.ArgumentParser(description="巅峰赛（排位赛）独立自动化程序")
    parser.add_argument(
        "--port",
        type=int,
        help="MuMu ADB 端口，例如 7555；等价于设备 127.0.0.1:7555"
    )
    parser.add_argument(
        "--device",
        help="完整 ADB 设备地址，例如 127.0.0.1:7555；优先级高于 --port"
    )
    return parser.parse_args()

def main():
    args = parse_args()
    print("====================================================")
    print("   巅峰赛 (排位赛) 独立自动化日常挑战程序启动       ")
    print("====================================================")
    
    app_config = load_app_config()
    if args.device:
        app_config["device_id"] = args.device
    elif args.port is not None:
        app_config["device_id"] = f"127.0.0.1:{args.port}"

    print(f"ADB 设备: {app_config['device_id']}")
    # 强制将目标任务设为 '巅峰'
    runner = TaskRunner(app_config, BASE_DIR, dry_run=False)
    
    try:
        result = runner.run(target_task="巅峰")
        print("----------------------------------------------------")
        print(f"巅峰赛挑战独立运行完毕。状态: {result.get('status')}, 原因: {result.get('reason')}")
        print("====================================================")
    except Exception as exc:
        print(f"运行发生异常: {exc}")

if __name__ == "__main__":
    main()
