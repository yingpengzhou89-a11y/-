import hashlib
import json
import os
import time
from datetime import datetime

import cv2
import numpy as np

from actions import adb_swipe, adb_tap, wait_after_tap
from adb_client import capture_screenshot

from task_detector import detect_task_page, merge_task_config, text_contains_any


DEFAULT_GUARDRAILS = {
    "max_steps_per_task": 200,
    "max_run_seconds": 3600,
    "min_confidence": 0.65,
    "max_unchanged_screens": 3,
    "max_target_search_scrolls": 6,
    "screen_hash_size": 32,
    "forbidden_keywords": [
        "充值",
        "购买",
        "钻石",
        "付费",
        "商城",
        "确认购买"
    ],
    "allowed_actions": [
        "tap",
        "wait",
        "swipe",
        "claim",
        "stop"
    ]
}


def merge_guardrails(app_config):
    guardrails = dict(DEFAULT_GUARDRAILS)
    guardrails.update(app_config.get("guardrails") or {})
    return guardrails


DEFAULT_RECRUITMENT_CONFIG = {
    "page_keywords": ["高级招募", "普通招募", "特定招募", "跳过动画", "招募十次"],
    "advanced_keywords": ["高级招募"],
    "advanced_tab_point": {"x": 168, "y": 386},
    "skip_animation_keywords": ["跳过动画"],
    "skip_animation_point": {"x": 1020, "y": 642},
    "free_single_keywords": ["免费"],
    "free_single_point": {"x": 512, "y": 654},
    "ten_recruit_keywords": ["招募十次", "十连", "10次"],
    "ten_recruit_point": {"x": 800, "y": 650},
    "close_result_point": {"x": 513, "y": 634},
    "max_recruit_actions": 2
}


DEFAULT_ARENA_CONFIG = {
    "main_keywords": ["本服竞技场", "跨服竞技场", "巅峰竞技场"],
    "local_keywords": ["资格赛", "排位赛"],
    "challenge_list_keywords": ["挑战列表", "今日次数", "自动战斗"],
    "formation_keywords": ["VS", "一键布阵", "助战"],
    "battle_keywords": ["挂起", "暂停"],
    "qualifier_home_keywords": ["竞技场赛季奖励", "挑战积分", "今日免费", "防守阵容"],
    "challenge_button_point": {"x": 1185, "y": 642},
    "formation_challenge_point": {"x": 1185, "y": 642},
    "close_challenge_list_point": {"x": 1142, "y": 82},
    "home_point": {"x": 324, "y": 39},
    "first_free_challenge_point": {"x": 995, "y": 233},
    "continue_point": {"x": 640, "y": 650},
    "max_free_challenges": 5
}


DEFAULT_WAREHOUSE_CONFIG = {
    "page_keywords": ["资源仓库"],
    "sub_keywords": ["快速采集", "当前存储", "存储时间", "奖励预览", "免费次数"],
    "collect_point": {"x": 700, "y": 575},
    "close_point": {"x": 1106, "y": 137},
    "max_collect_actions": 3
}


DEFAULT_GUILD_DONATION_CONFIG = {
    "donation_entry_point": {"x": 382, "y": 623},
    "gold_donation_point": {"x": 587, "y": 595},
    "close_point": {"x": 1217, "y": 82},
    "back_point": {"x": 324, "y": 39}
}


def merge_guild_donation_config(app_config):
    config = dict(DEFAULT_GUILD_DONATION_CONFIG)
    config.update(app_config.get("guild_donation") or {})
    return config


DEFAULT_SHOP_REFRESH_CONFIG = {
    "page_keywords": ["日常商店", "道具商店", "集结商店", "自动购买"],
    "refresh_point": {"x": 380, "y": 597},
    "back_point": {"x": 324, "y": 39},
    "max_refresh_actions": 2
}


def merge_shop_refresh_config(app_config):
    config = dict(DEFAULT_SHOP_REFRESH_CONFIG)
    config.update(app_config.get("shop_refresh") or {})
    return config


DEFAULT_MEMORY_HOUSE_CONFIG = {
    "page_keywords": ["回忆之屋", "扫荡", "补星", "通关信息", "回忆限购"],
    "sweep_point": {"x": 1093, "y": 677},
    "back_point": {"x": 324, "y": 39},
    "max_sweep_actions": 1
}


def merge_memory_house_config(app_config):
    config = dict(DEFAULT_MEMORY_HOUSE_CONFIG)
    config.update(app_config.get("memory_house") or {})
    return config


DEFAULT_DAILY_DUNGEON_CONFIG = {
    "page_keywords": ["日常副本", "经验副本", "金币副本", "碎片副本", "装备副本", "刻印副本"],
    "sweep_point": {"x": 745, "y": 666},
    "single_sweep_point": {"x": 858, "y": 666},
    "close_point": {"x": 400, "y": 250},
    "back_point": {"x": 324, "y": 39},
    "max_sweep_actions": 2
}


def merge_daily_dungeon_config(app_config):
    config = dict(DEFAULT_DAILY_DUNGEON_CONFIG)
    config.update(app_config.get("daily_dungeon") or {})
    return config


DEFAULT_KAKUJA_HUNT_CONFIG = {
    "page_keywords": ["赫者讨伐", "排行", "挑战", "剩余"],
    "challenge_point": {"x": 1175, "y": 640},
    "skip_point": {"x": 336, "y": 40},
    "confirm_point": {"x": 965, "y": 650},
    "back_point": {"x": 324, "y": 39},
    "max_main_challenge_attempts": 2,
    "max_formation_boss_attempts": 2,
    "max_skip_attempts": 2,
    "max_victory_confirm_attempts": 3
}


def merge_kakuja_hunt_config(app_config):
    config = dict(DEFAULT_KAKUJA_HUNT_CONFIG)
    config.update(app_config.get("kakuja_hunt") or {})
    return config


def merge_recruitment_config(app_config):
    config = dict(DEFAULT_RECRUITMENT_CONFIG)
    config.update(app_config.get("recruitment") or {})
    return config


def merge_arena_config(app_config):
    config = dict(DEFAULT_ARENA_CONFIG)
    config.update(app_config.get("arena") or {})
    return config


def merge_warehouse_config(app_config):
    config = dict(DEFAULT_WAREHOUSE_CONFIG)
    config.update(app_config.get("warehouse") or {})
    return config


