import os
import Engine.xcat as xcat
import Engine.filesync as filesync
from Engine.basicstimuluspresentationengine import Engine
import Engine.generatesequence as generatesequence
import Engine.eegpipe as eegpipe
import numpy
import scipy
from tkinter import Tk     # from tkinter import Tk for Python 3.x
from tkinter.filedialog import askopenfilename

if __name__ == "__main__":
    
    task = Engine()
    task.finished = True
    Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename()  # show an "Open" dialog box and return the path to the selected file
    task.outputfile = filename.split('.')[0] + '.psydat'
    
    
    
    # creates a stimulus locked model ERP.
    [outsum, outvect, xtime] = eegpipe.createsignal(
         Window = [-0.1, 1.0],
         Latency =   [ 0.08,  0.25, 0.35],
         Amplitude = [-0.1,  -0.45, 0.50],
         Width =     [40,       80,  180],
         Shape =     [0,         0,    0],
         Smoothing = [0,         0,    0],
         OverallSmooth = 20, 
         Srate = 250.0)
    
    
    # creates a stimulus locked model ERP.
    [outsum, outvect, xtime] = eegpipe.createsignal(
         Window =    [-0.500,  1.0],
         Latency =   [-0.00, 0.25],
         Amplitude = [-0.5, 0.25],
         Width =     [100,   180],
         Shape =     [0,    0],
         Smoothing = [0,    0],
         OverallSmooth = 20, 
         Srate = 250.0)
    eegpipe.plot([outsum], xtime)
    
    EEG = eegpipe.readUnicornBlack(task.outputfile.split('.')[0] + '.csv')
    EEG = eegpipe.simplefilter(EEG, Filter = 'Notch', Cutoff = [60.0])
    EEG = eegpipe.simplefilter(EEG, Filter = 'Bandpass', Design = 'Butter', Cutoff = [0.5, 30.0], Order=3)
    
    #EEGdist = eegpipe.simpleepoch(EEG, Window = [-0.100, 1.000], Types = [20, 10020])
    EEGdist = eegpipe.simpleepoch(EEG, Window = [-0.500, 0.800], Types = [51, 10051])
    EEGdist = eegpipe.simplebaselinecorrect(EEGdist, Window = [-0.500, -0.200])
    EEGdist = eegpipe.voltagethreshold(EEGdist, Threshold = [-100.0, 100.0], Step = 50.0)
    #EEGdist = eegpipe.antiphasedetection(EEGdist, Threshold=0.0, Window = [0.200, 0.800], Channel=['FZ', 'FC1', 'FC2', 'CZ'], Template=outsum[eegpipe.closestidx(xtime, 0.200):eegpipe.closestidx(xtime, 0.800)])
    EEGdist = eegpipe.antiphasedetection(EEGdist, Threshold=0.0, Window = [-0.150, 0.300], Channel=['FZ', 'FC1', 'FC2', 'CZ'], Template=outsum[eegpipe.closestidx(xtime, -0.150):eegpipe.closestidx(xtime, 0.300)])
    EEGdist = eegpipe.antiphasedetection(EEGdist, Threshold=0.0, Window = [-0.150, 0.300], Channel=['FZ', 'FC1', 'FC2', 'CZ'])
    EEGdist = eegpipe.netdeflectiondetection(EEGdist, Threshold=10, Direction='positive', Window = [-0.150, 0.300],Channel=['FZ', 'FC1', 'FC2', 'CZ'])
    EEGdist = eegpipe.simplefilter(EEGdist, Design = 'savitzky-golay', Order = 6)
    EEGdist = eegpipe.simplebaselinecorrect(EEGdist, Window = [-0.500, -0.200])
    
    window = eegpipe.inspectionwindow()
    #window.inspect(EEGdist, chanlist1=['CZ', 'CPZ', 'PZ'], chanlist2=['PZ'])
    window.inspect(EEGdist, chanlist1=['FZ', 'FC1', 'FC2', 'CZ'], chanlist2=['FC1', 'FC2'])