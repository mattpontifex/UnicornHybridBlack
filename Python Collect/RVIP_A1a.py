from __future__ import division  # so that 1/3=0.333 instead of 1/3=0
from psychopy import visual, core, data, event, logging, gui
from psychopy.constants import *  # things like STARTED, FINISHED
import numpy
from numpy import sin, cos, tan, log, log10, pi, average, sqrt, std, deg2rad, rad2deg, linspace, asarray
#from numpy.random import random, randint, normal, shuffle
import os  # handy system and path functions
import warnings
warnings.simplefilter('ignore')
logging.console.setLevel(logging.CRITICAL)
from datetime import datetime
import pandas
import Engine.xcat as xcat

#Determine if triggers are sent
optTrigger = True 
if optTrigger:
    from psychopy import parallel
    # EEG: Establish parallel port
    try:
        parallel.setPortAddress('0xD010') #address for parallel port
        parallel.setData(0) #sets all pins low
    except:
        boler = 1
        
# EEG: Send Trigger Function
def sendtrigger(code):
    if optTrigger:
        try:
            parallel.setData(int('{0:08b}'.format(int(code)),2))
            core.wait(0.002) # 2 ms pulse duration
            parallel.setData(0) #sets all pins low
        except:
            boler = 1

class FolderStructure():
    def __init__(self, enginefolder='Engine', taskfolder='Gentask', stimulusfolder='Stimuli', sequencefolder='Sequence', outputfolder='Raw'):
        self.taskfolder = taskfolder
        self.stimulusfolder = stimulusfolder
        self.sequencefolder = sequencefolder
        self.outputfolder = outputfolder
        self.enginefolder = taskfolder + os.path.sep + enginefolder

def cdPerMToPyth(cdPerM,gammaToPhys,minPhys,maxPhys):   #Convert physical luminance to python value
    return pow(((cdPerM-minPhys)/(maxPhys-minPhys)),1./gammaToPhys)*2.-1.

class MonitorParameters():
    def __init__(self, displaynumber=0, resolution=(1920,1080), physicalsize=(33.8,27.1), backgroundcolor='#000000', forgroundcolor='#FFFFFF', distance=100, fullscreen=True, gui=False, stencil=False, colorspace='rgb', monitor='testMonitor'):
        self.displaynumber = displaynumber # 
        self.resolution = resolution # 
        self.physicalsize = physicalsize # physical screen size in centimeters
        self.backgroundcolor = backgroundcolor # RGB Codes (-1 to 1) or Hex Code
        self.forgroundcolor = forgroundcolor # RGB Codes (-1 to 1) or Hex Code
        self.distance = distance # Distance between participant and screen in centimeters
        self.fullscreen = fullscreen
        self.gui = gui # show gui
        self.stencil = stencil
        self.colorspace = colorspace
        self.monitor = monitor





participantmonitor = MonitorParameters()
experimentermonitor = MonitorParameters()
experimentermonitor.fullscreen = False
experimentermonitor.gui = False
cdpermMin=.25
cdpermMax=[19.65,61.72,5.97,83.5]
gammaPyToPhys=[2.33,2.14,2.57,2.14]
backgroundColorPhys = 20.0
participantmonitor.backgroundcolor=cdPerMToPyth(backgroundColorPhys,gammaPyToPhys[-1],cdpermMin,cdpermMax[-1])
experimentermonitor.backgroundcolor=cdPerMToPyth(backgroundColorPhys,gammaPyToPhys[-1],cdpermMin,cdpermMax[-1])
del cdpermMin, cdpermMax, gammaPyToPhys, backgroundColorPhys

# Modify Screen Settings for Participant
participantmonitor.displaynumber = 1 # Monitor Number
participantmonitor.resolution = (1920, 1080)
participantmonitor.physicalsize = (53,30) # physical screen size in centimeters
participantmonitor.distance = 41 # Distance between participant and screen in centimeters
participantmonitor.forgroundcolor = '#FFFFFF' # RGB Codes (-1 to 1) or Hex Code

# Modify Screen Settings for Experimenter
experimentermonitor.displaynumber = 0 # Monitor Number
experimentermonitor.resolution = (1200, 675)
experimentermonitor.fullscreen = False
experimentermonitor.gui = False # show gui
experimentermonitor.forgroundcolor = '#FFFFFF' # RGB Codes (-1 to 1) or Hex Code

