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
#import UnicornPy as UnicornPy


class UnicornBlackFunctions():    
    """class for data collection using the g.tec Unicorn Hybrid Black
	"""
    
    def __init__(self):

        # establish variables
        self.collectversion = '2020.05.27.2'
        self.device = None;
        self.path = os.path.dirname(os.getcwd())
        self.outputfolder = 'Raw'
        
        # create a Queue and Lock
        self._queue = Queue()
        self._queuelock = Lock()
        self._logsamplequeue = Queue()
        self._logeventqueue = Queue()
        self._lock = Lock()
        self._datalock = Lock()
        self._bufferlock = Lock()
        self._loglock = Lock()
        self._logeventlock = Lock()
        
        # initialize data collectors
        self.logdata = False
        self.logfilename = None
        self._timetemp = None
        self._safetolog = False
        self._dataheaderlog = False
                
        # establish parameters
        self._configuration = None
        self._numberOfAcquiredChannels = None
        self._frameLength = 1
        self._samplefreq = 250.0
        self._intsampletime = 1.0 / self._samplefreq / 2
        self.channellabels = 'FZ, C3, CZ, C4, PZ, O1, OZ, O2, AccelX, AccelY, AccelZ, GyroX, GyroY, GyroZ, Battery, Sample'
        
        # activate
        self._receiveBuffer = None
        self.lastsampledpoint = None
        self.data = None
        
    
    def connect(self, deviceID=None, rollingspan=15.0):
        
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
            
        # Initialize acquisition members.
        self._rollingspan = rollingspan # seconds
        self._logchunksize = int(math.floor(5 * self._samplefreq))
                
        self._numberOfAcquiredChannels = self.device.GetNumberOfAcquiredChannels()
        self._configuration = self.device.GetConfiguration()
    
        # Allocate memory for the acquisition buffer.
        self._receiveBufferBufferLength = self._frameLength * self._numberOfAcquiredChannels * 4
        self._receiveBuffer = bytearray(self._receiveBufferBufferLength)
        self.data = [[0.0] * self._numberOfAcquiredChannels] * math.floor( float(self._rollingspan) * float(self._samplefreq) )
                
        try:
            # initialize sample streamer
            self._streaming = True
            self._ssthread = Thread(target=self._stream_samples, args=[self._logsamplequeue], daemon=True)
            self._ssthread.name = 'samplestreamer'
        except:
            print("Error initializing sample streamer.")
        
            
        try:
            # initialize data recorder
            self._recording = True
            self._drthread = Thread(target=self._log_sample, args=[self._logsamplequeue], daemon=True)
            self._drthread.name = 'datarecorder'
            
        except:
            print("Error initializing data recorder.")
            
            
        try:
            # initialize event recorder
            self._eventrecording = True
            self._erthread = Thread(target=self._log_event, args=[self._logeventqueue], daemon=True)
            self._erthread.name = 'eventrecorder'
            
        except:
            print("Error initializing event recorder.")
            
            
        try:
            # start processes
            self.device.StartAcquisition(False)
        except:
            print("Error starting acquisition.")
            
        self.logdata = False
        self._ssthread.start()
        self._drthread.start()
        self._erthread.start()
        print("Connection Complete")
        
    def disconnect(self):
       
        time.sleep((self._intsampletime * float(10)))
        
        #self.stoprecording()       
        self._streaming = False
        self._ssthread.join()
        self._drthread.join()
        self._erthread.join()
	
        try:
            self.device.StopAcquisition()
        except:
            pass
                
        try:
            self._logfile.close()
        except:
            pass
        
        del self.device
        self.device = None
        print("Disconnection Complete")
        
    def _stream_samples(self, queue):
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
                # Receives the configured number of samples from the Unicorn device and writes it to the acquisition buffer.
                self.device.GetData(self._frameLength,self._receiveBuffer,self._receiveBufferBufferLength)
                # Convert receive buffer to numpy float array 
                sampledata = numpy.frombuffer(self._receiveBuffer, dtype=numpy.float32, count=self._numberOfAcquiredChannels * self._frameLength)
                sampledata = numpy.reshape(sampledata, (self._frameLength, self._numberOfAcquiredChannels))
                boolgetdata = True
            except:
                self._receiveBufferBufferLength = self._frameLength * self._numberOfAcquiredChannels * 4
                self._receiveBuffer = bytearray(self._receiveBufferBufferLength)
                print('\n\nMotherfucking overflow error in polling device.\n\n') 
            self._bufferlock.release()
            
            
            if boolgetdata:   
                self._queuelock.acquire(True)
                if not (str(int(float(self.data[-1][15]))) == str(int(float(sampledata[0][15])))): # protect against sampling the same point twice    
                    #self.lastsampledpoint = copy.deepcopy(sampledata[0][15])
                    self.lastsampledpoint = str(int(float(sampledata[0][15])))
                    queue.put(sampledata)
                    self.data.append(sampledata[0]) 
                    self.data.pop(0)
                self._queuelock.release()
                
                self._bufferlock.acquire(True)
                self._receiveBuffer = bytearray(self._receiveBufferBufferLength) # make sure everything is cleared
                self._bufferlock.release()
        
            time.sleep(self._intsampletime)
            
        self._queuelock.acquire(True)
        queue.put(None) # poison pill approach
        self._queuelock.release()
        self._eventrecording = False
        

    def _log_sample(self, logqueue):
        """Continuously log samples
				
		queue		--	a multithreading.Queue instance, to read samples
						from
		"""
        
        templogholding = None
        finalpush = False
        # keep trying to log until it is signalled that we should stop
        while self._recording:   
            # read new item from the queue 
            while not logqueue.empty():
                self._loglock.acquire(True)
                sampledata = logqueue.get()
                self._loglock.release()
                
                if sampledata is None:
                    # Poison pill means shutdown
                    self._recording = False
                    finalpush = True
                    break
                    break
                else:
                    if self.logdata:
                        if templogholding is None:
                            templogholding = sampledata[:,0:-1]
                        else:
                            templogholding = numpy.vstack([templogholding, sampledata[:,0:-1]])
                            
                        # check if it is safe to log
                        if self._safetolog:
                            # only write chunks of data to save I/O overhead
                            if (len(templogholding) >= self._logchunksize):
                                numpy.savetxt(self._logfile,templogholding,delimiter=',',fmt='%.3f',newline='\n')
                                self._logfile.flush() # internal buffer to RAM
                                os.fsync(self._logfile.fileno()) # RAM file cache to disk
                                templogholding = None            
        if finalpush:
            if templogholding is not None:
                numpy.savetxt(self._logfile,templogholding,delimiter=',',fmt='%.3f',newline='\n')
                self._logfile.flush() # internal buffer to RAM
                os.fsync(self._logfile.fileno()) # RAM file cache to disk
                templogholding = None
                self._logfile.close()

    def _log_event(self, logeventqueue):
        """Continuously log events
				
		logeventqueue	--	a multithreading.Queue instance, to read samples
						from
		"""
        eventheaderlog = False
        templogholding = None
        # keep trying to log until it is signalled that we should stop
        while self._eventrecording:   
            # read new item from the queue 
            while not logeventqueue.empty():
                self._logeventlock.acquire(True)
                sampledata = logeventqueue.get()
                self._logeventlock.release()
            
                # wait to create file until we know there is a need
                if self.logdata:
                    if not eventheaderlog:
                        header = 'collect.....= UnicornPy_' + self.collectversion + '\n'
                        header = header + 'date........= ' + self._timetemp  + '\n'
                        header = header + 'filename....= ' + self.logfilename  + '\n'
                        header = header + 'Latency, Event' + '\n'
                        self._eventlogfile = open('%s.csve' % (self.logfilename), 'w')
                        self._eventlogfile.write(header) # to internal buffer
                        self._eventlogfile.flush() # internal buffer to RAM
                        os.fsync(self._eventlogfile.fileno()) # RAM file cache to disk  
                        eventheaderlog = True 
                    
                if sampledata is None:
                    # Poison pill means shutdown
                    self._eventrecording = False
                    break
                    break
                else:
                    if self.logdata:
                        if templogholding is None:
                            templogholding = sampledata
                        else:
                            templogholding = numpy.vstack([templogholding, sampledata])
                            
                        # check if it is safe to log
                        if self._safetolog:
                            # only write chunks of data to save I/O overhead
                            if (len(templogholding) >= self._logchunksize):
                                numpy.savetxt(self._eventlogfile,templogholding,delimiter=',',fmt='%.3f',newline='\n')
                                self._eventlogfile.flush() # internal buffer to RAM
                                os.fsync(self._eventlogfile.fileno()) # RAM file cache to disk
                                templogholding = None            
        
        if templogholding is not None:
                numpy.savetxt(self._eventlogfile,templogholding,delimiter=',',fmt='%s',newline='\n')
                self._eventlogfile.flush() # internal buffer to RAM
                os.fsync(self._eventlogfile.fileno()) # RAM file cache to disk
                templogholding = None
                self._eventlogfile.close()
        
        
    def startrecording(self, logfilename='default'):
        
        self.logdata = True
        self.logfilename = self.path + os.path.sep + self.outputfolder + os.path.sep + logfilename
        timetemp = str(datetime.now()).split()
        self._timetemp = timetemp[0] + 'T' + timetemp[1]
        self._logfile = open('%s.csv' % (self.logfilename), 'w')
        self._safetolog = True
        self._log_header()
        
        # ensure we are getting data
        nc = 0
        while (str(int(float(self.data[-1][15]))) == str(int(float(0.0)))):
            nc = nc + 1
        
        print("Starting Recording")
	
                        
    def _log_header(self):
        """Logs a header to the data file
        """
        if not self._dataheaderlog: 
            header = 'collect.....= UnicornPy_' + self.collectversion + '\n'
            header = header + 'device......= ' + self.deviceID  + '\n'
            header = header + ('samplerate..= %.3f' % self._samplefreq)  + '\n'
            header = header + ('channels....= %d' % (self._numberOfAcquiredChannels - 1))  + '\n'
            header = header + 'date........= ' + self._timetemp  + '\n'
            header = header + 'filename....= ' + self.logfilename  + '\n'
            
            header = header + self.channellabels + '\n'
            #'FZ, C3, CZ, C4, PZ, O1, OZ, O2, AccelX, AccelY, AccelZ, GyroX, GyroY, GyroZ, Battery, Sample'
            self._logfile.write(header) # to internal buffer
            self._logfile.flush() # internal buffer to RAM
            os.fsync(self._logfile.fileno()) # RAM file cache to disk
            self._dataheaderlog = True 
       
            
    def mark_event(self, event):
        """Logs data to the event file
        """
        if self.lastsampledpoint is not None:
            self._logeventlock.acquire(True)
            self._logeventqueue.put(numpy.array([str(self.lastsampledpoint), str(event)]))
            self._logeventlock.release()
        

            
            
            
