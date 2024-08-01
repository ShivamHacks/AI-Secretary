from datetime import datetime
import pytz


def to_rfc3339(date_str, time_str, timezone_str="America/Los_Angeles"):
    """
    Convert date and time strings to an RFC3339 formatted string in UTC.

    Parameters:
    date_str (str): Date string in the format %Y-%m-%d.
    time_str (str): Time string in the format HH:MM.
    timezone_str (str): Timezone string, e.g., 'US/Pacific'.

    Returns:
    str: The RFC3339 formatted string in UTC.
    """
    date_time_str = f"{date_str} {time_str}"
    naive_date_time = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M")
    local_tz = pytz.timezone(timezone_str)
    local_date_time = local_tz.localize(naive_date_time)
    utc_date_time = local_date_time.astimezone(pytz.UTC)
    return utc_date_time.isoformat()
