import os
from Engine.basicstimuluspresentationengine import Engine
import Engine.xcat as xcat

if __name__ == "__main__":
    # Unicorn multiprocessing will not run in Spyder 
    # Run -> Configuration per file... 
    # Change the Console to Execute in an external system terminal
    # Select the checkbox for External system terminal Interact with the Python console after execution
    
    with open('UnicornDeviceID.txt', 'r') as f:
        deviceID = f.read(); f.close()
    with open('UnicornDeviceChannels.txt', 'r') as f:
        deviceChannels  = f.read(); f.close()

    task = Engine()
    
    # Instructions
    task.instructioncard = ['FlankerPrac1.png', 'FlankerPrac2.png', 'FlankerPrac3.png', 'FlankerPrac4.png', 'FlankerPrac5.png', 'FlankerPrac6.png']
    
    # Sequence File
    task.sequence = 'Flanker_Practice.csv'
    
    # Filename Prefix and Suffix
    task.prefix = 'FT'
    task.suffix = ''
    task.filenametooltip = 'Format: ### Remember to add condition after the ID.'
    task.testblock = True
    
    # Global image frame/mask
    task.permanentframemask = 'flankerfixation.png'
    
    # Usable keys during task
    task.participantkeys = ['enter', 'f', 'j']
    
    # Onscreen touch buttons
    task.buttons = [
        {"pos": (0.9, 0.9), "buttonText": 'Quit', "buttonCode": 'q',
            "width": 0.1, "height":  0.1, 
            "lineColor": '#4A4A4A', "lineWidth": 0, 
            "fillColor": [1,1,1], "opacity": 0.1,
            "textColor": [0,0,0], "textOpacity": 1, "textHeight": 0.05},
        
        {"pos": (-0.88, 0.05), "buttonText": 'F', "buttonCode": 'f',
            "width": 0.15, "height":  0.2, 
            "lineColor": '#D4D4D4', "lineWidth": 0, 
            "fillColor": '#D4D4D4', "opacity": 0.85,
            "textColor": '#4A4A4A', "textOpacity": 1, "textHeight": 0.1},
        
        {"pos": (0.88, 0.05), "buttonText": 'J', "buttonCode": 'j',
            "width": 0.15, "height":  0.2, 
            "lineColor": '#D4D4D4', "lineWidth": 0, 
            "fillColor": '#D4D4D4', "opacity": 0.85,
            "textColor": '#4A4A4A', "textOpacity": 1, "textHeight": 0.1}         
    ]
    
    
    # Experiment Flow Settings
    task.delaybeforestart = 3 # Seconds between end of instructions and beginning of task
    task.participantprogressnotice = [0.1, 0.25, 0.5, 0.75, 0.9]
    
    # Modify Screen Settings for Participant
    task.participantmonitor.displaynumber = 0 # Monitor Number
    task.participantmonitor.resolution = (1920, 1080)
    task.participantmonitor.backgroundcolor = '#595959' # RGB Codes (-1 to 1) or Hex Code
    task.participantmonitor.forgroundcolor = '#FFFFFF' # RGB Codes (-1 to 1) or Hex Code
    
    # Device Settings
    task.unicorn = deviceID
    task.unicornchannels = deviceChannels  
    task.unicornrequired = False
    
    # Begin the Task
    task.start()
    
    # if the task finished then pull the data
    if task.finished:
        taskoutput = xcat.BehavioralAnalysis()
        taskoutput.run(inputfile = task.outputfile, trialtypes = [10, 12, 30, 31, 32, 33, 34, 35, 36, 37, 20, 22, 40, 41, 42, 43, 44, 45, 46, 47])
        taskoutput.show(label = 'All', header = True)
        taskoutput.run(inputfile = task.outputfile, trialtypes = [10, 12, 30, 31, 32, 33, 34, 35, 36, 37])
        taskoutput.show(label = 'Congruent')
        taskoutput.run(inputfile = task.outputfile, trialtypes = [20, 22, 40, 41, 42, 43, 44, 45, 46, 47])
        taskoutput.show(label = 'Incongruent')