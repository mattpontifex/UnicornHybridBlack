#!/usr/bin/env python3
# Authors: Matthew B. Pontifex <pontifex@msu.edu>

import os
import sys
import string
import math
import time
import numpy
import codecs
import pickle
import copy 
import matplotlib.mlab as mlab
import scipy.signal
import neurokit2
import matplotlib.pyplot as plt

numpy.seterr(divide='ignore', invalid='ignore')


#https://github.com/gerazov/EEGpy
#https://github.com/hadrienj/EEG
#https://github.com/curiositry/EEGrunt

#https://github.com/neuropsychology/NeuroKit
#pip install neurokit2
#pip install mne



def version():
    print('eegpipe toolbox version 0.1, updated 2020-12-11')
    # 0.1


def plot(invar, timeaxis=False):
    # generic funcction to quickly plot time series data
    
    #isinstance(invar,numpy.ndarray) # is it an array
    multientry = isinstance(invar,list) # is it a list
    if timeaxis is False:
        if multientry:
            timeaxis = range(len(invar[0]))
        else:
            timeaxis = range(len(invar))
    
    if multientry:
        for Y in range(len(invar)):
            plt.plot(timeaxis, invar[Y])
    else:
        try:
            plt.plot(timeaxis, [invar])
        except:
            plt.plot(timeaxis, invar)
            
    
    plt.show()

def checkdefaultsettings(invar, settvar):
    # generic function for checking data inputs
    # first element of settvar is the default
    
    boolset = 0
    if invar == False:
        # user did not specify so use default
        invar = settvar[0]
        boolset = 1
    else:
        # user did specify so run case insensitive check
        for labs in settvar:
            if invar.lower() == labs.lower():
                invar = labs
                boolset = 1
                
        # user may have only put in part of the setting
        if boolset == 0:    
            for labs in settvar:
                if invar.lower() in labs.lower():
                    invar = labs
                    boolset = 1
                    
    # by this point if we still dont have a setting then use the default
    if boolset == 0:
        invar = settvar[0]

    return invar


def voltagethreshold(EEG, Threshold=False, Step=False):
    # function to screen epoched data for voltages or voltage steps that exceed particular thresholds
    # only updates the EEG.reject status with 1 for voltage threshold and 2 for voltage step

    OUTEEG = copy.deepcopy(EEG)
    
    if OUTEEG.trials > 0:
    
        if Threshold != False:
            for cC in range(EEG.nbchan):
                currentchanneldata = EEG.data[cC]
                for cE in range(len(currentchanneldata)):
                    # check high
                    check = [i for i in currentchanneldata[cE] if i >= float(Threshold[1])]
                    if len(check) > 0:
                        OUTEEG.reject[cE] = 1
                    # check low
                    check = [i for i in currentchanneldata[cE] if i <= float(Threshold[0])]
                    if len(check) > 0:
                        OUTEEG.reject[cE] = 1
            
        if Step != False:
            for cC in range(EEG.nbchan):
                currentchanneldata = EEG.data[cC]
                for cE in range(len(currentchanneldata)):
                    check = [i for i in abs(numpy.diff(currentchanneldata[cE])) if i >= float(Step)]
                    if len(check) > 0:
                        OUTEEG.reject[cE] = 2

    return OUTEEG


def simplepsd(EEG, Scale=500, Ceiling=False):
    # simple function to use the mlab.psd function to compute the psd of the data
    # works on both continous and epoched datasets
    
    OUTEEG = copy.deepcopy(EEG)
    
    overlaplength = int(numpy.divide(float(OUTEEG.pnts),3.0))
    if (int(Scale) <= overlaplength):
        overlaplength = int(numpy.divide(int(Scale),2.0))
    
    OUTEEG.freqdata = []
    OUTEEG.freqpnts = 0
    OUTEEG.frequencies = []
        
    # loop through each channel and apply compute the psd
    for i in range(EEG.nbchan):
        
        # if the data is continous or an average then compute for the entire channel
        if OUTEEG.trials == 0:
            _power, _freqs = mlab.psd(x=EEG.data[i], NFFT=int(Scale), Fs=float(EEG.srate), noverlap=overlaplength, sides='onesided', scale_by_freq=True)
            OUTEEG.freqdata.append(_power)
            
        else:
            # the data is epoched the compute for each epoch
            currentepoch = []
            for cE in range(EEG.trials):
                _power, _freqs = mlab.psd(x=EEG.data[i][cE], NFFT=int(Scale), Fs=float(EEG.srate), noverlap=overlaplength, sides='onesided', scale_by_freq=True)
                currentepoch.append(_power)
                
            OUTEEG.freqdata.append(currentepoch)
        
    OUTEEG.frequencies = _freqs
    OUTEEG.freqpnts = len(_power)
    
    if Ceiling != False:
        # apply ceiling frequency
        stopindex = numpy.argmin(abs(numpy.subtract(OUTEEG.frequencies,float(Ceiling))))
        OUTEEG.frequencies = OUTEEG.frequencies[0:stopindex]
        OUTEEG.freqpnts = len(OUTEEG.frequencies)
        
        for i in range(EEG.nbchan):
            if OUTEEG.trials == 0:
                OUTEEG.freqdata[i] = OUTEEG.freqdata[i][0:stopindex]
            else:
                for cE in range(EEG.trials):
                    OUTEEG.freqdata[i][cE] = OUTEEG.freqdata[i][cE][0:stopindex]
                
    return OUTEEG

