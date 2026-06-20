# Resource Detector

基于 MuMu 模拟器的手游资源点监控辅助项目。

目标是定时读取资源点列表，识别每个资源点是否被占领、占领者昵称、组织名，并在发现敌方组织占领时提醒。后续可以扩展自动翻页和自动派兵。

## 当前进度

已完成：

- ADB 截图链路
- 固定分辨率截图读取，目标分辨率为 `1280 x 720`
- 8 个资源点 Slot 坐标标定
- Slot 标定工具
- 离线截图检测入口
- 检测结果结构化输出
- 敌我判断配置入口
- RapidOCR 接入和本地截图验证
- 组织名模糊匹配，降低 OCR 小误差影响

待完成：

- 补全每个 Slot 的 `empty_box` / `name_box` / `guild_box`
- 基于 OCR 文本做稳定的空位判断
- 敌方命中后的提醒方式
- 自动翻页和多页扫描

## 文件结构

```text
resource_detector/
├── adb_client.py          # ADB 启动、设备检查、截图
├── detector.py            # Slot 检测、OCR 接口、敌我判断
├── image_io.py            # 本地图片读取，支持 OpenCV / Pillow
├── label_slots.py         # Slot 坐标标定工具
├── main.py                # 命令行入口
├── config.json            # ADB、OCR、己方/敌方组织配置
├── config_slots.json      # Slot 坐标配置
├── requirements.txt
└── screenshots/
    └── test.png
```

## 安装依赖

基础开发依赖：

```powershell
pip install -r requirements.txt
```

如果只用本地截图做无 OCR 检测，也可以只安装 Pillow：

```powershell
pip install pillow
```

## 使用方式

你已经为项目配置了 conda 环境 `DJ`。推荐直接用环境里的 Python：

```powershell
C:\miniconda\envs\DJ\python.exe main.py --image screenshots\test.png
```

也可以使用项目内的便捷脚本：

```powershell
run_dj.bat --image screenshots\test.png
run_dj.bat --image screenshots\test.png --json
```

如果在 Anaconda Prompt 中操作，也可以先激活环境：

```bat
conda activate DJ
python main.py --image screenshots\test.png
```

使用现有截图离线检测：

```powershell
python main.py --image screenshots\test.png
```

输出 JSON：

```powershell
python main.py --image screenshots\test.png --json
```

连接 MuMu 并实时截图检测：

```powershell
python main.py
```

## 日常任务自动化 MVP

新增入口 `daily_tasks.py` 用于识别和执行日常任务闭环：

```powershell
run_dj.bat daily_tasks.py --image C:\path\to\task_page.png
run_dj.bat daily_tasks.py --dry-run
run_dj.bat daily_tasks.py --target 友情点
```

工作流：

- 每轮通过 ADB 截图，并保存到 `task_runs\<run_id>\step_XXX.png`。
- 如果当前不在任务页，且 `task_page.daily_entry_point` 配了坐标，会先点击该入口打开每日任务页。
- 优先用 OCR 和固定区域识别任务标题、进度、`领取` / `前往` 按钮。
- 规则能判断时直接执行：先领奖，再点击未完成任务的 `前往`。
- 规则看不懂时才调用云端视觉模型，要求返回固定 JSON 动作。
- 每一步都会写入 `task_runs\<run_id>\events.jsonl`，用于回放和排查。

默认 `ai.enabled` 为 `false`，只启用规则层和安全停机。要启用云端视觉模型：

```powershell
$env:OPENAI_API_KEY="你的 API Key"
```

然后在 `config.json` 中设置：

```json
"ai": {
    "enabled": true,
    "api_key_env": "OPENAI_API_KEY",
    "base_url": "https://api.openai.com/v1/chat/completions",
    "model": "gpt-4o-mini",
    "timeout_seconds": 45
}
```

安全护栏：

