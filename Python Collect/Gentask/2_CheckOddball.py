import os
import Engine.xcat as xcat
import Engine.filesync as filesync
from Engine.basicstimuluspresentationengine import Engine
import Engine.generatesequence as generatesequence
import Engine.eegpipe as eegpipe
import numpy
import scipy

if __name__ == "__main__":
    # Unicorn multiprocessing will not run in Spyder 
    # Run -> Configuration per file... 
    # Change the Console to Execute in an external system terminal
    # Select the checkbox for External system terminal Interact with the Python console after execution
    
    task = Engine()
    task.outputfile = 'Raw\OBmatt97.psydat'
    task.finished = True
    
    
    
    
    ###### Post task options ######################################################################################
    
    
    ### Pull behavioral performance
    #task.outputfile = 'Raw\OBReportTest.psydat'
    
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
        try:
            EEG = eegpipe.mergetaskperformance(EEG, task.outputfile.split('.')[0] + '.psydat')
        except:
            boolfail = True
        EEG = eegpipe.simplefilter(EEG, Filter = 'Notch', Cutoff = [60.0])
        EEG = eegpipe.simplefilter(EEG, Filter = 'Bandpass', Design = 'Butter', Cutoff = [1.0, 25.0], Order=3)
        
        # Distractor stimulus - 30
        EEGdist = None
        try:
            EEGdist = eegpipe.simpleepoch(EEG, Window = [-0.500, 1.000], Types = [30, 10030])
            EEGdist = eegpipe.simplebaselinecorrect(EEGdist, Window = [-0.100, 0.0])
            EEGdist = eegpipe.voltagethreshold(EEGdist, Threshold = [-100.0, 100.0], Step = 50.0)
            EEGdist = eegpipe.simplefilter(EEGdist, Design = 'savitzky-golay', Order = 4)
            EEGdist = eegpipe.simplezwave(EEGdist, BaselineWindow = [-0.500, 0.0])
            EEGdist = eegpipe.simpleaverage(EEGdist, Approach = 'Mean')
            eegpipe.saveset(EEGdist, task.outputfile.split('.')[0] + '_Distractor.erp')
            EEGdist = eegpipe.collapsechannels(EEGdist, Channels = ['C3', 'CZ', 'C4', 'CPZ', 'PZ', 'POZ'], NewChannelName='HOTSPOT', Approach='median')
            EEGdist = eegpipe.simplefilter(EEGdist, Design = 'savitzky-golay', Order = 4)
        except:
            EEGdist = None
            
        if EEGdist != None:
            [outputamplitude, outputlatency] = eegpipe.extractpeaks(EEGdist, Window=[0.300, 0.700], Points=9)
            outputamplitude = eegpipe.extractamplitude(EEGdist, Window=[0.300, 0.700], Approach='mean')
            outputchannels = EEGdist.channels
            # snag waveform
            distractorwave = eegpipe.waveformplotprep()
            distractorwave.title = 'Orientation'
            distractorwave.x = EEGdist.times
            distractorwave.y = EEGdist.data[outputchannels.index('HOTSPOT')]
            distractorwave.linestyle='solid'
            distractorwave.linecolor= '#A91CD4'
            distractorwave.lineweight=2
            if wavechunk == None:
                wavechunk = [distractorwave]
            else: 
                wavechunk.append(distractorwave)
            
            # snag egghead
            [outputchannels, outputamplitude] = eegpipe.eggpad(outputchannels, outputamplitude)
            distractoregg = eegpipe.eggheadplotprep()
            distractoregg.title = 'Orientation'
            distractoregg.channels = outputchannels
            distractoregg.amplitudes = outputamplitude 
            distractoregg.scale = [1, 9]
            distractoregg.steps = 256
            distractoregg.opacity = 0.2 
            if eggchunk == None:
                eggchunk = [distractoregg]
            else: 
                eggchunk.append(distractoregg)  
            # place in bar
            Orientation = eegpipe.barplotprep()
            Orientation.title = 'Orientation'
            Orientation.labels = ['Distractor']
            Orientation.values = [outputamplitude[outputchannels.index('HOTSPOT')]]
            Orientation.scale = [0, 20]
            Orientation.biggerisbetter = True
            Orientation.unit = ' microV'
            barchunks.append(Orientation)
            
            
        # Target stimulus - 20
        EEGtarg = None
        try:
            EEGtarg = eegpipe.simpleepoch(EEG, Window = [-0.500, 1.000], Types = [20, 10020])
            EEGtarg = eegpipe.simplebaselinecorrect(EEGtarg, Window = [-0.100, 0.0])
            EEGtarg = eegpipe.voltagethreshold(EEGtarg, Threshold = [-100.0, 100.0], Step = 50.0)
            EEGtarg = eegpipe.simplefilter(EEGtarg, Design = 'savitzky-golay', Order = 4)
            EEGtarg = eegpipe.simplezwave(EEGtarg, BaselineWindow = [-0.500, 0.0])
            EEGtarg = eegpipe.simpleaverage(EEGtarg, Approach = 'Mean')
            eegpipe.saveset(EEGtarg, task.outputfile.split('.')[0] + '_Target.erp')
            EEGtarg = eegpipe.collapsechannels(EEGtarg, Channels = ['C3', 'CZ', 'C4', 'CPZ', 'PZ', 'POZ'], NewChannelName='HOTSPOT', Approach='median')
            EEGtarg = eegpipe.simplefilter(EEGtarg, Design = 'savitzky-golay', Order = 4)
        except:
            EEGtarg = None
        
        if EEGtarg != None:
            [outputamplitude, outputlatency] = eegpipe.extractpeaks(EEGtarg, Window=[0.300, 0.700], Points=9)
            outputamplitude = eegpipe.extractamplitude(EEGtarg, Window=[0.300, 0.700], Approach='mean')
            outputchannels = EEGtarg.channels
            # snag waveform
            targetwave = eegpipe.waveformplotprep()
            targetwave.title = 'Attention'
            targetwave.x = EEGtarg.times
            targetwave.y = EEGtarg.data[outputchannels.index('HOTSPOT')]
            targetwave.linestyle='solid'
            targetwave.linecolor= '#2A60EB'
            targetwave.lineweight=2
            if wavechunk == None:
                wavechunk = [targetwave]
            else: 
                wavechunk.append(targetwave)
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
               
        
        
    eegpipe.reportingwindow(eggs=eggchunk, waveforms=wavechunk, bars=barchunks, fileout = task.outputfile.split('.')[0] + '.png')

    # Backup data
    #filesync.pushfiles(inpath = '\\Studies\Raw', outpath = 'Z:\Studies\Raw', file_types = ['.psydat', '.tsv', '.tsve', '.csv', '.csve'])
    
