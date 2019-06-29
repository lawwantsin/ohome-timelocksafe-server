#!/usr/local/bin/python3.6 -u

"""Encapulate all the TZ crazyness in one place, so maybe the stupid that
we have to deal with because politicians need to feel important won't
poison everything else, but you know, we failed because we still have to
ask the user about the timezone.

Also this module has the get temperature function and the extended
storage stuff where we store the alarms, and other user prefs, so it is
really trying to encapsulate all hardware.

We also expose an interface to the the data stored in the memory chip and not
the RTC itself, which stores all user-prefs (the timezone and alarms).  This
storage is battery-backed, same as the RTC, so we call it PRAM instead of RAM
(like system memory).  We read and write from byte-addressable memory (via a
read and write (byte at a time) function."""

import sys, traceback

if __name__ == "__main__":
    print("Please load as a module, instead of running as a script.",
        file=sys.stderr)
    sys.exit(1)

def sprint_exception(exp):
    """Convert the given exception into a string."""
    try:
        return "".join(
                traceback.format_exception(None, exp, exp.__traceback__))
    except Exception:
        return "Error in sprint_exception."

import enum, time, datetime, threading
from math import sin, exp, pi
import RPi.GPIO  # System module (should be installed).
import crc8, pytz  # Local dir (non-system) modules.
try:
    # This is the RTC, thermometer, & (battery-backed) storage.
    # We set here so we can set the versions in one place.  This may throw,
    # or otherwise fail, but loading this module should not, so if this fails
    # we have to make sure the stuff below is skipped as well.
    import DS3231_AT24C32  # Local, may fail.
    _RTC = DS3231_AT24C32.DS3231_AT24C32()
    _RTC.rtc_load_error = ""  # If set (non-empty) we don't do anything.
except Exception as exp:
    class DummyRTC():
        """Object that just returns the version fields used below, but none
        of the PRAM stuff, since it should know better."""
        __version__ = "Unknown (DummyRTC)"
        _smbus_version = "Unknown (DummyRTC)"
        rtc_load_error = sprint_exception(exp)

    _RTC = DummyRTC()



_PROC_START_TIME_REFERENCE = time.monotonic()  # Proc uptime

def proc_uptime_str():
    proc_elapsed_secs = time.monotonic() - _PROC_START_TIME_REFERENCE
    return str(datetime.timedelta(seconds=proc_elapsed_secs))


# See the _large_ comment below called "PRAM Format (Version 0)".
_PRAM_format_version = 0  # Currently stored as a byte, so int (0, 255).

# All the versions to pass into the diag page.
versions_tuple = (
        ("pytz", pytz.VERSION),
        ("Olson/IANA DB", pytz.OLSON_VERSION),
        ("RTC_SDL_DS3231", _RTC.__version__),
        ("smbus2", _RTC._smbus_version),
        ("PRAM format", f"{_PRAM_format_version:d}"),
        ("crc8.py", crc8.__version__),
    )

@enum.unique
class STATE(enum.Enum):
    """This is the state of the hardware memory (including the alarms).
    Each state is described below.  This is used to choose what page is
    displayed on a GET request to '/'.  In this context the word "alarm"
    means the time(s) and day(s) the box latch should be unlocked."""
    OVERRIDE = ("The latch has been manually unlocked and can be opened.  "
            "LED is blinking about twice a second.")
    CORRUPT = ("There was some kind of error.  "
            "When in this state only the error page will be displayed "
            "showing the error string.  This is also the state during boot.  "
            "LED is blinking about once every five seconds.")
    NEW = ("The box is either new or the battery has died (wiping PRAM).  "
            "Memory was read successfully but it seems like nothing was "
            "previously stored there.  This means that no timezone, time, or "
            "alarms are set, so we show the user the page to set them.  "
            "LED is continuously on.")
    NOALARMS = ("There are no enabled alarms (there could be defined "
            "disabled alarms, though).  LED is continuously on.")
    UNLOCKED = ("At least one alarm is currently firing and the box "
            "is currently unlocked and alarms can be modified or added "
            "and the time changed, etc.  The page should pop up a timer "
            "showing exactly how much time is left before the box locks "
            "because there is no way to safely allow modifications after "
            "the box is locked.  LED is blinking about twice a second.")
    LOCKED = ("There is at least one enabled alarm and no alarms are "
            "currently firing, so the web page shows when the next alarm "
            "will fire and how long until then.  Should be no way to "
            "unlock the box, reset the time or timezone, or add, delete, "
            "or modify any alarms from the web page or SSH in (obviously "
            "getting in via SSH even when it this state is easy with a tiny "
            "bit of effort, see the description in the hacking section but "
            "the simple first things shouldn't work).  LED is breathing.")


# Board pin 7 is the LED, and
# board pin 11 is the latch (pin defaults to low on board power on).
RPi.GPIO.setmode(RPi.GPIO.BOARD)
RPi.GPIO.setup(7, RPi.GPIO.OUT)
RPi.GPIO.output(7, RPi.GPIO.LOW)
RPi.GPIO.setup(11, RPi.GPIO.OUT)
RPi.GPIO.output(11, RPi.GPIO.LOW)

