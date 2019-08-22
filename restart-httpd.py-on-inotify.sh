#!/bin/sh

# This script is not that solid.  We should be using a systemd unit.
# This is called from the boot scripts and from the inotifyd below,
# in both cases (and if it's called by hand) we should (re)start and
# then exit.  Inotifyd and the restart if the server fails on its
# own are run in the background if they aren't running, and if they
# are this script will kill the current proc and expect them to
# restart it.
# We do the restart thing by an argument that is really only called
# from within this script that does not exit, but just keeps
# restarting httpd.py, with a timeout so that we don't try an
# restart a million times a second if the script immedeately fails.


exec </dev/null >>/home/tc/box.log 2>&1


if [[ "$1" == "RESTART_ONLY" ]]; then
    # We should not exit here, unless something is wrong.
    # This block should start httpd.py and whenever it exits
    # start it again, with a time limit.  The kill script below
    # waits a little less than a second, so we _never_ attempt
    # a restart faster than that, and back off from there, if
    # we are within the restart limit, 5 minutes.
    # Also, this shell can't do arithmatic with fractional
    # numbers so we are restricted to one second precision.
    MAX_WAIT_SECS=$((12))
    # MAX_WAIT_SECS=$((60*5)) # This shit is too long.
    MIN_WAIT_SECS=1
    CURRENT_WAIT_SECS=$MIN_WAIT_SECS

    while : ; do
        if [[ -n "$(pidof httpd.py)" ]]; then
            echo "$0: httpd.py ALREADY exists!  Eek!  Exiting." >&2
            exit 1
        fi

        # No waiting the first time.
        echo "$0: Starting python-httpd." >&2
        START_TIME=$(awk -F '[. ]' 'NR == 1 {print $1}' /proc/uptime)
        /home/tc/httpd.py
        END_TIME=$(awk -F '[. ]' 'NR == 1 {print $1}' /proc/uptime)
        DURATION=$((END_TIME-START_TIME))

        # We lock the latch in case it was left unlocked.
        /home/tc/lock_box_latch.py
        rm -f "/tmp/box_state"  # So we can log in if the server dies.

        if [[ $DURATION -gt $MAX_WAIT_SECS ]]; then
            CURRENT_WAIT_SECS=$MIN_WAIT_SECS
            continue
        fi

        echo "$0: Waiting $CURRENT_WAIT_SECS seconds to restart." >&2
        sleep $CURRENT_WAIT_SECS

        CURRENT_WAIT_SECS=$((2*CURRENT_WAIT_SECS))
        if [[ $CURRENT_WAIT_SECS -ge $MAX_WAIT_SECS ]]; then
            CURRENT_WAIT_SECS=$MAX_WAIT_SECS
        fi
    done

    echo "Something failed in RESTART_ONLY." >&2
    exit 1  # If we get here something broke.
fi


PROG=$(realpath "$0")

# Inotify when the file is closed for writing (touch won't work).
if [[ -z "$(pgrep inotifyd)" ]]; then
    echo "Starting inotifyd to watch httpd.py." >&2
    ( /usr/sbin/inotifyd "$PROG" "/home/tc/httpd.py:w" & ) &
fi

RESTART_ONLY_PID=$(pgrep -of "${PROG##*/} RESTART_ONLY")
if [[ -z "$RESTART_ONLY_PID" ]]; then
    echo "Starting httpd.py RESTART_ONLY." >&2
    ( "$PROG" RESTART_ONLY & ) &
else
    # The restart script is already running so we kill it, so
    # that it will be restarted.
    echo "Killing existing httpd.py." >&2
    kill $(pidof httpd.py)
    sleep 0.4  # These two sleeps must be less than min restart time.
    if [[ -n "$(pidof httpd.py)" ]]; then
        kill -9 $(pidof httpd.py)
    fi
    sleep 0.4  # These two sleeps must be less than min restart time.
    # If that doesn't kill it there is likely no reason to keep
    # trying, so just print a message...
    if [[ -n "$(pidof httpd.py)" ]]; then
        echo "Could not kill httpd.py in a timely fashion." >&2
    fi
fi
