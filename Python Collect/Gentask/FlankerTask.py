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
    task.instructioncard = ['FlankerPrac1.png', 'FlankerPrac2.png', 'FlankerPrac3.png', 'FlankerPrac4.png', 'FlankerPrac5.png', 'FlankerPrac6.png']
    task.showinstructions = True
    
    # Sequence File
    generatesequence.createflankersequence(filout = task.folders.sequencefolder + os.path.sep + 'randomsequence.csv', cycles = 1, style = 1, parameters = [55, 100, 80, 1000, 1500, ['z','m']], variableiti = False, feedback = [80, 0, 1, 1, 1, 1])
    task.sequence = 'randomsequence.csv'
    
    # Filename Prefix and Suffix
    task.prefix = 'FT'
    task.suffix = ''
    task.filenametooltip = 'Format: ### Remember to add condition after the ID.'
    task.testblock = False
    
    # Global image frame/mask
    task.permanentframemask = ''
    
    # Usable keys during task
    task.participantkeys = ['1', '4', 'enter', 'a', 'l', 'z', 'm', 's','d','f','j','k']
    
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
    taskoutput.run(inputfile = task.outputfile, trialtypes = [10, 12, 30, 31, 32, 33, 34, 35, 36, 37, 20, 22, 40, 41, 42, 43, 44, 45, 46, 47])
    taskoutput.show(label = 'All', header = True)
    taskoutput.run(inputfile = task.outputfile, trialtypes = [10, 12, 30, 31, 32, 33, 34, 35, 36, 37])
    taskoutput.show(label = 'Congruent')
    taskoutput.run(inputfile = task.outputfile, trialtypes = [20, 22, 40, 41, 42, 43, 44, 45, 46, 47])
    taskoutput.show(label = 'Incongruent')
    
    # Process EEG    
    print('\nPlease wait while the EEG data is rapid processed.')
    EEG = eegpipe.readUnicornBlack(task.outputfile.split('.')[0] + '.csv')
    try:
        EEG = eegpipe.mergetaskperformance(EEG, task.outputfile.split('.')[0] + '.psydat')
    except:
        bollfail = True
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


    # Backup data
    #filesync.pushfiles(inpath = '\\Studies\Raw', outpath = 'Z:\Studies\Raw', file_types = ['.psydat', '.tsv', '.tsve', '.csv', '.csve'])
    
