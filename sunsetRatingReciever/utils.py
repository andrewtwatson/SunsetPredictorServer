"""
Utility functions to use
"""


def hoursDelta(t1, t2):
    """
    Gets the time between t1 and t2 in hours.
    t1 and t2 are unix times (that is, seconds since January 1, 1970)
    For a positive time, t1 should be before t2
    """
    return round((t2 - t1) / 3600)

def minutesDelta(t1, t2):
    """
    Gets the time between t1 and t2 in minutes.
    t1 and t2 are unix times (that is, seconds since January 1, 1970)
    For a positive time, t1 should be before t2
    """
    return round((t2 - t1) / 3600)