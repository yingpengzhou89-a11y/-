from task_detector import text_contains_any

def run_task(runner, observation):
    """独立包装：友情点任务的完成与退出逻辑"""
    page_text = observation.get("page_text") or ""
    
    if text_contains_any(page_text, ["每日赠送上限30/30"]):
        return {
            "intent": "友情点已赠送完成，回到主界面",
            "action": "tap",
            "target": {
                "x": 324,
                "y": 39
            },
            "confidence": 0.9,
            "risk": "low"
        }

    used_friendship_action = runner.has_decision("友情点页面执行领取赠送")

    if not used_friendship_action:
        return {
            "intent": "友情点页面执行领取赠送",
            "action": "tap",
            "target": {
                "x": 1156,
                "y": 653
            },
            "confidence": 0.82,
            "risk": "low"
        }

    returned_after_friendship = runner.has_decision("友情点动作完成后回到主界面")

    if not returned_after_friendship:
        return {
            "intent": "友情点动作完成后回到主界面",
            "action": "tap",
            "target": {
                "x": 324,
                "y": 39
            },
            "confidence": 0.9,
            "risk": "low"
        }

    return {
        "intent": "友情点页面已返回过任务页，停止避免重复操作",
        "action": "stop",
        "target": {
            "reason": "friendship page still visible after back"
        },
        "confidence": 1,
        "risk": "low"
    }
