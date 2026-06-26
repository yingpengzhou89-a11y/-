import json
import os
import sys
import time
import urllib.parse
import webbrowser
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from ocr_utils import BASE_DIR, load_app_config
from adb_client import capture_screenshot
from task_runner import GuardrailError, TaskRunner, RunLogger
TEMP_SCREENSHOT_DIR = os.path.join(BASE_DIR, "temp_screenshots")

# 全局多设备状态管理
RUNNER_STATES = {}
DEVICE_LOCKS = {}

# 获取或初始化模拟器状态
def get_or_create_device_state(device_id):
    if device_id not in RUNNER_STATES:
        RUNNER_STATES[device_id] = {
            "status": "idle",       # idle, running, blocked, stopped
            "target": "",
            "steps": 0,
            "run_id": "",
            "logs": [],
            "latest_screenshot": "",
            "should_stop": False
        }
    return RUNNER_STATES[device_id]

# 获取设备级别的并发锁
def get_device_lock(device_id):
    if device_id not in DEVICE_LOCKS:
        DEVICE_LOCKS[device_id] = threading.Lock()
    return DEVICE_LOCKS[device_id]

# 静态保存各仪表盘专用的设备临时截图路径
def get_device_screenshot_path(device_id):
    safe_id = device_id.replace(":", "_").replace(".", "_")
    return os.path.join(TEMP_SCREENSHOT_DIR, f"dashboard_temp_{safe_id}.png")

def log_to_device(device_id, message):
    timestamp = time.strftime("%H:%M:%S")
    state = get_or_create_device_state(device_id)
    state["logs"].append(f"[{timestamp}] {message}")
    if len(state["logs"]) > 100:
        state["logs"].pop(0)
    print(f"[{device_id}] [{timestamp}] {message}")

class DashboardLogger(RunLogger):
    """自定义日志处理器，将特定设备的运行事件同步输出至 Web 控制台"""
    def __init__(self, base_dir, run_id, device_id):
        super().__init__(base_dir, run_id)
        self.device_id = device_id
        
    def event(self, event_type, data):
        super().event(event_type, data)
        state = get_or_create_device_state(self.device_id)
        
        if event_type == "step":
            step = data.get("step")
            screenshot = data.get("screenshot")
            decision = data.get("decision", {})
            intent = decision.get("intent", "未知意图")
            action = decision.get("action", "未知动作")
            source = data.get("source", "rules")
            
            # 将具体截图拷至设备的专属临时截图路径下
            device_screenshot = get_device_screenshot_path(self.device_id)
            if screenshot and os.path.exists(screenshot):
                try:
                    import shutil
                    os.makedirs(os.path.dirname(device_screenshot), exist_ok=True)
                    shutil.copy(screenshot, device_screenshot)
                except Exception as e:
                    print(f"[{self.device_id}] 复制运行截图失败: {e}")
            
            state["latest_screenshot"] = device_screenshot
            state["steps"] = step
            
            log_to_device(self.device_id, f"[步骤 {step}] [{source.upper()}] 匹配意图: {intent} -> 执行动作: {action}")
        elif event_type == "blocked":
            reason = data.get("reason", "")
            log_to_device(self.device_id, f"[BLOCKED] 触发护栏安全停机: {reason}")
        elif event_type == "stop":
            reason = data.get("reason", "")
            log_to_device(self.device_id, f"[STOP] 任务正常停止: {reason}")

# 动态代理 TaskRunner 的截图函数以支持设备级别的手动取消
original_capture = TaskRunner.capture
def custom_capture(self, step):
    device_id = self.app_config.get("device_id")
    if device_id:
        state = get_or_create_device_state(device_id)
        if state.get("should_stop"):
            raise GuardrailError("用户手动终止了日常任务")
    return original_capture(self, step)

TaskRunner.capture = custom_capture

def load_dashboard_config(device_id=None):
    """读取主配置文件 config.json 并合并运行时覆盖，且强制关联当前设备实例"""
    config = load_app_config(os.path.join(BASE_DIR, "config.json"))
    if device_id:
        config["device_id"] = device_id
        
    runtime_path = os.path.join(BASE_DIR, "config_runtime_7555.json")
    if os.path.exists(runtime_path):
        try:
            with open(runtime_path, "r", encoding="utf-8") as f:
                runtime_config = json.load(f)
                config.update(runtime_config)
                # 再次强保传入的 device_id 优先
                if device_id:
                    config["device_id"] = device_id
        except Exception as exc:
            print(f"合并 runtime 配置失败: {exc}")
    return config

