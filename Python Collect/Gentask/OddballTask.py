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
    
    task = Engine()
    
    # Instructions
    task.instructioncard = ['OddballInstructions.png']
    task.showinstructions = True
    
    # Sequence File
    generatesequence.createoddballsequence(filout = task.folders.sequencefolder + os.path.sep + 'randomsequence.csv', cycles = 1, parameters = [200, 200, 900, 1100, 'm'])
    task.sequence = 'randomsequence.csv'
    
    # Filename Prefix and Suffix
    task.prefix = 'OB'
    task.suffix = ''
    task.filenametooltip = 'Format: ### Remember to add condition after the ID.'
    task.testblock = False
    
    # Global image frame/mask
    task.permanentframemask = ''
    
    # Usable keys during task
    task.participantkeys = ['1', '4', 'enter', 'a', 'l', 'm']
    
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
    task.unicornrequired = True
    
    # Begin the Task
    task.start()
    
    
    
    
    
    
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
    
    Accuracy = eegpipe.barplotprep()
    Accuracy.title = 'Accuracy'
    Accuracy.labels = ['Target', 'Nontarget']
    Accuracy.values = datapull[2]
    Accuracy.scale = [80, 100]
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
        except:
            EEGtarg = None
        
        if EEGtarg != None:
            [outputamplitude, outputlatency] = eegpipe.extractpeaks(EEGtarg, Window=[0.300, 0.700], Points=9)
            outputamplitude = eegpipe.extractamplitude(EEGtarg, Window=[0.300, 0.700], Approach='mean')
            outputchannels = [x.strip() for x in task.unicornchannels.split(',')[0:8]]
            # snag waveform
            targetwave = eegpipe.waveformplotprep()
            targetwave.title = 'Target'
            targetwave.x = EEGtarg.times
            targetwave.y = EEGtarg.data[outputchannels.index('PZ')]
            targetwave.linestyle='solid'
            targetwave.linecolor= '#2A60EB'
            targetwave.lineweight=2
            # snag egghead
            [outputchannels, outputamplitude] = eegpipe.eggpad(outputchannels, outputamplitude)
            targetegg = eegpipe.eggheadplotprep()
            targetegg.title = 'Target'
            targetegg.channels = outputchannels
            targetegg.amplitudes = outputamplitude  
            targetegg.scale = [1, 9]
            targetegg.steps = 256
            targetegg.opacity = 0.2  
            
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
        except:
            EEGdist = None
            
        if EEGdist != None:
            [outputamplitude, outputlatency] = eegpipe.extractpeaks(EEGdist, Window=[0.300, 0.700], Points=9)
            outputamplitude = eegpipe.extractamplitude(EEGdist, Window=[0.300, 0.700], Approach='mean')
            outputchannels = [x.strip() for x in task.unicornchannels.split(',')[0:8]]
            # snag waveform
            distractorwave = eegpipe.waveformplotprep()
            distractorwave.title = 'Distractor'
            distractorwave.x = EEGdist.times
            distractorwave.y = EEGdist.data[outputchannels.index('PZ')]
            distractorwave.linestyle='solid'
            distractorwave.linecolor= '#A91CD4'
            distractorwave.lineweight=2
            # snag egghead
            [outputchannels, outputamplitude] = eegpipe.eggpad(outputchannels, outputamplitude)
            distractoregg = eegpipe.eggheadplotprep()
            distractoregg.title = 'Distractor'
            distractoregg.channels = outputchannels
            distractoregg.amplitudes = outputamplitude 
            distractoregg.scale = [1, 9]
            distractoregg.steps = 256
            distractoregg.opacity = 0.2   
        
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
        
        # place structures      
        eggchunk = [targetegg, distractoregg]
        wavechunk = [Reference, targetwave, distractorwave]
        
    eegpipe.reportingwindow(eggs=eggchunk, waveforms=wavechunk, bars=barchunks, fileout = task.outputfile.split('.')[0] + '.png')

    # Backup data
    #filesync.pushfiles(inpath = '\\Studies\Raw', outpath = 'Z:\Studies\Raw', file_types = ['.psydat', '.tsv', '.tsve', '.csv', '.csve'])
    