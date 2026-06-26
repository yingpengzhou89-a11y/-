# 他人电脑部署说明

这个项目现在推荐按下面流程部署，不要再全局 `pip install`。

## 1. 解压项目

把整个项目文件夹放到一个简单路径，例如：

```text
D:\daily_task
```

尽量不要放在带特殊符号、中文过多或网盘同步目录里。

## 2. 安装依赖

双击：

```text
install.bat
```

它会自动：

- 创建项目内虚拟环境 `.venv`
- 安装 `requirements.txt`
- 使用清华 pip 源
- 提示输入 MuMu 模拟器目录，并更新 `config.json` 里的 `adb_path`
- 运行环境自检

当它提示输入 MuMu 目录时，可以填写类似：

```text
C:\Netease\MuMu\nx_main
```

也可以直接填写 `adb.exe` 的完整路径：

```text
C:\Netease\MuMu\nx_main\adb.exe
```

如果不确定，直接回车，程序会尝试自动查找 ADB。

如果安装失败，窗口会停住。把窗口里的报错截图发给维护者。

## 3. 启动模拟器和游戏

先打开 MuMu / 雷电 / 其他安卓模拟器，并进入游戏主界面。

## 4. 启动 Web 面板

双击：

```text
run_dashboard.bat
```

正常启动后，命令行窗口会一直开着，并提示：

```text
http://localhost:7556
```

用浏览器打开这个地址。

## 5. 绑定设备

如果网页没自动识别设备：

1. 确认模拟器已经启动；
2. 点击网页里的设备扫描/绑定功能；
3. 如果仍失败，重新运行 `install.bat`，输入正确的 MuMu 目录。

## 常见问题

### 双击后一闪而过

不要直接猜。请在项目目录空白处 Shift + 右键，打开终端，然后运行：

```bat
run_dashboard.bat
```

窗口会停住，复制报错内容。

### No module named xxx

说明依赖没有装到当前 Python。重新运行：

```bat
install.bat
```

### Python was not found

安装 Python 3.9+，安装时勾选 Add Python to PATH，然后重新运行：

```bat
install.bat
```

### ADB 路径不存在

检查模拟器是否安装。然后重新运行：

```bat
install.bat
```

在提示中输入 MuMu 模拟器目录或 `adb.exe` 完整路径。

常见路径：

```text
C:\Netease\MuMu\nx_main\adb.exe
C:\Program Files\Netease\MuMuPlayer-12.0\shell\adb.exe
C:\Program Files\BlueStacks_nxt\HD-Adb.exe
C:\LDPlayer\LDPlayer9\adb.exe
```

### 未检测到在线设备

先启动模拟器，再运行：

```bat
.venv\Scripts\python.exe check_env.py
```

如果仍没有设备，打开网页后尝试扫描常见端口。

### 端口 7556 被占用

可能已经启动过 dashboard。先关闭旧窗口，或者在任务管理器里结束旧的 Python 进程。
