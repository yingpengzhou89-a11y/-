# CHANGELOG

## [Unreleased] - 2026-06-21 22:43:00 (CST)

### Added
- `c:/Users/work/Desktop/daily_task/test_swipe.py` L1-103 (`+103 -0`) (Create interactive test_swipe.py utility for scroll coordinates and speeds fine-tuning)

### Fixed
- `c:/Users/work/Desktop/daily_task/task_runner.py` L653-1201 -> L653-1205 (`+7 -3`) (Define kakuja_hunt_loading and add it to transition routes)
- `c:/Users/work/Desktop/daily_task/tasks/kakuja_hunt.py` L8 -> L8-18 (`+10 -0`) (Add kakuja_hunt_loading transitional wait to prevent lobby fallback)

## [Unreleased] - 2026-06-21 21:20:00 (CST)

### Fixed
- `c:/Users/work/Desktop/daily_task/tasks/arena.py` L68 (`+1 -1`) (Isolate arena free challenges count with after_intent filter)
- `c:/Users/work/Desktop/daily_task/tasks/daily_dungeon.py` L21 (`+1 -1`) (Isolate daily_dungeon sweep count with after_intent filter)
- `c:/Users/work/Desktop/daily_task/tasks/kakuja_hunt.py` L58 (`+1 -1`) (Isolate kakuja_hunt action count with after_intent filter)
- `c:/Users/work/Desktop/daily_task/tasks/memory_house.py` L19 (`+1 -1`) (Isolate memory_house sweep count with after_intent filter)
- `c:/Users/work/Desktop/daily_task/tasks/resource_warehouse.py` L11 (`+1 -1`) (Isolate resource_warehouse collect count with after_intent filter)
- `c:/Users/work/Desktop/daily_task/tasks/shop_refresh.py` L19 (`+1 -1`) (Isolate shop_refresh count with after_intent filter)

## [Unreleased] - 2026-06-21 20:58:00 (CST)

### Changed
- `c:/Users/work/Desktop/daily_task/task_runner.py` L895-910 -> L900-905 (`+5 -5`) (Increase max everyday tasks list scrolls from 4 to 8 to avoid premature stop before bottom tasks show up)

## [Unreleased] - 2026-06-21 20:20:00 (CST)

### Fixed
- `c:/Users/work/Desktop/daily_task/task_detector.py` L155-195 -> L155-213 (`+29 -11`) (Replace fixed-height row slicing with dynamic Y-clustering to group text items of task page adaptively)
- `c:/Users/work/Desktop/daily_task/task_runner.py` L244-1020 -> L244-1024 (`+7 -1`) (Fix premature claim by introducing local daily_page_swipe_count to isolate scrolling count from cumulative global run history)

## [Unreleased] - 2026-06-21 19:13:00 (CST)

### Changed
- `c:/Users/work/Desktop/daily_task/task_runner.py` L829-1016 -> L829-1011 (`+121 -126`) (Refactor daily tasks page decision tree to delay task rewards claiming until all possible routine tasks are completed or list scrolling reaches its limit)

## [Unreleased] - 2026-06-21 17:29:00 (CST)

### Changed
- `c:/Users/work/Desktop/daily_task/config.json` L251-252 -> L251-252 (`+2 -2`) (Increase max_steps_per_task from 100 to 200, and max_run_seconds from 2700 to 3600)
- `c:/Users/work/Desktop/daily_task/dashboard.html` L581 -> L581 (`+1 -1`), L620-633 -> L620-641 (`+22 -14`) (Add flex-grow:1 to config card for bottom alignment, and update instructions text)
- `c:/Users/work/Desktop/daily_task/README.md` L47-113 -> L47-131 (`+18 -0`) (Add bilingual prerequisites instructions for daily dungeon, recruitment and configuration)
- `c:/Users/work/Desktop/daily_task/README.md` L1-310 -> L1-112 (`+112 -310`) (Rewrite outdated resource detector README to bilingual daily task automation instructions)
- `c:/Users/work/Desktop/daily_task/task_runner.py` L17-18 -> L17-18 (`+2 -2`) (Increase default max_steps_per_task to 200 and max_run_seconds to 3600)
- `c:/Users/work/Desktop/daily_task/task_runner.py` L321-331 -> (Deleted) (`+0 -11`) (Remove check and action for checking and clicking checkSkipAnimation checkbox)
- `c:/Users/work/Desktop/daily_task/task_runner.py` L519 -> (Deleted) (`+0 -1`) (Remove "勾选跳过招募动画" from whitelist)
- `c:/Users/work/Desktop/daily_task/tasks/recruitment.py` L31-42 -> (Deleted) (`+0 -12`) (Remove recruitment "勾选跳过招募动画" branch logic)

## [Unreleased] - 2026-06-21 16:42:00 (CST)

