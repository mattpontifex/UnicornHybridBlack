import os
import Engine.xcat as xcat
import Engine.filesync as filesync
from Engine.vepengine import Engine

#https://webvision.med.utah.edu/book/electrophysiology/visually-evoked-potentials/
#The major component of the VEP is the large positive wave peaking at about 100 milliseconds (Fig. 5).
# This “P100” or P1 in the jargon of evoked potentials, is very reliable between individuals and 
# stable from about age 5 years to 60 years.

if __name__ == "__main__":
    # Unicorn multiprocessing will not run in Spyder 
    # Run -> Configuration per file... 
    # Change the Console to Execute in an external system terminal
    # Select the checkbox for External system terminal Interact with the Python console after execution
    
    task = Engine()
    
    # Instructions
    task.showinstructions = True
    
    # Sequence File
    task.totaltrials = 10
    
    # Filename Prefix and Suffix
    task.prefix = 'VEP'
    task.suffix = ''
    task.filenametooltip = 'Format: ### Remember to add condition after the ID.'
    task.testblock = False
    
    # Global image frame/mask
    task.permanentframemask = ''
    
    # Usable keys during task
    task.participantkeys = ['1', '4', 'enter', 'a', 'l']
    
    # Experiment Flow Settings
    task.pauseatstart = False # Only Experimentor can advance to the task after the instructions
    task.delaybeforestart = 5 # Seconds between end of instructions and beginning of task
    task.pauseatend = False
    
    # Modify Screen Settings for Participant
    task.participantmonitor.displaynumber = 0 # Monitor Number
    task.participantmonitor.resolution = (1920, 1080)
    task.participantmonitor.physicalsize = (53,30) # physical screen size in centimeters
    task.participantmonitor.backgroundcolor = '#000000' # RGB Codes (-1 to 1) or Hex Code
    task.participantmonitor.forgroundcolor = '#FFFFFF' # RGB Codes (-1 to 1) or Hex Code
    
    # Modify Screen Settings for Experimenter
    task.experimentermonitor.displaynumber = 0 # Monitor Number
    task.experimentermonitor.resolution = (1200, 675)
    task.experimentermonitor.fullscreen = False
    task.experimentermonitor.gui = False # show gui
    task.experimentermonitor.backgroundcolor = '#000000' # RGB Codes (-1 to 1) or Hex Code
    task.experimentermonitor.forgroundcolor = '#FFFFFF' # RGB Codes (-1 to 1) or Hex Code
    task.activedisplaylog = True
    
    # Event Triggers
    task.triggers = True
    task.paralleltriggermodule = False # true if trying to send parallel port triggers
    task.markfirstresponseonly = True
    task.triggerportaddress = '0xD010'# 0xD010 on SynampsRT system  0xD050 on Grael
    task.unicorn = 'UN-2019.05.51' # [] if using other system
    task.unicornchannels = 'FZ, C3, CZ, C4, PZ, O1, OZ, O2, AccelX, AccelY, AccelZ, GyroX, GyroY, GyroZ, Battery, Sample'
    
    # Begin the Task
    task.start()
    
    # Check Performance Settings using xcat
    taskoutput = xcat.BehavioralAnalysis()
    taskoutput.run(inputfile = task.outputfile, trialtypes = [8, 9])
    taskoutput.show(label = 'All', header = True)
    
    # Backup data
    #filesync.pushfiles(inpath = '\\Studies\Raw', outpath = 'Z:\Studies\Raw', file_types = ['.psydat', '.tsv', '.tsve', '.csv', '.csve'])
    #filesync.pushfiles(inpath = '\\Studies\Raw', outpath = 'Z:\Studies\Raw', file_types = ['.dat', '.dap', '.rs3', '.cdt', '.cdt.dpa', '.cef', '.ceo', '.cdt.cef', '.cdt.ceo'])
    