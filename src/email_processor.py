from parser import parse_query
from datetime import datetime, timedelta
from config import MY_TZ
from scheduler import show_free_slots_tomorrow


def process_email(subject, events):
    print(f"\nProcessing email subject: {subject}")

    parsed = parse_query(subject)

    if not parsed or "intent" not in parsed:
        print("No scheduling intent detected.")
        return

    print(f"[DEBUG] parsed = {parsed}")

    # --- DEFAULT DATE (IMPORTANT) ---
    now_local = datetime.now(MY_TZ)
    target_date = now_local.date()

    if parsed.get("date") == "tomorrow":
        target_date = (now_local + timedelta(days=1)).date()

    # --- TIME WINDOWS ---
    after_hour = parsed.get("after_hour")
    after_min = parsed.get("after_min", 0)

    before_hour = parsed.get("before_hour")
    before_min = parsed.get("before_min", 0)

    earliest_start = None
    if after_hour is not None:
        earliest_start = datetime.combine(
            target_date, datetime.min.time(), tzinfo=MY_TZ
        ).replace(hour=after_hour, minute=after_min)

    latest_end = None
    if before_hour is not None:
        latest_end = datetime.combine(
            target_date, datetime.min.time(), tzinfo=MY_TZ
        ).replace(hour=before_hour, minute=before_min)

    # --- SHOW SLOTS ---
    show_free_slots_tomorrow(
        events,
        earliest_start=earliest_start,
        latest_end=latest_end,
    )

    # --- SPECIFIC TIME CHECK (PRIORITY FEATURE) ---
    at_hour = parsed.get("at_hour")
    at_min = parsed.get("at_min", 0)

    if at_hour is not None:
        specific_time = datetime.combine(
            target_date, datetime.min.time(), tzinfo=MY_TZ
        ).replace(hour=at_hour, minute=at_min)

        print("\nSpecific time check:")

        is_free = True

        for e in events:
            start_dt_str = e["start"].get("dateTime")
            end_dt_str = e["end"].get("dateTime")

            if not start_dt_str or not end_dt_str:
                continue

            start_dt = datetime.fromisoformat(start_dt_str.replace("Z", "+00:00")).astimezone(MY_TZ)
            end_dt = datetime.fromisoformat(end_dt_str.replace("Z", "+00:00")).astimezone(MY_TZ)

            if start_dt <= specific_time < end_dt:
                is_free = False
                break

        if is_free:
            print(f"Result: FREE at {specific_time.strftime('%H:%M')}")
        else:
            print(f"Result: BUSY at {specific_time.strftime('%H:%M')}")