### Fixed
- `c:/Users/work/Desktop/daily_task/tasks/daily_dungeon.py` L3-8 -> L3-11 (`+2 -0`) (Fix NameError by correctly importing text_contains_any and extracting page_text from observation object)

## [Unreleased] - 2026-06-21 14:52:00 (CST)

### Changed
- `c:/Users/work/Desktop/daily_task/tasks/resource_warehouse.py` L10-69 -> (Deleted) (`+0 -60`) (Remove all diamond checks and 80 diamonds safety rails to simplify resource warehouse collection script)
- `c:/Users/work/Desktop/daily_task/run_dashboard.bat` L3-6 (`+4 -0`) (Inject automated cleanup for background web_dashboard.py python processes to prevent ports conflict)
- `c:/Users/work/Desktop/daily_task/config.json` L247 -> L247 (`+1 -1`) (Increase max_steps_per_task from 50 to 100 to avoid premature guardrail exits)
- `c:/Users/work/Desktop/daily_task/task_runner.py` L17 -> L17 (`+1 -1`) (Increase default max_steps_per_task from 20 to 100)
- `c:/Users/work/Desktop/daily_task/config.json` L248 -> L248 (`+1 -1`) (Increase max_run_seconds from 900 to 2700 to prevent execution timeout)
- `c:/Users/work/Desktop/daily_task/task_runner.py` L18 -> L18 (`+1 -1`) (Increase default max_run_seconds from 900 to 2700)
- `c:/Users/work/Desktop/daily_task/config.json` L217 -> L217 (`+4 -0`) (Add single_sweep_point coordinate to daily_dungeon)
- `c:/Users/work/Desktop/daily_task/task_runner.py` L133 -> L133 (`+1 -0`) (Add single_sweep_point default value to DEFAULT_DAILY_DUNGEON_CONFIG)
- `c:/Users/work/Desktop/daily_task/tasks/daily_dungeon.py` L31-36 -> L31-41 (`+7 -2`) (Automatically switch to single_sweep_point when one-key sweep is not unlocked, matching only precise long term "一键扫荡" to prevent false positives)
- `c:/Users/work/Desktop/daily_task/dashboard.html` L531-576 -> L531-572 (`+7 -11`) (Relocate btnScanDevice to the button group and hide the emulator connect manager card to simplify UI without breaking JS references)

## [Unreleased] - 2026-06-21 03:15:00 (CST)

### Changed
- `c:/Users/work/Desktop/daily_task/config.json` L85-88 -> L85-88 (`+2 -2`), L126-133 -> (Deleted) (`+0 -8`), L144-156 -> (Deleted) (`+0 -13`) (Update recruitment 10x position and remove unused arena coordinates)
- `c:/Users/work/Desktop/daily_task/task_runner.py` L56 -> L56 (`+1 -1`), L69-76 -> L69-72 (`+0 -4`), L401-418 -> (Deleted) (`+0 -17`), L469-482 -> (Deleted) (`+0 -13`), L512-529 -> (Deleted) (`+0 -17`), L876-900 -> (Deleted) (`+0 -24`) (Update recruitment 10x default coordinate, delete unused arena coordinates, and remove logic for one-key battle, auto battle checkbox, sub-arena navigation, member customer service popup, and activity ranking popup)
- `c:/Users/work/Desktop/daily_task/tasks/arena.py` L117-136 -> (Deleted) (`+0 -20`) (Remove local_keywords and main_keywords sub-arena navigation branching)

## [Unreleased] - 2026-06-21 03:07:00 (CST)

### Changed
- `c:/Users/work/Desktop/daily_task/tasks/recruitment.py` L10-23 -> (Deleted) (`+0 -14`) (Delete redundant confirm_point logic)
- `c:/Users/work/Desktop/daily_task/config.json` L89-92 -> (Deleted) (`+0 -4`) (Remove confirm_point coordinates)
- `c:/Users/work/Desktop/daily_task/task_runner.py` L57 -> (Deleted) (`+0 -1`) (Remove confirm_point from default recruitment config)

## [Unreleased] - 2026-06-21 02:49:00 (CST)

### Changed
- `c:/Users/work/Desktop/daily_task/task_runner.py` L611-620 -> L611-621 (`+1 -0`) (Whitelist all recruitment intents in validate_decision to bypass forbidden keyword checks on summon pages)

## [Unreleased] - 2026-06-21 02:41:00 (CST)

### Changed
- `c:/Users/work/Desktop/daily_task/task_runner.py` L1284-1309 -> L1284-1300 (`+17 -26`) (Restore missing def check_unchanged method definition to fix AttributeError)

## [Unreleased] - 2026-06-21 02:38:00 (CST)

### Changed
- `c:/Users/work/Desktop/daily_task/task_runner.py` L1013-1027 -> L1013-1025 (`+13 -15`) (Restore active_points >= 100 gate to only claim chests when active points reaches 100)

