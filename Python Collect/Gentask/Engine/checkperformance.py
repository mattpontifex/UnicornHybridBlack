import os
from os.path import exists
from sys import platform
try:
    import Engine.xcat as xcat
except:
    import xcat as xcat
try:
    import Engine.eegpipe as eegpipe
except:
    import eegpipe as eegpipe
import numpy
import scipy
from tkinter import Tk     # from tkinter import Tk for Python 3.x
from tkinter.filedialog import askopenfilename
import matplotlib.pyplot
from matplotlib.colors import ListedColormap, LinearSegmentedColormap

import tkinter 
import tkinter.ttk 
from PIL import ImageTk 
import time
from threading import Thread
from multiprocessing import Queue
import gc
from alive_progress import alive_bar

from alive_progress.animations.spinners import alongside_spinner_factory, scrolling_spinner_factory
#bouncing_spinner_factory, delayed_spinner_factory, frame_spinner_factory, \
#scrolling_spinner_factory, sequential_spinner_factory

#https://github.com/rsalmei/alive-progress
#pip install alive-progress


def performancereporter(task):
    gc.collect()
    showoutput = False
    eggchunk = None
    wavechunk = None
    barchunks = None
    _baractive = False
    
    # create custom theme to avoid using characters that will not show
    _arrows_left = scrolling_spinner_factory('.·˂', 6, 3, right=False)
    _arrows_right = scrolling_spinner_factory('.·˃', 6, 3, right=True)
    arrows_in = alongside_spinner_factory(_arrows_right, _arrows_left)
    
    #with alive_bar(total=0, title='..processing...', unknown='arrows_in', spinner='classic', monitor=False, stats=True) as bar:
    with alive_bar(total=0, title='..Processing data..', unknown=arrows_in, spinner='classic', monitor=False, stats=True) as bar:
        _baractive = True
    
        filin = task.outputfile.split('.')[0]
        filin = os.path.split(filin)[1]
        if filin[0:2] == 'OB':
            # oddball task
            [eggchunk, wavechunk, barchunks] = checkoddballperf(task, showoutput)
            
        elif filin[0:2] == 'FT':
            # flanker task
            [eggchunk, wavechunk, barchunks] = checkflankerperf(task, showoutput)
            
        elif filin[0:3] == 'N2B':
            # flanker task
            [eggchunk, wavechunk, barchunks] = checkn2backperf(task, showoutput)
            
        elif filin[0:3] == 'CN2B':
            # flanker task
            [eggchunk, wavechunk, barchunks] = checkcontinousn2backperf(task, showoutput)
    if _baractive:
        _baractive = True
        bar() 
        _baractive = False
        
    with alive_bar(total=0, title='..Loading results..', unknown=arrows_in, spinner='classic', monitor=False, stats=True) as bar:
        _baractive = True
        if not ((eggchunk == None) and (wavechunk == None) and (barchunks == None)):
            fig = matplotlib.pyplot.figure(figsize=(20, 12))
            eegpipe.reportingwindow(fig, eggs=eggchunk, waveforms=wavechunk, bars=barchunks, fileout=task.outputfile.split('.')[0] + '.png')
            bar()
            _baractive = False
            matplotlib.pyplot.show()
    if _baractive:
        bar()
        

def performancereporter_wait(task):
    gc.collect()
    eggchunk = None
    wavechunk = None
    barchunks = None
    
    # initialize the proccessing wait screen
    waitscr = waitscreen()
    # send task to processor
    waitscr.task = task
    # start the processor
    waitscr.show()
        
    root = Tk()
    root.withdraw()
    root.destroy()
    # pull the processor result    
    [eggchunk, wavechunk, barchunks] = waitscr.result
    if not ((eggchunk == None) and (wavechunk == None) and (barchunks == None)):
        fig = matplotlib.pyplot.figure(figsize=(20, 12))
        eegpipe.reportingwindow(fig, eggs=eggchunk, waveforms=wavechunk, bars=barchunks, fileout=task.outputfile.split('.')[0] + '.png')
        matplotlib.pyplot.show()


class alternatethread():
    
    def __init__(self):
        self._close = False
        self.result = 0
    
    def run(self, queue, task):
        showoutput = False
        eggchunk = None
        wavechunk = None
        barchunks = None
        
        filin = task.outputfile.split('.')[0]
        filin = os.path.split(filin)[1]
        if filin[0:2] == 'OB':
            # oddball task
            [eggchunk, wavechunk, barchunks] = checkoddballperf(task, showoutput)
            
        elif filin[0:2] == 'FT':
            # flanker task
            [eggchunk, wavechunk, barchunks] = checkflankerperf(task, showoutput)
            
        elif filin[0:3] == 'N2B':
            # flanker task
            [eggchunk, wavechunk, barchunks] = checkn2backperf(task, showoutput)
            
        elif filin[0:3] == 'CN2B':
            # flanker task
            [eggchunk, wavechunk, barchunks] = checkcontinousn2backperf(task, showoutput)
        
        queue.put([eggchunk, wavechunk, barchunks])
        queue.put(None)
    
