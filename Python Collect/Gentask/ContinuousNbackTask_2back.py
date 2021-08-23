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
    task.prefix = 'NB'
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
    task.unicornrequired = False
    
    # Begin the Task
    task.start()
    
    #task.outputfile = 'Raw\OBMattApril2.psydat'
    # Check Performance Settings using xcat
    taskoutput = xcat.BehavioralAnalysis()
    datapull = [[0], [0], [0]]
    taskoutput.run(inputfile = task.outputfile, trialtypes = [10, 20, 30, 40])
    taskoutput.show(label = 'All', header = True)
    datapull[0][0] = taskoutput.meanrt
    datapull[1][0] = taskoutput.sdrt
    datapull[2][0] = taskoutput.responseaccuracy
    #taskoutput.run(inputfile = task.outputfile, trialtypes = [30, 40])
    #taskoutput.show(label = 'Target')
    #taskoutput.run(inputfile = task.outputfile, trialtypes = [10, 20])
    #taskoutput.show(label = 'Nontarget')
    
    # Process EEG    
    print('\nPlease wait while the EEG data is rapid processed.')
    eggchunk = None
    wavechunk = None
    try:
        EEG = eegpipe.readUnicornBlack(task.outputfile.split('.')[0] + '.csv')
        try:
            EEG = eegpipe.mergetaskperformance(EEG, task.outputfile.split('.')[0] + '.psydat')
        except:
            boolfail = True
        EEG = eegpipe.simplefilter(EEG, Filter = 'Notch', Cutoff = [60.0])
        EEG = eegpipe.simplefilter(EEG, Filter = 'Bandpass', Design = 'Butter', Cutoff = [1.0, 25.0], Order=3)
        EEG = eegpipe.simpleepoch(EEG, Window = [-0.500, 1.000], Types = [20, 10020])
        EEG = eegpipe.simplebaselinecorrect(EEG, Window = [-0.100, 0.0])
        EEG = eegpipe.voltagethreshold(EEG, Threshold = [-100.0, 100.0], Step = 50.0)
        EEG = eegpipe.simplefilter(EEG, Design = 'savitzky-golay', Order = 4)
        EEG = eegpipe.simplezwave(EEG, BaselineWindow = [-0.500, 0.0])
        EEG = eegpipe.simpleaverage(EEG, Approach = 'Mean')
        eegpipe.saveset(EEG, task.outputfile)
        
        #[outputamplitude, outputlatency] = eegpipe.extractpeaks(EEG, Window=[0.300, 0.700], Points=9)
        outputamplitude = eegpipe.extractamplitude(EEG, Window=[0.300, 0.700], Approach='mean')
        outputchannels = [x.strip() for x in task.unicornchannels.split(',')[0:8]]
        [outputchannels, outputamplitude] = eegpipe.eggpad(outputchannels, outputamplitude)
        eegpipe.eggheadplot(outputchannels, outputamplitude, Scale = [0, max(outputamplitude)*0.9], Steps = 256, BrainOpacity = 0.2, Title ='Egghead', Colormap=eegpipe.crushparula(256))
    except:
        boolfail = True
        
    # send data to reporting window
    Speed = eegpipe.barplotprep()
    Speed.title = 'Speed'
    Speed.labels = ['All']
    Speed.values = datapull[0]
    Speed.scale = [150, 500]
    Speed.biggerisbetter = False
    Speed.unit = ' ms'
    
    Consistency = eegpipe.barplotprep()
    Consistency.title = 'Consistency'
    Consistency.labels = ['All']
    Consistency.values = datapull[1]
    Consistency.scale = [20, 300]
    Consistency.biggerisbetter = False
    Consistency.unit = ' ms'
    
    Accuracy = eegpipe.barplotprep()
    Accuracy.title = 'Accuracy'
    Accuracy.labels = ['All']
    Accuracy.values = datapull[2]
    Accuracy.scale = [70, 100]
    Accuracy.biggerisbetter = True
    Accuracy.unit = ' %'
    
    barchunks = [Speed, Consistency, Accuracy]
    eegpipe.reportingwindow(eggs=eggchunk, waveforms=wavechunk, bars=barchunks)
    # Backup data
    #filesync.pushfiles(inpath = '\\Studies\Raw', outpath = 'Z:\Studies\Raw', file_types = ['.psydat', '.tsv', '.tsve', '.csv', '.csve'])
    