def capture_idle_screenshot(device_id):
    """空闲时获取一次最新的模拟器画面，用于仪表盘初次加载或手动刷新"""
    try:
        app_config = load_dashboard_config(device_id)
        screenshot_path = get_device_screenshot_path(device_id)
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
        capture_screenshot(
            app_config["adb_path"],
            device_id,
            screenshot_path
        )
        state = get_or_create_device_state(device_id)
        state["latest_screenshot"] = screenshot_path
    except Exception as exc:
        print(f"[{device_id}] 空闲状态截图失败: {exc}")

def run_automation_thread(device_id, tasks, target_task=None, run_peak_arena=True):
    lock = get_device_lock(device_id)
    with lock:
        state = get_or_create_device_state(device_id)
        state["status"] = "running"
        state["steps"] = 0
        state["logs"] = []
        state["should_stop"] = False
        
        if target_task:
            log_to_device(device_id, f"开始独立执行 {target_task} 任务...")
            state["target"] = target_task
        else:
            log_to_device(device_id, "开始一键托管日常任务大循环...")
            state["target"] = "自动托管日常"
        
        app_config = load_dashboard_config(device_id)
        runner = TaskRunner(app_config, BASE_DIR, dry_run=False)
        state["run_id"] = runner.logger.run_id
        
        # 替换为当前设备绑定的日志处理器
        runner.logger = DashboardLogger(BASE_DIR, runner.logger.run_id, device_id)
        
        try:
            result = runner.run(target_task=target_task)
            
            if result.get("status") == "blocked":
                log_to_device(device_id, f"日常大循环触发阻断或发生异常，运行中断。原因: {result.get('reason')}")
                state["status"] = "blocked"
            elif result.get("status") == "stopped":
                reason = result.get("reason")
                if reason == "outside game":
                    log_to_device(device_id, "检测到游戏已退回到桌面，停止日常大循环。")
                elif reason == "commission requires manual work":
                    log_to_device(device_id, "检测到委托任务未完成（需人工手动做完），日常大循环安全挂起。")
                else:
                    log_to_device(device_id, f"日常托管大循环正常运行完毕。结束原因: {reason}")
                state["status"] = "stopped"
            else:
                state["status"] = "stopped"
                log_to_device(device_id, f"日常托管结束，状态: {result.get('status')}")
                
            # 串联巅峰赛自动挑战
            if not target_task and run_peak_arena and state.get("status") == "stopped" and not state.get("should_stop", False):
                log_to_device(device_id, "日常大循环已正常结束，检测到巅峰赛开关开启，开始执行巅峰赛挑战...")
                state["target"] = "巅峰赛挑战"
                state["status"] = "running"
                
                peak_result = runner.run(target_task="巅峰")
                
                if peak_result.get("status") == "blocked":
                    log_to_device(device_id, f"巅峰赛挑战触发阻断或发生异常，运行中断。原因: {peak_result.get('reason')}")
                    state["status"] = "blocked"
                elif peak_result.get("status") == "stopped":
                    reason = peak_result.get("reason")
                    log_to_device(device_id, f"巅峰赛挑战正常运行完毕。结束原因: {reason}")
                    state["status"] = "stopped"
                else:
                    state["status"] = "stopped"
                    log_to_device(device_id, f"巅峰赛挑战结束，状态: {peak_result.get('status')}")
                
            log_to_device(device_id, "日常自动化流水线运行完成。")
        except GuardrailError as exc:
            state["status"] = "blocked"
            log_to_device(device_id, f"日常任务触发安全保护，执行中断。原因: {exc}")
            result = {
                "status": "blocked",
                "reason": str(exc),
                "run_dir": runner.logger.path
            }
            runner.logger.event("blocked", result)
        except Exception as exc:
            state["status"] = "blocked"
            log_to_device(device_id, f"日常任务发生未知异常: {exc}")

