import os
from Engine.basicstimuluspresentationengine import Engine
import Engine.generatesequence as generatesequence
from Engine.checkperformance import performancereporter

if __name__ == "__main__":
    # Unicorn multiprocessing will not run in Spyder 
    # Run -> Configuration per file... 
    # Change the Console to Execute in an external system terminal
    # Select the checkbox for External system terminal Interact with the Python console after execution

    with open('UnicornDeviceID.txt', 'r') as f:
        unicorndeviceid = f.read(); f.close()
    
    task = Engine()
    
    # Instructions
    task.instructioncard = ['SNBp1.png', 'SNBp2.png', 'SNBp3.png', 'SNBp4.png', 'SNBp5.png', 'SNBp6.png', 'SNBp7.png']
    
    # Sequence File
    generatesequence.createnbacksequence(filout = task.folders.sequencefolder + os.path.sep + 'randomsequence.csv', cycles = 1, style = 1, back = 2, parameters = [500, 100, 2450, 2500, ['f', 'j']], feedback = [80, 0, 1, 1, 1, 1])
    task.sequence = 'randomsequence.csv'
    
    # Filename Prefix and Suffix
    task.prefix = 'N2B'
    task.suffix = ''
    task.filenametooltip = 'Format: ### Remember to add condition after the ID.'
    task.testblock = False
    
    # Global image frame/mask
    task.permanentframemask = 'SNB6grid.png'
    
    # Usable keys during task
    task.participantkeys = ['enter', 'f', 'j']
    task.participantprogressnotice = [0.1, 0.25, 0.5, 0.75, 0.9]
    
    # Experiment Flow Settings
    task.delaybeforestart = 3 # Seconds between end of instructions and beginning of task
    
    # Modify Screen Settings for Participant
    task.participantmonitor.displaynumber = 0 # Monitor Number
    task.participantmonitor.resolution = (1920, 1080)
    task.participantmonitor.backgroundcolor = '#595959' # RGB Codes (-1 to 1) or Hex Code
    task.participantmonitor.forgroundcolor = '#FFFFFF' # RGB Codes (-1 to 1) or Hex Code
    
    # Device Settings
    task.unicorn = unicorndeviceid
    task.unicornchannels = 'FZ, FC1, FC2, CP3, CPZ, CP4, PZ, POZ, AccelX, AccelY, AccelZ, GyroX, GyroY, GyroZ, Battery, Sample'
    
    # Begin the Task
    task.start()
    
    # if the task finished then pull the data
    if task.finished:
        performancereporter(task)
    