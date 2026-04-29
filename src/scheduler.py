from datetime import datetime, timedelta
from config import *


def is_leave_all_day(title: str) -> bool:
    t = (title or "").upper()
    return any(k in t for k in LEAVE_KEYWORDS)


def show_free_slots_tomorrow(events, earliest_start=None, latest_end=None):
    print("\n=== FREE SLOTS (Tomorrow, MY time) ===\n")

    now_local = datetime.now(MY_TZ)
    tomorrow = (now_local + timedelta(days=1)).date()

    day_start = datetime.combine(tomorrow, datetime.min.time(), tzinfo=MY_TZ).replace(
        hour=WORK_START_HOUR, minute=WORK_START_MIN
    )
    day_end = datetime.combine(tomorrow, datetime.min.time(), tzinfo=MY_TZ).replace(
        hour=WORK_END_HOUR, minute=WORK_END_MIN
    )

    # Apply filters
    if earliest_start is not None:
        day_start = max(day_start, earliest_start)

    if latest_end is not None:
        day_end = min(day_end, latest_end)

    # Invalid window check
    if day_start >= day_end:
        print("Requested time window is invalid (start >= end). No slots.")
        return

    busy = []

    for e in events:
        title = e.get("summary", "")

        start_dt_str = e["start"].get("dateTime")
        end_dt_str = e["end"].get("dateTime")
        start_date_str = e["start"].get("date")
        end_date_str = e["end"].get("date")

        if start_dt_str and end_dt_str:
            # Timed event
            start_dt = datetime.fromisoformat(start_dt_str.replace("Z", "+00:00")).astimezone(MY_TZ)
            end_dt = datetime.fromisoformat(end_dt_str.replace("Z", "+00:00")).astimezone(MY_TZ)

            if end_dt <= day_start or start_dt >= day_end:
                continue

            busy.append((max(start_dt, day_start), min(end_dt, day_end), title))

        else:
            # All-day event
            if not is_leave_all_day(title):
                continue

            start_dt = datetime.fromisoformat(start_date_str).replace(tzinfo=MY_TZ)
            end_dt = datetime.fromisoformat(end_date_str).replace(tzinfo=MY_TZ)

            all_day_start = datetime.combine(tomorrow, datetime.min.time(), tzinfo=MY_TZ)
            all_day_end = all_day_start + timedelta(days=1)

            if end_dt <= all_day_start or start_dt >= all_day_end:
                continue

            busy.append((day_start, day_end, title + " [ALL-DAY]"))

    # --- NO BUSY EVENTS ---
    if not busy:
        if earliest_start:
            print(f"No events after {earliest_start.strftime('%H:%M')} tomorrow.")
        elif latest_end:
            print(f"No events before {latest_end.strftime('%H:%M')} tomorrow.")
        else:
            print("No events tomorrow.")

        print(f"FREE  {day_start.strftime('%H:%M')} → {day_end.strftime('%H:%M')}")
        return

    # --- MERGE BUSY BLOCKS ---
    busy.sort(key=lambda x: x[0])

    merged = []
    for s, e, title in busy:
        if not merged or s > merged[-1][1]:
            merged.append([s, e, [title]])
        else:
            merged[-1][1] = max(merged[-1][1], e)
            merged[-1][2].append(title)

    # --- PRINT BUSY ---
    print("Busy blocks tomorrow (work hours):")
    for s, e, titles in merged:
        if s == day_start and e == day_end:
            print(f"  BUSY  ALL DAY  (reason: {titles[0]})")
        else:
            print(f"  BUSY  {s.strftime('%H:%M')} → {e.strftime('%H:%M')}  (e.g., {titles[0]})")

    # --- COMPUTE FREE ---
    free_slots = []
    cursor = day_start

    for s, e, _ in merged:
        if s > cursor:
            free_slots.append((cursor, s))
        cursor = max(cursor, e)

    if cursor < day_end:
        free_slots.append((cursor, day_end))

    # --- OUTPUT ---
    if not free_slots:
        if earliest_start:
            print(f"\nNo available slots after {earliest_start.strftime('%H:%M')} tomorrow.")
        elif latest_end:
            print(f"\nNo available slots before {latest_end.strftime('%H:%M')} tomorrow.")
        else:
            print("\nNo available slots tomorrow.")
        return

    print("\nFree slots tomorrow:")
    for s, e in free_slots:
        print(f"  FREE  {s.strftime('%H:%M')} → {e.strftime('%H:%M')}")