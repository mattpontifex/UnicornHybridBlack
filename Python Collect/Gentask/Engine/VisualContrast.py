# -*- coding: utf-8 -*-
"""
Things to consider

Could do:

FC1, FCZ, FC2

CPZ, P1, PZ, P2, POZ


Or could do:
    
FCZ

CP1, CPZ, CP2, P1, PZ, P2, POZ


"""

#https://webvision.med.utah.edu/book/electrophysiology/visually-evoked-potentials/
#The major component of the VEP is the large positive wave peaking at about 100 milliseconds (Fig. 5).
# This “P100” or P1 in the jargon of evoked potentials, is very reliable between individuals and 
# stable from about age 5 years to 60 years. 

#
import time
from psychopy import visual, core, event
import unicornhybridblack as unicornhybridblack

if __name__ == "__main__":
    winsize = (1504, 1003)
    fixationsize = 16
    
    participantwin = visual.Window(size = winsize, fullscr = True, screen = 0, allowGUI = False, allowStencil = False, monitor = 'testMonitor', color = '#000000', colorSpace = 'rgb')
                      
    statustext = visual.TextStim(participantwin, text='Keep your eyes focused on the red dot.', pos=(0.5,0), color='#FFFFFF', height=0.0911, antialias=True, bold=True, italic=False, autoLog=None)          
    
    board = visual.ImageStim(participantwin, image='CheckersUnfiltered.png', interpolate=False, flipHoriz=False, flipVert=False, autoLog=None)
    board.size = board.size * 3.5
    board2 = visual.ImageStim(participantwin, image='CheckersUnfilteredReverse.png', interpolate=False, flipHoriz=False, flipVert=False, autoLog=None)
    board2.size = board2.size * 3.5
    
    targetstimuli = visual.Circle(participantwin, radius=[0.1, 0.1], pos = [0,-0.005], fillColor='#FF0000', lineColor='#FF0000', autoLog=False)
    stimradiusInitial = (fixationsize*(1.0/winsize[0]), fixationsize*(1.0/winsize[1]))
    targetstimuli.setRadius(stimradiusInitial)  
    
    # connect to Device
    UnicornBlack = unicornhybridblack.UnicornBlackProcess() 
    UnicornBlack.channellabels = 'FCZ, CP1, CPZ, CP2, P1, PZ, P2, OZ, AccelX, AccelY, AccelZ, GyroX, GyroY, GyroZ, Battery, Sample'
    UnicornBlack.connect(deviceID='UN-2019.05.51', rollingspan=2.0, logfilename='Matt_VisualContrast2')
    
    # wait up to 3 seconds for connection
    continueExperiment = False
    checktimer = core.CountdownTimer(start=3.0)
    while not continueExperiment:
        if UnicornBlack.ready:
            continueExperiment = True
        if (checktimer.getTime() <= 0):
            continueExperiment = True
    powerlevel = UnicornBlack.check_battery()
            
    statustext.draw()
    participantwin.flip() 
                          
    time.sleep(3)   
    
    UnicornBlack.startrecording()
    
    event.BuilderKeyResponse()
    event.clearEvents()       
    
    targetstimuli.setAutoDraw(True)  
    participantwin.flip()       
                              
    time.sleep(0.5) #lets get data rolling before we start
    
    continueExperiment = True
    invert = True
    eventcode = 5
    for incrX in range(200):
        
        if continueExperiment:  
            
            if event.getKeys(["escape", "q"]): # Check for kill keys
                continueExperiment = False
                break   
            
            if invert:
                board2.draw()
                invert = False
                eventcode = 6
            else:
                board.draw()
                invert = True
                eventcode = 5
            
            targetstimuli.setAutoDraw(True)  
            UnicornBlack.safe_to_log(False)           
    
            participantwin.flip() 
            UnicornBlack.mark_event(eventcode) # Send trigger   
        
            UnicornBlack.safe_to_log(True)
            time.sleep(0.5) 
    
    board.setAutoDraw(False)
    board2.setAutoDraw(False)
    targetstimuli.setAutoDraw(False)
    participantwin.flip() 
    
    # stop recording
    UnicornBlack.disconnect()
    
    participantwin.close()