class waitscreen():
    
    def __init__(self):
        self._close = False
        self._queue = Queue()
        self.task = None
        self.result = None
    
    def show(self):
        # creating tkinter window
        self.window = tkinter.Tk()
        self.window.lift()
        self.window.wm_attributes('-topmost',1)
        self.window.title("")
        self.winsize = [400, 300]
    
        # intialize alternative thread
        try:
            # initialize alternative thread
            self.altthread = alternatethread()
            self._altthread = Thread(target=self.altthread.run, args=[self._queue, self.task], daemon=True)
            self._altthread.name = 'altthread'
            self._altthread.start()
        except:
            print("Error initializing.")
    
        #TK approach is to create then place
        header = tkinter.Frame(master=self.window, width=self.winsize[0], height=numpy.multiply(self.winsize[1],0.1), bg="white")
        header2 = tkinter.Frame(master=self.window, width=self.winsize[0], height=numpy.multiply(self.winsize[1],0.1), bg="white")
        body = tkinter.Frame(master=self.window, width=self.winsize[0], height=numpy.multiply(self.winsize[1],0.7), bg="white")
        
        header2text = tkinter.Label(master=header2, text='processing...', fg='gray', font=(None, 25), bg="white",
                                 justify='center', anchor='center', 
                                 width=int(numpy.multiply(self.winsize[0],0.09)))
        
        footer = tkinter.Frame(master=self.window, width=self.winsize[0], height=numpy.multiply(self.winsize[1],0.1), bg="white")
       
        frame = tkinter.Frame(self.window, bg="white", borderwidth=0, highlightthickness=0)
        if platform == "linux" or platform == "linux2" or platform == "darwin":
            # OS X
            self.canvas = tkinter.Canvas(frame, bg="white", width=self.winsize[0], height=numpy.multiply(self.winsize[1],0.7),borderwidth=0, highlightthickness=0)
        elif platform == "win32":
            self.canvas = tkinter.Canvas(frame, bg="white", width=self.winsize[0]*1.1, height=numpy.multiply(self.winsize[1],0.7),borderwidth=0, highlightthickness=0)
        photoimage = []
        try:
            photoimage = ImageTk.PhotoImage(file="eggheadframe1.png")
        except:
            try:
                photoimage = ImageTk.PhotoImage(file="Engine" + os.path.sep + "eggheadframe1.png")
            except:
                photoimage = ImageTk.PhotoImage(file="Gentask" + os.path.sep + "Engine" + os.path.sep + "eggheadframe1.png")
        try:
            if platform == "linux" or platform == "linux2" or platform == "darwin":
                # OS X
                self.canvas.create_image(self.winsize[0]/2 + self.winsize[0]/5, numpy.multiply(self.winsize[1],0.7)/2, image=photoimage, anchor="center")
            elif platform == "win32":    
                self.canvas.create_image(self.winsize[0]/2 + self.winsize[0]/3, numpy.multiply(self.winsize[1],0.7)/2, image=photoimage, anchor="center")
        except:
            pass
        self.window.columnconfigure(0, weight=0, minsize=self.winsize[0])
        header.grid(row=0, column=0, sticky="nsew")
        header2text.grid(row=1, column=0, sticky="nsew")
        header2.grid(row=1, column=0, sticky="nsew")
        
        frame.grid(row=2, column=0, sticky="nsew")
        self.canvas.grid(row=2, column=0, sticky="nsew")
        body.grid(row=2, column=0, sticky="nsew")
        
        footer.grid(row=3, column=0, sticky="nsew")
        
        self.window.rowconfigure(0, weight=0, minsize=numpy.multiply(self.winsize[1],0.1))
        self.window.rowconfigure(1, weight=0, minsize=numpy.multiply(self.winsize[1],0.2))
        self.window.rowconfigure(2, weight=0, minsize=numpy.multiply(self.winsize[1],0.7))
        self.window.rowconfigure(3, weight=0, minsize=numpy.multiply(self.winsize[1],0.1))
        
        [x, y] = centerprompt(self.window)
        
        self.window.geometry("+%d+%d" % (x, y))
        self._job = self.window.after(10, self._amidead)
        self.animate_scan()
        self.window.mainloop()
        
    def close(self):
        self._close = True
        self.window.after_cancel(self._job)
        self._altthread.join()
        self.result = self._queue.get()
        
    def _amidead(self):
        try:
            self._job = self.window.after(10, self._amidead)
            if not self._altthread.isAlive():
                self.close()
            if self._close:
                try:
                    self.window.after_cancel(self._job)
                    self.window.destroy()
                    self._altthread.join()
                except:
                    pass
        except:
            pass
  
    def animate_scan(self):
        self.x0 = self.winsize[0]/2
        self.y0 = numpy.multiply(self.winsize[1],0.7)/2
        if platform == "linux" or platform == "linux2" or platform == "darwin":
            self.scan = self.canvas.create_rectangle(self.x0-10, self.y0, self.x0+165, self.y0+8, outline="#0DB14B", fill="#0DB14B")
        elif platform == "win32":
            self.scan = self.canvas.create_rectangle(self.x0+30, self.y0, self.x0+300, self.y0+8, outline="#0DB14B", fill="#0DB14B")
        yinc = 2
        #xinc = 5
        
        while not self._close:
            self.canvas.move(self.scan,0,yinc)
            self.window.update()
            time.sleep(0.01)
            
            if not self._close:
                scan_pos = self.canvas.coords(self.scan)
                xl,yl,xr,yr = scan_pos
                #if xl < abs(xinc) or xr > animation_window_width-abs(xinc):
                #  xinc = -xinc
                if yl < abs(yinc)+(abs(yinc)*15) or yr > numpy.multiply(self.winsize[1],0.7)-(abs(yinc)*15):
                  yinc = -yinc




def centerprompt(toplevel):
    toplevel.update_idletasks()

    # Tkinter way to find the screen resolution
    screen_width = toplevel.winfo_screenwidth()
    screen_height = toplevel.winfo_screenheight()

    size = tuple(int(_) for _ in toplevel.geometry().split('+')[0].split('x'))
    x = screen_width/2 - size[0]/2
    y = screen_height/2 - size[1]/2
    
    toplevel.geometry("+%d+%d" % (x, y))
    
    return [x, y]



