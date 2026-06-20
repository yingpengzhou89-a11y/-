from task_detector import text_contains_any

def run_task(runner, observation):
    """独立包装：招募任务的完成与退出逻辑"""
    from task_runner import merge_recruitment_config
    
    page_text = observation.get("page_text") or ""
    recruitment_config = merge_recruitment_config(runner.app_config)

    # 1. 确认高级招募（通常在点十连后如果弹出确认框，或直接执行）
    if (
        text_contains_any(page_text, ["确认", "确定"])
        and text_contains_any(page_text, recruitment_config.get("advanced_keywords") or [])
        and not text_contains_any(page_text, runner.guardrails["forbidden_keywords"])
    ):
        return {
            "intent": "确认高级招募",
            "action": "tap",
            "target": recruitment_config["confirm_point"],
            "confidence": 0.7,
            "risk": "low"
        }

    # 2. 关闭招募结果页
    if text_contains_any(page_text, ["招募结果", "再次招募", "获得", "再抽1次", "再抽10次", "遣散", "稀有角色"]):
        return {
            "intent": "关闭招募结果页",
            "action": "tap",
            "target": recruitment_config["close_result_point"],
            "confidence": 0.78,
            "risk": "low"
        }

    # 3. 切换到高级招募
    if not runner.has_decision("切换到高级招募"):
        return {
            "intent": "切换到高级招募",
            "action": "tap",
            "target": recruitment_config["advanced_tab_point"],
            "confidence": 0.76,
            "risk": "low"
        }

    # 4. 勾选跳过招募动画
    if (
        text_contains_any(page_text, recruitment_config.get("skip_animation_keywords") or [])
        and not runner.has_decision("勾选跳过招募动画")
    ):
        return {
            "intent": "勾选跳过招募动画",
            "action": "tap",
            "target": recruitment_config["skip_animation_point"],
            "confidence": 0.72,
            "risk": "low"
        }

    # 5. 执行一次高级招募十连，完成后退出
    has_done_ten = runner.has_decision("执行高级招募十连")

    if not has_done_ten:
        return {
            "intent": "执行高级招募十连",
            "action": "tap",
            "target": recruitment_config["ten_recruit_point"],
            "confidence": 0.85,
            "risk": "low"
        }

    # 6. 已执行过十连，且关闭了结算，返回主界面以继续其它日常
    return {
        "intent": "高级招募已完成，返回主界面",
        "action": "tap",
        "target": {
            "x": 324,
            "y": 39
        },
        "confidence": 0.9,
        "risk": "low"
    }
