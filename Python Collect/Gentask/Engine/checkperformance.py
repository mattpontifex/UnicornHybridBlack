import os
from os.path import exists
import re
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
import copy
from datetime import datetime
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
try:
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
except:
    pass


def perfdebug(task):
    eggchunk = None
    wavechunk = None
    barchunks = None
    #[eggchunk, wavechunk, barchunks] = checkecperf(task, True)
    [eggchunk, wavechunk, barchunks] = checkoddballdriverperf(task, True)
    
    fig = matplotlib.pyplot.figure(figsize=(20, 12))
    eegpipe.reportingwindow(fig, eggs=eggchunk, waveforms=wavechunk, bars=barchunks)
    matplotlib.pyplot.show()
    


def performancereporter(task):
    gc.collect()
    showoutput = False
    eggchunk = None
    wavechunk = None
    barchunks = None
    _baractive = False
    waveformpositivedown = True
    
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
            
            if filin[0:3] == 'OBD':
                # oddball task
                [eggchunk, wavechunk, barchunks] = checkoddballdriverperf(task, showoutput)
            else:
                # oddball task
                [eggchunk, wavechunk, barchunks] = checkoddballperf(task, showoutput)
                        
        elif filin[0:2] == 'EC':
            # flanker task
            [eggchunk, wavechunk, barchunks] = checkecperf(task, showoutput)
            waveformpositivedown = False
            
        elif filin[0:2] == 'FT':
            # flanker task
            [eggchunk, wavechunk, barchunks] = checkflankerperf(task, showoutput)
            
        elif filin[0:3] == 'GNG':
            # flanker task
            [eggchunk, wavechunk, barchunks] = checkgonogoperf(task, showoutput)
            
        elif filin[0:3] == 'N2B':
            # 2 back
            [eggchunk, wavechunk, barchunks] = checkn2backperf(task, showoutput)
            
        elif filin[0:4] == 'CN2B':
            # continuous 2back
            [eggchunk, wavechunk, barchunks] = checkcontinousn2backperf(task, showoutput)
            
        elif filin[0:3] == 'SAR':
            # SAR task
            [eggchunk, wavechunk, barchunks] = checknsarperf(task, showoutput)
            
    if _baractive:
        _baractive = True
        bar() 
        _baractive = False
        
    with alive_bar(total=0, title='..Loading results..', unknown=arrows_in, spinner='classic', monitor=False, stats=True) as bar:
        _baractive = True
        if not ((eggchunk == None) and (wavechunk == None) and (barchunks == None)):
            fig = matplotlib.pyplot.figure(figsize=(20, 12))
            eegpipe.reportingwindow(fig, eggs=eggchunk, waveforms=wavechunk, bars=barchunks, waveformpositivedown=waveformpositivedown, fileout=task.outputfile.split('.')[0] + '.png')
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
            
        if filin[0:3] == 'OB3':
            # oddball task
            [eggchunk, wavechunk, barchunks] = check3stimoddballperf(task, showoutput)
            
        elif filin[0:2] == 'FT':
            # flanker task
            [eggchunk, wavechunk, barchunks] = checkflankerperf(task, showoutput)
            
        elif filin[0:3] == 'GNG':
            # flanker task
            [eggchunk, wavechunk, barchunks] = checkgonogoperf(task, showoutput)
            
        elif filin[0:3] == 'N2B':
            # flanker task
            [eggchunk, wavechunk, barchunks] = checkn2backperf(task, showoutput)
            
        elif filin[0:4] == 'CN2B':
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
    logtext = []
    tempval = task.outputfile.split('.')[0]
    tempval = re.split('\/', tempval)
    tempfilname = tempval[len(tempval)-1]

    try:
        tempval = tempfilname.split('_')
    except:
        tempval = [tempfilname,'']

    subtemp = tempval[0]

    if subtemp[0:3] == 'Raw':
        subtemp = subtemp[-(len(subtemp)-4):]

    #subtemp = subtemp[-(len(subtemp)-3):]
    subtemp = subtemp[:-2]

    logtext.append('filename')
    logtext.append(subtemp)
    print(subtemp)

    timestamp = str(datetime.now()).split()

    logtext.append('date')
    logtext.append(str(timestamp[0]))
    
    logtext.append('time')
    logtext.append(str(timestamp[1]))
    
    
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
    
    logval(logtext, 'TargetSpeed', datapull[0][0], scale=False)
    logval(logtext, 'TargetSpeedNorm', datapull[0][0], scale=Speed.scale, biggerisbetter=Speed.biggerisbetter)

    Consistency = eegpipe.barplotprep()
    Consistency.title = 'Consistency'
    Consistency.labels = ['Target', 'Nontarget']
    Consistency.values = datapull[1]
    Consistency.scale = [10, 80]
    Consistency.biggerisbetter = False
    Consistency.unit = ' ms'
    
    logval(logtext, 'TargetConsistency', datapull[1][0], scale=False)
    logval(logtext, 'TargetConsistencyNorm', datapull[1][0], scale=Consistency.scale, biggerisbetter=Consistency.biggerisbetter)

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
    
    logval(logtext, 'AccuracyDprime', dprime, scale=False)
    logval(logtext, 'AccuracyDprimeNorm', dprime, scale=Prime.scale, biggerisbetter=Prime.biggerisbetter)
    
    
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
            
        # Target stimulus - 20
        EEGtarg = None
        try:
            EEGtarg = eegpipe.simpleepoch(EEG, Window = [-0.100, 1.000], Types = [20, 10020])
            EEGtarg = eegpipe.simplebaselinecorrect(EEGtarg, Window = [-0.100, 0.0])
            EEGtarg = eegpipe.pthreepipe(EEGtarg)
            if EEGtarg.acceptedtrials > 5:
                EEGtarg = eegpipe.simpleaverage(EEGtarg, Approach = 'Mean')
                EEGtarg = eegpipe.collapsechannels(EEGtarg, Channels = ['CZ', 'CPZ', 'PZ', 'P3', 'P4', 'CP3', 'CPP1', 'CPP2', 'CP4', 'POZ'], NewChannelName='HOTSPOT', Approach='median')
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
            
            logval(logtext, 'Attention', Attention.values[0], scale=False)
            logval(logtext, 'AttentionNorm', Attention.values[0], scale=Attention.scale, biggerisbetter=Attention.biggerisbetter)
            
            
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
        
        
    #performancelogger(fileout=r'C:\Studies\PythonCollect7\oddballperformancelog.csv', textout=logtext)
        
    return [eggchunk, wavechunk, barchunks] 


