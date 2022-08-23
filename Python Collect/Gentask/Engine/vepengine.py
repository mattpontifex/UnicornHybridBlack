"""
Version 1
Authored by Matthew Pontifex

#https://webvision.med.utah.edu/book/electrophysiology/visually-evoked-potentials/
The major component of the VEP is the large positive wave peaking at about 100 milliseconds (Fig. 5).
This “P100” or P1 in the jargon of evoked potentials, is very reliable between individuals and 
stable from about age 5 years to 60 years.

"""

# vepengine: classes to run a vep experiment in psychopy
#

import os #handy system and path functions
import time
from datetime import datetime
import csv
import numpy

from psychopy import prefs
from psychopy import visual, core, event, gui
try:
    try:
        import unicornhybridblack as unicornhybridblack
    except:
        import Engine.unicornhybridblack as unicornhybridblack
    unicornmodule = True
except:
    unicornmodule = False

try:
    from psychopy import parallel
    paralleltriggermodule = True
except:
    paralleltriggermodule = False
try:
    prefs.general['audioLib'] = ['pygame']
    from psychopy import sound
    soundmodule = True
except:
    soundmodule = False

import warnings
warnings.simplefilter('ignore')
from psychopy import logging
logging.console.setLevel(logging.CRITICAL)




class MonitorParameters():
    
    def __init__(self, displaynumber=0, resolution=(1920,1080), physicalsize=(33.8,27.1), backgroundcolor='#787878', forgroundcolor='#FFFFFF', distance=100, fullscreen=True, gui=False, stencil=False, colorspace='rgb', monitor='testMonitor'):
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

class FolderStructure():
    
    def __init__(self, enginefolder='Engine', taskfolder='Gentask', stimulusfolder='Stimuli', sequencefolder='Sequence', outputfolder='Raw'):
        self.taskfolder = taskfolder
        self.stimulusfolder = stimulusfolder
        self.sequencefolder = sequencefolder
        self.outputfolder = outputfolder
        self.enginefolder = taskfolder + os.path.sep + enginefolder
        
