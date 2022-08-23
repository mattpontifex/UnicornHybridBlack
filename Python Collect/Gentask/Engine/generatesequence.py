# -*- coding: utf-8 -*-

import random
import numpy
import copy


def createsartsequence(filout = [], cycles = [], mask = 1, parameters=[], feedback=[]):

    # populate headers
    newvarlabels = ['stimulusFile','preStimulusInterval','stimulusDuration','stimulusDuration_min','responseWindow_min','responseWindow_max','stimulusITI','postResponseInterval','stimulusXcoord','stimulusYcoord', 'correctResp','stimulusCode','maskFile','feedbackDuration','preFeedbackDelay','endFeedbackWithResponse','correctResponseStimulusFile','correctResponseCode','commissionErrorStimulusFile','commissionErrorCode', 'omissionErrorStimulusFile','omissionErrorCode','impulsiveErrorStimulusFile','impulsiveErrorCode','delayErrorStimulusFile','delayErrorCode']
    
    # Populate database with variable names
    f = open(filout, 'w') # Write Variable Labels to Database - Any original file is overwritten
    for i in newvarlabels:
        f.write(i)   # Write variable to file
        if (i != newvarlabels[-1]): f.write(',') # Insert Comma between each variable
    f.write('\n') # Write end of line character
    

    # write instruction prompt into beginning of file 
    dummytrials = ['nothing.png', 'SARTinstruct1.png', 'SARTinstruct2.png']
    for cT in range(len(dummytrials)): # loop through each trial
        
        for i in range(len(newvarlabels)):
            tout = 0
            
            if newvarlabels[i] == 'stimulusFile':
                tout = dummytrials[cT]
                
            if newvarlabels[i] == 'stimulusDuration':
                if dummytrials[cT] == 'nothing.png':
                    tout = 500.0
                else:
                    tout = 10000.0
                
            if newvarlabels[i] == 'stimulusDuration_min':
                tout = parameters[1]
                
            if newvarlabels[i] == 'responseWindow_min':
                tout = parameters[1]
                
            if newvarlabels[i] == 'responseWindow_max':
                if dummytrials[cT] == 'nothing.png':
                    tout = 500.0
                else:
                    tout = 10000.0
                
            if newvarlabels[i] == 'postResponseInterval':
                if dummytrials[cT] == 'nothing.png':
                    tout = 500.0
                else:
                    tout = 500.0
                
            if newvarlabels[i] == 'correctResp':
                tout = parameters[4][0]
                
            f.write(str(tout)) # Write data as a string to file
            if (i < len(newvarlabels)): f.write(',') # Include Comma between each item
        f.write('\n') # Write end of line character 
    
    
    # write a few practice trials into beginning of file
    dummytrials = [11, 18, 13, 19, 16]
    for cT in range(len(dummytrials)): # loop through each trial
        
        for i in range(len(newvarlabels)):
            tout = 0
            
            if newvarlabels[i] == 'stimulusFile':
                tout = 'SART_' + str(dummytrials[cT]) + '.png'
                
            if newvarlabels[i] == 'stimulusDuration':
                tout = numpy.multiply(parameters[2], 2)
                
            if newvarlabels[i] == 'stimulusDuration_min':
                tout = parameters[1]
                
            if newvarlabels[i] == 'responseWindow_min':
                tout = parameters[1]
                
            if newvarlabels[i] == 'responseWindow_max':
                tout = parameters[2]
                
            if newvarlabels[i] == 'stimulusITI':
                tout = parameters[3]
                
            if newvarlabels[i] == 'correctResp':
                if dummytrials[cT] == 13:
                    tout = 0
                else:
                    tout = parameters[4][0]
            
            if mask == 1:
                if newvarlabels[i] == 'maskFile':
                    tout = 'SARTmask.png'

            if len(feedback) > 0:
                # feedback only for target trials
                if newvarlabels[i] == 'feedbackDuration':
                    tout = feedback[0]
                        
                if feedback[2] != 0:
                    if newvarlabels[i] == 'commissionErrorStimulusFile':
                        tout = 'SARTError.png'
                        
                        
                if feedback[3] != 0:
                    if newvarlabels[i] == 'omissionErrorStimulusFile':
                        tout = 'SARTError.png'
                        
                        
                if feedback[4] != 0:
                    if newvarlabels[i] == 'impulsiveErrorStimulusFile':
                        tout = 'SARTError.png'
                        
                        
                if feedback[5] != 0:
                    if newvarlabels[i] == 'delayErrorStimulusFile':
                        tout = 'SARTError.png'
                        
                    

            f.write(str(tout)) # Write data as a string to file
            if (i < len(newvarlabels)): f.write(',') # Include Comma between each item
        f.write('\n') # Write end of line character 
    
    # create sequence
    basetrials = [11, 12, 14, 15, 16, 17, 18, 19]
    trials = [5] * 2 + [6] * 3 + [7] * 4 + [8] * 4 + [9] * 6 + [10] * 8
    
    # each cycle has 120 trials
    trials = trials * cycles
    sequence = []
    workingbase = copy.deepcopy(basetrials)
    random.shuffle(workingbase)
    for cT in range(len(trials)):
        newsequence = []
        for cTa in range(trials[cT]):
            if len(workingbase) == 1:
                removed_element = workingbase[0]
                workingbase = copy.deepcopy(basetrials)
                random.shuffle(workingbase)
            else:
                removed_element = workingbase.pop(0)
            newsequence.append(removed_element)
        newsequence.append(13)
                
        sequence = sequence + [newsequence]  
            
    # randomly reorder chunks
    random.shuffle(sequence)
    # unpack chunks
    sequence = [item for sublist in sequence for item in sublist]
    
    for cT in range(len(sequence)): # loop through each trial
        for i in range(len(newvarlabels)):
            tout = 0
            
            if newvarlabels[i] == 'stimulusFile':
                tout = 'SART_' + str(sequence[cT]) + '.png'
                
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
                if sequence[cT] == 13:
                    tout = 0
                else:
                    tout = parameters[4][0]
                
            if newvarlabels[i] == 'stimulusCode':
                tout = sequence[cT]
            
            if mask == 1:
                if newvarlabels[i] == 'maskFile':
                    tout = 'SARTmask.png'

            if len(feedback) > 0:
                # feedback only for target trials
                if newvarlabels[i] == 'feedbackDuration':
                    tout = feedback[0]
                        
                if feedback[2] != 0:
                    if newvarlabels[i] == 'commissionErrorStimulusFile':
                        tout = 'SARTError.png'
                        
                    if newvarlabels[i] == 'commissionErrorCode':
                        tout = 51
                        
                if feedback[3] != 0:
                    if newvarlabels[i] == 'omissionErrorStimulusFile':
                        tout = 'SARTError.png'
                        
                    if newvarlabels[i] == 'omissionErrorCode':
                        tout = 52
                        
                if feedback[4] != 0:
                    if newvarlabels[i] == 'impulsiveErrorStimulusFile':
                        tout = 'SARTError.png'
                        
                    if newvarlabels[i] == 'impulsiveErrorCode':
                        tout = 53
                        
                if feedback[5] != 0:
                    if newvarlabels[i] == 'delayErrorStimulusFile':
                        tout = 'SARTError.png'
                        
                    if newvarlabels[i] == 'delayErrorCode':
                        tout = 54
            
            
            f.write(str(tout)) # Write data as a string to file
            if (i < len(newvarlabels)): f.write(',') # Include Comma between each item
        f.write('\n') # Write end of line character 
    
    f.close() # close file