def checkoddballperf(task, show=True):   
    
    barchunks = None
    
    # Check Performance Settings using xcat
    datapull = [[0, 0], [0, 0], [0, 0]]
    taskoutput = xcat.BehavioralAnalysis()
    taskoutput.run(inputfile = task.outputfile, trialtypes = [10, 20, 30])
    if show:
        taskoutput.show(label = 'All', header = True)
    taskoutput.run(inputfile = task.outputfile, trialtypes = [20])
    if show:
        taskoutput.show(label = 'Target')
    datapull[0][0] = taskoutput.meanrt
    datapull[1][0] = taskoutput.sdrt
    datapull[2][0] = taskoutput.responseaccuracy
    taskoutput.run(inputfile = task.outputfile, trialtypes = [10, 30])
    if show:
        taskoutput.show(label = 'Nontarget')
    datapull[0][1] = taskoutput.meanrt
    datapull[1][1] = taskoutput.sdrt
    datapull[2][1] = taskoutput.responseaccuracy
    
    # send data to reporting window
    Speed = eegpipe.barplotprep()
    Speed.title = 'Speed'
    Speed.labels = ['Target', 'Nontarget']
    Speed.values = datapull[0]
    Speed.scale = [150, 600]
    Speed.biggerisbetter = False
    Speed.unit = ' ms'
    
    Consistency = eegpipe.barplotprep()
    Consistency.title = 'Consistency'
    Consistency.labels = ['Target', 'Nontarget']
    Consistency.values = datapull[1]
    Consistency.scale = [10, 80]
    Consistency.biggerisbetter = False
    Consistency.unit = ' ms'
    
    # d prime
    HR = numpy.divide(datapull[2][0],100)
    if HR > 0.99: 
        HR = 0.99
    if HR < 0.01: 
        HR = 0.01
    FA = numpy.subtract(1, numpy.divide(datapull[2][1],100))
    if FA > 0.99: 
        FA = 0.99
    if FA < 0.01: 
        FA = 0.01
    dprime = numpy.subtract(scipy.stats.norm.ppf(HR), scipy.stats.norm.ppf(FA))
    Prime = eegpipe.barplotprep()
    Prime.title = 'Accuracy'
    Prime.labels = ['Dprime']
    Prime.values = [dprime]
    Prime.scale = [-1, 4.65]
    Prime.biggerisbetter = True
    Prime.unit = ''
    
    barchunks = [Speed, Consistency, Prime]
    
    ### Rapid Process EEG data ######################################################################################
    if show:
        print('\nPlease wait while the EEG data is rapid processed.')
    eggchunk = None
    wavechunk = None
    
    # if the task finished then pull the data
    if task.finished and exists(task.outputfile.split('.')[0] + '.csv'):
        
        EEG = eegpipe.readUnicornBlack(task.outputfile.split('.')[0] + '.csv')
        EEG = eegpipe.simplefilter(EEG, Filter = 'Notch', Cutoff = [60.0])
        EEG = eegpipe.simplefilter(EEG, Filter = 'Bandpass', Design = 'Butter', Cutoff = [0.5, 30.0], Order=3)
        
        # creates a stimulus locked model ERP.
        [outsum, outvect, xtime] = eegpipe.createsignal(
             Window = [-0.1, 1.0],
             Latency =   [ 0.08,  0.25, 0.35],
             Amplitude = [-0.1,  -0.45, 0.50],
             Width =     [40,       80,  180],
             Shape =     [0,         0,    0],
             Smoothing = [0,         0,    0],
             OverallSmooth = 20, 
             Srate = 250.0)
        
        # Distractor stimulus - 30
        EEGdist = None
        try:
            EEGdist = eegpipe.simpleepoch(EEG, Window = [-0.100, 1.000], Types = [30, 10030])
            EEGdist = eegpipe.simplebaselinecorrect(EEGdist, Window = [-0.100, 0.0])
            EEGdist = eegpipe.pthreepipe(EEGdist)
            if EEGdist.acceptedtrials > 5:
                EEGdist = eegpipe.simpleaverage(EEGdist, Approach = 'Mean')
                EEGdist = eegpipe.collapsechannels(EEGdist, Channels = ['CZ', 'CPZ', 'PZ', 'P3', 'P4', 'CP3', 'CP4', 'C3', 'C4'], NewChannelName='HOTSPOT', Approach='median')
                EEGdist = eegpipe.simplefilter(EEGdist, Design = 'savitzky-golay', Order = 4)
            else:
                EEGdist = None
        except:
            EEGdist = None
            
        if EEGdist != None:
            outputchannels = EEGdist.channels
            
            # place in bar
            [outputamplitude, outputlatency] = eegpipe.extractpeaks(EEGdist, Window=[0.300, 0.700], Points=9, Surround=8)
            Orientation = eegpipe.barplotprep()
            Orientation.title = 'Orientation'
            Orientation.labels = ['Distractor']
            Orientation.values = [outputamplitude[outputchannels.index('HOTSPOT')]]
            Orientation.scale = [0, 20]
            Orientation.biggerisbetter = True
            Orientation.unit = ' microV'
            barchunks.append(Orientation)
            
            # snag waveform
            distractorwave = eegpipe.waveformplotprep()
            distractorwave.title = 'Orientation'
            distractorwave.x = EEGdist.times[eegpipe.closestidx(EEGdist.times, -0.100):eegpipe.closestidx(EEGdist.times, 1.000)]
            distractorwave.y = EEGdist.data[outputchannels.index('HOTSPOT')][eegpipe.closestidx(EEGdist.times, -0.100):eegpipe.closestidx(EEGdist.times, 1.000)]
            distractorwave.linestyle='solid'
            distractorwave.linecolor= '#EF9A35'
            distractorwave.lineweight=2
            distractorwave.fillbetween='ZeroP'
            distractorwave.fillwindow=[numpy.subtract(outputlatency[outputchannels.index('HOTSPOT')],0.1),numpy.add(outputlatency[outputchannels.index('HOTSPOT')],0.1)]
            distractorwave.fillbetweencolor='#EF9A35'
            if wavechunk == None:
                wavechunk = [distractorwave]
            else: 
                wavechunk.append(distractorwave)
            
            # snag egghead
            #outputamplitude = eegpipe.extractamplitude(EEGdist, Window=[0.300, 0.600], Approach='mean')
            distractoregg = eegpipe.eggheadplotprep()
            distractoregg.title = 'Orientation'
            distractoregg.channels = outputchannels
            distractoregg.amplitudes = outputamplitude 
            distractoregg.scale = [0, 1]
            if outputamplitude[outputchannels.index('HOTSPOT')] > distractoregg.scale[1]:
                distractoregg.scale[1] = outputamplitude[outputchannels.index('HOTSPOT')]
            distractoregg.opacity = 0.2 
            if eggchunk == None:
                eggchunk = [distractoregg]
            else: 
                eggchunk.append(distractoregg)  
            
            
        # Target stimulus - 20
        EEGtarg = None
        try:
            EEGtarg = eegpipe.simpleepoch(EEG, Window = [-0.100, 1.000], Types = [20, 10020])
            EEGtarg = eegpipe.simplebaselinecorrect(EEGtarg, Window = [-0.100, 0.0])
            EEGtarg = eegpipe.pthreepipe(EEGtarg)
            if EEGtarg.acceptedtrials > 5:
                EEGtarg = eegpipe.simpleaverage(EEGtarg, Approach = 'Mean')
                EEGtarg = eegpipe.collapsechannels(EEGtarg, Channels = ['CZ', 'CPZ', 'PZ', 'P3', 'P4', 'CP3', 'CP4', 'POZ'], NewChannelName='HOTSPOT', Approach='median')
                EEGtarg = eegpipe.simplefilter(EEGtarg, Design = 'savitzky-golay', Order = 4)
            else:
                EEGtarg = None
        except:
            EEGtarg = None
        
        if EEGtarg != None:
            outputchannels = EEGtarg.channels
            
            # place in bar
            [outputamplitude, outputlatency] = eegpipe.extractpeaks(EEGtarg, Window=[0.300, 0.700], Points=9, Surround=8)
            Attention = eegpipe.barplotprep()
            Attention.title = 'Attention'
            Attention.labels = ['Target']
            Attention.values = [outputamplitude[outputchannels.index('HOTSPOT')]]
            Attention.scale = [0, 16]
            Attention.biggerisbetter = True
            Attention.unit = ' microV'
            barchunks.append(Attention)
            
            Processing = eegpipe.barplotprep()
            Processing.title = 'Processing'
            Processing.labels = ['Target']
            Processing.values = [numpy.multiply(outputlatency[outputchannels.index('HOTSPOT')],1000)]
            Processing.scale = [300, 700]
            Processing.biggerisbetter = False
            Processing.unit = ' ms'
            barchunks.append(Processing)
            
            # snag waveform
            targetwave = eegpipe.waveformplotprep()
            targetwave.title = 'Attention'
            targetwave.x = EEGtarg.times[eegpipe.closestidx(EEGtarg.times, -0.100):eegpipe.closestidx(EEGtarg.times, 1.000)]
            targetwave.y = EEGtarg.data[outputchannels.index('HOTSPOT')][eegpipe.closestidx(EEGtarg.times, -0.100):eegpipe.closestidx(EEGtarg.times, 1.000)]
            targetwave.linestyle='solid'
            targetwave.linecolor= '#3D5E73'
            targetwave.lineweight=2
            targetwave.fillbetween='ZeroP'
            targetwave.fillwindow=[numpy.subtract(outputlatency[outputchannels.index('HOTSPOT')],0.1),numpy.add(outputlatency[outputchannels.index('HOTSPOT')],0.1)]
            targetwave.fillbetweencolor='#3D5E73'
            if wavechunk == None:
                wavechunk = [targetwave]
            else: 
                wavechunk.append(targetwave)
            
            Reference = eegpipe.waveformplotprep()
            Reference.title = 'Reference'
            Reference.x = xtime
            Reference.y = numpy.multiply(outsum,8)
            Reference.linestyle='dashed'
            Reference.linecolor= '#999999'
            Reference.lineweight=0.5
            if wavechunk == None:
                wavechunk = [Reference]
            else: 
                wavechunk.append(Reference)
            
            # snag egghead
            #outputamplitude = eegpipe.extractamplitude(EEGdist, Window=[0.300, 0.600], Approach='mean')
            targetegg = eegpipe.eggheadplotprep()
            targetegg.title = 'Attention'
            targetegg.channels = outputchannels
            targetegg.amplitudes = outputamplitude  
            targetegg.scale = [0, 1]
            if outputamplitude[outputchannels.index('HOTSPOT')] > targetegg.scale[1]:
                targetegg.scale[1] = outputamplitude[outputchannels.index('HOTSPOT')]
            targetegg.opacity = 0.2 
            if eggchunk == None:
                eggchunk = [targetegg]
            else: 
                eggchunk.append(targetegg) 
                
        if eggchunk != None:
            eggscale = [0, 1]
            for cA in range(len(eggchunk)):
                eggscale = eegpipe.determinerescale(eggscale, eggchunk[cA].scale)
            eggscale = eegpipe.centershift(eggscale)
            for cA in range(len(eggchunk)):
                eggchunk[cA].scale = eggscale
        
    return [eggchunk, wavechunk, barchunks] 

