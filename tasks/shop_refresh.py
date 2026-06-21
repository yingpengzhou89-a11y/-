def run_task(runner, observation):
    """独立包装：日常商店刷新2次日常任务的控制与退出逻辑"""
    from task_runner import merge_shop_refresh_config
    
    page_type = runner.classify_current_page(observation)
    shop_config = merge_shop_refresh_config(runner.app_config)

    # 1. 弹出快速购买的结算页处理
    if page_type == "shop_buy_settlement":
        return {
            "intent": "日常商店购买弹窗点击关闭",
            "action": "tap",
            "target": shop_config["refresh_point"],
            "confidence": 0.9,
            "risk": "low"
        }

    # 2. 刷新动作计数限制
    refresh_actions = runner.decision_count(action="tap", intent_contains="日常商店执行刷新", after_intent="前往执行未完成任务: 日常商店刷新")
    max_refresh_actions = int(shop_config.get("max_refresh_actions", 2))

    if refresh_actions >= max_refresh_actions:
        return {
            "intent": "日常商店刷新动作已满足限制，点击小房子返回主界面",
            "action": "tap",
            "target": shop_config["back_point"],
            "confidence": 0.9,
            "risk": "low"
        }

    # 3. 正常刷新点击
    return {
        "intent": f"日常商店执行刷新第{refresh_actions + 1}次",
        "action": "tap",
        "target": shop_config["refresh_point"],
        "confidence": 0.85,
        "risk": "low"
    }
