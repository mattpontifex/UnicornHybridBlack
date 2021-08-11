# -*- coding: utf-8 -*-

import random
import numpy
import copy

def createoddballsequence(filout = [], cycles = [], parameters=[]):
    # Example Code:
    # createoddballsequence(filout = 'S:\Data\Raw\randomsequence.csv', cycles = 2, parameters = [100, 80, 900, 1000, 'm'])
    
    # populate headers
    newvarlabels = ['stimulusFile','preStimulusInterval','stimulusDuration','stimulusDuration_min','responseWindow_min','responseWindow_max','stimulusITI','postResponseInterval','stimulusXcoord','stimulusYcoord', 'correctResp','stimulusCode','maskFile','feedbackDuration','preFeedbackDelay','endFeedbackWithResponse','correctResponseStimulusFile','correctResponseCode','commissionErrorStimulusFile','commissionErrorCode', 'omissionErrorStimulusFile','omissionErrorCode','impulsiveErrorStimulusFile','impulsiveErrorCode','delayErrorStimulusFile','delayErrorCode']
    
    # Populate database with variable names
    f = open(filout, 'w') # Write Variable Labels to Database - Any original file is overwritten
    for i in newvarlabels:
        f.write(i)   # Write variable to file
        if (i != newvarlabels[-1]): f.write(',') # Insert Comma between each variable
    f.write('\n') # Write end of line character
    
    
    # 3 stim oddball creation
    trials = [1] * 4 + [2] * 5 + [3] * 5 + [4] * 5 + [5] * 4 + [6] * 4
    # 22.5% target probability
    # 22.5% distractor probability
    
    # each cycle has 120 trials
    trials = trials * cycles
    sequence = []
    
    # nontarget = 10
    # target = 20
    # distractor = 30
    for cT in range(len(trials)):
        newsequence = [10] * trials[cT] + [20]
        
        if (trials[cT] == 1):
            newsequence[0] = 30
        elif (trials[cT] == 2):
            tempind = []
            tempind.extend(range(0, trials[cT]))
            random.shuffle(tempind)
            newsequence[tempind[0]] = 30
        else:
            tempind = []
            tempind.extend(range(1, trials[cT]))
            random.shuffle(tempind)
            newsequence[tempind[0]] = 30
    
        sequence = sequence + [newsequence]
    
    # randomly reorder chunks
    random.shuffle(sequence)
    # unpack chunks
    sequence = [item for sublist in sequence for item in sublist]
    
    dummytrials = [10, 10, 20]
    for cT in range(len(dummytrials)): # loop through each trial
        
        for i in range(len(newvarlabels)):
            tout = 0
            
            if newvarlabels[i] == 'stimulusFile':
                if dummytrials[cT] == 10:
                    tout = 'nontarget.png'
                elif dummytrials[cT] == 20:
                    tout = 'target.png'
                elif dummytrials[cT] == 30:
                    tout = 'distractor.png'
                
            if newvarlabels[i] == 'stimulusDuration':
                if dummytrials[cT] == 20:
                    tout = numpy.multiply(parameters[2], 2)
                else:
                    tout = parameters[1]
                
            if newvarlabels[i] == 'stimulusDuration_min':
                tout = parameters[1]
                
            if newvarlabels[i] == 'responseWindow_min':
                tout = parameters[1]
                
            if newvarlabels[i] == 'responseWindow_max':
                tout = parameters[2]
                
            if dummytrials[cT] == 20:
                if newvarlabels[i] == 'postResponseInterval':
                    tout = 1000.0
            else:
                if newvarlabels[i] == 'stimulusITI':
                    tout = parameters[3]
                
            if newvarlabels[i] == 'correctResp':
                if dummytrials[cT] == 20:
                    tout = parameters[4]
                else:
                    tout = 0
                
            f.write(str(tout)) # Write data as a string to file
            if (i < len(newvarlabels)): f.write(',') # Include Comma between each item
        f.write('\n') # Write end of line character 
    
    for cT in range(len(sequence)): # loop through each trial
        for i in range(len(newvarlabels)):
            tout = 0
            
            if newvarlabels[i] == 'stimulusFile':
                if sequence[cT] == 10:
                    tout = 'nontarget.png'
                elif sequence[cT] == 20:
                    tout = 'target.png'
                elif sequence[cT] == 30:
                    tout = 'distractor.png'
                
            if newvarlabels[i] == 'stimulusDuration':
                tout = parameters[0]
                
            if newvarlabels[i] == 'stimulusDuration_min':
                tout = parameters[1]
                
            if newvarlabels[i] == 'responseWindow_min':
                tout = parameters[1]
                
            if newvarlabels[i] == 'responseWindow_max':
                tout = parameters[2]
                
            if newvarlabels[i] == 'stimulusITI':
                tout = parameters[3]
                
            if newvarlabels[i] == 'correctResp':
                if sequence[cT] == 20:
                    tout = parameters[4]
                else:
                    tout = 0
                
            if newvarlabels[i] == 'stimulusCode':
                tout = sequence[cT]
            
            f.write(str(tout)) # Write data as a string to file
            if (i < len(newvarlabels)): f.write(',') # Include Comma between each item
        f.write('\n') # Write end of line character 
    
    f.close() # close file 
    
    
