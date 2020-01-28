import time
import Engine.unicornhybridblack as unicornhybridblack

# connect to Device
UnicornBlack = unicornhybridblack.UnicornBlackFunctions() 
UnicornBlack.connect(deviceID='UN-2019.05.51')
time.sleep(1) # give it some initialization time

#UnicornBlack.startrecording('oddballtest')

minutes = 3

time.sleep(float(minutes)*60.0) 

UnicornBlack.disconnect()
           