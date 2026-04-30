from datetime import datetime, timedelta
from config import *

#checks whether an all-day event is actually a type of "on leave" event
def is_leave_all_day(title: str) -> bool:
    t = (title or "").upper()
    return any(k in t for k in LEAVE_KEYWORDS)


def show_free_slots_tomorrow(events, earliest_start=None, latest_end=None, target_date=None):
    now_local = datetime.now(MY_TZ)

    #Determines which day is being evaluated
    if target_date is None:
        day = (now_local + timedelta(days=1)).date()  # fallback = tomorrow
        label = "Tomorrow"
    else:
        day = target_date
        label = "Selected Day"

    print(f"\n=== FREE SLOTS ({label}, MY time) ===\n")

    #Define working window
    day_start = datetime.combine(day, datetime.min.time(), tzinfo=MY_TZ).replace(
        hour=WORK_START_HOUR, minute=WORK_START_MIN
    )
    day_end = datetime.combine(day, datetime.min.time(), tzinfo=MY_TZ).replace(
        hour=WORK_END_HOUR, minute=WORK_END_MIN
    )

    # invalid range check
    if earliest_start is not None:
        day_start = max(day_start, earliest_start)

    if latest_end is not None:
        day_end = min(day_end, latest_end)

    if day_start >= day_end:
        print("Requested time window is invalid (start >= end). No slots.")
        return

    busy = []


    #Build list of busy intervals
    for e in events:
        title = e.get("summary", "")

        start_dt_str = e["start"].get("dateTime")
        end_dt_str = e["end"].get("dateTime")
        start_date_str = e["start"].get("date")
        end_date_str = e["end"].get("date")

        if start_dt_str and end_dt_str:
            start_dt = datetime.fromisoformat(start_dt_str.replace("Z", "+00:00")).astimezone(MY_TZ)
            end_dt = datetime.fromisoformat(end_dt_str.replace("Z", "+00:00")).astimezone(MY_TZ)

            if end_dt <= day_start or start_dt >= day_end:
                continue

            busy.append((max(start_dt, day_start), min(end_dt, day_end), title))

        else:
            start_dt = datetime.fromisoformat(start_date_str).replace(tzinfo=MY_TZ)
            end_dt = datetime.fromisoformat(end_date_str).replace(tzinfo=MY_TZ)

            t = (title or "").upper()

            # Ignore public holidays and annual  leave entries
            if "HOLIDAY" in t or "PUBLIC" in t:
                continue

            if "AL" in t or "LEAVE" in t or "OOO" in t:
                continue

            all_day_start = datetime.combine(day, datetime.min.time(), tzinfo=MY_TZ)
            all_day_end = all_day_start + timedelta(days=1)

            if end_dt <= all_day_start or start_dt >= all_day_end:
                continue

            busy.append((day_start, day_end, title + " [ALL-DAY]"))


    # if nothing is clashing with other events of the day
    if not busy:
        print("No events.")
        print(f"FREE  {day_start.strftime('%H:%M')} → {day_end.strftime('%H:%M')}")
        return

    # merge overlapping busy intervals
    busy.sort(key=lambda x: x[0])

    merged = []
    for s, e, title in busy:
        if not merged or s > merged[-1][1]:
            merged.append([s, e, [title]])
        else:
            merged[-1][1] = max(merged[-1][1], e)
            merged[-1][2].append(title)

    print("Busy blocks:")
    for s, e, titles in merged:
        if s == day_start and e == day_end:
            print(f"  BUSY ALL DAY (reason: {titles[0]})")
        else:
            print(f"  BUSY {s.strftime('%H:%M')} → {e.strftime('%H:%M')}")

    free_slots = []
    cursor = day_start

    for s, e, _ in merged:
        if s > cursor:
            free_slots.append((cursor, s))
        cursor = max(cursor, e)

    if cursor < day_end:
        free_slots.append((cursor, day_end))

    if not free_slots:
        print("\nNo available slots.")
        return

    print("\nFree slots:")
    for s, e in free_slots:
        print(f"  FREE {s.strftime('%H:%M')} → {e.strftime('%H:%M')}")