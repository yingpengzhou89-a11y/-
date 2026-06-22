# 赫者讨伐任务：`max_actions` 语义与可靠状态管理优化说明

## 1. 文档目的

本文只针对赫者讨伐任务逻辑中的两个核心问题进行详细说明：

1. `max_actions` 当前到底控制了什么，以及为什么它不能代表任务完成；
2. 如何用更可靠的任务状态替代“根据历史点击记录猜测执行结果”。

目标是帮助 Antigravity 理解现有代码的真实行为，并据此重构 `run_task()`，避免出现以下问题：

- 挑战按钮第一次没有点成功，程序却直接退出；
- 上一次任务的历史记录污染本次任务；
- 已经发出点击动作，就被错误地当成页面已跳转或任务已完成；
- 新一场战斗因为旧的“跳过”记录而不再点击跳过；
- 正常的防重复机制和真实任务状态混在一起，导致流程难以维护。

---

# 2. 相关原始代码

当前主界面部分逻辑如下：

```python
if page_type == "kakuja_hunt_main":
    if runner.has_decision("赫者讨伐胜利结算点击确定"):
        return {
            "intent": "赫者讨伐挑战已完成，点击小房子返回主界面",
            "action": "tap",
            "target": config["back_point"],
            "confidence": 0.9,
            "risk": "low"
        }

    actions = runner.decision_count(
        action="tap",
        intent_contains="赫者讨伐主界面点击挑战",
        after_intent="前往执行未完成任务:"
    )

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
```

当前战斗部分还使用了类似的历史判断：

```python
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
```

---

# 3. `max_actions` 当前的真实含义

## 3.1 它统计的是“点击尝试次数”

当前代码：

```python
actions = runner.decision_count(
    action="tap",
    intent_contains="赫者讨伐主界面点击挑战",
    after_intent="前往执行未完成任务:"
)
```

统计的是：

> 从最近一次“前往执行未完成任务”之后，程序曾经返回过多少次“点击赫者讨伐主界面挑战按钮”的决策。

它只能证明：

```text
程序曾经尝试点击挑战按钮
```

它不能证明：

```text
挑战按钮确实被点击成功
页面确实进入了布阵界面
战斗确实开始
任务确实完成
```

因此，`max_actions` 实际上是一个：

```text
挑战入口最大点击尝试次数限制
```

它不是最大挑战完成次数、任务目标次数，也不是任务完成状态。

---

## 3.2 默认值为1时的真实流程

假设配置为：

```python
max_actions = 1
```

第一次进入赫者讨伐主界面：

```text
actions = 0
```

程序返回一次“点击挑战”。该决策一旦写入历史记录，之后：

```text
actions = 1
```

如果页面仍然停留在赫者讨伐主界面，代码就会直接点击小房子退出。

实际流程是：

```text
第一次识别主界面
    ↓
尝试点击挑战
    ↓
无论点击是否成功，历史记录都增加为1
    ↓
如果下一轮仍识别为主界面
    ↓
直接点击小房子退出
```

这意味着 `max_actions = 1` 非常保守：

- 优点：防止无限重复点击和重复消耗；
- 缺点：第一次点击只要没有成功，就完全没有重试机会。

---

# 4. `max_actions` 逻辑的主要风险

## 4.1 点击失败后提前退出

```text
主界面识别成功
→ 程序点击挑战
→ 点击位置短暂被动画遮挡
→ 游戏没有响应
→ 下一轮仍是主界面
→ actions 已经等于1
→ 程序直接退出
```

最终结果：任务没有完成，但程序以为已经达到动作限制。

## 4.2 网络延迟会被误判为点击失败

点击已经成功，但页面切换可能需要数秒。控制循环如果很快再次截图，仍可能识别为主界面，然后错误触发退出。

## 4.3 页面分类延迟会触发错误退出

点击挑战后，画面可能已经开始变化，但分类器仍返回 `kakuja_hunt_main`。当前代码无法区分：

```text
稳定停留在主界面
```

和：