def createoddballsequence(filout = [], cycles = [], parameters=[], variant=2):
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
                    if variant == 2:
                        # 2 stim
                        tout = 'nontarget.png'
                    else:
                        # 3 stim
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
#                
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
                    if variant == 2:
                        # 2 stim
                        tout = 'nontarget.png'
                    else:
                        # 3 stim
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
    
    
    
def createnogosequence(filout = [], cycles = [], style=0, mask=[], parameters=[], variableiti=[], feedback=[]):
    # Example Code:
    # createnogosequence(filout = 'S:\Data\Raw\randomsequence.csv', cycles = 1, parameters = [100, 80, 1000, 1500, ['j']], variableiti=250, feedback = [])
    
    # populate headers
    newvarlabels = ['stimulusFile','preStimulusInterval','stimulusDuration','stimulusDuration_min','responseWindow_min','responseWindow_max','stimulusITI','postResponseInterval','stimulusXcoord','stimulusYcoord', 'correctResp','stimulusCode','maskFile','feedbackDuration','preFeedbackDelay','endFeedbackWithResponse','correctResponseStimulusFile','correctResponseCode','commissionErrorStimulusFile','commissionErrorCode', 'omissionErrorStimulusFile','omissionErrorCode','impulsiveErrorStimulusFile','impulsiveErrorCode','delayErrorStimulusFile','delayErrorCode']
    
    # Populate database with variable names
    f = open(filout, 'w') # Write Variable Labels to Database - Any original file is overwritten
    for i in newvarlabels:
        f.write(i)   # Write variable to file
        if (i != newvarlabels[-1]): f.write(',') # Insert Comma between each variable
    f.write('\n') # Write end of line character
    
    # write instruction prompt into beginning of file 
    dummytrials = ['nothing.png', 'GoInstruct.png', 'NogoInstruct.png', 'NogoInstruct2.png']
    for cT in range(len(dummytrials)): # loop through each trial
        
        for i in range(len(newvarlabels)):
            tout = 0
            
            if newvarlabels[i] == 'stimulusFile':
                tout = dummytrials[cT]
                
            if newvarlabels[i] == 'stimulusDuration':
                if dummytrials[cT] == 'nothing.png':
                    tout = 500.0
                else:
                    tout = 10000.0
                
            if newvarlabels[i] == 'stimulusDuration_min':
                tout = parameters[1]
                
            if newvarlabels[i] == 'responseWindow_min':
                tout = parameters[1]
                
            if newvarlabels[i] == 'responseWindow_max':
                if dummytrials[cT] == 'nothing.png':
                    tout = 500.0
                else:
                    tout = 10000.0
                
            if newvarlabels[i] == 'postResponseInterval':
                if dummytrials[cT] == 'nothing.png':
                    tout = 500.0
                else:
                    tout = 500.0
                
            if newvarlabels[i] == 'correctResp':
                tout = parameters[4][0]
                    
            f.write(str(tout)) # Write data as a string to file
            if (i < len(newvarlabels)): f.write(',') # Include Comma between each item
        f.write('\n') # Write end of line character 
    
    
    # write a few practice trials into beginning of file
    dummytrials = [8, 8, 9]
    for cT in range(len(dummytrials)): # loop through each trial
        
        for i in range(len(newvarlabels)):
            tout = 0
            
            if newvarlabels[i] == 'stimulusFile':
                if dummytrials[cT] in [8]:
                    tout = 'GNG_Target.png'
                elif dummytrials[cT] in [9]:
                    tout = 'GNG_Nogo.png'
                
            if newvarlabels[i] == 'stimulusDuration':
                tout = numpy.multiply(parameters[2], 2)
                
            if newvarlabels[i] == 'stimulusDuration_min':
                tout = parameters[1]
                
            if newvarlabels[i] == 'responseWindow_min':
                tout = parameters[1]
                
            if newvarlabels[i] == 'responseWindow_max':
                tout = parameters[2]
                
            if dummytrials[cT] == 8:
                if newvarlabels[i] == 'postResponseInterval':
                    tout = 1000.0
            else:
                if newvarlabels[i] == 'stimulusITI':
                    tout = parameters[3]
                
            if newvarlabels[i] == 'correctResp':
                if dummytrials[cT] == 8:
                    tout = parameters[4][0]
                else:
                    tout = 0
            
            if mask == 1:
                if newvarlabels[i] == 'maskFile':
                    tout = 'NG_Mask.png'
                    
            if len(feedback) > 0:
                # feedback only for target trials
                if newvarlabels[i] == 'feedbackDuration':
                    tout = feedback[0]
                    
                if feedback[1] != 0:
                    if newvarlabels[i] == 'correctResponseStimulusFile':
                        if dummytrials[cT] in [8]:
                            tout = 'GNG_GoCorrect.png'
                        elif dummytrials[cT] in [9]:
                            tout = 'GNG_NogoCorrect.png'
                        
                    if newvarlabels[i] == 'correctResponseCode':
                        tout = 50
                        
                if feedback[2] != 0:
                    if newvarlabels[i] == 'commissionErrorStimulusFile':
                        if dummytrials[cT] in [8]:
                            tout = 'GNG_GoError.png'
                        elif dummytrials[cT] in [9]:
                            tout = 'GNG_NogoError.png'
                        
                    if newvarlabels[i] == 'commissionErrorCode':
                        tout = 51
                        
                if feedback[3] != 0:
                    if newvarlabels[i] == 'omissionErrorStimulusFile':
                        if dummytrials[cT] in [8]:
                            tout = 'GNG_GoError.png'
                        elif dummytrials[cT] in [9]:
                            tout = 'GNG_NogoError.png'
                        
                    if newvarlabels[i] == 'omissionErrorCode':
                        tout = 52
                        
                if feedback[4] != 0:
                    if newvarlabels[i] == 'impulsiveErrorStimulusFile':
                        if dummytrials[cT] in [8]:
                            tout = 'GNG_GoError.png'
                        elif dummytrials[cT] in [9]:
                            tout = 'GNG_NogoError.png'
                        
                    if newvarlabels[i] == 'impulsiveErrorCode':
                        tout = 53
                        
                if feedback[5] != 0:
                    if newvarlabels[i] == 'delayErrorStimulusFile':
                        if dummytrials[cT] in [8]:
                            tout = 'GNG_GoError.png'
                        elif dummytrials[cT] in [9]:
                            tout = 'GNG_NogoError.png'
                        
                    if newvarlabels[i] == 'delayErrorCode':
                        tout = 54
                    
            f.write(str(tout)) # Write data as a string to file
            if (i < len(newvarlabels)): f.write(',') # Include Comma between each item
        f.write('\n') # Write end of line character 
    

    # write nogo task trials
    blocks = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    blocks = blocks * cycles
    random.shuffle(blocks)
    sequence = [[]]
    
    for cB in range(len(blocks)):
        newsequence = [0] * 4
        
        if (blocks[cB] == 1):
            newsequence = [12, 10, 22, 20]
            
        elif (blocks[cB] == 2):
            newsequence = [10, 12, 20, 22]
            
        elif (blocks[cB] == 3):
            newsequence = [12,	20,	22,	12,	10,	22]
            
        elif (blocks[cB] == 4):
            newsequence = [10,	22,	20,	10,	12,	20]
            
        elif (blocks[cB] == 5):
            newsequence = [12, 22, 20, 10, 22, 12, 10, 20]
            
        elif (blocks[cB] == 6):
            newsequence = [20,	22,	12,	20,	12,	10,	20,	10]
            
        elif (blocks[cB] == 7):
            newsequence = [22,	20,	10,	22,	10,	12,	22,	12]
            
        elif (blocks[cB] == 8):
            newsequence = [22,	10,	20,	12,	10,	22,	10,	20]
            
        elif (blocks[cB] == 9):
            newsequence = [20,	12,	22,	10,	12,	20,	12,	22]
    
        if cB == 0:
            sequence = sequence + [newsequence]
        else:
            sequence = sequence + [newsequence[0:len(newsequence)]]
        
    sequence = [item for sublist in sequence for item in sublist]
    
    # determine trial type
    typecode = [0] * len(sequence)
    respcode = [0] * len(sequence)
    gocode = 11
    nogocode = 42
    for cT in range(len(sequence)):
        # 10, 12, 20 - go             
        # 22 - nogo
        
        typecode[cT] = sequence[cT]
        tempcode = 0
    
        # code current direction
        if sequence[cT] == 10 or sequence[cT] == 12 or sequence[cT] == 20:
            # go
            tempcode = gocode
            respcode[cT] = parameters[4][0]
        else:
            # nogo
            tempcode = nogocode
            respcode[cT] = 0
            
        typecode[cT] = tempcode
                
        
    # allow ITI to vary
    itilist = [parameters[4]] * len(sequence)
    if not variableiti == 0:
        # varies the ITI using a gaussian distribution
        tempitilist = numpy.random.normal(loc=parameters[3], scale=variableiti, size=len(sequence))
        for cT in range(len(tempitilist)):
            # force the value to be in multiples of the screen refresh rate - assume 120 hz
            tempiti = round(numpy.divide(tempitilist[cT], 8.3),0)
            itilist[cT] = round(numpy.multiply(tempiti, 8.3),0)
    
    
    for cT in range(len(sequence)): # loop through each trial
        for i in range(len(newvarlabels)):
            tout = 0
            
            if newvarlabels[i] == 'stimulusFile':
                if typecode[cT] in [gocode]:
                    tout = 'GNG_Target.png'
                elif typecode[cT] in [nogocode]:
                    tout = 'GNG_Nogo.png'
                
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
                tout = respcode[cT]
                
            if newvarlabels[i] == 'stimulusCode':
                tout = typecode[cT]
            
            if mask == 1:
                if newvarlabels[i] == 'maskFile':
                    tout = 'NG_Mask.png'
                    
            if len(feedback) > 0:
                # feedback only for target trials
                if newvarlabels[i] == 'feedbackDuration':
                    tout = feedback[0]
                    
                if feedback[1] != 0:
                    if newvarlabels[i] == 'correctResponseStimulusFile':
                        if typecode[cT] in [gocode]:
                            tout = 'GNG_GoCorrect.png'
                        elif typecode[cT] in [nogocode]:
                            tout = 'GNG_NogoCorrect.png'
                        
                    if newvarlabels[i] == 'correctResponseCode':
                        tout = 50
                        
                if feedback[2] != 0:
                    if newvarlabels[i] == 'commissionErrorStimulusFile':
                        if typecode[cT] in [gocode]:
                            tout = 'GNG_GoError.png'
                        elif typecode[cT] in [nogocode]:
                            tout = 'GNG_NogoError.png'
                        
                    if newvarlabels[i] == 'commissionErrorCode':
                        tout = 51
                        
                if feedback[3] != 0:
                    if newvarlabels[i] == 'omissionErrorStimulusFile':
                        if typecode[cT] in [gocode]:
                            tout = 'GNG_GoError.png'
                        elif typecode[cT] in [nogocode]:
                            tout = 'GNG_NogoError.png'
                        
                    if newvarlabels[i] == 'omissionErrorCode':
                        tout = 52
                        
                if feedback[4] != 0:
                    if newvarlabels[i] == 'impulsiveErrorStimulusFile':
                        if typecode[cT] in [gocode]:
                            tout = 'GNG_GoError.png'
                        elif typecode[cT] in [nogocode]:
                            tout = 'GNG_NogoError.png'
                        
                    if newvarlabels[i] == 'impulsiveErrorCode':
                        tout = 53
                        
                if feedback[5] != 0:
                    if newvarlabels[i] == 'delayErrorStimulusFile':
                        if typecode[cT] in [gocode]:
                            tout = 'GNG_GoError.png'
                        elif typecode[cT] in [nogocode]:
                            tout = 'GNG_NogoError.png'
                        
                    if newvarlabels[i] == 'delayErrorCode':
                        tout = 54
            
            f.write(str(tout)) # Write data as a string to file
            if (i < len(newvarlabels)): f.write(',') # Include Comma between each item
        f.write('\n') # Write end of line character 
    
    f.close() # close file 
    