class boxLatch():
    """Class to (un)lock the latch.  Only things that should be called are:
            boxLatch.lock()
        and
            boxLatch.unlock()
    """

    def __init__(self):
        raise Exception("Don't instantiate, boxLatch is used as a singleton.")

    _event = threading.Event()
    _lock = threading.Lock()  # For _box_latch_locked.
    _box_latch_locked = True
    RPi.GPIO.output(11, RPi.GPIO.LOW)  # Start with it locked.

    @classmethod
    def background_thread(cls):
        """We could use the SW PWM, but the module sucks.  Sometimes it would
        vibrate the latch at a random frequency and the PWM didn't always
        stop with the stop() function.  Since this moves really slowly and
        exact timing isn't important we just use a bg thread and a sleep.
        I *think* this solenoid has a max on time of under a second and a
        duty cycle of under 25 %, so we use 0.8 seconds and 20 % for a 4 secs
        long pattern of 0.8 seconds on followed by 3.2 seconds off."""
        while True:
            cls._event.clear()
            with cls._lock:
                is_locked = cls._box_latch_locked

            if is_locked:
                cls._event.wait()
            else:
                while not cls._event.is_set():
                    RPi.GPIO.output(11, RPi.GPIO.HIGH)
                    time.sleep(0.8)
                    RPi.GPIO.output(11, RPi.GPIO.LOW)
                    time.sleep(3.2)

    @classmethod
    def lock(cls):
        """Lock the physical box.  Needs to be idempotent."""
        with cls._lock:
            cls._box_latch_locked = True
        cls._event.set()

    @classmethod
    def unlock(cls):
        """Unlock the physical box.  Needs to be idempotent."""
        with cls._lock:
            cls._box_latch_locked = False
        cls._event.set()

# Wait until after RTC init to start the background thread.

class boxLED():
    """Control the LED.  Only call should be to `boxLED.set_state(state)`."""

    def __init__(self):
        raise Exception("Don't instantiate, boxLED used as a singleton.")

    # We use event here becaue we want the duty cycle change for breathing to
    # happen in as tight a loop as possible and `threading.Event().is_set()`
    # is _an_order_of_magnitude_ faster to check (when not set) than any of:
    #   threading.Event().wait(timeout=0.0)
    #   queue.Queue().empty()
    #   queue.Queue().get_nowait()
    #   etc.
    _event = threading.Event()
    # Lock for all the variables.  Everything should use the context manager.
    _lock = threading.Lock()

    @enum.unique
    class STATE(enum.Enum):
        OFF = enum.auto()
        SOLID = enum.auto()
        BREATHING = enum.auto()
        BLINKING_FAST = enum.auto()
        BLINKING_SLOW = enum.auto()

    state = STATE.OFF

    _t_pwm = RPi.GPIO.PWM(7, 1.0)  # 1 Hz

    @classmethod
    def background_thread(cls):
        while True:
            cls._event.wait()
            cls._t_pwm.stop()
            time.sleep(0.5) # Stop sometimes takes a bit, so this is a hack.
            cls._event.clear()

            with cls._lock:  # Don't want to set the event.
                _state = cls.state


            if _state == cls.STATE.OFF:
                RPi.GPIO.output(7, RPi.GPIO.LOW)
            elif _state == cls.STATE.SOLID:
                RPi.GPIO.output(7, RPi.GPIO.HIGH)
            elif _state in (cls.STATE.BLINKING_FAST, cls.STATE.BLINKING_SLOW):
                if _state == cls.STATE.BLINKING_SLOW:
                    cls._t_pwm.ChangeFrequency(1.0 / 5.0)
                else:
                    cls._t_pwm.ChangeFrequency(1.0 / 0.2)
                cls._t_pwm.start(25.0)
            elif _state == cls.STATE.BREATHING:
                # This looks way better than a bare sine wave, I got it from:
                #   https://sean.voisen.org/blog/2011/10/breathing-led-with-arduino/
                cls._t_pwm.ChangeFrequency(120.0)
                cls._t_pwm.start(0.0)
                while not cls._event.is_set():  # See comment for cls._event.
                    cls._t_pwm.ChangeDutyCycle(
                            exp(sin((2.0 * pi / 5.0) * time.time()))
                            * 42.3529411764706 - 15.5807762823529
                        )
            else:
                RPi.GPIO.output(7, RPi.GPIO.LOW)
                err = "Unknow LED state given, should never happen, abort."
                print(err, file=sys.stderr)
                raise Exception(err)

    @classmethod
    def set_state(cls, state):
        if not isinstance(state, cls.STATE):
            raise Exception(f"Given state is not a boxLED.STATE: {state}")
        with cls._lock:
            try:
                cls.state = state
            finally:
                cls._event.set()

# Wait until after RTC init to start the background thread.


def crc8_3c(c1, c2, c3):
    """Take 3 chars (int (0, 255)) and return an int (0, 255) as a CRC8.
    This is a function only because the format to get this is kinda messy and
    hard to read and we always want 3 bytes at a time in this version of
    the PRAM format."""
    return crc8.crc8(bytes((c1, c2, c3))).digest()[0]