def switchnumbers(sequence, x, y, z=999):
    # change X to Y and Y to X
    
    # change all x to Z
    for cT in range(len(sequence)):
        if sequence[cT] == x:
            sequence[cT] = z
            
    # change all y to x
    for cT in range(len(sequence)):
        if sequence[cT] == y:
            sequence[cT] = x
            
    # change all Z to y
    for cT in range(len(sequence)):
        if sequence[cT] == z:
            sequence[cT] = y
    
    return sequence
    
    
def constrainbacksequence(sequence, newsequence):
    boolswitch1needed = True
    boolswitch2needed = True
    
    while boolswitch1needed or boolswitch2needed:
        boolswitch1needed = False
        boolswitch2needed = False
        if (sequence[-1] == newsequence[0]):
            # last and first trial match for 1back
            boolswitch1needed = True
            
        if (sequence[-1] == newsequence[1]):
            # last and second trial match for 2back
            boolswitch2needed = True
            
        if (sequence[-2] == newsequence[0]):
            # second to last and first trial match for 2back
            boolswitch2needed = True
            
        if boolswitch1needed or boolswitch2needed:
            # need to change something
            templocations = [1, 2, 3, 4, 5, 6]
            
            if boolswitch1needed:
                templocations.remove(newsequence[0])
            if boolswitch2needed:
                try:
                    templocations.remove(newsequence[1])
                except:
                    booler = 1
            
            random.shuffle(templocations)
            if boolswitch1needed:
                switchnumbers(newsequence, newsequence[0], templocations[0])
            if boolswitch2needed:
                switchnumbers(newsequence, newsequence[1], templocations[1])
    
    return newsequence
    
    