- 仅允许 `tap`、`wait`、`swipe`、`claim`、`stop`；不会发送 Android 返回键 / ESC。
- 低置信度、高风险、越界坐标会停机。
- 识别到 `充值`、`购买`、`钻石`、`商城` 等关键词会停机。
- 连续多步画面不变会停机，避免卡住后重复乱点。
- `--dry-run` 会生成日志但不实际点击，适合先观察 AI 决策。

如果想让它从主界面自动打开任务页，可以先把任务入口坐标填进 `config.json`：

```json
"task_page": {
    "daily_entry_point": {
        "x": 40,
        "y": 280
    }
}
```

坐标需要按你的 MuMu 主界面实际入口微调。

## 配置说明

`config.json`：

- `adb_path`：MuMu 的 `adb.exe` 路径
- `device_id`：模拟器设备 ID，默认 `emulator-5554`
- `ocr_backend`：OCR 后端，目前支持 `none`、`rapidocr` 和 `pytesseract`
- `ocr_min_score`：OCR 文本片段最低置信度
- `name_match_threshold`：昵称模糊匹配阈值
- `guild_match_threshold`：组织名模糊匹配阈值
- `empty_keywords`：空位关键词，默认识别 `未占领`
- `occlusion_keywords`：聊天栏或遮挡关键词
- `ignored_slots`：固定忽略的 Slot，当前默认忽略 `7`，因为左下聊天栏无法去除
- `friendly_guilds`：己方组织名列表
- `enemy_guilds`：敌方组织名列表；仅组织命中不会打，只会标记为 `suspect_enemy_guild`
- `enemy_names`：敌方昵称列表；和 `enemy_guilds` 组合使用
- `enemy_targets`：推荐使用的精确目标列表，必须昵称和组织同时匹配才会标记为 `enemy`
- `alert.show_suspects`：是否显示疑似目标；默认 `false`，正常使用只提醒双命中的 `enemy`
- `task_page`：日常任务页列表区域、按钮关键词和行高配置
- `ai`：云端视觉模型配置；默认关闭，缺少 API Key 时会安全停机
- `guardrails`：自动点击护栏，包括最大步数、超时、禁止关键词、最低置信度
- `known_tasks`：人工命名的任务关键词和备注，用于后续扩展固定流程

敌方目标推荐配置：

```json
"enemy_targets": [
    {
        "name": "敌方昵称",
        "guild": "教练员"
    }
]
```

安全规则：

- `enemy`：昵称和组织都匹配，允许后续提醒或执行动作。
- `suspect_enemy_name` / `suspect_enemy_guild`：只匹配一半，不打，默认不提醒。
- `ignored`：固定忽略的槽位，当前第 7 槽因为聊天栏无法去除而默认跳过。

## 下一步建议

1. 重新标定或补全所有 Slot 的三个文本区域。
2. 用更多截图验证 RapidOCR 在不同背景、角色遮挡、聊天遮挡下的稳定性。
3. 加入提醒模块，例如控制台提示、声音、Windows Toast 或企业微信 webhook。
4. 加入翻页扫描，把每页结果汇总后统一判断。

## 标定流程

先生成当前框位预览：

```bat
run_dj.bat preview_slots.py --image screenshots\test.png
```

输出文件为 `screenshots\slots_preview.png`。颜色含义：

- 绿色：完整资源点区域 `full_box`
- 紫色：未占领文字区域 `empty_box`
- 黄色：昵称区域 `name_box`
- 蓝色：组织区域 `guild_box`

需要手动微调时运行：

```bat
run_dj.bat label_slots.py --image screenshots\test.png
```

标定器快捷键：

- `N` / `P`：切换下一个 / 上一个 Slot
- `1`：完整资源点框
- `2`：未占领文字框
- `3`：昵称框
- `4`：组织框
- 鼠标左键拖拽：覆盖当前 Slot 的当前框
- `S`：保存到 `config_slots.json`
- `Q`：退出

正确框法：