class Alarm():
    """One alarm.  So needs to store the hour, minute, enabled, and the
    days of the week (days_of_week is a tuple with ints that this alarm
    is active on with Monday as 0 (like the stupid Python function
    `date.weekday()`), so we can just use `in` to determine inclusion).
    Both minutes before and after are stored as 3 or 4 bit values (so
    they can be in the same byte as the hours and mintues of the alarm),
    so if they need to be expanded then the PRAM format (and version)
    will need to be updated."""
    def __init__(self, aid, enabled, days_of_week, hour, minute,
            mins_before, mins_after):

        if not isinstance(aid, int) and not aid in range(256):
            raise Exception("Alarm ID invalid: %s" % aid)
        if not isinstance(enabled, bool):
            raise Exception("Alarm enabled (%s) not boolean." % enabled)
        if not isinstance(days_of_week, tuple):
            raise Exception("Alarm days of week not tuple: %s" % days_of_week)
        for d in days_of_week:
            if not isinstance(d, int) or not d in range(7):
                raise Exception("Alarm day of week (%s) not int (0,6)" % d)
        if not isinstance(hour, int) or not hour in range(24):
            raise Exception("Alarm hour not int (0, 23): %s" % hour)
        if not isinstance(minute, int) or not minute in range(60):
            raise Exception("Alarm minute not int (0, 59): %s" % minute)
        if not isinstance(mins_before, int) or not mins_before in range(4):
            raise Exception("Alarm mbefore not int (0, 3): %s" % mins_before)
        if not isinstance(mins_after, int) or not mins_after in range(8):
            raise Exception("Alarm mafter not int (0, 7): %s" % mins_after)

        self.aid = aid
        self.enabled = enabled
        self.days_of_week = days_of_week
        self.hour = hour
        self.minute = minute
        self.mins_before = mins_before
        self.mins_after = mins_after

    def __str__(self):
        return "%d %s %s %d:%d-%dm+%dm" % (
                self.aid, self.enabled, self.days_of_week,
                self.hour, self.minute, self.mins_before, self.mins_after)

    def to_quad(self):
        """Return aid and a bytes object with 4 bytes of this instance."""
        def c2i(c):
            """Raise if argument isn't exactly 8 chars, all of which are
            either '0' or '1', otherwise return an int (0, 255)."""
            if len(c) != 8:
                raise Exception("Given str is not 8 chars long: %s" % c)
            for i in range(8):
                if not c[i] in ("0", "1"):
                    raise Exception("Given str has non-0-or-1 value: %s" % c)
            return int(c, 2)

        if self.enabled:
            c1 = '1'
        else:
            c1 = '0'

        for d in range(7):
            if d in self.days_of_week:
                c1 = c1 + '1'
            else:
                c1 = c1 + '0'

        c1 = c2i(c1)
        c2 = c2i(bin(self.mins_after)[2:].zfill(3)
                + bin(self.hour)[2:].zfill(5))
        c3 = c2i(bin(self.mins_before)[2:].zfill(2)
                + bin(self.minute)[2:].zfill(6))

        return self.aid, bytes((c1, c2, c3, crc8_3c(c1, c2, c3)))

    # We also store all the things related to generating the alarm and stuff.
    @classmethod
    def from_quad(cls, aid, qb):
        """Take 4 bytes (as a bytes or bytearray object) in qb and return
        an Alarm instance.  Will throw if the CRC or any of the fields are
        not valid."""

        if len(qb) != 4:
            raise Exception("Given quad is not length 4: %s" % qb)

        if crc8_3c(qb[0], qb[1], qb[2]) != qb[3]:
            raise Exception("Alarm CRC8 does not match, memory is corrupt.")

        # Alarms are stored as 3 bit-fields where the first byte is:
        #     b0: `1` is alarm enabled.
        #     b1--b7: Monday--Sunday, `1` is day selected.
        # The second byte is:
        #     b0--b2: mins after (0,7) as an unsigned 3-bit int.
        #     b3--b7: hours (0, 23) as an unsigned 5-bit int.
        # Last byte is:
        #     b0,b1: mins before (0,3) as an unsigned 2-bit int.
        #     b2--b7: minutes (0,59) as an unsigned 6-bit int.
        c1 = bin(qb[0])[2:].zfill(8)  # str of binary rep.
        c2 = bin(qb[1])[2:].zfill(8)  # str of binary rep.
        c3 = bin(qb[2])[2:].zfill(8)  # str of binary rep.

        en = c1[0] == '1'

        dow = []
        for day in range(7):
            if c1[day+1] == '1':
                dow.append(day)
        dow = tuple(dow)

        ma = int(c2[:3], 2)
        h = int(c2[3:], 2)

        mb = int(c3[:2], 2)
        m = int(c3[2:], 2)

        return Alarm(aid, en, dow, h, m, mb, ma)



