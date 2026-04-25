import re

def parse_query(text: str):
    text_l = text.lower()

    out = {}

    # date intent (for now only "tomorrow")
    if "tomorrow" in text_l:
        out["date"] = "tomorrow"

    # after-time patterns:
    # - "after 3pm"
    # - "after 3:30pm"
    # - "after 15:00"
    m = re.search(r"\bafter\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\b", text_l)
    if m:
        hour = int(m.group(1))
        minute = int(m.group(2) or "0")
        ampm = m.group(3)

        if ampm:  # 12-hour format
            if ampm == "pm" and hour != 12:
                hour += 12
            if ampm == "am" and hour == 12:
                hour = 0

        # basic sanity clamp
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            out["after_hour"] = hour
            out["after_min"] = minute

    m2 = re.search(r"\bbefore\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\b", text_l)
    if m2:
        hour = int(m2.group(1))
        minute = int(m2.group(2) or "0")
        ampm = m2.group(3)

        if ampm:
            if ampm == "pm" and hour != 12:
                hour += 12
            if ampm == "am" and hour == 12:
             hour = 0

        if 0 <= hour <= 23 and 0 <= minute <= 59:
            out["before_hour"] = hour
            out["before_min"] = minute

        if "free" in text_l:
            out["intent"] = "free_time"

    return out if out else None