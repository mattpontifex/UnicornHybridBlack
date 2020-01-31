# unicornhybridblack: classes to communicate with g.tec Unicorn Hybrid Black
#
import os
import math
import numpy
import time
from datetime import datetime
from threading import Thread, Lock
from multiprocessing import Queue
import Engine.UnicornPy as UnicornPy


class UnicornBlackFunctions():    
    """class for data collection using the g.tec Unicorn Hybrid Black
	"""
    
    def __init__(self):

        # establish variables
        self.collectversion = '2020.01.28.1'
        self.device = None;
        self.path = os.path.dirname(os.getcwd())
        self.outputfolder = 'Raw'
        
        # create a Queue and Lock
        self._queue = Queue()
        self._queuelock = Lock()
        self._bufferlock = Lock()
        self._logeventqueue = Queue()
        self._logeventqueuelock = Lock()
        self.lastsampledpoint = None
        
        self.channellabels = ['FZ', 'C3', 'CZ', 'C4', 'PZ', 'O1', 'OZ', 'O2', 'AccelX', 'AccelY', 'AccelZ', 'GyroX', 'GyroY', 'GyroZ', 'Battery', 'Sample']
        self._samplefreq = 250.0
        self._intsampletime = 0.5 / self._samplefreq
        self._logchunksize = int(math.floor(5 * self._samplefreq))
        self.rollingspan = 5
        self._rollingdatasize = int(math.floor(self.rollingspan * self._samplefreq))
        self.data = None
        self._numberOfAcquiredChannels = 17
        self._timetemp = None
        self._streaming = False
        self._recording = False
        
        self._booldatarecord = False
        self._booleventrecord = False
        self.safetolog = True
        
        
        
    def connect(self, deviceID=None):
        self.deviceID = deviceID
        
        
        self.deviceID = deviceID;
        # make sure everything is disconnected
        try:
            self.device.StopAcquisition()
        except:
            pass
        del self.device
        self.device = None
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
        
        # Allocate memory for the acquisition buffer.
        self._numberOfAcquiredChannels = self.device.GetNumberOfAcquiredChannels()
        self._receiveBufferBufferLength = self._frameLength * self._numberOfAcquiredChannels * 4
        self._receiveBuffer = bytearray(self._receiveBufferBufferLength)
        
        # recalculate in case parameters were reset
        self._rollingdatasize = int(math.floor(self.rollingspan * self._samplefreq))
        self.data = [[0.0] * int(self._numberOfAcquiredChannels)] * int(self._rollingdatasize)
                
        
        try:
            # initialize data sampler
            self._streaming = True
            self._datasamplerthread = Thread(target=self._sample_data_thread, args=[self._queue], daemon=True)
            self._datasamplerthread.name = 'datasampler'
            self._datasamplerthread.start()
            print("Connection Complete")
        except:
            print("Error initializing data sampler.")
            
        
        
    def _clearqueue(self):
        while not self._queue.empty():
            self._queue.get()
        while not self._logeventqueue.empty():
            self._logeventqueue.get()
            
            
    def disconnect(self):
      
        self._streaming = False
        self._recording = False
        self._datasamplerthread.join()
        if self._booldatarecord:
            self._dataloggerthread.join()
            self._eventloggerthread.join()
            
            self._logfile.close() # close log file   
              
            # close eventlog file
            if self._booleventrecord:
                self._eventlogfile.close()
                
        try:
            self.device.StopAcquisition()
        except:
            pass
                
        del self.device
        self.device = None
                
        print("Disconnection Complete")
        self._clearqueue()
        
        
    def startrecording(self, logfilename='default'):
        
        self._recording = True   
        timetemp = str(datetime.now()).split()
        self._timetemp = timetemp[0] + 'T' + timetemp[1]
        self.logfilename = self.path + os.path.sep + self.outputfolder + os.path.sep + logfilename
        self.logfilename = logfilename
        
        header = 'collect.....= UnicornPy_' + self.collectversion + '\n'
        header = header + 'device......= ' + self.deviceID  + '\n'
        header = header + ('samplerate..= %.3f' % self._samplefreq)  + '\n'
        header = header + ('channels....= %d' % (self._numberOfAcquiredChannels - 1))  + '\n'
        header = header + 'date........= ' + self._timetemp  + '\n'
        header = header + 'filename....= ' + self.logfilename  + '\n'
        for incrX in range(len(self.channellabels)):
            header = header + self.channellabels[incrX]
            if (incrX < len(self.channellabels)):
                header = header + ','
        header = header + '\n'
        
        # initialize file out
        self._logfile = open('%s.csv' % (self.logfilename), 'w')
        self._logfile.write(header) # to internal buffer
        self._logfile.flush() # internal buffer to RAM
        os.fsync(self._logfile.fileno()) # RAM file cache to disk  
        self._booldatarecord = True
        
        self.eventheader = 'collect.....= UnicornPy_' + self.collectversion + '\n'
        self.eventheader = self.eventheader + 'date........= ' + self._timetemp  + '\n'
        self.eventheader = self.eventheader + 'filename....= ' + self.logfilename  + '\n'
        self.eventheader = self.eventheader + 'Latency, Event' + '\n'         
        
        try:
            # initialize data logger
            self._dataloggerthread = Thread(target=self._data_logger_thread, args=[self._queue], daemon=True)
            self._dataloggerthread.name = 'datalogger'
            self._dataloggerthread.start()
            self._datalogging = True
        except:
            print("Error initializing data logger.")
        try:
            # initialize event logger
            self._eventloggerthread = Thread(target=self._event_logger_thread, args=[self._logeventqueue], daemon=True)
            self._eventloggerthread.name = 'eventlogger'
            self._eventloggerthread.start()
            self._eventlogging = True
        except:
            print("Error initializing event logger.")
        
        print("Starting Recording")    


    def mark_event(self, event):
        """Logs data to the event file
        """
        if self.lastsampledpoint is not None:
            self._logeventqueuelock.acquire(True)
            self._logeventqueue.put(numpy.array([str(self.lastsampledpoint), str(event)]))
            self._logeventqueuelock.release()
            
            
            
    def _sample_data_thread(self, queue):
        """Continuously polls the device, and puts all new samples in a
		Queue instance
		
		arguments
		
		queue		--	a multithreading.Queue instance, to put samples
						into
		"""
		
        # keep streaming until it is signalled that we should stop
        while self._streaming:
            boolgetdata = False
            self._bufferlock.acquire(True)
            try:
                #sampledata = [numpy.ndarray.tolist(numpy.multiply(numpy.random.rand(int(self._numberOfAcquiredChannels)), 100))]
                self.device.GetData(self._frameLength,self._receiveBuffer,self._receiveBufferBufferLength)
                # Convert receive buffer to numpy float array 
                sampledata = numpy.frombuffer(self._receiveBuffer, dtype=numpy.float32, count=self._numberOfAcquiredChannels * self._frameLength)
                sampledata = numpy.reshape(sampledata, (self._frameLength, self._numberOfAcquiredChannels))
                boolgetdata = True
            except:
                pass
            self._bufferlock.release()
                
            if boolgetdata:   
                self._queuelock.acquire(True)
                if not (str(self.lastsampledpoint) == str(sampledata[0][15])): # protect against sampling the same point twice
                    self.lastsampledpoint = str(sampledata[0][15])
                    queue.put(sampledata)
                    self.data.append(sampledata[0]) 
                    self.data.pop(0)
                self._queuelock.release()
            
            time.sleep(self._intsampletime)
            
        self._queuelock.acquire(True)
        queue.put(None) # poison pill approach
        self._queuelock.release()
        
     
        
    def _data_logger_thread(self, queue):
        templogholding = None
        # keep logging until it is signalled that we should stop
        while self._recording:  
            # read new item from the queue
            while not queue.empty():
                self._queuelock.acquire(True)
                queueinsample = queue.get()
                self._queuelock.release()
                
                if queueinsample is None:
                    # Poison pill means shutdown
                    self._recording = False
                    break
                    break
                else: 
                    # chunk data
                    if templogholding is None:
                        templogholding = queueinsample
                    else:
                        templogholding = numpy.vstack([templogholding, queueinsample])
                    
                    # only write chunks of data to save I/O overhead
                    if self.safetolog:
                        if (len(templogholding) >= self._logchunksize):
                            numpy.savetxt(self._logfile,templogholding,delimiter=',',fmt='%.3f',newline='\n')
                            self._logfile.flush() # internal buffer to RAM
                            os.fsync(self._logfile.fileno()) # RAM file cache to disk
                            templogholding = None  
                            
                time.sleep(self._intsampletime)
                        
        # processing is completed; push final data
        if templogholding is not None:
            numpy.savetxt(self._logfile,templogholding,delimiter=',',fmt='%.3f',newline='\n')
            self._logfile.flush() # internal buffer to RAM
            os.fsync(self._logfile.fileno()) # RAM file cache to disk
            templogholding = None
                              
               
                
    def _event_logger_thread(self, queue):
        templogholding = None
        # keep logging until it is signalled that we should stop
        while self._recording:   
            # read new item from the queue
            while not queue.empty():
                self._logeventqueuelock.acquire(True)
                queueinsample = queue.get()
                self._logeventqueuelock.release()
                
                if queueinsample is None:
                    # Poison pill means shutdown
                    self._recording = False
                    break
                    break
                else:  
                    # if we need to create the file - go ahead and do so
                    if not self._booleventrecord:
                        self._eventlogfile = open('%s.csve' % (self.logfilename), 'w')
                        self._eventlogfile.write(self.eventheader) # to internal buffer
                        self._eventlogfile.flush() # internal buffer to RAM
                        os.fsync(self._eventlogfile.fileno()) # RAM file cache to disk  
                        self._booleventrecord = True
                        
                    # chunk data
                    if templogholding is None:
                        templogholding = queueinsample
                    else:
                        templogholding = numpy.vstack([templogholding, queueinsample])
                
                    # only write chunks of data to save I/O overhead
                    if self.safetolog:
                        if (len(templogholding) >= self._logchunksize):
                            numpy.savetxt(self._eventlogfile,templogholding,delimiter=',',fmt='%s',newline='\n')
                            self._eventlogfile.flush() # internal buffer to RAM
                            os.fsync(self._eventlogfile.fileno()) # RAM file cache to disk
                            templogholding = None   
                
                time.sleep(self._intsampletime)
         
        # processing is completed; push final data
        if templogholding is not None:
            numpy.savetxt(self._eventlogfile,templogholding,delimiter=',',fmt='%s',newline='\n')
            self._eventlogfile.flush() # internal buffer to RAM
            os.fsync(self._eventlogfile.fileno()) # RAM file cache to disk
            templogholding = None     
        
        
        



if __name__ == "__main__":

    UnicornBlack = UnicornBlackFunctions()   
    
    UnicornBlack.connect(deviceID='UN-2019.05.51')
    time.sleep(2)
    UnicornBlack.startrecording()
    UnicornBlack.mark_event(5)
    time.sleep(15)
    UnicornBlack.mark_event(5)
    UnicornBlack.disconnect()
    