# Output structure
folders = FolderStructure()
path = os.chdir(os.path.dirname(os.getcwd()))
prefix = 'CF'
suffix = 'R1a'
filename = 'test'
filenametooltip = 'Enter participant number and condition: ###X or ###Y'
testblock = False
instructioncard = ['RVIP_Instructions.png']
showinstructions = True
delaybeforestart = 5
pauseatstart = True
pauseatend = True
sequence = []
permanentframemask = []
participantkeys = ['1', '2', '3', '4']
experimenterkeys = ['space', 'enter', 'return', 'escape', 'a', 'r', 'q']
cumulativeTime = core.Clock()




# begin experiment



# Prompt for filename
if not testblock:
    dlg=gui.Dlg(title='Enter the Participant ID Number')
    dlg.addText('')
    if (filenametooltip == ''):
        dlg.addField('Participant ID:')
    else:
        dlg.addField('Participant ID:', tip=filenametooltip)
    if (prefix != '') and (suffix != ''):
        dlg.addText('')
        dlg.addText('The prefix %s and suffix %s will be added automatically.' % (prefix, suffix), color='Gray')
    elif (prefix != ''):
        dlg.addText('')
        dlg.addText('The prefix %s will be added automatically.' % (prefix), color='Gray')
    elif (suffix != ''):
        dlg.addText('')
        dlg.addText('The suffix %s will be added automatically.' % (suffix), color='Gray')
    dlg.addText('')
    dlg.show()
    if dlg.OK==False: core.quit() #user pressed cancel
    filename = '%s' %( dlg.data[0])
    #Determine if file already exists if so append '_1' to it
    while (os.path.isfile(folders.outputfolder + os.path.sep + prefix + filename + suffix + '.psydat')): 
        suffix = suffix + '_1'
    outputfile = folders.outputfolder + os.path.sep + prefix + filename + suffix  + '.psydat' # Save File As
    print ('Output data file: %s%s%s' % (prefix, filename, suffix))


## Establish monitors and windows
# Determine if the experimeter monitor was declared
if (participantmonitor.displaynumber == experimentermonitor.displaynumber):
    expdisp = False
else:
    expdisp = True
    
# Setup Display Window
participantwin = visual.Window(size = participantmonitor.resolution, fullscr = participantmonitor.fullscreen, screen = participantmonitor.displaynumber, allowGUI = participantmonitor.gui, allowStencil = participantmonitor.stencil, monitor = participantmonitor.monitor, color = participantmonitor.backgroundcolor, colorSpace = participantmonitor.colorspace)
if expdisp:
    experimenterwin = visual.Window(size = experimentermonitor.resolution, fullscr = experimentermonitor.fullscreen, screen = experimentermonitor.displaynumber, allowGUI = experimentermonitor.gui, allowStencil = experimentermonitor.stencil, monitor = experimentermonitor.monitor, color = experimentermonitor.backgroundcolor, colorSpace = experimentermonitor.colorspace)
                
# Setup notifications for experimenter
if expdisp:
    experimenternotificationtext = visual.TextStim(experimenterwin, text='...', height = 0.05, pos=[-0.95,-0.95], alignHoriz = 'left', alignVert='bottom', color=experimentermonitor.forgroundcolor, autoLog=False)
    experimenternotificationtext.setAutoDraw(True); experimenterwin.flip()
    
# Start Showing Windows
participantwin.flip()
if expdisp:
    experimenterwin.flip()


# Prep stimuli
participantstim_text = visual.TextStim(win=participantwin, ori=0, name='stim_text',
    text='nonsense',    font=u'Arial',
    pos=[0, 0], height=0.3, wrapWidth=None,
    color=participantmonitor.forgroundcolor, colorSpace=u'rgb', opacity=1,
    depth=0.0)
if expdisp:
    experimenterstim_text = visual.TextStim(win=experimenterwin, ori=0, name='stim_text',
        text='nonsense',    font=u'Arial',
        pos=[0, 0], height=0.3, wrapWidth=None,
        color=experimentermonitor.forgroundcolor, colorSpace=u'rgb', opacity=1,
        depth=0.0)

# turn off mouse
event.Mouse(visible=False)