## [Unreleased] - 2026-06-21 02:26:00 (CST)

### Changed
- `c:/Users/work/Desktop/daily_task/task_runner.py` L651-689 -> L651-688 (`+38 -39`) (Restore execute_decision block to fix syntax error caused by HTML tags corruption), L995 -> L994 (`+1 -1`) (Remove has_go_task condition to allow claiming active points chests even when some tasks remain incomplete)

## [Unreleased] - 2026-06-21 02:05:00 (CST)

### Changed
- `c:/Users/work/Desktop/daily_task/task_runner.py` L1107-1288 -> L1107-1288 (`+182 -182`) (Fix corrupted non-ASCII Chinese text and comments under target selection branch, preventing kakuja_hunt misidentification)
- `c:/Users/work/Desktop/daily_task/run_dj.bat` L5 -> L5-6 (`+1 -0`) (Inject PYTHONUTF8=1 to batch script environment to ensure Python uses UTF-8 decoding for files by default)
- `c:/Users/work/Desktop/daily_task/run_dashboard.bat` L3 -> L3-4 (`+1 -0`) (Inject PYTHONUTF8=1 to dashboard batch script to fix multi-instance OCR decoding)

## [Unreleased] - 2026-06-21 00:36:00 (CST)

### Changed
- `c:/Users/work/Desktop/daily_task/web_dashboard.py` L13-16 -> L13-17 (`+1 -0`) (Define TEMP_SCREENSHOT_DIR globally to resolve NameError in logging handler), L500-502 -> L500-502 (`+1 -1`) (Extend COMMON_PORTS list to scan up to 7 MuMu12 multi-instances, resolving 3rd instance offline issue)
- `c:/Users/work/Desktop/daily_task/dashboard.html` L654-960 -> L654-986 (`+31 -10`) (Refactor JS controllers to fully support dynamic tabs rendering, independent status polling, log routing, and parameter encapsulation per device_id)
- `c:/Users/work/Desktop/daily_task/task_runner.py` L611-620 -> L611-621 (`+1 -0`) (Add recruitment to skip_forbidden_text whitelist to bypass diamond warnings), L783 -> L783-785 (`+4 -0`) (Classify illustration_page by checking text indicators), L1034-1047 -> L1034-1047 (`+1 -1`) (Expand max list scrolls to 8 while keeping swipe coordinates at 190px), L1209 -> L1209-1219 (`+10 -0`) (Add automatic return-to-home navigation sequence for illustration_page to prevent lockups)
- `c:/Users/work/Desktop/daily_task/config.json` L76-88 -> L76-88 (`+2 -2`) (Correct recruitment free_single_point to (512, 655) and ten_recruit_point to (848, 655) coordinates based on user calibration), L93-96 -> L93-96 (`+1 -1`) (Move close_result_point to user specified coordinate (514, 633) to prevent misclicks on summon screens)

## [Unreleased] - 2026-06-20 20:31:00 (CST)

### Added
- `c:/Users/work/Desktop/daily_task/ocr_utils.py` L1-125 (`+125 -0`) (Create ocr_utils.py with general configuration loaders and OCR functions extracted from detector.py)

### Changed
- `c:/Users/work/Desktop/daily_task/task_detector.py` L1 -> L1 (`+1 -1`) (Redirect detector imports to ocr_utils)
- `c:/Users/work/Desktop/daily_task/daily_tasks.py` L6 -> L6 (`+1 -1`) (Redirect detector imports to ocr_utils)
- `c:/Users/work/Desktop/daily_task/web_dashboard.py` L10 -> L10 (`+1 -1`) (Redirect detector imports to ocr_utils), L14-151 -> L14-142 (`+130 -139`) (Refactor global variables, Logger, and thread runner to route status and locks per device_id), L209-213 -> L209-226 (`+17 -5`), L269-281 -> L282-309 (`+28 -13`) (Update status and screenshot endpoints to query and respond by device_id), L316-373 -> L321-395 (`+62 -45`) (Update run and stop endpoints to accept device_id and control threads independently), L478, L541-543, L575-576 -> L478, L541-543, L575-587 (`+16 -4`) (Pass device_id to capture_idle_screenshot calls and pre-capture screenshots for all online emulators on start), L391 -> L391-467 (`+76 -0`) (Add POST /api/device/scan endpoint for automated TCP port scanning and auto-binding)
- `c:/Users/work/Desktop/daily_task/dashboard.html` L380-384 -> L380-440 (`+57 -0`) (Add Toast and device connection LED pulsing animation CSS styles), L436-440 -> L440-490 (`+49 -0`) (Add device tabs and tab status light CSS animations), L502-504 -> L502-511 (`+8 -1`) (Add emulator multi-instance card panel above main layout), L488-510 -> L488-520 (`+12 -0`), L633-642 -> L633-653 (`+12 -1`) (Add emulator screenshot canvas frame with status overlay DOM markup), L811 -> L811-813 (`+2 -0`) (Add status led, connect/scan buttons, and toast container DOM markup), L747-821 -> L751-890 (`+139 -71`) (Implement showToast, loadDeviceStatus badge rendering, and scanDevice fetch interactions in JS)
- `c:/Users/work/Desktop/daily_task/run_dj.bat` L7-21 -> L7-21 (`+2 -2`) (Change default python runner target to daily_tasks.py)
- `c:/Users/work/Desktop/daily_task/config.json` L7-40 -> (Deleted) (`+0 -34`) (Remove unused resource detector settings from config.json)

