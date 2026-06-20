from ocr_utils import normalize_box, normalize_text, rapidocr_items


DEFAULT_TASK_CONFIG = {
    "task_list_region": {
        "x1": 315,
        "y1": 225,
        "x2": 1190,
        "y2": 650
    },
    "row_height": 127,
    "task_text_x": 520,
    "button_region_x1": 950,
    "claim_keywords": [
        "领取",
        "一键领取"
    ],
    "go_keywords": [
        "前往"
    ],
    "completed_progress_keywords": [
        "1/1",
        "3/3",
        "5/5"
    ],
    "daily_tab_keywords": [
        "日常任务"
    ],
    "reward_popup_keywords": [
        "恭喜获得",
        "点击任意区域关闭"
    ]
}


def merge_task_config(app_config):
    config = dict(DEFAULT_TASK_CONFIG)
    config.update(app_config.get("task_page") or {})
    return config


def item_in_box(item, box):
    return box.x1 <= item["x"] <= box.x2 and box.y1 <= item["y"] <= box.y2


def row_index_for_item(item, top, row_height):
    return int((item["y"] - top) // row_height)


def text_contains_any(text, keywords):
    normalized = normalize_text(text)
    return any(normalize_text(keyword) in normalized for keyword in keywords)


def progress_is_done(progress):
    if not progress or "/" not in progress:
        return False

    left, right = progress.split("/", 1)

    try:
        return int(left) >= int(right) and int(right) > 0
    except ValueError:
        return False


def title_required_count(title):
    compact = title.replace(" ", "")
    marker = "次"
    index = compact.find(marker)

    if index <= 0:
        return None

    digits = []
    cursor = index - 1

    while cursor >= 0 and compact[cursor].isdigit():
        digits.append(compact[cursor])
        cursor -= 1

    if not digits:
        return None

    return int("".join(reversed(digits)))


def progress_left_value(progress):
    if not progress or "/" not in progress:
        return None

    left, _ = progress.split("/", 1)

    try:
        return int(left)
    except ValueError:
        return None


def task_is_done(title, progress):
    required = title_required_count(title)
    left = progress_left_value(progress)

    if required is not None and left is not None:
        return left >= required

    return progress_is_done(progress)


def extract_progress(text):
    compact = text.replace(" ", "")

    for index, char in enumerate(compact):
        if char != "/":
            continue

        left = []
        right = []
        cursor = index - 1

        while cursor >= 0 and compact[cursor].isdigit():
            left.append(compact[cursor])
            cursor -= 1

        cursor = index + 1

        while cursor < len(compact) and compact[cursor].isdigit():
            right.append(compact[cursor])
            cursor += 1

        if left and right:
            return f"{''.join(reversed(left))}/{''.join(right)}"

    return ""


def classify_button(text, task_config):
    if text_contains_any(text, ["已领取"]):
        return "claimed"

    if text_contains_any(text, task_config["claim_keywords"]):
        return "claim"

    if text_contains_any(text, task_config["go_keywords"]):
        return "go"

    return "unknown"


def detect_task_page(image, app_config):
    task_config = merge_task_config(app_config)
    region = normalize_box(task_config["task_list_region"])
    items = rapidocr_items(image, app_config)
    page_text = "".join(item["text"] for item in items)
    rows = {}

    for item in items:
        if not item_in_box(item, region):
            continue

        index = row_index_for_item(item, region.y1, int(task_config["row_height"]))
        rows.setdefault(index, []).append(item)

    tasks = []

    for index in sorted(rows):
        row_items = sorted(rows[index], key=lambda item: (round(item["y"] / 10), item["x"]))
        row_text = "".join(item["text"] for item in row_items)
        title_items = [
            item for item in row_items
            if item["x"] >= int(task_config["task_text_x"])
            and item["x"] < int(task_config["button_region_x1"])
            and "/" not in item["text"]
        ]
        button_items = [
            item for item in row_items
            if item["x"] >= int(task_config["button_region_x1"])
        ]
        # 计算标题的平均 y 坐标，用于过滤掉跨行混入的杂质按钮
        title_y = None
        if title_items:
            title_y = sum(item["y"] for item in title_items) / len(title_items)
            
        if title_y is not None:
            button_items = [
                item for item in button_items
                if abs(item["y"] - title_y) < 50
            ]
        progress = extract_progress(row_text)
        title = "".join(item["text"] for item in title_items).strip()
        button_text = "".join(item["text"] for item in button_items).strip()
        button_state = classify_button(button_text, task_config)
        center_y = region.y1 + index * int(task_config["row_height"]) + int(task_config["row_height"]) / 2
        best_y = int(center_y)
        if button_items:
            valid_button_items = [
                item for item in button_items
                if text_contains_any(item["text"], task_config["go_keywords"] + task_config["claim_keywords"] + ["已领取", "领取", "前往"])
            ]
            if valid_button_items:
                best_y = int(sum(item["y"] for item in valid_button_items) / len(valid_button_items))
            else:
                best_y = int(sum(item["y"] for item in button_items) / len(button_items))
        task = {
            "row": index,
            "title": title or row_text,
            "progress": progress,
            "done": task_is_done(title or row_text, progress),
            "button_text": button_text,
            "button_state": button_state,
            "action_point": {
                "x": 1068,
                "y": best_y
            },
            "raw_text": row_text
        }

        if task["done"] and task["button_state"] == "unknown":
            task["button_state"] = "claimed"

        if task["title"] or task["progress"] or task["button_text"]:
            tasks.append(task)

    return {
        "is_task_page": text_contains_any(page_text, task_config["daily_tab_keywords"]),
        "page_text": page_text,
        "tasks": tasks,
        "items": items
    }