# Determine Monitor Refresh Rate Under Load
stimulus = visual.PatchStim(participantwin, tex = 'sin', mask = 'gauss', size = 100, sf = 0.05, ori = 45, units = 'pix', autoLog = False) # Establish Gabor patch
routineTimer = core.CountdownTimer(2) # Sets to run for 2 seconds 
masterlatency = []
while routineTimer.getTime()>0:
    stimulus.setPhase(0.05,'+')
    stimulus.draw()
    participantwin.flip() 
    masterlatency.append(core.getTime())
frameTimes = numpy.diff(masterlatency)
temparray = []
for fcount in range(0,len(frameTimes)):
    temparray.append(float('%.9f' % (numpy.round(float(frameTimes[fcount]),decimals=9))))
temparray.sort() # Sort the latency values
temparray = temparray[int(len(temparray)*0.15):(int(len(temparray)*0.15)*-1)]
refreshrate = numpy.float('%.6f' % (numpy.round(numpy.median(temparray),decimals=6)))
del fcount, frameTimes, temparray, masterlatency

participantwin.flip()

# Show Task Instructions
for n in range(0,len(instructioncard)):
    if expdisp:
        if not pauseatstart:
            experimenternotificationtext.setText('task will begin when someone pushes a button...'); experimenterwin.flip()
        else:
            experimenternotificationtext.setText('push a button to continue...'); experimenterwin.flip()
    
    # Load image
    participantstimulus = visual.ImageStim(participantwin, image = os.path.join(folders.stimulusfolder, instructioncard[n]), autoLog=False)
    if expdisp:
        experimenterstimulus = visual.ImageStim(experimenterwin, image = os.path.join(folders.stimulusfolder, instructioncard[n]), interpolate=True, autoLog=False)
        experimenterstimulus.size = participantstimulus.size
    participantstimulus.setAutoDraw(True); participantwin.flip()
    if expdisp:
         experimenterstimulus.setAutoDraw(True); experimenterwin.flip()

    continueRoutine = True
    while continueRoutine:
        if event.getKeys(experimenterkeys): # Expermenter can always end it
            break
        if not pauseatstart: # Participant can only end it if originally specified
            if event.getKeys(participantkeys):
                continueRoutine = False
                break
            
    participantstimulus.setAutoDraw(False); participantwin.flip()
    if expdisp:
        experimenterstimulus.setAutoDraw(False); experimenterwin.flip()