def run_peak_arena_thread(device_id):
    lock = get_device_lock(device_id)
    with lock:
        state = get_or_create_device_state(device_id)
        state["status"] = "running"
        state["steps"] = 0
        state["logs"] = []
        state["should_stop"] = False
        
        log_to_device(device_id, "开始执行巅峰赛挑战独立程序...")
        state["target"] = "巅峰赛挑战"
        
        app_config = load_dashboard_config(device_id)
        runner = TaskRunner(app_config, BASE_DIR, dry_run=False)
        state["run_id"] = runner.logger.run_id
        
        runner.logger = DashboardLogger(BASE_DIR, runner.logger.run_id, device_id)
        
        try:
            result = runner.run(target_task="巅峰")
            
            if result.get("status") == "blocked":
                log_to_device(device_id, f"巅峰赛挑战触发阻断或发生异常，运行中断。原因: {result.get('reason')}")
                state["status"] = "blocked"
            elif result.get("status") == "stopped":
                reason = result.get("reason")
                log_to_device(device_id, f"巅峰赛挑战正常运行完毕。结束原因: {reason}")
                state["status"] = "stopped"
            else:
                state["status"] = "stopped"
                log_to_device(device_id, f"巅峰赛挑战结束，状态: {result.get('status')}")
                
            log_to_device(device_id, "巅峰赛独立自动化流水线运行完成。")
        except GuardrailError as exc:
            state["status"] = "blocked"
            log_to_device(device_id, f"运行触发安全保护，执行中断。原因: {exc}")
            result = {
                "status": "blocked",
                "reason": str(exc),
                "run_dir": runner.logger.path
            }
            runner.logger.event("blocked", result)
        except Exception as exc:
            state["status"] = "blocked"
            log_to_device(device_id, f"运行发生未知异常: {exc}")

class DashboardHTTPRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # 屏蔽控制台刷请求日志，保持界面干净
        pass

    # 添加 CORS 头部（通配符）
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

    # 处理预检请求
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        global LATEST_SCREENSHOT_PATH
        parsed_path = urllib.parse.urlparse(self.path)
        
        if parsed_path.path == "/":
            try:
                with open(os.path.join(BASE_DIR, "dashboard.html"), "r", encoding="utf-8") as f:
                    page_content = f.read()
            except Exception as e:
                page_content = f"<h1>无法加载 dashboard.html: {e}</h1>"
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
            self.end_headers()
            self.wfile.write(page_content.encode("utf-8"))
            
        elif parsed_path.path == "/api/status":
            query = urllib.parse.parse_qs(parsed_path.query)
            device_id = query.get("device_id", [None])[0]
            
            if device_id:
                state = get_or_create_device_state(device_id)
                # 过滤 thread 对象
                clean_state = {k: v for k, v in state.items() if k != "thread"}
                res_data = clean_state
            else:
                res_data = {}
                for dev_id, state in RUNNER_STATES.items():
                    res_data[dev_id] = {k: v for k, v in state.items() if k != "thread"}
                    
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(res_data, ensure_ascii=False).encode("utf-8"))
            
        elif parsed_path.path == "/api/device":
            try:
                config_path = os.path.join(BASE_DIR, "config.json")
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                current_device = config.get("device_id", "127.0.0.1:7555")
                
                import subprocess
                adb_path = config.get("adb_path", r"C:\Netease\MuMu\nx_main\adb.exe")
                devices = []
                res = subprocess.run([adb_path, "devices"], capture_output=True, text=True, check=False)
                lines = res.stdout.splitlines()
                for line in lines[1:]:
                    if line.strip() and "\tdevice" in line:
                        device_name = line.split("\t")[0]
                        devices.append(device_name)
                        
                res_data = {
                    "current_device": current_device,
                    "devices": devices
                }
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(res_data, ensure_ascii=False).encode("utf-8"))
            except Exception as exc:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "reason": str(exc)}, ensure_ascii=False).encode("utf-8"))
                
        elif parsed_path.path == "/api/config":
            try:
                config_path = os.path.join(BASE_DIR, "config.json")
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                
                res_data = {
                    "max_free_challenges": config.get("arena", {}).get("max_free_challenges", 5),
                    "max_recruit_actions": config.get("recruitment", {}).get("max_recruit_actions", 2),
                    "max_collect_actions": config.get("warehouse", {}).get("max_collect_actions", 3),
                    "max_refresh_actions": config.get("shop_refresh", {}).get("max_refresh_actions", 2)
                }
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(res_data, ensure_ascii=False).encode("utf-8"))
            except Exception as exc:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "reason": str(exc)}, ensure_ascii=False).encode("utf-8"))
                
        elif parsed_path.path == "/screenshot":
            query = urllib.parse.parse_qs(parsed_path.query)
            device_id = query.get("device_id", [None])[0]
            
            if not device_id:
                try:
                    config = load_dashboard_config(None)
                    device_id = config.get("device_id")
                except Exception:
                    pass
            
            if device_id:
                state = get_or_create_device_state(device_id)
                if state["status"] == "idle":
                    capture_idle_screenshot(device_id)
                
                screenshot_path = state["latest_screenshot"]
                if screenshot_path and os.path.exists(screenshot_path):
                    self.send_response(200)
                    self.send_header("Content-Type", "image/png")
                    self.end_headers()
                    with open(screenshot_path, "rb") as f:
                        self.wfile.write(f.read())
                    return
            
            self.send_response(404)
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        
        if parsed_path.path == "/api/run":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length).decode("utf-8")
            try:
                params = json.loads(post_data) if post_data else {}
            except ValueError:
                params = {}
                
            print(f"[API] Received /api/run request with params: {params}")
            try:
                with open(os.path.join(BASE_DIR, "api_debug.log"), "a", encoding="utf-8") as debug_f:
                    debug_f.write(f"Received /api/run with params: {params}\n")
            except Exception:
                pass
            device_id = params.get("device_id", "").strip()
            if not device_id:
                try:
                    config = load_dashboard_config(None)
                    device_id = config.get("device_id")
                except Exception:
                    pass
            
            if not device_id:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "reason": "未指定有效的模拟器设备"}, ensure_ascii=False).encode("utf-8"))
                return
                
            target = params.get("target", "")
            tasks = params.get("tasks", [])
            
            # 向前兼容旧的 API 传参
            if not tasks and target:
                if target == "全部日常" or target == "":
                    tasks = ["login", "commission", "friendship", "recruitment", "arena", "collect", "donate", "daily_dungeon", "shop_refresh", "memory_house", "kakuja_hunt"]
                else:
                    target_map = {
                        "登录": ["login"],
                        "委托": ["commission"],
                        "友情": ["friendship"],
                        "招募": ["recruitment"],
                        "竞技": ["arena"],
                        "采集": ["collect"],
                        "捐献": ["donate"],
                        "副本": ["daily_dungeon"],
                        "商店": ["shop_refresh"],
                        "回忆": ["memory_house"],
                        "讨伐": ["kakuja_hunt"]
                    }
                    tasks = target_map.get(target, [])
            
            state = get_or_create_device_state(device_id)
            if state["status"] == "running":
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "reason": f"该设备 {device_id} 的日常任务已在运行中"}, ensure_ascii=False).encode("utf-8"))
                return
                
            target_task = params.get("target_task", None)
            run_peak_arena = params.get("run_peak_arena", True)
            if target_task == "巅峰":
                t = threading.Thread(target=run_peak_arena_thread, args=(device_id,))
            else:
                t = threading.Thread(target=run_automation_thread, args=(device_id, tasks, target_task, run_peak_arena))
            t.daemon = True
            t.start()
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True}).encode("utf-8"))
            
        elif parsed_path.path == "/api/stop":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length).decode("utf-8")
            try:
                params = json.loads(post_data) if post_data else {}
            except ValueError:
                params = {}
                
            device_id = params.get("device_id", "").strip()
            if not device_id:
                try:
                    config = load_dashboard_config(None)
                    device_id = config.get("device_id")
                except Exception:
                    pass
            
            if device_id:
                state = get_or_create_device_state(device_id)
                if state["status"] == "running":
                    state["should_stop"] = True
                    log_to_device(device_id, "收到用户终止运行指令，等待当前步骤退出...")
                
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True}).encode("utf-8"))
            
        elif parsed_path.path == "/api/config":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length).decode("utf-8")
            try:
                params = json.loads(post_data) if post_data else {}
            except ValueError:
                params = {}
                
            try:
                config_path = os.path.join(BASE_DIR, "config.json")
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)

                if "arena" not in config:
                    config["arena"] = {}
                config["arena"]["max_free_challenges"] = int(params.get("max_free_challenges", 5))

                if "recruitment" not in config:
                    config["recruitment"] = {}
                config["recruitment"]["max_recruit_actions"] = int(params.get("max_recruit_actions", 2))

                if "warehouse" not in config:
                    config["warehouse"] = {}
                config["warehouse"]["max_collect_actions"] = int(params.get("max_collect_actions", 3))

                if "shop_refresh" not in config:
                    config["shop_refresh"] = {}
                config["shop_refresh"]["max_refresh_actions"] = int(params.get("max_refresh_actions", 2))

                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(config, f, indent=4, ensure_ascii=False)

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": True}).encode("utf-8"))
            except Exception as exc:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "reason": str(exc)}, ensure_ascii=False).encode("utf-8"))
                
        elif parsed_path.path == "/api/device":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length).decode("utf-8")
            try:
                params = json.loads(post_data) if post_data else {}
            except ValueError:
                params = {}
                
            new_device = params.get("device_id", "").strip()
            if not new_device:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "reason": "设备ID不能为空"}, ensure_ascii=False).encode("utf-8"))
                return
                
            try:
                config_path = os.path.join(BASE_DIR, "config.json")
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                
                import subprocess
                adb_path = config.get("adb_path", r"C:\Netease\MuMu\nx_main\adb.exe")
                if ":" in new_device:
                    subprocess.run([adb_path, "connect", new_device], capture_output=True, text=True, check=False)
                
                config["device_id"] = new_device
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(config, f, indent=4, ensure_ascii=False)
                
                # connect 完或切换设备后重新获取截图
                capture_idle_screenshot(new_device)
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": True}).encode("utf-8"))
            except Exception as exc:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "reason": str(exc)}, ensure_ascii=False).encode("utf-8"))
                
        elif parsed_path.path == "/api/device/scan":
            try:
                config_path = os.path.join(BASE_DIR, "config.json")
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                
                adb_path = config.get("adb_path", r"C:\Netease\MuMu\nx_main\adb.exe")
                current_device = config.get("device_id", "127.0.0.1:7555")
                
                # 常见模拟器端口列表（扩充 MuMu12 多开至 7 个实例）
                COMMON_PORTS = [16384, 16416, 16448, 16480, 16512, 16544, 16576, 7555, 5555, 62001, 52001, 21503]
                
                import socket
                import subprocess
                
                open_ports = []
                for port in COMMON_PORTS:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(0.15)
                    try:
                        s.connect(("127.0.0.1", port))
                        open_ports.append(port)
                        s.close()
                    except Exception:
                        pass
                
                for port in open_ports:
                    device_str = f"127.0.0.1:{port}"
                    try:
                        subprocess.run([adb_path, "connect", device_str], capture_output=True, text=True, timeout=2.0)
                    except Exception:
                        pass
                
                # 获取最新的在线设备列表
                devices = []
                res = subprocess.run([adb_path, "devices"], capture_output=True, text=True, check=False)
                lines = res.stdout.splitlines()
                for line in lines[1:]:
                    if line.strip() and "\tdevice" in line:
                        device_name = line.split("\t")[0]
                        devices.append(device_name)
                
                # 自适应绑定逻辑
                new_binding = current_device
                if devices:
                    if current_device not in devices:
                        new_binding = devices[0]
                        config["device_id"] = new_binding
                        with open(config_path, "w", encoding="utf-8") as f:
                            json.dump(config, f, indent=4, ensure_ascii=False)
                        capture_idle_screenshot(new_binding)
                    else:
                        capture_idle_screenshot(new_binding)
                    
                    res_data = {
                        "success": True,
                        "current_device": new_binding,
                        "devices": devices,
                        "scanned_count": len(devices)
                    }
                else:
                    res_data = {
                        "success": False,
                        "reason": "未搜寻到任何活跃的模拟器。请确保您的模拟器（如 MuMu、雷电等）已经处于启动状态。"
                    }
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(res_data, ensure_ascii=False).encode("utf-8"))
            except Exception as exc:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "reason": str(exc)}, ensure_ascii=False).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