```text
刚点击挑战，正在等待页面切换
```

## 4.4 “达到动作限制”不等于“完成任务”

当前意图名称：

```text
赫者讨伐动作已满足限制，点击小房子返回主界面
```

容易让人误解成任务已经完成。建议改成：

```text
赫者讨伐挑战入口已达到最大尝试次数，为防止重复消耗而退出
```

---

# 5. `max_actions` 应该保留吗

可以保留，但应把它定位为最后一道安全保险，而不是主要流程判断依据。

适合承担的职责：

- 防止页面识别异常时无限点击挑战；
- 防止挑战入口被重复触发；
- 防止因错误分类造成资源重复消耗；
- 多次尝试仍无法进入布阵页面时安全退出。

不适合承担的职责：

- 判断任务是否完成；
- 判断点击是否成功；
- 判断是否已经进入战斗；
- 判断是否应该返回主界面；
- 代替明确的任务状态。

---

# 6. 推荐重新命名

建议将：

```python
max_actions
```

改成：

```python
max_main_challenge_attempts
```

或：

```python
max_challenge_entry_attempts
```

例如：

```python
max_attempts = int(
    config.get("max_main_challenge_attempts", 2)
)
```

这能明确表示它限制的是主界面挑战入口的最大尝试次数。

---

# 7. 推荐的可靠状态判断原则

## 7.1 页面状态优先于点击历史

判断当前处于什么阶段，应优先依赖：

- 当前截图；
- 当前页面分类；
- 当前可见按钮；
- 当前弹窗；
- 页面转换结果。

而不是只依赖“之前点过什么”。

## 7.2 发出动作不等于动作成功

必须明确区分：

```text
action_requested
```

和：

```text
action_confirmed
```

例如，程序发出“点击挑战”只代表：

```text
challenge_click_requested = True
```

只有下一轮识别到：

```python
page_type == "kakuja_hunt_formation"
```

才能确认：

```text
challenge_entry_confirmed = True
```

## 7.3 状态转换必须由新页面确认

推荐转换关系：

```text
主界面点击挑战
    ↓
识别到布阵界面
    ↓
确认挑战入口成功

布阵界面点击BOSS战
    ↓
识别到加载页或战斗页
    ↓
确认BOSS战启动成功

战斗页点击跳过
    ↓
识别到胜利结算
    ↓
确认战斗完成

胜利结算点击确定
    ↓
再次识别到赫者讨伐主界面
    ↓
确认结算已关闭，可以退出
```

---

# 8. 推荐的任务状态结构

建议为赫者讨伐任务维护独立状态：

```python
runner.task_state["kakuja_hunt"] = {
    "stage": "idle",

    "main_challenge_attempts": 0,
    "challenge_click_pending": False,
    "challenge_click_time": None,

    "formation_boss_attempts": 0,
    "boss_click_pending": False,

    "skip_attempts": 0,
    "skip_clicked": False,

    "loading_wait_count": 0,

    "battle_result_seen": False,
    "victory_confirm_attempts": 0,
    "victory_confirmed": False,

    "completed": False,
    "last_page_type": None,
    "unknown_page_count": 0,
}
```

---

# 9. 每个状态字段的作用

## 9.1 `stage`

表示当前任务流程阶段，例如：

```python
"idle"
"entered_main"
"challenge_requested"
"formation"
"boss_requested"
"loading"
"battle"
"result"
"returning"
"completed"
"failed"
```

它让程序知道当前应该期待哪个页面，而不只是知道过去点过哪些按钮。

## 9.2 `main_challenge_attempts`

只记录本次任务中，在赫者讨伐主界面点击挑战的次数。

用途：

- 第一次点击失败后允许有限重试；
- 达到上限后安全退出；
- 不使用整个全局历史记录；
- 新任务开始时自动清零。

## 9.3 `challenge_click_pending`

表示：

```text
刚刚点击了挑战，正在等待页面跳转
```

点击挑战以后，不应该立刻在下一轮因为仍是主界面而退出。

应先进入等待状态：

