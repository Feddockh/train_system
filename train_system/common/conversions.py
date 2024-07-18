# train_system.common.utils

def time_to_seconds(time_str: str):

    """
    Converts a time string in the format 'HH:MM' to the number of seconds since midnight.

    Args:
        time_str (str): The time string to convert.

    Returns:
        int: The number of seconds since midnight.
    """

    hours, minutes = map(int, time_str.split(':'))
    return hours * 3600 + minutes * 60

def seconds_to_time(seconds: int) -> str:
    """
    Converts the number of seconds since midnight to a time string in the format 'HH:MM'.

    Args:
        seconds (int): The number of seconds since midnight.

    Returns:
        str: The time string in the format 'HH:MM'.
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours:02}:{minutes:02}"

def meters_to_miles(meters: float) -> float:
    """
    Converts a distance in meters to miles.

    Args:
        meters (float): The distance in meters.

    Returns:
        float: The distance in miles.
    """
    return meters * 0.000621371

def miles_to_meters(miles: float) -> float:
    """
    Converts a distance in miles to meters.

    Args:
        miles (float): The distance in miles.

    Returns:
        float: The distance in meters.
    """
    return miles / 0.000621371

def kph_to_mph(kph: float) -> float:
    """
    Converts a speed in kilometers per hour to miles per hour.

    Args:
        kph (float): The speed in kilometers per hour.

    Returns:
        float: The speed in miles per hour.
    """
    return kph * 0.621371

def mph_to_kph(mph: float) -> float:
    """
    Converts a speed in miles per hour to kilometers per hour.

    Args:
        mph (float): The speed in miles per hour.

    Returns:
        float: The speed in kilometers per hour.
    """
    return mph / 0.621371
