def run_task(runner, observation):
    """独立包装：挑战回忆之屋1次日常任务的控制与退出逻辑"""
    from task_runner import merge_memory_house_config
    
    page_type = runner.classify_current_page(observation)
    memory_config = merge_memory_house_config(runner.app_config)

    # 1. 扫荡奖励领取结算弹窗处理
    if page_type == "memory_house_sweep_settlement":
        return {
            "intent": "回忆之屋扫荡奖励弹窗关闭",
            "action": "tap",
            "target": memory_config["sweep_point"],
            "confidence": 0.9,
            "risk": "low"
        }

    # 2. 扫荡动作计数限制
    sweep_actions = runner.decision_count(intent_contains="回忆之屋执行扫荡")
    max_sweep_actions = int(memory_config.get("max_sweep_actions", 1))

    if sweep_actions >= max_sweep_actions:
        return {
            "intent": "回忆之屋扫荡动作已满足限制，点击小房子返回主界面",
            "action": "tap",
            "target": memory_config["back_point"],
            "confidence": 0.9,
            "risk": "low"
        }

    # 3. 正常扫荡点击
    return {
        "intent": f"回忆之屋执行扫荡第{sweep_actions + 1}次",
        "action": "tap",
        "target": memory_config["sweep_point"],
        "confidence": 0.85,
        "risk": "low"
    }
