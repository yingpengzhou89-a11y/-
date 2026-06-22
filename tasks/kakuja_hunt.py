import time
from task_detector import text_contains_any

def run_task(runner, observation):
    """独立包装：赫者讨伐任务的显式状态机与防失控保护"""
    page_type = runner.classify_current_page(observation)
    from task_runner import merge_kakuja_hunt_config
    config = merge_kakuja_hunt_config(runner.app_config)

    # 1. 任务级别状态机显式初始化
    if "kakuja_hunt" not in runner.task_state:
        runner.task_state["kakuja_hunt"] = {
            "stage": "idle",
            "main_challenge_attempts": 0,
            "challenge_click_pending": False,
            "challenge_click_time": None,
            "formation_boss_attempts": 0,
            "boss_click_pending": False,
            "boss_click_time": None,
            "skip_attempts": 0,
            "battle_result_seen": False,
            "victory_confirm_attempts": 0,
            "victory_confirmed": False,
            "completed": False
        }

    state = runner.task_state["kakuja_hunt"]

    # 2. 过渡加载动画处理
    if page_type == "kakuja_hunt_loading":
        state["challenge_click_pending"] = False
        state["boss_click_pending"] = False
        state["stage"] = "loading"
        return {
            "intent": "赫者讨伐进入加载过渡，等待2秒",
            "action": "wait",
            "target": {"seconds": 2},
            "confidence": 0.9,
            "risk": "low"
        }

    # 3. 战斗胜利结算页处理
    if page_type == "kakuja_hunt_victory":
        state["battle_result_seen"] = True
        state["stage"] = "result"
        
        max_confirm_attempts = int(config.get("max_victory_confirm_attempts", 3))
        if state["victory_confirm_attempts"] >= max_confirm_attempts:
            return {
                "intent": "赫者讨伐结算页多次点击确定未果，尝试点房子退出",
                "action": "tap",
                "target": config["back_point"],
                "confidence": 0.9,
                "risk": "low"
            }
            
        state["victory_confirm_attempts"] += 1
        return {
            "intent": f"赫者讨伐胜利结算第{state['victory_confirm_attempts']}次点击确定",
            "action": "tap",
            "target": config["confirm_point"],
            "confidence": 0.9,
            "risk": "low"
        }

    # 4. 战斗进行中，点击跳过
    if page_type == "kakuja_hunt_battle":
        state["boss_click_pending"] = False
        state["stage"] = "battle"
        
        max_skip_attempts = int(config.get("max_skip_attempts", 2))
        if state["skip_attempts"] < max_skip_attempts:
            state["skip_attempts"] += 1
            return {
                "intent": f"赫者讨伐战斗中第{state['skip_attempts']}次尝试点击跳过",
                "action": "tap",
                "target": config["skip_point"],
                "confidence": 0.85,
                "risk": "low"
            }
            
        return {
            "intent": "赫者讨伐跳过已达到尝试上限，等待战斗完成",
            "action": "wait",
            "target": {"seconds": 3},
            "confidence": 0.9,
            "risk": "low"
        }

    # 5. 布阵挑战界面，点击“BOSS战”
    if page_type == "kakuja_hunt_formation":
        state["challenge_click_pending"] = False
        state["stage"] = "formation"
        
        # 如果已经点击了BOSS战，且仍在布阵页面，先等待跳转
        if state["boss_click_pending"]:
            elapsed = time.time() - (state["boss_click_time"] or 0)
            if elapsed < 3.0:
                return {
                    "intent": "赫者讨伐已点击BOSS战，等待进入战斗",
                    "action": "wait",
                    "target": {"seconds": 1.5},
                    "confidence": 0.9,
                    "risk": "low"
                }
            # 超时未跳转，释放 pending 允许重试
            state["boss_click_pending"] = False
            
        max_boss_attempts = int(config.get("max_formation_boss_attempts", 2))
        if state["formation_boss_attempts"] >= max_boss_attempts:
            return {
                "intent": "赫者讨伐布阵BOSS战多次尝试未果，安全返回大厅",
                "action": "tap",
                "target": config["back_point"],
                "confidence": 0.9,
                "risk": "low"
            }
            
        state["formation_boss_attempts"] += 1
        state["boss_click_pending"] = True
        state["boss_click_time"] = time.time()
        
        return {
            "intent": f"赫者讨伐布阵界面第{state['formation_boss_attempts']}次尝试点击BOSS战",
            "action": "tap",
            "target": config["challenge_point"],
            "confidence": 0.85,
            "risk": "low"
        }

    # 6. 赫者讨伐主界面
    if page_type == "kakuja_hunt_main":
        # 6.1 如果之前已经看到过结算（或者打完了），说明挑战已完成，安全退出
        if state["battle_result_seen"]:
            state["victory_confirmed"] = True
            state["completed"] = True
            state["stage"] = "completed"
            return {
                "intent": "赫者讨伐已确认完成，点击小房子返回主界面",
                "action": "tap",
                "target": config["back_point"],
                "confidence": 0.95,
                "risk": "low"
            }
            
        # 6.2 如果刚刚点击了挑战，且页面还没来得及跳转，先等待跳转
        if state["challenge_click_pending"]:
            elapsed = time.time() - (state["challenge_click_time"] or 0)
            if elapsed < 3.0:
                return {
                    "intent": "赫者讨伐已点击挑战，等待进入布阵界面",
                    "action": "wait",
                    "target": {"seconds": 1.5},
                    "confidence": 0.9,
                    "risk": "low"
                }
            # 超过3秒还在主页面，说明上一次点击可能由于各种原因失败，释放 pending 允许重试
            state["challenge_click_pending"] = False

        # 6.3 判断重试次数限制（作为防卡死安全锁）
        max_attempts = int(config.get("max_main_challenge_attempts", 2))
        if state["main_challenge_attempts"] >= max_attempts:
            return {
                "intent": f"赫者讨伐挑战入口已达到最大尝试次数{max_attempts}次，安全退出",
                "action": "tap",
                "target": config["back_point"],
                "confidence": 0.9,
                "risk": "low"
            }

        state["main_challenge_attempts"] += 1
        state["challenge_click_pending"] = True
        state["challenge_click_time"] = time.time()
        state["stage"] = "challenge_requested"

        return {
            "intent": f"赫者讨伐主界面第{state['main_challenge_attempts']}次尝试点击挑战",
            "action": "tap",
            "target": config["challenge_point"],
            "confidence": 0.85,
            "risk": "low"
        }

    return None