def createkramernogosequence(filout = [], cycles = [], style=1, mask=[], parameters=[], variableiti=[], feedback=[]):
    # Example Code:
    # createnogosequence(filout = 'S:\Data\Raw\randomsequence.csv', cycles = 1, parameters = [100, 80, 1000, 1500, ['f','j']], variableiti=250, feedback = [])
    
    # populate headers
    newvarlabels = ['stimulusFile','preStimulusInterval','stimulusDuration','stimulusDuration_min','responseWindow_min','responseWindow_max','stimulusITI','postResponseInterval','stimulusXcoord','stimulusYcoord', 'correctResp','stimulusCode','maskFile','feedbackDuration','preFeedbackDelay','endFeedbackWithResponse','correctResponseStimulusFile','correctResponseCode','commissionErrorStimulusFile','commissionErrorCode', 'omissionErrorStimulusFile','omissionErrorCode','impulsiveErrorStimulusFile','impulsiveErrorCode','delayErrorStimulusFile','delayErrorCode']
    
    # Populate database with variable names
    f = open(filout, 'w') # Write Variable Labels to Database - Any original file is overwritten
    for i in newvarlabels:
        f.write(i)   # Write variable to file
        if (i != newvarlabels[-1]): f.write(',') # Insert Comma between each variable
    f.write('\n') # Write end of line character
    
    
    # go sequence
    if style == 1:
        
        # write a few practice trials into beginning of file
        dummytrials = [8, 9, 9]
        for cT in range(len(dummytrials)): # loop through each trial
            
            for i in range(len(newvarlabels)):
                tout = 0
                
                if newvarlabels[i] == 'stimulusFile':
                    if dummytrials[cT] in [8]:
                        tout = 'GNG_Left.png'
                    elif dummytrials[cT] in [9]:
                        tout = 'GNG_Right.png'
                    
                if newvarlabels[i] == 'stimulusDuration':
                    tout = numpy.multiply(parameters[2], 2)
                    
                if newvarlabels[i] == 'stimulusDuration_min':
                    tout = parameters[1]
                    
                if newvarlabels[i] == 'responseWindow_min':
                    tout = parameters[1]
                    
                if newvarlabels[i] == 'responseWindow_max':
                    tout = parameters[2]
                    
                if newvarlabels[i] == 'postResponseInterval':
                    tout = 1000.0
                    
                if newvarlabels[i] == 'correctResp':
                    if dummytrials[cT] == 8:
                        tout = parameters[4][0]
                    else:
                        tout = parameters[4][1]
                    
                if mask == 1:
                    if newvarlabels[i] == 'maskFile':
                        tout = 'G_Mask.png'
                    
                if len(feedback) > 0:
                    # feedback only for target trials
                    if newvarlabels[i] == 'feedbackDuration':
                        tout = feedback[0]
                        
                    if feedback[1] != 0:
                        if newvarlabels[i] == 'correctResponseStimulusFile':
                            if dummytrials[cT] in [8]:
                                tout = 'GNG_LeftCorrect.png'
                            elif dummytrials[cT] in [9]:
                                tout = 'GNG_RightCorrect.png'
                            
                        if newvarlabels[i] == 'correctResponseCode':
                            tout = 50
                            
                    if feedback[2] != 0:
                        if newvarlabels[i] == 'commissionErrorStimulusFile':
                            if dummytrials[cT] in [8]:
                                tout = 'GNG_LeftError.png'
                            elif dummytrials[cT] in [9]:
                                tout = 'GNG_RightError.png'
                            
                        if newvarlabels[i] == 'commissionErrorCode':
                            tout = 51
                            
                    if feedback[3] != 0:
                        if newvarlabels[i] == 'omissionErrorStimulusFile':
                            if dummytrials[cT] in [8]:
                                tout = 'GNG_LeftError.png'
                            elif dummytrials[cT] in [9]:
                                tout = 'GNG_RightError.png'
                            
                        if newvarlabels[i] == 'omissionErrorCode':
                            tout = 52
                            
                    if feedback[4] != 0:
                        if newvarlabels[i] == 'impulsiveErrorStimulusFile':
                            if dummytrials[cT] in [8]:
                                tout = 'GNG_LeftError.png'
                            elif dummytrials[cT] in [9]:
                                tout = 'GNG_RightError.png'
                            
                        if newvarlabels[i] == 'impulsiveErrorCode':
                            tout = 53
                            
                    if feedback[5] != 0:
                        if newvarlabels[i] == 'delayErrorStimulusFile':
                            if dummytrials[cT] in [8]:
                                tout = 'GNG_LeftError.png'
                            elif dummytrials[cT] in [9]:
                                tout = 'GNG_RightError.png'
                            
                        if newvarlabels[i] == 'delayErrorCode':
                            tout = 54
                        
                f.write(str(tout)) # Write data as a string to file
                if (i < len(newvarlabels)): f.write(',') # Include Comma between each item
            f.write('\n') # Write end of line character 
        
        
        # write go task trials
        blocks = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        blocks = blocks * cycles
        random.shuffle(blocks)
        sequence = [[]]
        
        for cB in range(len(blocks)):
            newsequence = [0] * 4
            
            if (blocks[cB] == 1):
                newsequence = [12, 10, 22, 20]
                
            elif (blocks[cB] == 2):
                newsequence = [10, 12, 20, 22]
                
            elif (blocks[cB] == 3):
                newsequence = [12,	20,	22,	12,	10,	22]
                
            elif (blocks[cB] == 4):
                newsequence = [10,	22,	20,	10,	12,	20]
                
            elif (blocks[cB] == 5):
                newsequence = [12, 22, 20, 10, 22, 12, 10, 20]
                
            elif (blocks[cB] == 6):
                newsequence = [20,	22,	12,	20,	12,	10,	20,	10]
                
            elif (blocks[cB] == 7):
                newsequence = [22,	20,	10,	22,	10,	12,	22,	12]
                
            elif (blocks[cB] == 8):
                newsequence = [22,	10,	20,	12,	10,	22,	10,	20]
                
            elif (blocks[cB] == 9):
                newsequence = [20,	12,	22,	10,	12,	20,	12,	22]
        
            if cB == 0:
                sequence = sequence + [newsequence]
            else:
                sequence = sequence + [newsequence[0:len(newsequence)]]
            
        sequence = [item for sublist in sequence for item in sublist]
        
        # determine trial type
        typecode = [0] * len(sequence)
        respcode = [0] * len(sequence)
        for cT in range(len(sequence)):
            # 10, 20 - left             
            # 12, 22 - right
            
            typecode[cT] = sequence[cT]
            tempcode = 0
        
            # code current direction
            if sequence[cT] == 10 or sequence[cT] == 20:
                # left
                tempcode = numpy.add(1, tempcode)
                respcode[cT] = parameters[4][0]
            else:
                # right
                tempcode = numpy.add(2, tempcode)
                respcode[cT] = parameters[4][1]
                
            if cT == 0:
                tempcode = numpy.add(10, tempcode)
                
            elif cT > 0:
                
                # code if a response change occurred
                if (sequence[cT] == 10 or sequence[cT] == 20) and (sequence[cT-1] == 10 or sequence[cT-1] == 20):
                    # left on both
                    tempcode = numpy.add(10, tempcode)
                elif (sequence[cT] == 12 or sequence[cT] == 22) and (sequence[cT-1] == 12 or sequence[cT-1] == 22):
                    # right on both
                    tempcode = numpy.add(10, tempcode)
                else:
                    # different
                    tempcode = numpy.add(20, tempcode)
                
            # Same L - 11
            # Same R - 12
            # Different L - 21
            # Different R - 22
            typecode[cT] = tempcode
                    
            # Left - 11, 21
            # Right - 12, 22
            
        # allow ITI to vary
        itilist = [parameters[4]] * len(sequence)
        if not variableiti == 0:
            # varies the ITI using a gaussian distribution
            tempitilist = numpy.random.normal(loc=parameters[3], scale=variableiti, size=len(sequence))
            for cT in range(len(tempitilist)):
                # force the value to be in multiples of the screen refresh rate - assume 120 hz
                tempiti = round(numpy.divide(tempitilist[cT], 8.3),0)
                itilist[cT] = round(numpy.multiply(tempiti, 8.3),0)
        
        
        for cT in range(len(sequence)): # loop through each trial
            for i in range(len(newvarlabels)):
                tout = 0
                
                if newvarlabels[i] == 'stimulusFile':
                    if typecode[cT] in [11, 21, 31, 41]:
                        tout = 'GNG_Left.png'
                    elif typecode[cT] in [12, 22, 32, 42]:
                        tout = 'GNG_Right.png'
                    
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
                    tout = respcode[cT]
                    
                if newvarlabels[i] == 'stimulusCode':
                    tout = typecode[cT]
                
                if mask == 1:
                    if newvarlabels[i] == 'maskFile':
                        tout = 'G_Mask.png'
                        
                if len(feedback) > 0:
                    # feedback only for target trials
                    if newvarlabels[i] == 'feedbackDuration':
                        tout = feedback[0]
                        
                    if feedback[1] != 0:
                        if newvarlabels[i] == 'correctResponseStimulusFile':
                            if typecode[cT] in [11, 21, 31, 41]:
                                tout = 'GNG_LeftCorrect.png'
                            elif typecode[cT] in [12, 22, 32, 42]:
                                tout = 'GNG_RightCorrect.png'
                            
                        if newvarlabels[i] == 'correctResponseCode':
                            tout = 50
                            
                    if feedback[2] != 0:
                        if newvarlabels[i] == 'commissionErrorStimulusFile':
                            if typecode[cT] in [11, 21, 31, 41]:
                                tout = 'GNG_LeftError.png'
                            elif typecode[cT] in [12, 22, 32, 42]:
                                tout = 'GNG_RightError.png'
                            
                        if newvarlabels[i] == 'commissionErrorCode':
                            tout = 51
                            
                    if feedback[3] != 0:
                        if newvarlabels[i] == 'omissionErrorStimulusFile':
                            if typecode[cT] in [11, 21, 31, 41]:
                                tout = 'GNG_LeftError.png'
                            elif typecode[cT] in [12, 22, 32, 42]:
                                tout = 'GNG_RightError.png'
                            
                        if newvarlabels[i] == 'omissionErrorCode':
                            tout = 52
                            
                    if feedback[4] != 0:
                        if newvarlabels[i] == 'impulsiveErrorStimulusFile':
                            if typecode[cT] in [11, 21, 31, 41]:
                                tout = 'GNG_LeftError.png'
                            elif typecode[cT] in [12, 22, 32, 42]:
                                tout = 'GNG_RightError.png'
                            
                        if newvarlabels[i] == 'impulsiveErrorCode':
                            tout = 53
                            
                    if feedback[5] != 0:
                        if newvarlabels[i] == 'delayErrorStimulusFile':
                            if typecode[cT] in [11, 21, 31, 41]:
                                tout = 'GNG_LeftError.png'
                            elif typecode[cT] in [12, 22, 32, 42]:
                                tout = 'GNG_RightError.png'
                            
                        if newvarlabels[i] == 'delayErrorCode':
                            tout = 54
                
                f.write(str(tout)) # Write data as a string to file
                if (i < len(newvarlabels)): f.write(',') # Include Comma between each item
            f.write('\n') # Write end of line character 
        
    
    # nogo sequence
    
    # write instruction prompt into beginning of file 
    dummytrials = ['nothing.png', 'GNG_Instruct4.png', 'GNG_Instruct5.png', 'GNG_Instruct6.png']
    for cT in range(len(dummytrials)): # loop through each trial
        
        for i in range(len(newvarlabels)):
            tout = 0
            
            if newvarlabels[i] == 'stimulusFile':
                tout = dummytrials[cT]
                
            if newvarlabels[i] == 'stimulusDuration':
                if dummytrials[cT] == 'nothing.png':
                    tout = 500.0
                else:
                    tout = 10000.0
                
            if newvarlabels[i] == 'stimulusDuration_min':
                tout = parameters[1]
                
            if newvarlabels[i] == 'responseWindow_min':
                tout = parameters[1]
                
            if newvarlabels[i] == 'responseWindow_max':
                if dummytrials[cT] == 'nothing.png':
                    tout = 500.0
                else:
                    tout = 10000.0
                
            if newvarlabels[i] == 'postResponseInterval':
                if dummytrials[cT] == 'nothing.png':
                    tout = 500.0
                else:
                    tout = 500.0
                
            if newvarlabels[i] == 'correctResp':
                tout = parameters[4][1]
                    
            f.write(str(tout)) # Write data as a string to file
            if (i < len(newvarlabels)): f.write(',') # Include Comma between each item
        f.write('\n') # Write end of line character 
    
    
    # write a few practice trials into beginning of file
    dummytrials = [8, 8, 9]
    for cT in range(len(dummytrials)): # loop through each trial
        
        for i in range(len(newvarlabels)):
            tout = 0
            
            if newvarlabels[i] == 'stimulusFile':
                if dummytrials[cT] in [8]:
                    tout = 'GNG_Left.png'
                elif dummytrials[cT] in [9]:
                    tout = 'GNG_Right.png'
                
            if newvarlabels[i] == 'stimulusDuration':
                tout = numpy.multiply(parameters[2], 2)
                
            if newvarlabels[i] == 'stimulusDuration_min':
                tout = parameters[1]
                
            if newvarlabels[i] == 'responseWindow_min':
                tout = parameters[1]
                
            if newvarlabels[i] == 'responseWindow_max':
                tout = parameters[2]
                
            if dummytrials[cT] == 8:
                if newvarlabels[i] == 'postResponseInterval':
                    tout = 1000.0
            else:
                if newvarlabels[i] == 'stimulusITI':
                    tout = parameters[3]
                
            if newvarlabels[i] == 'correctResp':
                if dummytrials[cT] == 8:
                    tout = parameters[4][0]
                else:
                    tout = 0
            
            if mask == 1:
                if newvarlabels[i] == 'maskFile':
                    tout = 'NG_Mask.png'
                    
            if len(feedback) > 0:
                # feedback only for target trials
                if newvarlabels[i] == 'feedbackDuration':
                    tout = feedback[0]
                    
                if feedback[1] != 0:
                    if newvarlabels[i] == 'correctResponseStimulusFile':
                        if dummytrials[cT] in [8]:
                            tout = 'GNG_LeftCorrect.png'
                        elif dummytrials[cT] in [9]:
                            tout = 'GNG_RightCorrect.png'
                        
                    if newvarlabels[i] == 'correctResponseCode':
                        tout = 50
                        
                if feedback[2] != 0:
                    if newvarlabels[i] == 'commissionErrorStimulusFile':
                        if dummytrials[cT] in [8]:
                            tout = 'GNG_LeftError.png'
                        elif dummytrials[cT] in [9]:
                            tout = 'GNG_RightError.png'
                        
                    if newvarlabels[i] == 'commissionErrorCode':
                        tout = 51
                        
                if feedback[3] != 0:
                    if newvarlabels[i] == 'omissionErrorStimulusFile':
                        if dummytrials[cT] in [8]:
                            tout = 'GNG_LeftError.png'
                        elif dummytrials[cT] in [9]:
                            tout = 'GNG_RightError.png'
                        
                    if newvarlabels[i] == 'omissionErrorCode':
                        tout = 52
                        
                if feedback[4] != 0:
                    if newvarlabels[i] == 'impulsiveErrorStimulusFile':
                        if dummytrials[cT] in [8]:
                            tout = 'GNG_LeftError.png'
                        elif dummytrials[cT] in [9]:
                            tout = 'GNG_RightError.png'
                        
                    if newvarlabels[i] == 'impulsiveErrorCode':
                        tout = 53
                        
                if feedback[5] != 0:
                    if newvarlabels[i] == 'delayErrorStimulusFile':
                        if dummytrials[cT] in [8]:
                            tout = 'GNG_LeftError.png'
                        elif dummytrials[cT] in [9]:
                            tout = 'GNG_RightError.png'
                        
                    if newvarlabels[i] == 'delayErrorCode':
                        tout = 54
                    
            f.write(str(tout)) # Write data as a string to file
            if (i < len(newvarlabels)): f.write(',') # Include Comma between each item
        f.write('\n') # Write end of line character 
    
    
    # write nogo task trials
    
    blocks = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    blocks = blocks * cycles
    random.shuffle(blocks)
    sequence = [[]]
    
    for cB in range(len(blocks)):
        newsequence = [0] * 4
        
        if (blocks[cB] == 1):
            newsequence = [12, 10, 22, 20]
            
        elif (blocks[cB] == 2):
            newsequence = [10, 12, 20, 22]
            
        elif (blocks[cB] == 3):
            newsequence = [12,	20,	22,	12,	10,	22]
            
        elif (blocks[cB] == 4):
            newsequence = [10,	22,	20,	10,	12,	20]
            
        elif (blocks[cB] == 5):
            newsequence = [12, 22, 20, 10, 22, 12, 10, 20]
            
        elif (blocks[cB] == 6):
            newsequence = [20,	22,	12,	20,	12,	10,	20,	10]
            
        elif (blocks[cB] == 7):
            newsequence = [22,	20,	10,	22,	10,	12,	22,	12]
            
        elif (blocks[cB] == 8):
            newsequence = [22,	10,	20,	12,	10,	22,	10,	20]
            
        elif (blocks[cB] == 9):
            newsequence = [20,	12,	22,	10,	12,	20,	12,	22]
    
        if cB == 0:
            sequence = sequence + [newsequence]
        else:
            sequence = sequence + [newsequence[0:len(newsequence)]]
        
    sequence = [item for sublist in sequence for item in sublist]
    
    # determine trial type
    typecode = [0] * len(sequence)
    respcode = [0] * len(sequence)
    for cT in range(len(sequence)):
        # 10, 20 - left             
        # 12, 22 - right - Nogo trials
        
        typecode[cT] = sequence[cT]
        tempcode = 0
    
        # code current direction
        if sequence[cT] == 10 or sequence[cT] == 20:
            # left
            tempcode = numpy.add(1, tempcode)
            respcode[cT] = parameters[4][0]
        else:
            # right
            tempcode = numpy.add(2, tempcode)
            respcode[cT] = 0
            
        if cT == 0:
            tempcode = numpy.add(30, tempcode)
            
        elif cT > 0:
            
            # code if a response change occurred
            if (sequence[cT] == 10 or sequence[cT] == 20) and (sequence[cT-1] == 10 or sequence[cT-1] == 20):
                # left on both
                tempcode = numpy.add(30, tempcode)
            elif (sequence[cT] == 12 or sequence[cT] == 22) and (sequence[cT-1] == 12 or sequence[cT-1] == 22):
                # right on both
                tempcode = numpy.add(30, tempcode)
            else:
                # different
                tempcode = numpy.add(40, tempcode)
            
        # Same L - 31
        # Same R - 32
        # Different L - 41
        # Different R - 42
        typecode[cT] = tempcode
                
        # Left - 31, 41
        # Right - 32, 42
        
    # allow ITI to vary
    itilist = [parameters[4]] * len(sequence)
    if not variableiti == 0:
        # varies the ITI using a gaussian distribution
        tempitilist = numpy.random.normal(loc=parameters[3], scale=variableiti, size=len(sequence))
        for cT in range(len(tempitilist)):
            # force the value to be in multiples of the screen refresh rate - assume 120 hz
            tempiti = round(numpy.divide(tempitilist[cT], 8.3),0)
            itilist[cT] = round(numpy.multiply(tempiti, 8.3),0)
    
    
    for cT in range(len(sequence)): # loop through each trial
        for i in range(len(newvarlabels)):
            tout = 0
            
            if newvarlabels[i] == 'stimulusFile':
                if typecode[cT] in [11, 21, 31, 41]:
                    tout = 'GNG_Left.png'
                elif typecode[cT] in [12, 22, 32, 42]:
                    tout = 'GNG_Right.png'
                
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
                tout = respcode[cT]
                
            if newvarlabels[i] == 'stimulusCode':
                tout = typecode[cT]
            
            if mask == 1:
                if newvarlabels[i] == 'maskFile':
                    tout = 'NG_Mask.png'
                    
            if len(feedback) > 0:
                # feedback only for target trials
                if newvarlabels[i] == 'feedbackDuration':
                    tout = feedback[0]
                    
                if feedback[1] != 0:
                    if newvarlabels[i] == 'correctResponseStimulusFile':
                        if typecode[cT] in [11, 21, 31, 41]:
                            tout = 'GNG_LeftCorrect.png'
                        elif typecode[cT] in [12, 22, 32, 42]:
                            tout = 'GNG_RightCorrect.png'
                        
                    if newvarlabels[i] == 'correctResponseCode':
                        tout = 50
                        
                if feedback[2] != 0:
                    if newvarlabels[i] == 'commissionErrorStimulusFile':
                        if typecode[cT] in [11, 21, 31, 41]:
                            tout = 'GNG_LeftError.png'
                        elif typecode[cT] in [12, 22, 32, 42]:
                            tout = 'GNG_RightError.png'
                        
                    if newvarlabels[i] == 'commissionErrorCode':
                        tout = 51
                        
                if feedback[3] != 0:
                    if newvarlabels[i] == 'omissionErrorStimulusFile':
                        if typecode[cT] in [11, 21, 31, 41]:
                            tout = 'GNG_LeftError.png'
                        elif typecode[cT] in [12, 22, 32, 42]:
                            tout = 'GNG_RightError.png'
                        
                    if newvarlabels[i] == 'omissionErrorCode':
                        tout = 52
                        
                if feedback[4] != 0:
                    if newvarlabels[i] == 'impulsiveErrorStimulusFile':
                        if typecode[cT] in [11, 21, 31, 41]:
                            tout = 'GNG_LeftError.png'
                        elif typecode[cT] in [12, 22, 32, 42]:
                            tout = 'GNG_RightError.png'
                        
                    if newvarlabels[i] == 'impulsiveErrorCode':
                        tout = 53
                        
                if feedback[5] != 0:
                    if newvarlabels[i] == 'delayErrorStimulusFile':
                        if typecode[cT] in [11, 21, 31, 41]:
                            tout = 'GNG_LeftError.png'
                        elif typecode[cT] in [12, 22, 32, 42]:
                            tout = 'GNG_RightError.png'
                        
                    if newvarlabels[i] == 'delayErrorCode':
                        tout = 54
            
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

  
    
    