```python
challenge_click_pending = True
```

下一轮如果仍是主界面：

- 距离点击不足2秒：继续等待；
- 超过2秒仍未跳转：允许重试；
- 重试达到上限：安全退出。

## 9.4 `formation_boss_attempts`

记录布阵页面中点击BOSS战的次数，用于避免网络卡顿时无限点击，同时允许第一次失败后重试。

## 9.5 `skip_attempts`

记录当前这一场战斗中点击跳过的尝试次数。

它必须是当前战斗级别的计数，不能是整个任务历史或整个程序生命周期的计数。

进入新一场战斗时应重置：

```python
skip_attempts = 0
skip_clicked = False
```

## 9.6 `battle_result_seen`

识别到胜利结算时设为 `True`，表示战斗结果页面已经真实出现。

## 9.7 `victory_confirmed`

不能在发出“点击确定”时立即设为 `True`。

应当在：

```text
胜利结算点击确定后
重新识别到赫者讨伐主界面
```

时设置：

```python
victory_confirmed = True
completed = True
```

---

# 10. 推荐状态机

```text
IDLE
  ↓ 从日常任务点击前往
ENTERED_MAIN
  ↓ 点击挑战
CHALLENGE_REQUESTED
  ├─ 识别到布阵界面 → FORMATION
  ├─ 短时间仍在主界面 → WAIT
  └─ 超时仍在主界面 → RETRY_OR_ABORT

FORMATION
  ↓ 点击BOSS战
BOSS_REQUESTED
  ├─ 识别到加载页 → LOADING
  ├─ 识别到战斗页 → BATTLE
  └─ 超时仍在布阵页 → RETRY_OR_ABORT

LOADING
  ├─ 识别到战斗页 → BATTLE
  └─ 超过最大等待时间 → ABORT

BATTLE
  ├─ 跳过按钮可用且尚未成功点击 → TRY_SKIP
  ├─ 跳过已尝试 → WAIT
  └─ 识别到胜利结算 → RESULT

RESULT
  ↓ 点击确定
RESULT_CONFIRM_PENDING
  ├─ 识别到赫者讨伐主界面 → COMPLETED
  └─ 仍在结算页 → RETRY_CONFIRM

COMPLETED
  ↓ 点击小房子退出
DONE
```

---

# 11. 推荐的主界面逻辑

下面是更可靠的伪代码：

```python
if page_type == "kakuja_hunt_main":
    state = runner.task_state["kakuja_hunt"]

    # 胜利结算后重新回到主界面，才确认任务完成
    if state.get("battle_result_seen"):
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

    # 刚点击挑战，先等待页面跳转
    if state.get("challenge_click_pending"):
        elapsed = now() - state["challenge_click_time"]

        if elapsed < 2.0:
            return {
                "intent": "赫者讨伐已点击挑战，等待进入布阵界面",
                "action": "wait",
                "target": {"seconds": 1},
                "confidence": 0.9,
                "risk": "low"
            }

        # 超时后认为本次点击没有成功
        state["challenge_click_pending"] = False

    max_attempts = int(
        config.get("max_main_challenge_attempts", 2)
    )

    if state["main_challenge_attempts"] >= max_attempts:
        return {
            "intent": "赫者讨伐挑战入口多次尝试仍未成功，为防止重复操作而退出",
            "action": "tap",
            "target": config["back_point"],
            "confidence": 0.9,
            "risk": "low"
        }

    state["main_challenge_attempts"] += 1
    state["challenge_click_pending"] = True
    state["challenge_click_time"] = now()
    state["stage"] = "challenge_requested"

    return {
        "intent": (
            f"赫者讨伐主界面第"
            f"{state['main_challenge_attempts']}次尝试点击挑战"
        ),
        "action": "tap",
        "target": config["main_challenge_point"],
        "confidence": 0.88,
        "risk": "low"
    }
```

---

# 12. 布阵页面如何确认主界面点击成功

当识别到：

```python
page_type == "kakuja_hunt_formation"
```

