import os
import Engine.xcat as xcat
import Engine.filesync as filesync
from Engine.basicstimuluspresentationengine import Engine
import Engine.generatesequence as generatesequence
import Engine.eegpipe as eegpipe
import numpy

if __name__ == "__main__":
    # Unicorn multiprocessing will not run in Spyder 
    # Run -> Configuration per file... 
    # Change the Console to Execute in an external system terminal
    # Select the checkbox for External system terminal Interact with the Python console after execution
    
    # tools -> Preferences -> iPython console -> Graphics -> Automatic
    
    task = Engine()
    
    # Instructions
    task.instructioncard = ['FlankerPrac1.png', 'FlankerPrac2.png', 'FlankerPrac3.png', 'FlankerPrac4.png', 'FlankerPrac5.png', 'FlankerPrac6.png']
    task.showinstructions = True
    
    # Sequence File
    generatesequence.createflankersequence(filout = task.folders.sequencefolder + os.path.sep + 'randomsequence.csv', cycles = 1, style = 1, parameters = [55, 150, 80, 1000, 1500, ['z','m']], variableiti = 50.0, feedback = [80, 0, 1, 1, 1, 1])
    task.sequence = 'randomsequence.csv'
    
    # Filename Prefix and Suffix
    task.prefix = 'FT'
    task.suffix = ''
    task.filenametooltip = 'Format: ### Remember to add condition after the ID.'
    task.testblock = False
    
    # Global image frame/mask
    task.permanentframemask = 'flankerfixation.png'
    
    # Usable keys during task
    task.participantkeys = ['1', '4', 'enter', 'z', 'm']
    
    # Experiment Flow Settings
    task.pauseatstart = False # Only Experimentor can advance to the task after the instructions
    task.delaybeforestart = 5 # Seconds between end of instructions and beginning of task
    task.pauseatend = False
    
    # Modify Screen Settings for Participant
    task.participantmonitor.displaynumber = 0 # Monitor Number
    task.participantmonitor.resolution = (1920, 1080)
    task.participantmonitor.physicalsize = (53,30) # physical screen size in centimeters
    task.participantmonitor.backgroundcolor = '#787878' # RGB Codes (-1 to 1) or Hex Code
    task.participantmonitor.forgroundcolor = '#FFFFFF' # RGB Codes (-1 to 1) or Hex Code
    
    # Event Triggers
    task.triggers = True
    task.markfirstresponseonly = True
    task.unicorn = 'UN-2019.05.51' # [] if using other system
    #task.unicornchannels = 'FZ, CP1, CPZ, CP2, P1, PZ, P2, OZ, AccelX, AccelY, AccelZ, GyroX, GyroY, GyroZ, Battery, Sample'
    task.unicornchannels = 'FZ, FCZ, C3, CZ, C4, CPZ, PZ, POZ, AccelX, AccelY, AccelZ, GyroX, GyroY, GyroZ, Battery, Sample'
    task.unicornchannels = 'FC1, FC2, C3, C4, CPZ, P1, P2, POZ, AccelX, AccelY, AccelZ, GyroX, GyroY, GyroZ, Battery, Sample'
    task.unicornrequired = True
    
    # Begin the Task
    task.start()
    
    
    
    
    
    ###### Post task options ######################################################################################
    
    
    ### Pull behavioral performance
    #task.outputfile = 'Raw\OBReportTest.psydat'
    
    # Check Performance Settings using xcat
    datapull = [[0, 0], [0, 0], [0, 0]]
    taskoutput = xcat.BehavioralAnalysis()
    taskoutput.run(inputfile = task.outputfile, trialtypes = [10, 12, 30, 31, 32, 33, 34, 35, 36, 37, 20, 22, 40, 41, 42, 43, 44, 45, 46, 47])
    taskoutput.show(label = 'All', header = True)
    taskoutput.run(inputfile = task.outputfile, trialtypes = [10, 12, 30, 31, 32, 33, 34, 35, 36, 37])
    taskoutput.show(label = 'Congruent')
    datapull[0][0] = taskoutput.meanrt
    datapull[1][0] = taskoutput.sdrt
    datapull[2][0] = taskoutput.responseaccuracy
    taskoutput.run(inputfile = task.outputfile, trialtypes = [20, 22, 40, 41, 42, 43, 44, 45, 46, 47])
    taskoutput.show(label = 'Incongruent')
    datapull[0][1] = taskoutput.meanrt
    datapull[1][1] = taskoutput.sdrt
    datapull[2][1] = taskoutput.responseaccuracy
    
    # send data to reporting window
    Speed = eegpipe.barplotprep()
    Speed.title = 'Speed'
    Speed.labels = ['Congruent', 'Incongruent']
    Speed.values = datapull[0]
    Speed.scale = [150, 600]
    Speed.biggerisbetter = False
    Speed.unit = ' ms'
    
    Consistency = eegpipe.barplotprep()
    Consistency.title = 'Consistency'
    Consistency.labels = ['Congruent', 'Incongruent']
    Consistency.values = datapull[1]
    Consistency.scale = [20, 300]
    Consistency.biggerisbetter = False
    Consistency.unit = ' ms'
    
    Accuracy = eegpipe.barplotprep()
    Accuracy.title = 'Inhibition'
    Accuracy.labels = ['Congruent', 'Incongruent']
    Accuracy.values = datapull[2]
    Accuracy.scale = [75, 100]
    Accuracy.biggerisbetter = True
    Accuracy.unit = ' %'
    
    barchunks = [Speed, Consistency, Accuracy]
    
    
    
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
        
        
        # Stimulus locked - 30
        stimcodes = [10, 12, 30, 31, 32, 33, 34, 35, 36, 37] # congruent
        stimcodes.extend([20, 22, 40, 41, 42, 43, 44, 45, 46, 47]) # incongruent
        stimcodes = numpy.ndarray.tolist(numpy.add(stimcodes, 10000)) # only accept correct trials
        EEGstim = None
        try:
            EEGstim = eegpipe.simpleepoch(EEG, Window = [-0.500, 1.000], Types = stimcodes)
            EEGstim = eegpipe.simplebaselinecorrect(EEGstim, Window = [-0.100, 0.0])
            EEGstim = eegpipe.voltagethreshold(EEGstim, Threshold = [-100.0, 100.0], Step = 50.0)
            EEGstim = eegpipe.simplefilter(EEGstim, Design = 'savitzky-golay', Order = 4)
            EEGstim = eegpipe.simplezwave(EEGstim, BaselineWindow = [-0.500, 0.0])
            EEGstim = eegpipe.simpleaverage(EEGstim, Approach = 'Mean')
            eegpipe.saveset(EEGstim, task.outputfile.split('.')[0] + '_StimLocked.erp')
            EEGstim = eegpipe.collapsechannels(EEGstim, Channels = ['C3', 'CZ', 'C4', 'CPZ', 'PZ', 'POZ'], NewChannelName='HOTSPOT', Approach='median')
        except:
            EEGstim = None
            
        if EEGstim != None:
            [outputamplitude, outputlatency] = eegpipe.extractpeaks(EEGstim, Window=[0.300, 0.700], Points=9)
            outputamplitude = eegpipe.extractamplitude(EEGstim, Window=[0.300, 0.700], Approach='mean')
            outputchannels = EEGstim.channels
            # snag waveform
            stimwave = eegpipe.waveformplotprep()
            stimwave.title = 'Stimlocked'
            stimwave.x = EEGstim.times
            stimwave.y = EEGstim.data[outputchannels.index('HOTSPOT')]
            stimwave.linestyle='solid'
            stimwave.linecolor= '#A91CD4'
            stimwave.lineweight=2
            if wavechunk == None:
                wavechunk = [stimwave]
            else: 
                wavechunk.append(stimwave)
            
            # snag egghead
            [outputchannels, outputamplitude] = eegpipe.eggpad(outputchannels, outputamplitude)
            stimegg = eegpipe.eggheadplotprep()
            stimegg.title = 'Attention'
            stimegg.channels = outputchannels
            stimegg.amplitudes = outputamplitude 
            stimegg.scale = [1, 9]
            stimegg.steps = 256
            stimegg.opacity = 0.2  
            if eggchunk == None:
                eggchunk = [stimegg]
            else: 
                eggchunk.append(stimegg)
                
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
            Reference.title = 'Reference Stimlocked'
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
            outputchannels = EEGresp.channels
            # snag waveform
            errorwave = eegpipe.waveformplotprep()
            errorwave.title = 'Error'
            errorwave.x = EEGresp.times
            errorwave.y = EEGresp.data[outputchannels.index('HOTSPOT')]
            errorwave.linestyle='solid'
            errorwave.linecolor= '#2A60EB'
            errorwave.lineweight=2
            if wavechunk == None:
                wavechunk = [errorwave]
            else: 
                wavechunk.append(errorwave)
            # snag egghead
            [outputchannels, outputamplitude] = eegpipe.eggpad(outputchannels, outputamplitude)
            erroregg = eegpipe.eggheadplotprep()
            erroregg.title = 'Error'
            erroregg.channels = outputchannels
            erroregg.amplitudes = outputamplitude  
            erroregg.scale = [-9, 1]
            erroregg.steps = 256
            erroregg.opacity = 0.2  
            if eggchunk == None:
                eggchunk = [erroregg]
            else: 
                eggchunk.append(erroregg)
            # place in bar
            Monitoring = eegpipe.barplotprep()
            Monitoring.title = 'Monitoring'
            Monitoring.labels = ['Error']
            Monitoring.values = [outputamplitude[outputchannels.index('HOTSPOT')]]
            Monitoring.scale = [-10, 0]
            Monitoring.biggerisbetter = False
            Monitoring.unit = ' microV'
            barchunks.append(Monitoring)
            
        
    eegpipe.reportingwindow(eggs=eggchunk, waveforms=wavechunk, bars=barchunks, fileout = task.outputfile.split('.')[0] + '.png')

    # Backup data
    #filesync.pushfiles(inpath = '\\Studies\Raw', outpath = 'Z:\Studies\Raw', file_types = ['.psydat', '.tsv', '.tsve', '.csv', '.csve'])
    