stims = [9, 5, 7, 6, 3, 9, 7, 4, 6, 2, 4, 6, 3, 7, 5, 8, 5, 4, 5, 3, 5, 2, 3, 5, 7, 5, 3, 2, 5, 9, 8, 9, 3, 8, 3, 5, 2, 4, 6, 7, 5, 2, 6, 7, 6, 1, 9, 7, 4, 6, 8, 9, 7, 9, 5, 8, 1, 5, 2, 4, 6, 2, 3, 9, 8, 7, 9, 8, 2, 1, 2, 1, 8, 4, 6, 8, 7, 9, 8, 3, 5, 2, 5, 2, 1, 6, 9, 6, 7, 9, 5, 2, 9, 1, 2, 4, 6, 3, 2, 6, 4, 3, 5, 3, 5, 7, 4, 1, 2, 4, 2, 6, 3, 5, 7, 4, 5, 1, 2, 3, 1, 9, 4, 7, 9, 3, 5, 7, 8, 1, 9, 5, 2, 3, 5, 2, 8, 1, 4, 6, 8, 5, 2, 4, 5, 3, 4, 6, 8, 5, 3, 6, 7, 2, 6, 4, 6, 8, 2, 4, 2, 7, 6, 2, 4, 6, 2, 6, 7, 4, 8, 3, 8, 2, 5, 7, 2, 9, 4, 2, 4, 9, 4, 3, 5, 3, 5, 8, 3, 6, 3, 2, 8, 9, 1, 4, 6, 8, 5, 7, 4, 3, 2, 7, 2, 4, 6, 2, 9, 1, 7, 4, 5, 3, 4, 2, 3, 2, 3, 5, 7, 9, 6, 5, 2, 3, 1, 5, 4, 6, 8, 6, 3, 6, 9, 1, 7, 1, 3, 2, 1, 9, 3, 4, 6, 8, 5, 3, 5, 8, 5, 9, 2, 4, 6, 3, 4, 1, 7, 3, 4, 2, 6, 8, 9, 6, 8, 5, 3, 5, 7, 1, 7, 9, 5, 7, 5, 3, 5, 7, 4, 2, 5, 3, 6, 8, 5, 1, 6, 2, 4, 6, 4, 5, 9, 1, 9, 1, 2, 5, 1, 9, 7, 8, 2, 3, 5, 7, 8, 9, 6, 5, 4, 8, 4, 7, 5, 2, 3, 5, 7, 1, 8, 5, 4, 9, 4, 6, 4, 2, 8, 2, 4, 6, 1, 5, 9, 8, 4, 2, 4, 6, 2, 9, 6, 8, 9, 8, 3, 2, 1, 6, 9, 7, 4, 6, 8, 5, 3, 5, 9, 1, 8, 7, 3, 5, 7, 2, 7, 4, 2, 3, 7, 1, 7, 6, 2, 4, 6, 5, 9, 2, 9, 5, 7, 4, 6, 8, 3, 1, 5, 6, 8, 5, 3, 8, 4, 6, 8, 3, 2, 5]
response = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]
stimulusCode = [7, 7, 14, 7, 7, 7, 7, 7, 13, 12, 7, 20, 12, 7, 7, 7, 7, 7, 7, 7, 7, 11, 7, 7, 21, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 11, 7, 20, 12, 7, 7, 7, 7, 7, 7, 7, 7, 7, 13, 22, 7, 7, 7, 7, 7, 7, 7, 7, 7, 20, 12, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 13, 22, 7, 7, 7, 7, 7, 11, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 20, 12, 7, 7, 7, 7, 7, 11, 7, 21, 7, 7, 7, 7, 10, 7, 7, 7, 21, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 21, 7, 7, 7, 7, 7, 7, 7, 11, 7, 7, 7, 13, 22, 7, 7, 7, 10, 7, 7, 13, 22, 7, 7, 7, 7, 7, 7, 7, 13, 22, 7, 7, 10, 7, 7, 7, 7, 20, 12, 7, 7, 7, 7, 7, 7, 7, 7, 14, 7, 7, 7, 7, 7, 10, 7, 7, 7, 11, 7, 11, 7, 7, 7, 7, 7, 7, 7, 7, 13, 22, 7, 14, 7, 7, 7, 7, 7, 7, 20, 12, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 21, 7, 7, 7, 7, 7, 7, 7, 7, 13, 22, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 13, 22, 7, 7, 7, 11, 7, 7, 7, 7, 20, 12, 7, 7, 7, 7, 7, 7, 7, 15, 7, 7, 15, 7, 7, 7, 21, 7, 7, 7, 7, 14, 7, 7, 7, 21, 7, 7, 7, 7, 7, 15, 7, 7, 7, 7, 7, 20, 12, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 21, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 21, 7, 7, 7, 7, 7, 7, 13, 12, 7, 7, 7, 7, 20, 12, 7, 7, 7, 7, 7, 7, 20, 12, 7, 7, 15, 7, 7, 7, 7, 7, 7, 7, 7, 7, 13, 22, 7, 7, 7, 11, 7, 7, 7, 7, 7, 21, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 20, 12, 7, 7, 7, 7, 14, 7, 13, 22, 7, 7, 7, 7, 15, 7, 7, 7, 7, 13, 22, 7, 7, 7]
seperations = [numpy.nan] * len(stims)
cNtarg = 0
for cN in range(0,len(stims)):
    if (response[cN] == 1):
        seperations[cN] = cNtarg
        cNtarg = 0
    else:
        cNtarg = cNtarg + 1

# Establish spec array to track what happens
stimulustracking = []
for trial in range(0,len(stims)):
    stimulustracking.append(["%.6f" % (numpy.nan),"%.6f" % (numpy.nan)])
responsetracking = []

if expdisp:
    experimenternotificationtext.setText('starting task...'); experimenterwin.flip()

# Create Target Mask
participanttargetmask = visual.ImageStim(participantwin, image = os.path.join(folders.stimulusfolder, 'targetmask.png'), pos=(0.0, -0.5), autoLog=False)
participanttargetmask.setAutoDraw(True); participantwin.flip()

#Prepare response buttons
event.BuilderKeyResponse()
event.clearEvents()

core.wait(delaybeforestart)

