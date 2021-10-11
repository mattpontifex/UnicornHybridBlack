# -*- coding: utf-8 -*-

from psychopy import visual, core, event, gui

participantwin = visual.Window(size = [600,600], fullscr = 0, screen = 0)

event.BuilderKeyResponse()
event.clearEvents()

continueRoutine = True
while continueRoutine:
    
    if event.getKeys(["escape", "q"]):
        continueRoutine = False
        
    theseKeys = event.getKeys()
    if (len(theseKeys) > 0): #at least one key was pressed
        print('The label for the key pressed is: %s' % theseKeys[0])
        event.clearEvents()

participantwin.close()     