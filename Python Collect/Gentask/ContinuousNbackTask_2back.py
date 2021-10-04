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
    task.instructioncard = ['SNBfp1.png', 'SNBfp2.png', 'SNBfp3.png', 'SNBfp4.png', 'SNBfp5.png', 'SNBfp6.png', 'SNBfp7.png']
    
    # Sequence File
    generatesequence.createnbacksequence(filout = task.folders.sequencefolder + os.path.sep + 'randomsequence.csv', cycles = 1, style = 3, back = 2, parameters = [1480, 100, 1480, 1500, ['s','d','f','j','k','l']], feedback = [80, 0, 1, 1, 0, 1])
    task.sequence = 'randomsequence.csv'
    
    # Filename Prefix and Suffix
    task.prefix = 'CN2B'
    task.suffix = ''
    task.filenametooltip = 'Format: ### Remember to add condition after the ID.'
    task.testblock = False
    
    # Global image frame/mask
    task.permanentframemask = 'SNB6gridflat.png'
    
    # Usable keys during task
    task.participantkeys = ['1', '4', 'enter', 'a', 'l', 'm', 's','d','f','j','k']
    
    # Experiment Flow Settings
    task.delaybeforestart = 2 # Seconds between end of instructions and beginning of task
    
    # Modify Screen Settings for Participant
    task.participantmonitor.displaynumber = 0 # Monitor Number
    task.participantmonitor.resolution = (1920, 1080)
    task.participantmonitor.backgroundcolor = '#787878' # RGB Codes (-1 to 1) or Hex Code
    task.participantmonitor.forgroundcolor = '#FFFFFF' # RGB Codes (-1 to 1) or Hex Code
    
    # Device Settings
    task.unicorn = 'UN-2019.05.51' # [] if using other system
    task.unicornchannels = 'FZ, FC1, FC2, C3, CZ, C4, CPZ, PZ, AccelX, AccelY, AccelZ, GyroX, GyroY, GyroZ, Battery, Sample'
    
    # Begin the Task
    task.start()
    
    # if the task finished then pull the data
    if task.finished:
        performancereporter(task)
    