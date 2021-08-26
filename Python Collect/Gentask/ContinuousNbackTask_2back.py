import os
import Engine.xcat as xcat
import Engine.filesync as filesync
from Engine.basicstimuluspresentationengine import Engine
import Engine.generatesequence as generatesequence
import Engine.eegpipe as eegpipe

if __name__ == "__main__":
    # Unicorn multiprocessing will not run in Spyder 
    # Run -> Configuration per file... 
    # Change the Console to Execute in an external system terminal
    # Select the checkbox for External system terminal Interact with the Python console after execution
    
    task = Engine()
    
    # Instructions
    task.instructioncard = ['SNBfp1.png', 'SNBfp2.png', 'SNBfp3.png', 'SNBfp4.png', 'SNBfp5.png', 'SNBfp6.png', 'SNBfp7.png']
    task.showinstructions = True
    
    # Sequence File
    generatesequence.createnbacksequence(filout = task.folders.sequencefolder + os.path.sep + 'randomsequence.csv', cycles = 1, style = 3, back = 2, parameters = [1400, 100, 1450, 1500, ['s','d','f','j','k','l']], feedback = [80, 0, 1, 1, 0, 1])
    task.sequence = 'randomsequence.csv'
    
    # Filename Prefix and Suffix
    task.prefix = 'CNB'
    task.suffix = ''
    task.filenametooltip = 'Format: ### Remember to add condition after the ID.'
    task.testblock = False
    
    # Global image frame/mask
    task.permanentframemask = 'SNB6gridflat.png'
    
    # Usable keys during task
    task.participantkeys = ['1', '4', 'enter', 'a', 'l', 'm', 's','d','f','j','k']
    
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
    datapull = [[0], [0], [0]]
    taskoutput = xcat.BehavioralAnalysis()
    taskoutput.run(inputfile = task.outputfile, trialtypes = list(range(10,50)))
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
    Consistency.scale = [20, 300]
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
        
    eegpipe.reportingwindow(eggs=eggchunk, waveforms=wavechunk, bars=barchunks)
    # Backup data
    #filesync.pushfiles(inpath = '\\Studies\Raw', outpath = 'Z:\Studies\Raw', file_types = ['.psydat', '.tsv', '.tsve', '.csv', '.csve'])
    