说明主界面挑战按钮已经成功生效。

此时应更新状态：

```python
state["challenge_click_pending"] = False
state["stage"] = "formation"
```

然后再点击BOSS战。

进入加载页或战斗页后，才能确认BOSS战按钮点击成功：

```python
state["boss_click_pending"] = False
```

---

# 13. 战斗跳过状态的可靠实现

当前使用：

```python
runner.has_decision("赫者讨伐战斗中点击跳过")
```

可能受到旧任务污染。

推荐改为当前任务状态：

```python
if page_type == "kakuja_hunt_battle":
    state = runner.task_state["kakuja_hunt"]
    state["stage"] = "battle"
    state["boss_click_pending"] = False

    max_skip_attempts = int(
        config.get("max_skip_attempts", 2)
    )

    if state["skip_attempts"] < max_skip_attempts:
        state["skip_attempts"] += 1

        return {
            "intent": (
                f"赫者讨伐战斗中第"
                f"{state['skip_attempts']}次尝试点击跳过"
            ),
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
```

更理想的方式是增加：

```python
observation["kakuja_skip_button_visible"]
```

只有检测到跳过按钮可见时才点击。

---

# 14. 胜利状态的可靠实现

识别到胜利结算：

```python
if page_type == "kakuja_hunt_victory":
    state["battle_result_seen"] = True
    state["stage"] = "result"
```

然后点击确定。

注意，此时只能确认胜利结算已出现，还不能确认结算已经成功关闭。

只有下一轮重新识别到赫者讨伐主界面时，才设置：

```python
state["victory_confirmed"] = True
state["completed"] = True
```

---

# 15. 任务状态初始化与清理

## 15.1 新任务开始时初始化

当外层逻辑执行：

```text
前往执行未完成任务: 赫者讨伐1次
```

应立即初始化：

```python
runner.task_state["kakuja_hunt"] = {
    "stage": "idle",
    "main_challenge_attempts": 0,
    "challenge_click_pending": False,
    "challenge_click_time": None,
    "formation_boss_attempts": 0,
    "boss_click_pending": False,
    "skip_attempts": 0,
    "loading_wait_count": 0,
    "battle_result_seen": False,
    "victory_confirmed": False,
    "completed": False,
    "unknown_page_count": 0,
}
```

这样不会受到昨天、上一次任务、上一场战斗或旧跳过记录的影响。

## 15.2 任务结束后清理

完成并返回任务栏后，可以：

```python
runner.task_state.pop("kakuja_hunt", None)
```

也可以保留最终结果用于日志，但下一次任务开始时必须覆盖重置。

---

# 16. 是否完全弃用 `decision_count`

不需要完全弃用。

`decision_count` 仍适合：

- 审计日志；
- 调试；
- 输出任务执行过程；
- 统计异常次数；
- 防止程序彻底失控；
- 在任务状态丢失时提供最后一道保护。

但不应再作为主要业务状态。

建议优先级：

```text
当前页面证据
    >
当前任务显式状态
    >
当前任务内决策历史
    >
全局历史记录
```

---

# 17. 建议的配置项

```python
{
    "max_main_challenge_attempts": 2,
    "main_challenge_transition_timeout": 2.5,

    "max_formation_boss_attempts": 2,
    "formation_transition_timeout": 3.0,

    "max_skip_attempts": 2,

    "max_loading_wait_count": 15,
    "loading_wait_seconds": 2,

    "max_victory_confirm_attempts": 3,
    "max_unknown_page_count": 5
}
```

说明：

- `max_main_challenge_attempts`：主界面挑战按钮最多尝试几次；
- `main_challenge_transition_timeout`：点击挑战后等待布阵页面的时间；
- `max_formation_boss_attempts`：BOSS战按钮最多尝试几次；
- `max_skip_attempts`：当前战斗最多点击几次跳过；
- `max_loading_wait_count`：加载页最多循环等待多少次；
- `max_victory_confirm_attempts`：胜利确定最多尝试几次；
- `max_unknown_page_count`：未知页面连续出现多少次后停止。