def check3stimoddballperf(task, show=True):   
    
    barchunks = None
    logtext = []
    tempval = task.outputfile.split('.')[0]
    tempval = re.split('\/', tempval)
    tempfilname = tempval[len(tempval)-1]

    try:
        tempval = tempfilname.split('_')
    except:
        tempval = [tempfilname,'']

    subtemp = tempval[0]

    if subtemp[0:3] == 'Raw':
        subtemp = subtemp[-(len(subtemp)-4):]

    #subtemp = subtemp[-(len(subtemp)-3):]
    subtemp = subtemp[:-3]

    logtext.append('filename')
    logtext.append(subtemp)

    timestamp = str(datetime.now()).split()

    logtext.append('date')
    logtext.append(str(timestamp[0]))
    
    logtext.append('time')
    logtext.append(str(timestamp[1]))
    
    
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
    
    logval(logtext, 'TargetSpeed', datapull[0][0], scale=False)
    logval(logtext, 'TargetSpeedNorm', datapull[0][0], scale=Speed.scale, biggerisbetter=Speed.biggerisbetter)

    Consistency = eegpipe.barplotprep()
    Consistency.title = 'Consistency'
    Consistency.labels = ['Target', 'Nontarget']
    Consistency.values = datapull[1]
    Consistency.scale = [10, 80]
    Consistency.biggerisbetter = False
    Consistency.unit = ' ms'
    
    logval(logtext, 'TargetConsistency', datapull[1][0], scale=False)
    logval(logtext, 'TargetConsistencyNorm', datapull[1][0], scale=Consistency.scale, biggerisbetter=Consistency.biggerisbetter)

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
    
    logval(logtext, 'AccuracyDprime', dprime, scale=False)
    logval(logtext, 'AccuracyDprimeNorm', dprime, scale=Prime.scale, biggerisbetter=Prime.biggerisbetter)
    
    
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
                EEGdist = eegpipe.collapsechannels(EEGdist, Channels = ['CZ', 'CPZ', 'PZ', 'P3', 'P4', 'CP3', 'CP4','CPP1', 'CPP2', 'C3', 'C4'], NewChannelName='HOTSPOT', Approach='median')
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
            
            logval(logtext, 'Orientation', Orientation.values[0], scale=False)
            logval(logtext, 'OrientationNorm', Orientation.values[0], scale=Orientation.scale, biggerisbetter=Orientation.biggerisbetter)
            
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
                EEGtarg = eegpipe.collapsechannels(EEGtarg, Channels = ['CZ', 'CPZ', 'PZ', 'P3', 'P4', 'CP3', 'CP4','CPP1', 'CPP2', 'POZ'], NewChannelName='HOTSPOT', Approach='median')
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
            
            logval(logtext, 'Attention', Attention.values[0], scale=False)
            logval(logtext, 'AttentionNorm', Attention.values[0], scale=Attention.scale, biggerisbetter=Attention.biggerisbetter)
            
            
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
        
        
    #performancelogger(fileout=r'C:\Studies\PythonCollect7\threestimoddballperformancelog.csv', textout=logtext)
        
    return [eggchunk, wavechunk, barchunks] 

