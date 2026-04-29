import re

def parse_query(text: str):
    text_l = text.lower()

    out = {}

    # date intent (for now only "tomorrow")
    if "tomorrow" in text_l:
        out["date"] = "tomorrow"

    # AFTER
    m = re.search(r"\bafter\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\b", text_l)
    if m:
        hour = int(m.group(1))
        minute = int(m.group(2) or "0")
        ampm = m.group(3)

        if ampm:
            if ampm == "pm" and hour != 12:
                hour += 12
            if ampm == "am" and hour == 12:
                hour = 0

        if 0 <= hour <= 23 and 0 <= minute <= 59:
            out["after_hour"] = hour
            out["after_min"] = minute

    # BEFORE
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

    # NEW: AT TIME (THIS IS THE IMPORTANT PART)
    m3 = re.search(r"\bat\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\b", text_l)
    if m3:
        hour = int(m3.group(1))
        minute = int(m3.group(2) or "0")
        ampm = m3.group(3)

        if ampm:
            if ampm == "pm" and hour != 12:
                hour += 12
            if ampm == "am" and hour == 12:
                hour = 0

        if 0 <= hour <= 23 and 0 <= minute <= 59:
            out["at_hour"] = hour
            out["at_min"] = minute

    if "free" in text_l:
        out["intent"] = "free_time"

    return out if out else None