def arena_today_count(page_text):
    compact = page_text.replace(" ", "").replace("：", ":")
    marker = "今日次数:"
    index = compact.find(marker)

    if index < 0:
        return None

    cursor = index + len(marker)
    digits = []

    while cursor < len(compact) and compact[cursor].isdigit():
        digits.append(compact[cursor])
        cursor += 1

    if not digits:
        return None

    return int("".join(digits))


def now_run_id():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


class RunLogger:
    def __init__(self, base_dir, run_id=None):
        self.run_id = run_id or now_run_id()
        self.path = os.path.join(base_dir, "task_runs", self.run_id)
        os.makedirs(self.path, exist_ok=True)
        self.events_path = os.path.join(self.path, "events.jsonl")

    def screenshot_path(self, step):
        return os.path.join(self.path, f"step_{step:03d}.png")

    def event(self, event_type, data):
        record = {
            "time": datetime.now().isoformat(timespec="seconds"),
            "type": event_type,
            "data": data
        }

        with open(self.events_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def image_hash(image, size=32):
    small = cv2.resize(image, (size, size), interpolation=cv2.INTER_AREA)
    return hashlib.sha1(small.tobytes()).hexdigest()


class GuardrailError(RuntimeError):
    pass


class TaskRunner:
    def __init__(self, app_config, base_dir, dry_run=False):
        self.app_config = app_config
        self.guardrails = merge_guardrails(app_config)

        self.logger = RunLogger(base_dir)
        self.dry_run = dry_run
        self.history = []
        self.last_hash = None
        self.unchanged_count = 0
        self.active_task_go_clicked = False
        self.active_target_task = None
        self.daily_page_swipe_count = 0
        self.arena_last_auto_try_count = -1
        self.task_state = {}
        self.daily_page_claiming = False
        self.daily_page_up_swipe_count = 0

    def decision_count(self, action=None, intent_contains=None, after_intent=None):
        count = 0
        active = after_intent is None

        for item in self.history:
            decision = item.get("decision", {})
            intent = decision.get("intent", "")

            if after_intent and after_intent in intent:
                active = True
                count = 0
                continue

            if not active:
                continue

            if action and decision.get("action") != action:
                continue

            if intent_contains and intent_contains not in intent:
                continue

            count += 1

        return count

    def has_decision(self, intent_contains):
        return self.decision_count(intent_contains=intent_contains) > 0

    def choose_arena_decision(self, observation, target_task=None):
        if not target_task or not ("竞技" in target_task or "竞技场" in target_task):
            return None

        page_text = observation.get("page_text") or ""
        arena_config = merge_arena_config(self.app_config)

        if text_contains_any(page_text, ["战斗胜利", "战斗失败", "点击继续", "点击任意区域"]):
            return {
                "intent": "关闭竞技场战斗结果",
                "action": "tap",
                "target": arena_config["continue_point"],
                "confidence": 0.82,
                "risk": "low"
            }


        if text_contains_any(page_text, ["进行3次战斗后方可跳过"]):
            return {
                "intent": "跳过未解锁，改用免费挑战并观看战斗",
                "action": "tap",
                "target": arena_config["first_free_challenge_point"],
                "confidence": 0.72,
                "risk": "low"
            }

        if text_contains_any(page_text, arena_config.get("formation_keywords") or []):
            return {
                "intent": "确认竞技场挑战出战",
                "action": "tap",
                "target": arena_config["formation_challenge_point"],
                "confidence": 0.78,
                "risk": "low"
            }

        if text_contains_any(page_text, arena_config.get("qualifier_home_keywords") or []):
            if self.has_decision("竞技场挑战次数已满足"):
                return {
                    "intent": "竞技场挑战完成后回主界面",
                    "action": "tap",
                    "target": arena_config["home_point"],
                    "confidence": 0.78,
                    "risk": "low"
                }

            return {
                "intent": "打开竞技场挑战列表",
                "action": "tap",
                "target": arena_config["challenge_button_point"],
                "confidence": 0.8,
                "risk": "low"
            }

        if text_contains_any(page_text, arena_config.get("challenge_list_keywords") or []):
            free_challenges = self.decision_count(intent_contains="竞技场免费挑战")
            max_free_challenges = int(arena_config.get("max_free_challenges", 3))
            today_count = arena_today_count(page_text)

            if today_count is not None and today_count >= max_free_challenges:
                return {
                    "intent": "竞技场挑战次数已满足，关闭挑战列表",
                    "action": "tap",
                    "target": arena_config["close_challenge_list_point"],
                    "confidence": 0.82,
                    "risk": "low"
                }


            if free_challenges < max_free_challenges and text_contains_any(page_text, ["免费"]):
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

        if text_contains_any(page_text, arena_config.get("battle_keywords") or []):
            return {
                "intent": "竞技场战斗中等待",
                "action": "wait",
                "target": {
                    "seconds": 8
                },
                "confidence": 0.86,
                "risk": "low"
            }


        return None

    def capture(self, step):
        path = self.logger.screenshot_path(step)
        image = capture_screenshot(
            self.app_config["adb_path"],
            self.app_config["device_id"],
            path
        )
        return image, path

    def validate_decision(self, decision, observation):
        if not isinstance(decision, dict):
            decision = {"action": "stop", "intent": "invalid decision format", "confidence": 0, "risk": "high"}
        decision.setdefault("action", "stop")
        decision.setdefault("intent", "unknown")
        decision.setdefault("confidence", 1.0)
        decision.setdefault("risk", "low")
        decision["action"] = decision["action"].lower()
        action = decision["action"]

        if action not in self.guardrails["allowed_actions"]:
            raise GuardrailError(f"action not allowed: {action}")

        if decision["risk"] == "high":
            raise GuardrailError(f"high risk action blocked: {decision}")

        if action not in {"stop", "wait"} and decision["confidence"] < float(self.guardrails["min_confidence"]):
            raise GuardrailError(f"low confidence action blocked: {decision}")

        skip_forbidden_text = decision["intent"] in {
            "从 MuMu 桌面重新打开游戏",
            "关闭领奖弹窗",
            "关闭会员客服弹窗",
            "关闭资源仓库弹窗",
            "从主界面打开任务页",
            "返回主界面以寻找任务页",
            "切换到高级招募",
            "执行高级招募十连",
            "确认消耗钻石进行快速采集",
            "达到80钻石消耗上限，拒绝快速采集并关闭弹窗",
            "快速采集次数已达上限，关闭资源仓库弹窗",
            "关闭招募结果页",
            "进入本服竞技场",
            "进入本服竞技场资格赛",
            "打开竞技场挑战列表",
            "竞技场挑战次数已满足，关闭挑战列表",
            "竞技场挑战完成后回主界面",
            "确认竞技场挑战出战",
            "尝试竞技场一键战斗",
            "勾选竞技场自动战斗",
            "一键战斗未解锁，改用免费挑战",
            "跳过未解锁，改用免费挑战并观看战斗",
            "关闭竞技场战斗结果",
            "勾选挑战列表自动战斗",
            "确认竞技场快速战斗",
            "点击挂起跳过战斗",
            "关闭自动战斗未解锁提示",
            "等待竞技场战斗结束",
            "竞技场页面识别不完整，等待重试",
            "组织捐献页面点击金币捐献",
            "组织捐献完成，关闭选择弹窗",
            "组织页面点击组织捐献入口",
            "组织捐献任务结束，返回主界面",
            "日常商店购买弹窗点击关闭",
            "日常商店刷新动作已满足限制，点击小房子返回主界面",
            "回忆之屋扫荡奖励弹窗关闭",
            "回忆之屋扫荡动作已满足限制，点击小房子返回主界面",
            "日常副本扫荡结算弹窗关闭",
            "日常副本扫荡动作已满足限制，点击小房子返回主界面",
            "赫者讨伐胜利结算点击确定",
            "赫者讨伐已点击跳过，等待战斗完成",
            "赫者讨伐战斗中点击跳过",
            "赫者讨伐布阵界面点击BOSS战",
            "赫者讨伐挑战已完成，点击小房子返回主界面",
            "赫者讨伐动作已满足限制，点击小房子返回主界面"
        }

        if (
            decision["intent"].startswith("竞技场免费挑战")
            or decision["intent"].startswith("执行快速采集")
            or decision["intent"].startswith("日常商店执行刷新")
            or decision["intent"].startswith("回忆之屋执行扫荡")
            or decision["intent"].startswith("日常副本执行扫荡")
            or decision["intent"].startswith("赫者讨伐主界面点击挑战")
            or decision["intent"].startswith("领取日常活跃度宝箱")
            or "招募" in decision["intent"]
            or "巅峰赛" in decision["intent"]
            or "从主界面直接前往竞技场大厅(巅峰赛入口)" in decision["intent"]
        ):
            skip_forbidden_text = True

        if (
            not skip_forbidden_text
            and text_contains_any(observation.get("page_text") or "", self.guardrails["forbidden_keywords"])
        ):
            raise GuardrailError(f"forbidden keyword detected on screen. Decision: {decision}")

        if action in {"tap", "claim"}:
            target = decision.get("target") or {}
            x = int(target.get("x", -1))
            y = int(target.get("y", -1))
            resolution = self.app_config.get("resolution") or {"width": 1280, "height": 720}

            if not (0 <= x <= int(resolution["width"]) and 0 <= y <= int(resolution["height"])):
                raise GuardrailError(f"tap out of bounds: {x},{y}")

        if action == "swipe":
            target = decision.get("target") or {}
            resolution = self.app_config.get("resolution") or {"width": 1280, "height": 720}

            for key in ["x1", "y1", "x2", "y2"]:
                value = int(target.get(key, -1))
                limit = int(resolution["width"] if key.startswith("x") else resolution["height"])

                if not 0 <= value <= limit:
                    raise GuardrailError(f"swipe out of bounds: {key}={value}")

        return decision

    def execute_decision(self, decision):
        action = decision["action"]
        target = decision.get("target") or {}

        if self.dry_run:
            return {
                "executed": False,
                "dry_run": True
            }

        if action in {"tap", "claim"}:
            adb_tap(
                self.app_config["adb_path"],
                self.app_config["device_id"],
                target["x"],
                target["y"]
            )
            wait_after_tap(0.8)
            return {"executed": True}

        if action == "wait":
            time.sleep(float(target.get("seconds", 1)))
            return {"executed": True}

        if action == "swipe":
            adb_swipe(
                self.app_config["adb_path"],
                self.app_config["device_id"],
                target["x1"],
                target["y1"],
                target["x2"],
                target["y2"],
                target.get("duration_ms", 450)
            )
            wait_after_tap(0.8)
            return {"executed": True}

        return {"executed": False, "stopped": True}
    def has_clicked_go(self, task_name):
        """检查历史动作中是否已在任务页点击了该任务的'前往'"""
        for event in reversed(self.history):
            decision = event.get("decision", {})
            intent = decision.get("intent", "")
            if "前往执行未完成任务" in intent and task_name in intent:
                return True
            if "回到主界面" in intent or "回主界面" in intent or "目标任务已领取" in intent:
                return False
        return False

    def classify_current_page(self, observation):
        """集中式页面分类器，提供排他的页面状态匹配"""
        page_text = observation.get("page_text") or ""
        is_task_page = observation.get("is_task_page") or False

        if is_task_page:
            return "daily_tasks"

        # 0.01 赫者讨伐战斗胜利结算页 (高优先级)
        if text_contains_any(page_text, ["战斗胜利", "VICTORY"]) and text_contains_any(page_text, ["确定"]) and text_contains_any(page_text, ["总伤害"]):
            return "kakuja_hunt_victory"

        # 0.02 赫者讨伐战斗进行中 (排除竞技场战斗)
        if text_contains_any(page_text, ["造成伤害", "挂起"]) and not text_contains_any(page_text, ["今日次数", "挑战列表", "本服", "资格赛", "VS", "一键布阵"]):
            return "kakuja_hunt_battle"

        # 0.02 赫者讨伐加载动画页
        if text_contains_any(page_text, ["强敌来袭", "强活来袭"]):
            return "kakuja_hunt_loading"

        # 0.021 赫者讨伐挑战布阵页
        if text_contains_any(page_text, ["BOSS战"]) and text_contains_any(page_text, ["布阵", "VS", "一键布阵"]):
            return "kakuja_hunt_formation"

        # 0.022 赫者讨伐主界面
        kakuja_config = merge_kakuja_hunt_config(self.app_config)
        if text_contains_any(page_text, kakuja_config["page_keywords"]) and text_contains_any(page_text, ["赫者讨伐"]):
            return "kakuja_hunt_main"

        # 0.03 日常副本扫荡奖励结算弹窗 (高优先级，包含“恭喜获得”以及“日常副本/副本扫荡”)
        if text_contains_any(page_text, ["恭喜获得"]) and text_contains_any(page_text, ["日常副本", "金币副本", "经验副本", "碎片副本", "装备副本", "刻印副本"]):
            return "daily_dungeon_settlement"

        # 0.04 日常副本主界面 (包含日常副本及各子副本特征)
        dungeon_config = merge_daily_dungeon_config(self.app_config)
        if text_contains_any(page_text, dungeon_config["page_keywords"]) and text_contains_any(page_text, ["日常副本"]):
            return "daily_dungeon_main"

        # 0.05 回忆之屋扫荡奖励弹窗 (高优先级，包含“恭喜获得”以及“扫荡”或背景中的“回忆之屋”)
        if text_contains_any(page_text, ["恭喜获得"]) and text_contains_any(page_text, ["扫荡", "回忆之屋", "回忆限购"]):
            return "memory_house_sweep_settlement"

        # 0.06 回忆之屋主界面 (包含回忆之屋等排他特征)
        memory_config = merge_memory_house_config(self.app_config)
        if text_contains_any(page_text, memory_config["page_keywords"]) and text_contains_any(page_text, ["回忆之屋"]):
            return "memory_house_main"

        # 0.1 日常商店刷新弹窗 (高优先级，包含“恭喜获得”以及“快速购买/购买消耗/自动购买”)
        if text_contains_any(page_text, ["恭喜获得"]) and text_contains_any(page_text, ["快速购买", "购买消耗", "自动购买"]):
            return "shop_buy_settlement"

        # 0.2 日常商店主界面 (包含日常商店等排他特征，置于最顶端以防其他模块误拦截)
        shop_config = merge_shop_refresh_config(self.app_config)
        if text_contains_any(page_text, shop_config["page_keywords"]):
            return "shop_main"

        # 0. 资源仓库 (高优先级，防止由于包含“获得”等词误判为招募结算)
        warehouse_config = merge_warehouse_config(self.app_config)
        if (
            text_contains_any(page_text, warehouse_config["page_keywords"])
            and text_contains_any(page_text, warehouse_config["sub_keywords"])
        ):
            return "resource_warehouse"
        # 资源仓库二次确认弹窗兜底分类
        if (
            text_contains_any(page_text, ["确认", "确定"])
            and text_contains_any(page_text, ["消耗", "钻石", "钻"])
            and text_contains_any(page_text, ["快速采集", "资源仓库"])
        ):
            return "resource_warehouse"

        # 1. 招募结果/再次招募结果页 (高优先级优先，防止被招募主页字眼误匹配)
        # 排除包含资源仓库特征词，防止误判
        if (
            text_contains_any(page_text, ["招募结果", "再次招募", "再抽1次", "再抽10次", "遣散", "稀有角色"])
            or (text_contains_any(page_text, ["获得"])
                and text_contains_any(page_text, ["招募", "抽"])
                and not text_contains_any(page_text, ["资源仓库", "快速采集", "存储时间", "日常商店", "日常任务", "冒险", "战令", "背包", "图鉴"]))
        ):
            return "recruit_settlement"

        # 2. 招募主页面
        recruitment_config = merge_recruitment_config(self.app_config)
        recruitment_keywords = recruitment_config.get("page_keywords") or ["高级招募", "普通招募", "特定招募", "跳过动画", "招募十次"]
        if text_contains_any(page_text, recruitment_keywords):
            return "recruit_main"

        # 3. 竞技场对战结算页
        if text_contains_any(page_text, ["战斗胜利", "战斗失败", "点击继续", "点击任意区域", "DEFEAT", "WIN"]):
            return "arena_settlement"

        # 4. 竞技场对战进行中
        arena_config = merge_arena_config(self.app_config)
        battle_exclude = ["今日次数", "今日免费", "防守阵容", "挑战积分", "挑战列表", "VS", "一键布阵"]
        if text_contains_any(page_text, arena_config.get("battle_keywords") or ["挂起", "暂停"]):
            if not text_contains_any(page_text, battle_exclude):
                return "arena_battle"

        # 5. 竞技场布阵界面
        if text_contains_any(page_text, ["VS", "一键布阵", "助战"]):
            return "arena_formation"

        # 6. 竞技场今日挑战列表页
        list_exclude = ["战斗胜利", "战斗失败", "DEFEAT", "WIN", "VS", "一键布阵"]
        list_keywords = arena_config.get("challenge_list_keywords") or ["挑战列表", "今日次数", "自动战斗"]
        if "/50" in page_text or text_contains_any(page_text, list_keywords):
            if not text_contains_any(page_text, list_exclude):
                return "arena_challenge_list"

        # 7. 竞技场排位赛/资格赛主页面
        qualifier_keywords = arena_config.get("qualifier_home_keywords") or ["今日免费", "防守阵容", "挑战积分", "赛季奖励"]
        if text_contains_any(page_text, qualifier_keywords):
            return "arena_qualifier"

        # 7. 竞技场排位赛/资格赛主页面
        qualifier_keywords = arena_config.get("qualifier_home_keywords") or ["今日免费", "防守阵容", "挑战积分", "赛季奖励"]
        if text_contains_any(page_text, qualifier_keywords):
            return "arena_qualifier"

        # 巅峰赛购买弹窗
        if text_contains_any(page_text, ["购买次数"]) and text_contains_any(page_text, ["总价", "拥有"]) and text_contains_any(page_text, ["确认", "取消"]):
            return "peak_arena_buy"

        # 巅峰赛排位主页
        if text_contains_any(page_text, ["开始匹配"]) and text_contains_any(page_text, ["匹配次数", "每日任务"]):
            return "peak_arena_rank"

        # 巅峰赛布阵界面
        if text_contains_any(page_text, ["VS", "一键布阵"]) or (text_contains_any(page_text, ["挑战"]) and not text_contains_any(page_text, ["开始匹配", "赛季奖励", "奖励商店", "日常商店"])):
            return "peak_arena_formation"

        # 巅峰赛战斗进行中
        if text_contains_any(page_text, ["跳过", "跳过战斗"]) and not text_contains_any(page_text, ["开始匹配", "挑战"]):
            return "peak_arena_battle"

        # 巅峰赛对战结算页
        if text_contains_any(page_text, ["返回"]) and not text_contains_any(page_text, ["开始匹配", "匹配次数", "每日任务", "日常任务", "任务", "角色", "背包"]):
            return "peak_arena_settlement"

        # 巅峰竞技场选择主页
        if text_contains_any(page_text, ["排位赛"]) and text_contains_any(page_text, ["巅峰赛"]) and text_contains_any(page_text, ["巅峰竞技场"]):
            return "peak_arena_home"

        # 8. 竞技场选择大厅
        main_keywords = arena_config.get("main_keywords") or ["本服竞技场", "跨服竞技场", "巅峰竞技场"]
        if text_contains_any(page_text, main_keywords):
            return "arena_main"

        # 9. 友情点界面
        if text_contains_any(page_text, ["每日赠送上限", "友情点", "好友"]):
            return "friendship"

        # 10. 组织界面 (防止组织商店被误判为大厅商店)
        if text_contains_any(page_text, ["组织信息", "组织捐献", "组织技能", "组织商店", "镜像试炼"]):
            return "guild_main"

        # 12. 组织捐献选择页面
        if text_contains_any(page_text, ["金币捐献", "金币捐赠", "钻石捐献", "钻石捐赠", "选择捐赠", "选择捐献"]):
            return "guild_donation_select"


        # 11. 游戏主城 (绝对排他)
        main_city_keywords = ["喰种", "喰祖", "冒险", "战令", "日常", "任务", "角色", "背包", "图鉴", "商店"]
        if text_contains_any(page_text, main_city_keywords):
            return "main_city"

        return "unknown"

    def choose_rule_decision(self, observation, target_task=None):
        tasks = observation.get("tasks") or []
        task_page_config = merge_task_config(self.app_config)
        page_text = observation.get("page_text") or ""

        # 1. 弹窗清理拦截 (高优先级，常规处理)
        if text_contains_any(page_text, task_page_config.get("reward_popup_keywords") or []):
            page_type = self.classify_current_page(observation)
            if page_type == "daily_dungeon_settlement":
                dungeon_config = merge_daily_dungeon_config(self.app_config)
                return {
                    "intent": "日常副本扫荡结算弹窗关闭",
                    "action": "tap",
                    "target": dungeon_config["close_point"],
                    "confidence": 0.9,
                    "risk": "low"
                }
            elif page_type == "memory_house_sweep_settlement":
                memory_config = merge_memory_house_config(self.app_config)
                return {
                    "intent": "回忆之屋扫荡奖励弹窗关闭",
                    "action": "tap",
                    "target": memory_config["sweep_point"],
                    "confidence": 0.9,
                    "risk": "low"
                }
            return {
                "intent": "关闭领奖弹窗",
                "action": "tap",
                "target": {
                    "x": 640,
                    "y": 650
                },
                "confidence": 0.9,
                "risk": "low"
            }


        if text_contains_any(page_text, ["进化东京"]):
            return {
                "intent": "检测到 MuMu 桌面，停止等待用户切回游戏",
                "action": "stop",
                "target": {
                    "reason": "outside game"
                },
                "confidence": 1,
                "risk": "low"
            }

        # 2. 如果在日常任务页：只做“寻找任务”、“前往”或“领奖”
        if observation.get("is_task_page"):
            if target_task and ("巅峰" in target_task or "排位" in target_task):
                return {
                    "intent": "巅峰赛任务不处于日常任务列表页，直接点击小房子返回以从主界面进入",
                    "action": "tap",
                    "target": {
                        "x": 324,
                        "y": 40
                    },
                    "confidence": 0.95,
                    "risk": "low"
                }
            self.active_task_go_clicked = False  # 成功回到任务页，重置本轮“前往”状态
            self.active_target_task = None       # 重置当前临时目标任务

            # ------------------------------------------------------------
            # 第一阶段：安全拦截（委托未完成或目标已领取）
            # ------------------------------------------------------------
            for task in tasks:
                if target_task and target_task not in task["title"]:
                    continue
                # 委托任务为人工执行，未完成时直接安全停机
                if target_task and "委托" in target_task and task["button_state"] == "go":
                    return {
                        "intent": f"接取3次委托任务未完成，该任务需手动执行，停止日常: {task['title']}",
                        "action": "stop",
                        "target": {
                            "reason": "commission requires manual work"
                        },
                        "confidence": 1,
                        "risk": "low"
                    }
                if target_task and task["button_state"] == "claimed":
                    return {
                        "intent": f"目标任务已领取: {task['title']}",
                        "action": "stop",
                        "target": {
                            "reason": "target task already claimed"
                        },
                        "confidence": 1,
                        "risk": "low"
                    }

            # ------------------------------------------------------------
            # 第二阶段：遍历可见列表，优先寻找并执行有效的 go 任务
            # ------------------------------------------------------------
            go_task_to_execute = None
            has_go_task = False
            for task in tasks:
                if target_task and target_task not in task["title"]:
                    continue
                if not task["done"] and task["button_state"] == "go":
                    # 过滤监狱及不受支持的低性价比任务
                    if any(k in task["title"] for k in ["库克利亚", "监狱", "镜像试炼", "强化装备"]):
                        continue
                    supported_keywords = ["登录", "委托", "友情", "招募", "资源", "采集", "竞技", "捐献", "商店", "回忆", "副本", "讨伐", "赫者"]
                    if not any(k in task["title"] for k in supported_keywords):
                        continue
                    if "招募" in task["title"] and self.has_decision("高级招募已完成，返回主界面"):
                        continue
                    has_go_task = True
                    if not go_task_to_execute:
                        go_task_to_execute = task

            if go_task_to_execute:
                self.active_task_go_clicked = True  # 设置本轮已点击“前往”状态
                self.active_target_task = go_task_to_execute["title"]  # 记录当前点击前往的任务
                self.daily_page_swipe_count = 0  # 点击前往时重置当前列表滑动计数器
                self.daily_page_claiming = False
                self.daily_page_up_swipe_count = 0
                self.task_state = {}  # 点击前往新任务时，重置所有任务显式状态机，防止跨任务状态污染
                return {
                    "intent": f"前往执行未完成任务: {go_task_to_execute['title']}",
                    "action": "tap",
                    "target": go_task_to_execute["action_point"],
                    "confidence": 0.82,
                    "risk": "low"
                }

            # ------------------------------------------------------------
            # 第三阶段：若当前屏没有 go 任务，且滚屏次数未超限，优先滑动寻找 go 任务
            # ------------------------------------------------------------
            if target_task:
                scroll_intent = f"滚动任务列表寻找目标任务: {target_task}"
                max_scrolls = int(self.guardrails.get("max_target_search_scrolls", 6))
            else:
                scroll_intent = "滚动任务列表寻找未完成日常任务"
                max_scrolls = int(self.guardrails.get("max_list_search_scrolls", 6))

            # 使用实例属性记录当前在任务页连续滑动的次数，防止跨任务被错误累加
            scroll_count = self.daily_page_swipe_count

            # 检测是否已经触底：如果上一次动作是向下滚动寻找任务，且这一帧画面没有改变，说明已触底
            last_action_is_down_swipe = False
            if self.history:
                last_dec = self.history[-1].get("decision", {})
                if last_dec.get("action") == "swipe" and "寻找" in last_dec.get("intent", "") and "向上" not in last_dec.get("intent", ""):
                    last_action_is_down_swipe = True
            
            if last_action_is_down_swipe and self.unchanged_count >= 1:
                self.daily_page_swipe_count = max_scrolls
                scroll_count = max_scrolls

            if scroll_count >= max_scrolls:
                self.daily_page_claiming = True

            # 在没有可做前往任务且滑动次数未超限前，继续向下滑动搜寻
            if scroll_count < max_scrolls and not self.daily_page_claiming:
                y1_val = 550
                y2_val = 280
                if target_task:
                    claimed_or_rewarded = (
                        self.has_decision("领取已完成任务奖励")
                        or self.has_decision("目标任务已领取")
                    )
                    if claimed_or_rewarded:
                        y1_val = 300
                        y2_val = 610

                self.daily_page_swipe_count += 1  # 累加本次连续滑动次数

                return {
                    "intent": scroll_intent,
                    "action": "swipe",
                    "target": {
                        "x1": 700,
                        "y1": y1_val,
                        "x2": 700,
                        "y2": y2_val,
                        "duration_ms": 1000
                    },
                    "confidence": 0.75,
                    "risk": "low"
                }

            # ------------------------------------------------------------
            # 第四阶段：当滑动达到上限且没有 go 任务时，统一执行 claim 领奖
            # ------------------------------------------------------------
            has_claimable_task = False
            # 增加保护：如果在本次日常大循环中已经点击过一次领奖，为了防止空点击，不再重复寻找 claim
            already_claimed = self.has_decision("领取已完成任务奖励")
            
            if not already_claimed:
                for task in tasks:
                    if target_task and target_task not in task["title"]:
                        continue
                    if task["button_state"] == "claim" or (task["done"] and task["button_state"] not in ("go", "claimed")):
                        has_claimable_task = True
                        return {
                            "intent": f"领取已完成任务奖励: {task['title']}",
                            "action": "claim",
                            "target": task["action_point"],
                            "confidence": 0.9,
                            "risk": "low"
                        }

            # 如果当前屏没有可领奖的任务，但之前曾向下滑动过，且回滑次数未超限（仅允许向上回滑 1 次），向上划回去
            if not already_claimed and not has_claimable_task and self.daily_page_swipe_count > 0 and self.daily_page_up_swipe_count < 1:
                self.daily_page_swipe_count -= 1  # 逐渐递减滑动计数以逐步回滑
                self.daily_page_up_swipe_count += 1
                return {
                    "intent": "当前屏无领奖按钮，向上滑动 1 次以寻找已完成日常奖励",
                    "action": "swipe",
                    "target": {
                        "x1": 700,
                        "y1": 365,
                        "x2": 700,
                        "y2": 550,
                        "duration_ms": 800
                    },
                    "confidence": 0.75,
                    "risk": "low"
                }

            # ------------------------------------------------------------
            # 第五阶段：若无日常领奖任务，领取日常活跃度宝箱并安全停机
            # ------------------------------------------------------------
            # 采用盲点扫尾策略：依次尝试点击 4 个日常活跃度宝箱坐标各 1 次（已领过的在历史里自动过滤跳过），能领则领
            chests = task_page_config.get("active_chests") or [
                {"x": 624, "y": 144},
                {"x": 800, "y": 144},
                {"x": 965, "y": 144},
                {"x": 1135, "y": 144}
            ]
            for index, chest in enumerate(chests):
                chest_name = f"第{index + 1}个"
                chest_intent = f"领取日常活跃度宝箱{chest_name}"
                if not self.has_decision(chest_intent):
                    return {
                        "intent": chest_intent,
                        "action": "tap",
                        "target": chest,
                        "confidence": 0.85,
                        "risk": "low"
                    }

            # 安全停机逻辑
            if not target_task:
                return {
                    "intent": "当前任务页没有可执行或可领取任务",
                    "action": "stop",
                    "target": {
                        "reason": "no actionable task"
                    },
                    "confidence": 1,
                    "risk": "low"
                }
            else:
                if self.has_decision("领取已完成任务奖励") or self.has_decision("目标任务已领取"):
                    return {
                        "intent": f"目标任务奖励已领取，停止查验: {target_task}",
                        "action": "stop",
                        "target": {
                            "reason": "target reward was claimed"
                        },
                        "confidence": 1,
                        "risk": "low"
                    }
                if target_task and ("巅峰" in target_task or "排位" in target_task):
                    return {
                        "intent": "巅峰赛任务不在日常任务页，点击小房子退回以从主界面进入",
                        "action": "tap",
                        "target": {
                            "x": 324,
                            "y": 40
                        },
                        "confidence": 0.9,
                        "risk": "low"
                    }
                return {
                    "intent": f"未找到目标任务，停止: {target_task}",
                    "action": "stop",
                    "target": {
                        "reason": "target task not found"
                    },
                    "confidence": 1,
                    "risk": "low"
                }

        # 3. 如果不在日常任务页
        if not observation.get("is_task_page"):
            self.daily_page_swipe_count = 0  # 不在任务页时，重置日常列表滑动计数器
            self.daily_page_claiming = False
            self.daily_page_up_swipe_count = 0
            page_type = self.classify_current_page(observation)
            effective_target = target_task or self.active_target_task
            
            # 自适应豁免：如果当前页面正好就是我们要执行的子任务目标页面，自动激活前往标记，避免多余的退回再进动作
            is_matched_page = False
            if effective_target:
                if "友情" in effective_target and page_type == "friendship":
                    is_matched_page = True
                elif "招募" in effective_target and page_type in ["recruit_main", "recruit_settlement"]:
                    is_matched_page = True
                elif ("资源" in effective_target or "采集" in effective_target) and page_type == "resource_warehouse":
                    is_matched_page = True
                elif ("竞技" in effective_target or "竞技场" in effective_target) and page_type in [
                    "arena_main", "arena_qualifier", "arena_challenge_list", "arena_formation", "arena_battle", "arena_settlement"
                ]:
                    is_matched_page = True
                elif ("巅峰" in effective_target or "排位" in effective_target) and page_type in [
                    "arena_main", "peak_arena_home", "peak_arena_rank", "peak_arena_buy", "peak_arena_formation", "peak_arena_battle", "peak_arena_settlement"
                ]:
                    is_matched_page = True
                elif "捐献" in effective_target and page_type in ["guild_main", "guild_donation_select"]:
                    is_matched_page = True
                elif "商店" in effective_target and page_type in ["shop_main", "shop_buy_settlement"]:
                    is_matched_page = True
                elif "回忆" in effective_target and page_type in ["memory_house_main", "memory_house_sweep_settlement"]:
                    is_matched_page = True
                elif "副本" in effective_target and page_type in ["daily_dungeon_main", "daily_dungeon_settlement"]:
                    is_matched_page = True
                elif ("讨伐" in effective_target or "赫者" in effective_target) and page_type in ["kakuja_hunt_main", "kakuja_hunt_formation", "kakuja_hunt_battle", "kakuja_hunt_victory", "kakuja_hunt_loading"]:
                    is_matched_page = True

            is_go_triggered = self.active_task_go_clicked or is_matched_page or (effective_target and self.has_clicked_go(effective_target))

            # 3.1 核心前往原则：必须已触发“前往”，且当前处于该任务子页面的特征范围时，才执行具体子任务动作
            if effective_target and is_go_triggered:
                from tasks import (
                    login, commission, friendship, recruitment, resource_warehouse, arena, guild_donation,
                    shop_refresh, memory_house, daily_dungeon, kakuja_hunt, peak_arena
                )
                # 日常登录日常逻辑 (无需具体子页面逻辑，由通用逻辑直接领奖)
                if "登录" in effective_target:
                    decision = login.run_task(self, observation)
                    if decision:
                        return decision

                # 委托日常逻辑 (无需具体子页面逻辑，由通用逻辑直接领奖，未完成时会在日常页被安全挂起)
                elif "委托" in effective_target:
                    decision = commission.run_task(self, observation)
                    if decision:
                        return decision

                # 友情点日常页面逻辑
                elif "友情" in effective_target and page_type == "friendship":
                    decision = friendship.run_task(self, observation)
                    if decision:
                        return decision

                # 招募日常页面逻辑
                elif "招募" in effective_target and page_type in ["recruit_main", "recruit_settlement"]:
                    decision = recruitment.run_task(self, observation)
                    if decision:
                        return decision

                # 资源仓库快速采集任务逻辑
                elif ("资源" in effective_target or "采集" in effective_target) and page_type == "resource_warehouse":
                    decision = resource_warehouse.run_task(self, observation)
                    if decision:
                        return decision

                # 竞技场日常页面逻辑
                elif ("竞技" in effective_target or "竞技场" in effective_target) and page_type in [
                    "arena_main", "arena_qualifier", "arena_challenge_list", "arena_formation", "arena_battle", "arena_settlement"
                ]:
                    decision = arena.run_task(self, observation)
                    if decision:
                        return decision

                # 巅峰赛日常页面逻辑
                elif ("巅峰" in effective_target or "排位" in effective_target) and page_type in [
                    "arena_main", "peak_arena_home", "peak_arena_rank", "peak_arena_buy", "peak_arena_formation", "peak_arena_battle", "peak_arena_settlement"
                ]:
                    decision = peak_arena.run_task(self, observation)
                    if decision:
                        return decision

                # 组织捐献日常任务逻辑
                elif "捐献" in effective_target and page_type in ["guild_main", "guild_donation_select"]:
                    decision = guild_donation.run_task(self, observation)
                    if decision:
                        return decision
                elif "商店" in effective_target and page_type in ["shop_main", "shop_buy_settlement"]:
                    decision = shop_refresh.run_task(self, observation)
                    if decision:
                        return decision
                elif "回忆" in effective_target and page_type in ["memory_house_main", "memory_house_sweep_settlement"]:
                    decision = memory_house.run_task(self, observation)
                    if decision:
                        return decision
                elif "副本" in effective_target and page_type in ["daily_dungeon_main", "daily_dungeon_settlement"]:
                    decision = daily_dungeon.run_task(self, observation)
                    if decision:
                        return decision
                elif ("讨伐" in effective_target or "赫者" in effective_target) and page_type in ["kakuja_hunt_main", "kakuja_hunt_formation", "kakuja_hunt_battle", "kakuja_hunt_victory", "kakuja_hunt_loading", "unknown"]:
                    decision = kakuja_hunt.run_task(self, observation)
                    if decision:
                        return decision

            # 3.2 导航返回日常任务栏：如果处于子页面但尚未触发前往，或者不在当前目标任务页面，执行层级导航退回
            
            # 特例一：如果在招募结果结算页，直接调用关闭，以退回到招募主界面
            if page_type == "recruit_settlement":
                recruitment_config = merge_recruitment_config(self.app_config)
                return {
                    "intent": "关闭招募结果页",
                    "action": "tap",
                    "target": recruitment_config["close_result_point"],
                    "confidence": 0.85,
                    "risk": "low"
                }

            # 特例三：如果处于图鉴页面，点击右上角小房子返回主界面以摆脱误触
            if page_type == "illustration_page":
                return {
                    "intent": "从图鉴返回主界面",
                    "action": "tap",
                    "target": {"x": 1215, "y": 40},
                    "confidence": 0.9,
                    "risk": "low"
                }

            # 特例二：如果在挑战列表弹窗中且尚未前往，点击右上角大红 X 按钮先关闭弹窗
            if page_type == "arena_challenge_list":
                return {
                    "intent": "竞技场尚未触发前往，先关闭挑战列表弹窗",
                    "action": "tap",
                    "target": {
                        "x": 1142,
                        "y": 82
                    },
                    "confidence": 0.85,
                    "risk": "low"
                }

            # 如果当前已经处于主界面（大厅），点击日常入口图标 (50, 328) 进入日常任务
            # 特例：若目标任务是巅峰赛/排位赛，由于其不出现在大厅，直接从主界面进入竞技场 (282, 357)
            if page_type == "main_city":
                if target_task and ("巅峰" in target_task or "排位" in target_task):
                    return {
                        "intent": "从主界面直接前往竞技场大厅(巅峰赛入口)",
                        "action": "tap",
                        "target": {
                            "x": 282,
                            "y": 357
                        },
                        "confidence": 0.9,
                        "risk": "low"
                    }
                return {
                    "intent": "从主界面打开任务页",
                    "action": "tap",
                    "target": {
                        "x": 50,
                        "y": 328
                    },
                    "confidence": 0.78,
                    "risk": "low"
                }

            if page_type == "resource_warehouse":
                warehouse_config = merge_warehouse_config(self.app_config)
                return {
                    "intent": "资源仓库尚未触发前往，先关闭弹窗",
                    "action": "tap",
                    "target": warehouse_config["close_point"],
                    "confidence": 0.85,
                    "risk": "low"
                }

            # 特例四：如果在招募主页面动作已完成，点击右上角小房子 (1215, 40) 返回主界面
            if page_type == "recruit_main":
                return {
                    "intent": "返回主界面以寻找任务页",
                    "action": "tap",
                    "target": {
                        "x": 1215,
                        "y": 40
                    },
                    "confidence": 0.85,
                    "risk": "low"
                }

            # 如果处于其他任何任务子页面 (如资格赛主页、布阵等) 但还没前往，一律点顶部房子图标 (324, 39) 退回大厅
            if page_type in ["arena_main", "arena_qualifier", "arena_formation", "friendship", "unknown", "guild_main", "guild_donation_select", "shop_main", "shop_buy_settlement", "memory_house_main", "memory_house_sweep_settlement", "daily_dungeon_main", "daily_dungeon_settlement", "kakuja_hunt_main", "kakuja_hunt_formation", "kakuja_hunt_battle", "kakuja_hunt_victory", "kakuja_hunt_loading", "peak_arena_home", "peak_arena_rank", "peak_arena_buy", "peak_arena_formation", "peak_arena_battle", "peak_arena_settlement"]:
                return {
                    "intent": "返回主界面以寻找任务页",
                    "action": "tap",
                    "target": {
                        "x": 324,
                        "y": 39
                    },
                    "confidence": 0.85,
                    "risk": "low"
                }
    def check_unchanged(self, image):
        current_hash = image_hash(image, int(self.guardrails["screen_hash_size"]))

        # 优化逻辑：只对可能改变画面的动作（如 tap, swipe, claim）进行画面未改变计数，而对 wait 等动作免除计数保护
        last_action = None
        if self.history:
            last_action = self.history[-1].get("decision", {}).get("action")

        if last_action not in {"tap", "swipe", "claim"}:
            self.unchanged_count = 0
            self.last_hash = current_hash
            return

        if current_hash == self.last_hash:
            self.unchanged_count += 1
        else:
            self.unchanged_count = 0

        self.last_hash = current_hash

        if self.unchanged_count >= int(self.guardrails["max_unchanged_screens"]):
            raise GuardrailError("screen did not change after repeated actions")

    def run(self, target_task=None):
        self.history = []  # 重置本次运行的动作历史，防止跨轮日常托管累积滑动与决策计数
        self.active_task_go_clicked = False
        self.active_target_task = None
        self.arena_last_auto_try_count = -1
        self.arena_task_complete = False
        self.arena_no_action_retry_count = 0
        self.has_scrolled_to_top = False
        started = time.time()
        max_steps = int(self.guardrails["max_steps_per_task"])

        for step in range(1, max_steps + 1):
            if time.time() - started > float(self.guardrails["max_run_seconds"]):
                raise GuardrailError("max run time exceeded")

            image, screenshot_path = self.capture(step)
            self.last_image = image
            self.check_unchanged(image)
            observation = detect_task_page(image, self.app_config)
            context = {
                "目标任务": target_task,
                "当前观察": observation,
                "历史动作": self.history[-6:],
                "可用动作": self.guardrails["allowed_actions"],
                "规则": "优先领取已完成任务；未完成任务点击前往；不确定或高风险则 stop。"
            }
            decision = self.choose_rule_decision(observation, target_task)
            source = "rules"

            if decision is None:
                decision = {
                    "intent": "当前画面未匹配任何规则动作，安全停机",
                    "action": "stop",
                    "target": {
                        "reason": "no rule matched"
                    },
                    "confidence": 1,
                    "risk": "low"
                }
                source = "rules"

            decision = self.validate_decision(decision, observation)
            action_result = self.execute_decision(decision)
            event = {
                "step": step,
                "screenshot": screenshot_path,
                "source": source,
                "observation": observation,
                "decision": decision,
                "action_result": action_result
            }
            self.history.append(event)
            self.logger.event("step", event)

            if self.dry_run:
                self.logger.event("dry_run_stop", decision)
                return {
                    "status": "dry_run",
                    "next_decision": decision,
                    "run_dir": self.logger.path,
                    "steps": step
                }

            if decision["action"] == "stop":
                self.logger.event("stop", decision)
                return {
                    "status": "stopped",
                    "reason": decision.get("target", {}).get("reason") or decision["intent"],
                    "run_dir": self.logger.path,
                    "steps": step
                }

        return {
            "status": "max_steps_reached",
            "run_dir": self.logger.path,
            "steps": max_steps
        }
