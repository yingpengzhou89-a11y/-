import json
import os

from ocr_utils import BASE_DIR, find_adb_path


CONFIG_PATH = os.path.join(BASE_DIR, "config.json")


def normalize_input(raw):
    return (raw or "").strip().strip('"').strip("'")


def resolve_adb_path(user_input):
    value = normalize_input(user_input)
    if not value:
        return find_adb_path()

    expanded = os.path.abspath(os.path.expandvars(os.path.expanduser(value)))

    if os.path.isfile(expanded):
        return expanded

    candidates = [
        os.path.join(expanded, "adb.exe"),
        os.path.join(expanded, "shell", "adb.exe"),
        os.path.join(expanded, "nx_main", "adb.exe"),
    ]

    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate

    # Return the most likely path to make the error message concrete.
    return candidates[0]


def main():
    print("MuMu / ADB configuration")
    print("=" * 40)
    print("请输入 MuMu 模拟器目录，例如：")
    print(r"  C:\Netease\MuMu\nx_main")
    print("如果不确定，可以直接回车，程序会尝试自动查找 ADB。")
    print()

    user_input = input("MuMu 目录或 adb.exe 完整路径：")
    adb_path = resolve_adb_path(user_input)

    if not os.path.exists(adb_path):
        print()
        print(f"[WARN] 未找到 ADB：{adb_path}")
        print("仍会把该路径写入 config.json；如果后续自检失败，请重新运行 install.bat 并输入正确目录。")
    else:
        print()
        print(f"[OK] ADB 路径：{adb_path}")

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    config["adb_path"] = adb_path

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

    print("[OK] 已更新 config.json 中的 adb_path")


if __name__ == "__main__":
    main()