class StateVariablesAlarmThread():
    """This class holds all the variables that should be protected by a lock.
    They are in this (singleton) class only to make it clear to a reader which
    ones they are, and that the there is a background thread mucking with
    them.  In addition, they are related (changing some of them implies that
    others should change at the same time) so there are no setters or getters,
    and only one lock (to cover them all).
    
    The backgrount thread waits on an event, with a timeout.  So when it is in
    the LOCKED or UNLOCKED states it will set this timeout to be right after
    when it needs to change something, otherwise it is woken up when any of
    the input variables change (setting an event) and it then re-calculates
    what the current state should be.  The only things used in determining
    state are the RTC time and these variables.
    
    The flow goes something like this:  the thread waits on an event, then
    locks the variables, clears the event, mucks about to set the state, and
    then releases the lock.  The rest of this program locks the lock, mucks
    about, releases it, and then sets the event (that way, if there are
    multiple things trying to set the variables at the same time the thread
    only gets woken up once (otherwise it'll just be wasted effort)).  So the
    lock, in both cases, should be used with as a context manager (the `with`
    statement) and the event could be set within it."""

    def __init__(self):
        raise Exception("Don't instantiate, used as a singleton.")

    # Main state variable.  Should not be set anywhere else.  Instead the
    # variables below should be set (under a lock) and then the background
    # alarm thread should be woken to change this.
    state = STATE.CORRUPT

    # Wake the background thread before timeout.
    var_event = threading.Event()
    # Lock for all the variables.  Everything should use the context manager.
    var_lock = threading.Lock()

    # Variables to change under the lock.
    timezone = None  # pytz.timezone
    alarms = []  # Alarms that are set.
    # If set, do not close latch, in any state (including LOCKED).
    # We don't use the RTC time for this b/c we don't want it to be affected
    # by the user changing it, and we can't use time.time() b/c time.time()
    # may go backwards or jump forward (and we want only a minute in every
    # case), so we use time.monotonic().  The one issue is that monotonic()
    # has no 0 point so it may be negative and only the difference between
    # successive calls is meaningful.  Thankfully since if only care about the
    # difference if monotonic is less than the until time this is fine.
    # Set to None to allow non-OVERRIDE states.
    override_latch_until = None
    # If set something is wrong, and the CORRUPT state is used.
    unrecoverable_error = None
    # For displaying on the various pages.
    expected_next_state_change_at_dt_utc = None

    @classmethod
    def manually_unlock_for_a_minute(cls):
        """Unless state is LOCKED unlock the box and set the state to
        OVERRIDE, for one minute.  We don't want to allow this to be
        too long since it's just for someone to press it and immediately go
        open the box.
        
        If state is locked return False, otherwise return True."""
        with cls.var_lock:
            if cls.state == STATE.LOCKED:
                return False
            else:
                # We do not use the RTC time because we want this for a minute
                # even if the user changes the clock.  We don't know what time
                # the pi is set to and don't care, but we need to be careful
                # that we only pay attention to differeneces instead of
                # absolute times.
                cls.override_latch_until = time.monotonic() + 60.0
                cls.var_event.set()
                return True

    @staticmethod
    def are_any_alarms_firing(dt_utc, timezone, alarms):
        """Return a tuple of `(firing, timeout)` where `firing` is `True`, if
        for the given UTC datetime any alarms (that are enabled and defined
        over the timezone `timezone`) are currently firing, `False` otherwise;
        and timeout is the number of (float) seconds until the next event (an
        alarm starting or ceasing to fire).
        
        The three arguments are expected to be of types datetime (with
        tzinfo=pytz.utc), pytz.timezone, and a list of Alarm instances.
        
        This is a static method which uses no global shared state so we can
        call it from the background thread without synchronizing anything."""

        firing = False
        timeout = float('inf')

        def to_utc_before_after(alarm, dt_ymd, tz):
            """Return a list of 2-tuples.  The dt is constructed from the year,
            month, day of dt_ymd, the hour and minute from the alarm, and
            localized from the timezone tz.  Then, if the day of week is
            enabled the localized dt is converted to UTC, after which minutes
            before and after are taken from the alarm and added to it (plus
            one minute is always added to after because if there are supposed
            to be zero before and zero after then the expected thing is to have
            the alarm firing for that whole minute).  When it
            is being localized there may be two date times produced if the
            datetime falls during a discontinuity (like a daylight saving time
            change).  Therefore the returned list could have 0, 1, or 2
            elements (each of which is a 2-tuple of the UTC dt the alarm
            starts and stops firing).
            
            The `pytz` module has some interesting behaviour when localizing,
            namely if `is_dst` is not passed in it will guess which time to
            use if there is more than one possibility, if `is_dst` is None
            then it will raise either a "time does not exist" or a "time is
            amgiguous" exception if it falls over a discontinuity, and if
            `is_dst` is either `True` or `False` it will return one of the two
            possbilities (this is true even when the given time does not exist
            as it will adjust the offset to place it were it is supposed to go
            (which means it is possible to construct a datetime where after
            converting it to UTC and then back again the result is not the
            same time as the initial datetime)).  And finally, if the datetime
            does not fall over a discontinuity then it will return the same
            datetime for both `True` and `False`.
            
            Here we hang on to both possibilities and say yes it is firing for
            them both.  This means that sometimes the box may be unlocked
            twice, which is better than the alternative of it not unlocking at
            all on a given day."""
            dt_unaware = datetime.datetime(
                    dt_ymd.year, dt_ymd.month, dt_ymd.day,
                    alarm.hour, alarm.minute)
            dts_loc_t = tz.localize(dt_unaware, is_dst=True)
            dts_loc_f = tz.localize(dt_unaware, is_dst=False)

            dts_loc = set()  # Keep only one if True/Flase are the same dt.

            if dts_loc_t.weekday() in alarm.days_of_week:
                dts_loc.add(dts_loc_t)

            if dts_loc_f.weekday() in alarm.days_of_week:
                dts_loc.add(dts_loc_f)

            dts_utc_before_after = []

            for dt_loc in dts_loc:
                dt_utc = dt_loc.astimezone(pytz.utc)
                dt_utc_before = \
                        dt_utc - datetime.timedelta(minutes=alarm.mins_before)
                dt_utc_after = dt_utc + \
                        datetime.timedelta(minutes=1) + \
                        datetime.timedelta(minutes=alarm.mins_after)
                dts_utc_before_after.append((dt_utc_before, dt_utc_after))

            return dts_utc_before_after


        for alarm in alarms:
            # Skip if disabled or no days are selected (if we didn't skip days
            # of week here we couldn't back up and go forward a day at a time
            # looking for the next and most recent event easily since the
            # loop wouldn't be known to find one at some point).
            if not alarm.enabled or not alarm.days_of_week:
                continue
            # We do not want to do any time math on the local time (like
            # calculating mins_before or mins_after), so for each alarm we take
            # the year/month/day from UTC and create a localized local datetime
            # (or more than one, see the comments in the
            # `to_utc_before_after()` function) which also has the advantage of
            # not having to figure out which way the discontinuity is going
            # which means the box unlocks the latch an extra time (which is way
            # better than it not unlocking on some day it was supposed to).
            # Then we check if that date is selected, and walk it both forward
            # and back to make sure we get any alarms that are firing (we only
            # need one) and the next event (starting or stopping) after the
            # current UTC datetime.
            found_alarm_before_dt_utc = False
            found_alarm_after_dt_utc = False
            for days_adj in (0, -1, 1, -2, 2, -3, 3, -4, 4, -5, 5, -6, 6, -7,
                    7, -8, 8, -9, 9, -10, 10, -11, 11, -12, 12, -13, 13, -14,
                    14, -15, 15, -16):
                dts_before_after = to_utc_before_after(
                        alarm,
                        dt_utc + datetime.timedelta(days=days_adj),
                        timezone)

                #print("dt_utc: " + str(dt_utc), file=sys.stderr)
                #print("dts_before_after: " + str(dts_before_after), file=sys.stderr)

                for dt_b_a in dts_before_after:

                    for dt_b_a_part in dt_b_a:
                        if dt_b_a_part >= dt_utc:
                            timeout = min(timeout,
                                    (dt_b_a_part - dt_utc).total_seconds())

                    if dt_b_a[0] <= dt_utc and dt_b_a[1] > dt_utc:
                        firing = True
                        # Could break here if we didn't need to calc timeout.

                if dts_before_after:
                    if all(map(lambda x: x[1] < dt_utc, dts_before_after)):
                        found_alarm_before_dt_utc = True
                    if all(map(lambda x: x[0] > dt_utc, dts_before_after)):
                        found_alarm_after_dt_utc = True

                if found_alarm_before_dt_utc and found_alarm_after_dt_utc:
                    break

            # We check here because if that for loop made it all the way to
            # two weeks out something is wrong (probably a bug).
            if not found_alarm_before_dt_utc or not found_alarm_after_dt_utc:
                print("We tried to loop to see if any alarms were " + \
                        "firing, but none were found which is almost " + \
                        "certainly a programing error.  Alarms is: " + \
                        "%s at %s" % (alarm, dt_utc), file=sys.stderr)

        return (firing, timeout)

    @classmethod
    def background_thread(cls):
        """Thread to take the values of the "variables under lock" and set
        the state.  Will also do the annoying datetime math to figure out
        when to actually lock and unlock the box (by calling
        StateVariablesAlarmThread.are_any_alarms_firing)."""

        timeout = 0.0  # We want to set the state the first time through.
        old_state = None  # Set LED, latch, file first time through.

        while True:
            if timeout > threading.TIMEOUT_MAX:
                cls.var_event.wait(timeout=None)  # Forever.
            else:
                cls.var_event.wait(timeout=timeout)
            cls.var_event.clear()

            timeout = float('inf')  # Wait forever by defualt.
            rtc_dt_utc_now = get_datetime()
            with cls.var_lock:  # We don't want to set the event with this.
                try:
                    # In all states (including CORRUPT)
                    # the manual unlock should work.
                    if cls.override_latch_until:
                        if time.monotonic() < cls.override_latch_until:
                            timeout = \
                                cls.override_latch_until - time.monotonic()
                            boxLatch.unlock()
                        else:
                            cls.override_latch_until = None
                            boxLatch.lock()

                    if cls.override_latch_until:
                        cls.state = STATE.OVERRIDE
                        boxLED.set_state(boxLED.STATE.BLINKING_FAST)

                    elif cls.unrecoverable_error:
                        cls.state = STATE.CORRUPT
                        boxLED.set_state(boxLED.STATE.BLINKING_SLOW)

                    elif not cls.timezone:
                        cls.state = STATE.NEW
                        boxLED.set_state(boxLED.STATE.SOLID)

                    elif 0 == sum(1 for a in cls.alarms if
                            a.enabled and a.days_of_week):
                        cls.state = STATE.NOALARMS
                        boxLED.set_state(boxLED.STATE.SOLID)

                    else:
                        # We have alarms, we are UNLOCKED or LOCKED.
                        firing, timeout = \
                            StateVariablesAlarmThread.are_any_alarms_firing(
                                rtc_dt_utc_now, cls.timezone, cls.alarms)
                        if firing:
                            cls.state = STATE.UNLOCKED
                            boxLED.set_state(boxLED.STATE.BLINKING_FAST)
                            boxLatch.unlock()

                        else:
                            cls.state = STATE.LOCKED
                            boxLED.set_state(boxLED.STATE.BREATHING)
                            boxLatch.lock()

                    if old_state != cls.state:
                        old_state = cls.state
                        with open("/tmp/box_state", "w") as f:
                            f.write(cls.state.name)

                except Exception as exp:
                    timeout = float('inf')
                    cls.state = STATE.CORRUPT
                    cls.unrecoverable_error = sprint_exception(exp)
                finally:
                    try:  # Still within the var lock.
                        cls.expected_next_state_change_at_dt_utc = \
                                rtc_dt_utc_now + \
                                datetime.timedelta(seconds=int(timeout))
                    except:
                        cls.expected_next_state_change_at_dt_utc = None