def simplefilter(EEG, Filter=False, Design=False, Cutoff=False, Order=False):
    # simple function to use scipy signal processing for filtering the data
    # works on both continuous and epoched datasets
    
    OUTEEG = copy.deepcopy(EEG)
    
    Filter = checkdefaultsettings(Filter, ['lowpass', 'highpass', 'bandpass', 'notch'])
    Design = checkdefaultsettings(Design, ['butter', 'savitzky-golay', 'savgol'])
    
    if Design in ['butter']:
        
        if Cutoff == False:
            Cutoff = [1, 30]
        else:
            if len(Cutoff) == 1:
                if Filter == 'lowpass':
                    Cutoff = [0.0, Cutoff[0]]
                elif Filter == 'highpass':
                    Cutoff = [Cutoff[0], 100.0]
                elif Filter == 'bandpass':
                    Cutoff = [0.1, Cutoff[0]]
                elif Filter == 'notch':
                    Cutoff = [Cutoff[0], 100.0]
        
        if Order == False:
            Order = 3
            
        # design the filter
        if Filter == 'notch':
            b, a = scipy.signal.iirnotch(float(Cutoff[0]), float(numpy.divide(Cutoff[0],2)), float(OUTEEG.srate)) # Design notch filter
        elif Filter == 'lowpass':
            b, a = scipy.signal.iirfilter(int(Order), Cutoff[1], btype='lowpass', ftype=Design, fs=float(OUTEEG.srate), output='ba')
        elif Filter == 'highpass':
            b, a = scipy.signal.iirfilter(int(Order), Cutoff[0], btype='highpass', ftype=Design, fs=float(OUTEEG.srate), output='ba')
        elif Filter == 'bandpass':
            b, a = scipy.signal.iirfilter(int(Order), Cutoff, btype='bandpass', ftype=Design, fs=float(OUTEEG.srate), output='ba')
            
        # loop through each channel and apply the filter
        for i in range(EEG.nbchan):
            if Filter == 'notch':
                OUTEEG.data[i] = scipy.signal.filtfilt(b=b, a=a, x=(OUTEEG.data[i]), padtype='constant', padlen=int(math.floor(len(OUTEEG.data[i])/3.0)), method="pad") 
                
            elif Filter == 'lowpass':
                OUTEEG.data[i] = scipy.signal.filtfilt(b=b, a=a, x=(OUTEEG.data[i]), padtype=None) 
                
            elif Filter == 'highpass':
                OUTEEG.data[i] = scipy.signal.filtfilt(b=b, a=a, x=(OUTEEG.data[i]), padtype=None) 
                
            elif Filter == 'bandpass':
                OUTEEG.data[i] = scipy.signal.filtfilt(b=b, a=a, x=(OUTEEG.data[i]), padtype=None) 
     
            
    elif Design in ['savitzky-golay', 'savgol']:   
        
        """Filter a signal using the Savitzky-Golay method.
        Default window size is chosen based on `Sadeghi, M., & Behnia, F. (2018). Optimum window length of
        Savitzky-Golay filters with arbitrary order. arXiv preprint arXiv:1808.10489.
        <https://arxiv.org/ftp/arxiv/papers/1808/1808.10489.pdf>`_.
        """
        window_size = int(numpy.round(EEG.srate / 3))
        if (window_size % 2) == 0:
            window_size + 1  # Make sure it's odd
        
        for i in range(EEG.nbchan):
            #checkindex = numpy.argwhere(numpy.isnan(OUTEEG.data[i]))
            OUTEEG.data[i] = numpy.nan_to_num(OUTEEG.data[i], copy=True, nan=0.0)
            OUTEEG.data[i] = scipy.signal.savgol_filter(OUTEEG.data[i], window_length=int(window_size), polyorder=Order)
        
        
    return OUTEEG
    

