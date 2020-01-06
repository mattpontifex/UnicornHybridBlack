from psychopy import visual, core, event, logging, gui
from psychopy.constants import *  # things like STARTED, FINISHED
import numpy
import os  # handy system and path functions
import warnings
warnings.simplefilter('ignore')
logging.console.setLevel(logging.CRITICAL)
from datetime import datetime

import UnicornPy

FrameLength = 250;
AcquisitionDurationInSeconds = 1;
DataFile = "data.csv";

deviceList = UnicornPy.GetAvailableDevices(True)
device = UnicornPy.Unicorn(deviceList[0])

numberOfAcquiredChannels = device.GetNumberOfAcquiredChannels()
configuration = device.GetConfiguration()
numberOfGetDataCalls = int(AcquisitionDurationInSeconds * UnicornPy.SamplingRate / FrameLength);

# Allocate memory for the acquisition buffer.
receiveBufferBufferLength = FrameLength * numberOfAcquiredChannels * 4
receiveBuffer = bytearray(receiveBufferBufferLength)
        
# Create a file to store data.
file = open(DataFile, "wb")
 
device.StartAcquisition(True)
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
    
    numpy.savetxt(file,data,delimiter=',',fmt='%.3f',newline='\n')
    
 
device.StopAcquisition()
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