# Cannot start the StateVariablesAlarmThread until after RTC init.



#########################
# PRAM Format (Version 0)
#########################
# Define an arbitrary offset so we don't use the first k of memory, for no
# good reason (but, I was using the start of memory to test things manually).
_PRAM_offset = 1500

# The signature or magic bytes we use are 9 ASCII bytes:
# "Box PRAM\0", so (in hex):  42 6f 78 20 50 52 41 4d 00, which is
# a C-style string, in case someone manually looks at the memory.
# If 7 of the 9 are there we return corrupted memory, if less than
# that we assume nothing has been written (or the battery has died).
# We do not CRC this because it's a known string, so it's just compared.
_PRAM_magic_nums = bytearray(b'Box PRAM\x00')

# Next byte is version, then we have the length of the timezone name,
# 255 max (0 means no tz is stored), then the number of (3-byte + CRC8)
# alarms, 0 to 255 of them, then the crc8 of those 3 bytes, which all
# together totals 4 bytes.
_PRAM_offset_version_quad = _PRAM_offset + len(_PRAM_magic_nums)

_PRAM_offset_timezone = _PRAM_offset_version_quad + 4
_PRAM_max_timezone_size = 255  # UTF-8 of the tz name.
_PRAM_max_number_of_alarms = 255  # Number of 4-byte alarm quads.
def _PRAM_offset_alarm_with_aid(aid):
    """Return the offset of alram with aid aid (which is just an array).
    So aid must be an int (0, 255)."""
    return _PRAM_offset_timezone + _PRAM_max_timezone_size + 4*aid

