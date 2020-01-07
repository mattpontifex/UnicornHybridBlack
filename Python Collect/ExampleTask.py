from psychopy import visual, core, event

trialsequence = [0.6, 0.6, 1.2, 0.6, 1.2, 0.6]
stimdelayinsec = 0.150
stimdurationinsec = .300
durationinsec = 1.0
cumulativeTime = core.Clock(); cumulativeTime.reset()
participantwin = visual.Window(size = (500,500), fullscr = False, screen = 0, allowGUI = False, allowStencil = False, monitor = 'testMonitor', color = '#000000', colorSpace = 'rgb')

participantwin.flip()   

targetstimuli = visual.Circle(participantwin, radius=[0.1, 0.1], pos = [0,0], fillColor='#FFFFFF', lineColor='#FFFFFF', autoLog=False)

for countTrials in range(len(trialsequence)):
        
    event.BuilderKeyResponse()
    event.clearEvents()
    runtimeTime = core.Clock(); runtimeTime.reset()
    
    stimradiusInitial = ((trialsequence[countTrials]/500)*100, (trialsequence[countTrials]/500)*100)
    targetstimuli.setRadius(stimradiusInitial)
    
    continueExperiment = True
    stimon = False
    while continueExperiment:
        
        if event.getKeys(["escape", "q"]): # Check for kill keys
            continueExperiment = False
            break
    
        if (runtimeTime.getTime() > float(durationinsec)):
            continueExperiment = False
        
        if not stimon:
            if (runtimeTime.getTime() > float(stimdelayinsec)) and (runtimeTime.getTime() < (float(stimdelayinsec) + float(stimdurationinsec))):
                targetstimuli.setAutoDraw(True)
                stimon = True
                participantwin.flip()  
                
        if stimon:
            if (runtimeTime.getTime() >= (float(stimdelayinsec) + float(stimdurationinsec))):
                targetstimuli.setAutoDraw(False)
                stimon = False
                participantwin.flip()  
                

participantwin.close()
del countTrials, targetstimuli, trialsequence
del continueExperiment, durationinsec, participantwin, stimon, runtimeTime, stimdelayinsec, stimdurationinsec, stimradiusInitial
print("Elapsed time: %.6f" % cumulativeTime.getTime())
del  cumulativeTime