def extractamplitude(EEG, Window=False, Approach=False):
    
    Approach = checkdefaultsettings(Approach, ['median', 'mean'])
    
    if Window != False:
        startindex = numpy.argmin(abs(numpy.subtract(EEG.times,numpy.divide(float(Window[0]),1000))))
        stopindex = numpy.argmin(abs(numpy.subtract(EEG.times,numpy.divide(float(Window[1]),1000))))
    else:
        startindex = 0
        stopindex = len(EEG.times)
    
    outputvalues = []
    for cC in range(EEG.nbchan):
        if EEG.trials > 0:
            currentepoch = []
            for cE in range(EEG.trials):
                if Approach == 'mean':
                    currentmean = numpy.nanmean(EEG.data[cC][cE][startindex:stopindex])
                elif Approach == 'median':
                    currentmean = numpy.nanmedian(EEG.data[cC][cE][startindex:stopindex])
                
                currentepoch.append(currentmean)
            outputvalues.append(currentepoch)
        else:
            if Approach == 'mean':
                currentmean = numpy.nanmean(EEG.data[cC][startindex:stopindex])
            elif Approach == 'median':
                currentmean = numpy.nanmedian(EEG.data[cC][startindex:stopindex])
            outputvalues.append(currentmean)
                
    return outputvalues



def simplezwave(EEG, BaselineWindow=False, ddof=1):
    # function that computes the mean and sd over a baseline period and then z scores the entire dataset based upon that information
    
    OUTEEG = copy.deepcopy(EEG)
    
    # only works for epoched datasets
    if OUTEEG.trials > 0:
        
        if BaselineWindow != False:
            startindex = numpy.argmin(abs(numpy.subtract(EEG.times,numpy.divide(float(BaselineWindow[0]),1000))))
            stopindex = numpy.argmin(abs(numpy.subtract(EEG.times,numpy.divide(float(BaselineWindow[1]),1000))))
        else:
            startindex = 0
            stopindex = len(EEG.times)
            

        for cC in range(EEG.nbchan):
            for cE in range(EEG.trials):
                currentmean = numpy.nanmean(EEG.data[cC][cE][startindex:stopindex])
                currentsd = numpy.nanstd(EEG.data[cC][cE][startindex:stopindex], ddof=ddof, dtype=numpy.float64)
                for cP in range(EEG.pnts):
                    # there may be a better way to do this
                    OUTEEG.data[cC][cE][cP] = numpy.divide(numpy.subtract(OUTEEG.data[cC][cE][cP], currentmean), currentsd)
        
    return OUTEEG


def simplemerge(EEG1, EEG2):
    
    OUTEEG = copy.deepcopy(EEG1)
    TEEG2 = copy.deepcopy(EEG2)
        
    OUTEEG.filename = OUTEEG.filename + '_mergedwith_' + TEEG2.filename
    
    if OUTEEG.srate == TEEG2.srate:
        
        if (OUTEEG.trials == 0) and (TEEG2.trials == 0):
            # continuous data
            
            # append data
            for cC in range(TEEG2.nbchan):
                OUTEEG.data[OUTEEG.channels.index(TEEG2.channels[cC])] = numpy.append(OUTEEG.data[OUTEEG.channels.index(TEEG2.channels[cC])], TEEG2.data[cC])
            
            # append samples notation
            OUTEEG.samples = numpy.append(OUTEEG.samples, TEEG2.samples)
                
            # append event markers
            for cC in range(len(TEEG2.events)):
                OUTEEG.events[OUTEEG.eventsegments.index(TEEG2.eventsegments[cC])] = numpy.append(OUTEEG.events[OUTEEG.eventsegments.index(TEEG2.eventsegments[cC])], TEEG2.events[cC])
                
            OUTEEG.pnts = len(OUTEEG.data[0])
            OUTEEG.times = numpy.arange(0,numpy.multiply(OUTEEG.pnts,numpy.divide(1.0,OUTEEG.srate)),numpy.divide(1.0,OUTEEG.srate))
            OUTEEG.freqdata = []
            OUTEEG.freqpnts = 0
            OUTEEG.frequencies = []
            OUTEEG.reject = []
            OUTEEG.stderror = []
            OUTEEG.stddev = []
            OUTEEG.acceptedtrials = 0
            
            
        elif (OUTEEG.trials > 0) and (TEEG2.trials > 0):
            # epoched data
            
            if all(OUTEEG.times == TEEG2.times):
                
                # append data
                OUTEEG.data = numpy.ndarray.tolist(numpy.array(OUTEEG.data))
                TEEG2.data = numpy.ndarray.tolist(numpy.array(TEEG2.data))
                for cC in range(TEEG2.nbchan):
                    for cE in range(TEEG2.trials):
                        OUTEEG.data[OUTEEG.channels.index(TEEG2.channels[cC])].append(TEEG2.data[cC][cE])
                        
                # append event markers
                for cC in range(len(TEEG2.events)):
                    for cE in range(TEEG2.trials):
                        OUTEEG.events[OUTEEG.eventsegments.index(TEEG2.eventsegments[cC])].append(TEEG2.events[cC][cE])
            
                if (len(OUTEEG.freqdata) > 0) and (len(TEEG2.freqdata) > 0):
                    # there is frequency data available
                    if all(OUTEEG.frequencies == TEEG2.frequencies):
                        # append freqdata
                        
                        for cC in range(TEEG2.nbchan):
                            for cE in range(TEEG2.trials):
                                OUTEEG.freqdata[OUTEEG.channels.index(TEEG2.channels[cC])].append(TEEG2.freqdata[cC][cE])
                        
                # append reject vector
                for cP in range(len(TEEG2.reject)):
                    OUTEEG.reject.append(TEEG2.reject[cP])
                
                OUTEEG.samples = []
                OUTEEG.stderror = []
                OUTEEG.stddev = []
                OUTEEG.acceptedtrials = 0
    
    return OUTEEG



