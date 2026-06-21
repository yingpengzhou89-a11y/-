from task_detector import text_contains_any

def run_task(runner, observation):
    """独立包装：资源仓库快速采集3次日常任务的控制与退出逻辑"""
    from task_runner import merge_warehouse_config
    
    page_text = observation.get("page_text") or ""
    warehouse_config = merge_warehouse_config(runner.app_config)

    # 1. 动作计数限制，达到设定次数就关闭弹窗退出
    collect_actions = runner.decision_count(intent_contains="执行快速采集")
    max_actions = int(warehouse_config.get("max_collect_actions", 3))

    if collect_actions >= max_actions:
        return {
            "intent": "快速采集次数已达上限，关闭资源仓库弹窗",
            "action": "tap",
            "target": warehouse_config["close_point"],
            "confidence": 0.9,
            "risk": "low"
        }

    # 2. 直接进行快速采集点击，不做任何钻石拦截
    return {
        "intent": f"执行快速采集第{collect_actions + 1}次",
        "action": "tap",
        "target": warehouse_config["collect_point"],
        "confidence": 0.85,
        "risk": "low"
    }
