#!/usr/local/bin/python3.6 -u

# Really there should be a more formalized set of unit tests, but there hasn't
# been much that I wanted to spend the time to test (my fault, I know), so you
# get this shitty stand-alone file instead.

import pytz
import Hardware
from datetime import datetime, timedelta

# First we check the function that does the scary tz conversions.  I'm sure
# I've missed things.

are_any_alarms_firing = Hardware.StateVariablesAlarmThread.are_any_alarms_firing

# Alarm(aid, enabled, days_of_week, hour, minute, mins_before, mins_after)
alarms = [
    Hardware.Alarm(0, True, (0,1,2,3,4,5,6), 6, 23, 0, 0),
    Hardware.Alarm(1, True, (1, ), 21, 23, 3, 7),
    Hardware.Alarm(2, False, (6, ), 21, 23, 2, 2),
]

print("Alarms are:")
for a in alarms:
    print("    %s" % (a, ))
    assert(str(a) == str(Hardware.Alarm.from_quad(*a.to_quad())))
print("From and to quad tests passed.")

def dt_utc(dt):
    """Convert unaware dt to utc dt."""
    ret = pytz.utc.localize(dt, is_dst=True)
    if ret != pytz.utc.localize(dt, is_dst=False):
        raise Exception("UTC should not ever have discontinuities.")
    return ret

tz = pytz.timezone('America/Los_Angeles')
def loc(dt):
    global tz
    return dt.astimezone(tz)

def sprint(name, dt):
    global loc
    def sprint_one(dt):
        return "%s %s, DOW is %d" % (dt, dt.tzinfo.zone, dt.weekday())
    return "%s:\n    %s\n    %s" % (name, sprint_one(dt), sprint_one(loc(dt)))

# datetime(2014, 12, 4, 6, 21, tzinfo=<DstTzInfo 'America/Los_Angeles' PST-1 day, 16:00:00 STD>)
# with weekday() = 1
dt1 = dt_utc(datetime(2014, 12, 4, 14, 21))

# The datetime(2002, 4, 7, 2, 30, 00) did not exist in Los Angeles, and
# when converting it corresponds to the two datetimes:
#     datetime(2002, 4, 7,  9, 30, tzinfo=<UTC>)
#     datetime(2002, 4, 7, 10, 30, tzinfo=<UTC>)
# weekday is 6
dt2 = dt_utc(datetime(2002, 4, 7,  9, 30))
dt3 = dt_utc(datetime(2002, 4, 7, 10, 30))


print(sprint("dt1", dt1))
print(sprint("dt2", dt2))
print(sprint("dt3", dt3))
print("Test:")
print("are_any_alarms_firing(dt1, tz, alarms) == (False, 120.0))")
assert(are_any_alarms_firing(dt1, tz, alarms) == (False, 120.0))
print("are_any_alarms_firing(dt1 + timedelta(minutes=2), tz, alarms)) == (True, 0.0)")
assert(are_any_alarms_firing(dt1 + timedelta(minutes=2), tz, alarms) == (True, 0.0))
print("are_any_alarms_firing(dt1 + timedelta(minutes=2, seconds=1), tz, alarms)) == (True, 59.0)")
assert(are_any_alarms_firing(dt1 + timedelta(minutes=2, seconds=1), tz, alarms) == (True, 59.0))

print("Passed.")