def simpleaverage(EEG, Approach=False, BaselineWindow=False):
    
    Approach = checkdefaultsettings(Approach, ['median', 'mean'])
    
    OUTEEG = copy.deepcopy(EEG)
    
    epochs = []
    stderror = []
    stddev = []
    for cC in range(EEG.nbchan):
        currentepoch = []
        for cE in range(EEG.trials):
            # check to see if we have rejected that trial
            if EEG.reject[cE] == 0:
                currentepoch.append(EEG.data[cC][cE])
        tempmat = numpy.vstack(currentepoch)
        
        if Approach == 'mean':
            epochs.append(numpy.nanmean(tempmat, axis=0))
        elif Approach == 'median':
            epochs.append(numpy.nanmedian(tempmat, axis=0))
        
        tempvect = numpy.nanstd(tempmat, axis=0)
        stddev.append(tempvect)
        tempse = []
        for cI in range(len(tempvect)):
            # SD / sqrt(n)
            tempse.append(numpy.divide(tempvect[cI], numpy.sqrt(len(tempmat) - numpy.count_nonzero(numpy.isnan(tempmat[:,cI])))))
        stderror.append(tempse)
     
    OUTEEG.data = epochs
    OUTEEG.stderror = stderror
    OUTEEG.stddev = stddev
    OUTEEG.samples = []
    OUTEEG.trials = 0
    OUTEEG.acceptedtrials = len([v for i,v in enumerate(EEG.reject) if v == 0])
    
    if BaselineWindow != False:
        startindex = numpy.argmin(abs(numpy.subtract(EEG.times,numpy.divide(float(BaselineWindow[0]),1000))))
        stopindex = numpy.argmin(abs(numpy.subtract(EEG.times,numpy.divide(float(BaselineWindow[1]),1000))))
        
        for cC in range(EEG.nbchan):
            if Approach == 'mean':
                OUTEEG.data[cC] = numpy.subtract(OUTEEG.data[cC], numpy.nanmean(OUTEEG.data[cC][startindex:stopindex]))
            elif Approach == 'median':
                OUTEEG.data[cC] = numpy.subtract(OUTEEG.data[cC], numpy.nanmedian(OUTEEG.data[cC][startindex:stopindex]))
    
    # check and see if there is frequency data that we should average
    if len(EEG.freqdata) > 0:
        epochs = []
        for cC in range(EEG.nbchan):
            currentepoch = []
            for cE in range(EEG.trials):
                # check to see if we have rejected that trial
                if EEG.reject[cE] == 0:
                    currentepoch.append(EEG.freqdata[cC][cE])
            tempmat = numpy.vstack(currentepoch)
            
            if Approach == 'mean':
                epochs.append(numpy.nanmean(tempmat, axis=0))
            elif Approach == 'median':
                epochs.append(numpy.nanmedian(tempmat, axis=0))
        
        OUTEEG.freqdata = epochs
    
    
    return OUTEEG