### Removed
- `c:/Users/work/Desktop/daily_task/detector.py`
- `c:/Users/work/Desktop/daily_task/main.py`
- `c:/Users/work/Desktop/daily_task/label_slots.py`
- `c:/Users/work/Desktop/daily_task/preview_slots.py`
- `c:/Users/work/Desktop/daily_task/monitor.py`
- `c:/Users/work/Desktop/daily_task/detail_probe.py`
- `c:/Users/work/Desktop/daily_task/capture_samples.py`
- `c:/Users/work/Desktop/daily_task/coordinate_calibration.py`
- `c:/Users/work/Desktop/daily_task/validate_ocr.py`

## [Unreleased] - 2026-06-20 13:49:00 (CST)

### Added
- `c:/Users/work/Desktop/interest/resource_detector/web_dashboard.py` L175-207 (`+32 -0`), L310-362 (`+52 -10`) (Add GET and POST /api/device endpoints to dynamically query, connect, and save new MuMu emulator instances)
- `c:/Users/work/Desktop/interest/resource_detector/dashboard.html` L428-454 (`+26 -3`), L675-748 (`+74 -3`) (Add Emulator Connection Management HTML card and JS functions to allow user to connect, switch and query active devices)

### Changed
- `c:/Users/work/Desktop/interest/resource_detector/dashboard.html` L550-562 (`+13 -6`) (Disable device connection controls during active running state)

## [Unreleased] - 2026-06-20 03:00:00 (CST)

### Changed
- `c:/Users/work/Desktop/interest/resource_detector/task_runner.py` L1037-1038 -> L1037-1038 (`+2 -2`) (Decrease swipe vertical distance to 190 pixels to prevent jumping over daily tasks in log capture)

## [Unreleased] - 2026-06-20 02:50:00 (CST)

### Changed
- `c:/Users/work/Desktop/interest/resource_detector/task_detector.py` L175-182 -> L175-192 (`+10 -6`) (Filter button items by title y-coordinate distance limit of 50 pixels to avoid cross-row misalignment)

## [Unreleased] - 2026-06-20 02:38:00 (CST)

### Changed
- `c:/Users/work/Desktop/interest/resource_detector/task_detector.py` L185-195 -> L185-202 (`+11 -3`) (Filter button items based on valid action keywords before averaging y-coordinates to eliminate coordinates skew caused by residual scrolled-out row text)

## [Unreleased] - 2026-06-20 02:25:00 (CST)

### Changed
- `c:/Users/work/Desktop/interest/resource_detector/task_detector.py` L183-199 -> L183-202 (`+16 -13`) (Calculate action_point y-coordinate adaptively based on detected button items instead of relying on grid offset)
- `c:/Users/work/Desktop/interest/resource_detector/task_runner.py` L1037-1038 -> L1037-1038 (`+2 -2`) (Restrict y1_val to 600 and y2_val to 280 to keep gesture inside scroll container)

## [Unreleased] - 2026-06-20 01:57:00 (CST)

### Changed
- `c:/Users/work/Desktop/interest/resource_detector/task_runner.py` L1009-1025 -> L1009-1027 (`+13 -11`) (Restrict daily chest taps to only trigger when parsed active points is at or above 100)

## [Unreleased] - 2026-06-20 01:51:00 (CST)

### Changed
- `c:/Users/work/Desktop/interest/resource_detector/task_runner.py` L990-1010 -> L990-1016 (`+16 -13`) (Extract current active points via OCR and restrict chest tap based on thresholds to prevent opening preview popup)

## [Unreleased] - 2026-06-20 01:41:00 (CST)

### Changed
- `c:/Users/work/Desktop/interest/resource_detector/task_runner.py` L1026 -> L1026, L1048 -> L1048 (`+2 -2`) (Decrease y2_val to 200 and increase duration_ms to 1000 to improve swipe success rate on emulator)

## [Unreleased] - 2026-06-20 01:31:00 (CST)