def createnbacksequence(filout = [], cycles = [], style=1, back=2, parameters=[], feedback=[]):
    # Example Code:
    # createnbacksequence(filout = 'S:\Data\Raw\randomsequence.csv', cycles = 1, style = 1, back = 2, parameters = [200, 150, 1450, 1500, ['z','m']], feedback = [])
    
    if len(feedback) > 0:
        tempfeedback = [0]*6
        for i in range(len(feedback)):
            tempfeedback[i] = feedback[i]
        feedback = copy.deepcopy(tempfeedback)
        
    # populate headers
    newvarlabels = ['stimulusFile','preStimulusInterval','stimulusDuration','stimulusDuration_min','responseWindow_min','responseWindow_max','stimulusITI','postResponseInterval','stimulusXcoord','stimulusYcoord', 'correctResp','stimulusCode','maskFile','feedbackDuration','preFeedbackDelay','endFeedbackWithResponse','correctResponseStimulusFile','correctResponseCode','commissionErrorStimulusFile','commissionErrorCode', 'omissionErrorStimulusFile','omissionErrorCode','impulsiveErrorStimulusFile','impulsiveErrorCode','delayErrorStimulusFile','delayErrorCode']
    
    # Populate database with variable names
    f = open(filout, 'w') # Write Variable Labels to Database - Any original file is overwritten
    for i in newvarlabels:
        f.write(i)   # Write variable to file
        if (i != newvarlabels[-1]): f.write(',') # Insert Comma between each variable
    f.write('\n') # Write end of line character
    
    # 6 locations
    # 144 trials
    # each location will have 24 trials:
    #    2 occurrances of type 40 when both Nb1 and Nb2 targets occur (8%)
    #    6 occurrances of type 30 when Nb2 targets occur but not Nb1 (25%)
    #    6 occurrances of type 20 when Nb1 targets occur but not Nb2 (25%)
    #    10 occurrances of type 10 when neither Nb1 or Nb2 targets occur (42%)
    
    # constraints
    # each location should occur with similar probability
    
    locations = [1, 2, 3, 4, 5, 6]
    blocks = [1, 2, 3, 4, 5, 6]
    blocks = blocks * cycles
    random.shuffle(blocks)
    sequence = [[5, 1]]
    
    for cB in range(len(blocks)):
        newsequence = [0] * 24
        
        if (blocks[cB] == 1):
            newsequence = [3,1,3,1,1,1,4,6,5,5,2,3,4,2,3,6,6,6,4,5,4,5,2,2]
            #1	2	2
            #2	1	0
            #3	0	1
            #4	0	1
            #5	1	1
            #6	2	1
                
        elif (blocks[cB] == 2):
            newsequence = [6,2,6,3,3,2,5,5,5,4,1,2,6,2,6,3,4,3,1,1,1,4,4,5]
            #1	2	1
            #2	0	1
            #3	1	1
            #4	1	0
            #5	2	1
            #6	0	2
            
        elif (blocks[cB] == 3):
            newsequence = [4,1,6,1,3,2,2,2,5,4,3,4,3,1,1,2,6,3,6,6,5,5,5,4]       
            #1	1	1
            #2	2	1
            #3	0	1
            #4	0	1
            #5	2	1
            #6	1	1
    
        elif (blocks[cB] == 4):
            newsequence = [4,2,4,2,6,5,1,1,1,5,2,2,3,6,6,6,3,3,4,1,4,5,3,5] 
            #1	2	1
            #2	1	1
            #3	1	0
            #4	0	2
            #5	0	1
            #6	2	1
    
        elif (blocks[cB] == 5):
            newsequence = [2,2,4,2,4,4,4,1,5,3,5,2,5,3,6,1,5,3,6,6,6,3,1,1]
            #1	1	0
            #2	1	1
            #3	0	0
            #4	2	2
            #5	0	2
            #6	2	1
            
        elif (blocks[cB] == 6):
            newsequence = [1,4,4,4,1,2,1,4,5,6,3,3,2,6,2,2,3,6,3,6,5,5,5,3]
            #1	0	1
            #2	1	1
            #3	1	1
            #4	2	1
            #5	2	1
            #6	0	1
    
        if cB == 0:
            sequence = sequence + [newsequence]
        else:
            #constrainbacksequence(sequence[-1], newsequence)
            sequence = sequence + [newsequence[0:len(newsequence)]]
    
    sequence = [item for sublist in sequence for item in sublist]
    
    # switch around the numbers
    newlocations = copy.deepcopy(locations)
    random.shuffle(newlocations)
    for cT in range(len(locations)):
        switchnumbers(sequence, locations[cT], newlocations[cT])
        
    # determine trial type
    typecode = [10] * len(sequence)
    respcode = [10] * len(sequence)
    for cT in range(len(sequence)):
        typecode[cT] = numpy.add(10, sequence[cT])
        
        # 1 back hit
        if cT > 0:
            if sequence[cT] == sequence[cT-1]:
                # 1back hit
                typecode[cT] = numpy.add(20, sequence[cT])
                respcode[cT] = 20
                
        if cT > 1:
            if sequence[cT] == sequence[cT-2]:
                # 2back hit
                typecode[cT] = numpy.add(30, sequence[cT])
                respcode[cT] = 30
                
                if sequence[cT] == sequence[cT-1]:
                    # 1back and 2back hit
                    typecode[cT] = numpy.add(40, sequence[cT])
                    respcode[cT] = 40
    
    
    locationcounter = [0] * len(locations)
    nb1targetcounter = [0] * len(locations)
    nb2targetcounter = [0] * len(locations)
    for cT in range(len(locations)):
        locationcounter[cT] = sequence.count(locations[cT])
        
        nb1targetcounter[cT] = numpy.add(typecode.count(numpy.add(20, locations[cT])),typecode.count(numpy.add(40, locations[cT])))
        
        nb2targetcounter[cT] = numpy.add(typecode.count(numpy.add(30, locations[cT])),typecode.count(numpy.add(40, locations[cT])))
        
    
    for cT in range(len(sequence)): # loop through each trial
        for i in range(len(newvarlabels)):
            tout = 0
            
            if newvarlabels[i] == 'stimulusFile':
                if style == 1:
                    if sequence[cT] == 1:
                        tout = 'SNB1.png'
                    elif sequence[cT] == 2:
                        tout = 'SNB2.png'
                    elif sequence[cT] == 3:
                        tout = 'SNB3.png'
                    elif sequence[cT] == 4:
                        tout = 'SNB4.png'
                    elif sequence[cT] == 5:
                        tout = 'SNB5.png'
                    elif sequence[cT] == 6:
                        tout = 'SNB6.png'
                elif style == 2:
                    if sequence[cT] == 1:
                        tout = 'SNBfu1.png'
                    elif sequence[cT] == 2:
                        tout = 'SNBfu2.png'
                    elif sequence[cT] == 3:
                        tout = 'SNBfu3.png'
                    elif sequence[cT] == 4:
                        tout = 'SNBfu4.png'
                    elif sequence[cT] == 5:
                        tout = 'SNBfu5.png'
                    elif sequence[cT] == 6:
                        tout = 'SNBfu6.png'
                elif style == 3:
                    if sequence[cT] == 1:
                        tout = 'SNBf1.png'
                    elif sequence[cT] == 2:
                        tout = 'SNBf2.png'
                    elif sequence[cT] == 3:
                        tout = 'SNBf3.png'
                    elif sequence[cT] == 4:
                        tout = 'SNBf4.png'
                    elif sequence[cT] == 5:
                        tout = 'SNBf5.png'
                    elif sequence[cT] == 6:
                        tout = 'SNBf6.png'
                
            if newvarlabels[i] == 'stimulusDuration':
                tout = parameters[0]
                
            if newvarlabels[i] == 'stimulusDuration_min':
                tout = parameters[1]
                
            if newvarlabels[i] == 'responseWindow_min':
                tout = parameters[1]
                
            if newvarlabels[i] == 'responseWindow_max':
                tout = parameters[2]
                
            if newvarlabels[i] == 'stimulusITI':
                tout = parameters[3]
                
            if newvarlabels[i] == 'correctResp':
                if style < 3:
                    if back == 1:
                        if (respcode[cT] == 20) or (respcode[cT] == 40):
                            tout = parameters[4][1]
                        else:
                            tout = parameters[4][0]
                            
                    elif back == 2:
                        if (respcode[cT] == 30) or (respcode[cT] == 40):
                            tout = parameters[4][1]
                        else:
                            tout = parameters[4][0]
                            
                elif style == 3:
                    tout = 0
                    if back == 1:
                        if cT > 0:
                            tout = parameters[4][sequence[cT-1]-1]
                    if back == 2:
                        if cT > 1:
                            tout = parameters[4][sequence[cT-2]-1]
                
            if newvarlabels[i] == 'stimulusCode':
                tout = typecode[cT]
                if back == 1:
                    if cT == 0:
                        tout = 0
                if back == 2:
                    if cT < 2:
                        tout = 0
                        
            if len(feedback) > 0:
                boolpass = True         
                if back == 1:
                    if cT == 0:
                        boolpass = False
                if back == 2:
                    if cT < 2:
                        boolpass = False
                if boolpass:
                    if newvarlabels[i] == 'feedbackDuration':
                        tout = feedback[0]
                    #if newvarlabels[i] == 'preFeedbackDelay':
                    #if newvarlabels[i] == 'endFeedbackWithResponse':
                    if feedback[1] != 0:
                        if newvarlabels[i] == 'correctResponseStimulusFile':
                            if style == 1:
                                tout = 'SNBcorrect.png'
                            elif style == 2:
                                tout = 'SNBfucorrect.png'
                            elif style == 3:
                                tout = 'SNBfcorrect.png'
                        if newvarlabels[i] == 'correctResponseCode':
                            tout = 50
                    if feedback[2] != 0:
                        if newvarlabels[i] == 'commissionErrorStimulusFile':
                            if style == 1:
                                tout = 'SNBerror.png'
                            elif style == 2:
                                tout = 'SNBferror.png'
                            elif style == 3:
                                tout = 'SNBferror.png'
                        if newvarlabels[i] == 'commissionErrorCode':
                            tout = 51
                    if feedback[3] != 0:
                        if newvarlabels[i] == 'omissionErrorStimulusFile':
                            if style == 1:
                                tout = 'SNBerror.png'
                            elif style == 2:
                                tout = 'SNBferror.png'
                            elif style == 3:
                                tout = 'SNBferror.png'
                        if newvarlabels[i] == 'omissionErrorCode':
                            tout = 52
                    if feedback[4] != 0:
                        if newvarlabels[i] == 'impulsiveErrorStimulusFile':
                            if style == 1:
                                tout = 'SNBerror.png'
                            elif style == 2:
                                tout = 'SNBferror.png'
                            elif style == 3:
                                tout = 'SNBferror.png'
                        if newvarlabels[i] == 'impulsiveErrorCode':
                            tout = 53
                    if feedback[5] != 0:
                        if newvarlabels[i] == 'delayErrorStimulusFile':
                            if style == 1:
                                tout = 'SNBerror.png'
                            elif style == 2:
                                tout = 'SNBferror.png'
                            elif style == 3:
                                tout = 'SNBferror.png'
                        if newvarlabels[i] == 'delayErrorCode':
                            tout = 54

            
            f.write(str(tout)) # Write data as a string to file
            if (i < len(newvarlabels)): f.write(',') # Include Comma between each item
        f.write('\n') # Write end of line character 
    
    f.close() # close file 

  