def simplebaselinecorrect(EEG, Window=False, Approach=False):
    
    Approach = checkdefaultsettings(Approach, ['median', 'mean'])
    
    OUTEEG = copy.deepcopy(EEG)
    
    for cC in range(EEG.nbchan):
        for cE in range(EEG.trials):
            if Window == False:
                if Approach == 'mean':
                    OUTEEG.data[cC][cE] = numpy.subtract(EEG.data[cC][cE], numpy.nanmean(EEG.data[cC][cE]))
                elif Approach == 'median':
                    OUTEEG.data[cC][cE] = numpy.subtract(EEG.data[cC][cE], numpy.nanmedian(EEG.data[cC][cE]))
                    
            else:
                startindex = numpy.argmin(abs(numpy.subtract(EEG.times,numpy.divide(float(Window[0]),1000))))
                stopindex = numpy.argmin(abs(numpy.subtract(EEG.times,numpy.divide(float(Window[1]),1000))))
                
                if Approach == 'mean':
                    OUTEEG.data[cC][cE] = numpy.subtract(EEG.data[cC][cE], numpy.nanmean(EEG.data[cC][cE][startindex:stopindex]))
                elif Approach == 'median':
                    OUTEEG.data[cC][cE] = numpy.subtract(EEG.data[cC][cE], numpy.nanmedian(EEG.data[cC][cE][startindex:stopindex]))
    
    return OUTEEG


def simpleepoch(EEG, Window=False, Types=False):
    # Convert a continuous EEG dataset to epoched data by extracting data time locked to specified event types.

    OUTEEG = copy.deepcopy(EEG)
    stimlistvalue = [v for i,v in enumerate(OUTEEG.events[0]) if v > 0]
    stimlistindex = [i for i,v in enumerate(OUTEEG.events[0]) if v > 0]
    
    # if no types are specified then use all trial types
    if Types == False:
        Types = numpy.unique(stimlistvalue)

    if Window != False:
        
        # figure out how big the span needs to be
        epochsamples = int(numpy.floor(numpy.multiply(numpy.divide(numpy.subtract(float(Window[1]),float(Window[0])),float(1000.0)),OUTEEG.srate)))
        OUTEEG.times = numpy.arange(numpy.divide(Window[0],1000.0), numpy.divide(Window[1],1000.0),numpy.divide(1.0,OUTEEG.srate))
        epochindexmin = numpy.multiply(numpy.divide(Window[0],1000.0), OUTEEG.srate)
        
        # epoch data
        epochs = []
        for cC in range(OUTEEG.nbchan):
            currentepoch = []
            for cE in range(len(stimlistvalue)):
                # if the event code is in the list of types to epoch
                if stimlistvalue[cE] in Types:
                    epochindexstart = int(numpy.sum([stimlistindex[cE],int(epochindexmin)]))
                    epochindexstop = int(numpy.sum([epochindexstart,int(epochsamples)]))
                    activeepoch = [numpy.nan]*epochsamples
                    
                    # determine if adjustments need to be made to retain a trial
                    epochindexstartadj = 0
                    if (epochindexstart < 0):
                        epochindexstartadj = int(abs(epochindexstart))
                        epochindexstart = 0
                        
                    epochindexstopadj = 0
                    if (epochindexstop >= EEG.pnts):
                        epochindexstopadj = epochindexstop - EEG.pnts
                        epochindexstop = EEG.pnts
                        
                    # plug in data
                    activeepoch[0+epochindexstartadj:epochsamples-epochindexstopadj] = OUTEEG.data[cC][epochindexstart:epochindexstop]
            
                    currentepoch.append(activeepoch)
                    
            epochs.append(currentepoch)
            
        # first index will correspond with channel
        # second index will correspond with epoch
        OUTEEG.data = copy.deepcopy(epochs)
            
        # epoch event codes
        events = []     
        for cC in range(len(EEG.events)):
            currentepoch = []
            for cE in range(len(stimlistvalue)):
                # if the event code is in the list of types to epoch
                if stimlistvalue[cE] in Types:
                    epochindexstart = int(numpy.sum([stimlistindex[cE],int(epochindexmin)]))
                    epochindexstop = int(numpy.sum([epochindexstart,int(epochsamples)]))
                    activeepoch = [numpy.nan]*epochsamples
                    
                    # determine if adjustments need to be made to retain a trial
                    epochindexstartadj = 0
                    if (epochindexstart < 0):
                        epochindexstartadj = int(abs(epochindexstart))
                        epochindexstart = 0
                        
                    epochindexstopadj = 0
                    if (epochindexstop >= EEG.pnts):
                        epochindexstopadj = epochindexstop - EEG.pnts
                        epochindexstop = EEG.pnts
                        
                    # plug in data
                    activeepoch[0+epochindexstartadj:epochsamples-epochindexstopadj] = OUTEEG.events[cC][epochindexstart:epochindexstop]
            
                    currentepoch.append(activeepoch)
                    
            events.append(currentepoch)
        OUTEEG.events = copy.deepcopy(events)
        
        
        samples = []
        for cE in range(len(stimlistvalue)):
            # if the event code is in the list of types to epoch
            if stimlistvalue[cE] in Types:
                epochindexstart = int(numpy.sum([stimlistindex[cE],int(epochindexmin)]))
                epochindexstop = int(numpy.sum([epochindexstart,int(epochsamples)]))
                activeepoch = [numpy.nan]*epochsamples
                
                # determine if adjustments need to be made to retain a trial
                epochindexstartadj = 0
                if (epochindexstart < 0):
                    epochindexstartadj = int(abs(epochindexstart))
                    epochindexstart = 0
                    
                epochindexstopadj = 0
                if (epochindexstop >= EEG.pnts):
                    epochindexstopadj = epochindexstop - EEG.pnts
                    epochindexstop = EEG.pnts
                    
                # plug in data
                activeepoch[0+epochindexstartadj:epochsamples-epochindexstopadj] = OUTEEG.samples[epochindexstart:epochindexstop]
        
                samples.append(activeepoch)
        OUTEEG.samples = copy.deepcopy(samples)
        OUTEEG.pnts = len(OUTEEG.times)
        OUTEEG.trials = len(samples)
        OUTEEG.reject = [0] * OUTEEG.trials

    return OUTEEG


