#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import random

filout = 'randomsequence.csv'
cycles = 2
parameters = [100, 80, 900, 1000]

#def createoddballsequence(filout = [], cycles = [], parameters=[]):
    # Example Code:
    # createoddballsequence(filout = 'S:\Data\Raw\randomsequence.csv', cycles = 2, parameters = [100, 80, 900, 1000])
    
# populate headers
newvarlabels = ['stimulusFile','preStimulusInterval','stimulusDuration','stimulusDuration_min','responseWindow_min','responseWindow_max','stimulusITI','postResponseInterval','stimulusXcoord','stimulusYcoord', 'correctResp','stimulusCode','maskFile','feedbackDuration','preFeedbackDelay','endFeedbackWithResponse','correctResponseStimulusFile','correctResponseCode','commissionErrorStimulusFile','commissionErrorCode', 'omissionErrorStimulusFile','omissionErrorCode','impulsiveErrorStimulusFile','impulsiveErrorCode','delayErrorStimulusFile','delayErrorCode']

# Populate database with variable names
f = open(filout, 'w') # Write Variable Labels to Database - Any original file is overwritten
for i in newvarlabels:
    f.write(i)   # Write variable to file
    if (i != newvarlabels[-1]): f.write(', ') # Insert Comma between each variable
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
            tout = 3
            
        if newvarlabels[i] == 'stimulusCode':
            tout = sequence[cT]
        
        f.write(str(tout)) # Write data as a string to file
        if (i != len(newvarlabels)): f.write(', ') # Include Comma between each item
    f.write('\n') # Write end of line character 




f.close() # close file 