def checkflankerperf(task, show=True):    
    barchunks = None
    logtext = []
    tempval = task.outputfile.split('.')[0]
    tempval = re.split('\/', tempval)
    tempfilname = tempval[len(tempval)-1]

    try:
        tempval = tempfilname.split('_')
    except:
        tempval = [tempfilname,'']

    subtemp = tempval[0]

    if subtemp[0:3] == 'Raw':
        subtemp = subtemp[-(len(subtemp)-4):]

    #subtemp = subtemp[-(len(subtemp)-3):]
    subtemp = subtemp[:-2]

    logtext.append('filename')
    logtext.append(subtemp)

    timestamp = str(datetime.now()).split()

    logtext.append('date')
    logtext.append(str(timestamp[0]))
    
    logtext.append('time')
    logtext.append(str(timestamp[1]))
    
    
    
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
    
    logval(logtext, 'Speed', datapull[0][0], scale=False)
    logval(logtext, 'SpeedNorm', datapull[0][0], scale=Speed.scale, biggerisbetter=Speed.biggerisbetter)
    
    Consistency = eegpipe.barplotprep()
    Consistency.title = 'Consistency'
    Consistency.labels = ['All']
    Consistency.values = [datapull[1][0]]
    Consistency.scale = [10, 80]
    Consistency.biggerisbetter = False
    Consistency.unit = ' ms'
    
    logval(logtext, 'Consistency', datapull[1][0], scale=False)
    logval(logtext, 'ConsistencyNorm', datapull[1][0], scale=Consistency.scale, biggerisbetter=Consistency.biggerisbetter)
    
    Accuracy = eegpipe.barplotprep()
    Accuracy.title = 'Inhibition'
    Accuracy.labels = ['All']
    
    outval = datapull[2][2]
    if (datapull[2][2] > datapull[2][1]): 
        # cong is worse than incong, so remove the half difference in accuracy
        # 100 for inc and 75 for cong - 100-12.5 = 87.5
        # 100 for inc and 0 for cong - 100 - 50 = 50
        # 85 for inc and 80 for cong - 85 - 2.5 = 82.5
        outval = numpy.subtract(outval, numpy.divide(numpy.subtract(datapull[2][2],datapull[2][1]),2))
    Accuracy.values =  [outval]
    Accuracy.scale = [75, 100]
    Accuracy.biggerisbetter = True
    Accuracy.unit = ' %'
    
    logval(logtext, 'Inhibition', outval, scale=False)
    logval(logtext, 'InhibitionNorm', outval, scale=Accuracy.scale, biggerisbetter=Accuracy.biggerisbetter)
    
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
                EEGstim = eegpipe.collapsechannels(EEGstim, Channels = ['CZ', 'CPZ', 'PZ', 'P3', 'P4', 'CP3', 'CP4','CPP1', 'CPP2', 'POZ'], NewChannelName='HOTSPOT', Approach='median')
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
            
            logval(logtext, 'Attention', Attention.values[0], scale=False)
            logval(logtext, 'AttentionNorm', Attention.values[0], scale=Attention.scale, biggerisbetter=Attention.biggerisbetter)
            
            Processing = eegpipe.barplotprep()
            Processing.title = 'Processing'
            Processing.labels = ['Target']
            Processing.values = [numpy.multiply(outputlatency[outputchannels.index('HOTSPOT')],1000)]
            Processing.scale = [300, 700]
            Processing.biggerisbetter = False
            Processing.unit = ' ms'
            barchunks.append(Processing)
            
            logval(logtext, 'Processing', Processing.values[0], scale=False)
            logval(logtext, 'ProcessingNorm', Processing.values[0], scale=Processing.scale, biggerisbetter=Processing.biggerisbetter)
            
            
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
            if EEGresp.acceptedtrials > 2:
                EEGresp = eegpipe.simpleaverage(EEGresp, Approach = 'Mean')
                EEGresp = eegpipe.collapsechannels(EEGresp, Channels = ['FZ', 'FC1', 'FC2', 'FFC1', 'FFC2','CZ'], NewChannelName='HOTSPOT', Approach='median')
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
            
            logval(logtext, 'Monitoring', Monitoring.values[0], scale=False)
            logval(logtext, 'MonitoringNorm', Monitoring.values[0], scale=Monitoring.scale, biggerisbetter=Monitoring.biggerisbetter)
            
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
            

    #performancelogger(fileout=r'C:\Studies\PythonCollect7\flankerperformancelog.csv', textout=logtext)
    return [eggchunk, wavechunk, barchunks] 