# begin task
elapsedTime = core.Clock(); 
cumulativeTime.reset()
trial = 0
continueTrial = True
continueExperiment = True
while continueExperiment:
    
    if (trial >= len(stims)):
        continueExperiment = False
        break
    
    if event.getKeys(["escape", "q"]): # Check for kill keys
        continueExperiment = False
        break
    
    if not continueTrial:
        stimulustracking[trial-1][1] = "%.6f" % cumulativeTime.getTime()
        
    continueTrial = True
    # set the new stimulus
    participantstim_text.setText("%d" % stims[trial], log=False)
    participantstim_text.setAutoDraw(True)
    if expdisp:
        experimenternotificationtext.setText('Trial %d of %d.' % (trial, len(stims)))
        experimenterstim_text.setText("%d" % stims[trial], log=False)
        experimenterstim_text.setAutoDraw(True)

    elapsedTime.reset()
    participantwin.flip(); sendtrigger(stimulusCode[trial]) # Send trigger
    stimulustracking[trial][0] = "%.6f" % cumulativeTime.getTime()
        
    if expdisp:
         experimenterwin.flip()

    while continueTrial:
        if (float(numpy.sum([elapsedTime.getTime(),refreshrate])) < float(0.6)): # If stimulus duration has not expired
    
            # To avoid tying RT to the monitor refresh rate, this loops for most of the refresh rate period
            checkkeytimer = core.CountdownTimer(start=(float(numpy.multiply(float(0.8),float(refreshrate)))))
            while (checkkeytimer.getTime() > 0):
                
                theseKeys = event.getKeys(keyList=participantkeys, timeStamped=cumulativeTime)
                if (len(theseKeys) > 0): #at least one key was pressed
                    responsetracking.append(theseKeys[0])
                    sendtrigger(theseKeys[0][0])
                        
                if event.getKeys(["escape", "q"]): # Check for kill keys
                    continueExperiment = False
                    break
        else:
            continueTrial = False
            trial = trial + 1
            
    event.clearEvents()

if not continueExperiment:
    participanttargetmask.setAutoDraw(False)
    participantstim_text.setAutoDraw(False); participantwin.flip()
    stimulustracking[trial-1][1] = "%.6f" % cumulativeTime.getTime()
    if expdisp:
        experimenterstim_text.setAutoDraw(False); experimenterwin.flip()

# Load data into matrix
eventmatrix  = pandas.DataFrame(columns = ['Trial', 'Event', 'Onset', 'Duration', 'Type', 'Stimulus', 'Seperation', 'Response', 'Latency', 'Accuracy'])
for trial in range(0,len(stims)):
    if not numpy.isnan(numpy.float32(stimulustracking[trial][0])):
        i = len(eventmatrix)
        eventmatrix.at[i, 'Trial'] = trial
        eventmatrix.at[i, 'Event'] = 'Stimulus'
        eventmatrix.at[i, 'Onset'] = numpy.float32(stimulustracking[trial][0])
        eventmatrix.at[i, 'Duration'] = numpy.subtract(numpy.float32(stimulustracking[trial][1]),numpy.float32(stimulustracking[trial][0]))
        eventmatrix.at[i, 'Type'] = int(stimulusCode[trial])
        eventmatrix.at[i, 'Stimulus'] = stims[trial]
        eventmatrix.at[i, 'Seperation'] = seperations[trial]
        try:
            adjustment = numpy.subtract(numpy.float32(stimulustracking[trial+1][0]),numpy.float32(stimulustracking[trial][0]))
            if not numpy.isnan(adjustment):
                eventmatrix.at[i, 'Duration'] = adjustment
        except:
            bolerr = 0
respmatrix  = pandas.DataFrame(columns = ['Event', 'Onset', 'Type'])
for trial in range(0,len(responsetracking)):
    respmatrix.at[trial,'Event'] = 'Response'
    respmatrix.at[trial,'Onset'] = numpy.float32(responsetracking[trial][1])
    respmatrix.at[trial,'Type'] = int(responsetracking[trial][0])
eventmatrix = eventmatrix.append(respmatrix)
eventmatrix = eventmatrix.sort('Onset')
eventmatrix = eventmatrix.reset_index(drop=True)