def saveset(EEG, fileout):
    
    # force file type
    head, tail = os.path.split(fileout)
    fileout = head + os.path.sep + tail.split('.')[0] + '.eeg'
    
    with open(fileout, 'wb') as pickle_file:
        pickle.dump(EEG, pickle_file)
    
    
def loadset(inputfile):
    
    # force file type
    head, tail = os.path.split(inputfile)
    inputfile = head + os.path.sep + tail.split('.')[0] + '.eeg'
    
    if (os.path.isfile(inputfile)):
    
        EEG = []
        with open(inputfile, 'rb') as pickle_file:
            EEG = pickle.load(pickle_file)
            
        return EEG
    

def readUnicornBlack(inputfile):
    # function to read in data from the UnicornHybridBlack
    
    head, tail = os.path.split(inputfile)
    if (os.path.isfile(inputfile)): 
    
        # create structure
        EEG = eeglabstructure()
        
        # plug in known values
        EEG.nbchan = 8
        EEG.trials = 0
    
        # read in the data
        dcontents = open(inputfile, encoding="utf-8").readlines()
        
        # check file version
        if 'UnicornPy_2020.05.30.0' in dcontents[0]:
            
            #tempst = dcontents[5].split('=')[1]
            #tempst = tempst.translate({ord(c): None for c in string.whitespace})
            #EEG.filename = tempst.split('\\')[1]
            EEG.filename = tail.split('.')[0]
            EEG.filepath = head
            
            tempst = dcontents[2].split('=')[1]
            EEG.srate = float(tempst.translate({ord(c): None for c in string.whitespace}))
            
            # extract data 
            deveryline = []
            for dinfo in range(7, len(dcontents)):
                deveryline.append(dcontents[dinfo].split(',')) 
            temparray = numpy.asarray(deveryline, dtype=numpy.float64)
            EEG.samples = temparray[:,-1]
            EEG.events = [[0]*len(temparray)]
            EEG.eventsegments = ['Type']
            
            # populate list of EEG channels
            #tempst = dcontents[3].split('=')[1]
            #EEG.nbchan = int(tempst.translate({ord(c): None for c in string.whitespace}))
            tempst = dcontents[6].split(',')
            for cchan in range(EEG.nbchan):
                EEG.channels.append(tempst[cchan].translate({ord(c): None for c in string.whitespace}))
                EEG.data.append(temparray[:, cchan])
        
        # check to see if there are any events
        if (os.path.isfile(inputfile +  'e')): 
            # read in the fitbit data
            dcontents = open(inputfile +  'e', encoding="utf-8").readlines()
        
            # check file version
            if 'UnicornPy_2020.05.30.0' in dcontents[0]:
                
                for dinfo in range(4, len(dcontents)):
                    currentline = dcontents[dinfo].split(',')
                    currentindex = numpy.argmin(abs(numpy.subtract(EEG.samples,float(currentline[0]))))
                    EEG.events[0][currentindex] = float(currentline[1])
                    
        # convert samples to time    
        EEG.times = numpy.multiply(EEG.samples, numpy.divide(1.0, EEG.srate))
        EEG.pnts = len(EEG.times)
        EEG.checkset()
        
        # see if there is behavioral data available
        if (os.path.isfile(head + os.path.sep + tail.split('.')[0] + '.psydat')): 
            EEG = mergetaskperformance(EEG, head + os.path.sep + tail.split('.')[0] + '.psydat')
    
        return EEG
    

