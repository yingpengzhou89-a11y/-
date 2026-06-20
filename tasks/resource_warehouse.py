from task_detector import text_contains_any

def run_task(runner, observation):
    """独立包装：资源仓库快速采集3次日常任务的控制与退出逻辑"""
    from task_runner import merge_warehouse_config
    
    page_text = observation.get("page_text") or ""
    warehouse_config = merge_warehouse_config(runner.app_config)

    # 2. 消耗钻石确认弹窗
    if text_contains_any(page_text, ["确认", "确定"]) and text_contains_any(page_text, ["消耗", "钻石", "钻"]):
        # 80钻石绝对红线拦截
        if "80" in page_text:
            return {
                "intent": "达到80钻石消耗上限，拒绝快速采集并关闭弹窗",
                "action": "tap",
                "target": warehouse_config["close_point"],
                "confidence": 0.95,
                "risk": "low"
            }
        # 否则（20钻石或50钻石等安全范围），点击确定进行采集
        return {
            "intent": "确认消耗钻石进行快速采集",
            "action": "tap",
            "target": {
                "x": 760,
                "y": 515
            },
            "confidence": 0.85,
            "risk": "low"
        }

    # 3. 动作计数限制
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

    # 4. 正常采集点击前检查（80 钻石绝对红线拦截）
    if "80" in page_text:
        return {
            "intent": "达到80钻石消耗上限，拒绝快速采集并关闭弹窗",
            "action": "tap",
            "target": warehouse_config["close_point"],
            "confidence": 0.95,
            "risk": "low"
        }

    return {
        "intent": f"执行快速采集第{collect_actions + 1}次",
        "action": "tap",
        "target": warehouse_config["collect_point"],
        "confidence": 0.85,
        "risk": "low"
    }