def checkgonogoperf(task, show=True):
    barchunks = None
    
    ###### Post task options ######################################################################################
    
    
    ### Pull behavioral performance
    #task.outputfile = 'Raw\OBReportTest.psydat'
    
    # Check Performance Settings using xcat
    datapull = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    taskoutput = xcat.BehavioralAnalysis()
    taskoutput.run(inputfile = task.outputfile, trialtypes = [11, 21, 12, 22])
    if show:
        taskoutput.show(label = 'Go', header = True)
    datapull[0][0] = taskoutput.meanrt
    datapull[1][0] = taskoutput.sdrt
    datapull[2][0] = taskoutput.responseaccuracy
    taskoutput.run(inputfile = task.outputfile, trialtypes = [31, 41])
    if show:
        taskoutput.show(label = 'Nogo Go')
    datapull[0][1] = taskoutput.meanrt
    datapull[1][1] = taskoutput.sdrt
    datapull[2][1] = taskoutput.responseaccuracy
    taskoutput.run(inputfile = task.outputfile, trialtypes = [32, 42])
    if show:
        taskoutput.show(label = 'Nogo Nogo')
    datapull[0][2] = taskoutput.meanrt
    datapull[1][2] = taskoutput.sdrt
    datapull[2][2] = taskoutput.responseaccuracy
    taskoutput.run(inputfile = task.outputfile, trialtypes = [31, 41, 32, 42])
    if show:
        taskoutput.show(label = 'Nogo')
    datapull[0][3] = taskoutput.meanrt
    datapull[1][3] = taskoutput.sdrt
    datapull[2][3] = taskoutput.responseaccuracy
    
    # send data to reporting window
    Speed = eegpipe.barplotprep()
    Speed.title = 'Speed'
    Speed.labels = ['Go']
    Speed.values = [datapull[0][0]]
    Speed.scale = [300, 900]
    Speed.biggerisbetter = False
    Speed.unit = ' ms'
    
    Consistency = eegpipe.barplotprep()
    Consistency.title = 'Consistency'
    Consistency.labels = ['Go']
    Consistency.values = [datapull[1][0]]
    Consistency.scale = [30, 200]
    Consistency.biggerisbetter = False
    Consistency.unit = ' ms'
    
    Accuracy = eegpipe.barplotprep()
    Accuracy.title = 'Inhibition'
    Accuracy.labels = ['Go', 'Nogo']
    Accuracy.values =  [datapull[2][0], datapull[2][3]]
    Accuracy.scale = [65, 100]
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
        stimcodes = [32, 42] # NoGo Right
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
            Attention.labels = ['Nogo']
            Attention.values = [outputamplitude[outputchannels.index('HOTSPOT')]]
            Attention.scale = [0, 16]
            Attention.biggerisbetter = True
            Attention.unit = ' microV'
            barchunks.append(Attention)
            
            Processing = eegpipe.barplotprep()
            Processing.title = 'Processing'
            Processing.labels = ['Nogo']
            Processing.values = [numpy.multiply(outputlatency[outputchannels.index('HOTSPOT')],1000)]
            Processing.scale = [300, 700]
            Processing.biggerisbetter = False
            Processing.unit = ' ms'
            barchunks.append(Processing)
            
            
            # snag waveform
            targetwave = eegpipe.waveformplotprep()
            targetwave.title = 'Nogo'
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
            targetegg.title = 'Nogo'
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
            if EEGresp.acceptedtrials > 2:
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
            [outputamplitude, outputlatency] = eegpipe.extractpeaks(EEGresp, Window=[-0.200, 0.100], Direction='min', Points=9, Surround=8)
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
    logtext = []
    tempval = task.outputfile.split('.')[0]
    tempval = re.split('\/', tempval)
    tempfilname = tempval[len(tempval)-1]

    try:
        tempval = tempfilname.split('_')
    except:
        tempval = [tempfilname,'']

    subtemp = tempval[0]

    if subtemp[0:3] == 'Raw':
        subtemp = subtemp[-(len(subtemp)-4):]

    #subtemp = subtemp[-(len(subtemp)-3):]
    subtemp = subtemp[:-3]

    logtext.append('filename')
    logtext.append(subtemp)

    timestamp = str(datetime.now()).split()

    logtext.append('date')
    logtext.append(str(timestamp[0]))
    
    logtext.append('time')
    logtext.append(str(timestamp[1]))
    
    
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
    
    logval(logtext, 'Speed', Speed.values[0], scale=False)
    logval(logtext, 'SpeedNorm', Speed.values[0], scale=Speed.scale, biggerisbetter=Speed.biggerisbetter)
        
    
    Consistency = eegpipe.barplotprep()
    Consistency.title = 'Consistency'
    Consistency.labels = ['All']
    Consistency.values = [datapull[1][0]]
    Consistency.scale = [10, 80]
    Consistency.biggerisbetter = False
    Consistency.unit = ' ms'
    
    logval(logtext, 'Consistency', Consistency.values[0], scale=False)
    logval(logtext, 'ConsistencyNorm', Consistency.values[0], scale=Consistency.scale, biggerisbetter=Consistency.biggerisbetter)
    
    Accuracy = eegpipe.barplotprep()
    Accuracy.title = 'Accuracy'
    Accuracy.labels = ['All']
    Accuracy.values = [datapull[2][0]]
    Accuracy.scale = [60, 100]
    Accuracy.biggerisbetter = True
    Accuracy.unit = ' %'
    
    logval(logtext, 'Accuracy', Accuracy.values[0], scale=False)
    logval(logtext, 'AccuracyNorm', Accuracy.values[0], scale=Accuracy.scale, biggerisbetter=Accuracy.biggerisbetter)
    
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
    
    logval(logtext, 'Dprime', Prime.values[0], scale=False)
    logval(logtext, 'DprimeNorm', Prime.values[0], scale=Prime.scale, biggerisbetter=Prime.biggerisbetter)
    
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
                EEGtarg = eegpipe.collapsechannels(EEGtarg, Channels = ['CZ', 'CPZ', 'PZ', 'P3', 'P4', 'CP3', 'CP4', 'CPP1', 'CPP2', 'POZ'], NewChannelName='HOTSPOT', Approach='median')
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
            
            logval(logtext, 'Attention', Attention.values[0], scale=False)
            logval(logtext, 'AttentionNorm', Attention.values[0], scale=Attention.scale, biggerisbetter=Attention.biggerisbetter)
            
            Processing = eegpipe.barplotprep()
            Processing.title = 'Processing'
            Processing.labels = ['Target']
            Processing.values = [numpy.multiply(outputlatency[outputchannels.index('HOTSPOT')],1000)]
            Processing.scale = [300, 700]
            Processing.biggerisbetter = False
            Processing.unit = ' ms'
            barchunks.append(Processing)
            
            logval(logtext, 'Processing', Processing.values[0], scale=False)
            logval(logtext, 'ProcessingNorm', Processing.values[0], scale=Processing.scale, biggerisbetter=Processing.biggerisbetter)
            
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
            if EEGresp.acceptedtrials > 2:
                EEGresp = eegpipe.simpleaverage(EEGresp, Approach = 'Mean')
                EEGresp = eegpipe.collapsechannels(EEGresp, Channels = ['FZ', 'FC1', 'FC2', 'FFC1', 'FFC2', 'CZ'], NewChannelName='HOTSPOT', Approach='median')
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
            
            logval(logtext, 'Monitoring', Monitoring.values[0], scale=False)
            logval(logtext, 'MonitoringNorm', Monitoring.values[0], scale=Monitoring.scale, biggerisbetter=Monitoring.biggerisbetter)
            
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
    
    #performancelogger(fileout=r'C:\Studies\PythonCollect7\twobackperformancelog.csv', textout=logtext)
    return [eggchunk, wavechunk, barchunks] 


def checkcontinousn2backperf(task, show=True):   
    
    barchunks = None
    logtext = []
    tempval = task.outputfile.split('.')[0]
    tempval = re.split('\/', tempval)
    tempfilname = tempval[len(tempval)-1]

    try:
        tempval = tempfilname.split('_')
    except:
        tempval = [tempfilname,'']

    subtemp = tempval[0]

    if subtemp[0:3] == 'Raw':
        subtemp = subtemp[-(len(subtemp)-4):]

    #subtemp = subtemp[-(len(subtemp)-3):]
    subtemp = subtemp[:-4]

    logtext.append('filename')
    logtext.append(subtemp)

    timestamp = str(datetime.now()).split()

    logtext.append('date')
    logtext.append(str(timestamp[0]))
    
    logtext.append('time')
    logtext.append(str(timestamp[1]))
    
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
    
    logval(logtext, 'Speed', Speed.values[0], scale=False)
    logval(logtext, 'SpeedNorm', Speed.values[0], scale=Speed.scale, biggerisbetter=Speed.biggerisbetter)
    
    Consistency = eegpipe.barplotprep()
    Consistency.title = 'Consistency'
    Consistency.labels = ['Consistency']
    Consistency.values = datapull[1]
    Consistency.scale = [10, 80]
    Consistency.biggerisbetter = False
    Consistency.unit = ' ms'
    
    logval(logtext, 'Consistency', Consistency.values[0], scale=False)
    logval(logtext, 'ConsistencyNorm', Consistency.values[0], scale=Consistency.scale, biggerisbetter=Consistency.biggerisbetter)
    
    Accuracy = eegpipe.barplotprep()
    Accuracy.title = 'Accuracy'
    Accuracy.labels = ['Accuracy']
    Accuracy.values = datapull[2]
    Accuracy.scale = [60, 100]
    Accuracy.biggerisbetter = True
    Accuracy.unit = ' %'
    
    logval(logtext, 'Accuracy', Accuracy.values[0], scale=False)
    logval(logtext, 'AccuracyNorm', Accuracy.values[0], scale=Accuracy.scale, biggerisbetter=Accuracy.biggerisbetter)
    
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
            if EEGresp.acceptedtrials > 2:
                EEGresp = eegpipe.simpleaverage(EEGresp, Approach = 'Mean')
                EEGresp = eegpipe.collapsechannels(EEGresp, Channels = ['FZ', 'FC1', 'FC2', 'FFC1', 'FFC2', 'CZ'], NewChannelName='HOTSPOT', Approach='median')
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
            
            logval(logtext, 'Monitoring', Monitoring.values[0], scale=False)
            logval(logtext, 'MonitoringNorm', Monitoring.values[0], scale=Monitoring.scale, biggerisbetter=Monitoring.biggerisbetter)
            
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
    
    
    #performancelogger(fileout=r'C:\Studies\PythonCollect7\continuoustwobackperformancelog.csv', textout=logtext)
    return [eggchunk, wavechunk, barchunks] 