def start_server(port=7556):
    server_address = ("", port)
    httpd = ThreadingHTTPServer(server_address, DashboardHTTPRequestHandler)
    print(f"自动肝日常系统 Web 控制面板运行在 http://localhost:{port}")
    
    def async_warmup():
        print("正在后台扫描在线设备并预抓取首张截图...")
        try:
            config = load_dashboard_config(None)
            adb_path = config.get("adb_path", r"C:\Netease\MuMu\nx_main\adb.exe")
            import subprocess
            res = subprocess.run([adb_path, "devices"], capture_output=True, text=True, check=False)
            lines = res.stdout.splitlines()
            for line in lines[1:]:
                if line.strip() and "\tdevice" in line:
                    dev_id = line.split("\t")[0]
                    print(f"正在连接设备 {dev_id} 并抓取首张截图...")
                    capture_idle_screenshot(dev_id)
        except Exception as exc:
            print(f"后台启动首图获取失败: {exc}")
            
    warmup_t = threading.Thread(target=async_warmup)
    warmup_t.daemon = True
    warmup_t.start()
    print(f"请在浏览器中手动打开控制面板: http://localhost:{port}")
    # 避免在无头/非交互式环境下调用浏览器导致主线程死锁挂起
    # webbrowser.open(f"http://localhost:{port}")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n正在关闭 Web 控制面板服务器...")
        httpd.server_close()
        sys.exit(0)

if __name__ == "__main__":
    start_server()