- `empty_box` 只框住“未占领”三个字，尽量不要框到聊天栏或底部按钮。
- `name_box` 从昵称第一个字左侧开始，向右多留一些余量，避免三字昵称或英文昵称被截断。
- `guild_box` 从组织名第一个字左侧开始，向右至少覆盖到完整组织名末尾；宁可稍宽，不要截断。
- 底部 Slot 容易被聊天栏遮挡，标定时最好等聊天栏收起或找一张无遮挡截图。

## 多截图验证

采集多张样本：

```bat
run_dj.bat capture_samples.py --count 10 --delay 2
```

批量验证 OCR：

```bat
run_dj.bat validate_ocr.py --pattern screenshots\samples\*.png
```

验证结果会写入 `ocr_validation.csv`。如果某个 Slot 出现 `occluded`，说明文字区域被聊天栏、弹窗或角色遮挡，建议换一张无遮挡截图或重新调框。

## 扫描策略

默认使用 `scan_mode: fast_fullscreen`：每页只做一次整图 OCR，再把文本按坐标映射回 8 个 Slot。这个模式比逐个 ROI OCR 快很多，适合多页扫描。

安全规则仍然不变：

- 只有列表页同时识别到目标昵称和目标组织，才是 `enemy`。
- 只识别到目标昵称，或者只识别到目标组织，都不自动打。
- 详情页组织排行 top5 只能作为辅助确认，因为它不能证明列表里的目标昵称一定属于该组织。

采集某个 Slot 的详情页截图：

```bat
run_dj.bat detail_probe.py --slot 1 --out screenshots\detail_slot1.png --back
```

拿到详情页截图后，需要再标定“组织排行 top5”区域，才能开发详情页辅助确认。

## OCR 验证结果

当前 `screenshots/test.png` 中，RapidOCR 可以把 4、5、6 号资源点识别为己方组织：

```text
1 empty 未占领
2 empty 未占领
3 empty 未占领
4 friendly AAAB国际财团 -> AAA国际财团
5 friendly AAA国际财团 -> AAA国际财团
6 friendly AAA国际财团 -> AAA国际财团
7 occluded 聊天栏遮挡
8 empty 未占领
```

昵称识别仍有少量误差，后续主要优化方向是重新标定更宽的昵称 ROI，并在需要时加入文本清洗规则。

## 🖥️ 可视化控制台 (Dashboard) 独立脱离运行使用指南

控制台提供了一个完全脱离 AI、对用户十分友好的 Web 图形界面，并支持超参数的滑动配置（例如拉进度条修改竞技场挑战次数等），不需要在终端中输入任何代码命令。

### 1. 启动方式
双击项目根目录下的 **`run_dashboard.bat`** 启动脚本。它将自动在本地后台启动 Web 服务（默认 `7556` 端口），并自动在您的默认浏览器中打开控制台页面：
`http://localhost:7556`

### 2. 界面功能与超参数调节
* **任务控制中心**：点击对应的按钮可以一键执行“友情点赠送”、“高级招募”、“竞技场挑战”或“快速采集资源”任务，也可以一键顺序执行全部任务，随时监控运行 ID、执行步数与日志。
* **日常任务超参数配置**：
  * **竞技场挑战上限 (0 - 15 次)**：直接拖拽滑动条修改，实时展示数值。
  * **高级招募上限 (0 - 10 次)**：直接拖拽滑动条修改。
  * **资源快速采集上限 (0 - 5 次)**：直接拖拽滑动条修改。
  * 调整完毕后，点击 **“保存全局配置”** 即可写入项目配置文件，即时对后续启动的自动化生效。
* **模拟器实时画面**：控制面板支持在空闲和自动执行时，高帧率展示 MuMu 模拟器最新的截图画面。
* **终止当前运行**：在任务执行过程中如果想要退出，点击下方的“终止当前运行”红色按钮即可在当前步骤结束后安全停机。