_PRAM_offset_max = _PRAM_offset_alarm_with_aid(255)

def _PRAM_read(offset, length):
    """Return a bytearray of the bytes from storage starting at offset, since
    the RTC only gives us read or write access one byte at a time."""
    ret = bytearray()
    for i in range(offset, offset + length):
        ret.append(_RTC.read_AT24C32_byte(i))
    return ret

def _PRAM_write(offset, bytes_or_bytearray):
    """Write the bytes given starting at the given offset."""
    for i in range(len(bytes_or_bytearray)):
        _RTC.write_AT24C32_byte(offset + i, bytes_or_bytearray[i])

def PRAM_clear():
    """Clear the PRAM by writing headers with nothing---the NEW state."""
    _PRAM_write(_PRAM_offset, _PRAM_magic_nums)
    _PRAM_write(
        _PRAM_offset_version_quad,
        bytes((
            _PRAM_format_version, 0, 0, crc8_3c(_PRAM_format_version, 0, 0))))

def _PRAM_write_tz_alarms():
    """Write out only if changed."""
    (       pram_storage_version,
            tz_name_length,
            alarms_count,
            ver_crc,
    ) = _PRAM_read(_PRAM_offset_version_quad, 4)

    with StateVariablesAlarmThread.var_lock:
        new_tzname = ""
        if StateVariablesAlarmThread.timezone:
            new_tzname = StateVariablesAlarmThread.timezone.zone
        new_alarms = StateVariablesAlarmThread.alarms

    if pram_storage_version != _PRAM_format_version \
            or tz_name_length != len(new_tzname) \
            or alarms_count != len(new_alarms):

        _PRAM_write(_PRAM_offset_version_quad, bytes((
            _PRAM_format_version, len(new_tzname), len(new_alarms),
            crc8_3c(_PRAM_format_version, len(new_tzname), len(new_alarms)),
            )))

    old_tzname = _PRAM_read(_PRAM_offset_timezone, tz_name_length
            ).decode('utf-8', 'strict')
    if tz_name_length != len(new_tzname) or old_tzname != new_tzname:
        _PRAM_write(_PRAM_offset_timezone,
                new_tzname.encode('utf-8', 'strict'))

    for a in new_alarms:
        aid, bytesquad = a.to_quad()
        if _PRAM_read(_PRAM_offset_alarm_with_aid(aid), 4) != bytesquad:
            _PRAM_write(_PRAM_offset_alarm_with_aid(aid), bytesquad)



