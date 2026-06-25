import time
import re
from task_detector import text_contains_any

def run_task(runner, observation):
    """
    巅峰赛（排位赛）日常任务的完成与退出逻辑
    - 阶段流转完全由显式状态机 runner.task_state["peak_arena"] 控制
    """
    page_type = runner.classify_current_page(observation)
    page_text = observation.get("page_text") or ""

    # 1. 任务状态初始化
    if "peak_arena" not in runner.task_state:
        runner.task_state["peak_arena"] = {
            "stage": "idle",
            "tickets_bought": False,
            "buy_count": 0,
            "buy_clicks": 0,
            "challenge_count": 0,
            "skip_clicks_in_battle": 0,
            "claim_idx": 0,
            "completed": False,
            "unknown_page_count": 0
        }

    state = runner.task_state["peak_arena"]

    # 1.1 重置未知页面计数
    if page_type in ["arena_main", "peak_arena_home", "peak_arena_rank", "peak_arena_buy", "peak_arena_formation", "peak_arena_battle", "peak_arena_settlement"]:
        state["unknown_page_count"] = 0

    # 2. 状态机逻辑流转
    
    # 2.1 竞技大厅界面 (arena_main)
    if page_type == "arena_main":
        # 点击右边“巅峰竞技场” (1030, 330)
        return {
            "intent": "巅峰赛: 在竞技大厅点击巅峰竞技场",
            "action": "tap",
            "target": {"x": 1030, "y": 330},
            "confidence": 0.9,
            "risk": "low"
        }

    # 2.2 巅峰竞技场选择主页 (peak_arena_home)
    if page_type == "peak_arena_home":
        # 点击左边“排位赛” (300, 300)
        return {
            "intent": "巅峰赛: 选择排位赛",
            "action": "tap",
            "target": {"x": 300, "y": 300},
            "confidence": 0.9,
            "risk": "low"
        }

    # 2.3 巅峰赛排位主页 (peak_arena_rank)
    if page_type == "peak_arena_rank":
        state["skip_clicks_in_battle"] = 0  # 每次回到排位主页，重置战斗跳过点击次数
        # 2.3.1 若已标记完成，点击小房子 (324, 40) 返回主城
        if state["completed"]:
            runner.arena_task_complete = True
            return {
                "intent": "巅峰赛: 任务已完成，点击小房子返回主城",
                "action": "tap",
                "target": {"x": 324, "y": 40},
                "confidence": 0.95,
                "risk": "low"
            }

        # 2.3.2 识别当前票数
        current_tickets = None
        match = re.search(r'匹配次数\D*(\d+)', page_text)
        if match:
            try:
                current_tickets = int(match.group(1))
            except ValueError:
                pass

        # 若提取失败，提供安全缺省或等待
        if current_tickets is None:
            return {
                "intent": "巅峰赛: 未能识别到当前匹配次数，等待重试",
                "action": "wait",
                "target": {"seconds": 2.0},
                "confidence": 0.8,
                "risk": "low"
            }

        # 2.3.3 判断是否买票
        if not state["tickets_bought"]:
            if current_tickets < 7:
                buy_count = 7 - current_tickets
                state["buy_count"] = buy_count
                state["buy_clicks"] = 0
                state["stage"] = "buying_tickets"
                # 点击次数右边的加号 (705, 658) 弹出购买次数界面
                return {
                    "intent": f"巅峰赛: 当前票数 {current_tickets}/6，点击加号准备购买 {buy_count} 次门票",
                    "action": "tap",
                    "target": {"x": 705, "y": 658},
                    "confidence": 0.9,
                    "risk": "low"
                }
            else:
                state["tickets_bought"] = True

        # 2.3.4 若买票完成且还有余票，开始匹配
        if current_tickets > 0:
            # 点击下方黄色按钮“开始匹配” (634, 613)
            return {
                "intent": f"巅峰赛: 当前票数 {current_tickets}，点击开始匹配",
                "action": "tap",
                "target": {"x": 634, "y": 613},
                "confidence": 0.9,
                "risk": "low"
            }
        else:
            # 2.3.5 若票数为 0 且买票已完成，说明 7 次挑战打完，去领奖
            state["stage"] = "claiming"
            # 点击右方“每日任务”按钮 (1217, 481)
            return {
                "intent": "巅峰赛: 门票已全部用尽，点击进入每日任务领奖",
                "action": "tap",
                "target": {"x": 1217, "y": 481},
                "confidence": 0.9,
                "risk": "low"
            }

    # 2.4 购买次数弹窗界面 (peak_arena_buy)
    if page_type == "peak_arena_buy":
        buy_count = state.get("buy_count", 0)
        if buy_count <= 0:
            # 安全兜底，如果没记录买几次，点取消 (525, 495) 退出
            return {
                "intent": "巅峰赛: 购买次数异常，点击取消关闭弹窗",
                "action": "tap",
                "target": {"x": 525, "y": 495},
                "confidence": 0.9,
                "risk": "low"
            }

        # 默认次数为 1。需要点右侧加号 (800, 313) 共 buy_count - 1 次
        target_clicks = buy_count - 1
        current_clicks = state.get("buy_clicks", 0)

        if current_clicks < target_clicks:
            state["buy_clicks"] = current_clicks + 1
            return {
                "intent": f"巅峰赛: 门票购买第 {current_clicks + 1} 次点击右侧加号增加数量",
                "action": "tap",
                "target": {"x": 800, "y": 313},
                "confidence": 0.9,
                "risk": "low"
            }
        else:
            # 数量加够了，点击黄色“确认”按钮 (755, 495) 购买
            state["tickets_bought"] = True
            return {
                "intent": f"巅峰赛: 门票数量已增加至 {buy_count}，点击确认购买",
                "action": "tap",
                "target": {"x": 755, "y": 495},
                "confidence": 0.95,
                "risk": "low"
            }

    # 2.5 匹配成功后的布阵出战页 (peak_arena_formation)
    if page_type in ["peak_arena_formation", "arena_formation"]:
        state["skip_clicks_in_battle"] = 0  # 每次匹配成功进入布阵，重置战斗跳过点击次数
        # 点击右下角“挑战” (1175, 641)
        return {
            "intent": "巅峰赛: 匹配成功进入布阵，点击挑战开始战斗",
            "action": "tap",
            "target": {"x": 1175, "y": 641},
            "confidence": 0.9,
            "risk": "low"
        }

    # 2.6 战斗中 (peak_arena_battle)
    if page_type in ["peak_arena_battle", "arena_battle"]:
        clicks = state.get("skip_clicks_in_battle", 0)
        last_skip = state.get("last_skip_time", 0)
        elapsed = time.time() - last_skip
        
        # 每次跳过指令后配置 4.5 秒的安全缓冲等待
        if elapsed < 4.5:
            return {
                "intent": f"巅峰赛: 距离上一次跳过仅 {elapsed:.1f} 秒，安全缓冲等待中",
                "action": "wait",
                "target": {"seconds": 2.0},
                "confidence": 0.9,
                "risk": "low"
            }
            
        if clicks < 5:
            state["skip_clicks_in_battle"] = clicks + 1
            state["last_skip_time"] = time.time()
            return {
                "intent": f"巅峰赛: 战斗中第 {clicks + 1} 次尝试点击跳过战斗",
                "action": "tap",
                "target": {"x": 337, "y": 40},
                "confidence": 0.85,
                "risk": "low"
            }
        else:
            return {
                "intent": "巅峰赛: 跳过点击次数已达上限，原地等待 3.0 秒",
                "action": "wait",
                "target": {"seconds": 3.0},
                "confidence": 0.9,
                "risk": "low"
            }

    # 2.7 战斗结算页 (peak_arena_settlement / arena_settlement)
    if page_type in ["peak_arena_settlement", "arena_settlement"]:
        state["skip_clicks_in_battle"] = 0
        
        # 2.7.1 若结算页还没有真正的“返回”按钮（例如全屏普通战斗胜利/失败弹窗，需点击任意区域）
        if not text_contains_any(page_text, ["返回"]):
            return {
                "intent": "巅峰赛: 战斗结束，点击屏幕任意区域关闭结果",
                "action": "tap",
                "target": {"x": 640, "y": 650},
                "confidence": 0.9,
                "risk": "low"
            }
        
        # 2.7.2 带有“返回”按钮的 MVP 或排位结算页
        state["challenge_count"] = state.get("challenge_count", 0) + 1
        # 点击“返回” (1013, 650)
        return {
            "intent": f"巅峰赛: 第 {state['challenge_count']} 次挑战结算，点击返回",
            "action": "tap",
            "target": {"x": 1013, "y": 650},
            "confidence": 0.9,
            "risk": "low"
        }

    # 2.8 每日任务领奖阶段处理
    if state["stage"] == "claiming":
        claim_idx = int(state.get("claim_idx", 0))

        # 已领取任务会自动沉底，后续可领奖任务会依次顶到第一行。
        # 固定点击第一行领取按钮即可领取全部四项奖励。
        if claim_idx < 4:
            state["claim_idx"] = claim_idx + 1
            return {
                "intent": f"巅峰赛: 固定坐标领取第 {claim_idx + 1}/4 个每日任务奖励",
                "action": "tap",
                "target": {"x": 1041, "y": 186},
                "confidence": 0.95,
                "risk": "low"
            }

        # 四次固定领奖完成后，点击右上角大红叉退出。
        state["completed"] = True
        return {
            "intent": "巅峰赛: 四个每日任务奖励已依次领取，点击右上角大红叉返回排位主页",
            "action": "tap",
            "target": {"x": 1134, "y": 92},
            "confidence": 0.9,
            "risk": "low"
        }

    # 3. 未知过渡页防失控保护
    if page_type == "unknown":
        state["unknown_page_count"] = state.get("unknown_page_count", 0) + 1
        if state["unknown_page_count"] <= 3:
            return {
                "intent": f"巅峰赛: 处于未知过渡界面（第 {state['unknown_page_count']} 次），原地等待 1.5 秒",
                "action": "wait",
                "target": {"seconds": 1.5},
                "confidence": 0.9,
                "risk": "low"
            }

    return None