MinRespWin = 0.1
MaxRespWin = 1.5
# First identify targets
for i in range(0,len(eventmatrix)):
    if not numpy.isnan(eventmatrix.at[i, 'Seperation']):
        onsetmin = numpy.sum([eventmatrix.at[i, 'Onset'],numpy.float32(MinRespWin)])
        onsetmax = numpy.sum([eventmatrix.at[i, 'Onset'],numpy.float32(MaxRespWin)])
        for k in range(i+1,len(eventmatrix)):
            if (numpy.float32(eventmatrix.at[k, 'Onset']) <= numpy.float32(onsetmax)):
                if (numpy.float32(eventmatrix.at[k, 'Onset']) >= numpy.float32(onsetmin)):
                    if numpy.isnan(eventmatrix.at[k, 'Duration']):
                        if numpy.isnan(eventmatrix.at[k, 'Latency']):
                            eventmatrix.at[i, 'Latency'] = numpy.subtract(eventmatrix.at[k, 'Onset'],eventmatrix.at[i, 'Onset'])
                            eventmatrix.at[i, 'Response'] = eventmatrix.at[k, 'Type']
                            eventmatrix.at[k, 'Trial'] = eventmatrix.at[i, 'Trial']
                            eventmatrix.at[k, 'Latency'] = numpy.subtract(eventmatrix.at[k, 'Onset'],eventmatrix.at[i, 'Onset'])
                            break
            else:
                break
# Next identify lures
for i in range(0,len(eventmatrix)):
    if int(eventmatrix.at[i, 'Type']) > int(7):
        onsetmin = numpy.sum([eventmatrix.at[i, 'Onset'],numpy.float32(MinRespWin)])
        onsetmax = numpy.sum([eventmatrix.at[i, 'Onset'],numpy.float32(MaxRespWin)])
        for k in range(i+1,len(eventmatrix)):
            if (numpy.float32(eventmatrix.at[k, 'Onset']) <= numpy.float32(onsetmax)):
                if (numpy.float32(eventmatrix.at[k, 'Onset']) >= numpy.float32(onsetmin)):
                    if numpy.isnan(eventmatrix.at[k, 'Duration']):
                        if numpy.isnan(eventmatrix.at[k, 'Latency']):
                            eventmatrix.at[i, 'Latency'] = numpy.subtract(eventmatrix.at[k, 'Onset'],eventmatrix.at[i, 'Onset'])
                            eventmatrix.at[i, 'Response'] = eventmatrix.at[k, 'Type']
                            eventmatrix.at[k, 'Trial'] = eventmatrix.at[i, 'Trial']
                            eventmatrix.at[k, 'Latency'] = numpy.subtract(eventmatrix.at[k, 'Onset'],eventmatrix.at[i, 'Onset'])
                            break  
            else:
                break
# Identify randoms
for i in range(0,len(eventmatrix)):
    if eventmatrix.at[i, 'Event'] == 'Response':
        if numpy.isnan(eventmatrix.at[i, 'Latency']):
            onsetmin = numpy.subtract(eventmatrix.at[i, 'Onset'],numpy.float32(MaxRespWin))
            onsetmax = numpy.subtract(eventmatrix.at[i, 'Onset'],numpy.float32(MinRespWin))
            for k in range(i-1,0,-1):
                if (numpy.float32(eventmatrix.at[k, 'Onset']) >= numpy.float32(onsetmin)):
                    if (numpy.float32(eventmatrix.at[k, 'Onset']) <= numpy.float32(onsetmax)):
                        if numpy.isnan(eventmatrix.at[k, 'Response']):
                            if numpy.isnan(eventmatrix.at[k, 'Latency']):
                                eventmatrix.at[k, 'Latency'] = numpy.subtract(eventmatrix.at[i, 'Onset'],eventmatrix.at[k, 'Onset'])
                                eventmatrix.at[k, 'Response'] = eventmatrix.at[i, 'Type']
                                eventmatrix.at[i, 'Trial'] = eventmatrix.at[k, 'Trial']
                                eventmatrix.at[i, 'Latency'] = numpy.subtract(eventmatrix.at[i, 'Onset'],eventmatrix.at[k, 'Onset'])
                                break
                else:
                    break
                
# Code Accuracy
for i in range(0,len(eventmatrix)):    
    if eventmatrix.at[i, 'Event'] == 'Stimulus':   
        if not numpy.isnan(eventmatrix.at[i, 'Response']): 
            if (int(eventmatrix.at[i, 'Type']) >= int(20)):
                if (int(eventmatrix.at[i, 'Response']) == int(4)):
                    eventmatrix.at[i, 'Accuracy'] = 1
                else:
                    eventmatrix.at[i, 'Accuracy'] = 0
            else:
                eventmatrix.at[i, 'Accuracy'] = 0
        else:
            if (int(eventmatrix.at[i, 'Type']) >= int(20)):
                eventmatrix.at[i, 'Accuracy'] = 0
            else:
                eventmatrix.at[i, 'Accuracy'] = 1
    eventmatrix.at[i, 'Duration'] = numpy.round(eventmatrix.at[i, 'Duration']*1000,3)
    eventmatrix.at[i, 'Latency'] = numpy.round(eventmatrix.at[i, 'Latency']*1000,3)
    
            
