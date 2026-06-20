import argparse
import json
import os
import sys

from ocr_utils import BASE_DIR, load_app_config
from image_io import load_image
from task_detector import detect_task_page
from task_runner import GuardrailError, TaskRunner


def parse_args():
    parser = argparse.ArgumentParser(description="日常任务 AI 自动执行入口")
    parser.add_argument(
        "--config",
        default=os.path.join(BASE_DIR, "config.json"),
        help="项目配置路径"
    )
    parser.add_argument(
        "--image",
        help="只分析本地任务页截图，不连接 ADB"
    )
    parser.add_argument(
        "--target",
        help="只处理标题包含该文本的未完成任务"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="生成决策和日志但不真正点击"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="输出 JSON"
    )
    return parser.parse_args()


def print_tasks(result):
    print("\n任务页识别结果")
    print("-" * 96)
    print(f"{'Row':<5}{'状态':<8}{'按钮':<12}{'进度':<10}任务")
    print("-" * 96)

    for task in result["tasks"]:
        status = "完成" if task["done"] else "未做"
        print(
            f"{task['row']:<5}"
            f"{status:<8}"
            f"{task['button_state']:<12}"
            f"{task['progress'] or '-':<10}"
            f"{task['title']}"
        )


def main():
    args = parse_args()
    app_config = load_app_config(args.config)

    if args.image:
        image = load_image(args.image)
        result = detect_task_page(image, app_config)

        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print_tasks(result)

        return

    runner = TaskRunner(app_config, BASE_DIR, dry_run=args.dry_run)

    try:
        result = runner.run(target_task=args.target)
    except GuardrailError as exc:
        result = {
            "status": "blocked",
            "reason": str(exc),
            "run_dir": runner.logger.path
        }
        runner.logger.event("blocked", result)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"状态: {result['status']}")
        print(f"原因: {result.get('reason', '-')}")
        print(f"日志目录: {result['run_dir']}")

    if result["status"] == "blocked":
        sys.exit(2)


if __name__ == "__main__":
    main()
