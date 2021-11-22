import os
from Engine.basicstimuluspresentationengine import Engine
import Engine.generatesequence as generatesequence
from Engine.checkperformance import performancereporter

if __name__ == "__main__":
    # Unicorn multiprocessing will not run in Spyder 
    # Run -> Configuration per file... 
    # Change the Console to Execute in an external system terminal
    # Select the checkbox for External system terminal Interact with the Python console after execution
    
    task = Engine()
    
    # Instructions
    task.instructioncard = ['FlankerPrac1.png', 'FlankerPrac2.png', 'FlankerPrac3.png', 'FlankerPrac4.png', 'FlankerPrac5.png', 'FlankerPrac6.png']
    
    # Sequence File
    #generatesequence.createflankersequence(filout = task.folders.sequencefolder + os.path.sep + 'randomsequence.csv', cycles = 1, style = 1, parameters = [0, 150, 80, 1000, 1500, ['f','j']], variableiti = 50.0, feedback = [80, 0, 1, 1, 1, 1])
    generatesequence.createflankersequence(filout = task.folders.sequencefolder + os.path.sep + 'randomsequence.csv', cycles = 1, style = 1, parameters = [55, 150, 80, 1000, 1500, ['f','j']], variableiti = 50.0, feedback = [80, 0, 1, 1, 1, 1])
    task.sequence = 'randomsequence.csv'
    
    # Filename Prefix and Suffix
    task.prefix = 'FT'
    task.suffix = ''
    task.filenametooltip = 'Format: ### Remember to add condition after the ID.'
    task.testblock = False
    
    # Global image frame/mask
    task.permanentframemask = 'flankerfixation.png'
    
    # Usable keys during task
    task.participantkeys = ['enter', 'f', 'j']
    
    # Experiment Flow Settings
    task.delaybeforestart = 3 # Seconds between end of instructions and beginning of task
    task.participantprogressnotice = [0.1, 0.25, 0.5, 0.75, 0.9]
    
    # Modify Screen Settings for Participant
    task.participantmonitor.displaynumber = 0 # Monitor Number
    task.participantmonitor.resolution = (1920, 1080)
    task.participantmonitor.backgroundcolor = '#595959' # RGB Codes (-1 to 1) or Hex Code
    task.participantmonitor.forgroundcolor = '#FFFFFF' # RGB Codes (-1 to 1) or Hex Code
    
    # Device Settings
    task.unicorn = 'UN-2019.05.51' # [] if using other system
    task.unicornchannels = 'FZ, FC1, FC2, CP3, CPZ, CP4, PZ, POZ, AccelX, AccelY, AccelZ, GyroX, GyroY, GyroZ, Battery, Sample'
    
    # Begin the Task
    task.start()
    
    # if the task finished then pull the data
    if task.finished:
        performancereporter(task)