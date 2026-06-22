import os
import sys

# 添加当前工作区路径到系统路径中
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from ocr_utils import load_app_config
from task_runner import TaskRunner

def main():
    print("====================================================")
    print("   巅峰赛 (排位赛) 独立自动化日常挑战程序启动       ")
    print("====================================================")
    
    app_config = load_app_config()
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
