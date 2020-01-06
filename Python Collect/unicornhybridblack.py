# unicornhybridblack: classes to communicate with g.tec Unicorn Hybrid Black
#
import os
import math
import numpy
import time
import copy
from datetime import datetime
from threading import Thread, Lock
from multiprocessing import Queue
import UnicornPy

class UnicornBlackFunctions():    
    """class for data collection using the g.tec Unicorn Hybrid Black
	"""
    
    def __init__(self):

        # establish variables
        self.collectversion = '2020.01.06'
        self.device = None;
        self.deviceID = None;
        
		# create a Queue and Lock
        self._queue = Queue()
        self._lock = Lock()
        
        # initialize data collectors
        self.logdata = False
        self.logfilename = None
        self._safetolog = True
        self._logqueue = None
        
        # establish parameters
        self._configuration = None
        self._numberOfAcquiredChannels = None
        self._frameLength = 1
        self._samplefreq = 250.0
        self._intsampletime = 1.0 / self._samplefreq
        self._rollingspan = 5 # seconds
        self.data = None
        self.channellabels = 'Time, FZ, C3, CZ, C4, PZ, O1, OZ, O2, AccelX, AccelY, AccelZ, GyroX, GyroY, GyroZ, Battery'
        self.arrayindx = numpy.array([15, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16])
                
        # activate
        self._receiveBuffer = None
        self.lastsampledpoint = None
        	
    def connect(self):

        # Did the user specify a particular device
        if (self.deviceID is None):
            try:
                # Get available device serials.
                deviceList = UnicornPy.GetAvailableDevices(True)
        
                if len(deviceList) <= 0 or deviceList is None:
                    raise Exception("No device available.Please pair with a Unicorn first.")
        
                # Print available device serials.
                print("Available devices:")
                i = 0
                for device in deviceList:
                    print("#%i %s" % (i,device))
                    i+=1
        
                # Request device selection.
                deviceID = int(input("Select device by ID #"))
                if deviceID < 0 or deviceID > len(deviceList):
                    raise IndexError('The selected device ID is not valid.')
                self.deviceID = deviceList[deviceID]
        
            except UnicornPy.DeviceException as e:
                print(e)
            except Exception as e:
                print("An unknown error occured. %s" %e)
                
        # Open selected device.
        try:
            self.device = UnicornPy.Unicorn(self.deviceID)
            print("Connected to '%s'." %self.deviceID)
        except:
            print("Unable to connect to '%s'." %self.deviceID)
            
        # Initialize acquisition members.
        self._numberOfAcquiredChannels = self.device.GetNumberOfAcquiredChannels()
        self._configuration = self.device.GetConfiguration()
    
        # Allocate memory for the acquisition buffer.
        self._receiveBufferBufferLength = self._frameLength * self._numberOfAcquiredChannels * 4
        self._receiveBuffer = bytearray(self._receiveBufferBufferLength)
        self.data = numpy.empty([ math.floor( float(self._rollingspan) * float(self._samplefreq) ), self._numberOfAcquiredChannels])
        self.data[:] = numpy.nan
        
        try:
    		# initialize sample streamer
            self._streaming = True
            self._ssthread = Thread(target=self._stream_samples, args=[self._queue], daemon=True)
            self._ssthread.name = 'samplestreamer'
        except:
            print("Error initializing sample streamer.")
        
        try:
            # initialize data processer
            self._processing = True
            self._dpthread = Thread(target=self._process_samples, args=[self._queue], daemon=True)
            self._dpthread.name = 'dataprocessor'
            
        except:
            print("Error initializing data recorder.")
            
        try:
            # start processes
            self.device.StartAcquisition(True)
        except:
            print("Error starting acquisition.")
            
        self._ssthread.start()
        self._dpthread.start()
        
    
    def disconnect(self):
       
        self._streaming = False
        self._processing = False
        self.logdata = False
        try:
            self.device.StopAcquisition()
        except:
            pass
                
        self._ssthread.join()
        self._dpthread.join()
        
        del self.device
        self.device = None
        
    def startacquisition(self):
        
        self._streaming = True
        self._processing = True
        
    def stopacquisition(self):
        
        self.logdata = False
        try:
            self._logfile.close()
        except:
            pass
        self._streaming = False
        self._processing = True

    def _stream_samples(self, queue):
        """Continuously polls the device, and puts all new samples in a
		Queue instance
		
		arguments
		
		queue		--	a multithreading.Queue instance, to put samples
						into
		"""
		
		# keep streaming until it is signalled that we should stop
        while self._streaming:
            # Receives the configured number of samples from the Unicorn device and writes it to the acquisition buffer.
            self.device.GetData(self._frameLength,self._receiveBuffer,self._receiveBufferBufferLength)
            
            # Convert receive buffer to numpy float array 
            sampledata = numpy.frombuffer(self._receiveBuffer, dtype=numpy.float32, count=self._numberOfAcquiredChannels * self._frameLength)
            sampledata = numpy.reshape(sampledata, (self._frameLength, self._numberOfAcquiredChannels))
            
            # put the sample in the Queue
            self.lastsampledpoint = copy.deepcopy(sampledata[0][15])
            if self._processing:
                self._lock.acquire(True)
                queue.put(sampledata)
                self._lock.release()
            
            time.sleep(self._intsampletime / 2)
                
    def _process_samples(self, queue):
        """Continuously processes samples, updating the most recent sample
				
		queue		--	a multithreading.Queue instance, to read samples
						from
		"""
		
		# keep processing until it is signalled that we should stop
        while self._processing:    
			# read new item from the queue
            if not queue.empty():
                self._lock.acquire(True)
                sampledata = queue.get()
                self._lock.release()
                
                # check if the new sample is the same as the current sample
                sampledata[:] = sampledata[:, self.arrayindx] # put counter first
                if not self.data[-1][0] == sampledata[0,0]:
                    # update current sample
                    self.data = numpy.append(self.data, sampledata, 0)
                    self.data = numpy.delete(self.data, (0), axis=0)
                    self._log_sample(sampledata)
                    
                    time.sleep(self._intsampletime / 2)

    def startloggingdata(self, logfilename='default'):
        
        self.logdata = True
        self.logfilename = logfilename
        self._logfile = open('%s.csv' % (self.logfilename), 'w')
        self._log_header()
        
    def _log_sample(self, sample):
        """Logs data to the data file
        """
        if self.logdata:
            
            sample[:,0] = float(float(sample[:,0]) * self._intsampletime) # Convert counter to time
            sample = sample[:,0:-1] # Trim off validation
            if self._logqueue is None:
                self._logqueue = sample
            else:
                self._logqueue = numpy.vstack([self._logqueue, sample])
                
            # check if it is safe to log
            if self._safetolog:
                numpy.savetxt(self._logfile,self._logqueue,delimiter=',',fmt='%.3f',newline='\n')
                self._logfile.flush() # internal buffer to RAM
                os.fsync(self._logfile.fileno()) # RAM file cache to disk
                self._logqueue = None

    def _log_header(self):
        """Logs a header to the data file
        """
        if self.logdata:
            # timestamp and note the recording parameters
            timetemp = str(datetime.now()).split()
            timetemp = timetemp[0] + 'T' + timetemp[1]
    
            header = 'collect.....= UnicornPy_' + self.collectversion + '\n'
            header = header + 'device......= ' + self.deviceID  + '\n'
            header = header + ('samplerate..= %.3f' % self._samplefreq)  + '\n'
            header = header + ('channels....= %d' % (self._numberOfAcquiredChannels - 1))  + '\n'
            header = header + 'date........= ' + timetemp  + '\n'
            header = header + 'filename....= ' + self.logfilename  + '\n'
            
            header = header + self.channellabels + '\n'
            #'Time, FZ, C3, CZ, C4, PZ, O1, OZ, O2, AccelX, AccelY, AccelZ, GyroX, GyroY, GyroZ, Battery'
            self._logfile.write(header) # to internal buffer
            self._logfile.flush() # internal buffer to RAM
            os.fsync(self._logfile.fileno()) # RAM file cache to disk
            self._firstlog = False 

            
            
            
            
            
# # # # #
# DEBUG #
if __name__ == "__main__":
    
    from psychopy import core
    
    # connect to Device
    UnicornBlack = UnicornBlackFunctions()
    UnicornBlack.deviceID = 'UN-2019.05.51'
    UnicornBlack.connect()
    
    cumulativeTime = core.Clock(); cumulativeTime.reset()
    
    UnicornBlack.startacquisition()
    UnicornBlack.startloggingdata('recordeddata')
    
    for incrX in range(10):
        core.wait(1)
        print("Time Lapsed: %d" % incrX)
    
    UnicornBlack.stopacquisition()
    
    
    print("Elapsed time: %.6f" % cumulativeTime.getTime())
    
    UnicornBlack.disconnect()
    print('Collection Complete')
    
    
    import matplotlib.pyplot as plt 
    sampleddata = UnicornBlack.data
    
    x = []
    y = []
    for incrX in range(len(sampleddata)):
        x.append(sampleddata[incrX][0] * (1 / 250.0))
        y.append(sampleddata[incrX][0])
    
    plt.plot(x,y)

# # # # #