class Engine():
    
    def __init__(self):
        
        self.debug = False
        self.quit = False
        self.folders = FolderStructure()
        self.participantmonitor = MonitorParameters()
        self.experimentermonitor = MonitorParameters()
        self.experimentermonitor.fullscreen = False; self.experimentermonitor.gui = False
        self.expdisp = False
        self.path = os.chdir(os.path.dirname(os.getcwd()))
        self.prefix = ''
        self.suffix = ''
        self.filename = 'test'
        self.filenametooltip = ''
        self.promptforfilename = True
        self.outputfile = self.folders.outputfolder + os.path.sep + self.prefix + self.filename + self.suffix  + '.psydat' # Save File As
        
        self.instructioncard = ['Instructions.png']
        self.showinstructions = True
        self.delaybeforestart = 5
        self.pauseatstart = True
        self.pauseatend = True
        self.waitcard = []
        self.sequence = []
        self.permanentframemask = []
        self.participantkeys = ['1', '2', '3', '4']
        self.experimenterkeys = ['space', 'enter', 'return', 'escape', 'a', 'r', 'q']
        
        self.triggers = True
        self.paralleltriggermodule = paralleltriggermodule
        self.soundmodule = soundmodule
        self.triggerpulseduration = 0.002
        self.markfirstresponseonly = True
        self.triggerportaddress = '0x2040'#address for parallel port on many machines
        self.unicorn = []
        self.unicornchannels = 'FZ, C3, CZ, C4, PZ, O1, OZ, O2, AccelX, AccelY, AccelZ, GyroX, GyroY, GyroZ, Battery, Sample'
        self.testblock = False
        
        self.mri = False
        self.mritriggerinputs = ['^', 'caret', '/', 'slash', 'escape', 'return', 'space']
        self.mriwaitforsyncpulse = False # Wait for a sync pulse to occur before the start of each trial
        
        self.activedisplaylog = False
        self.activedisplayspeed = 5
        self.activedisplaymarks = [0] * 20
        self.multiple = 1
        
        self.useiohub = False
        self.refreshrate = 0.0167
        self.followsequencefile = True
        self.sequencelistL = 0
        self.framemasktoggle = False
        self.sequenceready = False
        self.collectgarbage = False
        self.cumulativeTime = core.Clock()
        self.initializetime = core.getTime()
        self.previoustrialforexperimentermarker = [0,0,0,0]
        self.printoutput = False
        self.totaltrials = 20
        
        self.participantwinActive = False
        

        
    def start(self):

        if self.debug:
            self.printoutput = True
        
        self.sequencelistL = self.totaltrials + 1
        
        ##### Prompt for filename or use default ##### 
        if not self.testblock:
            dlg=gui.Dlg(title='Enter the Participant ID Number')
            dlg.addText('')
            if (self.filenametooltip == ''):
                dlg.addField('Participant ID:')
            else:
                dlg.addField('Participant ID:', tip=self.filenametooltip)
            if (self.prefix != '') and (self.suffix != ''):
                dlg.addText('')
                dlg.addText('The prefix %s and suffix %s will be added automatically.' % (self.prefix, self.suffix), color='Gray')
            elif (self.prefix != ''):
                dlg.addText('')
                dlg.addText('The prefix %s will be added automatically.' % (self.prefix), color='Gray')
            elif (self.suffix != ''):
                dlg.addText('')
                dlg.addText('The suffix %s will be added automatically.' % (self.suffix), color='Gray')
            dlg.addText('')
            dlg.show()
            if dlg.OK==False: self.quit = True #user pressed cancel
            self.filename = '%s' %( dlg.data[0])
            #Determine if file already exists if so append '_1' to it
            while (os.path.isfile(self.folders.outputfolder + os.path.sep + self.prefix + self.filename + self.suffix + '.psydat')): 
                self.suffix = self.suffix + '_1'
        
        self.outputfile = self.folders.outputfolder + os.path.sep + self.prefix + self.filename + self.suffix  + '.psydat' # Save File As
        print ('Output data file: %s%s%s' % (self.prefix, self.filename, self.suffix))
    
        if (len(self.unicorn) > 0):
            if not unicornmodule:
                print('ERROR: The unicornhybridblack module was unable to be loaded.')
                self.quit = True
                
                
        
        #####  Start Windows ##### 
        if not self.quit:
            if (self.participantmonitor.displaynumber == self.experimentermonitor.displaynumber):  # Determine if the experimeter monitor was declared
                self.expdisp = False
                self.activedisplaylog = False
            else:
                self.expdisp = True
                
            # Setup Display Window
            self.participantwin = visual.Window(size = self.participantmonitor.resolution, fullscr = self.participantmonitor.fullscreen, screen = self.participantmonitor.displaynumber, allowGUI = self.participantmonitor.gui, allowStencil = self.participantmonitor.stencil, monitor = self.participantmonitor.monitor, color = self.participantmonitor.backgroundcolor, colorSpace = self.participantmonitor.colorspace)
            self.participantwinActive = True
            if self.expdisp:
                self.experimenterwin = visual.Window(size = self.experimentermonitor.resolution, fullscr = self.experimentermonitor.fullscreen, screen = self.experimentermonitor.displaynumber, allowGUI = self.experimentermonitor.gui, allowStencil = self.experimentermonitor.stencil, monitor = self.experimentermonitor.monitor, color = self.experimentermonitor.backgroundcolor, colorSpace = self.experimentermonitor.colorspace)
                            
            # Setup notifications for experimenter
            if self.expdisp:
                self.experimenternotificationtext = visual.TextStim(self.experimenterwin, text='...', height = 0.05, pos=[-0.95,-0.95], alignHoriz = 'left', alignVert='bottom', color=self.experimentermonitor.forgroundcolor, autoLog=False)
                self.experimenternotificationtext.setAutoDraw(True); self.experimenterwin.flip()
            
            
            
            
        
            ##### Parameter update ##### 
            if (len(self.unicorn) > 0):
                
                if self.expdisp:
                    self.experimenternotificationtext.setText('initializing unicorn system...'); self.experimenterwin.flip()
                    
                try:
                    # connect to Device
                    self.UnicornBlack = unicornhybridblack.UnicornBlackProcess()
                    self.UnicornBlack.channellabels = self.unicornchannels
                    self.UnicornBlack.printoutput = self.printoutput
                    self.UnicornBlack.connect(deviceID=self.unicorn, rollingspan=2.0, logfilename=self.folders.outputfolder + os.path.sep + self.prefix + self.filename + self.suffix)
                    
                    # wait 3 seconds for connection
                    continueExperiment = False
                    checktimer = core.CountdownTimer(start=3.0)
                    while (checktimer.getTime() > 0):
                        if self.UnicornBlack.ready:
                            continueExperiment = True
                    if not continueExperiment:
                        self.quit = True
                    else:
                        powerlevel = self.UnicornBlack.check_battery()
                        if (powerlevel < 1):
                            print('ERROR: The device is out of battery.')
                            self.quit = True
                    
                    self.UnicornBlack.startrecording() 
                    
                    
                except:
                    print('ERROR: An error occurred while attempting to connect to the Unicorn device.')
                    self.quit = True
            
            
                if self.expdisp:
                    self.experimenternotificationtext.setText('unicorn recording...'); self.experimenterwin.flip()
                    
                    
                    
                
            # Start Showing Windows
            self.participantwin.flip()
            if self.expdisp:
                self.experimenterwin.flip()
        
        
        
        
        
        
            #####  Test Monitor #####  
            if self.expdisp: # Setup notifications for experimenter
                self.experimenternotificationtext.setText('verifying monitor refresh rate...'); self.experimenterwin.flip()
            
            # Setup stimulus
            stimulus = visual.PatchStim(self.participantwin, tex = 'sin', mask = 'gauss', size = 100, sf = 0.05, ori = 30, units = 'pix', autoLog = False) # Establish Gabor patch
            
            # Setup Clock
            routineTimer = core.CountdownTimer(2) # Sets to run for 2 seconds
            masterlatency = []
            while routineTimer.getTime()>0:
                if event.getKeys(["escape"]):
                    self.quit = True
                    break
                stimulus.setPhase(0.05,'+'); stimulus.draw();
                self.participantwin.flip()
                masterlatency.append(core.getTime())
            frameTimes = numpy.diff(masterlatency)
            
            # Load latency values into array
            temparray = []
            for fcount in range(0,len(frameTimes)):
                temparray.append(float('%.9f' % (numpy.round(float(frameTimes[fcount]),decimals=9))))
            temparray.sort() # Sort the latency values
            temparray = temparray[int(len(temparray)*0.15):(int(len(temparray)*0.15)*-1)]
            self.refreshrate = numpy.float('%.6f' % (numpy.round(numpy.median(temparray),decimals=6)))
            
            if self.expdisp:
                self.experimenternotificationtext.setText('monitor refresh rate: %s ms.'% (self.refreshrate*1000))
                
            self.participantwin.flip()
            if self.expdisp:
                self.experimenterwin.flip()
                
            if self.debug:
                print('Debug note: Under a light processing load, the Participant monitor-Video Card combiniation appears to be operating at %.0f Hz (%.1f ms per frame).' % (numpy.divide(1,self.refreshrate), numpy.multiply(self.refreshrate,1000)))
           
            self.testparallelport() # Determine if it is possible to send triggers through the parallel port
            if self.debug:
                if (self.paralleltriggermodule):
                    print('Debug note: The parallel port is available.')
                else:
                    print('Debug note: The parallel port is unavailable.')

            event.BuilderKeyResponse()
            event.clearEvents()   
            
            
            #####  Display Instructions #####
            if not self.quit:
                
                if self.showinstructions:
                            
                    if self.expdisp:
                        if not self.pauseatstart:
                            self.experimenternotificationtext.setText('task will begin when someone pushes a button...'); self.experimenterwin.flip()
                        else:
                            self.experimenternotificationtext.setText('push a button to continue...'); self.experimenterwin.flip()
                    
                    participantstimulus = visual.TextStim(self.participantwin, text='Keep your eyes focused on the red dot.', pos=(0.5,0.15), color='#FFFFFF', height=0.06, antialias=True, bold=True, italic=False, autoLog=None)   
                    
                    fixationsize = 16                            
                    participanttargetstimuli = visual.Circle(self.participantwin, radius=[0.1, 0.1], pos = [0,-0.005], fillColor='#FF0000', lineColor='#FF0000', autoLog=False)
                    stimradiusInitial = (fixationsize*(1.0/self.participantmonitor.resolution[0]), fixationsize*(0.9/self.participantmonitor.resolution[1]))
                    participanttargetstimuli.setRadius(stimradiusInitial) 
                    if self.expdisp:
                        experimenterstimulus = visual.TextStim(self.experimenterwin, text='Keep your eyes focused on the red dot.', pos=(0.5,0.15), color='#FFFFFF', height=0.06, antialias=True, bold=True, italic=False, autoLog=None) 
                        experimenterstimulus.size = participantstimulus.size
                        experimentertargetstimuli = visual.Circle(self.experimenterwin, radius=[0.1, 0.1], pos = [0,-0.005], fillColor='#FF0000', lineColor='#FF0000', autoLog=False)
                        experimentertargetstimuli.size = participanttargetstimuli.size
                    
                    participantstimulus.setAutoDraw(True); participanttargetstimuli.setAutoDraw(True); self.participantwin.flip()
                    if self.expdisp:
                        experimenterstimulus.setAutoDraw(True); experimentertargetstimuli.setAutoDraw(True) ; self.experimenterwin.flip()  
            
                        
                    # Preload stimuli
                    continueRoutine = True
                    try:
                        if not self.sequenceready:
                            
                            participantboard = visual.ImageStim(self.participantwin, image=os.path.join(self.folders.stimulusfolder, 'CheckersUnfiltered.png'), interpolate=False, flipHoriz=False, flipVert=False, autoLog=None)
                            participantboard.size = participantboard.size * 5.4
                            participantboard2 = visual.ImageStim(self.participantwin, image=os.path.join(self.folders.stimulusfolder, 'CheckersUnfilteredReverse.png'), interpolate=False, flipHoriz=False, flipVert=False, autoLog=None)
                            participantboard2.size = participantboard2.size * 5.4
                            if self.expdisp:
                                experimenterboard = visual.ImageStim(self.experimenterwin, image=os.path.join(self.folders.stimulusfolder, 'CheckersUnfiltered.png'), interpolate=False, flipHoriz=False, flipVert=False, autoLog=None)
                                experimenterboard2 = visual.ImageStim(self.experimenterwin, image=os.path.join(self.folders.stimulusfolder, 'CheckersUnfilteredReverse.png'), interpolate=False, flipHoriz=False, flipVert=False, autoLog=None)
                                experimenterboard.size = participantboard.size
                                experimenterboard2.size = participantboard2.size
                            
                            self.sequenceready = True
                    except:
                        print('ERROR: An error occurred while loading the sequence information or preloading the stimuli.')
                        continueRoutine = False
                        self.quit = True
                                
                    while continueRoutine:
                        if event.getKeys(self.experimenterkeys): # Expermenter can always end it
                            break
                        
                        if not self.pauseatstart: # Participant can only end it if originally specified
                            if event.getKeys(self.participantkeys):
                                continueRoutine = False
                                break
                            
                    participantstimulus.setAutoDraw(False); participanttargetstimuli.setAutoDraw(False); self.participantwin.flip()
                    if self.expdisp:
                        experimenterstimulus.setAutoDraw(False); experimentertargetstimuli.setAutoDraw(False) ; self.experimenterwin.flip()  
            
            
            
            
            #####  Prepare for task initiation #####
            if not self.quit:
                if not self.sequenceready:
                    print('ERROR: An error occurred while loading the sequence information or preloading the stimuli.')
                    self.quit = True

                # Establish tracking
                # Establish spec array to track what the engine actually did
                self.specarray = []
                speclist = ['Trial', 'Duration', 'ISI', 'ITI', 'Type', 'Resp', 'Correct', 'Latency', 'CumulativeLatency', 'Event', 'Trigger', 'MinRespWin', 'MaxRespWin', 'Stimulus', 'stimOn', 'stimOff', 'clockreset']
                self.specarray.append(speclist)
                for self.trial in range(1,self.sequencelistL):
                    self.specarray.append([("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan))])
                        
                self.stimcorrectcount = 0
                self.countcorrectresponseexpected = 0
                self.countresponseexpected = 0
                
                # Establish response array
                self.resparray = []
                for self.trial in range(0,self.sequencelistL):
                    self.resparray.append([])
        
                # Establish feedback array
                self.feedbackarray = []
                for self.trial in range(0,self.sequencelistL):
                    self.feedbackarray.append([int(0),[],[],[],[],[]])
                
                # Establish feedback response array
                self.feedbackresparray = []
                for self.trial in range(0,self.sequencelistL):
                    self.feedbackresparray.append([])
                
                # Establish response button trackers for experimenter
                if self.expdisp:
                    if self.activedisplaylog:
                        ticklist = [-0.95, -0.475, 0.0, 0.475, 0.95]
                        self.experimenterbuttonticks = [visual.TextStim(self.experimenterwin, text='|', height = 0.03, pos=[n,0.93], alignHoriz = 'left', alignVert='top', color=self.experimentermonitor.forgroundcolor, autoLog=False) for n in ticklist]
                        for n in range(0,len(ticklist)):
                            self.experimenterbuttonticks[n].setAutoDraw(True)
                        self.experimentertrackers = [visual.TextStim(self.experimenterwin, text='stim', height = 0.05, pos=[0,0.9], alignHoriz = 'left', alignVert='top', color=self.experimentermonitor.forgroundcolor, autoLog=False) for n in range(0,20)]
                
                # Establish global clock and if necessary wait for a synchronization pulse
                self.cumulativeTime.reset() # Reset the global clock
                self.initializetime = core.getTime()
                if self.mri:
                    if self.waitcard:
                        # Setup Display Window
                        participantstimulus = visual.ImageStim(self.participantwin, image = os.path.join(self.folders.stimulusfolder, self.waitcard), interpolate=True, autoLog=False)
                        if self.expdisp:
                            experimenterstimulus = visual.ImageStim(self.experimenterwin, image = os.path.join(self.folders.stimulusfolder, self.waitcard), interpolate=True, autoLog=False)
                            experimenterstimulus.size = participantstimulus.size
        
                        if self.expdisp:
                            self.experimenternotificationtext.setText('waiting for synchronization pulse...'); self.experimenterwin.flip()
                        
                        # Start Showing Image
                        participantstimulus.setAutoDraw(True); self.participantwin.flip()
                        if self.expdisp:
                            experimenterstimulus.setAutoDraw(True); self.experimenterwin.flip()
                        
                        continueRoutine = True
                        while continueRoutine:
                            if event.getKeys(self.experimenterkeys): # Expermenter can always end it
                                break
                            if event.getKeys(self.mritriggerinputs): # If a sync pulse was received
                                break
                        
                        self.cumulativeTime.reset() # Reset the global clock
                        self.initializetime = core.getTime()
                        
                        # Cleanup display windows
                        participantstimulus.setAutoDraw(False); self.participantwin.flip()
                        if self.expdisp:
                            experimenterstimulus.setAutoDraw(False); self.experimenterwin.flip()
                            
                # Determine if a mask needs to be applied to the screen
                if self.permanentframemask: 
                    self.participantframemask = visual.ImageStim(self.participantwin, image = os.path.join(self.folders.stimulusfolder, self.permanentframemask), interpolate=True, autoLog=False)
                    if self.expdisp:
                        self.experimenterframemask = visual.ImageStim(self.experimenterwin, image = os.path.join(self.folders.stimulusfolder, self.permanentframemask), interpolate=True, autoLog=False)
                        self.experimenterframemask.size = self.participantframemask.size
                    self.participantframemask.setAutoDraw(True); self.participantwin.flip()
                    if self.expdisp:
                        self.experimenterframemask.setAutoDraw(True); self.experimenterwin.flip()
                            
                # Delay before start of trials
                if self.expdisp:
                    self.experimenternotificationtext.setText('starting...'); self.experimenterwin.flip()
                
                
                # turn on fixation
                participanttargetstimuli.setAutoDraw(True) 
                if self.expdisp:
                    experimentertargetstimuli.setAutoDraw(True) 
                self.participantwin.flip()
                if self.expdisp:
                    self.experimenterwin.flip()
                
                # Prep process
                #self.participantwin.flip(); self.sendtrigger(0) # Send trigger
                #self.participantwin.flip(); self.sendtrigger(0) # Send trigger
                #self.participantwin.flip(); self.sendtrigger(0) # Send trigger
                
                time.sleep(self.delaybeforestart)
                
                #####  Task Begins #####              
        
                self.elapsedTime = core.Clock(); self.elapsedTime.reset()    
                event.clearEvents()

                invert = True
                                    
                # Progress through sequence of trials
                if (self.sequencelistL > 0):
                    for self.trial in range(1,self.sequencelistL):
                        if not self.quit:
                            
                            # Check to see if anyone is trying to quit
                            
                            self.continuetrial = True
                            if event.getKeys(["escape", "q"]):
                                self.quit = True
                                self.continuetrial = False
                                break
                                
                            # Check to see if the task is being paused
                            if event.getKeys(["p"]):
                                listofkeys = "{0}".format(", ".join(str(i) for i in self.experimenterkeys))
                                if self.expdisp:
                                    self.experimenternotificationtext.setText('Task Paused. \nPress any of these keys to continue: %s' % (listofkeys)); self.experimenterwin.flip()
                                
                                continueRoutine = True
                                while continueRoutine:
                                    if event.getKeys(self.experimenterkeys): # Expermenter can always end it
                                        break
                                if self.expdisp:
                                    self.experimenternotificationtext.setText('Task Resuming.'); self.experimenterwin.flip()
                                time.sleep(self.delaybeforestart)
                                
                            # determine which board to show
                            if invert:
                                participantboard2.draw()
                                if self.expdisp:
                                    experimenterboard2.draw()
                                invert = False
                                eventcode = 9
                                self.specarray[self.trial][13] = 'CheckersUnfilteredReverse.png'
                            else:
                                participantboard.draw()
                                if self.expdisp:
                                    experimenterboard.draw()
                                invert = True
                                eventcode = 8
                                self.specarray[self.trial][13] = 'CheckersUnfiltered.png'
                                
                                
                            # Load information for the current trial
                            self.specarray[self.trial][0] = self.trial # Trial
                            self.specarray[self.trial][2] = ("%.3f" % (float(0.0))) # ISI
                            self.specarray[self.trial][4] = eventcode # Type
                            self.specarray[self.trial][6] = 1 # Correct
                            self.specarray[self.trial][9] = 'Stimulus' # Event
                            if self.triggers:
                                self.specarray[self.trial][10] = 1
                            else:
                                self.specarray[self.trial][10] = 0
                            if (self.trial > 1):
                                self.specarray[self.trial-1][15] = self.elapsedTime.getTime() # StimOff
                                
                                
                            self.UnicornBlack.safe_to_log(False)   
                            self.participantwin.flip() 
                            self.sendtrigger(eventcode) # Send trigger   
                            self.specarray[self.trial][14] = self.elapsedTime.getTime() # StimOn
                            self.specarray[self.trial][8] = ("%.6f" % (numpy.round(self.cumulativeTime.getTime(),6))) # CumulativeStim
                        
                            self.UnicornBlack.safe_to_log(True)
                            
                            if self.expdisp:
                                self.experimenterwin.flip()
                                
                            time.sleep(0.497) 
                            
                

                # End of Task
                self.specarray[self.trial][15] = self.elapsedTime.getTime() # StimOff
                participantboard.setAutoDraw(False)
                participantboard2.setAutoDraw(False)
                participanttargetstimuli.setAutoDraw(False)
                if self.expdisp:
                    experimenterboard.setAutoDraw(False)
                    experimenterboard2.setAutoDraw(False)
                    experimentertargetstimuli.setAutoDraw(False)
                self.participantwin.flip() 
                if self.expdisp:
                    self.experimenterwin.flip()
                
                # Write tracking data to file
                if not self.quit:
                    for self.trial in range(0,self.sequencelistL):
                        
                        if (self.trial > 0):
                            # Compute data from Spec Array
                            self.specarray[self.trial][1] = ("%.3f" % (numpy.round((self.specarray[self.trial][15] - self.specarray[self.trial][14])*1000,3))) # Duration    
                            self.specarray[self.trial][3] = self.specarray[self.trial][1] # ITI  
                        
                        self.exporttrackingdata(trial = (self.trial))
                
                
                #####  End of task Closeout permanent frame mask and active displays #####  
                
                # If there is a permanent frame mask clear it
                if self.permanentframemask: 
                    self.participantframemask.setAutoDraw(False);
                    if self.expdisp:
                        self.experimenterframemask.setAutoDraw(False)
        
                # If active display is on clear it
                if self.expdisp:
                    if self.activedisplaylog:
                        for n in range(0,5):
                            self.experimenterbuttonticks[n].setAutoDraw(False)
                        for n in range(0,20):
                            self.experimentertrackers[n].setAutoDraw(False)
                
                # Flip the windows
                self.participantwin.flip()
                if self.expdisp:
                    self.experimenterwin.flip()
                        
                if not self.quit:
                    if self.pauseatend:
                        listofkeys = "{0}".format(", ".join(str(i) for i in self.experimenterkeys))
                        if self.expdisp:
                            self.experimenternotificationtext.setText('Task completed. \nPress any of these keys to exit: %s' % (listofkeys)); self.experimenterwin.flip()
                        else:
                            self.participantnotificationtext = visual.TextStim(self.participantwin, text='Task completed. \nPress any of these keys to exit: %s' % (listofkeys), height = 0.05, pos=[0.5,0], alignHoriz = 'center', alignVert='bottom', color=self.participantmonitor.forgroundcolor, autoLog=False)
                            self.participantnotificationtext.setAutoDraw(True); self.participantwin.flip()
                        continueRoutine = True
                        while continueRoutine:
                            if event.getKeys(self.experimenterkeys): # Expermenter can always end it
                                break
                        
                        # cleanup display
                        if self.expdisp:
                            self.experimenternotificationtext.setAutoDraw(False); self.experimenterwin.flip()
                        else:
                            self.participantnotificationtext.setAutoDraw(False); self.participantwin.flip()    
                    
    
        #####  Close Windows #####   
        if self.participantwinActive:
            self.participantwin.close()
            self.participantwinActive = False
            if self.expdisp:
                self.experimenterwin.close()
        
                
        if (len(self.unicorn) > 0):        
            try:
                # stop recording
                self.UnicornBlack.disconnect()
            except:
                bolerr = 1
            
            

    def sendtrigger(self, val):
        if self.triggers:
            if (len(self.unicorn) > 0):        
                try:
                    self.UnicornBlack.mark_event(int(val)) # Send trigger 
                except:
                    bolerr = 1
                    
            if self.paralleltriggermodule:
                #Send specifed value
                try:
                    parallel.setData(int('{0:08b}'.format(int(val)),2))
                    core.wait(self.triggerpulseduration) # 2 ms pulse duration
                    parallel.setData(0)#sets all pins low
                except:
                    # Try putting an event type 64 in that the user can modify later
                    try:
                        parallel.setData(int('{0:08b}'.format(64),2))
                        core.wait(self.triggerpulseduration) # 2 ms pulse duration
                        parallel.setData(0)#sets all pins low
                    except:
                        self.triggers = self.triggers
                        
            
                    
    def testparallelport(self):
        if self.paralleltriggermodule:
            try:
                parallel.setPortAddress(self.triggerportaddress)
                parallel.setData(0)#sets all pins low
            except:
                self.paralleltriggermodule = False                
                
                
    def updateexperimentermarker(self, stimuluscode, timemark):
        if self.expdisp:
            if self.activedisplaylog:
                
                if not self.useiohub:                     
                    try:
                        while (float(self.trial) > (4*self.multiple)):
                            self.multiple += 1
                        tempindex = int(numpy.subtract(3,(numpy.subtract((float(4)*self.multiple),float(self.trial)))))
                        
                        if (self.previoustrialforexperimentermarker[tempindex] != self.trial): # a new trial has come along
                            self.previoustrialforexperimentermarker[tempindex] = self.trial
                            
                            for n in range((tempindex*5),((tempindex*5)+5)): # Clear all markers
                                self.experimentertrackers[n].setAutoDraw(False)
                                self.activedisplaymarks[n] = 0

                        # determine what fraction of the ITI has elapsed, if no ITI use post-response interval, or max response window, or just default to 1 second...
                        if (float(self.sequencelist[self.trial][self.seqNstimulusITI]) != float(0)):
                            xpos = ((numpy.float(-0.95) + (numpy.float(tempindex)*numpy.float(0.475))) + numpy.float(numpy.true_divide(numpy.subtract(float(timemark),float(self.cumulstimOnTime)),float(self.sequencelist[self.trial][self.seqNstimulusITI])) * float(0.475)))
                        elif (float(self.sequencelist[self.trial][self.seqNpostResponseInterval]) != float(0)):
                            xpos = ((numpy.float(-0.95) + (numpy.float(tempindex)*numpy.float(0.475))) + numpy.float(numpy.true_divide(numpy.subtract(float(timemark),float(self.cumulstimOnTime)),float(self.sequencelist[self.trial][self.seqNpostResponseInterval])) * float(0.475)))
                        elif (float(self.sequencelist[self.trial][self.seqNresponseWindow_max]) != float(0)):
                           xpos = ((numpy.float(-0.95) + (numpy.float(tempindex)*numpy.float(0.475))) + numpy.float(numpy.true_divide(numpy.subtract(float(timemark),float(self.cumulstimOnTime)),float(self.sequencelist[self.trial][self.seqNresponseWindow_max])) * float(0.475)))
                        else:
                            xpos = ((numpy.float(-0.95) + (numpy.float(tempindex)*numpy.float(0.475))) + numpy.float(numpy.true_divide(numpy.subtract(float(timemark),float(self.cumulstimOnTime)),float(1)) * float(0.475)))
                                                
                       
                        if (self.activedisplaymarks[(tempindex*5):((tempindex*5)+5)].count(1) < 5):
                            self.experimentertrackers[self.activedisplaymarks[(tempindex*5):((tempindex*5)+5)].index(0)+(tempindex*5)].setPos([xpos,0.9])
                            self.experimentertrackers[self.activedisplaymarks[(tempindex*5):((tempindex*5)+5)].index(0)+(tempindex*5)].setText('%s' % (stimuluscode))
                            self.experimentertrackers[self.activedisplaymarks[(tempindex*5):((tempindex*5)+5)].index(0)+(tempindex*5)].setAutoDraw(True)
                            self.activedisplaymarks[self.activedisplaymarks[(tempindex*5):((tempindex*5)+5)].index(0)+(tempindex*5)] = 1
                    except:
                        boolerr = 1        

    def exporttrackingdata(self, trial=0):

        # Output Spec Array information
        if trial == 0:
            f = open(self.outputfile, 'w')
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
            f.write('%.3f' % (self.refreshrate*1000))
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
        else:
            # Write Stimulus Events
            f = open(self.outputfile, 'a')
            f.write(str(self.specarray[trial][0]).rjust(7)) # Trial
            f.write(str(self.specarray[trial][9]).rjust(16)) # Event
            for n in range(1,13):
                if n != 9:
                    f.write(str(self.specarray[trial][n]).rjust(16))
            f.write('        ')
            f.write(str(self.specarray[trial][13]).ljust(16))
            f.write('\n')

            # Write Response Events                                                      
            if (len(self.resparray[trial]) > 0):
                temparray = [("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan))]
                for n in range(0,len(self.resparray[trial])):
                    f.write(str(self.resparray[trial][n][0]).rjust(7)) # Trial
                    f.write(str('Response').rjust(16)) # Event
                    temparray[4] = self.resparray[trial][n][1]
                    temparray[6] = self.resparray[trial][n][2]
                    temparray[7] = self.resparray[trial][n][3]
                    temparray[8] = self.resparray[trial][n][4]
                    for m in range(0,(len(temparray)-1)):
                        f.write(str(temparray[m]).rjust(16))
                    f.write(str(temparray[(len(temparray)-1)]).rjust(11))
                    f.write('\n')

            # Write Feedback Events
            if (self.feedbackarray[trial][0] > 0):
                temparray = [("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan))]
                f.write(str(self.feedbackarray[trial][0]).rjust(7)) # Trial
                f.write(str('Feedback').rjust(16)) # Event
                for n in range(0,3):
                    f.write(str(temparray[0]).rjust(16))                                                                                 
                f.write(str(self.feedbackarray[trial][1]).rjust(16)) # Type 
                for n in range(0,3):
                    f.write(str(temparray[0]).rjust(16))                                                                                
                f.write(str(self.feedbackarray[trial][2]).rjust(16)) # Cumulative Time                                                                                 
                f.write(str(self.feedbackarray[trial][3]).rjust(16)) # Trigger 
                for n in range(0,2):
                    f.write(str(temparray[0]).rjust(16))
                f.write('        ')
                f.write(str(self.feedbackarray[trial][4]).ljust(16)) # Filename
                f.write('\n')                                                                             

            # Write Feedback Response Events                                                  
            if (len(self.feedbackresparray[trial]) > 0):
                temparray = [("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan)), ("%.6f" % (numpy.nan))]
                for n in range(0,len(self.feedbackresparray[trial])):
                    f.write(str(self.feedbackresparray[trial][n][0]).rjust(7)) # Trial
                    f.write(str('Response').rjust(16)) # Event
                    temparray[4] = self.feedbackresparray[trial][n][1]
                    temparray[6] = self.feedbackresparray[trial][n][2]
                    temparray[7] = self.feedbackresparray[trial][n][3]
                    temparray[8] = self.feedbackresparray[trial][n][4]
                    for m in range(0,(len(temparray)-1)):
                        f.write(str(temparray[m]).rjust(16))
                    f.write(str(temparray[(len(temparray)-1)]).rjust(11))
                    f.write('\n')
                    
        # Close File                   
        f.close()
          
            
# # # # #
# DEBUG #
if __name__ == "__main__":
    
    
    #from Engine.vepengine import Engine
    
    task = Engine()
    os.chdir(os.path.dirname(os.getcwd()))
    
    # Instructions
    task.showinstructions = True
    
    # Sequence Information
    task.totaltrials = 10
    
    # Filename Prefix and Suffix
    task.prefix = 'VEP'
    task.suffix = 'p'
    task.filenametooltip = 'Format: ### Remember to add condition after the ID.'
    task.testblock = False
    
    # Global image frame/mask
    task.permanentframemask = ''
    
    # Usable keys during task
    task.participantkeys = ['1', '4', 'enter']
    
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
    
    task.start()