def createflankersequence(filout = [], cycles = [], style = 1, parameters=[], variableiti=0, feedback = []):
    # Example Code:
    # createflankersequence(filout = 'S:\Data\Raw\randomsequence.csv', cycles = 2, parameters = [55, 100, 80, 1000, 1500, ['z','m']], variableiti=250, feedback = [])

    # Traditional
    # Respond Opposite
    # Include neutral Trials
    # Include cue masks
    # Letters or Arrows?
    # Flip mid task?
    
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
    
    
    blocks = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    blocks = blocks * cycles
    random.shuffle(blocks)
    sequence = [[]]
    
    for cB in range(len(blocks)):
        newsequence = [0] * 4
        
        if (blocks[cB] == 1):
            newsequence = [12, 10, 22, 20]
            
        elif (blocks[cB] == 2):
            newsequence = [10, 12, 20, 22]
            
        elif (blocks[cB] == 3):
            newsequence = [12,	20,	22,	12,	10,	22]
            
        elif (blocks[cB] == 4):
            newsequence = [10,	22,	20,	10,	12,	20]
            
        elif (blocks[cB] == 5):
            newsequence = [12, 22, 20, 10, 22, 12, 10, 20]
            
        elif (blocks[cB] == 6):
            newsequence = [20,	22,	12,	20,	12,	10,	20,	10]
            
        elif (blocks[cB] == 7):
            newsequence = [22,	20,	10,	22,	10,	12,	22,	12]
            
        elif (blocks[cB] == 8):
            newsequence = [22,	10,	20,	12,	10,	22,	10,	20]
            
        elif (blocks[cB] == 9):
            newsequence = [20,	12,	22,	10,	12,	20,	12,	22]
    
        if cB == 0:
            sequence = sequence + [newsequence]
        else:
            sequence = sequence + [newsequence[0:len(newsequence)]]
        
    sequence = [item for sublist in sequence for item in sublist]
        
    # determine trial type
    typecode = [0] * len(sequence)
    respcode = [0] * len(sequence)
    for cT in range(len(sequence)):
        # 10 - congruent left             
        # 12 - congruent right
        # 20 - incongruent left
        # 22 - incongruent right
        
        typecode[cT] = sequence[cT]
        tempcode = 0
    
        # code current direction
        if sequence[cT] == 10 or sequence[cT] == 20:
            # left
            tempcode = numpy.add(1, tempcode)
            respcode[cT] = parameters[5][0]
        else:
            # right
            tempcode = numpy.add(2, tempcode)
            respcode[cT] = parameters[5][1]
            
        if cT > 0:
            
            # code if a response change occurred
            if (sequence[cT] == 10 or sequence[cT] == 20) and (sequence[cT-1] == 10 or sequence[cT-1] == 20):
                # left on both
                tempcode = numpy.add(10, tempcode)
            elif (sequence[cT] == 12 or sequence[cT] == 22) and (sequence[cT-1] == 12 or sequence[cT-1] == 22):
                # right on both
                tempcode = numpy.add(10, tempcode)
            else:
                # different
                tempcode = numpy.add(20, tempcode)
            
            # code if current trial is congruent
            if sequence[cT] == 10 or sequence[cT] == 12:
                # current trial is congruent
                tempcode = numpy.add(100, tempcode)
            else:
                # current trial is incongruent
                tempcode = numpy.add(200, tempcode)
                
            # code if previous trial is congruent
            if sequence[cT-1] == 10 or sequence[cT-1] == 12:
                # prev trial is congruent
                tempcode = numpy.add(1000, tempcode)
            else:
                # prev trial is incongruent
                tempcode = numpy.add(2000, tempcode)
                
            # CongCongSameL - 1111   30
            # CongCongSameR - 1112   32
            # CongCongDiffL - 1121   31
            # CongCongDiffR - 1122   33
            if tempcode == 1111:
                typecode[cT] = 30
            elif tempcode == 1112:
                typecode[cT] = 32
            elif tempcode == 1121:
                typecode[cT] = 31
            elif tempcode == 1122:
                typecode[cT] = 33
                
            # IncoCongSameL - 2111   34
            # IncoCongSameR - 2112   36
            # IncoCongDiffL - 2121   35
            # IncoCongDiffR - 2122   37
            elif tempcode == 2111:
                typecode[cT] = 34
            elif tempcode == 2112:
                typecode[cT] = 36
            elif tempcode == 2121:
                typecode[cT] = 35
            elif tempcode == 2122:
                typecode[cT] = 37
                
            # CongIncoSameL - 1211   40
            # CongIncoSameR - 1212   42
            # CongIncoDiffL - 1221   41
            # CongIncoDiffR - 1222   43
            elif tempcode == 1211:
                typecode[cT] = 40
            elif tempcode == 1212:
                typecode[cT] = 42
            elif tempcode == 1221:
                typecode[cT] = 41
            elif tempcode == 1222:
                typecode[cT] = 43
        
            # IncoIncoSameL - 2211   44
            # IncoIncoSameR - 2212   46
            # IncoIncoDiffL - 2221   45
            # IncoIncoDiffR - 2222   47
            elif tempcode == 2211:
                typecode[cT] = 44
            elif tempcode == 2212:
                typecode[cT] = 46
            elif tempcode == 2221:
                typecode[cT] = 45
            elif tempcode == 2222:
                typecode[cT] = 47
                
            # CC - [10, 12, 30, 31, 32, 33]
            # IC - [34, 35, 36, 37]
            # CI - [20, 22, 40, 41, 42, 43]
            # II - [44, 45, 46, 47]
            # cong - [10, 12, 30, 31, 32, 33, 34, 35, 36, 37]
            # inco - [20, 22, 40, 41, 42, 43, 44, 45, 46, 47]
    
    # allow ITI to vary
    itilist = [parameters[4]] * len(sequence)
    if not variableiti == 0:
        # varies the ITI using a gaussian distribution
        tempitilist = numpy.random.normal(loc=parameters[4], scale=variableiti, size=len(sequence))
        for cT in range(len(tempitilist)):
            # force the value to be in multiples of the screen refresh rate - assume 120 hz
            tempiti = round(numpy.divide(tempitilist[cT], 8.3),0)
            itilist[cT] = round(numpy.multiply(tempiti, 8.3),0)
    
    for cT in range(len(sequence)): # loop through each trial
        tend = 2
        
        # flanking stimuli are presented concurrent with target
        if parameters[0] == 0:
            tend = 1
            
        for ti in range(tend):
            # loops through once if flanking stimuli are presented concurrent with target
            # loops through twice if flanking stimuli are presented prior to target
            
            for i in range(len(newvarlabels)):
                tout = 0
                
                if newvarlabels[i] == 'stimulusFile':
                    if ti == (tend - 1):
                        # full stim
                        if sequence[cT] == 10:
                            tout = 'congruentleft.png'
                        elif sequence[cT] == 12:
                            tout = 'congruentright.png'
                        elif sequence[cT] == 20:
                            tout = 'incongruentleft.png'
                        elif sequence[cT] == 22:
                            tout = 'incongruentright.png'
                    else:
                        # just the flanking
                        if sequence[cT] == 10:
                            tout = 'flankingleft.png'
                        elif sequence[cT] == 12:
                            tout = 'flankingright.png'
                        elif sequence[cT] == 20:
                            tout = 'flankingright.png'
                        elif sequence[cT] == 22:
                            tout = 'flankingleft.png'
                    
                if newvarlabels[i] == 'stimulusDuration':
                    if ti == (tend - 1):
                        # full stim
                        tout = parameters[1]
                    else:
                        # just the flanking
                        tout = parameters[0]
                    
                if newvarlabels[i] == 'stimulusDuration_min':
                    if ti == (tend - 1):
                        # full stim
                        tout = parameters[2]
                    else:
                        # just the flanking
                        tout = parameters[0]
                        
                if newvarlabels[i] == 'responseWindow_min':
                    if ti == (tend - 1):
                        # full stim
                        tout = parameters[2]
                    else:
                        # just the flanking
                        tout = numpy.subtract(parameters[0],1)
                    
                if newvarlabels[i] == 'responseWindow_max':
                    if ti == (tend - 1):
                        # full stim
                        tout = parameters[3]
                    else:
                        # just the flanking
                        tout = parameters[0]
                    
                if newvarlabels[i] == 'stimulusITI':
                    if ti == (tend - 1):
                        # full stim
                        tout = itilist[cT]
                    else:
                        # just the flanking
                        tout = parameters[0]
                    
                if newvarlabels[i] == 'correctResp':
                    if ti == (tend - 1):
                        # full stim
                        tout = respcode[cT]
                    else:
                        # just the flanking
                        tout = 0
                    
                if newvarlabels[i] == 'stimulusCode':
                    if ti == (tend - 1):
                        # full stim
                        tout = typecode[cT]
                    else:
                        # just the flanking
                        if sequence[cT] == 10:
                            tout = 5
                        elif sequence[cT] == 12:
                            tout = 6
                        elif sequence[cT] == 20:
                            tout = 6
                        elif sequence[cT] == 22:
                            tout = 5
                            
                if len(feedback) > 0:
                    if ti == (tend - 1):
                        # feedback only for target trials
                        if newvarlabels[i] == 'feedbackDuration':
                            tout = feedback[0]
                            
                        if feedback[1] != 0:
                            if newvarlabels[i] == 'correctResponseStimulusFile':
                                tout = 'flankercorrect.png'
                                
                            if newvarlabels[i] == 'correctResponseCode':
                                tout = 50
                                
                        if feedback[2] != 0:
                            if newvarlabels[i] == 'commissionErrorStimulusFile':
                                tout = 'flankererror.png'
                                
                            if newvarlabels[i] == 'commissionErrorCode':
                                tout = 51
                                
                        if feedback[3] != 0:
                            if newvarlabels[i] == 'omissionErrorStimulusFile':
                                tout = 'flankererror.png'
                                
                            if newvarlabels[i] == 'omissionErrorCode':
                                tout = 52
                                
                        if feedback[4] != 0:
                            if newvarlabels[i] == 'impulsiveErrorStimulusFile':
                                tout = 'flankererror.png'
                                
                            if newvarlabels[i] == 'impulsiveErrorCode':
                                tout = 53
                                
                        if feedback[5] != 0:
                            if newvarlabels[i] == 'delayErrorStimulusFile':
                                tout = 'flankererror.png'
                                
                            if newvarlabels[i] == 'delayErrorCode':
                                tout = 54
        
                f.write(str(tout)) # Write data as a string to file
                if (i < len(newvarlabels)): f.write(',') # Include Comma between each item
            f.write('\n') # Write end of line character 
    
    f.close() # close file 
    


if __name__ == "__main__":

    createnogosequence(filout = r'randomsequence.csv', cycles = 1, parameters = [100, 80, 1000, 1500, ['f','j']], variableiti=250, feedback = [])
    