from datetime import datetime, timedelta
import tzlocal
import pytz

DATE_STRING_FMT = "%Y-%m-%d %I:%M %p"
START_DATE_PARAM_DESC = f"The start date and time in {DATE_STRING_FMT} format"
END_DATE_PARAM_DESC = f"The end date and time in {DATE_STRING_FMT} format"
DEFAULT_USER_REJECTED_ACTION_MSG = {
    "success": False,
    "reason": "User rejected calendar action",
}


def get_local_timezone():
    return str(tzlocal.get_localzone())


def to_rfc3339(date_time_str, timezone_str=get_local_timezone()):
    """
    Convert date and time strings to an RFC3339 formatted string in UTC.

    Parameters:
    date_str (str): Date string in the format %Y-%m-%d.
    time_str (str): Time string in the format HH:MM.
    timezone_str (str): Timezone string, e.g., 'US/Pacific'.

    Returns:
    str: The RFC3339 formatted string in UTC.
    """
    # Check and correct for invalid '00:00 AM' or '00:00 PM' cases
    if "00:00 AM" in date_time_str:
        date_time_str = date_time_str.replace("00:00 AM", "12:00 AM")
    elif "00:00 PM" in date_time_str:
        date_time_str = date_time_str.replace("00:00 PM", "12:00 PM")

    naive_date_time = datetime.strptime(date_time_str, DATE_STRING_FMT)
    local_tz = pytz.timezone(timezone_str)
    local_date_time = local_tz.localize(naive_date_time)
    utc_date_time = local_date_time.astimezone(pytz.UTC)
    return utc_date_time.isoformat()


def from_rfc3339(rfc3339_str, timezone_str=get_local_timezone()):
    """
    Convert an RFC3339 formatted string in UTC to a human-readable date and time string.

    Parameters:
    rfc3339_str (str): RFC3339 formatted string in UTC.
    timezone_str (str): Timezone string, e.g., 'America/Los_Angeles'.

    Returns:
    str: The date and time string in the format '%Y-%m-%d %H:%M' in the specified timezone.
    """
    utc_date_time = datetime.fromisoformat(rfc3339_str.replace("Z", "+00:00"))
    local_tz = pytz.timezone(timezone_str)
    local_date_time = utc_date_time.astimezone(local_tz)
    date_time_str = local_date_time.strftime(DATE_STRING_FMT)
    return date_time_str


def now_plus_hours(num_hours):
    return (datetime.now() + timedelta(hours=num_hours)).strftime(DATE_STRING_FMT)