### Changed
- `c:/Users/work/Desktop/interest/resource_detector/task_runner.py` L1273 -> L1273 (`+1 -0`) (Reset self.history at the start of each daily tasks run to prevent cross-run pollution)

## [Unreleased] - 2026-06-20 01:15:00 (CST)

### Changed
- `c:/Users/work/Desktop/interest/resource_detector/task_runner.py` L977-1066 -> L978-1062 (`+50 -49`) (Implement adaptive list scrolling for general loop when runnable tasks are pushed down by skipped top tasks)

## [Unreleased] - 2026-06-20 01:11:00 (CST)

### Changed
- `c:/Users/work/Desktop/interest/resource_detector/task_runner.py` L955 -> L955 (`+1 -1`) (Add mirror trial and equipment upgrade to the task runner loop bypass list)

## [Unreleased] - 2026-06-20 01:09:00 (CST)

### Changed
- `c:/Users/work/Desktop/interest/resource_detector/task_runner.py` L953-964 -> L953-970 (`+6 -0`) (Bypass unsupported tasks like prison or non-white-listed tasks in the daily tasks loop)

## [Unreleased] - 2026-06-20 01:03:00 (CST)

### Changed
- `c:/Users/work/Desktop/interest/resource_detector/tasks/arena.py` L66-91 -> L66 (`+1 -26`) (Remove color detection and checkbox clicking logic for auto battle in arena challenge list)

## [Unreleased] - 2026-06-20 00:55:00 (CST)

### Changed
- `c:/Users/work/Desktop/interest/resource_detector/tasks/friendship.py` L7-17 -> L7-17, L34-46 -> L34-46 (`+2 -2`) (Unify hardcoded lobby back coordinates to 324, 39)
- `c:/Users/work/Desktop/interest/resource_detector/tasks/recruitment.py` L3-101 -> L3-98 (`+49 -52`) (Directly execute 10x recruitment and safely exit to lobby, removing free single check)
- `c:/Users/work/Desktop/interest/resource_detector/task_runner.py` L45-60 -> L45-60, L92-99 -> L92-99, L106-113 -> L106-113, L134-142 -> L134-142, L952-962 -> L952-964 (`+2 -0`) (Update recruitment coordinates, unify configurations lobby coordinates to 324, 39, and bypass already completed recruitment task)

## [Unreleased] - 2026-06-20 00:16:00 (CST)

### Changed
- `c:/Users/work/Desktop/interest/resource_detector/adb_client.py` L41-83 -> L41-88 (`+47 -42`) (Adapt ensure_adb_device to dynamically resolve and fallback to active device from `adb devices`)
- `c:/Users/work/Desktop/interest/resource_detector/actions.py` L7-57 -> L7-57 (`+3 -3`) (Assign dynamic device_id returned by ensure_adb_device to adb commands)

## [Unreleased] - 2026-06-20 00:09:00 (CST)

### Changed
- `c:/Users/work/Desktop/interest/resource_detector/web_dashboard.py` L108-173 -> L108-135 (`+28 -66`) (Trigger runner.run(None) directly for a single adaptive run)

## [Unreleased] - 2026-06-19 23:18:00 (CST)

### Changed
- `c:/Users/work/Desktop/interest/resource_detector/task_runner.py` L1226-1238 -> L1226-1249 (`+11 -0`) (Exempt passive wait steps from stability deadlock check)

## [Unreleased] - 2026-06-19 21:04:00 (CST)

### Added
- `c:/Users/work/Desktop/interest/resource_detector/dashboard.html` L466-474 -> L466-497 (`+30 -9`) (Restored "系统日常任务使用说明" card)

### Changed
- `c:/Users/work/Desktop/interest/resource_detector/dashboard.html` L527-532 -> L550-562 (`+13 -6`) (Disabled config sliders and button during active run)

## [Unreleased] - 2026-06-19 20:49:00 (CST)

### Changed
- `c:/Users/work/Desktop/interest/resource_detector/dashboard.html` L507-522 -> L507-511 (`+5 -16`), L568-603 -> L557 (`+0 -36`), L671-676 -> L633-636 (`+4 -6`)

## [Unreleased] - 2026-06-19 20:40:00 (CST)

### Removed
- `c:/Users/work/Desktop/interest/resource_detector/config_slots.json` (deleted)
- `c:/Users/work/Desktop/interest/resource_detector/task_ai.py` (deleted)

### Changed
- `c:/Users/work/Desktop/interest/resource_detector/config.json` L288-294 -> L288 (`+0 -7`)
- `c:/Users/work/Desktop/interest/resource_detector/task_runner.py` L12 -> L12 (`+0 -1`), L243 -> L243 (`+0 -1`), L1260-1262 -> L1258-1269 (`+9 -0`)
- `c:/Users/work/Desktop/interest/resource_detector/dashboard.html` L405-423 -> L405-415 (`+0 -8`), L668-670 -> L668 (`+0 -2`), L696-710 -> L696 (`+0 -15`)

