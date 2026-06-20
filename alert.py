def emit_alert(results, app_config):
    enemy_slots = [item for item in results if item["status"] == "enemy"]
    suspect_slots = [
        item for item in results
        if item["status"] in ["suspect_enemy_name", "suspect_enemy_guild"]
    ]
    alert_config = app_config.get("alert") or {}

    if enemy_slots:
        print("\n!!! CONFIRMED ENEMY TARGET !!!")

        for item in enemy_slots:
            target = item.get("matched_enemy_target") or {}
            print(
                f"Slot {item['slot']}: "
                f"{item.get('name') or '-'} / {item.get('guild') or '-'} "
                f"matched {target.get('name', '-')}/{target.get('guild', '-')}"
            )

        play_beep(app_config)

    if suspect_slots and alert_config.get("show_suspects", False):
        print("\nSuspect target, not actionable:")

        for item in suspect_slots:
            print(
                f"Slot {item['slot']}: "
                f"{item['status']} "
                f"{item.get('name') or '-'} / {item.get('guild') or '-'}"
            )


def play_beep(app_config):
    alert_config = app_config.get("alert") or {}

    if not alert_config.get("beep", True):
        return

    try:
        import winsound
    except ImportError:
        print("[alert] winsound unavailable; skipping beep")
        return

    winsound.Beep(
        int(alert_config.get("beep_frequency", 1200)),
        int(alert_config.get("beep_duration_ms", 600))
    )
