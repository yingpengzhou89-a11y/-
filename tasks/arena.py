import numpy as np
from task_detector import text_contains_any

def run_task(runner, observation):
    """独立包装：竞技场挑战各阶段控制与退出逻辑"""
    from task_runner import merge_arena_config, arena_today_count
    
    page_text = observation.get("page_text") or ""
    arena_config = merge_arena_config(runner.app_config)

    # 1. 结算关闭 (高优先级)
    if text_contains_any(page_text, ["战斗胜利", "战斗失败", "点击继续", "点击任意区域", "DEFEAT", "WIN"]):
        return {
            "intent": "关闭竞技场战斗结果",
            "action": "tap",
            "target": arena_config["continue_point"],
            "confidence": 0.82,
            "risk": "low"
        }

    # 2. 未解锁跳过弹窗处理 (高优先级)
    if text_contains_any(page_text, ["进行3次战斗", "3次战斗后", "方可跳过"]):
        return {
            "intent": "关闭自动战斗未解锁提示",
            "action": "tap",
            "target": {
                "x": 640,
                "y": 650
            },
            "confidence": 0.9,
            "risk": "low"
        }

    # 3. 战斗中正常观看等待 (不点击挂起)
    if text_contains_any(page_text, arena_config.get("battle_keywords") or []):
        return {
            "intent": "等待竞技场战斗结束",
            "action": "wait",
            "target": {
                "seconds": 8
            },
            "confidence": 0.86,
            "risk": "low"
        }

    # 4. 勾选“自动战斗”与挑战列表逻辑
    if "/50" in page_text or text_contains_any(page_text, arena_config.get("challenge_list_keywords") or []):
        runner.arena_no_action_retry_count = 0  # 重置容错计数
        today_count = arena_today_count(page_text)

        # 如果今日次数满足 target_today_count
        target_today_count = int(arena_config.get("max_free_challenges", 5))
        if today_count is not None and today_count >= target_today_count:
            runner.arena_task_complete = True  # 标记任务已完成，退回主页时使用
            return {
                "intent": "竞技场挑战次数已满足，关闭挑战列表",
                "action": "tap",
                "target": {
                    "x": 1142,  # 挑战列表右上角关闭 X 按钮
                    "y": 82
                },
                "confidence": 0.9,
                "risk": "low"
            }

        # 之后是正常的免费挑战
        if text_contains_any(page_text, ["免费", "ť"]):
            free_challenges = runner.decision_count(action="tap", intent_contains="竞技场免费挑战", after_intent="前往执行未完成任务: 挑战竞技场")
            return {
                "intent": f"竞技场免费挑战第{free_challenges + 1}次",
                "action": "tap",
                "target": arena_config["first_free_challenge_point"],
                "confidence": 0.74,
                "risk": "low"
            }

        return {
            "intent": "竞技场没有可确认的免费挑战入口，停止等待人工确认",
            "action": "stop",
            "target": {
                "reason": "no safe arena action"
            },
            "confidence": 1,
            "risk": "low"
        }

    # 5. 竞技场资格赛主页
    if text_contains_any(page_text, arena_config.get("qualifier_home_keywords") or []):
        runner.arena_no_action_retry_count = 0
        if runner.arena_task_complete:
            return {
                "intent": "竞技场挑战完成后回主界面",
                "action": "tap",
                "target": arena_config["home_point"],
                "confidence": 0.82,
                "risk": "low"
            }
        return {
            "intent": "打开竞技场挑战列表",
            "action": "tap",
            "target": arena_config["challenge_button_point"],
            "confidence": 0.8,
            "risk": "low"
        }

    # 6. 布阵出战页
    if text_contains_any(page_text, arena_config.get("formation_keywords") or []):
        runner.arena_no_action_retry_count = 0
        return {
            "intent": "确认竞技场挑战出战",
            "action": "tap",
            "target": arena_config["formation_challenge_point"],
            "confidence": 0.78,
            "risk": "low"
        }


    # 8. 容错重试机制
    if runner.arena_no_action_retry_count < 3:
        runner.arena_no_action_retry_count += 1
        return {
            "intent": "竞技场页面识别不完整，等待重试",
            "action": "wait",
            "target": {
                "seconds": 2
            },
            "confidence": 0.65,
            "risk": "low"
        }

    return None