try:
    # From here on out we are in a try because everything might fail, and we
    # want this module to load in every case, in order to report the error.
    if _RTC.rtc_load_error:  # Was already an error (on import).
        raise Exception()

    # If we check this here for the max size we don't have to check the
    # eeprom size on every read and write below.
    if _PRAM_offset_max > _RTC.eeprom_size:
        _RTC.rtc_load_error = "Storage module is too small " + \
            "(%d), " % _RTC.eeprom_size + \
            "it needs to hold at least %d bytes." % _PRAM_offset_max
        raise Exception()

    # Data Integrity.  We check the magic numbers by direct comparison, we
    # check the timezone by seeing if pytz knows about it, and we check each
    # alarm with a CRC.  If any fail we fail loading this module and set the
    # hardware state to CORRUPT because that means the PRAM chip is failing or
    # the data was read or written incorrectly (no error checking is done on
    # the I2C reads or writes themselves).

    # Since writes are _so_much_slower_ (0.3 secs/byte) than reads we only
    # write things when they change.  On first boot we write the magic numbers
    # and set timezone length to 0 and number of alarms to 0.  (Which slows
    # down the first boot by a couple seconds.)

    magic_nums = _PRAM_read(_PRAM_offset, len(_PRAM_magic_nums))
    n_diff = sum(1 for x in zip(magic_nums, _PRAM_magic_nums) if x[0] != x[1])

    del magic_nums

    if n_diff in (1, 2):
        _RTC.rtc_load_error = "Magic numbers were present but incorrect."
        raise Exception()
    elif n_diff > 2:
        # We assume nothing was ever written, so write the magic numbers
        # and set everything to zero, this is the NEW state (below).
        PRAM_clear()

    del n_diff

    (       pram_storage_version,
            tz_name_length,
            alarms_count,
            ver_crc,
    ) = _PRAM_read(_PRAM_offset_version_quad, 4)

    if crc8_3c(pram_storage_version, tz_name_length, alarms_count) != ver_crc:
        _RTC.rtc_load_error = "Version CRC8 didn't match.  Memory is corrupt."
        raise Exception()

    del ver_crc

    if _PRAM_format_version - 1 == pram_storage_version:
        # Normally here we would upgrade the storage format (during boot).
        _RTC.rtc_load_error = "Cannot upgrade from previous storage format."
        raise Exception()

    if _PRAM_format_version != pram_storage_version:
        _RTC.rtc_load_error = "PRAM storage format (%d" % \
                pram_storage_version + \
                ") is unsupported.  Current format version is " + \
                "%d." % _PRAM_format_version
        raise Exception()

    del pram_storage_version

    if tz_name_length == 0:
        # No tz has been set, so we are in state NEW.  If any alarms are set
        # we lose them; if we didn't setting the tz could lock the box which
        # is almost certainly not what anyone wants.
        if alarms_count != 0:
            _PRAM_write(_PRAM_offset_version_quad, bytes((
                _PRAM_format_version, 0, 0,
                crc8_3c(_PRAM_format_version, 0, 0),
                )))

        with StateVariablesAlarmThread.var_lock:
            StateVariablesAlarmThread.timezone = None
            StateVariablesAlarmThread.alarms = []
            StateVariablesAlarmThread.var_event.set()

        del tz_name_length, alarms_count

    else:
        timezone = pytz.timezone(_PRAM_read(
                    _PRAM_offset_timezone,
                    tz_name_length
                ).decode('utf-8', 'strict'))
        del tz_name_length

        alarms = []
        aid = None  # If no alarms then del will fail since loop isn't exec'd.
        for aid in range(alarms_count):
            alarms.append(Alarm.from_quad(
                aid,
                _PRAM_read(_PRAM_offset_alarm_with_aid(aid), 4)))
        del alarms_count, aid

        with StateVariablesAlarmThread.var_lock:
            StateVariablesAlarmThread.timezone = timezone
            StateVariablesAlarmThread.alarms = alarms
            StateVariablesAlarmThread.var_event.set()

        del timezone, alarms


except Exception as exp:
    # Something failed loading the info from the RTC, so we set everything
    # so some default and set the state to CORRUPT (in case it was changed).
    # The error message may have already been set (rtc_load_error), and if
    # so we ignore exp.  Otherwise we try and pull whatever information we
    # can out of exp to return.
    if not _RTC.rtc_load_error:
        _RTC.rtc_load_error = sprint_exception(exp)

    # Now we set the state to CORRUPT.
    with StateVariablesAlarmThread.var_lock:
        StateVariablesAlarmThread.unrecoverable_error = _RTC.rtc_load_error
        StateVariablesAlarmThread.var_event.set()