def mergetaskperformance(EEG, filein):
    OUTEEG = copy.deepcopy(EEG)
    
    #filein = '/Users/mattpontifex/Downloads/attachments/OBAva.psydat'
    
    if os.path.isfile(filein):
        # read in the data
        dcontents = open(filein).readlines()
        
        # check file version
        if 'PsychoPy_Engine_3' in dcontents[0]:
            
            # setup event lists
            #['Trial','Event','Duration','ISI','ITI','Type','Resp','Correct','Latency','ClockLatency','Trigger','MinRespWin','MaxRespWin','Stimulus']
            labline = dcontents[4].split()
            for lab in labline:
                try:
                    currentindex = OUTEEG.eventsegments.index(lab)
                except:
                    OUTEEG.eventsegments.append(lab)
                    OUTEEG.events.append([0]*len(OUTEEG.events[0]))
                
            # obtain list of events in the file
            stimlistvalue = [v for i,v in enumerate(OUTEEG.events[0]) if v > 0]
            stimlistindex = [i for i,v in enumerate(OUTEEG.events[0]) if v > 0]
            
            # cycle through event lines
            currenteventplace = 0
            for dinfo in range(6, len(dcontents)):
                currentline = dcontents[dinfo].split()
                # make sure it is not the end of the file
                if not 'taskruntime' in currentline[0]:
                    # make sure that it is an event we want marked
                    if float(currentline[labline.index('Type')]) != 0:
                        # make sure that it is a stimulus
                        if currentline[labline.index('Event')] == 'Stimulus':
                            # find next event that meets this criteria - shouldnt have to though
                            while float(currentline[labline.index('Type')]) != float(stimlistvalue[currenteventplace]):
                                currenteventplace = currenteventplace + 1
                            
                            for lab in labline:
                                # find associated list
                                currentlabindex = OUTEEG.eventsegments.index(lab)
                                sampleindex = stimlistindex[currenteventplace]
                                
                                if lab in ['Trial','Duration','ISI','ITI','Correct','Latency','ClockLatency','MinRespWin','MaxRespWin']:
                                    if currentline[labline.index(lab)] != 'nan':
                                        OUTEEG.events[currentlabindex][sampleindex] = float(currentline[labline.index(lab)])
            
                                if lab in ['Event','Resp','Stimulus']:
                                    if currentline[labline.index(lab)] != 'nan':
                                        OUTEEG.events[currentlabindex][sampleindex] = currentline[labline.index(lab)]
                            
                            # adjust stimulus type based on accuracy
                            # Correct Trials are increased by 10,000 
                            # Error of Commission Trials are increased by 50,000
                            # Error of Omission Trials are increased by 60,000
                            # (i.e., type 27 would become 10,027 if correct; 50,027 if an
                            # incorrect response was made; and 60,027 if an incorrect
                            # non-response occurred)
                            if float(currentline[labline.index('Correct')]) == float(1.0):
                                # correct trial
                                OUTEEG.events[0][sampleindex] = numpy.sum([OUTEEG.events[0][sampleindex], 10000])
                            elif float(currentline[labline.index('Correct')]) == float(0.0):
                                # error trial
                                if currentline[labline.index('Resp')] == 'nan':
                                    # error of omission
                                    OUTEEG.events[0][sampleindex] = numpy.sum([OUTEEG.events[0][sampleindex], 60000])
                                else:
                                    # error of comission
                                    OUTEEG.events[0][sampleindex] = numpy.sum([OUTEEG.events[0][sampleindex], 50000])
                            
                            # add response event information
                            # Correct Response are 2500
                            # Error of Commission Resonse are 3500
                            if currentline[labline.index('Resp')] != 'nan':
                                # RT in ms / 1000 times the sample rate gives you the number of samples
                                backsample = int(numpy.floor(numpy.multiply(numpy.divide(float(currentline[labline.index('Latency')]),1000), float(OUTEEG.srate))))
                                
                                if float(currentline[labline.index('Correct')]) == float(1.0):
                                    OUTEEG.events[0][sampleindex+backsample] = float(2500.0)
                                else:
                                    OUTEEG.events[0][sampleindex+backsample] = float(3500.0)
                                OUTEEG.events[OUTEEG.eventsegments.index('Event')][sampleindex+backsample] = 'Response'
                                OUTEEG.events[OUTEEG.eventsegments.index('Trial')][sampleindex+backsample] = float(currentline[labline.index('Trial')])
                                
                            # increment events to next mark
                            currenteventplace = currenteventplace + 1
    
        return OUTEEG
    else:
        return EEG


