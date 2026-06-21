# 自动肝日常系统 Web 控制面板 (Daily Task Automation System)

[English](#english) | [中文](#中文-1)

---

## 中文

本项目是一个基于 Python + ADB + OCR 以及原生 HTML5 Web 控制面板的手游日常任务一键自动托管系统。旨在通过自动化流程完成游戏内的重复性日常任务，并提供直观的多设备多开监控面板。

### 主要功能

* **多设备自动搜寻与管理**：支持一键扫描并自动绑定多开的 MuMu 模拟器端口（支持多开实例）。
* **高上限守护线程**：支持长达 200 步的连续决策及 1 小时的安全运行守护，防止在大参数配置下超时中断。
* **核心日常任务覆盖**：
  * 友情点领取与赠送
  * 高级招募十连
  * 资源仓库快速采集
  * 竞技场挑战
  * 日常商店刷新
  * 赫者讨伐
  * 组织金币捐献
  * 日常副本扫荡
  * 日常商店刷新
  * 回忆之屋扫荡
* **实时 Web 控制面板**：提供网页端的画布屏幕投影、运行日志轮询、实时运行状态灯展示以及全局参数配置滑块。

### 项目文件结构 (Clean Architecture)

```text
daily_task/
├── tasks/                 # 核心日常任务功能实现
│   ├── arena.py           # 竞技场挑战
│   ├── daily_dungeon.py   # 日常副本扫荡（支持自适应）
│   ├── recruitment.py     # 招募任务
│   └── warehouse.py       # 资源仓库快速采集
├── web_dashboard.py       # 原生多线程 HTTP 服务器，提供 API 与界面承载
├── task_runner.py         # 托管决策中心，包含安全护栏与逻辑执行流
├── task_detector.py       # 图像文本识别分类与页面检测器
├── ocr_utils.py           # RapidOCR 图像处理与全局配置加载工具库
├── dashboard.html         # 前端精美控制面板（支持多设备 Tab 页、实时日志、画布投影）
├── config.json            # 运行全局配置文件（包含所有坐标与限值参数）
├── run_dashboard.bat      # 【推荐】一键清理并启动 Web 仪表盘控制面板
├── run_dj.bat             # 一键启动命令行模式
└── daily_tasks.py         # 命令行模式执行入口
```

### 前置准备与使用说明

为了确保托管程序能够顺利跑完全程，请在启动托管前在游戏内及控制面板做好以下前置准备：

1. **手动完成委托任务**：由于“接取3次委托任务”存在高随机性，系统在日常任务列表检测到其未做完时会触发安全挂起停机。请务必在启动托管前**人为手动接取并做完委托任务**。
2. **游戏内勾选跳过招募动画**：系统已剔除了自动寻找并勾选招募动画跳过框的操作。请在游戏内的高级招募页面中，**手动勾选“跳过招募动画”**（游戏会自动记住该勾选状态）。
3. **游戏内勾选竞技场自动挑战**：在游戏内竞技场挑战页面，请**手动勾选“自动战斗”**或相关跳过框。
4. **配好控制面板参数**：在 Web 仪表盘的“日常任务参数配置”卡片中，**调好配好那三个日常参数**（竞技场挑战次数、资源快速采集次数、日常商店刷新次数），点击“保存全局配置”后再开始一键托管。

### 运行方式

#### 1. 运行 Web 仪表盘（推荐）
双击运行项目根目录下的 **`run_dashboard.bat`**。它将自动强杀冲突进程，加载最新代码，并在浏览器中自动打开控制面板：
`http://localhost:7556`

#### 2. 命令行独立运行
运行一键批处理文件：
```powershell
./run_dj.bat
```

---

## English

This project is an automated daily task executor and Web Dashboard for mobile games, built on Python, ADB, RapidOCR, and Vanilla HTML5/CSS/JS. It aims to eliminate repetitive daily grinding through decision-making loops and provides a responsive UI to monitor multiple emulator instances.

### Key Features

* **Multi-Instance Auto-Scanning**: One-click scanning to detect and bind active MuMu Emulator ports automatically.
* **Adaptive Dungeon Sweeping**:
  * Triggers "One-key Sweep" if the button is present.
  * Automatically falls back to single sweep coordinates `(858, 666)` for low-combat-power accounts where one-key sweep is not unlocked yet.
* **Extended Safety Guardrails**: Supports up to 200 execution steps and 1 hour of timeout limit per run.
* **Full Daily Automation**:
  * Friendship points gifting and claiming.
  * 10x advanced recruitment (skipping redundant animation checks).
  * Warehouse resource gathering.
  * Arena battles.
  * Shop refreshes and item purchasing.
  * Boss hunt (Kakuja) rewards harvesting.
* **Real-time Web Panel**: Canvas screenshot projections, responsive logs streaming, connection status LEDs, and global parameter configuration sliders.

### Project Directory Structure (Clean Architecture)

```text
daily_task/
├── tasks/                 # Core daily task task modules
│   ├── arena.py           # Arena battle handler
│   ├── daily_dungeon.py   # Dungeon sweep handler (adaptive)
│   ├── recruitment.py     # Recruitment handler
│   └── warehouse.py       # Warehouse collection handler
├── web_dashboard.py       # Multithreaded HTTP Server & Web API endpoints
├── task_runner.py         # Decision pipeline engine with safety limits
├── task_detector.py       # OCR-based page classification and state detector
├── ocr_utils.py           # OCR helpers and configurations parser
├── dashboard.html         # Responsive GUI (multi-device tabs, live logs, canvas projection)
├── config.json            # JSON configs for coordinates, offsets, and thresholds
├── run_dashboard.bat      # [Recommended] One-click script to kill duplicate services and start dashboard
├── run_dj.bat             # Start executor in CLI mode
└── daily_tasks.py         # CLI entrypoint
```

### Prerequisites & Usage Instructions

To ensure the automation script runs smoothly without safety interrupts, please complete the following steps in-game and on the dashboard before starting:

1. **Complete Commission Tasks Manually**: The system will trigger a safety stop if unfinished commission tasks are detected in the daily list. Please **manually accept and finish all 3 commission tasks** before starting.
2. **Check "Skip Recruitment Animation" in Game**: The system no longer automatically checks this box. Please **manually tick the "Skip Animation" checkbox** on the recruitment screen (the game will remember this state).
3. **Check "Auto Battle" in Arena**: Please **manually tick the "Auto Battle" or skip options** in the game's arena interface.
4. **Configure Parameters on Dashboard**: Adjust the **three daily parameters** (Arena challenges, Resource warehouse collection times, and Shop refresh times) in the configuration panel, click "Save global config", and then click "Start".

### Get Started

#### 1. Launch Web Dashboard (Recommended)
Double-click **`run_dashboard.bat`** in the root directory. It will clean up ports conflict, load the latest code, and launch:
`http://localhost:7556`

#### 2. CLI Execution
Run the batch file in PowerShell or Command Prompt:
```powershell
./run_dj.bat
```