def checkflankerperf(task, show=True):    
    barchunks = None
    
    ###### Post task options ######################################################################################
    
    
    ### Pull behavioral performance
    #task.outputfile = 'Raw\OBReportTest.psydat'
    
    # Check Performance Settings using xcat
    datapull = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    taskoutput = xcat.BehavioralAnalysis()
    taskoutput.run(inputfile = task.outputfile, trialtypes = [10, 12, 30, 31, 32, 33, 34, 35, 36, 37, 20, 22, 40, 41, 42, 43, 44, 45, 46, 47])
    if show:
        taskoutput.show(label = 'All', header = True)
    datapull[0][0] = taskoutput.meanrt
    datapull[1][0] = taskoutput.sdrt
    datapull[2][0] = taskoutput.responseaccuracy
    taskoutput.run(inputfile = task.outputfile, trialtypes = [10, 12, 30, 31, 32, 33, 34, 35, 36, 37])
    if show:
        taskoutput.show(label = 'Congruent')
    datapull[0][1] = taskoutput.meanrt
    datapull[1][1] = taskoutput.sdrt
    datapull[2][1] = taskoutput.responseaccuracy
    taskoutput.run(inputfile = task.outputfile, trialtypes = [20, 22, 40, 41, 42, 43, 44, 45, 46, 47])
    if show:
        taskoutput.show(label = 'Incongruent')
    datapull[0][2] = taskoutput.meanrt
    datapull[1][2] = taskoutput.sdrt
    datapull[2][2] = taskoutput.responseaccuracy
    
    # send data to reporting window
    Speed = eegpipe.barplotprep()
    Speed.title = 'Speed'
    Speed.labels = ['All']
    Speed.values = [datapull[0][0]]
    Speed.scale = [150, 600]
    Speed.biggerisbetter = False
    Speed.unit = ' ms'
    
    Consistency = eegpipe.barplotprep()
    Consistency.title = 'Consistency'
    Consistency.labels = ['All']
    Consistency.values = [datapull[1][0]]
    Consistency.scale = [10, 80]
    Consistency.biggerisbetter = False
    Consistency.unit = ' ms'
    
    Accuracy = eegpipe.barplotprep()
    Accuracy.title = 'Inhibition'
    Accuracy.labels = ['All']
    Accuracy.values =  [datapull[2][2]]
    Accuracy.scale = [75, 100]
    Accuracy.biggerisbetter = True
    Accuracy.unit = ' %'
    
    barchunks = [Speed, Consistency, Accuracy]
    
    
    
    ### Rapid Process EEG data ######################################################################################
    if show:
        print('\nPlease wait while the EEG data is rapid processed.')
    eggchunk = None
    wavechunk = None
    
    # if the task finished then pull the data
    if task.finished and exists(task.outputfile.split('.')[0] + '.csv'):
        EEG = eegpipe.readUnicornBlack(task.outputfile.split('.')[0] + '.csv')
        EEG = eegpipe.simplefilter(EEG, Filter = 'Notch', Cutoff = [60.0])
        EEG = eegpipe.simplefilter(EEG, Filter = 'Bandpass', Design = 'Butter', Cutoff = [0.5, 30.0], Order=3)
        
        # creates a stimulus locked model ERP.
        [outsum, outvect, xtime] = eegpipe.createsignal(
             Window = [-0.1, 1.0],
             Latency =   [ 0.08,  0.25, 0.35],
             Amplitude = [-0.1,  -0.45, 0.50],
             Width =     [40,       80,  180],
             Shape =     [0,         0,    0],
             Smoothing = [0,         0,    0],
             OverallSmooth = 20, 
             Srate = 250.0)
        
        # Stimulus locked - 30
        stimcodes = [10, 12, 30, 31, 32, 33, 34, 35, 36, 37] # congruent
        stimcodes.extend([20, 22, 40, 41, 42, 43, 44, 45, 46, 47]) # incongruent
        stimcodes = numpy.ndarray.tolist(numpy.add(stimcodes, 10000)) # only accept correct trials
        EEGstim = None
        try:
            EEGstim = eegpipe.simpleepoch(EEG, Window = [-0.500, 1.000], Types = stimcodes)
            EEGstim = eegpipe.simplebaselinecorrect(EEGstim, Window = [-0.100, 0.0])
            EEGstim = eegpipe.pthreepipe(EEGstim)
            if EEGstim.acceptedtrials > 5:
                EEGstim = eegpipe.simpleaverage(EEGstim, Approach = 'Mean')
                EEGstim = eegpipe.collapsechannels(EEGstim, Channels = ['CZ', 'CPZ', 'PZ', 'P3', 'P4', 'CP3', 'CP4', 'POZ'], NewChannelName='HOTSPOT', Approach='median')
                EEGstim = eegpipe.simplefilter(EEGstim, Design = 'savitzky-golay', Order = 4)
            else:
                EEGstim = None
        except:
            EEGstim = None
            
        if EEGstim != None:
            outputchannels = EEGstim.channels
            
            # place in bar
            [outputamplitude, outputlatency] = eegpipe.extractpeaks(EEGstim, Window=[0.300, 0.700], Points=9, Surround=8)
            Attention = eegpipe.barplotprep()
            Attention.title = 'Attention'
            Attention.labels = ['Target']
            Attention.values = [outputamplitude[outputchannels.index('HOTSPOT')]]
            Attention.scale = [0, 16]
            Attention.biggerisbetter = True
            Attention.unit = ' microV'
            barchunks.append(Attention)
            
            Processing = eegpipe.barplotprep()
            Processing.title = 'Processing'
            Processing.labels = ['Target']
            Processing.values = [numpy.multiply(outputlatency[outputchannels.index('HOTSPOT')],1000)]
            Processing.scale = [300, 700]
            Processing.biggerisbetter = False
            Processing.unit = ' ms'
            barchunks.append(Processing)
            
            
            # snag waveform
            targetwave = eegpipe.waveformplotprep()
            targetwave.title = 'Attention'
            targetwave.x = EEGstim.times[eegpipe.closestidx(EEGstim.times, -0.100):eegpipe.closestidx(EEGstim.times, 1.000)]
            targetwave.y = EEGstim.data[outputchannels.index('HOTSPOT')][eegpipe.closestidx(EEGstim.times, -0.100):eegpipe.closestidx(EEGstim.times, 1.000)]
            targetwave.linestyle='solid'
            targetwave.linecolor= '#3D5E73'
            targetwave.lineweight=2
            targetwave.fillbetween='ZeroP'
            targetwave.fillwindow=[numpy.subtract(outputlatency[outputchannels.index('HOTSPOT')],0.1),numpy.add(outputlatency[outputchannels.index('HOTSPOT')],0.1)]
            targetwave.fillbetweencolor='#3D5E73'
            if wavechunk == None:
                wavechunk = [targetwave]
            else: 
                wavechunk.append(targetwave)
            
            Reference = eegpipe.waveformplotprep()
            Reference.title = 'Attention Reference'
            Reference.x = xtime
            Reference.y = numpy.multiply(outsum,8)
            Reference.linestyle='dashed'
            Reference.linecolor= '#999999'
            Reference.lineweight=0.5
            if wavechunk == None:
                wavechunk = [Reference]
            else: 
                wavechunk.append(Reference)
                
                
            # snag egghead
            #outputamplitude = eegpipe.extractamplitude(EEGdist, Window=[0.300, 0.600], Approach='mean')
            targetegg = eegpipe.eggheadplotprep()
            targetegg.title = 'Attention'
            targetegg.channels = outputchannels
            targetegg.amplitudes = outputamplitude  
            targetegg.scale = [0, 1]
            if outputamplitude[outputchannels.index('HOTSPOT')] > targetegg.scale[1]:
                targetegg.scale[1] = outputamplitude[outputchannels.index('HOTSPOT')]
            targetegg.opacity = 0.2 
            if eggchunk == None:
                eggchunk = [targetegg]
            else: 
                eggchunk.append(targetegg) 
                
                
                
            
        # Feedback locked - 51 errors of commission
        EEGresp = None
        [outsum, outvect, xtime] = eegpipe.createsignal(
             Window =    [-0.500,  1.0],
             Latency =   [-0.10, 0.15],
             Amplitude = [-0.5, 0.25],
             Width =     [100,   180],
             Shape =     [0,    0],
             Smoothing = [0,    0],
             OverallSmooth = 20, 
             Srate = 250.0)
        
        try:
            EEGresp = eegpipe.simpleepoch(EEG, Window = [-0.500, 1.000], Types = [51, 10051])
            EEGresp = eegpipe.simplebaselinecorrect(EEGresp, Window = [-0.500, -0.200])
            EEGresp = eegpipe.ernpipe(EEGresp)
            if EEGresp.acceptedtrials > 4:
                EEGresp = eegpipe.simpleaverage(EEGresp, Approach = 'Mean')
                EEGresp = eegpipe.collapsechannels(EEGresp, Channels = ['FZ', 'FC1', 'FC2', 'CZ'], NewChannelName='HOTSPOT', Approach='median')
                EEGresp = eegpipe.simplefilter(EEGresp, Design = 'savitzky-golay', Order = 4)
            else:
                EEGresp = None
        except:
            EEGresp = None
        
        if EEGresp != None:
            outputchannels = EEGresp.channels
            
            # place in bar
            [outputamplitude, outputlatency] = eegpipe.extractpeaks(EEGresp, Window=[-0.250, 0.200], Direction='min', Points=9, Surround=8)
            Monitoring = eegpipe.barplotprep()
            Monitoring.title = 'Monitoring'
            Monitoring.labels = ['Error']
            Monitoring.values = [outputamplitude[outputchannels.index('HOTSPOT')]]
            Monitoring.scale = [-10, 0]
            Monitoring.biggerisbetter = False
            Monitoring.unit = ' microV'
            barchunks.append(Monitoring)
            
            # snag waveform
            errorwave = eegpipe.waveformplotprep()
            errorwave.title = 'Monitoring'
            errorwave.x = EEGresp.times[eegpipe.closestidx(EEGresp.times, -0.300):eegpipe.closestidx(EEGresp.times, 0.200)]
            errorwave.y = EEGresp.data[outputchannels.index('HOTSPOT')][eegpipe.closestidx(EEGresp.times, -0.300):eegpipe.closestidx(EEGresp.times, 0.200)]
            errorwave.linestyle='solid'
            errorwave.linecolor= '#EF9A35'
            errorwave.lineweight=2
            errorwave.fillbetween='ZeroN'
            errorwave.fillwindow=[numpy.subtract(outputlatency[outputchannels.index('HOTSPOT')],0.1),numpy.add(outputlatency[outputchannels.index('HOTSPOT')],0.1)]
            errorwave.fillbetweencolor='#EF9A35'
            if wavechunk == None:
                wavechunk = [errorwave]
            else: 
                wavechunk.append(errorwave)
                
            ErrReference = eegpipe.waveformplotprep()
            ErrReference.title = 'Monitoring Reference'
            ErrReference.x = xtime[eegpipe.closestidx(xtime, -0.300):eegpipe.closestidx(xtime, 0.200)]
            ErrReference.y = numpy.multiply(outsum,8)[eegpipe.closestidx(xtime, -0.300):eegpipe.closestidx(xtime, 0.200)]
            ErrReference.linestyle='dashed'
            ErrReference.linecolor= '#999999'
            ErrReference.lineweight=0.5
            if wavechunk == None:
                wavechunk = [ErrReference]
            else: 
                wavechunk.append(ErrReference)
            
        
            segs = ['#F593FA', '#9F71E3', '#7729F0', '#350C8F','#23248F', '#1C2C75', '#00004B'] 
            newcmap = LinearSegmentedColormap.from_list("", segs, 256) 
            
            # snag egghead
            #outputamplitude = eegpipe.extractamplitude(EEGdist, Window=[0.300, 0.600], Approach='mean')
            erroregg = eegpipe.eggheadplotprep()
            erroregg.title = 'Monitoring'
            erroregg.channels = outputchannels
            erroregg.amplitudes = outputamplitude 
            erroregg.colormap = newcmap
            erroregg.scale = [0, 1]
            if outputamplitude[outputchannels.index('HOTSPOT')] < erroregg.scale[0]:
                erroregg.scale[0] = outputamplitude[outputchannels.index('HOTSPOT')]
            erroregg.opacity = 0.2 
            if eggchunk == None:
                eggchunk = [erroregg]
            else: 
                eggchunk.append(erroregg) 
            

    return [eggchunk, wavechunk, barchunks] 


