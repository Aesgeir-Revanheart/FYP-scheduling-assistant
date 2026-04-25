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

           # If user asked "after X", shift the start of the work window forward
    if earliest_start is not None:
        day_start = max(day_start, earliest_start)

    # If user asked "before X", shift the end of the work window backward
    if latest_end is not None:
        day_end = min(day_end, latest_end)

    # Sanity check AFTER applying both filters
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

            # Overlap check with work window
            if end_dt <= day_start or start_dt >= day_end:
                continue

            busy.append((max(start_dt, day_start), min(end_dt, day_end), title))

        else:
            # All-day event (end date is exclusive)
            start_dt = datetime.fromisoformat(start_date_str).replace(tzinfo=MY_TZ)
            end_dt = datetime.fromisoformat(end_date_str).replace(tzinfo=MY_TZ)

            # Only treat as busy if it's a leave/OOO/holiday-style marker
            if not is_leave_all_day(title):
                continue

            # Convert all-day to overlap with our work window
            # If the all-day spans tomorrow, it blocks the whole work window.
            all_day_start = datetime.combine(tomorrow, datetime.min.time(), tzinfo=MY_TZ)
            all_day_end = all_day_start + timedelta(days=1)

            if end_dt <= all_day_start or start_dt >= all_day_end:
                continue

            busy.append((day_start, day_end, title + " [ALL-DAY]"))

    if not busy:
        print("No busy blocks tomorrow inside work hours.")
        print(f"FREE  {day_start.strftime('%H:%M')} → {day_end.strftime('%H:%M')}")
        return

    # Sort & merge busy blocks (ignore titles for merging)
    busy.sort(key=lambda x: x[0])

    merged = []
    for s, e, title in busy:
        if not merged or s > merged[-1][1]:
            merged.append([s, e, [title]])
        else:
            merged[-1][1] = max(merged[-1][1], e)
            merged[-1][2].append(title)

    # Print busy summary
    print("Busy blocks tomorrow (work hours):")
    for s, e, titles in merged:
        if s == day_start and e == day_end:
            print(f"  BUSY  ALL DAY  (reason: {titles[0]})")
        else:
            print(f"  BUSY  {s.strftime('%H:%M')} → {e.strftime('%H:%M')}  (e.g., {titles[0]})")

    # Compute free slots
    free_slots = []
    cursor = day_start
    for s, e, _ in merged:
        if s > cursor:
            free_slots.append((cursor, s))
        cursor = max(cursor, e)
    if cursor < day_end:
        free_slots.append((cursor, day_end))

    print("\nFree slots tomorrow:")
    
    if not free_slots:
        print("  (none within work hours)")
        return
    
    for s, e in free_slots:
        print(f"  FREE  {s.strftime('%H:%M')} → {e.strftime('%H:%M')}")