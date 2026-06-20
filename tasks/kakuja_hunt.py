def run_task(runner, observation):
    """独立包装：赫者讨伐1次日常任务的控制与退出逻辑"""
    from task_runner import merge_kakuja_hunt_config
    
    page_type = runner.classify_current_page(observation)
    config = merge_kakuja_hunt_config(runner.app_config)

    # 1. 战斗胜利结算页处理
    if page_type == "kakuja_hunt_victory":
        return {
            "intent": "赫者讨伐胜利结算点击确定",
            "action": "tap",
            "target": config["confirm_point"],
            "confidence": 0.9,
            "risk": "low"
        }

    # 2. 战斗进行中，点击跳过
    if page_type == "kakuja_hunt_battle":
        if runner.has_decision("赫者讨伐战斗中点击跳过"):
            return {
                "intent": "赫者讨伐已点击跳过，等待战斗完成",
                "action": "wait",
                "target": {"seconds": 3},
                "confidence": 0.9,
                "risk": "low"
            }
        return {
            "intent": "赫者讨伐战斗中点击跳过",
            "action": "tap",
            "target": config["skip_point"],
            "confidence": 0.85,
            "risk": "low"
        }

    # 3. 布阵挑战界面，点击“BOSS战”
    if page_type == "kakuja_hunt_formation":
        return {
            "intent": "赫者讨伐布阵界面点击BOSS战",
            "action": "tap",
            "target": config["challenge_point"],
            "confidence": 0.85,
            "risk": "low"
        }

    # 4. 赫者讨伐主界面
    if page_type == "kakuja_hunt_main":
        # 检查是否完成了挑战（点击过确定即认为讨伐成功）
        if runner.has_decision("赫者讨伐胜利结算点击确定"):
            return {
                "intent": "赫者讨伐挑战已完成，点击小房子返回主界面",
                "action": "tap",
                "target": config["back_point"],
                "confidence": 0.9,
                "risk": "low"
            }
        
        actions = runner.decision_count(intent_contains="赫者讨伐主界面点击挑战")
        if actions >= int(config.get("max_actions", 1)):
            return {
                "intent": "赫者讨伐动作已满足限制，点击小房子返回主界面",
                "action": "tap",
                "target": config["back_point"],
                "confidence": 0.9,
                "risk": "low"
            }

        return {
            "intent": "赫者讨伐主界面点击挑战",
            "action": "tap",
            "target": config["challenge_point"],
            "confidence": 0.85,
            "risk": "low"
        }
    return None