def checknsarperf(task, show=True):   
    
    barchunks = None
    logtext = []
    tempval = task.outputfile.split('.')[0]
    tempval = re.split('\/', tempval)
    tempfilname = tempval[len(tempval)-1]

    try:
        tempval = tempfilname.split('_')
    except:
        tempval = [tempfilname,'']

    subtemp = tempval[0]

    if subtemp[0:3] == 'Raw':
        subtemp = subtemp[-(len(subtemp)-4):]

    #subtemp = subtemp[-(len(subtemp)-3):]
    subtemp = subtemp[:-3]

    logtext.append('filename')
    logtext.append(subtemp)

    timestamp = str(datetime.now()).split()

    logtext.append('date')
    logtext.append(str(timestamp[0]))
    
    logtext.append('time')
    logtext.append(str(timestamp[1]))
    
    # Check Performance Settings using xcat
    datapull = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    taskoutput = xcat.BehavioralAnalysis()
    taskoutput.run(inputfile = task.outputfile, trialtypes = [11, 12, 14, 15, 16, 17, 18, 19])
    if show:
        taskoutput.show(label = 'Go', header = True)
    datapull[0][0] = taskoutput.meanrt
    datapull[1][0] = taskoutput.sdrt
    datapull[2][0] = taskoutput.responseaccuracy
    taskoutput.run(inputfile = task.outputfile, trialtypes = [42])
    if show:
        taskoutput.show(label = 'Nogo Go')
    datapull[0][1] = taskoutput.meanrt
    datapull[1][1] = taskoutput.sdrt
    datapull[2][1] = taskoutput.responseaccuracy
    taskoutput.run(inputfile = task.outputfile, trialtypes = [32])
    if show:
        taskoutput.show(label = 'Nogo Nogo')
    datapull[0][2] = taskoutput.meanrt
    datapull[1][2] = taskoutput.sdrt
    datapull[2][2] = taskoutput.responseaccuracy
    taskoutput.run(inputfile = task.outputfile, trialtypes = [13])
    if show:
        taskoutput.show(label = 'Nogo')
    datapull[0][3] = taskoutput.meanrt
    datapull[1][3] = taskoutput.sdrt
    datapull[2][3] = taskoutput.responseaccuracy
    
    # send data to reporting window
    Speed = eegpipe.barplotprep()
    Speed.title = 'Speed'
    Speed.labels = ['Go']
    Speed.values = [datapull[0][0]]
    Speed.scale = [300, 900]
    Speed.biggerisbetter = False
    Speed.unit = ' ms'

    logval(logtext, 'Speed', datapull[0][0], scale=False)	
    logval(logtext, 'SpeedNorm', datapull[0][0], scale=Speed.scale, biggerisbetter=Speed.biggerisbetter)


    Consistency = eegpipe.barplotprep()
    Consistency.title = 'Consistency'
    Consistency.labels = ['Go']
    Consistency.values = [datapull[1][0]]
    Consistency.scale = [30, 200]
    Consistency.biggerisbetter = False
    Consistency.unit = ' ms'

    logval(logtext, 'Consistency', datapull[1][0], scale=False)	
    logval(logtext, 'ConsistencyNorm', datapull[1][0], scale=Consistency.scale, biggerisbetter=Consistency.biggerisbetter)
    
    Accuracy = eegpipe.barplotprep()
    Accuracy.title = 'Inhibition'
    Accuracy.labels = ['Go', 'Nogo']
    Accuracy.values =  [datapull[2][0], datapull[2][3]]
    Accuracy.scale = [65, 100]
    Accuracy.biggerisbetter = True
    Accuracy.unit = ' %'
    
    logval(logtext, 'Inhibition', datapull[2][3], scale=False)	
    logval(logtext, 'Inhibition Norm', datapull[2][3], scale=Accuracy.scale, biggerisbetter= Accuracy.biggerisbetter)

    # d prime
    HR = numpy.divide(datapull[2][0],100)
    if HR > 0.99: 
        HR = 0.99
    if HR < 0.01: 
        HR = 0.01
    FA = numpy.subtract(1, numpy.divide(datapull[2][3],100))
    if FA > 0.99: 
        FA = 0.99
    if FA < 0.01: 
        FA = 0.01
        
    if HR > FA:
        netchange = numpy.subtract(HR, FA)
        aprime = numpy.add(0.5, numpy.divide(numpy.multiply(netchange, numpy.add(1,netchange)), numpy.multiply(numpy.multiply(4,HR), numpy.subtract(1,FA))))
    else:
        netchange = numpy.subtract(FA, HR)
        aprime = numpy.subtract(0.5, numpy.divide(numpy.multiply(netchange, numpy.add(1,netchange)), numpy.multiply(numpy.multiply(4,FA), numpy.subtract(1,HR))))
        
    Prime = eegpipe.barplotprep()
    Prime.title = 'Aprime'
    Prime.labels = ['Aprime']
    Prime.values = [aprime]
    Prime.scale = [0.6, 1]
    Prime.biggerisbetter = True
    Prime.unit = ''
    
    logval(logtext, 'Aprime', Prime.values[0], scale=False)
    logval(logtext, 'AprimeNorm', Prime.values[0], scale=Prime.scale, biggerisbetter=Prime.biggerisbetter)
    
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
            if EEGresp.acceptedtrials > 2:
                EEGresp = eegpipe.simpleaverage(EEGresp, Approach = 'Mean')
                EEGresp = eegpipe.collapsechannels(EEGresp, Channels = ['FZ', 'FC1', 'FC2','FFC1', 'FFC2', 'CZ'], NewChannelName='HOTSPOT', Approach='median')
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
            
            logval(logtext, 'Monitoring', Monitoring.values[0], scale=False)
            logval(logtext, 'MonitoringNorm', Monitoring.values[0], scale=Monitoring.scale, biggerisbetter=Monitoring.biggerisbetter)
            
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
    
    #performancelogger(fileout=r'C:\Studies\PythonCollect7\sartperformancelog.csv', textout=logtext)
    return [eggchunk, wavechunk, barchunks] 



