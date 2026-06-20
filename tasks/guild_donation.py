def run_task(runner, observation):
    """独立包装：进行1次组织捐献日常任务的控制与退出逻辑"""
    from task_runner import merge_guild_donation_config
    
    page_type = runner.classify_current_page(observation)
    donation_config = merge_guild_donation_config(runner.app_config)

    if page_type == "guild_donation_select":
        used_gold_donation = runner.has_decision("组织捐献页面点击金币捐献")
        if not used_gold_donation:
            return {
                "intent": "组织捐献页面点击金币捐献",
                "action": "tap",
                "target": donation_config["gold_donation_point"],
                "confidence": 0.85,
                "risk": "low"
            }
        else:
            return {
                "intent": "组织捐献完成，关闭选择弹窗",
                "action": "tap",
                "target": donation_config["close_point"],
                "confidence": 0.85,
                "risk": "low"
            }

    elif page_type == "guild_main":
        # 检查我们是否已经执行过金币捐献
        done_donation = runner.has_decision("组织捐献页面点击金币捐献")
        if not done_donation:
            return {
                "intent": "组织页面点击组织捐献入口",
                "action": "tap",
                "target": donation_config["donation_entry_point"],
                "confidence": 0.85,
                "risk": "low"
            }
        else:
            return {
                "intent": "组织捐献任务结束，返回主界面",
                "action": "tap",
                "target": donation_config["back_point"],
                "confidence": 0.85,
                "risk": "low"
            }
    return None