## [Unreleased] - 2026-06-19 20:35:00 (CST)

### Changed
- `c:/Users/work/Desktop/interest/resource_detector/dashboard.html` L233 -> L233 (`+1 -1`), L285-290 -> L285-291 (`+1 -0`), L596-604 -> L596-626 (`+22 -0`), L666-668 -> L673-682 (`+7 -0`)

## [Unreleased] - 2026-06-19 20:30:00 (CST)

### Changed
- `c:/Users/work/Desktop/interest/resource_detector/tasks/recruitment.py` L53-65 -> L53-70 (`+5 -0`)
- `c:/Users/work/Desktop/interest/resource_detector/task_runner.py` L337-349 -> L337-354 (`+5 -0`)

## [Unreleased] - 2026-06-19 17:20:00 (CST)

### Added
- `c:/Users/work/Desktop/interest/resource_detector/config.json` L327 -> L327-335 (`+8 -0`)

### Changed
- `c:/Users/work/Desktop/interest/resource_detector/dashboard.html` L436-535 -> L436-546 (`+11 -0`), L627-736 -> L627-737 (`+4 -0`)

## [Unreleased] - 2026-06-19 16:12:00 (CST)

### Added
- `c:/Users/work/Desktop/interest/resource_detector/config.json` L321 -> L321-327 (`+7 -0`)
- `c:/Users/work/Desktop/interest/resource_detector/tasks/__init__.py` L1-2 (`+2 -0`)
- `c:/Users/work/Desktop/interest/resource_detector/tasks/login.py` L1-9 (`+9 -0`)
- `c:/Users/work/Desktop/interest/resource_detector/tasks/friendship.py` L1-53 (`+53 -0`)
- `c:/Users/work/Desktop/interest/resource_detector/tasks/recruitment.py` L1-92 (`+92 -0`)
- `c:/Users/work/Desktop/interest/resource_detector/tasks/arena.py` L1-210 (`+210 -0`)
- `c:/Users/work/Desktop/interest/resource_detector/tasks/resource_warehouse.py` L1-53 (`+53 -0`)
- `c:/Users/work/Desktop/interest/resource_detector/tasks/guild_donation.py` L1-49 (`+49 -0`)
- `c:/Users/work/Desktop/interest/resource_detector/tasks/daily_dungeon.py` L1-38 (`+38 -0`)
- `c:/Users/work/Desktop/interest/resource_detector/tasks/shop_refresh.py` L1-41 (`+41 -0`)
- `c:/Users/work/Desktop/interest/resource_detector/tasks/memory_house.py` L1-38 (`+38 -0`)
- `c:/Users/work/Desktop/interest/resource_detector/tasks/kakuja_hunt.py` L1-72 (`+72 -0`)

### Changed
- `c:/Users/work/Desktop/interest/resource_detector/task_runner.py` L690-1876 -> L690-1277 (`+27 -626`)
- `c:/Users/work/Desktop/interest/resource_detector/web_dashboard.py` L100-228 -> L100-295 (`+73 -6`)
- `c:/Users/work/Desktop/interest/resource_detector/dashboard.html` L277-575 -> L277-827 (`+295 -43`)
- `c:/Users/work/Desktop/interest/resource_detector/run_dashboard.bat` L4 -> L4 (`+1 -1`)

## [Unreleased] - 2026-06-18 18:25:00 (CST)

### Added
- `c:/Users/work/Desktop/interest/resource_detector/config.json` L260 -> L263-281 (`+19 -0`), L343 -> L363-371 (`+9 -0`) (`+28 -0`)
- `c:/Users/work/Desktop/interest/resource_detector/task_runner.py` L147 -> L150-165 (`+16 -0`), L589 -> L594-600 (`+7 -0`), L597 -> L604 (`+1 -0`), L970 -> L975-1049 (`+75 -0`), L1204 -> L1207-1224 (`+18 -0`), L1526 -> L1530-1531 (`+2 -0`), L1576 -> L1577-1580 (`+4 -0`), L1623 -> L1627 (`+1 -1`) (`+124 -1`)
- `c:/Users/work/Desktop/interest/resource_detector/dashboard.html` L350-352 -> L353-355 (`+3 -0`), L445 -> L448 (`+1 -0`) (`+4 -0`)

## [Unreleased] - 2026-06-18 18:11:00 (CST)