def performancelogger(fileout='performancelog.csv', textout=[]):
    if len(textout) > 0:
        try:
            # see if we need to create the file or if it already exists
            if not (os.path.isfile(fileout)): 
                f = open(fileout, 'w')
            else:
                f = open(fileout, 'a')
    
            for n in range(0,len(textout)):
                if isinstance(textout[n], str):
                    f.write('%s' % (textout[n]))
                elif isinstance(textout[n], float):
                    f.write('%.5f' % (textout[n]))
                elif isinstance(textout[n], int):
                    f.write('%d' % (textout[n]))
                
                if n < (len(textout)-1):
                    f.write(', ')
                    
            f.write('\n')
            f.close()
        except:
            pass
        
def logval(loglist, label, value, scale=False, biggerisbetter=True):
    
    newvallist = []
    newvallist.append(label)
    newvallist.append('')
    
    try:
        newvallist[1] = value
    except:
        pass
        
    if isinstance(newvallist[1], float):
        # must have put something in there 
        if scale:
            try:
                valout = numpy.multiply(numpy.subtract(newvallist[1], scale[0]) / numpy.subtract(scale[1], scale[0]),100)
                if not biggerisbetter:
                    valout = numpy.subtract(100, valout)
                newvallist[1] = valout
            except:
                newvallist[1] = ''

    loglist.append(newvallist[0])
    loglist.append(newvallist[1])
    