def get_unrecoverable_error_str():
    with StateVariablesAlarmThread.var_lock:
        return StateVariablesAlarmThread.unrecoverable_error

def get_state_name():
    with StateVariablesAlarmThread.var_lock:
        return (StateVariablesAlarmThread.state.name,
                StateVariablesAlarmThread.expected_next_state_change_at_dt_utc)

def get_timezone_name():
    with StateVariablesAlarmThread.var_lock:
        if StateVariablesAlarmThread.timezone:
            return StateVariablesAlarmThread.timezone.zone
        else:
            return "Unknown"

def set_datetime_and_timezone(y, mo, d, h, mi, s, tz):
    """Set the RTC time to the given time.  The given tz is the user timezone
    we use when displaying the time to the user.  We have to set the tz after
    setting the RTC time because setting the timezone (or any variables under
    the lock) will signal the background thread to wake up and re- calculate
    the state."""
    # Will raise if anything goes wrong setting these things.

    tz_instance = pytz.timezone(tz)  # Outside lock in case this fails.

    _RTC.write_datetime(  # Ignores the tz, but excepts UTC.
            tz_instance.localize(
                datetime.datetime(
                    int(y), int(mo), int(d),
                    int(h), int(mi), int(s)),
                is_dst=None  # Raise if dt is ambiguous, non-existant, etc.
            ).astimezone(pytz.utc))

    with StateVariablesAlarmThread.var_lock:
        StateVariablesAlarmThread.timezone = tz_instance

    _PRAM_write_tz_alarms()  # Gets the var_lock again.
    StateVariablesAlarmThread.var_event.set()

def get_alarms_for_noalarm_page():
    """This is stupid and we should fix it."""
    with StateVariablesAlarmThread.var_lock:
        return [(a.aid, str(a)) for a in StateVariablesAlarmThread.alarms]

def get_alarm_strings():
    with StateVariablesAlarmThread.var_lock:
        return [str(a) for a in StateVariablesAlarmThread.alarms]

def add_new_alarm(h, m, mb, mf, dsow):
    dsow_i = tuple(int(d) for d in dsow)
    with StateVariablesAlarmThread.var_lock:
        aid = len(StateVariablesAlarmThread.alarms)
        StateVariablesAlarmThread.alarms.append(
            Alarm(aid, True, dsow_i, int(h), int(m), int(mb), int(mf)))

    _PRAM_write_tz_alarms()  # Gets the var_lock again.
    StateVariablesAlarmThread.var_event.set()

def toggle_alarm(aid):
    with StateVariablesAlarmThread.var_lock:
        if StateVariablesAlarmThread.alarms[int(aid)].enabled:
            StateVariablesAlarmThread.alarms[int(aid)].enabled = False
        else:
            StateVariablesAlarmThread.alarms[int(aid)].enabled = True

    _PRAM_write_tz_alarms()  # Gets the var_lock again.
    StateVariablesAlarmThread.var_event.set()

def del_alarm(aid):
    with StateVariablesAlarmThread.var_lock:
        del StateVariablesAlarmThread.alarms[int(aid)]

    _PRAM_write_tz_alarms()  # Gets the var_lock again.
    StateVariablesAlarmThread.var_event.set()


def fmt_datetime(dt):
    """Will raise if dt does not have a timezone or it's not UTC."""
    if not dt:
        return "None"
    if dt.tzinfo.zone != 'UTC':
        raise Exception("Cannot format non-UTC datetime.")
    return dt.strftime('%Y-%m-%d %H:%M:%S ') + dt.tzinfo.zone

def fmt_datetime_local(dt):
    """Will raise if dt does not have a timezone or it's not UTC."""
    if not dt:
        return "None"
    if dt.tzinfo.zone != 'UTC':
        raise Exception("Cannot format non-UTC datetime.")

    with StateVariablesAlarmThread.var_lock:
        timezone = StateVariablesAlarmThread.timezone

    if timezone:
        return dt.astimezone(timezone).strftime(
                '%Y-%m-%d %H:%M:%S ') + timezone.zone
    else:
        return "Unknown b/c time zone is not set."

def get_common_timezones():
    return sorted(pytz.common_timezones)

def get_temperature_fahrenheit():

    return _RTC.getTemp() * 1.8 + 32.0

def get_datetime():
    """Return a UTC datetime class of the RTC time."""
    try:
        return pytz.UTC.localize(_RTC.read_datetime())
    except:  # If this fails it is *probably* b/c it is unset.
        return pytz.UTC.localize(datetime.datetime.utcfromtimestamp(0.0))

def fmt_datetime_until(dt_utc):
    if not dt_utc:
        return "None"
    return str(dt_utc - get_datetime())



# After all other things are defined we start the threads.
threading.Thread(
        name="boxLatch",
        target=boxLatch.background_thread,
        daemon=True,
    ).start()
threading.Thread(
        name="boxLED",
        target=boxLED.background_thread,
        daemon=True,
    ).start()
threading.Thread(
        name="StateVariablesAlarmThread",
        target=StateVariablesAlarmThread.background_thread,
        daemon=True,
    ).start()