# # # # #
# DEBUG #
if __name__ == "__main__":
    
    from psychopy import core
    
    cumulativeTime = core.Clock(); cumulativeTime.reset()
    
    UnicornBlack = UnicornBlackFunctions()   
    
    UnicornBlack.connect(deviceID='UN-2019.05.51', rollingspan=10)
    
    UnicornBlack.startrecording('recordeddata')
    
    for incrX in range(20):
        time.sleep(1)
        UnicornBlack.mark_event(incrX)
        print("Time Lapsed: %d second" % (incrX+1))
        
    UnicornBlack.disconnect()
    
    print("Elapsed time: %.6f" % cumulativeTime.getTime())
    
    # Plotting function to check for dropped samples
    import matplotlib.pyplot as plt 
    #sampleddata = UnicornBlack.data
    
    #selectsampleddata = []
    #for incrX in range(len(sampleddata)):
    #    if not (sampleddata[incrX][0] == float(0)):
    #        selectsampleddata.append(sampleddata[incrX])
    #sampleddata = numpy.array(selectsampleddata)
    #del selectsampleddata
    
    #if (sampleddata.shape[0]) > 2:
    #    x = numpy.arange(sampleddata[0][15],sampleddata[-1][15],1) 
    #    y = numpy.array([0] * len(x))
    #    for incrX in range(len(sampleddata)):
    #        index_min = numpy.argmin(abs(x-(sampleddata[incrX][15])))
    #        #y[index_min] = sampleddata[incrX][15]
    #        y[index_min] = 1
    #    del index_min, incrX
    #    x = x * (1/ 250.0)
    #    plt.plot(x,y)
    #    print('The streamer had a total of %d dropped samples (%0.1f%%).' %(len(y)-numpy.count_nonzero(y), ((len(y)-numpy.count_nonzero(y))/len(y))*100))
        
    # show saved data
    lis = []
    with open("C:\\Studies\\Python Collect\\Gentask\\Raw\\recordeddata.csv", "rb") as f: 
        for cnt, line in enumerate(f):
            lis.append(line.decode("utf-8").split(','))
    f.close()
    del cnt, line
    lis = lis[7:-1]
    x2 = numpy.arange(int(float(lis[0][15])),int(float(lis[-1][15])),1) 
    y2 = numpy.array([0] * len(x2))
    for incrX in range(len(lis)):
        index_min = numpy.argmin(abs(x2-(int(float(lis[incrX][15])))))
        y2[index_min] = 1
    del index_min, incrX
    
    
    # read in event markers
    eventlis = []
    with open("C:\\Studies\\Python Collect\\Gentask\\Raw\\recordeddata.csve", "rb") as f: 
        for cnt, line in enumerate(f):
            eventlis.append(line.decode("utf-8").split(','))
    f.close()
    del cnt, line
    eventlis = eventlis[4:-1]
    
    y3 = numpy.array([0] * len(x2))
    for incrX in range(len(eventlis)):
        index_min = numpy.argmin(abs(x2-(int(float(eventlis[incrX][0])))))
        y3[index_min] = 2
    del index_min, incrX
    
    x2 = x2 * (1/ 250.0)
    plt.plot(x2,y2)
    plt.plot(x2,y3)
    print('The recording had a total of %d dropped samples (%0.1f%%).' %(len(y2)-numpy.count_nonzero(y2), ((len(y2)-numpy.count_nonzero(y2))/len(y2))*100))
    
    
    # core.wait was responsible for the dropped samples!
    

# # # # #
