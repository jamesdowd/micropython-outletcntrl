# This file is executed on every boot (including wake-boot from deepsleep)
#outlet 0.5.0
import gc
import webrepl
from ntptime import settime
import utime

settime()

webrepl.start()
gc.collect()

print("Socket 0.5.0: Boot!")
