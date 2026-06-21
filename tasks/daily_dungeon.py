def run_task(runner, observation):
    """独立包装：参与2次日常副本日常任务的控制与退出逻辑"""
    from task_runner import merge_daily_dungeon_config
    from task_detector import text_contains_any
    
    page_type = runner.classify_current_page(observation)
    dungeon_config = merge_daily_dungeon_config(runner.app_config)
    page_text = observation.get("page_text") or ""

    # 1. 扫荡奖励领取结算弹窗处理
    if page_type == "daily_dungeon_settlement":
        return {
            "intent": "日常副本扫荡结算弹窗关闭",
            "action": "tap",
            "target": dungeon_config["close_point"],
            "confidence": 0.9,
            "risk": "low"
        }

    # 2. 扫荡动作计数限制
    sweep_actions = runner.decision_count(action="tap", intent_contains="日常副本执行扫荡", after_intent="前往执行未完成任务: 参与2次日常副本")
    max_sweep_actions = int(dungeon_config.get("max_sweep_actions", 2))

    if sweep_actions >= max_sweep_actions:
        return {
            "intent": "日常副本扫荡动作已满足限制，点击小房子返回主界面",
            "action": "tap",
            "target": dungeon_config["back_point"],
            "confidence": 0.9,
            "risk": "low"
        }

    # 3. 执行扫荡
    target_point = dungeon_config.get("sweep_point")
    # 如果页面检测不到“一键扫荡”按钮，说明未解锁，使用单次扫荡坐标
    if not text_contains_any(page_text, ["一键扫荡"]):
        target_point = dungeon_config.get("single_sweep_point") or {"x": 858, "y": 666}

    return {
        "intent": f"日常副本执行扫荡第{sweep_actions + 1}次",
        "action": "tap",
        "target": target_point,
        "confidence": 0.85,
        "risk": "low"
    }