def checkoddballdriverperf(task, show=True):   
    
    barchunks = None
    eggchunk = None
    wavechunk = None
    if task.finished:
        
        logtext = []
        tempval = task.outputfile.split('.')[0]
        tempval = re.split('\/', tempval)
        tempfilname = tempval[len(tempval)-1]
    
        try:
            tempval = tempfilname.split('_')
        except:
            tempval = [tempfilname,'']
    
        subtemp = tempval[0]
    
        if subtemp[0:3] == 'Raw':
            subtemp = subtemp[-(len(subtemp)-4):]
    
        tempval = subtemp
        # Only using the bar plots 
        
        mfilname = tempval[3:len(tempval)]
        
        pulllabels = []
        speedpull = []
        accuracypull = []
        
        tempfilname = copy.deepcopy(mfilname)
        runcount = 1
        
        
        while (os.path.isfile(givemetherightpath() + 'OBD' + tempfilname + '.psydat')): 
        
            # Check Performance Settings using xcat
            datapull = [[0, 0], [0, 0], [0, 0]]
            taskoutput = xcat.BehavioralAnalysis()
            taskoutput.run(inputfile = givemetherightpath() + 'OBD' + tempfilname + '.psydat', trialtypes = [20])
            datapull[0][0] = taskoutput.meanrt
            datapull[1][0] = taskoutput.sdrt
            datapull[2][0] = taskoutput.responseaccuracy
            taskoutput.run(inputfile = givemetherightpath() + 'OBD' + tempfilname + '.psydat', trialtypes = [10, 30])
            datapull[0][1] = taskoutput.meanrt
            datapull[1][1] = taskoutput.sdrt
            datapull[2][1] = taskoutput.responseaccuracy    
        
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
        
            pulllabels.append('block ' + str(runcount))
            speedpull.append(datapull[0][0])
            accuracypull.append(dprime)
        
            tempfilname = tempfilname + '_1'
            runcount = runcount + 1
        
        # send data to reporting window
        Speed = eegpipe.barplotprep()
        Speed.title = 'Speed'
        Speed.labels = pulllabels
        Speed.values = speedpull
        Speed.scale = [150, 600]
        Speed.biggerisbetter = False
        Speed.unit = ' ms'
        
        Prime = eegpipe.barplotprep()
        Prime.title = 'Dprime'
        Prime.labels = pulllabels
        Prime.values = accuracypull
        Prime.scale = [-1, 4.65]
        Prime.biggerisbetter = True
        Prime.unit = ''
        
        barchunks = [Speed, Prime]
        
        ### Rapid Process EEG data ######################################################################################
        if show:
            print('\nPlease wait while the EEG data is rapid processed.')

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


        pulllabels = []
        attentionpull = []
        processingpull = []

        tempfilname = copy.deepcopy(mfilname)
        runcount = 1
        while (os.path.isfile(givemetherightpath() + 'OBD' + tempfilname + '.csv')): 
    
            EEG = eegpipe.readUnicornBlack(givemetherightpath() + 'OBD' + tempfilname + '.csv')
            EEG = eegpipe.simplefilter(EEG, Filter = 'Notch', Cutoff = [60.0])
            EEG = eegpipe.simplefilter(EEG, Filter = 'Bandpass', Design = 'Butter', Cutoff = [0.5, 30.0], Order=3)
    
            # Target stimulus - 20
            EEGtarg = None
            try:
                EEGtarg = eegpipe.simpleepoch(EEG, Window = [-0.100, 1.000], Types = [20, 10020])
                EEGtarg = eegpipe.simplebaselinecorrect(EEGtarg, Window = [-0.100, 0.0])
                EEGtarg = eegpipe.pthreepipe(EEGtarg)
                if EEGtarg.acceptedtrials > 5:
                    EEGtarg = eegpipe.simpleaverage(EEGtarg, Approach = 'Mean')
                    EEGtarg = eegpipe.collapsechannels(EEGtarg, Channels = ['CZ', 'CPZ', 'PZ', 'P3', 'P4', 'CP3', 'CP4','CPP1', 'CPP2', 'POZ'], NewChannelName='HOTSPOT', Approach='median')
                    EEGtarg = eegpipe.simplefilter(EEGtarg, Design = 'savitzky-golay', Order = 4)
                else:
                    EEGtarg = None
            except:
                EEGtarg = None
            
            if EEGtarg != None:
                outputchannels = EEGtarg.channels
                [outputamplitude, outputlatency] = eegpipe.extractpeaks(EEGtarg, Window=[0.300, 0.700], Points=9, Surround=8)
                
                attentionpull.append(outputamplitude[outputchannels.index('HOTSPOT')])
                processingpull.append(numpy.multiply(outputlatency[outputchannels.index('HOTSPOT')],1000))
                
                # snag waveform
                targetwave = eegpipe.waveformplotprep()
                targetwave.title = 'block ' + str(runcount)
                targetwave.x = EEGtarg.times[eegpipe.closestidx(EEGtarg.times, -0.100):eegpipe.closestidx(EEGtarg.times, 1.000)]
                targetwave.y = EEGtarg.data[outputchannels.index('HOTSPOT')][eegpipe.closestidx(EEGtarg.times, -0.100):eegpipe.closestidx(EEGtarg.times, 1.000)]
                targetwave.linestyle='solid'
                #targetwave.linecolor= '#3D5E73'
                targetwave.lineweight=2
                #targetwave.fillbetween='ZeroP'
                #targetwave.fillwindow=[numpy.subtract(outputlatency[outputchannels.index('HOTSPOT')],0.1),numpy.add(outputlatency[outputchannels.index('HOTSPOT')],0.1)]
                #targetwave.fillbetweencolor='#3D5E73'
                if wavechunk == None:
                    wavechunk = [targetwave]
                else: 
                    wavechunk.append(targetwave)
                
                
            else:
                attentionpull.append(numpy.nan)
                processingpull.append(numpy.nan)
            pulllabels.append('block ' + str(runcount))
    
    
            tempfilname = tempfilname + '_1'
            runcount = runcount + 1
    
        # place in bar
        Attention = eegpipe.barplotprep()
        Attention.title = 'Attention'
        Attention.labels = pulllabels
        Attention.values = attentionpull
        Attention.scale = [0, 16]
        Attention.biggerisbetter = True
        Attention.unit = ' microV'
        barchunks.append(Attention)
        
        
        Processing = eegpipe.barplotprep()
        Processing.title = 'Processing'
        Processing.labels = pulllabels
        Processing.values = processingpull
        Processing.scale = [300, 700]
        Processing.biggerisbetter = False
        Processing.unit = ' ms'
        barchunks.append(Processing)
            
            
    #performancelogger(fileout=r'C:\Studies\PythonCollect7\oddballperformancelog.csv', textout=logtext)
        
    return [eggchunk, wavechunk, barchunks] 



