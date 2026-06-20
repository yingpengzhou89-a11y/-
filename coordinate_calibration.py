import os
import sys
import argparse
import json
import cv2
import numpy as np

# 将当前目录加入模块搜索路径，确保可以正确导入同目录的 adb_client
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from adb_client import capture_screenshot

def load_config(config_path):
    config = {}
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            try:
                config = json.load(f)
            except Exception as e:
                print(f"解析主配置文件失败: {e}")
                
    # 动态搜寻并合并最新的 config_runtime_*.json 配置文件
    import glob
    runtime_files = sorted(glob.glob("config_runtime_*.json"))
    if runtime_files:
        latest_runtime = runtime_files[-1]
        print(f"检测到运行时配置文件: {latest_runtime}，自动进行覆盖合并。")
        try:
            with open(latest_runtime, "r", encoding="utf-8") as f:
                runtime_config = json.load(f)
                config.update(runtime_config)
        except Exception as e:
            print(f"合并运行时配置 {latest_runtime} 失败: {e}")
            
    return config

def get_latest_fallback_screenshot():
    runs_dir = "task_runs"
    if os.path.exists(runs_dir):
        # 寻找最新生成的任务运行目录
        subdirs = sorted([d for d in os.listdir(runs_dir) if d.startswith("2026")])
        if subdirs:
            latest_dir = subdirs[-1]
            img_dir = os.path.join(runs_dir, latest_dir)
            pngs = sorted([f for f in os.listdir(img_dir) if f.endswith(".png")])
            if pngs:
                return os.path.join(img_dir, pngs[-1])
    
    # 如果 task_runs 中没有，寻找 screenshots 文件夹
    screen_dir = "screenshots"
    if os.path.exists(screen_dir):
        pngs = sorted([f for f in os.listdir(screen_dir) if f.endswith(".png")])
        if pngs:
            return os.path.join(screen_dir, pngs[-1])
            
    return None

def main():
    parser = argparse.ArgumentParser(description="交互式 1280x720 坐标标定工具")
    parser.add_argument("--config", type=str, default="config.json", help="指定配置文件路径 (如 config_runtime_7555.json)")
    args = parser.parse_args()

    config = load_config(args.config)
    adb_path = config.get("adb_path", r"C:\Netease\MuMu\nx_main\adb.exe")
    device_id = config.get("device_id", "127.0.0.1:16416") # 默认当前在线的 16416 端口

    print(f"正在尝试从配置 '{args.config}' 获取 adb_path: {adb_path}, device_id: {device_id}")
    
    img = None
    # 尝试使用 ADB 实时截屏
    try:
        print("尝试连接模拟器并获取实时截图...")
        img = capture_screenshot(adb_path, device_id)
        print("成功获取实时截图！")
    except Exception as e:
        print(f"实时 ADB 截图失败 ({e})，连接设备 ID 为: {device_id}。正在尝试寻找本地历史截图...")
        fallback_path = get_latest_fallback_screenshot()
        if fallback_path:
            print(f"正在加载最新本地截图: {fallback_path}")
            img = cv2.imread(fallback_path)
        else:
            print("错误: 无法获取任何截图。请确保模拟器已开机或 task_runs 目录下存在截图文件。")
            return

    if img is None:
        print("错误: 无法读取图像数据。")
        return

    h, w = img.shape[:2]
    # 若图片不是 1280x720，等比缩放到 1280x720 使得用户点击返回的是控制逻辑直接可用的绝对逻辑坐标
    if w != 1280 or h != 720:
        print(f"检测到截图物理尺寸为 {w}x{h}，正在自动缩放为标准 1280x720 逻辑坐标系展示...")
        img = cv2.resize(img, (1280, 720))
    else:
        print("截图物理尺寸已是标准的 1280x720。")

    img_disp = img.copy()
    window_name = "Calibration Tool - ESC or Q to exit"

    def on_mouse(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            print(f"\n[标定成功] 鼠标点击坐标 -> x: {x}, y: {y}")
            print(f"可以直接复制粘贴到代码中: {{\"x\": {x}, \"y\": {y}}}")
            # 在画面上实时绘制一个准星圆圈和文字标识
            cv2.circle(img_disp, (x, y), 6, (0, 0, 255), 2)
            cv2.circle(img_disp, (x, y), 1, (0, 0, 255), -1)
            # 绘制文字阴影以增加清晰度
            cv2.putText(img_disp, f"({x}, {y})", (x + 11, y + 6), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(img_disp, f"({x}, {y})", (x + 10, y + 5), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 1, cv2.LINE_AA)
            cv2.imshow(window_name, img_disp)

    # 创建交互窗口并绑定鼠标事件
    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, on_mouse)
    cv2.imshow(window_name, img_disp)
    
    print("\n" + "="*80)
    print(" 交互坐标标定工具启动成功！")
    print("="*80)
    print(" 1. 请把模拟器界面切换到你要标定按钮的界面。")
    print(" 2. 在弹出的图片窗口中，直接【鼠标左键点击】按钮中心。")
    print(" 3. 终端命令行窗口将实时显示并打印 1280x720 格式的精准坐标。")
    print(" 4. 按键盘【ESC】或【Q】键，或直接点击窗口的关闭按钮退出。")
    print("="*80 + "\n")
    
    while True:
        key = cv2.waitKey(100) & 0xFF
        if key == 27 or key == ord('q') or key == ord('Q'):
            break
        # 允许 OpenCV 处理窗口关闭事件
        if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
            break
            
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
