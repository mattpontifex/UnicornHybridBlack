import os
import Engine.xcat as xcat
import Engine.filesync as filesync
from Engine.basicstimuluspresentationengine import Engine
import Engine.generatesequence as generatesequence
import Engine.eegpipe as eegpipe
import numpy
import scipy
from tkinter import Tk     # from tkinter import Tk for Python 3.x
from tkinter.filedialog import askopenfilename


def checkoddballperf(task):    
    
    # Check Performance Settings using xcat
    datapull = [[0, 0], [0, 0], [0, 0]]
    taskoutput = xcat.BehavioralAnalysis()
    taskoutput.run(inputfile = task.outputfile, trialtypes = [10, 20, 30])
    taskoutput.show(label = 'All', header = True)
    taskoutput.run(inputfile = task.outputfile, trialtypes = [20])
    taskoutput.show(label = 'Target')
    datapull[0][0] = taskoutput.meanrt
    datapull[1][0] = taskoutput.sdrt
    datapull[2][0] = taskoutput.responseaccuracy
    taskoutput.run(inputfile = task.outputfile, trialtypes = [10, 30])
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
    Consistency.scale = [20, 300]
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
    print('\nPlease wait while the EEG data is rapid processed.')
    eggchunk = None
    wavechunk = None
    
    # if the task finished then pull the data
    if task.finished:
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
            EEGdist = eegpipe.voltagethreshold(EEGdist, Threshold = [-100.0, 100.0], Step = 50.0)
            EEGdist = eegpipe.antiphasedetection(EEGdist, Threshold=0.0, Window = [0.200, 0.800], Channel=['CZ', 'CPZ', 'PZ'], Template=outsum[eegpipe.closestidx(xtime, 0.200):eegpipe.closestidx(xtime, 0.800)])
            EEGdist = eegpipe.antiphasedetection(EEGdist, Threshold=0.0, Window = [0.200, 0.800], Channel=['CZ', 'CPZ', 'PZ'])
            EEGdist = eegpipe.voltagethreshold(EEGdist, Threshold = [-100.0, 100.0], Step = 50.0)
            EEGdist = eegpipe.netdeflectiondetection(EEGdist, Threshold=-10, Direction='negative', Window = [0.200, 0.800],Channel=['CZ', 'CPZ', 'PZ'])
            EEGdist = eegpipe.simplefilter(EEGdist, Design = 'savitzky-golay', Order = 6)
            # EEGdist = eegpipe.simplezwave(EEGdist, BaselineWindow = [-0.100, 0.000])
            EEGdist = eegpipe.simpleaverage(EEGdist, Approach = 'Mean')
            EEGdist = eegpipe.collapsechannels(EEGdist, Channels = ['C3', 'CZ', 'C4', 'CPZ', 'PZ', 'POZ'], NewChannelName='HOTSPOT', Approach='median')
            EEGdist = eegpipe.simplefilter(EEGdist, Design = 'savitzky-golay', Order = 4)
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
            [outputchannels, outputamplitude] = eegpipe.eggpad(outputchannels, outputamplitude)
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
            EEGtarg = eegpipe.voltagethreshold(EEGtarg, Threshold = [-100.0, 100.0], Step = 50.0)
            EEGtarg = eegpipe.antiphasedetection(EEGtarg, Threshold=0.0, Window = [0.200, 0.800], Channel=['CZ', 'CPZ', 'PZ'], Template=outsum[eegpipe.closestidx(xtime, 0.200):eegpipe.closestidx(xtime, 0.800)])
            EEGtarg = eegpipe.antiphasedetection(EEGtarg, Threshold=0.0, Window = [0.200, 0.800], Channel=['CZ', 'CPZ', 'PZ'])
            EEGtarg = eegpipe.voltagethreshold(EEGtarg, Threshold = [-100.0, 100.0], Step = 50.0)
            EEGtarg = eegpipe.netdeflectiondetection(EEGtarg, Threshold=-10, Direction='negative', Window = [0.200, 0.800],Channel=['CZ', 'CPZ', 'PZ'])
            EEGtarg = eegpipe.simplefilter(EEGtarg, Design = 'savitzky-golay', Order = 6)
            #EEGtarg = eegpipe.simplezwave(EEGtarg, BaselineWindow = [-0.100, 0.000])
            EEGtarg = eegpipe.simpleaverage(EEGtarg, Approach = 'Mean')
            EEGtarg = eegpipe.collapsechannels(EEGtarg, Channels = ['C3', 'CZ', 'C4', 'CPZ', 'PZ', 'POZ'], NewChannelName='HOTSPOT', Approach='median')
            EEGtarg = eegpipe.simplefilter(EEGtarg, Design = 'savitzky-golay', Order = 4)
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
            Attention.scale = [0, 20]
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
            [outputchannels, outputamplitude] = eegpipe.eggpad(outputchannels, outputamplitude)
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
        
        eegpipe.reportingwindow(eggs=eggchunk, waveforms=wavechunk, bars=barchunks, fileout = task.outputfile.split('.')[0] + '.png')


if __name__ == "__main__":
    # Unicorn multiprocessing will not run in Spyder 
    # Run -> Configuration per file... 
    # Change the Console to Execute in an external system terminal
    # Select the checkbox for External system terminal Interact with the Python console after execution
    
    task = Engine()
    task.finished = True
    Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename()  # show an "Open" dialog box and return the path to the selected file
    task.outputfile = filename.split('.')[0] + '.psydat'
    #task.outputfile = r'Raw\OBLauren.psydat'
    
    checkoddballperf(task)
    