### Added
- `c:/Users/work/Desktop/interest/resource_detector/config.json` L247 -> L248-262 (`+15 -0`), L320 -> L335-342 (`+8 -0`) (`+23 -0`)
- `c:/Users/work/Desktop/interest/resource_detector/task_runner.py` L132 -> L135-149 (`+15 -0`), L560 -> L573-577 (`+4 -1`), L917 -> L932-970 (`+39 -0`), L1159 -> L1163-1171 (`+9 -0`), L1325-1337 -> L1344-1362 (`+19 -10`), L1444 -> L1464 (`+1 -0`), L1488 -> L1507-1510 (`+4 -0`), L1540 -> L1558-1559 (`+1 -1`) (`+92 -13`)
- `c:/Users/work/Desktop/interest/resource_detector/dashboard.html` L347-349 -> L350-352 (`+3 -0`), L440-441 -> L444 (`+1 -0`) (`+4 -0`)

## [Unreleased] - 2026-06-18 18:54:00 (CST)

### Added
- `c:/Users/work/Desktop/interest/resource_detector/config.json` L226 -> L237-247 (`+11 -0`), L311 -> L314-320 (`+7 -0`) (`+18 -0`)
- `c:/Users/work/Desktop/interest/resource_detector/task_runner.py` L120 -> L121-132 (`+12 -0`), L555 -> L558-559 (`+2 -0`), L561 -> L566 (`+1 -0`), L879 -> L880-918 (`+39 -0`), L1148 -> L1152-1160 (`+9 -0`), L1438 -> L1443-1444 (`+2 -0`), L1476 -> L1485-1488 (`+4 -0`), L1530 -> L1540 (`+1 -1`) (`+70 -1`)
- `c:/Users/work/Desktop/interest/resource_detector/dashboard.html` L344-348 -> L344-351 (`+3 -0`), L437-440 -> L437-441 (`+1 -0`) (`+4 -0`)

## [Unreleased] - 2026-06-18 17:15:00 (CST)

### Changed
- `c:/Users/work/Desktop/interest/resource_detector/config.json` L185 -> L185 (`+1 -1`), L206 -> L206 (`+1 -1`)
- `c:/Users/work/Desktop/interest/resource_detector/task_runner.py` L80 -> L80 (`+1 -1`), L960-961 -> L960-961 (`+1 -1`)
- `c:/Users/work/Desktop/interest/resource_detector/web_dashboard.py` L166-170 -> L166-171 (`+4 -3`), L252-262 -> L256-269 (`+12 -11`)
- `c:/Users/work/Desktop/interest/resource_detector/dashboard.html` L370-381 -> L370-389 (`+8 -0`), L495-513 -> L503-522 (`+5 -0`)

## [Unreleased] - 2026-06-18 17:12:00 (CST)

### Changed
- `c:/Users/work/Desktop/interest/resource_detector/dashboard.html` L232-271 -> L232-234 (`+3 -37`), L421-430 (`+0 -10`), L504-509 -> L504-506 (`+3 -5`), L542-550 (`+0 -9`), L602-607 -> L586-588 (`+3 -5`) (`+9 -66`)

## [Unreleased] - 2026-06-18 17:10:00 (CST)

### Changed
- `c:/Users/work/Desktop/interest/resource_detector/web_dashboard.py` L183-186 -> L183-186 (`+1 -1`)
- `c:/Users/work/Desktop/interest/resource_detector/dashboard.html` L601-602 -> L601-602 (`+1 -1`)

## [Unreleased] - 2026-06-18 15:57:00 (CST)

### Added
- `c:/Users/work/Desktop/interest/resource_detector/config.json` L225-226 -> L225-236 (`+11 -0`)

### Changed
- `c:/Users/work/Desktop/interest/resource_detector/config.json` L275-283 -> L286-297 (`+3 -0`) (`+14 -0`)
- `c:/Users/work/Desktop/interest/resource_detector/task_runner.py` L100-104 -> L100-119 (`+15 -0`), L805 -> L805-837 (`+32 -0`), L1093-1096 -> L1093-1110 (`+14 -0`), L1114-1120 -> L1128-1134 (`+1 -1`), L1172-1176 -> L1186 (`+0 -5`), L523-532 -> L523-535 (`+3 -0`), L1306-1307 -> L1320-1323 (`+2 -0`), L1339-1343 -> L1355-1361 (`+2 -0`), L1394-1396 -> L1412-1413 (`+1 -1`) (`+70 -7`)
- `c:/Users/work/Desktop/interest/resource_detector/dashboard.html` L378-383 -> L378-386 (`+3 -0`), L469-476 -> L472-480 (`+1 -0`) (`+4 -0`)

## [Unreleased] - 2026-06-18 15:20:00 (CST)

### Added
- `c:/Users/work/Desktop/interest/resource_detector/config.json` L205-207 -> L205-225 (`+18 -0`)

