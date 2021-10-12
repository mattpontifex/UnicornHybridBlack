"""
Version 7
Authored by Matthew Pontifex

Includes ability to present stimuli as images, movies, and sound

Follows traditional stim on, stim off, ITI/ISI format
"""

# basicstimuluspresentationengine: classes to run an experiment in psychopy
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
        self.pauseatstart = False
        self.pauseatend = False
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
        self.unicornrequired = True
        
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
        
        self.participantwinActive = False
        self.finished = False
        

        
    def start(self):
        
        if self.debug:
            self.printoutput = True
        
        if not self.unicornrequired:
            # if the unicorn device is not required
            self.unicorn = []
            
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
            self.participantwin.winHandle.activate() 
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
        
        
            self.participantwin.winHandle.maximize() 
            self.participantwin.winHandle.activate() 
            
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
                    image_file_types = ['.gif', '.png', '.jpg', '.bmp', '.tiff', '.jpeg', '.pbm', '.pgm', '.ppm', '.rast', '.xbm', '.rgb']
                    movie_file_types = ['.mov', '.wmv', '.mp4']
                    audio_file_types = ['.wav', '.mp3', '.3gp', '.m4a', '.wma']
                    for n in range(0,len(self.instructioncard)):
                        
                        if not self.quit:
                                            
                            self.participantwin.winHandle.maximize() 
                            self.participantwin.winHandle.activate() 
                            
                            if self.expdisp:
                                if not self.pauseatstart:
                                    self.experimenternotificationtext.setText('task will begin when someone pushes a button...'); self.experimenterwin.flip()
                                else:
                                    self.experimenternotificationtext.setText('push a button to continue...'); self.experimenterwin.flip()
                            
                            if self.instructioncard[n].endswith(tuple(image_file_types)): # Check if image
                                # Load image
                                participantstimulus = visual.ImageStim(self.participantwin, image = os.path.join(self.folders.stimulusfolder, self.instructioncard[n]), interpolate=True, autoLog=False)
                                if self.expdisp:
                                    experimenterstimulus = visual.ImageStim(self.experimenterwin, image = os.path.join(self.folders.stimulusfolder, self.instructioncard[n]), interpolate=True, autoLog=False)
                                    experimenterstimulus.size = participantstimulus.size
                                participantstimulus.setAutoDraw(True); self.participantwin.flip()
                                if self.expdisp:
                                    experimenterstimulus.setAutoDraw(True); self.experimenterwin.flip()
                                    
                            elif self.instructioncard[n].endswith(tuple(movie_file_types)): # Check if movie
                                # Load movie
                                participantstimulus = visual.MovieStim2(self.participantwin,filename=os.path.join(self.folders.stimulusfolder, self.instructioncard[n]), pos = [0.0,0.0], autoLog=False)
                                if self.expdisp:
                                    self.taskmovieexperimenter = visual.MovieStim2(self.experimenterwin,filename=os.path.join(self.folders.stimulusfolder, self.instructioncard[n]), pos = [0.0,0.0], volume=0, autoLog=False)
                                    experimenterstimulus.size = participantstimulus.size
                                    
                                participantstimulus.setAutoDraw(True); self.participantwin.flip()
                                if self.expdisp:
                                    experimenterstimulus.setAutoDraw(True); self.experimenterwin.flip()
                
                                continueRoutine = True
                                while (participantstimulus.status != visual.FINISHED) and continueRoutine:
                
                                    # Flip frames
                                    self.participantwin.flip();
                                    if self.expdisp:
                                        self.experimenterwin.flip()
                
                                    if event.getKeys(["escape", "q"]): # Check for kill keys
                                        self.quit = True
                                        continueRoutine = False
                                        break
                                    
                                    if event.getKeys(self.experimenterkeys): # Expermenter can always skip
                                        continueRoutine = False
                                        break
                                    
                            elif self.instructioncard[n].endswith(tuple(audio_file_types)): # Check if audio
                                if (self.soundmodule):
                                    participantstimulus = sound.Sound(os.path.join(self.folders.stimulusfolder, self.instructioncard[n]), autoLog=False)
                                    participantstimulus.play()
                            
                                
                            # load sequence file and preload stimuli
                            continueRoutine = True
                            try:
                                if not self.sequenceready:
                                    self.importsequencefile() # Import sequence information
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
                                        
                            # Remove the instruction card    
                            if self.instructioncard[n].endswith(tuple(image_file_types)) or self.instructioncard[n].endswith(tuple(movie_file_types)): # Check if image or movie
                                participantstimulus.setAutoDraw(False); self.participantwin.flip()
                                if self.expdisp:
                                    experimenterstimulus.setAutoDraw(False); self.experimenterwin.flip()  
                
            
            
        
            
            
            
            
            #####  Prepare for task initiation #####
            if not self.quit:
                try:
                    if not self.sequenceready:
                        self.importsequencefile() # Import sequence information if it was not imported during instructions
                except:
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
                
                # Prep process
                #self.participantwin.flip(); self.sendtrigger(0) # Send trigger
                #self.participantwin.flip(); self.sendtrigger(0) # Send trigger
                #self.participantwin.flip(); self.sendtrigger(0) # Send trigger
                
                time.sleep(self.delaybeforestart)

                #####  Task Begins #####  
                
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
                                
                            
                            self.participantwin.winHandle.maximize() 
                            self.participantwin.winHandle.activate()     
                                
                            #####  Prepare for trial #####
                            
                            # Load information for the current trial
                            if (self.trial > 1):
                                self.specarray[self.trial-1][3] = ("%.3f" % (numpy.round(self.elapsedTime.getTime()*1000,3)))
                    
                            # Load ITI information for the previous trial
                            if (self.trial > 2):
                                self.specarray[self.trial-2][2] = ("%.3f" % (numpy.round(numpy.float(self.specarray[self.trial-2][3])-(numpy.float(self.specarray[self.trial-2][15])*1000)+(numpy.float(self.specarray[self.trial-1][14])*1000),3)))
                            
                            # Initialize trial checks
                            self.stimulusisbeingdisplayed = False
                            self.responsehasbeenmade = False
                            self.continuetrial = True
                            self.stimOnTime = 0
                            self.stimOffTime = 0
                            self.trialkeys = []
                            self.trialRT = []
                            self.trialRTg = []
                            self.trialcorr = []
                            self.stimtrigger = 0
                            self.resptrigger = 0
                    
                            # Setup trial stimuli
                            if self.sequencelist[self.trial][self.seqNstimulustype] == '0': # if the stimulus type is an image
                                self.taskstimuliparticipant[int(self.sequencelist[self.trial][self.seqNstimulusFile])].setPos([self.sequencelist[self.trial][self.seqNstimulusXcoord],self.sequencelist[self.trial][self.seqNstimulusYcoord]]) # Load stimulus position information
                                if self.expdisp:
                                    self.taskstimuliexperimenter[int(self.sequencelist[self.trial][self.seqNstimulusFile])].pos = self.taskstimuliparticipant[int(self.sequencelist[self.trial][self.seqNstimulusFile])].pos
                                    self.taskstimuliexperimenter[int(self.sequencelist[self.trial][self.seqNstimulusFile])].size = self.taskstimuliparticipant[int(self.sequencelist[self.trial][self.seqNstimulusFile])].size
                            if self.sequencelist[self.trial][self.seqNstimulustype] == '1': # if the stimulus type is a movie
                                self.taskmovieparticipant[int(self.sequencelist[self.trial][self.seqNstimulusFile])].setPos([self.sequencelist[self.trial][self.seqNstimulusXcoord],self.sequencelist[self.trial][self.seqNstimulusYcoord]]) # Load stimulus position information
                                if self.expdisp:
                                    self.taskmovieexperimenter[int(self.sequencelist[self.trial][self.seqNstimulusFile])].pos = self.taskmovieparticipant[int(self.sequencelist[self.trial][self.seqNstimulusFile])].pos
                                    self.taskmovieexperimenter[int(self.sequencelist[self.trial][self.seqNstimulusFile])].size = self.taskmovieparticipant[int(self.sequencelist[self.trial][self.seqNstimulusFile])].size
                    
                            # Setup trial mask
                            if (self.trial > 1):
                                if (self.sequencelist[self.trial-1][self.seqNmask] != '-1'): # Did the previous trial have a mask
                                    if (self.sequencelist[self.trial-1][self.seqNmask] != self.sequencelist[self.trial][self.seqNmask]): # If the mask is not the same as the new trial
                                        self.taskstimuliparticipant[int(self.sequencelist[self.trial-1][self.seqNmask])].setAutoDraw(False) # stop showing mask
                                        if self.expdisp:
                                            self.taskstimuliexperimenter[int(self.sequencelist[self.trial-1][self.seqNmask])].setAutoDraw(False) # stop showing mask
                            if (self.sequencelist[self.trial][self.seqNmask] != '-1'):
                                self.taskstimuliparticipant[int(self.sequencelist[self.trial][self.seqNmask])].setAutoDraw(True) # start showing mask
                                if self.expdisp:
                                    self.taskstimuliexperimenter[int(self.sequencelist[self.trial][self.seqNmask])].pos = self.taskstimuliparticipant[int(self.sequencelist[self.trial][self.seqNmask])].pos
                                    self.taskstimuliexperimenter[int(self.sequencelist[self.trial][self.seqNmask])].size = self.taskstimuliparticipant[int(self.sequencelist[self.trial][self.seqNmask])].size
                                    self.taskstimuliexperimenter[int(self.sequencelist[self.trial][self.seqNmask])].setAutoDraw(True) # Start showing mask
                                    
                            
                            if (len(self.unicorn) > 0):        
                                try:
                                    self.UnicornBlack.safe_to_log(False)  # save io overhead
                                except:
                                    bolerr = 1
                            self.elapsedTime = core.Clock(); self.elapsedTime.reset()    
                            event.clearEvents()
                            
                            if self.debug:
                                checktimes = []
                                
                            #####  Run Trial #####
                            if self.sequencelist[self.trial][self.seqNstimulustype] == '0': # if the stimulus type is an image
                                
                                if self.debug:
                                    print('\n\n')
                                    print('Trial %d' % self.trial)
                                    print('Prestim period: %f' % float(self.sequencelist[self.trial][self.seqNpreStimulusInterval]))
                                    print('Stimulus duration: %f' % float(self.sequencelist[self.trial][self.seqNstimulusDuration]))
                                    print('Response window: %f' % float(self.sequencelist[self.trial][self.seqNresponseWindow_max]))
                                    print('Participant keys: ', self.participantkeys)


                                while self.continuetrial:
                                    turnstimoff = False
                    
                                    if event.getKeys(["escape", "q"]): # Check for kill keys
                                        self.quit = True
                                        self.continuetrial = False
                                        break
                                    else:
                                        
                                        #Stimulus Onset and Offset Controls
                                        if not self.stimulusisbeingdisplayed: # Stimulus is not being shown
                                            if (self.stimOnTime == 0): # Has the stimulus been shown yet
                                                if (self.elapsedTime.getTime() >= float(self.sequencelist[self.trial][self.seqNpreStimulusInterval])): # Has prestim time expired
                        
                                                    self.taskstimuliparticipant[int(self.sequencelist[self.trial][self.seqNstimulusFile])].setAutoDraw(True) # Start showing stimulus
                                                    self.participantwin.flip(); self.sendtrigger(self.sequencelist[self.trial][self.seqNstimulusCode]) # Send trigger
                                                    self.cumulstimOnTime = self.cumulativeTime.getTime()
                                                    self.stimOnTime = self.elapsedTime.getTime();
                                                    if self.expdisp:
                                                        self.taskstimuliexperimenter[int(self.sequencelist[self.trial][self.seqNstimulusFile])].setAutoDraw(True) # Start showing stimulus
                                                        self.experimenterwin.flip()
                                                    self.stimulusisbeingdisplayed = True
                                                    self.updateexperimentermarker(self.sequencelist[self.trial][self.seqNstimulusCode],self.cumulstimOnTime)
                                                    
                                        else: # Stimulus is being shown
                                            if ((self.elapsedTime.getTime() - self.stimOnTime) >= (float(self.sequencelist[self.trial][self.seqNstimulusDuration]))): # If stimulus duration expired
                                                turnstimoff = True
                                                
                                        #if self.debug:
                                            #print(self.participantwin._toDraw)
                                            #timecheck = self.elapsedTime.getTime()
                                            #print('%f' % timecheck)
                                            #checktimes.append(timecheck)
                        
                                        # Determine if a key has been pressed
                                        theseKeys = event.getKeys(keyList=self.participantkeys, timeStamped=self.cumulativeTime)
                                        if (len(theseKeys) > 0): #at least one key was pressed
                                            t = (theseKeys[0][1]-self.cumulstimOnTime)
                                            gt = theseKeys[0][1]
                                            if (self.trialkeys == []):
                                                self.trialkeys = theseKeys[0][0]
                                                self.sendtrigger(theseKeys[0][0])
                                                self.trialRT = t
                                                self.trialRTg = gt
                                            self.resparray[self.trial].append([self.trial, theseKeys[0][0], t, gt, 0])
                                            if ((self.elapsedTime.getTime() - self.stimOnTime) >= (float(self.sequencelist[self.trial][self.seqNstimulusDuration_min]))): # If a response is made and the minimum duration has expired
                                                turnstimoff = True
                                                self.continuetrial = False # End Trial
                                            self.updateexperimentermarker(theseKeys[0][0],gt)
                                            if self.debug:
                                                print('keypress received:', theseKeys[0][0])
                        
                                        if ((self.elapsedTime.getTime() - self.stimOnTime) >= (float(self.sequencelist[self.trial][self.seqNresponseWindow_max]))): # If the maximum response window duration has expired
                                            self.continuetrial = False # End Trial
                                            
                                        if turnstimoff or not self.continuetrial:
                                            self.taskstimuliparticipant[int(self.sequencelist[self.trial][self.seqNstimulusFile])].setAutoDraw(False) # Stop showing stimulus
                                            self.participantwin.flip()
                                            if (self.stimOffTime == 0):
                                                self.stimOffTime = self.elapsedTime.getTime()
                                                self.cumulstimOffTime = self.cumulativeTime.getTime()
                                            if self.expdisp:
                                                self.taskstimuliexperimenter[int(self.sequencelist[self.trial][self.seqNstimulusFile])].setAutoDraw(False) # Stop showing stimulus
                                                self.experimenterwin.flip()
                                            self.stimulusisbeingdisplayed = False
                        
                    
                            elif self.sequencelist[self.trial][self.seqNstimulustype] == '1': # if the stimulus type is a movie
                                while self.continuetrial:
                                    
                                    if event.getKeys(["escape", "q"]): # Check for kill keys
                                        self.quit = True
                                        self.continuetrial = False
                                        break
                                    
                                    #Stimulus Onset and Offset Controls
                                    if (self.stimOnTime == 0): # Has the stimulus been shown yet
                                        if (self.elapsedTime.getTime() >= float(self.sequencelist[self.trial][self.seqNpreStimulusInterval])): # Has prestim time expired
                    
                                            self.taskmovieparticipant[int(self.sequencelist[self.trial][self.seqNstimulusFile])].setAutoDraw(True) # Start showing stimulus
                                            if self.expdisp:
                                                self.taskmovieexperimenter[int(self.sequencelist[self.trial][self.seqNstimulusFile])].setAutoDraw(True) # Start showing stimulus
                                            self.participantwin.flip(); self.sendtrigger(self.sequencelist[self.trial][self.seqNstimulusCode]) # Send trigger
                                            self.cumulstimOnTime = self.cumulativeTime.getTime()
                                            self.stimOnTime = self.elapsedTime.getTime();
                                                
                                            if self.expdisp:
                                                self.experimenterwin.flip()
                                            self.stimulusisbeingdisplayed = True
                                            self.updateexperimentermarker(self.sequencelist[self.trial][self.seqNstimulusCode],self.cumulstimOnTime)
                    
                                            while (self.taskmovieparticipant[int(self.sequencelist[self.trial][self.seqNstimulusFile])].status != visual.FINISHED) and self.continuetrial:
                    
                                                # Flip frames
                                                self.participantwin.flip();
                                                if self.expdisp:
                                                    self.experimenterwin.flip()
                    
                                                # To avoid tying RT to the monitor refresh rate, this loops for most of the refresh rate period
                                                checkkeytimer = core.CountdownTimer(start=(float(numpy.multiply(float(0.8),float(self.refreshrate)))))
                                                while checkkeytimer.getTime() > 0 and (self.taskmovieparticipant[int(self.sequencelist[self.trial][self.seqNstimulusFile])].status != visual.FINISHED):
                                                                                           
                                                    # Determine if a key has been pressed
                                                    theseKeys = event.getKeys(keyList=self.participantkeys, timeStamped=self.cumulativeTime)
                                                    if (len(theseKeys) > 0): #at least one key was pressed
                                                        t = (theseKeys[0][1]-self.cumulstimOnTime)
                                                        gt = theseKeys[0][1]
                                                        if (self.trialkeys == []):
                                                            self.trialkeys = theseKeys[0][0]
                                                            self.sendtrigger(theseKeys[0][0])
                                                            self.trialRT = t
                                                            self.trialRTg = gt
                                                        self.resparray[self.trial].append([self.trial, theseKeys[0][0], t, gt, 0])
                                                        if ((self.elapsedTime.getTime() - self.stimOnTime) >= (float(self.sequencelist[self.trial][self.seqNstimulusDuration_min]))): # If a response is made and the minimum duration has expired
                                                            self.continuetrial = False # End trial once movie is over
                                                        self.updateexperimentermarker(theseKeys[0][0],gt)
                    
                                                    if event.getKeys(["escape", "q"]): # Check for kill keys
                                                        self.quit = True
                                                        self.continuetrial = False
                                                        break
                    
                                            # Once the movie has finished                                          
                                            self.taskmovieparticipant[int(self.sequencelist[self.trial][self.seqNstimulusFile])].setAutoDraw(False) # Stop showing stimulus
                                            self.participantwin.flip()
                                            if (self.stimOffTime == 0):
                                                self.stimOffTime = self.elapsedTime.getTime()
                                                self.cumulstimOffTime = self.cumulativeTime.getTime()
                                            if self.expdisp:
                                                self.taskmovieexperimenter[int(self.sequencelist[self.trial][self.seqNstimulusFile])].setAutoDraw(False) # Stop showing stimulus
                                                self.experimenterwin.flip()
                                            self.stimulusisbeingdisplayed = False
                    
                                    # Determine if a key has been pressed
                                    theseKeys = event.getKeys(keyList=self.participantkeys, timeStamped=self.cumulativeTime)
                                    if (len(theseKeys) > 0): #at least one key was pressed
                                        t = (theseKeys[0][1]-self.cumulstimOnTime)
                                        gt = theseKeys[0][1]
                                        if (self.trialkeys == []):
                                            self.trialkeys = theseKeys[0][0]
                                            self.sendtrigger(theseKeys[0][0])
                                            self.trialRT = t
                                            self.trialRTg = gt
                                            self.resparray[self.trial].append([self.trial, theseKeys[0][0], t, gt, 0])
                                            self.updateexperimentermarker(theseKeys[0][0],gt)
                                            self.continuetrial = False # End Trial
                                                        
                                    if ((self.elapsedTime.getTime() - self.stimOnTime) >= (float(self.sequencelist[self.trial][self.seqNresponseWindow_max]))): # If the maximum response window duration has expired
                                        self.continuetrial = False # End Trial
                                        
                            elif self.sequencelist[self.trial][self.seqNstimulustype] == '2': # if the stimulus type is audio
                                while self.continuetrial:
                                    
                                    if event.getKeys(["escape", "q"]): # Check for kill keys
                                        self.quit = True
                                        self.continuetrial = False
                                        break
                                    
                                    #Stimulus Onset and Offset Controls
                                    if (self.stimOnTime == 0): # Has the stimulus been played yet
                                        if (self.elapsedTime.getTime() >= float(self.sequencelist[self.trial][self.seqNpreStimulusInterval])): # Has prestim time expired
                                            
                                            self.taskaudioparticipant[int(self.sequencelist[self.trial][self.seqNstimulusFile])].play() # Play audio
                                            self.sendtrigger(self.sequencelist[self.trial][self.seqNstimulusCode]) # Send trigger    
                                            self.cumulstimOnTime = self.cumulativeTime.getTime()   
                                            self.stimOnTime = self.elapsedTime.getTime();                 
                                            self.stimOffTime = self.elapsedTime.getTime()
                                            self.cumulstimOffTime = self.cumulativeTime.getTime()
                                            self.updateexperimentermarker(self.sequencelist[self.trial][self.seqNstimulusCode],self.cumulstimOnTime)
                    
                                    # Determine if a key has been pressed
                                    theseKeys = event.getKeys(keyList=self.participantkeys, timeStamped=self.cumulativeTime)
                                    if (len(theseKeys) > 0): #at least one key was pressed
                                        t = (theseKeys[0][1]-self.cumulstimOnTime)
                                        gt = theseKeys[0][1]
                                        if (self.trialkeys == []):
                                            self.trialkeys = theseKeys[0][0]
                                            self.sendtrigger(theseKeys[0][0])
                                            self.trialRT = t
                                            self.trialRTg = gt
                                        self.resparray[self.trial].append([self.trial, theseKeys[0][0], t, gt, 0])
                                        if ((self.elapsedTime.getTime() - self.stimOnTime) >= (float(self.sequencelist[self.trial][self.seqNstimulusDuration_min]))): # If a response is made and the minimum duration has expired
                                            self.continuetrial = False # End Trial
                                        self.updateexperimentermarker(theseKeys[0][0],gt)
                    
                                    if ((self.elapsedTime.getTime() - self.stimOnTime) >= (float(self.sequencelist[self.trial][self.seqNresponseWindow_max]))): # If the maximum response window duration has expired
                                        self.continuetrial = False # End Trial
                            
                            
                            
                                
                            #####  Process Trial #####
                            if self.debug:
                                if (len(checktimes) > 0):
                                    #print(numpy.diff(checktimes))
                                    print('Time check: %f' % numpy.median(numpy.diff(checktimes)))
                                
                            
                            
                            # Check Responses
                            if (len(self.trialkeys) == 0): # No response was made
                                self.trialkeys = numpy.nan
                                self.trialRT = numpy.nan
                                if (str(self.sequencelist[self.trial][self.seqNcorrectResp]) == str(0)) or (str(self.sequencelist[self.trial][self.seqNcorrectResp]) == str('none')):
                                    self.trialcorr = 1 # Non-response was the correct answer
                                else:
                                    self.trialcorr = 0 # Trial was incorrect
                                if self.debug:
                                    print('No response was made. Trial accuracy is:', self.trialcorr)
                            else:
                                if (numpy.less(float(self.trialRT), float(self.sequencelist[self.trial][self.seqNresponseWindow_min]))):
                                    self.trialcorr = -1 # The response was impulsive and outside the window
                                    self.trialRT = self.trialRT - self.stimOnTime # Adjust RT based on stimulus onset
                                elif (numpy.greater(float(self.trialRT), float(self.sequencelist[self.trial][self.seqNresponseWindow_max]))):
                                    self.trialcorr = -2 # The response was outside the window
                                    self.trialRT = self.trialRT - self.stimOnTime # Adjust RT based on stimulus onset
                                else:
                                    self.trialRT = self.trialRT - self.stimOnTime # Adjust RT based on stimulus onset
                                    if (self.trialkeys == self.sequencelist[self.trial][self.seqNcorrectResp]):
                                        self.trialcorr = 1 # Trial was correct
                                    else:
                                        self.trialcorr = 0 # Trial was incorrect
                                    if self.debug:
                                        print('A response was received in the window. Trial accuracy is:', self.trialcorr)
                                        
                            # Load Data Into Spec Array
                            self.specarray[self.trial][0] = self.trial # Trial
                            self.specarray[self.trial][1] = ("%.3f" % (numpy.round((self.stimOffTime - self.stimOnTime)*1000,3))) # Duration        
                            self.specarray[self.trial][4] = self.sequencelist[self.trial][self.seqNstimulusCode] # Type
                            self.specarray[self.trial][5] = self.trialkeys # Response
                            self.specarray[self.trial][6] = self.trialcorr # Correct
                            self.specarray[self.trial][7] = ("%.3f" % (numpy.round(self.trialRT*1000,3))) # Latency
                            self.specarray[self.trial][8] = ("%.6f" % (numpy.round(self.cumulstimOnTime,6))) # CumulativeStim
                            self.specarray[self.trial][9] = 'Stimulus' # Event
                            if self.triggers:
                                self.specarray[self.trial][10] = 1
                            else:
                                self.specarray[self.trial][10] = 0
                            self.specarray[self.trial][11] = ("%.2f" % (numpy.round(numpy.float(self.sequencelist[self.trial][self.seqNresponseWindow_min])*1000,2))) # Min Resp Win
                            self.specarray[self.trial][12] = ("%.2f" % (numpy.round(numpy.float(self.sequencelist[self.trial][self.seqNresponseWindow_max])*1000,2))) # Max Resp Win
                            if self.sequencelist[self.trial][self.seqNstimulustype] == '0': # if the stimulus type is an image
                                self.specarray[self.trial][13] = self.individualimagelist[int(self.sequencelist[self.trial][self.seqNstimulusFile])] # Stimulus
                            elif self.sequencelist[self.trial][self.seqNstimulustype] == '1': # if the stimulus type is a movie
                                self.specarray[self.trial][13] = self.fullmovielist[int(self.sequencelist[self.trial][self.seqNstimulusFile])] # Stimulus
                            elif self.sequencelist[self.trial][self.seqNstimulustype] == '2': # if the stimulus type is audio
                                self.specarray[self.trial][13] = self.individualaudiolist[int(self.sequencelist[self.trial][self.seqNstimulusFile])] # Stimulus
                            self.specarray[self.trial][14] = self.stimOnTime # StimOn
                            self.specarray[self.trial][15] = self.stimOffTime # StimOff
                    
                            if self.debug:
                                print('Stim On: %f' % self.stimOnTime)
                                print('Stim Off: %f' % self.stimOffTime)
                                print('Actual Duration: %s' % self.specarray[self.trial][1])
                                print('\n')
                    
                            # Update experimentor screen with task performance
                            if self.expdisp:
                                    
                                if (self.trialcorr == 1):
                                    self.stimcorrectcount = self.stimcorrectcount + 1
                                    trialcorrect = ' Correct    '
                                    if not ((str(self.sequencelist[self.trial][self.seqNcorrectResp]) == str('none')) or (str(self.sequencelist[self.trial][self.seqNcorrectResp]) == str(0))):
                                        self.countcorrectresponseexpected = self.countcorrectresponseexpected + 1
                                        self.countresponseexpected = self.countresponseexpected + 1
                                if (self.trialcorr == 0):
                                    trialcorrect = ' Incorrect  '
                                    if not ((str(self.sequencelist[self.trial][self.seqNcorrectResp]) == str('none')) or (str(self.sequencelist[self.trial][self.seqNcorrectResp]) == str(0))):
                                        self.countresponseexpected = self.countresponseexpected + 1
                                if (self.trialcorr == -1):
                                    trialcorrect = ' Impulsive  '
                                if (self.trialcorr == -2):
                                    trialcorrect = ' Delayed    '
                                if (self.countresponseexpected > 0):
                                    overallaccuracy = '(%.1f%%)' % ((self.countcorrectresponseexpected/self.countresponseexpected)*100)
                                else:
                                    overallaccuracy = 'na'
                                self.experimenternotificationtext.setText('Trial %d: %s %s ' % (self.trial, trialcorrect, overallaccuracy)); self.experimenterwin.flip()
                    
                            # Format Response Tracking Data
                            if (len(self.resparray[self.trial]) > 0):
                                for n in range(0,len(self.resparray[self.trial])):
                                    self.resparray[self.trial][n][2] = ("%.3f" % (numpy.round((self.resparray[self.trial][n][2]- self.stimOnTime)*1000,3))) # Latency
                                    self.resparray[self.trial][n][3] = ("%.6f" % (numpy.round(self.resparray[self.trial][n][3],6))) # Latency
                                    if self.triggers:
                                        if self.markfirstresponseonly:
                                            self.resparray[self.trial][0][4] = 1
                                        else:
                                            self.resparray[self.trial][n][4] = 1
                                
                            if not self.quit:
                                self.exporttrackingdata(trial = (self.trial-2))
                    
                            
                            
                            #####  Provide Feedback #####
                            
                            # Check to see if we are even providing feedback this trial
                            if (self.sequencelist[self.trial][self.seqNcorrectResponseStimulusFile] != '-1') or (self.sequencelist[self.trial][self.seqNcommissionErrorStimulusFile] != '-1') or (self.sequencelist[self.trial][self.seqNomissionErrorStimulusFile] != '-1') or (self.sequencelist[self.trial][self.seqNimpulsiveErrorStimulusFile] != '-1') or (self.sequencelist[self.trial][self.seqNdelayErrorStimulusFile] != '-1'):
                    
                                # See how much of a delay is necessary
                                feedbackdelay =  numpy.subtract(float(self.sequencelist[self.trial][self.seqNpreFeedbackDelay]),numpy.subtract(self.elapsedTime.getTime(),self.stimOffTime))
                    
                                # Wait for the delay period to expire before presenting stimulus
                                event.clearEvents()
                                feedbackTimer = core.CountdownTimer(float(feedbackdelay)) # Sets to run for delay period
                                while (feedbackTimer.getTime() > 0):
                                    
                                    if event.getKeys(["escape", "q"]): # see if someone is trying to quit
                                        self.quit = True
                                        break
                                    
                                    # Determine if a key has been pressed
                                    theseKeys = event.getKeys(keyList=self.participantkeys, timeStamped=self.cumulativeTime)
                                    if (len(theseKeys) > 0): #at least one key was pressed
                                        t = (theseKeys[0][1]-self.cumulstimOnTime)
                                        gt = theseKeys[0][1]
                                        if self.triggers:
                                            if self.markfirstresponseonly and (len(self.resparray[self.trial]) > 0):
                                                self.resparray[self.trial].append([self.trial, theseKeys[0][0], ("%.3f" % (numpy.round((t)*1000,3))), ("%.6f" % (numpy.round(gt,6))), 0])
                                            else:
                                                self.sendtrigger(theseKeys[0][0])
                                                self.resparray[self.trial].append([self.trial, theseKeys[0][0], ("%.3f" % (numpy.round((t)*1000,3))), ("%.6f" % (numpy.round(gt,6))), 1])
                                        else:
                                            self.resparray[self.trial].append([self.trial, theseKeys[0][0], ("%.3f" % (numpy.round((t)*1000,3))), ("%.6f" % (numpy.round(gt,6))), 0])
                                        self.updateexperimentermarker(theseKeys[0][0],gt)
                                        event.clearEvents()
                    
                                # Start showing feedback
                                feedbacktoshow = ['nan','nan','nan']
                                if (self.trialcorr == 1): # Correct response
                                    if (self.sequencelist[self.trial][self.seqNcorrectResponseStimulusFile] != '-1'):
                                        if self.sequencelist[self.trial][self.seqNcorrectResponseStimulustype] == '0': # if the stimulus type is an image
                                            feedbacktoshow = [0,self.sequencelist[self.trial][self.seqNcorrectResponseStimulusFile],self.sequencelist[self.trial][self.seqNcorrectResponseCode]]
                                        elif self.sequencelist[self.trial][self.seqNcorrectResponseStimulustype] == '1': # if the stimulus type is a movie
                                            feedbacktoshow = [1,self.sequencelist[self.trial][self.seqNcorrectResponseStimulusFile],self.sequencelist[self.trial][self.seqNcorrectResponseCode]]
                                        elif self.sequencelist[self.trial][self.seqNcorrectResponseStimulustype] == '2': # if the stimulus type is audio
                                            feedbacktoshow = [2,self.sequencelist[self.trial][self.seqNcorrectResponseStimulusFile],self.sequencelist[self.trial][self.seqNcorrectResponseCode]]
                                            
                                elif (self.trialcorr == -1): # Impulsive response
                                    if (self.sequencelist[self.trial][self.seqNimpulsiveErrorStimulusFile] != '-1'):
                                        if self.sequencelist[self.trial][self.seqNimpulsiveErrorStimulustype] == '0': # if the stimulus type is an image
                                            feedbacktoshow = [0,self.sequencelist[self.trial][self.seqNimpulsiveErrorStimulusFile],self.sequencelist[self.trial][self.seqNimpulsiveErrorCode]]
                                        elif self.sequencelist[self.trial][self.seqNimpulsiveErrorStimulustype] == '1': # if the stimulus type is a movie
                                            feedbacktoshow = [1,self.sequencelist[self.trial][self.seqNimpulsiveErrorStimulusFile],self.sequencelist[self.trial][self.seqNimpulsiveErrorCode]]
                                        elif self.sequencelist[self.trial][self.seqNimpulsiveErrorStimulustype] == '2': # if the stimulus type is audio
                                            feedbacktoshow = [2,self.sequencelist[self.trial][self.seqNimpulsiveErrorStimulusFile],self.sequencelist[self.trial][self.seqNimpulsiveErrorCode]]
                    
                                elif (self.trialcorr == -2): # Delayed response
                                    if (self.sequencelist[self.trial][self.seqNdelayErrorStimulusFile] != '-1'):
                                        if self.sequencelist[self.trial][self.seqNdelayErrorStimulustype] == '0': # if the stimulus type is an image
                                            feedbacktoshow = [0,self.sequencelist[self.trial][self.seqNdelayErrorStimulusFile],self.sequencelist[self.trial][self.seqNdelayErrorCode]]
                                        elif self.sequencelist[self.trial][self.seqNdelayErrorStimulustype] == '1': # if the stimulus type is a movie
                                            feedbacktoshow = [1,self.sequencelist[self.trial][self.seqNdelayErrorStimulusFile],self.sequencelist[self.trial][self.seqNdelayErrorCode]]
                                        elif self.sequencelist[self.trial][self.seqNdelayErrorStimulustype] == '2': # if the stimulus type is audio
                                            feedbacktoshow = [2,self.sequencelist[self.trial][self.seqNdelayErrorStimulusFile],self.sequencelist[self.trial][self.seqNdelayErrorCode]]
                                        
                                elif (self.trialcorr == 0): # Incorrect response
                                    if numpy.isnan(self.trialRT): # Omission Error
                                        if (self.sequencelist[self.trial][self.seqNomissionErrorStimulusFile] != '-1'):
                                            if self.sequencelist[self.trial][self.seqNomissionErrorStimulustype] == '0': # if the stimulus type is an image
                                                feedbacktoshow = [0,self.sequencelist[self.trial][self.seqNomissionErrorStimulusFile],self.sequencelist[self.trial][self.seqNomissionErrorCode]]
                                            elif self.sequencelist[self.trial][self.seqNomissionErrorStimulustype] == '1': # if the stimulus type is a movie
                                                feedbacktoshow = [1,self.sequencelist[self.trial][self.seqNomissionErrorStimulusFile],self.sequencelist[self.trial][self.seqNomissionErrorCode]]
                                            elif self.sequencelist[self.trial][self.seqNomissionErrorStimulustype] == '2': # if the stimulus type is audio
                                                feedbacktoshow = [2,self.sequencelist[self.trial][self.seqNomissionErrorStimulusFile],self.sequencelist[self.trial][self.seqNomissionErrorCode]]
                                            
                                    else: # Commission Error
                                        if (self.sequencelist[self.trial][self.seqNcommissionErrorStimulusFile] != '-1'):
                                            if self.sequencelist[self.trial][self.seqNcommissionErrorStimulustype] == '0': # if the stimulus type is an image
                                                feedbacktoshow = [0,self.sequencelist[self.trial][self.seqNcommissionErrorStimulusFile],self.sequencelist[self.trial][self.seqNcommissionErrorCode]]
                                            elif self.sequencelist[self.trial][self.seqNcommissionErrorStimulustype] == '1': # if the stimulus type is a movie
                                                feedbacktoshow = [1,self.sequencelist[self.trial][self.seqNcommissionErrorStimulusFile],self.sequencelist[self.trial][self.seqNcommissionErrorCode]]
                                            elif self.sequencelist[self.trial][self.seqNcommissionErrorStimulustype] == '2': # if the stimulus type is audio
                                                feedbacktoshow = [2,self.sequencelist[self.trial][self.seqNcommissionErrorStimulusFile],self.sequencelist[self.trial][self.seqNcommissionErrorCode]]
                                                
                                if (feedbacktoshow[1] != 'nan'): # if there is a stimulus to show
                                    if (int(feedbacktoshow[0]) == int(2)): # if it is an audio file
                                        self.taskaudioparticipant[int(feedbacktoshow[1])].play() # Play audio                       
                                        self.sendtrigger(feedbacktoshow[2]) # Send trigger
                                        self.feedbackontime = self.cumulativeTime.getTime()
                                        self.updateexperimentermarker(feedbacktoshow[2],self.feedbackontime)
                                        
                                    elif (int(feedbacktoshow[0]) == int(1)): # if it is a movie file
                                        self.taskmovieparticipant[int(feedbacktoshow[1])].setAutoDraw(True) # Start showing stimulus
                                        if self.expdisp:
                                            self.taskmovieexperimenter[int(feedbacktoshow[1])].setAutoDraw(True) # Start showing stimulus
                                        self.participantwin.flip(); self.sendtrigger(feedbacktoshow[2]) # Send trigger
                                        if self.expdisp:
                                            self.experimenterwin.flip()
                                        self.feedbackontime = self.cumulativeTime.getTime()
                                        self.updateexperimentermarker(feedbacktoshow[2],self.feedbackontime)
                                        self.continuetrial = True
                                        while (self.taskmovieparticipant[int(feedbacktoshow[1])].status != visual.FINISHED) and self.continuetrial:
                    
                                            # Flip frames
                                            self.participantwin.flip();
                                            if self.expdisp:
                                                self.experimenterwin.flip()
                    
                                            # To avoid tying RT to the monitor refresh rate, this loops for most of the refresh rate period
                                            checkkeytimer = core.CountdownTimer(start=(float(numpy.multiply(float(0.8),float(self.refreshrate)))))
                                            while (checkkeytimer.getTime() > 0) and (self.taskmovieparticipant[int(feedbacktoshow[1])].status != visual.FINISHED) and (self.continuetrial):
                                                    
                                                if event.getKeys(["escape", "q"]): # see if someone is trying to quit
                                                    self.quit = True
                                                    break
                                                    
                                                # Determine if a key has been pressed
                                                theseKeys = event.getKeys(keyList=self.participantkeys, timeStamped=self.cumulativeTime)
                                                if (len(theseKeys) > 0): #at least one key was pressed
                                                    t = (theseKeys[0][1]-self.cumulstimOnTime)
                                                    gt = theseKeys[0][1]
                                                    if self.triggers:
                                                        if self.markfirstresponseonly and (len(self.feedbackresparray[self.trial]) > 0):
                                                            self.feedbackresparray[self.trial].append([self.trial, theseKeys[0][0], ("%.3f" % (numpy.round((t)*1000,3))), ("%.6f" % (numpy.round(gt,6))), 0])
                                                        else:
                                                            self.sendtrigger(theseKeys[0][0])
                                                            self.feedbackresparray[self.trial].append([self.trial, theseKeys[0][0], ("%.3f" % (numpy.round((t)*1000,3))), ("%.6f" % (numpy.round(gt,6))), 1])
                                                    else:
                                                        self.feedbackresparray[self.trial].append([self.trial, theseKeys[0][0], ("%.3f" % (numpy.round((t)*1000,3))), ("%.6f" % (numpy.round(gt,6))), 0])
                                                    if (int(self.sequencelist[self.trial][self.seqNendFeedbackWithResponse]) == int(1)):
                                                        self.continuetrial = False
                                                    self.updateexperimentermarker(theseKeys[0][0],gt)
                                                    event.clearEvents()
                    
                                        # Once the movie has finished                                          
                                        self.taskmovieparticipant[int(feedbacktoshow[1])].setAutoDraw(False) # Stop showing stimulus
                                        self.participantwin.flip()
                                        if self.expdisp:
                                            self.taskmovieexperimenter[int(feedbacktoshow[1])].setAutoDraw(False) # Stop showing stimulus
                                            self.experimenterwin.flip()
                                                
                                    elif (int(feedbacktoshow[0]) == int(0)): # if it is an image file
                                        
                                        self.taskstimuliparticipant[int(feedbacktoshow[1])].setAutoDraw(True) # Start showing stimulus
                                        if self.expdisp:
                                            self.taskstimuliexperimenter[int(feedbacktoshow[1])].setAutoDraw(True) # Start showing stimulus
                                        self.participantwin.flip(); self.sendtrigger(feedbacktoshow[2]) # Send trigger
                                        if self.expdisp:
                                            self.experimenterwin.flip()
                                        self.feedbackontime = self.cumulativeTime.getTime()
                                        self.updateexperimentermarker(feedbacktoshow[2],self.feedbackontime)
                    
                                        self.continuetrial = True
                                        feedbackTimer = core.CountdownTimer(float(self.sequencelist[self.trial][self.seqNfeedbackDuration])) # Sets to run for duration period
                                        while (feedbackTimer.getTime() > 0) and self.continuetrial:
                                                
                                            # Flip frames
                                            self.participantwin.flip();
                                            if self.expdisp:
                                                self.experimenterwin.flip()
                    
                                            # To avoid tying RT to the monitor refresh rate, this loops for most of the refresh rate period
                                            event.clearEvents()
                                            checkkeytimer = core.CountdownTimer(start=(float(numpy.multiply(float(0.8),float(self.refreshrate)))))
                                            while checkkeytimer.getTime() > 0 and self.continuetrial:
                                                    
                                                if event.getKeys(["escape", "q"]): # see if someone is trying to quit
                                                    self.quit = True
                                                    self.continuetrial = False
                                                    break
                                                    
                                                # Determine if a key has been pressed
                                                theseKeys = event.getKeys(keyList=self.participantkeys, timeStamped=self.cumulativeTime)
                                                if (len(theseKeys) > 0): #at least one key was pressed
                                                    t = (theseKeys[0][1]-self.cumulstimOnTime)
                                                    gt = theseKeys[0][1]
                                                    if self.triggers:
                                                        if self.markfirstresponseonly and (len(self.feedbackresparray[self.trial]) > 0):
                                                            self.feedbackresparray[self.trial].append([self.trial, theseKeys[0][0], ("%.3f" % (numpy.round((t)*1000,3))), ("%.6f" % (numpy.round(gt,6))), 0])
                                                        else:
                                                            self.sendtrigger(theseKeys[0][0])
                                                            self.feedbackresparray[self.trial].append([self.trial, theseKeys[0][0], ("%.3f" % (numpy.round((t)*1000,3))), ("%.6f" % (numpy.round(gt,6))), 1])
                                                    else:
                                                        self.feedbackresparray[self.trial].append([self.trial, theseKeys[0][0], ("%.3f" % (numpy.round((t)*1000,3))), ("%.6f" % (numpy.round(gt,6))), 0])
                                                    if (int(self.sequencelist[self.trial][self.seqNendFeedbackWithResponse]) == int(1)):
                                                        self.continuetrial = False
                                                    self.updateexperimentermarker(theseKeys[0][0],gt)
                                                    event.clearEvents()
                    
                                        # Once the duration has finished                                          
                                        self.taskstimuliparticipant[int(feedbacktoshow[1])].setAutoDraw(False) # Stop showing stimulus
                                        self.participantwin.flip()
                                        if self.expdisp:
                                            self.taskstimuliexperimenter[int(feedbacktoshow[1])].setAutoDraw(False) # Stop showing stimulus
                                            self.experimenterwin.flip()
                    
                                    # Load tracking information
                                    self.feedbackarray[self.trial][0] = self.trial # Trial
                                    self.feedbackarray[self.trial][1] = feedbacktoshow[2] # Type
                                    self.feedbackarray[self.trial][2] = ("%.6f" % (numpy.round(self.feedbackontime,6))) # CumulativeStim
                                    if self.triggers:
                                        self.feedbackarray[self.trial][3] = 1
                                    else:
                                        self.feedbackarray[self.trial][3] = 0
                                        
                                    if (int(feedbacktoshow[0]) == int(0)): # if it is an image file
                                        self.feedbackarray[self.trial][4] = self.individualimagelist[int(feedbacktoshow[1])] # Stimulus
                                    elif (int(feedbacktoshow[0]) == int(1)): # if it is a movie file
                                        self.feedbackarray[self.trial][4] = self.fullmovielist[int(feedbacktoshow[1])] # Stimulus
                                    elif (int(feedbacktoshow[0]) == int(2)): # if it is an audio file
                                        self.feedbackarray[self.trial][4] = self.individualaudiolist[int(feedbacktoshow[1])] # Stimulus


                            #####  Finish up trial #####
                            
                            if (len(self.unicorn) > 0):        
                                try:
                                    self.UnicornBlack.safe_to_log(True) # allow file write
                                except:
                                    bolerr = 1
                                    
                            # Determine how much time remains before the next stimulus
                            if numpy.equal(self.sequencelist[self.trial][self.seqNpreStimulusInterval],0):
                                timeRemain = 0;
                                if not numpy.equal(float(self.sequencelist[self.trial][self.seqNpostResponseInterval]), 0.0): # ISI control
                                    
                                    isiRemain = numpy.subtract(float(self.sequencelist[self.trial][self.seqNpostResponseInterval]),numpy.subtract(self.elapsedTime.getTime(),self.stimOffTime))
                                    if (isiRemain > 0):
                                        timeRemain = isiRemain # Gap between the end of the response (or response window) and the onset of the next stimuli
                    
                                elif not numpy.equal(float(self.sequencelist[self.trial][self.seqNstimulusITI]),0.0): # ITI control
                                    
                                    itiRemain = numpy.subtract(float(self.sequencelist[self.trial][self.seqNstimulusITI]),self.elapsedTime.getTime())
                                    if (itiRemain > 0):
                                        timeRemain = itiRemain # Gap between the now and the onset of the next stimuli
                    
                                event.clearEvents()
                                routineTimer = core.CountdownTimer(float(timeRemain)) # Sets to run for time remaining
                                while routineTimer.getTime() > 0:
                    
                                    # Flip frames
                                    self.participantwin.flip();
                                    if self.expdisp:
                                        self.experimenterwin.flip()
                    
                                    # To avoid tying RT to the monitor refresh rate, this loops for most of the refresh rate period
                                    checkkeytimer = core.CountdownTimer(start=(float(numpy.multiply(float(0.8),float(self.refreshrate)))))
                                    while (checkkeytimer.getTime() > 0) and (routineTimer.getTime() > 0):
                                        
                                        # Determine if a key has been pressed
                                        theseKeys = event.getKeys(keyList=self.participantkeys, timeStamped=self.cumulativeTime)
                                        if (len(theseKeys) > 0): #at least one key was pressed
                                            t = (theseKeys[0][1]-self.cumulstimOnTime)
                                            gt = theseKeys[0][1]
                                            if self.triggers:
                                                if self.markfirstresponseonly and (len(self.feedbackresparray[self.trial]) > 0):
                                                    self.feedbackresparray[self.trial].append([self.trial, theseKeys[0][0], ("%.3f" % (numpy.round((t)*1000,3))), ("%.6f" % (numpy.round(gt,6))), 0])
                                                else:
                                                    self.sendtrigger(theseKeys[0][0])
                                                    self.feedbackresparray[self.trial].append([self.trial, theseKeys[0][0], ("%.3f" % (numpy.round((t)*1000,3))), ("%.6f" % (numpy.round(gt,6))), 1])
                                            else:
                                                self.feedbackresparray[self.trial].append([self.trial, theseKeys[0][0], ("%.3f" % (numpy.round((t)*1000,3))), ("%.6f" % (numpy.round(gt,6))), 0])
                                            self.updateexperimentermarker(theseKeys[0][0],gt)
                                            event.clearEvents()
                    
                                        if event.getKeys(["escape", "q"]):
                                            self.quit = True
                                            break
                            
                        else:
                            break
                
                    if not self.quit:
                        # Finish ISI and ITI calculations and Write to File
                        self.specarray[self.trial-1][2] = ("%.3f" % (numpy.round(numpy.float(self.specarray[self.trial-1][3])-(numpy.float(self.specarray[self.trial-1][15])*1000)+(numpy.float(self.specarray[self.trial][14])*1000),3)))
                        self.specarray[self.trial][3] = ('%.3f' % (numpy.round((self.elapsedTime.getTime()*1000),3)))
                        self.specarray[self.trial][2] = ('%.3f' % (numpy.round(numpy.float(self.specarray[self.trial][3])-(numpy.float(self.specarray[self.trial][15])*1000),3)))
        
                    taskruntime = '%.6f' % (self.cumulativeTime.getTime())
                    self.exporttrackingdata(trial = (self.trial-1))
                    self.exporttrackingdata(trial = (self.trial))
                    f = open(self.outputfile, 'a')
                    f.write('taskruntime.= ')
                    f.write(taskruntime)
                    f.write(' sec\n')
                    f.close()
                
                
                # End of Task
                if not self.quit:
                    self.finished = True
                if self.debug:
                    print('Stimulus Events')
                    for incX in range(0,len(self.specarray)):
                        print(self.specarray[incX])
                    print('Response Events')
                    for incX in range(0,len(self.resparray)):
                        print(self.resparray[incX])

                if (self.sequencelistL > 0):
                    # Make sure the last stimulus is cleared
                    if self.sequencelist[self.trial][self.seqNstimulustype] == '0': # if the stimulus type is an image
                        self.taskstimuliparticipant[int(self.sequencelist[self.trial][self.seqNstimulusFile])].setAutoDraw(False) # stop showing mask
                        if self.expdisp:
                            self.taskstimuliexperimenter[int(self.sequencelist[self.trial][self.seqNstimulusFile])].setAutoDraw(False) # stop showing mask
                    if self.sequencelist[self.trial][self.seqNstimulustype] == '1': # if the stimulus type is a movie
                        self.taskmovieparticipant[int(self.sequencelist[self.trial][self.seqNstimulusFile])].setAutoDraw(False) # stop showing mask
                        if self.expdisp:
                            self.taskmovieexperimenter[int(self.sequencelist[self.trial][self.seqNstimulusFile])].setAutoDraw(False) # stop showing mask
        
                    # Make sure the frame masks are cleared
                    if (self.sequencelist[self.trial][self.seqNmask] != '0'):
                        self.taskstimuliparticipant[int(self.sequencelist[self.trial][self.seqNmask])].setAutoDraw(False) # stop showing mask
                        if self.expdisp:
                            self.taskstimuliexperimenter[int(self.sequencelist[self.trial][self.seqNmask])].setAutoDraw(False) # stop showing mask 
                
                   
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

    def importsequencefile(self):

        if self.sequence != []:
            
            if self.expdisp:
                self.experimenternotificationtext.setText('importing sequence file...'); self.experimenterwin.flip()
                
            # Import Sequence Information
            self.sequencelist = []
            
            with open(os.path.join(self.folders.sequencefolder, self.sequence), 'rU') as csvfile:
                 spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
                 for row in spamreader:
                    tempstring = row[0]
                    templist = tempstring.split(',')
                    if (templist[1] != ''):
                        self.sequencelist.append(templist)
            self.sequencelistL = len(self.sequencelist)
            

            # Identifies Location of Necessary Information
            seqHeaders = self.sequencelist[0]
            seqHeadersL = len(seqHeaders)
            
            self.seqNstimulusFile = seqHeaders.index('stimulusFile')
            self.seqNstimulusDuration = seqHeaders.index('stimulusDuration')
            self.seqNresponseWindow_min = seqHeaders.index('responseWindow_min')
            self.seqNresponseWindow_max = seqHeaders.index('responseWindow_max')
            self.seqNstimulusITI = seqHeaders.index('stimulusITI')
            self.seqNstimulusXcoord = seqHeaders.index('stimulusXcoord')
            self.seqNstimulusYcoord = seqHeaders.index('stimulusYcoord')
            self.seqNcorrectResp = seqHeaders.index('correctResp')
            self.seqNstimulusCode = seqHeaders.index('stimulusCode')
            
            try:
                self.seqNstimulusDuration_min = seqHeaders.index('stimulusDuration_min')
            except:
                self.seqNstimulusDuration_min = seqHeadersL
                seqHeadersL = seqHeadersL + 1
                for n in range(1,self.sequencelistL):
                    self.sequencelist[n].append(self.sequencelist[n][self.seqNresponseWindow_min]) # Populate with Minimum Response Window
            try:
                self.seqNpreStimulusInterval = seqHeaders.index('preStimulusInterval')
            except:
                self.seqNpreStimulusInterval = seqHeadersL
                seqHeadersL = seqHeadersL + 1
                for n in range(1,self.sequencelistL):
                    self.sequencelist[n].append('0') # Populate with Zeros
            try:
                self.seqNpostResponseInterval = seqHeaders.index('postResponseInterval')
            except:
                self.seqNpostResponseInterval = seqHeadersL
                seqHeadersL = seqHeadersL + 1
                for n in range(1,self.sequencelistL):
                    self.sequencelist[n].append('0') # Populate with Zeros
            try:
                self.seqNmask = seqHeaders.index('maskFile')
            except:
                self.seqNmask = seqHeadersL
                seqHeadersL = seqHeadersL + 1
                for n in range(1,self.sequencelistL):
                    self.sequencelist[n].append('0') # Populate with Zeros
                    
            try:
                self.seqNfeedbackDuration = seqHeaders.index('feedbackDuration')
            except:
                self.seqNfeedbackDuration = seqHeadersL
                seqHeadersL = seqHeadersL + 1
                for n in range(1,self.sequencelistL):
                    self.sequencelist[n].append('0') # Populate with Zeros
            try:
                self.seqNpreFeedbackDelay = seqHeaders.index('preFeedbackDelay')
            except:
                self.seqNpreFeedbackDelay = seqHeadersL
                seqHeadersL = seqHeadersL + 1
                for n in range(1,self.sequencelistL):
                    self.sequencelist[n].append('0') # Populate with Zeros
            try:
                self.seqNendFeedbackWithResponse = seqHeaders.index('endFeedbackWithResponse')
            except:
                self.seqNendFeedbackWithResponse = seqHeadersL
                seqHeadersL = seqHeadersL + 1
                for n in range(1,self.sequencelistL):
                    self.sequencelist[n].append('0') # Populate with Zeros
            try:
                self.seqNcorrectResponseStimulusFile = seqHeaders.index('correctResponseStimulusFile')
            except:
                self.seqNcorrectResponseStimulusFile = seqHeadersL
                seqHeadersL = seqHeadersL + 1
                for n in range(1,self.sequencelistL):
                    self.sequencelist[n].append('0') # Populate with Zeros
            try:
                self.seqNcorrectResponseCode = seqHeaders.index('correctResponseCode')
            except:
                self.seqNcorrectResponseCode = seqHeadersL
                seqHeadersL = seqHeadersL + 1
                for n in range(1,self.sequencelistL):
                    self.sequencelist[n].append('0') # Populate with Zeros
            try:
                self.seqNcommissionErrorStimulusFile = seqHeaders.index('commissionErrorStimulusFile')
            except:
                self.seqNcommissionErrorStimulusFile = seqHeadersL
                seqHeadersL = seqHeadersL + 1
                for n in range(1,self.sequencelistL):
                    self.sequencelist[n].append('0') # Populate with Zeros
            try:
                self.seqNcommissionErrorCode = seqHeaders.index('commissionErrorCode')
            except:
                self.seqNcommissionErrorCode = seqHeadersL
                seqHeadersL = seqHeadersL + 1
                for n in range(1,self.sequencelistL):
                    self.sequencelist[n].append('0') # Populate with Zeros
            try:
                self.seqNomissionErrorStimulusFile = seqHeaders.index('omissionErrorStimulusFile')
            except:
                self.seqNomissionErrorStimulusFile = seqHeadersL
                seqHeadersL = seqHeadersL + 1
                for n in range(1,self.sequencelistL):
                    self.sequencelist[n].append('0') # Populate with Zeros
            try:
                self.seqNomissionErrorCode = seqHeaders.index('omissionErrorCode')
            except:
                self.seqNomissionErrorCode = seqHeadersL
                seqHeadersL = seqHeadersL + 1
                for n in range(1,self.sequencelistL):
                    self.sequencelist[n].append('0') # Populate with Zeros
            try:
                self.seqNimpulsiveErrorStimulusFile = seqHeaders.index('impulsiveErrorStimulusFile')
            except:
                self.seqNimpulsiveErrorStimulusFile = seqHeadersL
                seqHeadersL = seqHeadersL + 1
                for n in range(1,self.sequencelistL):
                    self.sequencelist[n].append('0') # Populate with Zeros
            try:
                self.seqNimpulsiveErrorCode = seqHeaders.index('impulsiveErrorCode')
            except:
                self.seqNimpulsiveErrorCode = seqHeadersL
                seqHeadersL = seqHeadersL + 1
                for n in range(1,self.sequencelistL):
                    self.sequencelist[n].append('0') # Populate with Zeros
            try:
                self.seqNdelayErrorStimulusFile = seqHeaders.index('delayErrorStimulusFile')
            except:
                self.seqNdelayErrorStimulusFile = seqHeadersL
                seqHeadersL = seqHeadersL + 1
                for n in range(1,self.sequencelistL):
                    self.sequencelist[n].append('0') # Populate with Zeros
            try:
                self.seqNdelayErrorCode = seqHeaders.index('delayErrorCode')
            except:
                self.seqNdelayErrorCode = seqHeadersL
                seqHeadersL = seqHeadersL + 1
                for n in range(1,self.sequencelistL):
                    self.sequencelist[n].append('0') # Populate with Zeros
            

            image_file_types = ['.gif', '.png', '.jpg', '.bmp', '.tiff', '.jpeg', '.pbm', '.pgm', '.ppm', '.rast', '.xbm', '.rgb']
            movie_file_types = ['.mov', '.wmv', '.mp4']
            audio_file_types = ['.wav', '.mp3', '.3gp', '.m4a', '.wma']
            # Determine stimulus types
            self.seqNstimulustype = seqHeadersL
            seqHeadersL = seqHeadersL + 1
            self.sequencelist[0].append('stimulustype')
            for n in range(1,self.sequencelistL):
                self.sequencelist[n].append('0') # Assume an image
            for n in range(1,self.sequencelistL):
                if self.sequencelist[n][self.seqNstimulusFile].endswith(tuple(image_file_types)): # Check if image
                    self.sequencelist[n][self.seqNstimulustype] = '0'
                elif self.sequencelist[n][self.seqNstimulusFile].endswith(tuple(movie_file_types)): # Check if movie
                    self.sequencelist[n][self.seqNstimulustype] = '1'
                elif self.sequencelist[n][self.seqNstimulusFile].endswith(tuple(audio_file_types)): # Check if audio
                    self.sequencelist[n][self.seqNstimulustype] = '2'            


            # Determine stimulus types for feedback
            self.seqNcorrectResponseStimulustype = seqHeadersL
            seqHeadersL = seqHeadersL + 1
            self.sequencelist[0].append('correctResponseStimulustype')
            for n in range(1,self.sequencelistL):
                self.sequencelist[n].append([])
            for n in range(1,self.sequencelistL):
                if self.sequencelist[n][self.seqNcorrectResponseStimulusFile].endswith(tuple(image_file_types)): # Check if image
                    self.sequencelist[n][self.seqNcorrectResponseStimulustype] = '0'
                elif self.sequencelist[n][self.seqNcorrectResponseStimulusFile].endswith(tuple(movie_file_types)): # Check if movie
                    self.sequencelist[n][self.seqNcorrectResponseStimulustype] = '1'
                elif self.sequencelist[n][self.seqNcorrectResponseStimulusFile].endswith(tuple(audio_file_types)): # Check if audio
                    self.sequencelist[n][self.seqNcorrectResponseStimulustype] = '2'
                    
            # Determine stimulus types for feedback
            self.seqNcommissionErrorStimulustype = seqHeadersL
            seqHeadersL = seqHeadersL + 1
            self.sequencelist[0].append('commissionErrorStimulustype')
            for n in range(1,self.sequencelistL):
                self.sequencelist[n].append([])
            for n in range(1,self.sequencelistL):
                if self.sequencelist[n][self.seqNcommissionErrorStimulusFile].endswith(tuple(image_file_types)): # Check if image
                    self.sequencelist[n][self.seqNcommissionErrorStimulustype] = '0'
                elif self.sequencelist[n][self.seqNcommissionErrorStimulusFile].endswith(tuple(movie_file_types)): # Check if movie
                    self.sequencelist[n][self.seqNcommissionErrorStimulustype] = '1'
                elif self.sequencelist[n][self.seqNcommissionErrorStimulusFile].endswith(tuple(audio_file_types)): # Check if audio
                    self.sequencelist[n][self.seqNcommissionErrorStimulustype] = '2'
                    
            self.seqNomissionErrorStimulustype = seqHeadersL
            seqHeadersL = seqHeadersL + 1
            self.sequencelist[0].append('omissionErrorStimulustype')
            for n in range(1,self.sequencelistL):
                self.sequencelist[n].append([])
            for n in range(1,self.sequencelistL):
                if self.sequencelist[n][self.seqNomissionErrorStimulusFile].endswith(tuple(image_file_types)): # Check if image
                    self.sequencelist[n][self.seqNomissionErrorStimulustype] = '0'
                elif self.sequencelist[n][self.seqNomissionErrorStimulusFile].endswith(tuple(movie_file_types)): # Check if movie
                    self.sequencelist[n][self.seqNomissionErrorStimulustype] = '1'
                elif self.sequencelist[n][self.seqNomissionErrorStimulusFile].endswith(tuple(audio_file_types)): # Check if audio
                    self.sequencelist[n][self.seqNomissionErrorStimulustype] = '2' 
                    
            self.seqNimpulsiveErrorStimulustype = seqHeadersL
            seqHeadersL = seqHeadersL + 1
            self.sequencelist[0].append('impulsiveErrorStimulustype')
            for n in range(1,self.sequencelistL):
                self.sequencelist[n].append([])
            for n in range(1,self.sequencelistL):
                if self.sequencelist[n][self.seqNimpulsiveErrorStimulusFile].endswith(tuple(image_file_types)): # Check if image
                    self.sequencelist[n][self.seqNimpulsiveErrorStimulustype] = '0'
                elif self.sequencelist[n][self.seqNimpulsiveErrorStimulusFile].endswith(tuple(movie_file_types)): # Check if movie
                    self.sequencelist[n][self.seqNimpulsiveErrorStimulustype] = '1'
                elif self.sequencelist[n][self.seqNimpulsiveErrorStimulusFile].endswith(tuple(audio_file_types)): # Check if audio
                    self.sequencelist[n][self.seqNimpulsiveErrorStimulustype] = '2' 
                    
            self.seqNdelayErrorStimulustype = seqHeadersL
            seqHeadersL = seqHeadersL + 1
            self.sequencelist[0].append('delayErrorStimulustype')
            for n in range(1,self.sequencelistL):
                self.sequencelist[n].append([])
            for n in range(1,self.sequencelistL):
                if self.sequencelist[n][self.seqNdelayErrorStimulusFile].endswith(tuple(image_file_types)): # Check if image
                    self.sequencelist[n][self.seqNdelayErrorStimulustype] = '0'
                elif self.sequencelist[n][self.seqNdelayErrorStimulusFile].endswith(tuple(movie_file_types)): # Check if movie
                    self.sequencelist[n][self.seqNdelayErrorStimulustype] = '1'
                elif self.sequencelist[n][self.seqNdelayErrorStimulusFile].endswith(tuple(audio_file_types)): # Check if audio
                    self.sequencelist[n][self.seqNdelayErrorStimulustype] = '2' 

            self.sequencelist = numpy.array(self.sequencelist)
            for n in range(1,self.sequencelistL):
                
                # Typecast numbers and Convert
                if (self.sequencelist[n][self.seqNstimulusDuration] != '0'):
                    self.sequencelist[n][self.seqNstimulusDuration] = float(numpy.true_divide(float(self.sequencelist[n][self.seqNstimulusDuration]),1000))-float(self.refreshrate)
                else:
                    self.sequencelist[n][self.seqNstimulusDuration] = float(numpy.float(0))
                
                if (self.sequencelist[n][self.seqNstimulusDuration_min] != '0'):
                    self.sequencelist[n][self.seqNstimulusDuration_min] = float(numpy.true_divide(float(self.sequencelist[n][self.seqNstimulusDuration_min]),1000))-float(self.refreshrate)
                else:
                    self.sequencelist[n][self.seqNstimulusDuration_min] = float(numpy.float(0))

                if (self.sequencelist[n][self.seqNresponseWindow_min] != '0'):
                    self.sequencelist[n][self.seqNresponseWindow_min] = float(numpy.true_divide(float(self.sequencelist[n][self.seqNresponseWindow_min]),1000))-float(self.refreshrate)
                else:
                    self.sequencelist[n][self.seqNresponseWindow_min] = float(numpy.float(0))
                    
                if (self.sequencelist[n][self.seqNresponseWindow_max] != '0'):
                    self.sequencelist[n][self.seqNresponseWindow_max] = float(numpy.true_divide(float(self.sequencelist[n][self.seqNresponseWindow_max]),1000))+float(self.refreshrate)
                else:
                    self.sequencelist[n][self.seqNresponseWindow_max] = float(numpy.float(0))

                if (self.sequencelist[n][self.seqNstimulusITI] != '0'):
                    self.sequencelist[n][self.seqNstimulusITI] = float(numpy.true_divide(float(self.sequencelist[n][self.seqNstimulusITI]),1000))-float(self.refreshrate)
                else:
                    self.sequencelist[n][self.seqNstimulusITI] = float(numpy.float(0))

                if (self.sequencelist[n][self.seqNpreStimulusInterval] != '0'):
                    self.sequencelist[n][self.seqNpreStimulusInterval] = float(numpy.true_divide(float(self.sequencelist[n][self.seqNpreStimulusInterval]),1000))-float(self.refreshrate)
                else:
                    self.sequencelist[n][self.seqNpreStimulusInterval] = float(numpy.float(0))

                if (self.sequencelist[n][self.seqNpostResponseInterval] != '0'):
                    self.sequencelist[n][self.seqNpostResponseInterval] = float(numpy.true_divide(float(self.sequencelist[n][self.seqNpostResponseInterval]),1000))-float(self.refreshrate)
                else:
                    self.sequencelist[n][self.seqNpostResponseInterval] = float(numpy.float(0))

                self.sequencelist[n][self.seqNstimulusXcoord] = float(self.sequencelist[n][self.seqNstimulusXcoord])
                self.sequencelist[n][self.seqNstimulusYcoord] = float(self.sequencelist[n][self.seqNstimulusYcoord])
                self.sequencelist[n][self.seqNstimulusCode] = int(self.sequencelist[n][self.seqNstimulusCode])
                
                if (self.sequencelist[n][self.seqNfeedbackDuration] != '0'):
                    self.sequencelist[n][self.seqNfeedbackDuration] = float(numpy.true_divide(float(self.sequencelist[n][self.seqNfeedbackDuration]),1000))+float(self.refreshrate)
                else:
                    self.sequencelist[n][self.seqNfeedbackDuration] = float(numpy.float(0))
                    
                if (self.sequencelist[n][self.seqNpreFeedbackDelay] != '0'):
                    self.sequencelist[n][self.seqNpreFeedbackDelay] = float(numpy.true_divide(float(self.sequencelist[n][self.seqNpreFeedbackDelay]),1000))-float(self.refreshrate)
                else:
                    self.sequencelist[n][self.seqNpreFeedbackDelay] = float(numpy.float(0))

                self.sequencelist[n][self.seqNendFeedbackWithResponse] = int(self.sequencelist[n][self.seqNendFeedbackWithResponse])
                self.sequencelist[n][self.seqNcorrectResponseCode] = int(self.sequencelist[n][self.seqNcorrectResponseCode])
                self.sequencelist[n][self.seqNcommissionErrorCode] = int(self.sequencelist[n][self.seqNcommissionErrorCode])
                self.sequencelist[n][self.seqNomissionErrorCode] = int(self.sequencelist[n][self.seqNomissionErrorCode])
                self.sequencelist[n][self.seqNimpulsiveErrorCode] = int(self.sequencelist[n][self.seqNimpulsiveErrorCode])
                self.sequencelist[n][self.seqNdelayErrorCode] = int(self.sequencelist[n][self.seqNdelayErrorCode])
                
                # Perform parameter checks
                if (self.sequencelist[n][self.seqNstimulusDuration_min] > self.sequencelist[n][self.seqNstimulusDuration]):
                    self.sequencelist[n][self.seqNstimulusDuration_min] = self.sequencelist[n][self.seqNstimulusDuration] # minimum Stim duration cannot be longer than Stim Duration
                
                if (float(numpy.float(self.sequencelist[n][self.seqNstimulusITI])) != numpy.float(0)): # If ITI is enabled
                    if (self.sequencelist[n][self.seqNstimulusDuration] > self.sequencelist[n][self.seqNstimulusITI]):
                        self.sequencelist[n][self.seqNstimulusDuration] = self.sequencelist[n][self.seqNstimulusITI] # Stimulus duration cannot be longer than ITI
                    if (self.sequencelist[n][self.seqNresponseWindow_max] > self.sequencelist[n][self.seqNstimulusITI]):
                        self.sequencelist[n][self.seqNresponseWindow_max] = self.sequencelist[n][self.seqNstimulusITI] # Response window cannot be longer than ITI
                 
                if (float(numpy.float(self.sequencelist[n][self.seqNpostResponseInterval])) != float(numpy.float(0))):
                    self.sequencelist[n][self.seqNstimulusITI] = float(numpy.float(0)) # If postResponseInterval is enabled, Turn off ITI
                    
                if (float(numpy.float(self.sequencelist[n][self.seqNpreStimulusInterval])) != float(numpy.float(0))): # If preStimulusInterval is enabled
                    self.sequencelist[n][self.seqNstimulusDuration] = float(self.sequencelist[n][self.seqNstimulusDuration])+float(self.sequencelist[n][self.seqNpreStimulusInterval]) # Shift stim duration
                    self.sequencelist[n][self.seqNstimulusDuration_min] = float(self.sequencelist[n][self.seqNstimulusDuration_min]) + float(self.sequencelist[n][self.seqNpreStimulusInterval]) # Shift stim duration min
                    self.sequencelist[n][self.seqNresponseWindow_min] = float(self.sequencelist[n][self.seqNresponseWindow_min]) + float(self.sequencelist[n][self.seqNpreStimulusInterval]) # Shift response window min
                    self.sequencelist[n][self.seqNresponseWindow_max] = float(self.sequencelist[n][self.seqNresponseWindow_max]) + float(self.sequencelist[n][self.seqNpreStimulusInterval]) # Shift response window max
                    self.sequencelist[n][self.seqNpostResponseInterval] = float(numpy.float(0)) # If preStimulusInterval is enabled, Turn off postResponseInterval
                    self.sequencelist[n][self.seqNstimulusITI] = float(numpy.float(0)) # If preStimulusInterval is enabled, Turn off stimulusITI
                else:
                    self.sequencelist[n][self.seqNpreStimulusInterval] = float(numpy.float(0))
            
            self.sequenceready = True
            if self.expdisp:
                self.experimenternotificationtext.setText('sequence file loaded...'); self.experimenterwin.flip()
            
            self.preloadstimuli()
            
    def preloadstimuli(self):
        
        if self.expdisp:
            self.experimenternotificationtext.setText('preloading stimuli...'); self.experimenterwin.flip()

        # Computes how many unique stimuli are being used in the sequence file
        fullimagelist = []
        self.fullmovielist = []
        fullaudiolist = []
        for n in range(1,self.sequencelistL):
            if self.sequencelist[n][self.seqNstimulustype] == '0': # if the stimulus type is an image
                fullimagelist.append(self.sequencelist[n][self.seqNstimulusFile]) # Add all images to a list
            elif self.sequencelist[n][self.seqNstimulustype] == '1': # if the stimulus type is a movie
                self.fullmovielist.append(self.sequencelist[n][self.seqNstimulusFile]) # Add all movies to a list
            elif self.sequencelist[n][self.seqNstimulustype] == '2': # if the stimulus type is audio
                fullaudiolist.append(self.sequencelist[n][self.seqNstimulusFile]) # Add all audio to a list
            if (self.sequencelist[n][self.seqNmask] != '0'):
                fullimagelist.append(self.sequencelist[n][self.seqNmask]) # Add all mask images to a list
            
            if (self.sequencelist[n][self.seqNcorrectResponseStimulusFile] != '0'):
                if self.sequencelist[n][self.seqNcorrectResponseStimulustype] == '0': # if the stimulus type is an image
                    fullimagelist.append(self.sequencelist[n][self.seqNcorrectResponseStimulusFile]) # Add all images to a list
                elif self.sequencelist[n][self.seqNcorrectResponseStimulustype] == '1': # if the stimulus type is a movie
                    self.fullmovielist.append(self.sequencelist[n][self.seqNcorrectResponseStimulusFile]) # Add all movies to a list
                elif self.sequencelist[n][self.seqNcorrectResponseStimulustype] == '2': # if the stimulus type is audio
                    fullaudiolist.append(self.sequencelist[n][self.seqNcorrectResponseStimulusFile]) # Add all audio to a list
            
            if (self.sequencelist[n][self.seqNcommissionErrorStimulusFile] != '0'):
                if self.sequencelist[n][self.seqNcommissionErrorStimulustype] == '0': # if the stimulus type is an image
                    fullimagelist.append(self.sequencelist[n][self.seqNcommissionErrorStimulusFile]) # Add all images to a list
                elif self.sequencelist[n][self.seqNcommissionErrorStimulustype] == '1': # if the stimulus type is a movie
                    self.fullmovielist.append(self.sequencelist[n][self.seqNcommissionErrorStimulusFile]) # Add all movies to a list
                elif self.sequencelist[n][self.seqNcommissionErrorStimulustype] == '2': # if the stimulus type is audio
                    fullaudiolist.append(self.sequencelist[n][self.seqNcommissionErrorStimulusFile]) # Add all audio to a list
            
            if (self.sequencelist[n][self.seqNomissionErrorStimulusFile] != '0'):
                if self.sequencelist[n][self.seqNomissionErrorStimulustype] == '0': # if the stimulus type is an image
                    fullimagelist.append(self.sequencelist[n][self.seqNomissionErrorStimulusFile]) # Add all images to a list
                elif self.sequencelist[n][self.seqNomissionErrorStimulustype] == '1': # if the stimulus type is a movie
                    self.fullmovielist.append(self.sequencelist[n][self.seqNomissionErrorStimulusFile]) # Add all movies to a list
                elif self.sequencelist[n][self.seqNomissionErrorStimulustype] == '2': # if the stimulus type is audio
                    fullaudiolist.append(self.sequencelist[n][self.seqNomissionErrorStimulusFile]) # Add all audio to a list
            
            if (self.sequencelist[n][self.seqNimpulsiveErrorStimulusFile] != '0'):
                if self.sequencelist[n][self.seqNimpulsiveErrorStimulustype] == '0': # if the stimulus type is an image
                    fullimagelist.append(self.sequencelist[n][self.seqNimpulsiveErrorStimulusFile]) # Add all images to a list
                elif self.sequencelist[n][self.seqNimpulsiveErrorStimulustype] == '1': # if the stimulus type is a movie
                    self.fullmovielist.append(self.sequencelist[n][self.seqNimpulsiveErrorStimulusFile]) # Add all movies to a list
                elif self.sequencelist[n][self.seqNimpulsiveErrorStimulustype] == '2': # if the stimulus type is audio
                    fullaudiolist.append(self.sequencelist[n][self.seqNimpulsiveErrorStimulusFile]) # Add all audio to a list
            
            if (self.sequencelist[n][self.seqNdelayErrorStimulusFile] != '0'):
                if self.sequencelist[n][self.seqNdelayErrorStimulustype] == '0': # if the stimulus type is an image
                    fullimagelist.append(self.sequencelist[n][self.seqNdelayErrorStimulusFile]) # Add all images to a list
                elif self.sequencelist[n][self.seqNdelayErrorStimulustype] == '1': # if the stimulus type is a movie
                    self.fullmovielist.append(self.sequencelist[n][self.seqNdelayErrorStimulusFile]) # Add all movies to a list
                elif self.sequencelist[n][self.seqNdelayErrorStimulustype] == '2': # if the stimulus type is audio
                    fullaudiolist.append(self.sequencelist[n][self.seqNdelayErrorStimulusFile]) # Add all audio to a list

        self.individualimagelist = []
        for tempval in fullimagelist:
            if (self.individualimagelist.count(tempval) == 0):
                self.individualimagelist.append(tempval) # Only add image if it is unique
                
        self.individualaudiolist = []
        for tempval in fullaudiolist:
            if (self.individualaudiolist.count(tempval) == 0):
                self.individualaudiolist.append(tempval) # Only add audio if it is unique
        
        # Preloads images
        if self.individualimagelist: # if there are images in the list
            self.taskstimuliparticipant = [visual.ImageStim(self.participantwin,image=os.path.join(self.folders.stimulusfolder, img), pos = [0.0,0.0], interpolate=False, opacity=1.0, contrast=1.0, autoLog=False) for img in self.individualimagelist]  # preloads the unique images
            if self.expdisp:
                self.taskstimuliexperimenter = [visual.ImageStim(self.experimenterwin,image=os.path.join(self.folders.stimulusfolder, img), pos = [0.0,0.0], interpolate=False, autoLog=False) for img in self.individualimagelist]  # preloads the unique images
            for n in range(1,self.sequencelistL):
                if self.sequencelist[n][self.seqNstimulustype] == '0': # if the stimulus type is an image
                    self.sequencelist[n][self.seqNstimulusFile] = self.individualimagelist.index(self.sequencelist[n][self.seqNstimulusFile]) # replaces the file name with the unique image identifier
                if (self.sequencelist[n][self.seqNcorrectResponseStimulusFile] != '0'):
                    if self.sequencelist[n][self.seqNcorrectResponseStimulustype] == '0': # if the stimulus type is an image
                        self.sequencelist[n][self.seqNcorrectResponseStimulusFile] = self.individualimagelist.index(self.sequencelist[n][self.seqNcorrectResponseStimulusFile]) # replaces the file name with the unique image identifier
                else:
                    self.sequencelist[n][self.seqNcorrectResponseStimulusFile] = '-1'
                if (self.sequencelist[n][self.seqNcommissionErrorStimulusFile] != '0'):
                    if self.sequencelist[n][self.seqNcommissionErrorStimulustype] == '0': # if the stimulus type is an image
                        self.sequencelist[n][self.seqNcommissionErrorStimulusFile] = self.individualimagelist.index(self.sequencelist[n][self.seqNcommissionErrorStimulusFile]) # replaces the file name with the unique image identifier
                else:
                    self.sequencelist[n][self.seqNcommissionErrorStimulusFile] = '-1'
                if (self.sequencelist[n][self.seqNomissionErrorStimulusFile] != '0'):
                    if self.sequencelist[n][self.seqNomissionErrorStimulustype] == '0': # if the stimulus type is an image
                        self.sequencelist[n][self.seqNomissionErrorStimulusFile] = self.individualimagelist.index(self.sequencelist[n][self.seqNomissionErrorStimulusFile]) # replaces the file name with the unique image identifier
                else:
                    self.sequencelist[n][self.seqNomissionErrorStimulusFile] = '-1'
                if (self.sequencelist[n][self.seqNimpulsiveErrorStimulusFile] != '0'):
                    if self.sequencelist[n][self.seqNimpulsiveErrorStimulustype] == '0': # if the stimulus type is an image
                        self.sequencelist[n][self.seqNimpulsiveErrorStimulusFile] = self.individualimagelist.index(self.sequencelist[n][self.seqNimpulsiveErrorStimulusFile]) # replaces the file name with the unique image identifier
                else:
                    self.sequencelist[n][self.seqNimpulsiveErrorStimulusFile]  = '-1'
                if (self.sequencelist[n][self.seqNdelayErrorStimulusFile] != '0'):
                    if self.sequencelist[n][self.seqNdelayErrorStimulustype] == '0': # if the stimulus type is an image
                        self.sequencelist[n][self.seqNdelayErrorStimulusFile] = self.individualimagelist.index(self.sequencelist[n][self.seqNdelayErrorStimulusFile]) # replaces the file name with the unique image identifier
                else:
                    self.sequencelist[n][self.seqNdelayErrorStimulusFile] = '-1'
                if (self.sequencelist[n][self.seqNmask] != '0'):
                    self.sequencelist[n][self.seqNmask] = self.individualimagelist.index(self.sequencelist[n][self.seqNmask])
                else:
                    self.sequencelist[n][self.seqNmask] = '-1'

        # Loads movies
        if self.fullmovielist: # if there are movies in the list --- Note that once a movie has played we cannot reuse it, so just sequentially add movies to a list
            try:
                self.taskmovieparticipant = [visual.MovieStim2(self.participantwin,filename=os.path.join(self.folders.stimulusfolder, img), pos = [0.0,0.0], autoLog=False) for img in self.fullmovielist]  # preloads the unique movies
                if self.expdisp:
                    self.taskmovieexperimenter = [visual.MovieStim2(self.experimenterwin,filename=os.path.join(self.folders.stimulusfolder, img), pos = [0.0,0.0], volume=0, autoLog=False) for img in self.fullmovielist]  # preloads the unique movies
                moviecounter = 0
                for n in range(1,self.sequencelistL):
                    if self.sequencelist[n][self.seqNstimulustype] == '1': # if the stimulus type is a movie
                        self.sequencelist[n][self.seqNstimulusFile] = moviecounter # replaces the file name with the unique movie identifier
                        moviecounter = moviecounter + 1

                        # Adjust stimulus timing to run for the full movie clip
                        self.sequencelist[n][self.seqNstimulusDuration] = float(self.taskmovieparticipant[int(self.sequencelist[n][self.seqNstimulusFile])].duration)+float(self.refreshrate) # set duration to be the movie clip duration
                        if (float(numpy.float(self.sequencelist[n][self.seqNpreStimulusInterval])) != float(numpy.float(0))): # If preStimulusInterval is enabled
                            self.sequencelist[n][self.seqNstimulusDuration] = float(self.sequencelist[n][self.seqNstimulusDuration])+float(self.sequencelist[n][self.seqNpreStimulusInterval]) # Shift stim duration
                        elif (float(numpy.float(self.sequencelist[n][self.seqNstimulusITI])) != numpy.float(0)): # If ITI is enabled
                            if (self.sequencelist[n][self.seqNstimulusDuration] > self.sequencelist[n][self.seqNstimulusITI]):
                                self.sequencelist[n][self.seqNstimulusITI] = self.sequencelist[n][self.seqNstimulusDuration] 
                            if (self.sequencelist[n][self.seqNresponseWindow_max] < self.sequencelist[n][self.seqNstimulusDuration]):
                                self.sequencelist[n][self.seqNresponseWindow_max] = self.sequencelist[n][self.seqNstimulusDuration] 
                        self.sequencelist[n][self.seqNstimulusDuration_min] = self.sequencelist[n][self.seqNstimulusDuration]

                    if (self.sequencelist[n][self.seqNcorrectResponseStimulusFile] != '0'):
                        if self.sequencelist[n][self.seqNcorrectResponseStimulustype] == '1': # if the stimulus type is a movie
                            self.sequencelist[n][self.seqNcorrectResponseStimulusFile] = moviecounter # replaces the file name with the unique movie identifier
                            moviecounter = moviecounter + 1
                    if (self.sequencelist[n][self.seqNcommissionErrorStimulusFile] != '0'):
                        if self.sequencelist[n][self.seqNcommissionErrorStimulustype] == '1': # if the stimulus type is a movie
                            self.sequencelist[n][self.seqNcommissionErrorStimulusFile] = moviecounter # replaces the file name with the unique movie identifier
                            moviecounter = moviecounter + 1
                    if (self.sequencelist[n][self.seqNomissionErrorStimulusFile] != '0'):
                        if self.sequencelist[n][self.seqNomissionErrorStimulustype] == '1': # if the stimulus type is a movie
                            self.sequencelist[n][self.seqNomissionErrorStimulusFile] = moviecounter # replaces the file name with the unique movie identifier
                            moviecounter = moviecounter + 1
                    if (self.sequencelist[n][self.seqNimpulsiveErrorStimulusFile] != '0'):
                        if self.sequencelist[n][self.seqNimpulsiveErrorStimulustype] == '1': # if the stimulus type is a movie
                            self.sequencelist[n][self.seqNimpulsiveErrorStimulusFile] = moviecounter # replaces the file name with the unique movie identifier
                            moviecounter = moviecounter + 1
                    if (self.sequencelist[n][self.seqNdelayErrorStimulusFile] != '0'):
                        if self.sequencelist[n][self.seqNdelayErrorStimulustype] == '1': # if the stimulus type is a movie
                            self.sequencelist[n][self.seqNdelayErrorStimulusFile] = moviecounter # replaces the file name with the unique movie identifier
                            moviecounter = moviecounter + 1                        
            except:
                print('ERROR: This could be because the file name provided does not exist.')
                print('ERROR: To enable movie stimuli you must first download and install VLC media player (http://www.videolan.org/vlc/  32-bit version.')
                
                    
        # Preloads audio
        if self.individualaudiolist: # if there is audio in the list
            try:
                self.taskaudioparticipant = [sound.Sound(os.path.join(self.folders.stimulusfolder, audiostim), autoLog=False) for audiostim in self.individualaudiolist]  # preloads the unique audio
                for n in range(1,self.sequencelistL):
                    if self.sequencelist[n][self.seqNstimulustype] == '2': # if the stimulus type is audio
                        self.sequencelist[n][self.seqNstimulusFile] = self.individualaudiolist.index(self.sequencelist[n][self.seqNstimulusFile]) # replaces the file name with the unique audio identifier
                    if (self.sequencelist[n][self.seqNcorrectResponseStimulusFile] != '0'):
                        if self.sequencelist[n][self.seqNcorrectResponseStimulustype] == '2': # if the stimulus type is audio
                            self.sequencelist[n][self.seqNcorrectResponseStimulusFile] = self.individualaudiolist.index(self.sequencelist[n][self.seqNcorrectResponseStimulusFile]) # replaces the file name with the unique audio identifier
                    else:
                        self.sequencelist[n][self.seqNcorrectResponseStimulusFile]  = '-1'
                    if (self.sequencelist[n][self.seqNcommissionErrorStimulusFile] != '0'):
                        if self.sequencelist[n][self.seqNcommissionErrorStimulustype] == '2': # if the stimulus type is audio
                            self.sequencelist[n][self.seqNcommissionErrorStimulusFile] = self.individualaudiolist.index(self.sequencelist[n][self.seqNcommissionErrorStimulusFile]) # replaces the file name with the unique audio identifier
                    else:
                        self.sequencelist[n][self.seqNcommissionErrorStimulusFile] = '-1'
                    if (self.sequencelist[n][self.seqNomissionErrorStimulusFile] != '0'):
                        if self.sequencelist[n][self.seqNomissionErrorfStimulustype] == '2': # if the stimulus type is audio
                            self.sequencelist[n][self.seqNomissionErrorStimulusFile] = self.individualaudiolist.index(self.sequencelist[n][self.seqNomissionErrorStimulusFile]) # replaces the file name with the unique audio identifier
                    else:
                        self.sequencelist[n][self.seqNomissionErrorStimulusFile] = '-1'
                    if (self.sequencelist[n][self.seqNimpulsiveErrorStimulusFile] != '0'):
                        if self.sequencelist[n][self.seqNimpulsiveErrorStimulustype] == '2': # if the stimulus type is audio
                            self.sequencelist[n][self.seqNimpulsiveErrorStimulusFile] = self.individualaudiolist.index(self.sequencelist[n][self.seqNimpulsiveErrorStimulusFile]) # replaces the file name with the unique audio identifier
                    else:
                        self.sequencelist[n][self.seqNimpulsiveErrorStimulusFile] = '-1'
                    if (self.sequencelist[n][self.seqNdelayErrorStimulusFile] != '0'):
                        if self.sequencelist[n][self.seqNdelayErrorStimulustype] == '2': # if the stimulus type is audio
                            self.sequencelist[n][self.seqNdelayErrorStimulusFile] = self.individualaudiolist.index(self.sequencelist[n][self.seqNdelayErrorStimulusFile]) # replaces the file name with the unique audio identifier
                    else:
                        self.sequencelist[n][self.seqNdelayErrorStimulusFile] = '-1'
            except:
                print('ERROR: This could be because the file name provided does not exist.')
                print('ERROR: To enable audio stimuli you must first download and install Pygame (http://www.pygame.org/download.shtml).')
                print('After running the installer, select the installation folder as: C:\Program Files (x86)\PsychoPy3 or non PC equivalent folder.')
                
            
        if self.expdisp:
            self.experimenternotificationtext.setText('stimuli loaded...'); self.experimenterwin.flip()        
                    
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
    
    
    #from Engine.basicstimuluspresentationengine import Engine
    
    task = Engine()
    task.debug = True
    task.testblock = True
    os.chdir(os.path.dirname(os.getcwd()))
    print(os.getcwd())
    
    # create example sequence file
    f = open(task.folders.sequencefolder + os.path.sep + 'ExampleSequence.csv', 'w')
    f.write('stimulusFile,stimulusDuration,stimulusDuration_min,responseWindow_min,responseWindow_max,stimulusITI,stimulusXcoord,stimulusYcoord,correctResp,stimulusCode\n')
    f.write('RedDot.png,300,100,100,1000,2600,0,0,1,5\n')
    f.write('RedDot.png,300,100,100,1000,2600,0,0,1,5\n')
    f.write('RedDot.png,300,100,100,1000,2600,0,0,1,5\n')
    f.close()
    
    
    task.showinstructions = False
    task.sequence = 'ExampleSequence.csv'
    
    # Filename Prefix and Suffix
    task.prefix = 'AP'
    task.suffix = 'p'
    task.filenametooltip = 'Format: ### Remember to add condition after the ID.'
    task.testblock = True
    
    # Global image frame/mask
    task.permanentframemask = ''
    
    # Usable keys during task
    task.participantkeys = ['1', '4', 'enter']
    
    # Experiment Flow Settings
    task.pauseatstart = False # Only Experimentor can advance to the task after the instructions
    task.delaybeforestart = 3 # Seconds between end of instructions and beginning of task
    task.pauseatend = False
    
    # Parallel Port Triggers
    task.triggers = True
    task.markfirstresponseonly = True
    task.triggerportaddress = '0xD010'# 0xD010 on SynampsRT system  0xD050 on Grael
    task.paralleltriggermodule = False # true if trying to send parallel port triggers
    task.unicorn = 'UN-2019.05.51' # [] if using other system
    task.unicornchannels = 'FZ, C3, CZ, C4, PZ, O1, OZ, O2, AccelX, AccelY, AccelZ, GyroX, GyroY, GyroZ, Battery, Sample'
    
    task.start()
    