# put data in a meaningful format
f = open(outputfile, 'w')
timestamp = str(datetime.now()).split()
f.write('gentask.....= PsychoPy_Engine_3')
f.write('\n')
f.write('date........= ')
f.write(timestamp[0])
f.write('\n')
f.write('time........= ')
f.write(timestamp[1])
f.write('\n')
f.write('refreshrate.= ')
f.write('%.3f' % (refreshrate*1000))
f.write(' ms')
f.write('\n')

f.write(('Trial').rjust(7))
f.write(('Event').rjust(16))
f.write(('Duration').rjust(16))
f.write(('ISI').rjust(16))
f.write(('ITI').rjust(16))
f.write(('Type').rjust(16))
f.write(('Resp').rjust(16))
f.write(('Correct').rjust(16))
f.write(('Latency').rjust(16))
f.write(('ClockLatency').rjust(16))
f.write(('Trigger').rjust(16))
f.write(('MinRespWin').rjust(16))
f.write(('MaxRespWin').rjust(16))
f.write(('Stimulus').rjust(16))
f.write('\n')

f.write(('---').rjust(7))
for n in range(1,13):
    f.write(('---').rjust(16))
f.write(('---').rjust(11))
f.write('\n')
for i in range(0,len(eventmatrix)):
    f.write(str(eventmatrix.at[i, 'Trial']).rjust(7)) # Trial
    f.write(str(eventmatrix.at[i, 'Event']).rjust(16)) # Event
    f.write(str(eventmatrix.at[i, 'Duration']).rjust(16)) # Duration
    f.write(str('nan').rjust(16)) # ISI
    f.write(str(eventmatrix.at[i, 'Seperation']).rjust(16)) # ITI
    f.write(str(eventmatrix.at[i, 'Type']).rjust(16)) # Type
    f.write(str(eventmatrix.at[i, 'Response']).rjust(16)) # Resp
    f.write(str(eventmatrix.at[i, 'Accuracy']).rjust(16)) # Correct
    f.write(str(eventmatrix.at[i, 'Latency']).rjust(16)) # Latency
    f.write(str(eventmatrix.at[i, 'Onset']).rjust(16)) # ClockLatency
    f.write(str('1').rjust(16)) # Trigger
    f.write(str(MinRespWin).rjust(16)) # MinRespWindow
    f.write(str(MaxRespWin).rjust(16)) # MaxRespWindow
    f.write('        ')
    f.write(str(eventmatrix.at[i, 'Stimulus']).ljust(16)) # Stimulus
    f.write('\n')
f.close()



core.wait(1.0)  #1 sec break before end message
visual.TextStim(participantwin, text='End of the testing block.' , pos=(0.0,0.2)).draw()
visual.TextStim(participantwin, text='Thank you.' , pos=(0.0,-0.2)).draw()
participantwin.flip()

if expdisp:
    visual.TextStim(experimenterwin, text='End of the testing block.' , pos=(0.0,0.2)).draw()
    visual.TextStim(experimenterwin, text='Thank you.' , pos=(0.0,-0.2)).draw()
    experimenternotificationtext.setText('push a button to continue...'); experimenterwin.flip()

End = True
while End:
    for key in event.getKeys():
        End = False
del key, End
        
participantwin.close()
if expdisp:
    experimenterwin.close()
    
# Check Performance Settings using xcat
taskoutput = xcat.BehavioralAnalysis()
taskoutput.run(inputfile = outputfile, trialtypes = [20, 21, 22])
taskoutput.show(label = 'Targets', header = True)
taskoutput.run(inputfile = outputfile, trialtypes = [10, 11, 12])
taskoutput.show(label = 'Anticipate')
taskoutput.run(inputfile = outputfile, trialtypes = [13, 14, 15])
taskoutput.show(label = 'Memoryfail')
taskoutput.run(inputfile = outputfile, trialtypes = [7])
taskoutput.show(label = 'Nontarget')

os.remove(os.path.realpath(__file__)[0:-2] + 'pyc') # Remove compiled python file

    
    
core.quit()