def checkn2backperf(task, show=True):   
    
    barchunks = None
    
    
    # Check Performance Settings using xcat
    datapull = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    taskoutput = xcat.BehavioralAnalysis()
    taskoutput.run(inputfile = task.outputfile, trialtypes = list(range(10,50)))
    if show:
        taskoutput.show(label = 'All', header = True)
    datapull[0][0] = taskoutput.meanrt
    datapull[1][0] = taskoutput.sdrt
    datapull[2][0] = taskoutput.responseaccuracy
    taskoutput.run(inputfile = task.outputfile, trialtypes = list(range(30,50)))
    if show:
        taskoutput.show(label = 'Target')
    datapull[0][1] = taskoutput.meanrt
    datapull[1][1] = taskoutput.sdrt
    datapull[2][1] = taskoutput.responseaccuracy
    taskoutput.run(inputfile = task.outputfile, trialtypes = list(range(10,30)))
    if show:
        taskoutput.show(label = 'Nontarget')
    datapull[0][2] = taskoutput.meanrt
    datapull[1][2] = taskoutput.sdrt
    datapull[2][2] = taskoutput.responseaccuracy
    
    # send data to reporting window
    Speed = eegpipe.barplotprep()
    Speed.title = 'Speed'
    Speed.labels = ['All']
    Speed.values = [datapull[0][0]]
    Speed.scale = [250, 1200]
    Speed.biggerisbetter = False
    Speed.unit = ' ms'
    
    Consistency = eegpipe.barplotprep()
    Consistency.title = 'Consistency'
    Consistency.labels = ['All']
    Consistency.values = [datapull[1][0]]
    Consistency.scale = [10, 80]
    Consistency.biggerisbetter = False
    Consistency.unit = ' ms'
    
    Accuracy = eegpipe.barplotprep()
    Accuracy.title = 'Accuracy'
    Accuracy.labels = ['All']
    Accuracy.values = [datapull[2][0]]
    Accuracy.scale = [60, 100]
    Accuracy.biggerisbetter = True
    Accuracy.unit = ' %'
    
    # d prime
    HR = numpy.divide(datapull[2][1],100)
    if HR > 0.99: 
        HR = 0.99
    if HR < 0.01: 
        HR = 0.01
    FA = numpy.subtract(1, numpy.divide(datapull[2][2],100))
    if FA > 0.99: 
        FA = 0.99
    if FA < 0.01: 
        FA = 0.01
    dprime = numpy.subtract(scipy.stats.norm.ppf(HR), scipy.stats.norm.ppf(FA))
    Prime = eegpipe.barplotprep()
    Prime.title = 'Dprime'
    Prime.labels = ['Dprime']
    Prime.values = [dprime]
    Prime.scale = [-1, 4.65]
    Prime.biggerisbetter = True
    Prime.unit = ''
    
    barchunks = [Speed, Consistency, Accuracy, Prime]
    
    ### Rapid Process EEG data ######################################################################################   
    if show:
        print('\nPlease wait while the EEG data is rapid processed.')
    eggchunk = None
    wavechunk = None
    # if the task finished then pull the data
    if task.finished and exists(task.outputfile.split('.')[0] + '.csv'):
        EEG = eegpipe.readUnicornBlack(task.outputfile.split('.')[0] + '.csv')
        EEG = eegpipe.simplefilter(EEG, Filter = 'Notch', Cutoff = [60.0])
        EEG = eegpipe.simplefilter(EEG, Filter = 'Bandpass', Design = 'Butter', Cutoff = [0.5, 30.0], Order=3)
        
        # creates a stimulus locked model ERP.
        [outsum, outvect, xtime] = eegpipe.createsignal(
             Window = [-0.1, 1.0],
             Latency =   [ 0.08,  0.25, 0.35],
             Amplitude = [-0.1,  -0.45, 0.50],
             Width =     [40,       80,  180],
             Shape =     [0,         0,    0],
             Smoothing = [0,         0,    0],
             OverallSmooth = 20, 
             Srate = 250.0)
        
        # Target stimulus - 30 & 40
        EEGtarg = None
        targtrials = list(range(30,50))
        for cE in range(10030,10050):
            targtrials.append(int(cE))
            
        try:
            EEGtarg = eegpipe.simpleepoch(EEG, Window = [-0.100, 1.000], Types = targtrials)
            EEGtarg = eegpipe.simplebaselinecorrect(EEGtarg, Window = [-0.100, 0.0])
            EEGtarg = eegpipe.pthreepipe(EEGtarg)
            if EEGtarg.acceptedtrials > 5:
                EEGtarg = eegpipe.simpleaverage(EEGtarg, Approach = 'Mean')
                EEGtarg = eegpipe.collapsechannels(EEGtarg, Channels = ['CZ', 'CPZ', 'PZ', 'P3', 'P4', 'CP3', 'CP4', 'POZ'], NewChannelName='HOTSPOT', Approach='median')
                EEGtarg = eegpipe.simplefilter(EEGtarg, Design = 'savitzky-golay', Order = 4)
            else:
                EEGtarg = None
        except:
            EEGtarg = None
        
        if EEGtarg != None:
            outputchannels = EEGtarg.channels    
            
            # place in bar
            [outputamplitude, outputlatency] = eegpipe.extractpeaks(EEGtarg, Window=[0.300, 0.700], Points=9, Surround=8)
            Attention = eegpipe.barplotprep()
            Attention.title = 'Attention'
            Attention.labels = ['Target']
            Attention.values = [outputamplitude[outputchannels.index('HOTSPOT')]]
            Attention.scale = [0, 16]
            Attention.biggerisbetter = True
            Attention.unit = ' microV'
            barchunks.append(Attention)
            
            Processing = eegpipe.barplotprep()
            Processing.title = 'Processing'
            Processing.labels = ['Target']
            Processing.values = [numpy.multiply(outputlatency[outputchannels.index('HOTSPOT')],1000)]
            Processing.scale = [300, 700]
            Processing.biggerisbetter = False
            Processing.unit = ' ms'
            barchunks.append(Processing)
            
            # snag waveform
            targetwave = eegpipe.waveformplotprep()
            targetwave.title = 'Attention'
            targetwave.x = EEGtarg.times[eegpipe.closestidx(EEGtarg.times, -0.100):eegpipe.closestidx(EEGtarg.times, 1.000)]
            targetwave.y = EEGtarg.data[outputchannels.index('HOTSPOT')][eegpipe.closestidx(EEGtarg.times, -0.100):eegpipe.closestidx(EEGtarg.times, 1.000)]
            targetwave.linestyle='solid'
            targetwave.linecolor= '#3D5E73'
            targetwave.lineweight=2
            targetwave.fillbetween='ZeroP'
            targetwave.fillwindow=[numpy.subtract(outputlatency[outputchannels.index('HOTSPOT')],0.1),numpy.add(outputlatency[outputchannels.index('HOTSPOT')],0.1)]
            targetwave.fillbetweencolor='#3D5E73'
            if wavechunk == None:
                wavechunk = [targetwave]
            else: 
                wavechunk.append(targetwave)
            
            Reference = eegpipe.waveformplotprep()
            Reference.title = 'Attention Reference'
            Reference.x = xtime
            Reference.y = numpy.multiply(outsum,8)
            Reference.linestyle='dashed'
            Reference.linecolor= '#999999'
            Reference.lineweight=0.5
            if wavechunk == None:
                wavechunk = [Reference]
            else: 
                wavechunk.append(Reference)
            
            # snag egghead
            #outputamplitude = eegpipe.extractamplitude(EEGdist, Window=[0.300, 0.600], Approach='mean')
            targetegg = eegpipe.eggheadplotprep()
            targetegg.title = 'Attention'
            targetegg.channels = outputchannels
            targetegg.amplitudes = outputamplitude  
            targetegg.scale = [0, 1]
            if outputamplitude[outputchannels.index('HOTSPOT')] > targetegg.scale[1]:
                targetegg.scale[1] = outputamplitude[outputchannels.index('HOTSPOT')]
            targetegg.opacity = 0.2 
            if eggchunk == None:
                eggchunk = [targetegg]
            else: 
                eggchunk.append(targetegg) 
             
        
        # Feedback locked - 51 errors of commission
        EEGresp = None
        [outsum, outvect, xtime] = eegpipe.createsignal(
             Window =    [-0.500,  1.0],
             Latency =   [-0.00, 0.25],
             Amplitude = [-0.5, 0.25],
             Width =     [100,   180],
             Shape =     [0,    0],
             Smoothing = [0,    0],
             OverallSmooth = 20, 
             Srate = 250.0)
        
        try:
            EEGresp = eegpipe.simpleepoch(EEG, Window = [-0.500, 1.000], Types = [51, 10051])
            EEGresp = eegpipe.simplebaselinecorrect(EEGresp, Window = [-0.500, -0.200])
            EEGresp = eegpipe.ernpipe(EEGresp)
            if EEGresp.acceptedtrials > 4:
                EEGresp = eegpipe.simpleaverage(EEGresp, Approach = 'Mean')
                EEGresp = eegpipe.collapsechannels(EEGresp, Channels = ['FZ', 'FC1', 'FC2', 'CZ'], NewChannelName='HOTSPOT', Approach='median')
                EEGresp = eegpipe.simplefilter(EEGresp, Design = 'savitzky-golay', Order = 4)
            else:
                EEGresp = None
        except:
            EEGresp = None
        
        if EEGresp != None:
            outputchannels = EEGresp.channels
            
            # place in bar
            [outputamplitude, outputlatency] = eegpipe.extractpeaks(EEGresp, Window=[-0.150, 0.300], Direction='min', Points=9, Surround=8)
            Monitoring = eegpipe.barplotprep()
            Monitoring.title = 'Monitoring'
            Monitoring.labels = ['Error']
            Monitoring.values = [outputamplitude[outputchannels.index('HOTSPOT')]]
            Monitoring.scale = [-10, 0]
            Monitoring.biggerisbetter = False
            Monitoring.unit = ' microV'
            barchunks.append(Monitoring)
            
            # snag waveform
            errorwave = eegpipe.waveformplotprep()
            errorwave.title = 'Monitoring'
            errorwave.x = EEGresp.times[eegpipe.closestidx(EEGresp.times, -0.300):eegpipe.closestidx(EEGresp.times, 0.300)]
            errorwave.y = EEGresp.data[outputchannels.index('HOTSPOT')][eegpipe.closestidx(EEGresp.times, -0.300):eegpipe.closestidx(EEGresp.times, 0.300)]
            errorwave.linestyle='solid'
            errorwave.linecolor= '#EF9A35'
            errorwave.lineweight=2
            errorwave.fillbetween='ZeroN'
            errorwave.fillwindow=[numpy.subtract(outputlatency[outputchannels.index('HOTSPOT')],0.1),numpy.add(outputlatency[outputchannels.index('HOTSPOT')],0.1)]
            errorwave.fillbetweencolor='#EF9A35'
            if wavechunk == None:
                wavechunk = [errorwave]
            else: 
                wavechunk.append(errorwave)
                
            ErrReference = eegpipe.waveformplotprep()
            ErrReference.title = 'Monitoring Reference'
            ErrReference.x = xtime[eegpipe.closestidx(xtime, -0.300):eegpipe.closestidx(xtime, 0.300)]
            ErrReference.y = numpy.multiply(outsum,8)[eegpipe.closestidx(xtime, -0.300):eegpipe.closestidx(xtime, 0.300)]
            ErrReference.linestyle='dashed'
            ErrReference.linecolor= '#999999'
            ErrReference.lineweight=0.5
            if wavechunk == None:
                wavechunk = [ErrReference]
            else: 
                wavechunk.append(ErrReference)
            
            segs = ['#F593FA', '#9F71E3', '#7729F0', '#350C8F','#23248F', '#1C2C75', '#00004B'] 
            newcmap = LinearSegmentedColormap.from_list("", segs, 256)
            # snag egghead
            #outputamplitude = eegpipe.extractamplitude(EEGdist, Window=[0.300, 0.600], Approach='mean')
            erroregg = eegpipe.eggheadplotprep()
            erroregg.title = 'Monitoring'
            erroregg.channels = outputchannels
            erroregg.amplitudes = outputamplitude 
            erroregg.colormap = newcmap
            erroregg.scale = [0, 1]
            if outputamplitude[outputchannels.index('HOTSPOT')] < erroregg.scale[0]:
                erroregg.scale[0] = outputamplitude[outputchannels.index('HOTSPOT')]
            erroregg.opacity = 0.2 
            if eggchunk == None:
                eggchunk = [erroregg]
            else: 
                eggchunk.append(erroregg) 
    
    return [eggchunk, wavechunk, barchunks] 


