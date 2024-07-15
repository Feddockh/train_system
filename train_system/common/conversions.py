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