### Changed
- `c:/Users/work/Desktop/interest/resource_detector/task_runner.py` L84-91 -> L84-105 (`+14 -0`), L1056-1066 -> L1056-1070 (`+4 -0`), L1288-1296 -> L1288-1313 (`+17 -0`), L1315-1317 -> L1315-1323 (`+6 -0`), L1373-1375 -> L1379-1380 (`+1 -1`), L754-755 -> L754-800 (`+46 -0`) (`+88 -1`)
- `c:/Users/work/Desktop/interest/resource_detector/dashboard.html` L374-381 -> L374-384 (`+3 -0`), L472-475 -> L475-477 (`+1 -0`) (`+4 -0`)

## [Unreleased] - 2026-06-18 15:07:00 (CST)

### Changed
- `c:/Users/work/Desktop/interest/resource_detector/task_runner.py` L176 -> L176-177 (`+1 -0`), L1038-1046 -> L1038-1050 (`+4 -0`), L1103-1140 -> L1103-1142 (`+2 -0`), L1216-1248 -> L1216-1250 (`+1 -1`), L1303-1305 -> L1303-1305 (`+1 -1`), L1327-1332 -> L1327-1333 (`+1 -0`) (`+10 -2`)
- `c:/Users/work/Desktop/interest/resource_detector/dashboard.html` L401-416 -> L401-408 (`+0 -8`), L544-566 -> L536-556 (`+2 -5`) (`+2 -13`)
- `c:/Users/work/Desktop/interest/resource_detector/coordinate_calibration.py` L12-21 -> L12-35 (`+14 -0`), L74-77 -> L88-91 (`+1 -1`) (`+15 -1`)

## [Unreleased] - 2026-06-18 14:30:00 (CST)

### Added
- `c:/Users/work/Desktop/interest/resource_detector/dashboard.html` L1-614 (`+614 -0`)

### Changed
- `c:/Users/work/Desktop/interest/resource_detector/web_dashboard.py` L1-755 -> L1-299 (`+124 -580`)
- `c:/Users/work/Desktop/interest/resource_detector/README.md` L293-310 (`+18 -0`)

## [Unreleased] - 2026-06-17 21:13:00 (CST)

### Added
- `c:/Users/work/Desktop/interest/resource_detector/config.json` L185-186 -> L185-207 (`+21 -0`)
- `c:/Users/work/Desktop/interest/resource_detector/task_runner.py` L81-1211 -> L81-1300 (`+89 -30`)

## [Unreleased] - 2026-06-17 20:27:00 (CST)

### Changed
- `c:/Users/work/Desktop/interest/resource_detector/task_runner.py` L958-963 -> L958-974 (`+12 -2`)

## [Unreleased] - 2026-06-17 20:26:00 (CST)

### Changed
- `c:/Users/work/Desktop/interest/resource_detector/task_runner.py` L1083-1090 -> L1083-1094 (`+11 -7`)

## [Unreleased] - 2026-06-17 20:23:00 (CST)

### Changed
- `c:/Users/work/Desktop/interest/resource_detector/config.json` L107-113 -> L107-113 (`+3 -3`)
- `c:/Users/work/Desktop/interest/resource_detector/task_runner.py` L55-60 -> L55-60 (`+1 -1`)
- `c:/Users/work/Desktop/interest/resource_detector/task_runner.py` L643-647 -> L643-647 (`+1 -1`)

## [Unreleased] - 2026-06-17 20:12:00 (CST)

### Changed
- `c:/Users/work/Desktop/interest/resource_detector/task_runner.py` L781-807 -> L781-804 (`+15 -18`)

## [Unreleased] - 2026-06-17 18:10:00 (CST)

### Changed
- `c:/Users/work/Desktop/interest/resource_detector/task_runner.py` L1122-1133 -> L1122-1138 (`+11 -6`)

## [Unreleased] - 2026-06-17 18:08:00 (CST)

### Changed
- `c:/Users/work/Desktop/interest/resource_detector/config.json` L134-141 -> L134-139 (`+2 -4`)
- `c:/Users/work/Desktop/interest/resource_detector/task_runner.py` L66-70 -> L66-70 (`+1 -1`)

## [Unreleased] - 2026-06-17 18:01:00 (CST)

### Changed
- `c:/Users/work/Desktop/interest/resource_detector/config.json` L174-184 -> L174-184 (`+8 -8`)
- `c:/Users/work/Desktop/interest/resource_detector/task_runner.py` L75-80 -> L75-80 (`+2 -2`)
- `c:/Users/work/Desktop/interest/resource_detector/coordinate_calibration.py` L1-70 -> L1-119 (`+119 -70`)

## [Unreleased] - 2026-06-16 17:38:00 (CST)

### Changed
- `c:/Users/work/Desktop/interest/resource_detector/task_runner.py` L675 -> L675 (`+1 -1`)

### Added
- `c:/Users/work/Desktop/interest/resource_detector/web_dashboard.py` L1-755 (`+755 -0`)
- `c:/Users/work/Desktop/interest/resource_detector/run_dashboard.bat` L1-14 (`+14 -0`)