def checkcontinousn2backperf(task, show=True):   
    
    barchunks = None
    
    ###### Post task options ######################################################################################
    
    
    ### Pull behavioral performance
    #task.outputfile = 'Raw\OBReportTest.psydat'
    
    # Check Performance Settings using xcat
    datapull = [[0], [0], [0]]
    taskoutput = xcat.BehavioralAnalysis()
    taskoutput.run(inputfile = task.outputfile, trialtypes = list(range(10,50)))
    if show:
        taskoutput.show(label = 'All', header = True)
    datapull[0][0] = taskoutput.meanrt
    datapull[1][0] = taskoutput.sdrt
    datapull[2][0] = taskoutput.responseaccuracy
    
    # send data to reporting window
    Speed = eegpipe.barplotprep()
    Speed.title = 'Speed'
    Speed.labels = ['Speed']
    Speed.values = datapull[0]
    Speed.scale = [150, 600]
    Speed.biggerisbetter = False
    Speed.unit = ' ms'
    
    Consistency = eegpipe.barplotprep()
    Consistency.title = 'Consistency'
    Consistency.labels = ['Consistency']
    Consistency.values = datapull[1]
    Consistency.scale = [10, 80]
    Consistency.biggerisbetter = False
    Consistency.unit = ' ms'
    
    Accuracy = eegpipe.barplotprep()
    Accuracy.title = 'Accuracy'
    Accuracy.labels = ['Accuracy']
    Accuracy.values = datapull[2]
    Accuracy.scale = [60, 100]
    Accuracy.biggerisbetter = True
    Accuracy.unit = ' %'
    
    barchunks = [Speed, Consistency, Accuracy]
    
    ### Rapid Process EEG data ######################################################################################  
    if show:
        print('\nPlease wait while the EEG data is rapid processed.')
    eggchunk = None
    wavechunk = None
    
    # if the task finished then pull the data
    if task.finished and exists(task.outputfile.split('.')[0] + '.csv'):
        EEG = eegpipe.readUnicornBlack(task.outputfile.split('.')[0] + '.csv')
        EEG = eegpipe.simplefilter(EEG, Filter = 'Notch', Cutoff = [60.0])
        EEG = eegpipe.simplefilter(EEG, Filter = 'Bandpass', Design = 'Butter', Cutoff = [0.5, 30.0], Order=3)

        # Feedback locked - 51 errors of commission
        EEGresp = None
        [outsum, outvect, xtime] = eegpipe.createsignal(
             Window =    [-0.500,  1.0],
             Latency =   [-0.00, 0.25],
             Amplitude = [-0.5, 0.25],
             Width =     [100,   180],
             Shape =     [0,    0],
             Smoothing = [0,    0],
             OverallSmooth = 20, 
             Srate = 250.0)
        
        try:
            EEGresp = eegpipe.simpleepoch(EEG, Window = [-0.500, 1.000], Types = [51, 10051])
            EEGresp = eegpipe.simplebaselinecorrect(EEGresp, Window = [-0.500, -0.200])
            EEGresp = eegpipe.ernpipe(EEGresp)
            if EEGresp.acceptedtrials > 4:
                EEGresp = eegpipe.simpleaverage(EEGresp, Approach = 'Mean')
                EEGresp = eegpipe.collapsechannels(EEGresp, Channels = ['FZ', 'FC1', 'FC2', 'CZ'], NewChannelName='HOTSPOT', Approach='median')
                EEGresp = eegpipe.simplefilter(EEGresp, Design = 'savitzky-golay', Order = 4)
            else:
                EEGresp = None
        except:
            EEGresp = None
        
        if EEGresp != None:
            outputchannels = EEGresp.channels
            
            # place in bar
            [outputamplitude, outputlatency] = eegpipe.extractpeaks(EEGresp, Window=[-0.150, 0.300], Direction='min', Points=9, Surround=8)
            Monitoring = eegpipe.barplotprep()
            Monitoring.title = 'Monitoring'
            Monitoring.labels = ['Error']
            Monitoring.values = [outputamplitude[outputchannels.index('HOTSPOT')]]
            Monitoring.scale = [-10, 0]
            Monitoring.biggerisbetter = False
            Monitoring.unit = ' microV'
            barchunks.append(Monitoring)
            
            # snag waveform
            errorwave = eegpipe.waveformplotprep()
            errorwave.title = 'Monitoring'
            errorwave.x = EEGresp.times[eegpipe.closestidx(EEGresp.times, -0.300):eegpipe.closestidx(EEGresp.times, 0.300)]
            errorwave.y = EEGresp.data[outputchannels.index('HOTSPOT')][eegpipe.closestidx(EEGresp.times, -0.300):eegpipe.closestidx(EEGresp.times, 0.300)]
            errorwave.linestyle='solid'
            errorwave.linecolor= '#EF9A35'
            errorwave.lineweight=2
            errorwave.fillbetween='ZeroN'
            errorwave.fillwindow=[numpy.subtract(outputlatency[outputchannels.index('HOTSPOT')],0.1),numpy.add(outputlatency[outputchannels.index('HOTSPOT')],0.1)]
            errorwave.fillbetweencolor='#EF9A35'
            if wavechunk == None:
                wavechunk = [errorwave]
            else: 
                wavechunk.append(errorwave)
                
            ErrReference = eegpipe.waveformplotprep()
            ErrReference.title = 'Reference'
            ErrReference.x = xtime[eegpipe.closestidx(xtime, -0.300):eegpipe.closestidx(xtime, 0.300)]
            ErrReference.y = numpy.multiply(outsum,8)[eegpipe.closestidx(xtime, -0.300):eegpipe.closestidx(xtime, 0.300)]
            ErrReference.linestyle='dashed'
            ErrReference.linecolor= '#999999'
            ErrReference.lineweight=0.5
            if wavechunk == None:
                wavechunk = [ErrReference]
            else: 
                wavechunk.append(ErrReference)
            
            segs = ['#F593FA', '#9F71E3', '#7729F0', '#350C8F','#23248F', '#1C2C75', '#00004B'] 
            newcmap = LinearSegmentedColormap.from_list("", segs, 256)
            
            # snag egghead
            #outputamplitude = eegpipe.extractamplitude(EEGdist, Window=[0.300, 0.600], Approach='mean')
            erroregg = eegpipe.eggheadplotprep()
            erroregg.title = 'Monitoring'
            erroregg.channels = outputchannels
            erroregg.amplitudes = outputamplitude 
            erroregg.colormap = newcmap
            erroregg.scale = [0, 1]
            if outputamplitude[outputchannels.index('HOTSPOT')] < erroregg.scale[0]:
                erroregg.scale[0] = outputamplitude[outputchannels.index('HOTSPOT')]
            erroregg.opacity = 0.2 
            if eggchunk == None:
                eggchunk = [erroregg]
            else: 
                eggchunk.append(erroregg) 
    
    
    return [eggchunk, wavechunk, barchunks] 

class Engine():
    def __init__(self):
        self.finished = True
        
if __name__ == "__main__":

    task = Engine()
    root = Tk()
    root.lift()
    root.wm_attributes('-topmost',1)
    root.withdraw()
    filename = askopenfilename(filetypes=[("PythonCollect", "*.psydat"),("OddballTask", "OB*.psydat"), ("FlankerTask", "FT*.psydat"), ("N2backTask", "N2B*.psydat"), ("ContN2backTask", "CN2B*.psydat"), ("All", "*")])  # show an "Open" dialog box and return the path to the selected file
    root.destroy()
    if len(filename) > 0:
        task.outputfile = filename.split('.')[0] + '.psydat'
        performancereporter(task)
    