---

# 18. 推荐的日志设计

建议每次状态变化都记录：

```text
[kakuja_hunt]
stage: entered_main -> challenge_requested
main_challenge_attempts: 1
page_type: kakuja_hunt_main
action: tap
target: challenge_point
```

页面确认后记录：

```text
[kakuja_hunt]
stage: challenge_requested -> formation
confirmation: challenge entry succeeded
page_type: kakuja_hunt_formation
```

点击超时记录：

```text
[kakuja_hunt]
challenge transition timeout
attempt: 1/2
current page: kakuja_hunt_main
next action: retry
```

达到上限时记录：

```text
[kakuja_hunt]
challenge entry failed after 2 attempts
safe abort to main screen
```

---

# 19. 推荐验收场景

## 场景1：首次点击挑战成功

```text
主界面点击挑战
→ 等待
→ 识别到布阵
→ 不再点击小房子退出
```

## 场景2：首次点击挑战失败

```text
第一次点击
→ 等待页面转换
→ 超时仍是主界面
→ 第二次重试
→ 成功进入布阵
```

不能在第一次失败后立即退出。

## 场景3：连续两次点击挑战失败

```text
达到 max_main_challenge_attempts
→ 明确记录入口失败
→ 为防止重复操作而安全退出
```

不能把这种情况标记为任务完成。

## 场景4：点击后网络延迟

```text
challenge_click_pending = True
→ 等待配置的转换时间
→ 不立即重试或退出
```

## 场景5：旧任务有胜利历史

```text
新任务状态已重置
→ 不读取旧胜利记录作为本次完成依据
→ 正常点击挑战
```

## 场景6：旧战斗有跳过历史

```text
新任务 skip_attempts = 0
→ 新战斗仍然会点击跳过
```

## 场景7：胜利页面点击确定未生效

```text
仍识别为胜利页面
→ 在限制次数内再次点击确定
→ 直到重新识别到主界面
→ 才标记任务完成
```

---

# 20. 给 Antigravity 的直接修改要求

请重构赫者讨伐任务状态控制，重点要求如下：

1. `max_actions` 不得继续被理解为任务完成次数；
2. 将其改名为 `max_main_challenge_attempts`；
3. 它只作为挑战入口点击失败时的安全上限；
4. 点击挑战后增加 `challenge_click_pending` 状态；
5. 点击后先等待页面转换，不能下一轮仍是主界面就立刻退出；
6. 识别到布阵界面后，才确认主界面挑战点击成功；
7. 第一次点击失败后应允许有限重试；
8. 多次失败后才安全退出；
9. 不得使用全局 `has_decision()` 直接判断本次任务是否完成；
10. 新任务开始时初始化独立的 `kakuja_hunt` 状态；
11. 战斗跳过次数必须限制在当前任务或当前战斗内；
12. 识别到胜利结算时，只设置 `battle_result_seen`；
13. 胜利结算点击确定后重新回到赫者讨伐主界面，才设置 `completed = True`；
14. 页面证据优先于动作历史；
15. 动作历史只用于审计、防失控和辅助判断；
16. 状态变化、超时、重试和退出原因必须写入日志；
17. 配置中分别增加主界面挑战、布阵BOSS、跳过、加载和结算确认的重试上限；
18. 保证任务结束或新任务开始时状态正确清理。

---

# 21. 最终结论

现有 `max_actions` 逻辑本质上是：

```text
主界面挑战按钮的点击尝试次数保护
```

它可以防止无限点击，但不能证明：

```text
点击成功
页面跳转成功
战斗完成
任务完成
```

最可靠的优化方向不是简单把：

```python
max_actions = 1
```

改成：

```python
max_actions = 2
```

而是建立明确的任务状态，并通过页面转换确认每一步是否真正成功：

```text
发出点击
→ 等待页面变化
→ 新页面确认成功
→ 推进任务状态
```

`max_actions` 应退回到“最后一道安全保险”的位置，而不是继续承担任务状态判断职责。
