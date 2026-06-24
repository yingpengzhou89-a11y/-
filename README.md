# 自动肝日常系统 Web 控制面板 (Daily Task Automation System)

[English](#english) | [中文](#中文-1)

---

## 中文

本项目是一个基于 Python + ADB + OCR 以及原生 HTML5 Web 控制面板的手游日常任务一键自动托管系统。旨在通过自动化流程完成游戏内的重复性日常任务，并提供直观的多设备多开监控面板。

### 主要功能

* **多设备自动搜寻与管理**：支持一键扫描并自动绑定多开的 MuMu 模拟器端口（支持多开实例）。
* **高上限守护线程**：支持长达 200 步的连续决策及 1 小时的安全运行守护，防止在大参数配置下超时中断。
* **核心任务完全覆盖**：
  * **日常托管大循环**：友情点领取与赠送、高级招募十连、资源仓库快速采集、普通竞技场、日常商店刷新及购买、赫者讨伐、组织金币捐献、日常副本自动扫荡、回忆之屋扫荡。
  * **巅峰竞技场（排位赛）**：从大厅自动路由、智能门票缺额精细计算与购票（防钻石资源浪费）、自动挑战匹配、**4.5秒智能战斗跳过防连点保护锁**、结算返回。
* **实时 Web 控制面板**：网页端画布屏幕投影、运行日志轮询、实时运行状态灯、运行期间按钮置灰保护、**运行目标动态文本解析显示**（如“正在运行: 巅峰赛挑战”）以及全局参数滑块。

### 项目文件结构 (Clean Architecture)

```text
daily_task/
├── tasks/                 # 核心任务功能状态机模块
│   ├── arena.py           # 竞技场挑战
│   ├── daily_dungeon.py   # 日常副本扫荡（支持自适应）
│   ├── recruitment.py     # 招募任务
│   ├── warehouse.py       # 资源仓库快速采集
│   ├── kakuja_hunt.py     # 赫者讨伐
│   └── peak_arena.py      # 巅峰竞技场独立挑战
├── web_dashboard.py       # 原生多线程 HTTP 服务器，提供 API 与界面承载
├── task_runner.py         # 托管决策中心，包含安全护栏与逻辑执行流
├── task_detector.py       # 图像文本识别分类与页面检测器
├── ocr_utils.py           # RapidOCR 图像处理与全局配置加载工具库
├── dashboard.html         # 前端精美控制面板（支持多设备 Tab 页、实时日志、画布投影）
├── config.json            # 运行全局配置文件（包含所有坐标与限值参数）
├── peak_arena_run.py      # 巅峰赛独立命令行执行入口脚本
├── run_dashboard.bat      # 【推荐】一键清理并启动 Web 仪表盘控制面板
├── run_dj.bat             # 一键启动命令行模式（日常大循环）
└── daily_tasks.py         # 命令行模式日常托管执行入口
```

### 前置准备与使用说明

为了确保托管程序能够顺利跑完全程，请在启动托管前在游戏内及控制面板做好以下前置准备：

1. **手动完成委托任务**：由于“接取3次委托任务”存在高随机性，系统在日常任务列表检测到其未做完时会触发安全挂起停机。请务必在启动托管前**人为手动接取并做完委托任务**。
2. **游戏内勾选跳过招募动画**：系统已剔除了自动寻找并勾选招募动画跳过框的操作。请在游戏内的高级招募页面中，**手动勾选“跳过招募动画”**（游戏会自动记住该勾选状态）。
3. **游戏内勾选竞技场自动挑战**：在游戏内竞技场挑战页面，请**手动勾选“自动战斗”**或相关跳过框。
4. **配好控制面板参数**：在 Web 仪表盘的“日常任务参数配置”卡片中，**调好配好那三个日常参数**（竞技场挑战次数、资源快速采集次数、日常商店刷新次数），点击“保存全局配置”后再开始一键托管。

### 初次使用与环境配置步骤

若您是第一次在电脑上部署并运行本项目，请按以下步骤完成初始化配置：

1. **安装环境依赖**：
   - 确保本地已安装 Python 3.10+ 环境（推荐使用 Miniconda/Anaconda 管理）；
   - 在项目根目录下打开终端，执行以下命令安装运行所需的第三方库：
     ```powershell
     pip install -r requirements.txt
     ```
2. **配置安卓模拟器**：
   - 推荐下载并使用 **MuMu 模拟器12**；
   - 必须把模拟器的分辨率设置为 **`1280 x 720`** (DPI 设为 240)；
   - 在模拟器设置中开启 **ADB 调试**。
3. **修改配置文件 (config.json)**：
   - 用文本编辑器打开根目录下的 `config.json`；
   - 将首行的 `"adb_path"` 修改为您本地模拟器 `adb.exe` 的真实绝对路径（Windows 系统下请使用双反斜杠进行路径转义）；
   - 默认的主设备端口 `"device_id"` 设为 `127.0.0.1:7555`。若端口不同，可直接通过网页控制台扫描检测。
4. **启动游戏**：
   - 在模拟器内启动游戏，登录好并保持在游戏主城（或任意正常游戏页面）。

### 运行方式

#### 1. 运行 Web 仪表盘（推荐）
双击运行项目根目录下的 **`run_dashboard.bat`**。它将自动强杀冲突进程，加载最新代码，并在浏览器中自动打开控制面板：
`http://localhost:7556`

#### 2. 命令行独立运行（日常大循环）
运行一键批处理文件：
```powershell
./run_dj.bat
```

#### 3. 命令行独立运行（巅峰竞技场）
如果您需要直接通过命令行拉起独立的巅峰赛自动化流程，可激活 conda 环境后直接执行：
```powershell
python peak_arena_run.py
```

---

## English

This project is an automated daily task executor and Web Dashboard for mobile games, built on Python, ADB, RapidOCR, and Vanilla HTML5/CSS/JS. It aims to eliminate repetitive daily grinding through decision-making loops and provides a responsive UI to monitor multiple emulator instances.

### Key Features

* **Multi-Instance Auto-Scanning**: One-click scanning to detect and bind active MuMu Emulator ports automatically.
* **Extended Safety Guardrails**: Supports up to 200 execution steps and 1 hour of timeout limit per run.
* **Full Task Automation**:
  * **Daily Tasks Loop**: Friendship points gifting and claiming, 10x advanced recruitment, warehouse resource gathering, arena battles, shop refreshes & purchases, boss hunt (Kakuja) rewards harvesting, guild gold donations, adaptive dungeon sweeps, and memory house sweeps.
  * **Independent Peak Arena**: Dedicated routine flow starting directly from the lobby, precise ticket calculation and purchasing (safety coordinate `(800, 650)` to prevent diamond wastes), queue matches, **4.5s skip-button safety delay locks**, and rewards claiming.
* **Real-time Web Panel**: Canvas screen projection, log streaming, connection status LEDs, button disable protection, **dynamic running target labels** (e.g. "Running: Peak Arena Challenge"), and global configuration sliders.

### Project Directory Structure (Clean Architecture)

```text
daily_task/
├── tasks/                 # Core daily task task modules
│   ├── arena.py           # Arena battle handler
│   ├── daily_dungeon.py   # Dungeon sweep handler (adaptive)
│   ├── recruitment.py     # Recruitment handler
│   ├── warehouse.py       # Warehouse collection handler
│   ├── kakuja_hunt.py     # Boss hunt (Kakuja) handler
│   └── peak_arena.py      # Independent Peak Arena task handler
├── web_dashboard.py       # Multithreaded HTTP Server & Web API endpoints
├── task_runner.py         # Decision pipeline engine with safety limits
├── task_detector.py       # OCR-based page classification and state detector
├── ocr_utils.py           # OCR helpers and configurations parser
├── dashboard.html         # Responsive GUI (multi-device tabs, live logs, canvas projection)
├── config.json            # JSON configs for coordinates, offsets, and thresholds
├── peak_arena_run.py      # Independent Peak Arena CLI runner
├── run_dashboard.bat      # [Recommended] One-click script to kill duplicate services and start dashboard
├── run_dj.bat             # Start daily loop in CLI mode
└── daily_tasks.py         # Daily loop CLI entrypoint
```

### Prerequisites & Usage Instructions

To ensure the automation script runs smoothly without safety interrupts, please complete the following steps in-game and on the dashboard before starting:

1. **Complete Commission Tasks Manually**: The system will trigger a safety stop if unfinished commission tasks are detected in the daily list. Please **manually accept and finish all 3 commission tasks** before starting.
2. **Check "Skip Recruitment Animation" in Game**: The system no longer automatically checks this box. Please **manually tick the "Skip Animation" checkbox** on the recruitment screen (the game will remember this state).
3. **Check "Auto Battle" in Arena**: Please **manually tick the "Auto Battle" or skip options** in the game's arena interface.
4. **Configure Parameters on Dashboard**: Adjust the **three daily parameters** (Arena challenges, Resource warehouse collection times, and Shop refresh times) in the configuration panel, click "Save global config", and then click "Start".

### First-time Setup Guide

If you are running this project for the first time, please follow the steps below:

1. **Install Dependencies**:
   - Ensure Python 3.10+ is installed on your local environment (Miniconda/Anaconda is highly recommended).
   - Install required packages by running:
     ```powershell
     pip install -r requirements.txt
     ```
2. **Configure Emulator**:
   - We recommend downloading and installing **MuMu Player 12**.
   - Make sure to set the emulator resolution to exactly **`1280 x 720`** (DPI 240).
   - Enable **ADB debugging** in your emulator's settings.
3. **Update config.json**:
   - Open `config.json` in the root directory.
   - Change the first line `"adb_path"` to the actual absolute path of your emulator's `adb.exe` (use double backslashes in Windows to escape).
   - Set the default `"device_id"` to `127.0.0.1:7555`. If you run other emulators, you can search and bind emulator ports dynamically via the Web Dashboard.
4. **Start the Game**:
   - Launch your game in the emulator, log in, and stay on the main city interface (or any playable page).

### Get Started

#### 1. Launch Web Dashboard (Recommended)
Double-click **`run_dashboard.bat`** in the root directory. It will clean up ports conflict, load the latest code, and launch:
`http://localhost:7556`

#### 2. CLI Execution (Daily Tasks Loop)
Run the batch file in PowerShell or Command Prompt:
```powershell
./run_dj.bat
```

#### 3. CLI Execution (Peak Arena)
If you wish to execute the Peak Arena challenge automation task directly from Command Line:
```powershell
python peak_arena_run.py
```
