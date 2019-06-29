#!/usr/local/bin/python3.6 -u

"""This is called from the bash script that monitors the python process.
If it gets killed with the latch unlocked it may stay that way eating power
and burning out the solenoid; so the bash script calls this just to be sure.
"""

import RPi.GPIO
RPi.GPIO.setmode(RPi.GPIO.BOARD)
RPi.GPIO.setup(11, RPi.GPIO.OUT)
RPi.GPIO.output(11, RPi.GPIO.LOW)