def checkecperf(task, show=True):   
    
    barchunks = []
    eggchunk = None
    wavechunk = None
    if task.finished:
        logtext = []
        tempval = task.outputfile.split('.')[0]
        tempval = re.split('\/', tempval)
        tempfilname = tempval[len(tempval)-1]
    
        try:
            tempval = tempfilname.split('_')
        except:
            tempval = [tempfilname,'']
    
        subtemp = tempval[0]
    
        if subtemp[0:3] == 'Raw':
            subtemp = subtemp[-(len(subtemp)-4):]
    
        tempval = subtemp
        # Only using the bar plots 
        
        mfilname = tempval[2:len(tempval)]
        
        ### Rapid Process EEG data ######################################################################################
        if show:
            print('\nPlease wait while the EEG data is rapid processed.')

        pulllabels = []
        deltapull = []
        thetapull = []
        alphapull = []
        betapull = []
        
        tempfilname = copy.deepcopy(mfilname)
        runcount = 1
        while (os.path.isfile(givemetherightpath() + 'EC' + tempfilname + '.csv')): 
            
            EEG = eegpipe.readUnicornBlack(givemetherightpath() + 'EC' + tempfilname + '.csv')
            EEG = eegpipe.simplefilter(EEG, Filter = 'Notch', Cutoff = [60.0])
            EEG = eegpipe.simplefilter(EEG, Filter = 'Bandpass', Design = 'Butter', Cutoff = [1.0, 30.0], Order=3)
    
            # Target stimulus - 10
            EEGtarg = None
            try:
                EEGtarg = eegpipe.simpleepoch(EEG, Window = [-0.100, 3.000], Types = [10, 10010])
                EEGtarg = eegpipe.simplebaselinecorrect(EEGtarg, Window = [-0.100, 0.0])
                EEGtarg = eegpipe.collapsechannels(EEGtarg, Channels = ['FCZ','F1','F2','FFC1', 'FFC2','CZ', 'CPZ', 'PZ', 'P3', 'P4', 'CP3', 'CP4','CPP1', 'CPP2', 'POZ'], NewChannelName='HOTSPOT', Approach='median')
                EEGtarg = eegpipe.simplepsd(EEGtarg, Scale=500, Ceiling=30.0)
                EEGtarg = eegpipe.simpleaverage(EEGtarg, Approach = 'Mean')
            except:
                EEGtarg = None
    
            if EEGtarg != None:
                outputchannels = EEGtarg.channels
                
                outputamplitude = EEGtarg.freqdata[outputchannels.index('HOTSPOT')]
                outputlatency = EEGtarg.frequencies
                
                deltapull.append(numpy.mean(outputamplitude[eegpipe.closestidx(outputlatency, 0.5):eegpipe.closestidx(outputlatency, 4.0)]))
                thetapull.append(numpy.mean(outputamplitude[eegpipe.closestidx(outputlatency, 4.0):eegpipe.closestidx(outputlatency, 8.0)]))
                alphapull.append(numpy.mean(outputamplitude[eegpipe.closestidx(outputlatency, 8.0):eegpipe.closestidx(outputlatency, 12.0)]))
                betapull.append(numpy.mean(outputamplitude[eegpipe.closestidx(outputlatency, 12.0):eegpipe.closestidx(outputlatency, 32.0)]))
                
                # snag waveform
                targetwave = eegpipe.waveformplotprep()
                targetwave.title = 'block ' + str(runcount)
                targetwave.x = outputlatency
                targetwave.y = outputamplitude
                targetwave.linestyle='solid'
                #targetwave.linecolor= '#3D5E73'
                targetwave.lineweight=2
                if wavechunk == None:
                    wavechunk = [targetwave]
                else: 
                    wavechunk.append(targetwave)
                
            else:
                deltapull.append(numpy.nan)
                thetapull.append(numpy.nan)
                alphapull.append(numpy.nan)
                betapull.append(numpy.nan)
            pulllabels.append('block ' + str(runcount))
    
            tempfilname = tempfilname + '_1'
            runcount = runcount + 1
    
        # place in bar
        showdelta = False
        if showdelta:
            Delta = eegpipe.barplotprep()
            Delta.title = 'Delta\n(0.5 to 4 hz)'
            Delta.labels = pulllabels
            Delta.values = deltapull
            Delta.scale = [0, 4000]
            Delta.biggerisbetter = True
            Delta.unit = ''
            barchunks.append(Delta)
        
        showtheta = False
        if showtheta:
            Theta = eegpipe.barplotprep()
            Theta.title = 'Theta\n(4 to 8 hz)'
            Theta.labels = pulllabels
            Theta.values = thetapull
            Theta.scale = [0, 40]
            Theta.biggerisbetter = True
            Theta.unit = ''
            barchunks.append(Theta)
        
        showalpha = False
        if showalpha:
            Alpha = eegpipe.barplotprep()
            Alpha.title = 'Alpha\n(8 to 12 hz)'
            Alpha.labels = pulllabels
            Alpha.values = alphapull
            Alpha.scale = [0, 40]
            Alpha.biggerisbetter = False
            Alpha.unit = ''
            barchunks.append(Alpha)
        
        showbeta = False
        if showbeta:
            Beta = eegpipe.barplotprep()
            Beta.title = 'Beta\n(12 to 30 hz)'
            Beta.labels = pulllabels
            Beta.values = betapull
            Beta.scale = [0, 40]
            Beta.biggerisbetter = True
            Beta.unit = ''
            barchunks.append(Beta)
        
        AlphaBeta = eegpipe.barplotprep()
        AlphaBeta.title = 'Alpha(8-12)-Beta(12-30)\n(Concentration)'
        AlphaBeta.labels = pulllabels
        AlphaBeta.values = numpy.divide(alphapull,betapull)
        AlphaBeta.scale = [-1, 10]
        AlphaBeta.biggerisbetter = False
        AlphaBeta.unit = ''
        barchunks.append(AlphaBeta)
        
        ThetaBeta = eegpipe.barplotprep()
        ThetaBeta.title = 'Theta(4-8)-Beta(12-30)\n(Attentional Focus)'
        ThetaBeta.labels = pulllabels
        ThetaBeta.values = numpy.divide(thetapull,betapull)
        ThetaBeta.scale = [-1, 15]
        ThetaBeta.biggerisbetter = False
        ThetaBeta.unit = ''
        barchunks.append(ThetaBeta)
        
        ThetaAlpha = eegpipe.barplotprep()
        ThetaAlpha.title = 'Theta(4-8)-Alpha(8-12)\n(External Mindset)'
        ThetaAlpha.labels = pulllabels
        ThetaAlpha.values = numpy.divide(thetapull,alphapull)
        ThetaAlpha.scale = [-1, 10]
        ThetaAlpha.biggerisbetter = False
        ThetaAlpha.unit = ''
        barchunks.append(ThetaAlpha)
            
    #performancelogger(fileout=r'C:\Studies\PythonCollect7\oddballperformancelog.csv', textout=logtext)
        
    return [eggchunk, wavechunk, barchunks] 



def givemetherightpath():
    newpath = os.path.dirname(os.getcwd())
    if os.path.isdir(os.getcwd() + os.path.sep + 'Raw'):
        # in a good spot
        newpath = os.getcwd() + os.path.sep + 'Raw' + os.path.sep
    else:
        if os.path.isdir(os.getcwd() + os.path.sep + 'Engine'):
            # in the Gentask folder
            newpath = os.path.dirname(os.getcwd()) + os.path.sep + 'Raw' + os.path.sep
        elif os.path.isdir(os.path.dirname(os.getcwd()) + os.path.sep + 'Engine'):
            # in the Gentask Engine folder
            newpath = os.path.dirname(os.path.dirname(os.getcwd())) + os.path.sep + 'Raw' + os.path.sep
        
    #if not newpath[-1:] == os.path.sep:
    #    newpath = newpath + os.path.sep   
        
    return newpath

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
        #performancereporter(task)
        perfdebug(task)
    
