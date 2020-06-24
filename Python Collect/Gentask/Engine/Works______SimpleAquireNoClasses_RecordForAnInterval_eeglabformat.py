from psychopy import visual, core, event, logging, gui
from psychopy.constants import *  # things like STARTED, FINISHED
import math
import time
import numpy
import os  # handy system and path functions
import warnings
warnings.simplefilter('ignore')
logging.console.setLevel(logging.CRITICAL)

import Engine.UnicornPy as UnicornPy

FrameLength = 1;
AcquisitionDurationInSeconds = 30;
DataFile = "data.csv";
channellabels = 'FZ, C3, CZ, C4, PZ, O1, OZ, O2, AccelX, AccelY, AccelZ, GyroX, GyroY, GyroZ, Battery, Sample'
        

deviceList = UnicornPy.GetAvailableDevices(True)
device = UnicornPy.Unicorn(deviceList[0])
deviceID = deviceList[0]

numberOfAcquiredChannels = device.GetNumberOfAcquiredChannels()
configuration = device.GetConfiguration()
numberOfGetDataCalls = int(AcquisitionDurationInSeconds * UnicornPy.SamplingRate / FrameLength);

# Allocate memory for the acquisition buffer.
receiveBufferBufferLength = FrameLength * numberOfAcquiredChannels * 4
receiveBuffer = bytearray(receiveBufferBufferLength)
        
# Create a file to store data.
file = open(DataFile, "w")
header = 'collect.....= UnicornPy_2020.05.27.2\n'
header = header + 'device......= ' + deviceID  + '\n'
header = header + 'samplerate..= 250.000\n'
header = header + 'channels....= 16\n'
header = header + 'date........= 2020-05-29T07:45:30.221483\n'
header = header + 'filename....= none\n'

header = header + channellabels + '\n'
file.write(header) # to internal buffer
file.flush() # internal buffer to RAM
os.fsync(file.fileno()) # RAM file cache to disk
_samplefreq = 250.0
_rollingspan = 15.0
_intsampletime = 1.0 / _samplefreq / 1
masterdata = None
 
device.StartAcquisition(False) # True - test signal; False - measurement mode
cumulativeTime = core.Clock(); cumulativeTime.reset()
masterlatency = []

# Acquisition loop.
for i in range (0,numberOfGetDataCalls):
    # Receives the configured number of samples from the Unicorn device and writes it to the acquisition buffer.
    cumulativeTime.reset()
    device.GetData(FrameLength,receiveBuffer,receiveBufferBufferLength)
    masterlatency.append(cumulativeTime.getTime())

    # Convert receive buffer to numpy float array 
    data = numpy.frombuffer(receiveBuffer, dtype=numpy.float32, count=numberOfAcquiredChannels * FrameLength)
    data = numpy.reshape(data, (FrameLength, numberOfAcquiredChannels))
    
    if masterdata is None:
        masterdata = data[:,0:-1]
    else:
        masterdata = numpy.vstack([masterdata, data[:,0:-1]])
        
    time.sleep(_intsampletime)
     
device.StopAcquisition()

numpy.savetxt(file,masterdata,delimiter=',',fmt='%.3f',newline='\n')
file.flush() # internal buffer to RAM
os.fsync(file.fileno()) # RAM file cache to disk
file.close()
del receiveBuffer
del device

print("Write time: %.6f" % numpy.sum(masterlatency))
#0.001699 to write 250
#0.001217 to write 50

#1.011068 to read 250      net 1.006973
#0.200565 to read 50       net 1.002359
#0.003858 to read 1        net 0.948200


#CH1 - FZ
#CH2 - C3
#CH3 - CZ
#CH4 - C4
#CH5 - PZ
#CH6 - O1
#CH7 - OZ
#CH8 - O2
#CH9 - AccelX
#CH10 - AccelY
#CH11 - AccelZ
#CH12 - GyroX
#CH13 - GyroY
#CH14 - GyroZ
#CH15 - Battery
#CH16 - Counter
#CH17 - Validation