class eeglabstructure():
    # class to generally mimic the layout of EEGLAB
    
    def __init__(self):
        
        self.filename = ''
        self.filepath = ''
        
        self.data = []
        self.pnts = 0
        self.times = []
        self.samples = []
        
        self.freqdata = []
        self.freqpnts = 0
        self.frequencies = []
        
        self.nbchan = 0
        self.channels = []
        
        self.trials = 0
        self.srate = 250.0
        self.events = [] 
        self.eventsegments = []
        
        self.icawinv = []
        self.icasphere = []
        self.icaweights = []
        self.icaact = []
        
        self.reject = []
        self.stderror = []
        self.stddev = []
        self.acceptedtrials = 0
        
        self.comments = ''
        self.averef = 'no'
        self.ref = 'common'
        self.history = []
        
    def checkset(self):
        
        self.srate = float(self.srate)
        
        if (self.data != []):
            self.nbchan = len(self.data)
            if len(self.times) == 0:
                self.times = numpy.arange(0,numpy.multiply(self.pnts,numpy.divide(1.0,self.srate)),numpy.divide(1.0,self.srate))
        else:
            self.pnts = 0
            self.nbchan = 0
            self.times = []
            
        if (self.freqdata != []):
            self.freqpnts = len(self.freqdata[0])
            self.nbchan = len(self.freqdata)
        else:
            self.freqpnts = 0
            


            
# # # # #
# DEBUG #
if __name__ == "__main__":
    
    # notes
    # Can Read in Unicorn Data
    # Can Merge Behavior and Recode Trial Type Codes based on accuracy
    # Can Save and Load the EEG structure
    # Filter is ready
    # PSD is ready
    # Epoch Based on Trial Types is ready
    # Baseline Correct is ready
    # Create Averages is ready
    # Transform to Z score based on activity within specified period is ready
    # Merge multiple files together is ready
    
    
    
    # Still need to build
    
     
    # Detect Artifacts
    # Assess Noise
    # Collapse Electrodes
    # Remove Bad Electrodes
    # interchannel relationships - detect deviant channel? - convolution?
    
    
    
    
    #EEG = eeglabstructure()
    
    #EEG.srate = 250.0
    #for i in range(6):
    #    EEG.data.append(neurokit2.ppg_simulate(duration=10, sampling_rate=EEG.srate, heart_rate=numpy.random.randint(30,120,1)[0]))
        
    #EEG.checkset()
    
    
    EEG = readUnicornBlack('/Users/mattpontifex/Downloads/testdata/VEP090p.csv')
    
    EEG = simplefilter(EEG, Filter='Notch', Cutoff=[60.0])
    EEG = simplefilter(EEG, Filter='Bandpass', Design='Butter', Cutoff=[1,25], Order=3)
     
    #EEG = simpleepoch(EEG, Window=[-500, 1000], Types=[10008])
    #EEG = simplebaselinecorrect(EEG, Window=[-100.0, 0.0])
    #EEG = voltagethreshold(EEG, Threshold=[-100.0, 100.0], Step=50.0)
    #EEG = simplepsd(EEG, Scale=500, Ceiling=30.0)
    # 
    #EEG = simplefilter(EEG, Design='savitzky-golay', Order=4) # smoothes the shit out of the data
    
    #EEG = simplezwave(EEG, BaselineWindow=[-500.0, 0.0]) # amplitude in microvolts to z scored amplitude
    
    #EEG = simpleaverage(EEG, Approach='Mean', BaselineWindow=[-100, 0])
    
    
    #plot(EEG.data,EEG.times)
    
    
    #plot(EEG.freqdata,EEG.frequencies)
    
    #tempvect = extractamplitude(EEG, Window=[250, 600], Approach='Mean')
    #plot([tempvect])
    #EEG.channels
    #plot([EEG.data[4]])
    #plot([EEG.data[4]])
    #plot(EEG.data)
    
    #saveset(EEG, '/Users/mattpontifex/Downloads/attachments/OBAva.eeg')
    
    #EEG = loadset('/Users/mattpontifex/Downloads/attachments/OBAva.eeg')
    
    
    #tempmat = numpy.vstack(EEG.data[0])
    #plot([tempmat.transpose()])
    
    # see what events are available
    #[v for i,v in enumerate(EEG.events[0]) if v > 0]
    
    
    EEG = simpleepoch(EEG, Window = [-200.0, 600.0], Types = [10005, 10006])
    EEG = simplebaselinecorrect(EEG, Window = [-100.0, 0.0])
    EEG = voltagethreshold(EEG, Threshold = [-100.0, 100.0], Step = 50.0)
    EEG = simplepsd(EEG, Scale = 500, Ceiling = 30.0)
    EEG = simplefilter(EEG, Design = 'savitzky-golay', Order = 4)
    EEG = simplezwave(EEG, BaselineWindow = [-200.0, 0.0])
    EEG = simpleaverage(EEG, Approach = 'Mean', BaselineWindow = [-100, 0])
    #saveset(EEG, task.outputfile)
    
    plot(EEG.data,EEG.times)