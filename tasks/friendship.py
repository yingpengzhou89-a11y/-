def run_task(runner, observation):
    """友情点任务：执行领取赠送，确认成功后再退出。"""
    page_text = observation.get("page_text") or ""

    normalized_text = (
        page_text
        .replace(" ", "")
        .replace("\n", "")
        .replace("\r", "")
        .replace("：", "")
        .replace(":", "")
    )

    friendship_success = (
        "领取和赠送成功" in normalized_text
        or "每日赠送上限30/30" in normalized_text
    )

    if friendship_success:
        return {
            "intent": "友情点赠送确认成功，回到主界面",
            "action": "tap",
            "target": {
                "x": 324,
                "y": 39
            },
            "confidence": 0.95,
            "risk": "low"
        }

    clicked_once = runner.has_decision("友情点首次点击领取赠送")

    if not clicked_once:
        return {
            "intent": "友情点首次点击领取赠送",
            "action": "tap",
            "target": {
                "x": 1156,
                "y": 653
            },
            "confidence": 0.88,
            "risk": "low"
        }

    waited_once = runner.has_decision("友情点首次点击后等待确认")

    if not waited_once:
        return {
            "intent": "友情点首次点击后等待确认",
            "action": "wait",
            "target": {
                "seconds": 2
            },
            "confidence": 0.95,
            "risk": "low"
        }

    retried_once = runner.has_decision("友情点重试点击领取赠送")

    if not retried_once:
        return {
            "intent": "友情点重试点击领取赠送",
            "action": "tap",
            "target": {
                "x": 1156,
                "y": 653
            },
            "confidence": 0.82,
            "risk": "low"
        }

    waited_after_retry = runner.has_decision("友情点重试后等待确认")

    if not waited_after_retry:
        return {
            "intent": "友情点重试后等待确认",
            "action": "wait",
            "target": {
                "seconds": 2
            },
            "confidence": 0.95,
            "risk": "low"
        }

    return {
        "intent": "友情点领取结果未确认，停止避免往返死循环",
        "action": "stop",
        "target": {
            "reason": "friendship action result not confirmed after retry"
        },
        "confidence": 1.0,
        "risk": "low"
    }
