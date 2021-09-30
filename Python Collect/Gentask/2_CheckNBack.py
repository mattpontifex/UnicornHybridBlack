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
    #task.outputfile = r'Raw\NBmatt.psydat'

    
    
    ###### Post task options ######################################################################################
    
    
    ### Pull behavioral performance
    #task.outputfile = 'Raw\NBmatt.psydat'
    
    # Check Performance Settings using xcat
    datapull = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    taskoutput = xcat.BehavioralAnalysis()
    taskoutput.run(inputfile = task.outputfile, trialtypes = list(range(10,50)))
    taskoutput.show(label = 'All', header = True)
    datapull[0][0] = taskoutput.meanrt
    datapull[1][0] = taskoutput.sdrt
    datapull[2][0] = taskoutput.responseaccuracy
    taskoutput.run(inputfile = task.outputfile, trialtypes = list(range(30,50)))
    taskoutput.show(label = 'Target')
    datapull[0][1] = taskoutput.meanrt
    datapull[1][1] = taskoutput.sdrt
    datapull[2][1] = taskoutput.responseaccuracy
    taskoutput.run(inputfile = task.outputfile, trialtypes = list(range(10,30)))
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
    Consistency.scale = [20, 300]
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
    print('\nPlease wait while the EEG data is rapid processed.')
    eggchunk = None
    wavechunk = None
    # if the task finished then pull the data
    if task.finished:
        EEG = eegpipe.readUnicornBlack(task.outputfile.split('.')[0] + '.csv')
        #try:
        #    EEG = eegpipe.mergetaskperformance(EEG, task.outputfile.split('.')[0] + '.psydat')
        #except:
        #    boolfail = True
        EEG = eegpipe.simplefilter(EEG, Filter = 'Notch', Cutoff = [60.0])
        EEG = eegpipe.simplefilter(EEG, Filter = 'Bandpass', Design = 'Butter', Cutoff = [1.0, 25.0], Order=3)
        eggscale = [1,0]
        
        # Target stimulus - 30 & 40
        EEGtarg = None
        targtrials = list(range(30,50))
        for cE in range(10030,10050):
            targtrials.append(int(cE))
        #try:
        EEGtarg = eegpipe.simpleepoch(EEG, Window = [-0.500, 2.000], Types = targtrials)
        EEGtarg = eegpipe.simplebaselinecorrect(EEGtarg, Window = [-0.100, 0.0])
        EEGtarg = eegpipe.voltagethreshold(EEGtarg, Threshold = [-100.0, 100.0], Step = 50.0)
        EEGtarg = eegpipe.simplefilter(EEGtarg, Design = 'savitzky-golay', Order = 4)
        EEGtarg = eegpipe.simplezwave(EEGtarg, BaselineWindow = [-0.500, 0.0])
        EEGtarg = eegpipe.simpleaverage(EEGtarg, Approach = 'Mean')
        eegpipe.saveset(EEGtarg, task.outputfile.split('.')[0] + '_Target.erp')
        EEGtarg = eegpipe.collapsechannels(EEGtarg, Channels = ['C3', 'CZ', 'C4', 'CPZ', 'PZ', 'POZ'], NewChannelName='HOTSPOT', Approach='median')
        #except:
        #    EEGtarg = None
        
        if EEGtarg != None:
            [outputamplitude, outputlatency] = eegpipe.extractpeaks(EEGtarg, Window=[0.300, 0.700], Points=9)
            outputamplitude = eegpipe.extractamplitude(EEGtarg, Window=[0.300, 0.700], Approach='mean')
            eggscale = eegpipe.determinerescale(eggscale, outputamplitude)
            outputchannels = EEGtarg.channels
            # snag waveform
            targetwave = eegpipe.waveformplotprep()
            targetwave.title = 'Attention'
            targetwave.x = EEGtarg.times
            targetwave.y = EEGtarg.data[outputchannels.index('HOTSPOT')]
            targetwave.linestyle='solid'
            targetwave.linecolor= '#A91CD4'
            targetwave.lineweight=2
            targetwave.fillbetween='ZeroP'
            targetwave.fillwindow=[0.3,0.6]
            if wavechunk == None:
                wavechunk = [targetwave]
            else: 
                wavechunk.append(targetwave)
                
            # place in bar
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
            Processing.values = [outputlatency[outputchannels.index('HOTSPOT')]]
            Processing.scale = [0.300, 0.700]
            Processing.biggerisbetter = False
            Processing.unit = ' ms'
            barchunks.append(Processing)
            
            # snag egghead
            [outputchannels, outputamplitude] = eegpipe.eggpad(outputchannels, outputamplitude)
            targetegg = eegpipe.eggheadplotprep()
            targetegg.title = 'Attention'
            targetegg.channels = outputchannels
            targetegg.amplitudes = outputamplitude  
            targetegg.scale = [1, 9]
            targetegg.steps = 256
            targetegg.opacity = 0.2 
            if eggchunk == None:
                eggchunk = [targetegg]
            else: 
                eggchunk.append(targetegg) 
        
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
            Reference = eegpipe.waveformplotprep()
            Reference.title = 'Reference'
            Reference.x = xtime
            Reference.y = numpy.multiply(outsum,8)
            Reference.linestyle='dashed'
            Reference.linecolor= '#768591'
            Reference.lineweight=0.5
            if wavechunk == None:
                wavechunk = [Reference]
            else: 
                wavechunk.append(Reference)        
        
        # Feedback locked - 51 errors of commission
        EEGresp = None
        try:
            EEGresp = eegpipe.simpleepoch(EEG, Window = [-0.500, 1.000], Types = [51])
            EEGresp = eegpipe.simplebaselinecorrect(EEGresp, Window = [-0.100, 0.0])
            EEGresp = eegpipe.voltagethreshold(EEGresp, Threshold = [-100.0, 100.0], Step = 50.0)
            EEGresp = eegpipe.simplefilter(EEGresp, Design = 'savitzky-golay', Order = 4)
            EEGresp = eegpipe.simplezwave(EEGresp, BaselineWindow = [-0.500, 0.0])
            EEGresp = eegpipe.simpleaverage(EEGresp, Approach = 'Mean')
            eegpipe.saveset(EEGresp, task.outputfile.split('.')[0] + '_Error.erp')
            EEGresp = eegpipe.collapsechannels(EEGresp, Channels = ['FCZ','C3', 'CZ', 'C4'], NewChannelName='HOTSPOT', Approach='median')
        except:
            EEGresp = None
        
        if EEGresp != None:
            #[outputamplitude, outputlatency] = eegpipe.extractpeaks(EEGresp, Window=[0.300, 0.700], Points=9)
            outputamplitude = eegpipe.extractamplitude(EEGresp, Window=[-0.100, 0.100], Approach='mean')
            eggscale = eegpipe.determinerescale(eggscale, outputamplitude)
            outputchannels = EEGresp.channels
            # snag waveform
            errorwave = eegpipe.waveformplotprep()
            errorwave.title = 'Monitoring'
            errorwave.x = EEGresp.times
            errorwave.y = EEGresp.data[outputchannels.index('HOTSPOT')]
            errorwave.linestyle='solid'
            errorwave.linecolor= '#2A60EB'
            errorwave.lineweight=2
            errorwave.fillbetween='ZeroN'
            errorwave.fillwindow=[-0.1,0.2]
            if wavechunk == None:
                wavechunk = [errorwave]
            else: 
                wavechunk.append(errorwave)
                
            # place in bar
            Monitoring = eegpipe.barplotprep()
            Monitoring.title = 'Monitoring'
            Monitoring.labels = ['Error']
            Monitoring.values = [outputamplitude[outputchannels.index('HOTSPOT')]]
            Monitoring.scale = [-10, 0]
            Monitoring.biggerisbetter = False
            Monitoring.unit = ' microV'
            barchunks.append(Monitoring)
            
            # snag egghead
            [outputchannels, outputamplitude] = eegpipe.eggpad(outputchannels, outputamplitude)
            erroregg = eegpipe.eggheadplotprep()
            erroregg.title = 'Monitoring'
            erroregg.channels = outputchannels
            erroregg.amplitudes = outputamplitude  
            erroregg.scale = [-9, 1]
            erroregg.steps = 256
            erroregg.opacity = 0.2  
            if eggchunk == None:
                eggchunk = [erroregg]
            else: 
                eggchunk.append(erroregg)
            
        if eggchunk != None:
            eggscale = eegpipe.centershift(eggscale)
            for cA in range(len(eggchunk)):
                eggchunk[cA].scale = eggscale
        
    eegpipe.reportingwindow(eggs=eggchunk, waveforms=wavechunk, bars=barchunks, fileout = task.outputfile.split('.')[0] + '.png')

    # Backup data
    #filesync.pushfiles(inpath = '\\Studies\Raw', outpath = 'Z:\Studies\Raw', file_types = ['.psydat', '.tsv', '.tsve', '.csv', '.csve'])
    
