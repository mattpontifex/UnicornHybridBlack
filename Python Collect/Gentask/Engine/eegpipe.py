#!/usr/bin/env python3
# Authors: Matthew B. Pontifex <pontifex@msu.edu>

import os
import copy 
import string
import math
import numpy
numpy.seterr(divide='ignore', invalid='ignore')
import pickle
import pandas
import datetime
import scipy
import scipy.signal
import scipy.interpolate
from scipy.stats import pearsonr
from scipy import ndimage
import matplotlib
import matplotlib.pyplot
import matplotlib.animation
import matplotlib.image
import matplotlib.colors
import matplotlib.mlab as mlab
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
from matplotlib.widgets import Button

#pip install git+git://github.com/tknapen/FIRDeconvolution.git

try:
    from fir.FIRDeconvolution import FIRDeconvolution
    firmodule = True
except:
    firmodule = False
    
#pip install lmfit
from lmfit import minimize, Parameters
#pip install PeakUtils
import peakutils
from peakutils.plot import plot as peakutilspplot

#import neurokit2

#https://github.com/neuropsychology/NeuroKit
#pip install neurokit2
#pip install mne

#from IPython import embed as shell

# %matplotlib inline
#%matplotlib qt


def version():
    print('eegpipe toolbox version 0.1, updated 2020-12-29')
    # 0.1




def fill(data, invalid=None):
    """
    Replace the value of invalid 'data' cells (indicated by 'invalid') 
    by the value of the nearest valid data cell

    Input:
        data:    numpy array of any dimension
        invalid: a binary array of same shape as 'data'. True cells set where data
                 value should be replaced.
                 If None (default), use: invalid  = np.isnan(data)

    Output: 
        Return a filled array. 
    """
    #import numpy as np
    #import scipy.ndimage as nd

    if invalid is None: invalid = numpy.isnan(data)

    ind = ndimage.distance_transform_edt(invalid, return_distances=False, return_indices=True)
    return data[tuple(ind)]


    
def crushcolormap(cmap=False, ratio=False, outsize=False):
    if cmap == False:
        cmap = 'viridis'
        
    mapsize = 256
    
    if ratio == False:
        ratio = [0.5,1.5,1,1,3],
        
    if outsize == False:
        outsize = 512
    
    cmapBig = matplotlib.pyplot.cm.get_cmap(cmap, mapsize)
    newcmap = cmapBig(numpy.linspace(0, 1, mapsize))
    mapsplit = len(ratio)+1
    splitpoints = numpy.linspace(0, 1, mapsplit)
    splitsize = numpy.floor(numpy.divide(mapsize,mapsplit))
    
    mapcolors = []
    for cL in range(mapsplit-1):
    
        seg = cmapBig(numpy.linspace(splitpoints[cL], splitpoints[cL+1], int(numpy.ceil(numpy.multiply(splitsize, ratio[cL])))))
        if len(mapcolors) == 0:
            mapcolors = copy.deepcopy(seg)
        else:
            tempseg1 = copy.deepcopy(mapcolors)
            tempseg2 = copy.deepcopy(seg)
            mapcolors = numpy.append(tempseg1, tempseg2, axis=0)
        
    #newcmap = ListedColormap(mapcolors) 
    newcmap = LinearSegmentedColormap.from_list("", mapcolors, outsize) 
    
    return newcmap
    

def crushparula(mapsize=False):
    
    if mapsize == False:
        mapsize = 256
        
    segs = ['#00004B', '#1C2C75', '#38598C', '#2B798B', '#1E9B8A', '#85D54A', '#FDE725', '#F9FB0E'] 
    
    newcmap = LinearSegmentedColormap.from_list("", segs, mapsize) 
    
    return newcmap
    
def eggpad(Channels, Amplitude):
    
    overallchanlabs = ['NZ', 'IZ', 'F9', 'F10', 'T9', 'T10', 'P9', 'P10']
    for cChan in range(len(overallchanlabs)):
        try:
            matchindex = Channels.index(overallchanlabs[cChan].upper())
        except:
            Channels.append(overallchanlabs[cChan])
            Amplitude.append(0.0)
    
    return [Channels, Amplitude]


def eggheadplot(Channels, Amplitude, Steps=512, Scale=False, Colormap=False, Method='cubic', Complete=True, Style='Full', TickValues=False, BrainOpacity=0.2, Title=False, Electrodes=True, **kwargs):

    Method = checkdefaultsettings(Method, ['cubic', 'linear'])
    Style = checkdefaultsettings(Style, ['Full', 'Outline', 'None'])
    
    # check size 
    multiinput = any(isinstance(el, list) for el in Channels)
    nrow = 1;
    ncol = 1;
    if multiinput:
        if len(Channels) < 4:
            ncol = len(Channels);
        else:
            nrow = int(numpy.ceil(numpy.divide(len(Channels),4)))
            ncol = 4
        
        fig, ax = matplotlib.pyplot.subplots(nrow,ncol)
    else:
        fig, ax = matplotlib.pyplot.subplots(nrow,ncol)
    
    fig.tight_layout()
    #fig.patch.set_facecolor('#FFFFFF')
    try:
        fig.canvas.window().statusBar().setVisible(False) 
    except:
        pass
    
    if Title == False:
        if multiinput:
            Title = []
            for cA in range(len(Channels)):
                Title.append(' ')
        else:
            Title = ' '
    
    if multiinput:
        for cA in range(len(Channels)):
            ax[cA].set_title(Title[cA] + '\n')
    else:
        ax.set_title(Title)
    
    if Colormap == False:
        Colormap = matplotlib.pyplot.cm.viridis
        
    if multiinput:
        #for axs in ax.flat:
        #    im = axs.imshow(numpy.random.random((10,10)), vmin=Scale[0], vmax=Scale[1])
        cbar_ax = fig.add_axes([0.323, 0.15, 0.4, 0.035])
    else:
        #im = ax.imshow(numpy.random.random((10,10)), vmin=Scale[0], vmax=Scale[1])
        pos1 = ax.get_position()
        cbar_ax = fig.add_axes([0.323, pos1.y0-0.05, 0.4, 0.035])
    
    # configure ticks
    if TickValues == False:
        TickValues= matplotlib.ticker.AutoLocator()
        
    norm = matplotlib.colors.Normalize(vmin=Scale[0], vmax=Scale[1])
    fig.colorbar(matplotlib.cm.ScalarMappable(cmap=Colormap, norm=norm), cax=cbar_ax, orientation='horizontal', ticks=TickValues)
    
    if multiinput:
        for cA in range(len(Channels)):
            eggheadplot_sub(Channels[cA], Amplitude[cA], ax[cA], Steps=Steps, Scale=Scale, Colormap=Colormap, Method=Method, Complete=Complete, Style=Style, BrainOpacity=BrainOpacity, Electrodes=Electrodes)
    
    else:
        eggheadplot_sub(Channels, Amplitude, ax, Steps=Steps, Scale=Scale, Colormap=Colormap, Method=Method, Complete=Complete, Style=Style, BrainOpacity=BrainOpacity, Electrodes=Electrodes)
        
    matplotlib.pyplot.show()


def eggheadplot_sub(Channels, Amplitude, ax=None, Steps=512, Scale=False, Colormap=False, Method='cubic', Complete=True, Style='Full', BrainOpacity=0.2, Electrodes=True, **kwargs):
    
    Method = checkdefaultsettings(Method, ['cubic', 'linear'])
    Style = checkdefaultsettings(Style, ['Full', 'Outline', 'None'])
    
    matplotlib.pyplot.sca(ax)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    matplotlib.pyplot.tick_params(
        axis='both',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        left=False,      # ticks along the left edge are off
        right=False,      # ticks along the right edge are off
        bottom=False,      # ticks along the bottom edge are off
        top=False,         # ticks along the top edge are off
        labelleft=False,
        labelbottom=False) # labels along the bottom edge are off
    
    #ax.patch.set_facecolor('#FFFFFF')
    
    # figure out where the data goes
    overallchanlabs = ['NZ','IZ','P9','P10','T9','T10','F9','F10', 'FP1','FPZ','FP2','AFP5','AFP3','AFP1','AFP2','AFP4','AFP6','AF7','AF7h','AF5','AF5h','AF3','AF1','AF1h','AFZ','AF2h','AF2','AF4','AF6h','AF6','AF8h','AF8','AFF7','AFF7h','AFF5','AFF5h','AFF3','AFF3h','AFF1h','AFF2h','AFF4h','AFF4','AFF6h','AFF6','AFF8h','AFF8','F7','F7h','F5','F5h','F3','F3h','F1','F1h','FZ','F2h','F2','F4h','F4','F6h','F6','F8h','F8','FFT7','FFT7h','FFC5','FFC5h','FFC3','FFC3h','FFC1','FFC1h','FFCZ','FFC2h','FFC2','FFC4h','FFC4','FFC6h','FFC6','FFT8h','FFT8','FT7','FT7h','FC5','FC5h','FC3','FC3h','FC1','FC1h','FCZ','FC2h','FC2','FC4h','FC4','FC6h','FC6','FT8h','FT8','FTT7','FTT7h','FCC5','FCC5h','FCC3','FCC3h','FCC1','FCC1h','FCCZ','FCC2h','FCC2','FCC4h','FCC4','FCC6h','FCC6','FTT8h','FTT8','T7','T7h','C5','C5h','C3','C3h','C1','C1h','CZ','C2h','C2','C4h','C4','C6h','C6','T8h','T8','TTP7','TTP7h','CCP5','CCP5h','CCP3','CCP3h','CCP1','CCP1h','CCPZ','CCP2h','CCP2','CCP4h','CCP4','CCP6h','CCP6','TTP8h','TTP8','TP7','TP7h','CP5','CP5h','CP3','CP3h','CP1','CP1h','CPZ','CP2h','CP2','CP4h','CP4','CP6h','CP6','TP8h','TP8','TPP7','TPP7h','CPP5','CPP5h','CPP3','CPP3h','CPP1','CPP1h','CPPZ','CPP2h','CPP2','CPP4h','CPP4','CPP6h','CPP6','TPP8h','TPP8','P7','P7h','P5','P5h','P3','P3h','P1','P1h','PZ','P2h','P2','P4h','P4','P6h','P6','P8h','P8','PPO7','PPO7h','PPO5','PPO5h','PPO3','PPO3h','PPO1','PPO1h','PPOZ','PPO2h','PPO2','PPO4h','PPO4','PPO6h','PPO6','PPO8h','PPO8','PO7','PO7h','PO5','PO5h','PO3','PO3h','PO1','POZ','PO2','PO4h','PO4','PO6h','PO6','PO8h','PO8','POO5','POO3','POO1','POOZ','POO2','POO4','POO6','O1','O1h','OZ','O2h','O2','MiPf','MiCe','MiPa','MiOc','LLPf','LLFr','LLTe','LLOc','RLPf','RLFr','RLTe','RLOc','LMPf','LDFr','LDCe','LDPa','LMOc','RMPf','RDFr','RDCe','RDPa','RMOc','LMFr','LMCe','RMFr','RMCe']
    overallchanlabsupper = copy.deepcopy(overallchanlabs)
    overallchanlabsupper = [x.upper() for x in overallchanlabsupper]
    
    overalltempxvect = [-3,-3,-361,355,-380,370,-361,355, -79,-3,73,-148,-97,-42,36,91,142,-216,-182,-148,-113,-79,-57,-34,-3,28,51,73,107,142,176,210,-235,-209,-184,-150,-113,-79,-36,30,73,107,144,178,203,229,-254,-235,-216,-187,-155,-116,-79,-37,-3,31,73,110,149,182,210,230,248,-282,-256,-229,-198,-164,-126,-85,-44,-3,38,79,120,158,193,223,250,276,-309,-278,-245,-211,-178,-134,-91,-47,-3,41,86,128,172,205,238,272,303,-331,-295,-260,-224,-185,-142,-96,-49,-3,44,90,136,179,218,255,289,325,-349,-315,-278,-238,-198,-147,-100,-51,-3,45,94,141,192,233,272,309,343,-352,-315,-280,-243,-199,-149,-100,-52,-3,46,94,143,193,236,274,309,347,-341,-311,-280,-238,-198,-148,-100,-50,-3,44,94,142,192,232,275,305,335,-309,-277,-248,-214,-175,-134,-90,-47,-3,41,84,128,170,208,242,271,303,-258,-238,-219,-189,-157,-125,-80,-42,-3,36,74,119,151,183,213,233,252,-215,-197,-176,-148,-115,-79,-54,-28,-3,22,48,73,110,142,170,191,209,-172,-156,-141,-109,-77,-41,-22,-3,16,35,71,103,135,150,166,-125,-93,-41,-3,35,87,119,-79,-41,-3,35,73,-3,-3,-3,-3,-196,-300,-341,-215,190,294,335,209,-79,-198,-238,-214,-91,73,193,233,208,86,-91,-149,86,143]
    overalltempyvect = [415,-465,-380,-380,28,28,337,337, 398,402,398,387,372,370,370,372,387,359,346,343,341,337,337,337,337,337,337,337,341,343,346,359,332,324,317,313,311,308,308,308,308,311,313,317,324,332,305,296,291,286,282,279,276,274,273,274,276,279,282,286,291,296,305,252,239,228,219,213,209,205,200,199,200,205,209,213,219,228,239,252,199,176,162,150,143,137,134,129,126,129,134,137,143,150,162,176,199,114,99,86,77,70,64,60,56,52,56,60,64,70,77,86,99,114,28,13,6,1,-5,-10,-16,-18,-21,-18,-16,-10,-5,1,6,13,28,-62,-65,-67,-69,-71,-72,-74,-75,-75,-75,-74,-72,-71,-69,-67,-65,-62,-151,-147,-141,-137,-136,-133,-132,-130,-129,-130,-132,-133,-136,-137,-141,-147,-151,-220,-210,-204,-200,-195,-191,-188,-185,-183,-185,-188,-191,-195,-200,-204,-210,-220,-289,-274,-266,-260,-255,-248,-243,-239,-237,-239,-243,-248,-255,-260,-266,-274,-289,-328,-318,-309,-304,-299,-295,-293,-291,-289,-291,-293,-295,-299,-304,-309,-318,-328,-367,-356,-350,-345,-344,-342,-342,-341,-342,-342,-344,-345,-350,-356,-367,-384,-371,-369,-369,-369,-371,-384,-393,-395,-397,-395,-393,402,-21,-183,-397,345,176,-151,-328,345,176,-151,-328,308,219,1,-200,-293,308,219,1,-200,-293,134,-72,134,-72]
    
    chanvect = []
    zvect = []
    xvect = []
    yvect = []
    for cChan in range(len(Channels)):
        try:
            matchindex = overallchanlabsupper.index(Channels[cChan].upper())
        except:
            matchindex = 0
        if matchindex > 0:
            chanvect.append(overallchanlabs[matchindex])
            xvect.append(overalltempxvect[matchindex])
            yvect.append(overalltempyvect[matchindex])
            zvect.append(Amplitude[cChan])
        
    expand = 0.05
    # Adjust rostral sensors vertically
    temparray = ['NZ','AFP5','FP1','FP1h','FPZ','FP2h','FP2','AFP6','AF7','AFF7','F7','FFT7','AF8','AFF8','F8','FFT8','F9','F10','AF7','AFF7','F7','FFT7','AF8','AFF8','F8','FFT8','MiPf','LLPf','RLPf'];
    for cChan in range(len(chanvect)):
        try:
            matchindex = temparray.index(chanvect[cChan])
        except:
            matchindex = 0
        if matchindex > 0:
            yvect[cChan] = yvect[cChan] + numpy.multiply(yvect[cChan], expand)
            
    expand = 0.004
    # Adjust caudal sensors vertically
    temparray = ['IZ','POO5','O1','O1h','OZ','O2h','O2','POO6','TPP7','P7','PPO7','PO7','TPP8','P8','PPO8','PO8','MiOc','P9','P10']
    for cChan in range(len(chanvect)):
        try:
            matchindex = temparray.index(chanvect[cChan])
        except:
            matchindex = 0
        if matchindex > 0:
            yvect[cChan] = yvect[cChan] + numpy.multiply(yvect[cChan], expand)
            
    expand = 0.065
    # Adjust caudal sensors vertically
    temparray = ['LLOc','RLOc']
    for cChan in range(len(chanvect)):
        try:
            matchindex = temparray.index(chanvect[cChan])
        except:
            matchindex = 0
        if matchindex > 0:
            yvect[cChan] = yvect[cChan] + numpy.multiply(yvect[cChan], expand)
            
    expand = 0.05
    # Adjust lateral sensors horizontally
    temparray = ['AFP5','AFP6','AF7','AFF7','F7','FFT7','AF8','AFF8','F8', 'F9', 'F10','FFT8','POO5','POO6','TPP7','P7','PPO7','PO7','TPP8','P8','PPO8','PO8','FT7','FTT7','T7','TTP7','TP7','FT8','FTT8','T8','TTP8','TP8','LLPf','RLPf','LLFr','RLFr','LLTe','RLTe','LLOc','RLOc', 'P9','P10','T9','T10']
    for cChan in range(len(chanvect)):
        try:
            matchindex = temparray.index(chanvect[cChan])
        except:
            matchindex = 0
        if matchindex > 0:
            xvect[cChan] = xvect[cChan] + numpy.multiply(xvect[cChan], expand)
            
            
    x = numpy.linspace(-400,400,801)
    y = numpy.linspace(-400,400,801)
    xi, yi = numpy.meshgrid(x,y)
    zi = scipy.interpolate.griddata((xvect,yvect),zvect,(xi,yi),method=Method)
    # fill any missing points 
    if Complete:
        zi = fill(zi)
    
    # plot the activity
    if Colormap == False:
        Colormap = matplotlib.pyplot.cm.viridis
    contourplot = matplotlib.pyplot.contourf(xi,yi,zi, Steps, cmap=Colormap, vmin=Scale[0], vmax=Scale[1])
    ax.autoscale(False)
    
    if Electrodes != False:
        markervalue = 'k'
        if Electrodes != True:
            markervalue = Electrodes 
        
        matplotlib.pyplot.plot(numpy.multiply(xvect, 0.85), numpy.add(numpy.multiply(yvect,0.8),-35), linestyle="None", marker = '.', color=markervalue)
        
    extent = numpy.min(x), numpy.max(x), numpy.min(y), numpy.max(y)
    if Style.upper() == ('Full').upper():
        try:
            framemask = matplotlib.image.imread('eggheadplot1.png')
        except:
            framemask = matplotlib.image.imread('Gentask\Engine\eggheadplot1.png')
            
    elif Style.upper() == ('Outline').upper():
        try:
            framemask = matplotlib.image.imread('eggheadplot2.png')
        except:
            framemask = matplotlib.image.imread('Gentask\Engine\eggheadplot2.png')
    else:
        try:
            framemask = matplotlib.image.imread('eggheadplot3.png')
        except:
            framemask = matplotlib.image.imread('Gentask\Engine\eggheadplot3.png')
    
    imgmask = framemask[:,:,0] == framemask[:,:,1];
    framemask[imgmask == 0, 3] = 0      # 100% transparent
    
    if BrainOpacity != False:
        try:
            eggbrain = matplotlib.image.imread('eggheadplot4.png')
        except:
            eggbrain = matplotlib.image.imread('Gentask\Engine\eggheadplot4.png')
        
        imgmask = eggbrain[:,:,0] == eggbrain[:,:,1];
        eggbrain[imgmask == 0, 3] = 0      # 100% transparent
        ax.imshow(eggbrain, alpha=BrainOpacity, interpolation='nearest', extent=extent, zorder=5)
    
    ax.imshow(framemask, alpha=1.0, interpolation='nearest', extent=extent, zorder=6)
    
    
    

################################################################################################################################################
################################################################################################################################################
################################################################################################################################################    
#################### General Purpose Functions 
################################################################################################################################################
################################################################################################################################################
################################################################################################################################################
    


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
            matplotlib.pyplot.plot(timeaxis, invar[Y])
    else:
        try:
            matplotlib.pyplot.plot(timeaxis, [invar])
        except:
            matplotlib.pyplot.plot(timeaxis, invar)
            
    
    matplotlib.pyplot.show()

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

def smooth(invect,span=11,window=False):
    """smooth the data using a window with requested size.
    
    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal 
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.
    
    input:
        x: the input signal 
        span: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal
        
    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)
    
    see also: 
    
    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter
 
    """
    x = copy.deepcopy(invect)
    window = checkdefaultsettings(window, ['hanning', 'flat', 'hamming', 'bartlett', 'blackman'])
    if span>3:
        s=numpy.r_[x[span-1:0:-1],x,x[-2:-span-1:-1]]
        #print(len(s))
        if window == 'flat': #moving average
            w=numpy.ones(span,'d')
        else:
            w=eval('numpy.'+window+'(span)')
    
        y=numpy.convolve(w/w.sum(),s,mode='valid')
        
        return y[int(numpy.round(span/2-1)):-int(numpy.round(span/2))]
    
    else:
        return x

def minmax_scaling(inarray, columns, min_val=0, max_val=1):
    """Min max scaling of pandas' DataFrames.
    Parameters
    ----------
    array : pandas DataFrame or NumPy ndarray, shape = [n_rows, n_columns].
    columns : array-like, shape = [n_columns]
        Array-like with column names, e.g., ['col1', 'col2', ...]
        or column indices [0, 2, 4, ...]
    min_val : `int` or `float`, optional (default=`0`)
        minimum value after rescaling.
    max_val : `int` or `float`, optional (default=`1`)
        maximum value after rescaling.
    Returns
    ----------
    df_new : pandas DataFrame object.
        Copy of the array or DataFrame with rescaled columns.
    Examples
    ----------
    For usage examples, please see
    http://rasbt.github.io/mlxtend/user_guide/preprocessing/minmax_scaling/
    """
    array = copy.deepcopy(inarray)
    ary_new = array.astype(float)
    if len(ary_new.shape) == 1:
        ary_new = ary_new[:, numpy.newaxis]

    if isinstance(ary_new, pandas.DataFrame):
        ary_newt = ary_new.loc
    elif isinstance(ary_new, numpy.ndarray):
        ary_newt = ary_new
    else:
        raise AttributeError('Input array must be a pandas'
                             'DataFrame or NumPy array')

    numerator = ary_newt[:, columns] - ary_newt[:, columns].min(axis=0)
    denominator = (ary_newt[:, columns].max(axis=0) -
                   ary_newt[:, columns].min(axis=0))
    ary_newt[:, columns] = numerator / denominator

    ary_newt[:, columns] = (ary_newt[:, columns] *
                            (max_val - min_val) + min_val)

    return copy.deepcopy(ary_newt[:, columns])

def single_pupil_IRF(params, x):
    s1 = params['s1']
    n1 = params['n1']
    tmax1 = params['tmax1']
    return s1 * ((x**n1) * (numpy.e**((-n1*x)/tmax1)))

def single_pupil_IRF_ls(params, x, data):
    s1 = params['s1'].value
    n1 = params['n1'].value
    tmax1 = params['tmax1'].value
    model = s1 * ((x**n1) * (numpy.e**((-n1*x)/tmax1)))
    return model - data

def double_pupil_IRF(params, x):
    s1 = params['s1']
    s2 = params['s2']
    n1 = params['n1']
    n2 = params['n2']
    tmax1 = params['tmax1']
    tmax2 = params['tmax2']
    return s1 * ((x**n1) * (numpy.e**((-n1*x)/tmax1))) + s2 * ((x**n2) * (numpy.e**((-n2*x)/tmax2)))

def double_pupil_IRF_ls(params, x, data):
    s1 = params['s1'].value
    s2 = params['s2'].value
    n1 = params['n1'].value
    n2 = params['n2'].value
    tmax1 = params['tmax1'].value
    tmax2 = params['tmax2'].value
    model = s1 * ((x**n1) * (numpy.e**((-n1*x)/tmax1))) + s2 * ((x**n2) * (numpy.e**((-n2*x)/tmax2)))
    return model - data

    
def regressionbasedartifactremoval(inputdata, artifactindices, decompinterval, samplerate, artifactpolarity, ringingsmooth=False):
    # artifactpolarity: [-1 or 1]
    
    # interpolate any missing data
    filtdata = numpy.array(inputdata.copy())
    nans, x= numpy.isnan(filtdata), lambda z: z.nonzero()[0]
    filtdata[nans] = numpy.interp(x(nans), x(~nans), filtdata[~nans])
    
    # extract component
    fd = FIRDeconvolution(
            signal = filtdata, 
            events = [(numpy.array(artifactindices) / float(samplerate))], 
            event_names = ['onset'], 
            sample_frequency = samplerate,
            deconvolution_frequency = samplerate,
            deconvolution_interval = [0, decompinterval],
            )

    # we then tell it to create its design matrix
    fd.create_design_matrix()
    # perform the actual regression, in this case with the statsmodels backend
    fd.regress(method = 'lstsq')
    # and partition the resulting betas according to the different event types
    fd.betas_for_events()
    fd.calculate_rsq()
   
    boolmodelshow = False
    if boolmodelshow:
        samples = 2000
        f = matplotlib.pyplot.figure(figsize = (10,8))
        s = f.add_subplot(111)
        s.set_title('data and predictions')
        tempx = numpy.linspace(0,samples, int(samples * fd.deconvolution_frequency/fd.sample_frequency))
        tempy = fd.resampled_signal[:,:int(samples * fd.deconvolution_frequency/fd.sample_frequency)].T
        matplotlib.pyplot.plot(tempx, tempy, 'r')
        tempy = fd.predict_from_design_matrix(fd.design_matrix[:,:int(samples * fd.deconvolution_frequency/fd.sample_frequency)]).T
        matplotlib.pyplot.plot(tempx, tempy, 'k')
        matplotlib.pyplot.legend(['signal','explained'])
        
    model_response = numpy.array(fd.betas_per_event_type[0]).ravel()
    model_response = model_response - model_response[0].mean()
    x = numpy.linspace(0, decompinterval-float(0.0), len(model_response))
        
    # create a set of Parameters for powell method:
    params = Parameters()
    params.add('s1', value=-1, min=-numpy.inf, max=-1e-25)
    params.add('s2', value=1, min=1e-25, max=numpy.inf)
    params.add('n1', value=10, min=9, max=11)
    params.add('n2', value=10, min=8, max=12)
    params.add('tmax1', value=0.9, min=0.5, max=1.5)
    params.add('tmax2', value=2.5, min=1.5, max=4)
    
    model_result = minimize(double_pupil_IRF_ls, params, method='powell', args=(x, model_response))
    model_kernel = double_pupil_IRF(model_result.params, x)

    boolmodelshow = False
    if boolmodelshow:
        f = matplotlib.pyplot.figure(figsize = (10,3.5))
        matplotlib.pyplot.plot(x, model_response, label='model response')
        matplotlib.pyplot.plot(x, model_kernel, label='model fit')

        # evaluate fit of the model
        print(numpy.corrcoef(model_response, model_kernel)[0][1])
            
    # upsample the kernal
    #x = numpy.linspace(0, 6, 6.0*EEG.srate)
    #blink_kernel = double_pupil_IRF(blink_result.params, x)
    
    # regressors:
    model_reg = numpy.zeros(len(filtdata))
    model_reg[artifactindices] = 1
    model_reg_conv = scipy.signal.fftconvolve(model_reg, model_kernel, 'full')[:-(len(model_kernel)-1)]
    regs = [model_reg_conv]
    design_matrix = numpy.matrix(numpy.vstack([reg for reg in regs])).T
    
    # scale the artifact correction
    # when the correction does not correlate with the raw data the correction is reduced 
    for cA in range(len(artifactindices)):
        
        startindx = artifactindices[cA]
        stopindx= artifactindices[cA]+int(numpy.round(decompinterval * samplerate))
        
        tempvect = filtdata[startindx:stopindx]
        tempvect = tempvect - tempvect[0]
        regsvect = regs[0][startindx:stopindx]
        if artifactpolarity < 0:
            indices = peakutils.indexes(-tempvect, thres=0.75, min_dist=20)
        else:
            indices = peakutils.indexes(tempvect, thres=0.75, min_dist=20)
        # multiply peak by correlation to reduce the removal for uncorrelated data
        if len(indices) > 0:
            if artifactpolarity < 0:
                if tempvect[indices[0]] < 0:
                    artscale = numpy.multiply(tempvect[indices[0]], abs(numpy.corrcoef(tempvect, numpy.ndarray.flatten(regsvect))[0][1]))
                else:
                    # waveform is funky - artifact removal may be problematic
                    artscale = -0.00001
            else:
                if tempvect[indices[0]] > 0:
                    artscale = numpy.multiply(tempvect[indices[0]], abs(numpy.corrcoef(tempvect, numpy.ndarray.flatten(regsvect))[0][1]))
                else:
                    # waveform is funky - artifact removal may be problematic
                    artscale = -0.00001
        else:
            artscale = -0.00001
        # scale to the magnitude of the adjusted peak
        regsvect = minmax_scaling(regsvect, 0, min_val=artscale, max_val=0)
        #plot(tempvect); plot(regsvect)
        # place scaled correction back in
        regs[0][startindx:stopindx] = regsvect
        
    # GLM:
    betas = numpy.array(((design_matrix.T * design_matrix).I * design_matrix.T) * numpy.matrix(filtdata).T).ravel()
    if betas[0] > 1.1:
        # to prevent overcorrection
        betas[0] = float(1.1)
    modeledartifact = numpy.sum(numpy.vstack([betas[i]*regs[i] for i in range(len(betas))]), axis=0)
    
    # clean pupil:
    data_clean = numpy.subtract(filtdata, modeledartifact)
    
    # regression based subtraction approaches are prone to create ringing effects
    # smooth to minimize issues
    #if ringingsmooth == False:
    #    ringingsmooth = int(numpy.round(int(numpy.round(decompinterval * samplerate))/2.0))
    #ringingsmooth = int(numpy.round(ringingsmooth)) # force to be int
        
    #if ringingsmooth > 0:
    #    for cA in range(len(artifactindices)):
    #        startindx = artifactindices[cA]
    #        stopindx= artifactindices[cA]+int(numpy.round(decompinterval * samplerate))
    #        filtdata[startindx:stopindx] = smooth(numpy.array(filtdata[startindx:stopindx].copy()),span=ringingsmooth,window='hanning')
        
    return data_clean

def excel_date(date1):
    temp = datetime.datetime(1899, 12, 30)    # Note, not 31st Dec but 30th!
    delta = date1 - temp
    return float(delta.days) + (float(delta.seconds) / 86400)


def msdatefromref(date1, date2):
    delta = date2 - date1
    timeinmicrosec = (delta.seconds * 1000000) + delta.microseconds
    # give milliseccond precision
    return numpy.round(numpy.divide(timeinmicrosec,1000.0))
    
def closestidx(lst, K):
    return numpy.argmin(abs(numpy.subtract(lst, K)))


################################################################################################################################################
################################################################################################################################################
################################################################################################################################################    
#################### Data Read In Functions 
################################################################################################################################################
################################################################################################################################################
################################################################################################################################################
    
class eyetrackingstructure():
    
    def __init__(self):
        self.distance = 55.0
        self.accuracyleftdegrees = []
        self.accuracyleftpixels = []
        self.precisionleftpixels = []
        self.accuracyrightdegrees = []
        self.accuracyrightpixels = []
        self.precisionrightpixels = []


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
        self.eyetracking = eyetrackingstructure()
        
        
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
    
    
    

def readEyeTribe(inputfile):
    # function to read in pupillary data from the EyeTribe eye tracker
    
    head, tail = os.path.split(inputfile)
    if (os.path.isfile(inputfile)): 
    
        # create structure
        EEG = eeglabstructure()
        EEG.filename = tail.split('.')[0]
        EEG.filepath = head
        
        # plug in known values
        EEG.trials = 0
    
        # read in the data
        dcontents = open(inputfile).readlines()
        headerlabels = dcontents[0].split('\t')
        
        # find the start of the data and extract some information along the way
        cI = 1
        startofdata = 0
        while cI < len(dcontents):
            if dcontents[cI].split('\t')[0] == 'MSG':
                if 'Samplerate (in Hz)' in dcontents[cI].split('\t')[3]:
                    EEG.srate = float(dcontents[cI].split('\t')[3].split(':')[1])
                if 'Distance between participant' in dcontents[cI].split('\t')[3]:
                    EEG.eyetracking.distance = float(dcontents[cI].split('\t')[3].split(':')[1])
                if 'Left accuracy (degrees)' in dcontents[cI].split('\t')[3]:
                    EEG.eyetracking.accuracyleftdegrees = float(dcontents[cI].split('\t')[3].split(':')[1])
                if 'Left accuracy (in pixels)' in dcontents[cI].split('\t')[3]:
                    EEG.eyetracking.accuracyleftpixels = float(dcontents[cI].split('\t')[3].split(':')[1])
                if 'Left precision' in dcontents[cI].split('\t')[3]:
                    EEG.eyetracking.precisionleftpixels = float(dcontents[cI].split('\t')[3].split(':')[1])
                if 'Right accuracy (degrees)' in dcontents[cI].split('\t')[3]:
                    EEG.eyetracking.accuracyrightdegrees = float(dcontents[cI].split('\t')[3].split(':')[1])
                if 'Right accuracy (in pixels)' in dcontents[cI].split('\t')[3]:
                    EEG.eyetracking.accuracyrightpixels = float(dcontents[cI].split('\t')[3].split(':')[1])
                if 'Right precision' in dcontents[cI].split('\t')[3]:
                    EEG.eyetracking.precisionrightpixels = float(dcontents[cI].split('\t')[3].split(':')[1])
                
            else:
                try:
                    # pandas will kick an error if the input doesnt make sense for a date
                    sampletime = pandas.to_datetime(dcontents[cI].split('\t')[0])
                    startofdata = copy.deepcopy(cI)
                    cI = len(dcontents) # kick out of the loop
                except:
                    # not a message or a time stamp - so skip it
                    pass
                
            cI = cI + 1;
        
        # the EyeTribe does a decent job but it is prone to dropping samples and having an inconsistent sampling rate - but it does log when a sample occurs
        # using the first and last samples, create an array to load the data into
        
        # create reference date
        tempvect = dcontents[startofdata].split('\t')
        checkdate = tempvect[headerlabels.index('timestamp')]
        date0 = pandas.to_datetime(checkdate.split(' ')[0] + ' 00:00:00.0000001')
        
        # create time series matching the sampling rate
        starttime = msdatefromref(date0, pandas.to_datetime(tempvect[headerlabels.index('timestamp')]))
        stoptime = msdatefromref(date0, pandas.to_datetime(dcontents[len(dcontents)-1].split('\t')[headerlabels.index('timestamp')]))
        tempvect = numpy.arange(starttime,stoptime,numpy.multiply(numpy.divide(1.0,EEG.srate), 1000))
        
        # extract data
        #chanlist = ['Lrawx','Lrawy','Lpsize','Rrawx','Rrawy','Rpsize']
        chanlist = ['Lpsize','Rpsize']
        outdata = []
        outchan = []
        for cChan in range(len(chanlist)):
            outchan.append(chanlist[cChan])
            
            # populate array
            temparray = [numpy.nan] * len(tempvect)
            for cSample in range(startofdata,len(dcontents)):
                
                # find sample
                matchindex = closestidx(tempvect, msdatefromref(date0, pandas.to_datetime(dcontents[cSample].split('\t')[headerlabels.index('timestamp')])))
                temparray[matchindex] = float(dcontents[cSample].split('\t')[headerlabels.index(chanlist[cChan])])
                
            # interpolate any missing samples
            pupil_interpolated = numpy.array(temparray.copy())
            nans, x= numpy.isnan(pupil_interpolated), lambda z: z.nonzero()[0]
            pupil_interpolated[nans] = numpy.interp(x(nans), x(~nans), pupil_interpolated[~nans])
                
            outdata.append(numpy.ndarray.tolist(pupil_interpolated))
            
        # store the data in the structure
        EEG.data = copy.deepcopy(outdata)  
        EEG.pnts = len(EEG.data[0])
        EEG.channels = copy.deepcopy(chanlist)
        EEG.nbchan = len(EEG.channels)
        EEG.events = [[0]*EEG.pnts]
        EEG.eventsegments = ['Type']
            
        # pull the samples and create the times
        EEG.samples = []
        temparray = [numpy.nan] * len(tempvect)
        for cSample in range(startofdata,len(dcontents)):
            matchindex = closestidx(tempvect, msdatefromref(date0, pandas.to_datetime(dcontents[cSample].split('\t')[headerlabels.index('timestamp')])))
            temparray[matchindex] = float(dcontents[cSample].split('\t')[headerlabels.index('time')])
            
        sample_interpolated = numpy.array(temparray.copy())
        nans, x= numpy.isnan(sample_interpolated), lambda z: z.nonzero()[0]
        sample_interpolated[nans] = numpy.interp(x(nans), x(~nans), sample_interpolated[~nans])
            
        EEG.samples = copy.deepcopy(numpy.ndarray.tolist(sample_interpolated))
        EEG.times = numpy.arange(0,numpy.multiply(EEG.pnts,numpy.divide(1.0,EEG.srate)),numpy.divide(1.0,EEG.srate))
        
        # check to see if there are any events
        if (os.path.isfile(inputfile +  'e')): 
            # read in the fitbit data
            dcontents = open(inputfile +  'e').readlines()
        
            for dinfo in range(0, len(dcontents)):
                currentline = dcontents[dinfo].split(' ')
                currentindex = closestidx(EEG.samples, float(currentline[0]))
                EEG.events[0][currentindex] = float(currentline[-1])
        
        EEG.checkset()
        
        # see if there is behavioral data available
        if (os.path.isfile(head + os.path.sep + tail.split('.')[0] + '.psydat')): 
            EEG = mergetaskperformance(EEG, head + os.path.sep + tail.split('.')[0] + '.psydat')
    
        return EEG
    
def correctEyeTribe(EEG, Correction=False):
    OUTEEG = copy.deepcopy(EEG)
    
    if Correction == False:
        Correction = [0.005,0.089,-0.00000001]
        
    if OUTEEG.eyetracking.distance == 0.0:
        OUTEEG.eyetracking.distance = 55.0
    
    chanlist = ['Lpsize','Rpsize']
    for cChan in range(len(chanlist)):
        chanindex = OUTEEG.channels.index(chanlist[cChan])
        # account for distance from screen
        OUTEEG.data[chanindex] = numpy.add(numpy.array(OUTEEG.data[chanindex]), numpy.multiply(numpy.multiply(OUTEEG.eyetracking.distance, 10), Correction[0]))
        # scale the pupil 
        OUTEEG.data[chanindex] = numpy.multiply(numpy.array(OUTEEG.data[chanindex]), Correction[1])
        # add the model intercept in
        OUTEEG.data[chanindex] = numpy.add(numpy.array(OUTEEG.data[chanindex]), Correction[2])
        # scale to micrometers
        OUTEEG.data[chanindex] = numpy.multiply(OUTEEG.data[chanindex], 1000.0) 
        
    
    return OUTEEG

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
                    # will throw an error if not in list
                    currentindex = OUTEEG.eventsegments.index(lab)
                except:
                    OUTEEG.eventsegments.append(lab)
                    OUTEEG.events.append([0]*len(OUTEEG.events[0]))
                
            # obtain list of events in the file
            stimlistvalue = [v for i,v in enumerate(OUTEEG.events[0]) if v > 0]
            if len(stimlistvalue) > 0:
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
                                    if currentline[labline.index('Latency')] != 'nan':
                                        
                                        # RT in ms / 1000 times the sample rate gives you the number of samples
                                        backsample = int(numpy.floor(numpy.multiply(numpy.divide(float(currentline[labline.index('Latency')]),1000), float(OUTEEG.srate))))
                                        boolnumeric = True
                                        try:
                                            float(currentline[labline.index('Resp')])
                                        except:
                                            boolnumeric = False
                                        
                                        if float(currentline[labline.index('Correct')]) == float(1.0):
                                            if boolnumeric:
                                                OUTEEG.events[0][sampleindex+backsample] = numpy.add(float(currentline[labline.index('Resp')]), float(1190.0))
                                            else:
                                                OUTEEG.events[0][sampleindex+backsample] = float(1191.0)
                                        else:
                                            if boolnumeric:
                                                OUTEEG.events[0][sampleindex+backsample] = numpy.add(float(currentline[labline.index('Resp')]), float(2190.0))
                                            else:
                                                OUTEEG.events[0][sampleindex+backsample] = float(2191.0)
                                        OUTEEG.events[OUTEEG.eventsegments.index('Event')][sampleindex+backsample] = 'Response'
                                        OUTEEG.events[OUTEEG.eventsegments.index('Trial')][sampleindex+backsample] = float(currentline[labline.index('Trial')])
                                    
                                # increment events to next mark
                                currenteventplace = currenteventplace + 1
        
        return OUTEEG
    else:
        return EEG













################################################################################################################################################
################################################################################################################################################
################################################################################################################################################    
#################### Multi use Processing Functions 
################################################################################################################################################
################################################################################################################################################
################################################################################################################################################

def extractamplitude(EEG, Window=False, Approach=False):
    
    Approach = checkdefaultsettings(Approach, ['median', 'mean'])
    
    if Window != False:
        startindex = numpy.argmin(abs(numpy.subtract(EEG.times,numpy.divide(float(Window[0]),1))))
        stopindex = numpy.argmin(abs(numpy.subtract(EEG.times,numpy.divide(float(Window[1]),1))))
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

def extractpeaks(EEG, Window=False, Points=False):
    
    if Points == False:
        Points = 9
    Points = int(Points)    
    
    if Window != False:
        startindex = int(closestidx(EEG.times, float(Window[0])))
        stopindex = int(closestidx(EEG.times, float(Window[1])))
    else:
        startindex = 0
        stopindex = len(EEG.times)
    
    outputamplitude = []
    outputlatency = []
    for cC in range(EEG.nbchan):
        if EEG.trials > 0:
            currentepochamplitude = []
            currentepochlatency = []
            for cE in range(EEG.trials):
                
                maxthresh = 0.99
                outpoint = []
                while len(outpoint) == 0:
                    outpoint = peakutils.indexes(EEG.data[cC][cE][startindex:stopindex], thres=float(maxthresh), min_dist=int(Points))
                    maxthresh = numpy.subtract(maxthresh, 0.01)
                    if (maxthresh < 0.5):
                        outpoint = [0]              
                
                currentepochamplitude.append(EEG.data[cC][cE][startindex + outpoint[0]])
                currentepochlatency.append(EEG.times[startindex + outpoint[0]])
                
            outputamplitude.append(currentepochamplitude)
            outputlatency.append(currentepochlatency)
        else:
            
            maxthresh = 0.99
            outpoint = []
            while len(outpoint) == 0:
                outpoint = peakutils.indexes(EEG.data[cC][startindex:stopindex], thres=float(maxthresh), min_dist=int(Points))
                maxthresh = numpy.subtract(maxthresh, 0.01)
                if (maxthresh < 0.5):
                    outpoint = [0]
            
            outputamplitude.append(EEG.data[cC][startindex + outpoint[0]])
            outputlatency.append(EEG.times[startindex + outpoint[0]])
            
    return [outputamplitude, outputlatency]


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
                

    if OUTEEG.trials == 0:
        OUTEEG.coherence = numpy.zeros((OUTEEG.nbchan, OUTEEG.nbchan, OUTEEG.frequencies.size))
        for i in range(OUTEEG.nbchan): 
            for j in range(OUTEEG.nbchan): 
                i_fft = numpy.vstack(OUTEEG.freqdata[i]).transpose()
                j_fft = numpy.vstack(OUTEEG.freqdata[j]).transpose()
                i_fft_sum = numpy.sum(numpy.abs(i_fft)**2, axis=1)
                j_fft_sum = numpy.sum(numpy.abs(j_fft)**2, axis=1)
                ij_fft = i_fft * numpy.conj(j_fft)
                ij_fft_sum = numpy.sum(ij_fft, axis=1) 
                ij_fft_sum = numpy.abs(ij_fft_sum)**2
                OUTEEG.coherence[i,j,:] = ij_fft_sum / (i_fft_sum * j_fft_sum)
    else:
        OUTEEG.coherence = numpy.zeros((OUTEEG.trials, OUTEEG.nbchan, OUTEEG.nbchan, OUTEEG.frequencies.size)) 
        for cE in range(EEG.trials): 
            for i in range(OUTEEG.nbchan): 
                for j in range(OUTEEG.nbchan): 
                    i_fft = numpy.vstack(OUTEEG.freqdata[i][cE]).transpose()
                    j_fft = numpy.vstack(OUTEEG.freqdata[j][cE]).transpose()
                    i_fft_sum = numpy.sum(numpy.abs(i_fft)**2, axis=1)
                    j_fft_sum = numpy.sum(numpy.abs(j_fft)**2, axis=1)
                    ij_fft = i_fft * numpy.conj(j_fft)
                    ij_fft_sum = numpy.sum(ij_fft, axis=1) 
                    ij_fft_sum = numpy.abs(ij_fft_sum)**2
                    OUTEEG.coherence[cE,i,j,:] = ij_fft_sum / (i_fft_sum * j_fft_sum) 
        
    return OUTEEG

def simplefilter(EEG, Filter=False, Design=False, Cutoff=False, Order=False, Window=False):
    # simple function to use scipy signal processing for filtering the data
    # works on both continuous and epoched datasets
    
    OUTEEG = copy.deepcopy(EEG)
    
    Filter = checkdefaultsettings(Filter, ['lowpass', 'highpass', 'bandpass', 'notch'])
    Design = checkdefaultsettings(Design, ['butter', 'savitzky-golay', 'savgol', 'hanning', 'flat', 'hamming', 'bartlett', 'blackman'])
    
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
            
            # interpolate any missing data
            filtdata = numpy.array(OUTEEG.data[i].copy())
            nans, x= numpy.isnan(filtdata), lambda z: z.nonzero()[0]
            # interpolate prior to filtering
            filtdata[nans] = numpy.interp(x(nans), x(~nans), filtdata[~nans])
            
            if Filter == 'notch':
                filtdata = scipy.signal.filtfilt(b=b, a=a, x=(filtdata), padtype='constant', padlen=int(math.floor(len(filtdata)/3.0)), method="pad") 
                
            elif Filter == 'lowpass':
                filtdata = scipy.signal.filtfilt(b=b, a=a, x=(filtdata), padtype=None) 
                
            elif Filter == 'highpass':
                filtdata = scipy.signal.filtfilt(b=b, a=a, x=(filtdata), padtype=None) 
                
            elif Filter == 'bandpass':
                filtdata = scipy.signal.filtfilt(b=b, a=a, x=(filtdata), padtype=None) 
                
            if len(nans) > 0:
                # restore missing data
                filtdata[nans] = numpy.nan
            OUTEEG.data[i] = copy.deepcopy(numpy.ndarray.tolist(filtdata))
     
            
    elif Design in ['savitzky-golay', 'savgol']:   
        
        """Filter a signal using the Savitzky-Golay method.
        Default window size is chosen based on `Sadeghi, M., & Behnia, F. (2018). Optimum window length of
        Savitzky-Golay filters with arbitrary order. arXiv preprint arXiv:1808.10489.
        <https://arxiv.org/ftp/arxiv/papers/1808/1808.10489.pdf>`_.
        """
        if Window == False:
            window_size = int(numpy.round(EEG.srate / 3))
        else:
            window_size = Window
        if (window_size % 2) == 0:
            window_size = window_size + 1  # Make sure it's odd
        
        for i in range(OUTEEG.nbchan):
            
            # interpolate any missing data
            filtdata = numpy.array(OUTEEG.data[i].copy())
            nans, x= numpy.isnan(filtdata), lambda z: z.nonzero()[0]
            # interpolate prior to filtering
            filtdata[nans] = numpy.interp(x(nans), x(~nans), filtdata[~nans])
            try:
                filtdata = numpy.nan_to_num(filtdata, copy=True, nan=0.0)
            except:
                filtdata = numpy.nan_to_num(filtdata, copy=True)
            filtdata = scipy.signal.savgol_filter(filtdata, window_length=int(window_size), polyorder=Order)
        
            if len(nans) > 0:
                # restore missing data
                filtdata[nans] = numpy.nan
            OUTEEG.data[i] = copy.deepcopy(numpy.ndarray.tolist(filtdata))
        
        
    elif Design in ['hanning', 'flat', 'hamming', 'bartlett', 'blackman']:
        
        if Window == False:
            window_size = int(numpy.round(EEG.srate / 3))
        else:
            window_size = Window
        if (window_size % 2) == 0:
            window_size = window_size + 1  # Make sure it's odd
        
        for i in range(OUTEEG.nbchan):
            
            if OUTEEG.trials == 0:
                # continuous data
                    
                # interpolate any missing data
                filtdata = numpy.array(OUTEEG.data[i].copy())
                try:
                    nans, x= numpy.isnan(filtdata), lambda z: z.nonzero()[0]
                    # interpolate prior to filtering
                    filtdata[nans] = numpy.interp(x(nans), x(~nans), filtdata[~nans])
                    
                    try:
                        filtdata = numpy.nan_to_num(filtdata, copy=True, nan=0.0)
                    except:
                        filtdata = numpy.nan_to_num(filtdata, copy=True)
                    filtdata = smooth(filtdata, span=window_size, window=Design)
                
                    if len(nans) > 0:
                        # restore missing data
                        filtdata[nans] = numpy.nan
                except:
                    pass
                OUTEEG.data[i] = copy.deepcopy(numpy.ndarray.tolist(filtdata))
                
            elif OUTEEG.trials > 0:
                currentchan = []
                for cE in range(OUTEEG.trials):
                        
                    # interpolate any missing data
                    filtdata = numpy.array(OUTEEG.data[i][cE].copy())
                    
                    try:
                        nans, x= numpy.isnan(filtdata), lambda z: z.nonzero()[0]
                        # interpolate prior to filtering
                        filtdata[nans] = numpy.interp(x(nans), x(~nans), filtdata[~nans])
                        
                        try:
                            filtdata = numpy.nan_to_num(filtdata, copy=True, nan=0.0)
                        except:
                            filtdata = numpy.nan_to_num(filtdata, copy=True)
                        filtdata = smooth(filtdata, span=window_size, window=Design)
                    
                        if len(nans) > 0:
                            # restore missing data
                            filtdata[nans] = numpy.nan
                    except:
                        pass
                    currentchan.append(numpy.ndarray.tolist(filtdata))
                        
                OUTEEG.data[i] = copy.deepcopy(currentchan)
        
        
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


################################################################################################################################################
################################################################################################################################################
################################################################################################################################################    
#################### Continuous Data Processing Functions 
################################################################################################################################################
################################################################################################################################################
################################################################################################################################################
    

def epochtocontinous(EEG, skipreject=True):
    OUTEEG = copy.deepcopy(EEG)
    
    if EEG.trials > 0:
        
        # take data out of epochs and make continous
        outdata = []
        for cC in range(EEG.nbchan):
            currentchannel= []
            for cE in range(EEG.trials):
                boolpass = True
                if skipreject != False:
                    if EEG.reject[cE] != 0:
                        boolpass = False
                if boolpass:
                    for cP in range(EEG.pnts):
                        currentchannel.append(EEG.data[cC][cE][cP])
            outdata.append(currentchannel)
        OUTEEG.data = outdata
        OUTEEG.pnts = len(OUTEEG.data[0])
        
        # take epoch event codes out of epochs and make continous
        events = []     
        for cC in range(len(EEG.events)):
            currentchannel = []
            for cE in range(EEG.trials):
                boolpass = True
                if skipreject != False:
                    if EEG.reject[cE] != 0:
                        boolpass = False
                if boolpass:
                    for cP in range(EEG.pnts):
                        currentchannel.append(EEG.events[cC][cE][cP])
            events.append(currentchannel)
        OUTEEG.events = events
        
        # take samples out of epochs and make continous
        samples = []
        for cE in range(EEG.trials):
            boolpass = True
            if skipreject != False:
                if EEG.reject[cE] != 0:
                    boolpass = False
            if boolpass:
                for cP in range(EEG.pnts):
                    samples.append(EEG.samples[cE][cP])
        OUTEEG.samples = samples
        
        OUTEEG.times = numpy.arange(0,numpy.multiply(OUTEEG.pnts,numpy.divide(1.0,OUTEEG.srate)),numpy.divide(1.0,OUTEEG.srate))
        OUTEEG.trials = 0
        OUTEEG.reject = []
        OUTEEG.acceptedtrials = 0
    
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
        epochsamples = int(numpy.floor(numpy.multiply(numpy.divide(numpy.subtract(float(Window[1]),float(Window[0])),float(1.0)),OUTEEG.srate)))
        OUTEEG.times = numpy.arange(numpy.divide(Window[0],1.0), numpy.divide(Window[1],1.0),numpy.divide(1.0,OUTEEG.srate))
        epochindexmin = numpy.multiply(numpy.divide(Window[0],1.0), OUTEEG.srate)
        
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

################################################################################################################################################
################################################################################################################################################
################################################################################################################################################    
#################### Epoched Data Processing Functions 
################################################################################################################################################
################################################################################################################################################
################################################################################################################################################
    
def voltagethreshold(EEG, Threshold=False, Step=False, NaN=True):
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
                        
        if NaN != False:
            for cC in range(EEG.nbchan):
                for cE in range(len(currentchanneldata)):
                    # if the entire epoch is nan
                    if len(EEG.data[cC][cE]) == numpy.count_nonzero(numpy.isnan(EEG.data[cC][cE])):
                        OUTEEG.reject[cE] = 4
                        
                    # if the entire epoch is zero
                    if len(EEG.data[cC][cE]) == (len(EEG.data[cC][cE]) - numpy.count_nonzero(EEG.data[cC][cE])):
                        OUTEEG.reject[cE] = 4
                        

    return OUTEEG

def simplezwave(EEG, BaselineWindow=False, ddof=1):
    # function that computes the mean and sd over a baseline period and then z scores the entire dataset based upon that information
    
    OUTEEG = copy.deepcopy(EEG)
    
    # only works for epoched datasets
    if OUTEEG.trials > 0:
        
        if BaselineWindow != False:
            startindex = numpy.argmin(abs(numpy.subtract(EEG.times,numpy.divide(float(BaselineWindow[0]),1))))
            stopindex = numpy.argmin(abs(numpy.subtract(EEG.times,numpy.divide(float(BaselineWindow[1]),1))))
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

def simpleaverage(EEG, Approach=False):
    
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
                
                nans, x= numpy.isnan(EEG.data[cC][cE]), lambda z: z.nonzero()[0]
                if sum(nans) < len(EEG.data[cC][cE]):
                    
                    if Approach == 'mean':
                        OUTEEG.data[cC][cE] = numpy.subtract(EEG.data[cC][cE], numpy.nanmean(EEG.data[cC][cE]))
                    elif Approach == 'median':
                        OUTEEG.data[cC][cE] = numpy.subtract(EEG.data[cC][cE], numpy.nanmedian(EEG.data[cC][cE]))
                    
            else:
                startindex = numpy.argmin(abs(numpy.subtract(EEG.times,numpy.divide(float(Window[0]),1))))
                stopindex = numpy.argmin(abs(numpy.subtract(EEG.times,numpy.divide(float(Window[1]),1))))
                
                nans, x= numpy.isnan(EEG.data[cC][cE][startindex:stopindex]), lambda z: z.nonzero()[0]
                if sum(nans) < len(EEG.data[cC][cE][startindex:stopindex]):
                    
                    if Approach == 'mean':
                        OUTEEG.data[cC][cE] = numpy.subtract(EEG.data[cC][cE], numpy.nanmean(EEG.data[cC][cE][startindex:stopindex]))
                    elif Approach == 'median':
                        OUTEEG.data[cC][cE] = numpy.subtract(EEG.data[cC][cE], numpy.nanmedian(EEG.data[cC][cE][startindex:stopindex]))
    
    return OUTEEG

def EyeTribetousable(EEG, Threshold=False, Interval=False, Overlap=False, Peakspacing=False):
    # threshold [norm 0 to 1]
    # interval [seconds]
    # overlap [percentage]
    # peakspacing [points]
    
    OUTEEG = copy.deepcopy(EEG)
    
    if Threshold == False:
        Threshold = 0.85
        
    if Interval == False:
        Interval = 2.0
    interval = int(numpy.round(numpy.multiply(float(Interval), EEG.srate)))
        
    if Overlap == False:
        Overlap = 0.5
    if float(Overlap) > float(1.0):
        Overlap = 0.5
    if float(Overlap) < float(0.0):
        Overlap = 0.5
    Overlap = numpy.subtract(1.0, float(Overlap)) # so that 0.75 percent overlap shifts by 0.25 percent each loop
    
    if Peakspacing == False:
        Peakspacing = 1
    Peakspacing = int(numpy.round(Peakspacing))
    
    # loop through each channel
    for cChan in range(EEG.nbchan):
        # pull data and create vector for new data
        oldchanneldata = copy.deepcopy(EEG.data[cChan])
        newchanneldata = [numpy.nan] * len(oldchanneldata)
        spanstart = 0
        boolcont = True
        
        while boolcont:
            # determine what to pull
            segstart = spanstart
            segstop = segstart + interval
            if segstop > len(oldchanneldata):
                segstop = len(oldchanneldata) - 1
            
            # if the span distance is less than the overlap then stop
            if int(numpy.subtract(segstop, segstart)) < int(numpy.round(numpy.multiply(interval,Overlap))):
                boolcont = False
                
            if boolcont:
                # pull segment of data
                tempvect = numpy.array(oldchanneldata[segstart:segstop])
                
                # threshold is normalized to entire span with 1 being the max and 0 being the min
                indexes = peakutils.indexes(tempvect, thres=Threshold, min_dist=Peakspacing)
        
                boolshow = False
                if boolshow:
                    x = numpy.array(range(len(tempvect)))
                    matplotlib.pyplot.figure(figsize=(10,6))
                    peakutilspplot(x, tempvect, indexes)
                    
                # Pull peak data as real   
                for cP in range(len(tempvect)):
                    # if the point was identified as a peak
                    if cP in indexes:
                        newchanneldata[segstart + cP] = oldchanneldata[segstart + cP]
                    
            spanstart = numpy.add(spanstart, int(numpy.round(numpy.multiply(interval,Overlap))))
         
        filtdata = numpy.array(newchanneldata.copy())
        nans, x= numpy.isnan(filtdata), lambda z: z.nonzero()[0]
        filtdata[nans] = numpy.interp(x(nans), x(~nans), filtdata[~nans])               
        
        OUTEEG.data[cChan] = copy.deepcopy(filtdata)
    
    return OUTEEG

def catcheyeblinks(EEG, Threshold=False, Interpolate=True):
    OUTEEG = copy.deepcopy(EEG)
    
    if Threshold == False:
        Threshold = 1.0
    
    if OUTEEG.trials > 0:
        
        chanlist = ['Lpsize','Rpsize']
        OUTEEG.missingdata = []
        OUTEEG.missingdatalabels = []
        for cChan in range(len(chanlist)):
            currentcchannel = []
            OUTEEG.missingdatalabels.append(chanlist[cChan])
            
            for cE in range(OUTEEG.trials):
            
                workingdata = numpy.array(OUTEEG.data[OUTEEG.channels.index(chanlist[cChan])][cE].copy())
                threshlimit = [i for i,v in enumerate(abs(workingdata)) if v > float(Threshold)]
                
                # add one point prior to and following each
                newthreshlimit = []
                for cH in range(len(threshlimit)):
                    if (threshlimit[cH]-1) > 0:
                        newthreshlimit.append(threshlimit[cH]-1)
                    newthreshlimit.append(threshlimit[cH])
                    if (threshlimit[cH]+1) < len(workingdata):
                        newthreshlimit.append(threshlimit[cH]+1)
                threshlimit = numpy.unique(newthreshlimit)
                
                # replace with nan
                boolthresh = [False] * len(workingdata)
                for cH in range(len(threshlimit)):
                    boolthresh[threshlimit[cH]] = True
                workingdata[boolthresh] = numpy.nan
        
                # mark where missing data was
                currentcchannel.append(boolthresh)
                
                if Interpolate:
                    
                    try:
                        filtdata = numpy.array(workingdata.copy())
                        nans, x= numpy.isnan(filtdata), lambda z: z.nonzero()[0]
                        filtdata[nans] = numpy.interp(x(nans), x(~nans), filtdata[~nans])
                        workingdata = numpy.ndarray.tolist(filtdata.copy())
                    except:
                        pass
                
                # restore data
                OUTEEG.data[OUTEEG.channels.index(chanlist[cChan])][cE] = copy.deepcopy(workingdata)
                
            OUTEEG.missingdata.append(currentcchannel)
            
    return OUTEEG



class inspectionwindow:
    
    def __init__(self):
        
        self.LearnPositive = 0.25
        self.LearnNegative = 0.4
        self.yscale = [-50, 70]
        self.xscale = False
        self.channels = False
        self.polarity = 'Positive Down'
        
        self.rejectcolor = '#ffd4d4'
        self.acceptcolor = '#ededed'
        self.missingcolor = '#c7c7c7'
        
        self.trial1color = '#1d9100'
        self.trial2color = '#007291'
        self.Avgcolor = '#6b6b6b'
        
        self.WindowColor = '#D9D9D9'
        self.AxisColor = '#C7C7C7'
        self.AxisTickColor = '#303030'
        self.AxisFontSize = 10
        
        self.ButtonLabelSize = 14
        self.ButtonFaceColor = '#4D4D4D'
        self.ButtonTextColor = '#FFFFFF'
        self.ButtonHoverColor = '#BABABA'
        
        self.TextLabelColor = '#303030'
        self.TextLabelSize = 12
        
        self.fig = matplotlib.pyplot.figure(figsize=[17, 10])
        self.fig.patch.set_facecolor(self.WindowColor)
        gs = self.fig.add_gridspec(3, 4)
        
        self.pltax11 = self.fig.add_subplot(gs[0, 0])
        self.pltax12 = self.fig.add_subplot(gs[0, 1])
        self.pltax13 = self.fig.add_subplot(gs[0, 2])
        self.pltax14 = self.fig.add_subplot(gs[0, 3])
        
        self.pltax21 = self.fig.add_subplot(gs[1, 0])
        self.pltax22 = self.fig.add_subplot(gs[1, 1])
        self.pltax23 = self.fig.add_subplot(gs[1, 2])
        self.pltax24 = self.fig.add_subplot(gs[1, 3])
        
        self.pltax31 = self.fig.add_subplot(gs[2, 0])
        self.pltax32 = self.fig.add_subplot(gs[2, 1])
        self.pltax33 = self.fig.add_subplot(gs[2, 2])
        self.pltax34 = self.fig.add_subplot(gs[2, 3])
                                     
        matplotlib.pyplot.gcf().canvas.set_window_title('Visually Inspect Data')
        matplotlib.pyplot.tight_layout()
        matplotlib.pyplot.subplots_adjust(left=0.035, bottom=0.1, right=0.99, top=0.92, wspace=0.2, hspace=0.2)
        self.fig.canvas.window().statusBar().setVisible(False) # Remove status bar (bottom bar)
        self.fig.canvas.mpl_connect('close_event', self.handle_close)
        
        for tobj in [self.pltax11, self.pltax21, self.pltax31]:
            tobj.spines['top'].set_visible(False)
            tobj.spines['bottom'].set_visible(True)
            tobj.spines['left'].set_visible(True)
            tobj.spines['right'].set_visible(False)
            tobj.spines['bottom'].set_color(self.AxisColor) 
            tobj.spines['left'].set_color(self.AxisColor) 
            tobj.tick_params(axis='x', colors=self.AxisColor)
            tobj.tick_params(axis='y', colors=self.AxisColor)
            tobj.use_sticky_edges = True
            for item in (tobj.get_xticklabels()):
                item.set_fontsize(self.AxisFontSize)
            for item in (tobj.get_yticklabels()):
                item.set_fontsize(self.AxisFontSize)
            tobj.tick_params(axis='x', colors=self.AxisTickColor)
            tobj.tick_params(axis='y', colors=self.AxisTickColor)
            tobj.patch.set_facecolor(self.missingcolor)
        
        for tobj in [self.pltax12, self.pltax13, self.pltax14, self.pltax22, self.pltax23, self.pltax24, self.pltax32, self.pltax33, self.pltax34]:
            tobj.spines['top'].set_visible(False)
            tobj.spines['bottom'].set_visible(True)
            tobj.spines['left'].set_visible(False)
            tobj.spines['right'].set_visible(False)
            tobj.spines['bottom'].set_color(self.AxisColor) 
            #tobj.spines['left'].set_color(self.AxisColor) 
            tobj.tick_params(axis='x', colors=self.AxisColor)
            #tobj.tick_params(axis='y', colors=self.AxisColor)
            tobj.use_sticky_edges = True
            for item in (tobj.get_xticklabels()):
                item.set_fontsize(self.AxisFontSize)
            #for item in (tobj.get_yticklabels()):
            #    item.set_fontsize(self.AxisFontSize)
            tobj.get_yaxis().set_ticks([])
            tobj.tick_params(axis='x', colors=self.AxisTickColor)
            #tobj.tick_params(axis='y', colors=self.AxisTickColor)
            tobj.patch.set_facecolor(self.missingcolor)
        
        
        # Add buttons
        
        self.pageback = Button(matplotlib.pyplot.axes([0.015, 0.005, 0.12, 0.06]), 'Page Back', color=self.ButtonFaceColor, hovercolor=self.ButtonHoverColor)  #xpos, ypos, xsize, ysize
        self.pageback.label.set_fontsize(self.ButtonLabelSize)
        self.pageback.label.set_color(self.ButtonTextColor)
        self.pageback.on_clicked(self.pagebackward)
        
        self.pagefor = Button(matplotlib.pyplot.axes([0.87, 0.005, 0.12, 0.06]), 'Page Forward', color=self.ButtonFaceColor, hovercolor=self.ButtonHoverColor)  #xpos, ypos, xsize, ysize
        self.pagefor.label.set_fontsize(self.ButtonLabelSize)
        self.pagefor.label.set_color(self.ButtonTextColor)
        self.pagefor.on_clicked(self.pageforward)
        
        self.rejectall = Button(matplotlib.pyplot.axes([0.015, 0.94, 0.12, 0.05]), 'Reject All', color=self.ButtonFaceColor, hovercolor=self.ButtonHoverColor)  #xpos, ypos, xsize, ysize
        self.rejectall.label.set_fontsize(self.ButtonLabelSize)
        self.rejectall.label.set_color(self.ButtonTextColor)
        self.rejectall.on_clicked(self.rejectallbutton_clk)
        
        self.acceptall = Button(matplotlib.pyplot.axes([0.155, 0.94, 0.12, 0.05]), 'Accept All', color=self.ButtonFaceColor, hovercolor=self.ButtonHoverColor)  #xpos, ypos, xsize, ysize
        self.acceptall.label.set_fontsize(self.ButtonLabelSize)
        self.acceptall.label.set_color(self.ButtonTextColor)
        self.acceptall.on_clicked(self.acceptallbutton_clk)
        
        self.addpage = Button(matplotlib.pyplot.axes([0.59, 0.94, 0.12, 0.05]), 'Smart Add local', color=self.ButtonFaceColor, hovercolor=self.ButtonHoverColor)  #xpos, ypos, xsize, ysize
        self.addpage.label.set_fontsize(self.ButtonLabelSize)
        self.addpage.label.set_color(self.ButtonTextColor)
        self.addpage.on_clicked(self.learnposbuttonCallback)
        
        self.addall = Button(matplotlib.pyplot.axes([0.73, 0.94, 0.12, 0.05]), 'Smart Add', color=self.ButtonFaceColor, hovercolor=self.ButtonHoverColor)  #xpos, ypos, xsize, ysize
        self.addall.label.set_fontsize(self.ButtonLabelSize)
        self.addall.label.set_color(self.ButtonTextColor)
        self.addall.on_clicked(self.learnposallbuttonCallback)
        
        self.removepage = Button(matplotlib.pyplot.axes([0.87, 0.94, 0.12, 0.05]), 'Smart Remove local', color=self.ButtonFaceColor, hovercolor=self.ButtonHoverColor)  #xpos, ypos, xsize, ysize
        self.removepage.label.set_fontsize(self.ButtonLabelSize)
        self.removepage.label.set_color(self.ButtonTextColor)
        self.removepage.on_clicked(self.learnnegbuttonCallback)
        
        self.eegscaleupbutton = Button(matplotlib.pyplot.axes([0.3805, 0.005, 0.12, 0.045]), 'scale up', color=self.ButtonFaceColor, hovercolor=self.ButtonHoverColor)  #xpos, ypos, xsize, ysize
        self.eegscaleupbutton.label.set_fontsize(self.ButtonLabelSize)
        self.eegscaleupbutton.label.set_color(self.ButtonTextColor)
        self.eegscaleupbutton.on_clicked(self.eegscaleupbutton_clk)
        
        self.eegscaledownbutton = Button(matplotlib.pyplot.axes([0.51, 0.005, 0.12, 0.045]), 'scale down', color=self.ButtonFaceColor, hovercolor=self.ButtonHoverColor)  #xpos, ypos, xsize, ysize
        self.eegscaledownbutton.label.set_fontsize(self.ButtonLabelSize)
        self.eegscaledownbutton.label.set_color(self.ButtonTextColor)
        self.eegscaledownbutton.on_clicked(self.eegscaledownbutton_clk)
        
        
        # add text
        self.acceptedlabel = self.fig.text(0.36, 0.983, 'X of X Trials Accepted', horizontalalignment='left', verticalalignment='top', weight='medium', size=self.TextLabelSize, color=self.TextLabelColor)
        self.triallabel = self.fig.text(0.36, 0.955, 'Trial: X to X', horizontalalignment='left', verticalalignment='top', weight='medium', size=self.TextLabelSize, color=self.TextLabelColor)
        
        self.fig.canvas.mpl_connect('button_press_event', self.onClick)
        self.fig.canvas.mpl_connect('key_press_event', self.onKey)
        
        self.activefigs = [False] * 12
        self.activetrials = [-1] * 12 
        self.reject = []
        
    def onKey(self, event):
        
        if event.key == 'left':
            self.pagebackward()
            
        if event.key == 'right':
            self.pageforward()
            
        if event.key == 'down':
            self.yscale = numpy.multiply(self.yscale, 1.25);
            
        if event.key == 'shift+down':
            self.yscale = numpy.add(self.yscale, 0.5);
            
        if event.key == 'up':
            self.yscale = numpy.multiply(self.yscale, 0.75);
            
        if event.key == 'shift+up':
            self.yscale = numpy.add(self.yscale, -0.5);
        
        self.update()
        
    def onClick(self, event):
        
        subPlotNr = self.getSubPlotNr(event)
        if subPlotNr != None:
            
            if subPlotNr == 0:
                tobj = self.pltax11
            elif subPlotNr == 1:
                tobj = self.pltax12
            elif subPlotNr == 2:
                tobj = self.pltax13
            elif subPlotNr == 3:
                tobj = self.pltax14
            elif subPlotNr == 4:
                tobj = self.pltax21
            elif subPlotNr == 5:
                tobj = self.pltax22
            elif subPlotNr == 6:
                tobj = self.pltax23
            elif subPlotNr == 7:
                tobj = self.pltax24
            elif subPlotNr == 8:
                tobj = self.pltax31
            elif subPlotNr == 9:
                tobj = self.pltax32
            elif subPlotNr == 10:
                tobj = self.pltax33
            elif subPlotNr == 11:
                tobj = self.pltax34
            
            if subPlotNr < 12:
                # is the click on a figure that is active
                if self.activefigs[subPlotNr]:
                    if self.activetrials[subPlotNr] != -1:
                        
                        # match figure to trial
                        if self.EEG.reject[self.activetrials[subPlotNr]] == 0:
                            # currently accepted so need to reject it
                            self.EEG.reject[self.activetrials[subPlotNr]] = 3
                        else:
                            # currently rejected so need to accept it
                            self.EEG.reject[self.activetrials[subPlotNr]] = 0
                        
                        self.updateaverage()
                        self.update()
                
        
    def getSubPlotNr(self, event):
        i = 0
        axisNr = None
        for axis in self.fig.axes:
            if axis == event.inaxes:
                axisNr = i		
                break
            i += 1
        return axisNr
    
    def inspect(self, EEG, chanlist1=False, chanlist2=False):
        
        self.startingtrial = 0
        self.EEG = EEG
        self.xtime = self.EEG.times;
        
        if self.xscale == False:
            self.xscale = [numpy.multiply(self.EEG.times[0],1), numpy.multiply(self.EEG.times[-1],1)]
       
        for tobj in [self.pltax11, self.pltax12, self.pltax13, self.pltax14, self.pltax21, self.pltax22, self.pltax23, self.pltax24, self.pltax31, self.pltax32, self.pltax33, self.pltax34]:
            tobj.set_xlim([numpy.divide(float(self.xscale[0]),1), numpy.divide(float(self.xscale[1]),1)])
            
        #self.xtimeticks = numpy.linspace(1,int(math.floor(self.rollingspan-1)),int(self.rollingspan-1)).tolist()
        #self.xtimeticks = [int(i) for i in self.xtimeticks] 
        #self.pltax11.xaxis.set_major_locator(ticker.FixedLocator(self.xtimeticks))
        #self.pltax11.set_ylim([0, (self.numberOfAcquiredChannels+1)*self.timeplotoffsetscale])
        
        
        startindex = numpy.argmin(abs(numpy.subtract(self.EEG.times,numpy.divide(float(self.xscale[0]),1))))
        stopindex = numpy.argmin(abs(numpy.subtract(self.EEG.times,numpy.divide(float(self.xscale[1]),1))))
        self.xtime = self.xtime[startindex:stopindex]
        
        # populate initial links for the trials
        cE = 0
        while cE < len(self.EEG.reject):
            self.activetrials[cE] = cE
            cE = cE + 1
            if cE >= 11:
                cE = len(self.EEG.reject)
        
        # populate data
        self.Mat1 = []
        if chanlist1 != False:
            for cE in range(EEG.trials):
                currentepoch = []
                for cC in range(len(chanlist1)):
                    try:
                        workingindex = EEG.channels.index(chanlist1[cC])
                    except:
                        workingindex = -1
                        pass
                    
                    if workingindex > -1:
                        currentepoch.append(numpy.array(EEG.data[workingindex][cE][startindex:stopindex]))
                    
                currentepoch = numpy.vstack(currentepoch)
                self.Mat1.append(numpy.nanmean(currentepoch, axis=0))
        
        self.Mat2 = []
        if chanlist2 != False:
            for cE in range(EEG.trials):
                currentepoch = []
                for cC in range(len(chanlist1)):
                    try:
                        workingindex = EEG.channels.index(chanlist2[cC])
                    except:
                        workingindex = -1
                        pass
                    
                    if workingindex > -1:
                        currentepoch.append(numpy.array(EEG.data[workingindex][cE][startindex:stopindex]))
                    
                currentepoch = numpy.vstack(currentepoch)
                self.Mat2.append(numpy.nanmean(currentepoch, axis=0))
        
        # populate average
        self.updateaverage()
        
        # load plot data
        self.trialmin = 0
        self.trialmax = 0
        self.avglines = []
        self.mat1lines = []
        self.mat2lines = []
        self.plotobjs = [self.pltax11, self.pltax12, self.pltax13, self.pltax14, self.pltax21, self.pltax22, self.pltax23, self.pltax24, self.pltax31, self.pltax32, self.pltax33, self.pltax34]
        for cW in range(12):
            
            # have we exceeded available trials
            if (self.startingtrial + cW) < self.EEG.trials:
                    
                # store trial number
                self.activetrials[cW] = (self.startingtrial + cW)
                if cW == 0:
                    self.trialmin = self.activetrials[cW]
                else:
                    self.trialmax = self.activetrials[cW]
                    
                self.activefigs[cW] = True
           
                # plot the average
                avline, = self.plotobjs[cW].plot(self.xtime, self.AvgMat, linewidth=3.0, color=self.Avgcolor) 
                self.avglines.append(avline)
            
                # plot the epocchs
                if len(self.Mat1) > 0:
                    mat1line, = self.plotobjs[cW].plot(self.xtime, self.Mat1[self.activetrials[cW]], linewidth=2.0, color=self.trial1color) 
                    self.mat1lines.append(mat1line)
        
                if len(self.Mat2) > 0:
                    mat2line, = self.plotobjs[cW].plot(self.xtime, self.Mat2[self.activetrials[cW]], linewidth=2.0, color=self.trial2color) 
                    self.mat2lines.append(mat2line)
        
                self.plotobjs[cW].set_ylim(self.yscale)
                
                # set plot color
                if self.EEG.reject[self.activetrials[cW]] == 0:
                    self.plotobjs[cW].patch.set_facecolor(self.acceptcolor)
                else:
                    self.plotobjs[cW].patch.set_facecolor(self.rejectcolor)
                    
        
        self.triallabel.set_text('Trial: %d to %d' % (int(self.trialmin), int(self.trialmax)))
        
        self.update()
        
        #ani = matplotlib.animation.FuncAnimation(self.fig, self.update, interval=self.updatetime, blit=False)
        matplotlib.pyplot.show()
        
        
    def updateaverage(self):
        
        try:
            spansize = (max(len(self.Mat1[0]), len(self.Mat2[0])))
        except:
            try:
                spansize = len(self.Mat1[0])
            except:
                spansize = len(self.Mat2[0])
        
        self.AvgMat = []
        currentepoch = []
        for cE in range(self.EEG.trials):
            if self.EEG.reject[cE] == 0:
                if len(self.Mat1) > 0:
                    currentepoch.append(self.Mat1[cE])
                if len(self.Mat2) > 0:
                    currentepoch.append(self.Mat2[cE])
                    
        # if there were no accepted epochs then just populate the average with 0
        if len(currentepoch) == 0:
            self.AvgMat = numpy.array([0] * spansize)
        else:
            currentepoch = numpy.vstack(currentepoch)
            self.AvgMat = numpy.nanmean(currentepoch, axis=0)
        
        
        
    def rejectallbutton_clk(self, *args): 
        self.EEG.reject = [3] * self.EEG.trials
        self.updateaverage()
        self.update()
        
    def acceptallbutton_clk(self, *args): 
        self.EEG.reject = [0] * self.EEG.trials
        self.updateaverage()
        self.update()
        
    def eegscaleupbutton_clk(self, *args): 
        self.yscale = numpy.multiply(self.yscale, 1.25);
        self.update()
        
    def eegscaledownbutton_clk(self, *args): 
        self.yscale = numpy.multiply(self.yscale, 0.75);
        self.update()
        
    def update(self):
        
        # update plot colors and scales
        for cW in range(12):
            self.plotobjs[cW].set_ylim(self.yscale)
            if self.activetrials[cW] > -1:
                if self.EEG.reject[self.activetrials[cW]] == 0:
                    self.plotobjs[cW].patch.set_facecolor(self.acceptcolor)
                else:
                    self.plotobjs[cW].patch.set_facecolor(self.rejectcolor)
                    
        # update average    
        for cobj in self.avglines:
            cobj.set_ydata(self.AvgMat)
        
        # make sure lines reflect current trials
        for cW in range(12):
            if self.activetrials[cW] > -1:
        
                if len(self.Mat1) > 0:
                    self.mat1lines[cW].set_ydata(self.Mat1[self.activetrials[cW]])
                    
                if len(self.Mat2) > 0:
                    self.mat2lines[cW].set_ydata(self.Mat2[self.activetrials[cW]])
        
                if cW == 0:
                    self.trialmin = self.activetrials[cW]
                else:
                    self.trialmax = self.activetrials[cW]
        
        # update text
        qcount = 0
        for cE in range(self.EEG.trials):
            if self.EEG.reject[cE] == 0:
                qcount = qcount + 1
        
        self.acceptedlabel.set_text('%d of %d Trials Accepted' % (int(qcount), int(self.EEG.trials)))
        self.triallabel.set_text('Trial: %d to %d' % (int(self.trialmin)+1, int(self.trialmax)+1))
        
        self.reject = copy.deepcopy(self.EEG.reject)
        
        self.fig.canvas.draw_idle()
    
    def pageforward(self, *args):
        
        self.startingtrial = self.startingtrial + 12
        if self.startingtrial > (self.EEG.trials-12):
            self.startingtrial = (self.EEG.trials-12)
            
        # deactivate and reactivate trials
        self.activetrials = [-1] * 12 
        for cW in range(12):
            if (self.startingtrial + cW) < self.EEG.trials:
                self.activetrials[cW] = (self.startingtrial + cW)
                
        self.update()
        
    def pagebackward(self, *args):
        
        self.startingtrial = self.startingtrial - 12
        if self.startingtrial < 0:
            self.startingtrial = 0
            
        # deactivate and reactivate trials
        self.activetrials = [-1] * 12 
        for cW in range(12):
            if (self.startingtrial + cW) < self.EEG.trials:
                self.activetrials[cW] = (self.startingtrial + cW)
                
        self.update()
        
        
    def learnposbuttonCallback(self, *args):
        
        # obtain average of currently accepted trials
        self.updateaverage()
        
        # obtain correlation between average and each trial currently being displayed
        cormatrix = [0] * 12
        for cW in range(12):
        
            corr1 = 0
            if len(self.Mat1) > 0:
                corr1, _ = pearsonr(self.AvgMat, self.Mat1[self.activetrials[cW]])
            corr2 = 0
            if len(self.Mat2) > 0:
                corr2, _ = pearsonr(self.AvgMat, self.Mat2[self.activetrials[cW]])
            else:
                corr2 = copy.deepcopy(corr1)
            
            cormatrix[cW] = numpy.divide(numpy.add(corr1, corr2),2)
            if cormatrix[cW] >= self.LearnPositive:
                self.EEG.reject[self.activetrials[cW]] = 0
        
        self.update()
        
        
    def learnposallbuttonCallback(self, *args):
        
        # obtain average of currently accepted trials
        self.updateaverage()
        
        # obtain correlation between average and all trials
        for cW in range(self.EEG.trials):
        
            corr1 = 0
            if len(self.Mat1) > 0:
                corr1, _ = pearsonr(self.AvgMat, self.Mat1[cW])
            corr2 = 0
            if len(self.Mat2) > 0:
                corr2, _ = pearsonr(self.AvgMat, self.Mat2[cW])
            else:
                corr2 = copy.deepcopy(corr1)
            
            cormatrix = numpy.divide(numpy.add(corr1, corr2),2)
            if cormatrix >= self.LearnPositive:
                self.EEG.reject[cW] = 0
        
        self.update()
        
    def learnnegbuttonCallback(self, *args):
        
        # obtain average of currently accepted trials
        self.updateaverage()
        
        # obtain correlation between average and each trial currently being displayed
        cormatrix = [0] * 12
        for cW in range(12):
        
            corr1 = 0
            if len(self.Mat1) > 0:
                corr1, _ = pearsonr(self.AvgMat, self.Mat1[self.activetrials[cW]])
            corr2 = 0
            if len(self.Mat2) > 0:
                corr2, _ = pearsonr(self.AvgMat, self.Mat2[self.activetrials[cW]])
            else:
                corr2 = copy.deepcopy(corr1)
            
            cormatrix[cW] = numpy.divide(numpy.add(corr1, corr2),2)
            if cormatrix[cW] <= self.LearnNegative:
                self.EEG.reject[self.activetrials[cW]] = 3
        
        self.update()
        
        
    def handle_close(self, evt, *args):
        #matplotlib.pyplot.close()
        bolerr = 1 

def writeeegtofile(EEG, fileout):
    OUTEEG = copy.deepcopy(EEG)
    
    f = open(fileout, 'w') # Write to file - Any original file is overwritten

    f.write('file version = eegpipe_1.0.0\n')
    f.write('srate = %f\n' % OUTEEG.srate)
    f.write('nbchan = %d\n' % OUTEEG.nbchan)
    f.write('channels = ')
    for i in range(OUTEEG.nbchan):
        f.write('%s' % OUTEEG.channels[i])
        if (i < OUTEEG.nbchan-1): f.write(', ')
    f.write('\n')
    f.write('points = %d\n' % OUTEEG.pnts)
    f.write('times = ')
    for i in range(OUTEEG.pnts):
        f.write('%f' % OUTEEG.times[i])
        if (i < len(OUTEEG.times)-1): f.write(', ')
    f.write('\n')
    f.write('trials = %d\n' % OUTEEG.trials)
    f.write('data:\n')
    f.write('Event, Time, Markers, Reject, ')
    for i in range(OUTEEG.nbchan):
        f.write('%s' % OUTEEG.channels[i])
        if (i < OUTEEG.nbchan-1): f.write(', ')
    f.write('\n')
    if OUTEEG.trials > 0:
        for cE in range(OUTEEG.trials):
            for cT in range(OUTEEG.pnts):
                
                # Event   Time    Markers   Reject  Channel
                f.write('%d, ' % (cE+1)) # event
                f.write('%f, ' % (OUTEEG.times[cT])) # time
                f.write('%0.1f, ' % (OUTEEG.events[0][cE][cT])) # markers
                f.write('%0.1f, ' % (OUTEEG.reject[cE])) # reject
                for cChan in range(OUTEEG.nbchan):
                    f.write('%f' % (OUTEEG.data[cChan][cE][cT])) # channel
                    if (cChan < OUTEEG.nbchan-1): f.write(', ')
                f.write('\n')
    else:
    
        for cT in range(OUTEEG.pnts):
            # Event   Time    Markers   Reject  Channel
            f.write('%d, ' % (0)) # event
            f.write('%f, ' % (OUTEEG.times[cT])) # time
            f.write('%0.1f, ' % (OUTEEG.events[0][cT])) # markers
            f.write('%0.1f, ' % (0)) # reject
            for cChan in range(OUTEEG.nbchan):
                f.write('%f' % (OUTEEG.data[cChan][cT])) # channel
                if (cChan < OUTEEG.nbchan-1): f.write(', ')
            f.write('\n')
    f.close()
    
    
        
def realignvector(invector, oldpoint, newpoint, fill=False):
    dat = copy.deepcopy(invector)
    
    if fill==False:
        outdat = numpy.array([numpy.nan] * len(invector))
    else:
        outdat = numpy.array([fill] * len(invector))
    
    offset = oldpoint - newpoint
    
    for cP in range(len(outdat)):
        
        newoff = cP + offset
        if (newoff >= 0) and (newoff < len(outdat)):
            outdat[cP] = dat[newoff]
    
    return outdat    
    



  
def createsignal(Window, Latency, Amplitude, Width, Shape, Smoothing, OverallSmooth, Srate):   
    
    xtime = numpy.arange(Window[0],Window[1],numpy.divide(1.0,Srate))
    outvect = []
    
    for cR in range(len(Latency)):
        
        comp = numpy.zeros(len(xtime))
        matchindex = closestidx(xtime, Latency[cR])  # find point to place
        comp[matchindex] = abs(Amplitude[cR])  # place amplitude
        
        # expand to accomodate wider smoothing
        locatorcomp = numpy.zeros(len(xtime))
        locatorcomp[0] = 1; locatorcomp[-1] = 1; 
        expandexcomp = numpy.pad(copy.deepcopy(comp), (len(xtime)*3,len(xtime)*3), 'constant', constant_values=(0, 0))
        locatorcomp = numpy.pad(copy.deepcopy(locatorcomp), (len(xtime)*3,len(xtime)*3), 'constant', constant_values=(0, 0))
        trimlocators = numpy.where(locatorcomp == 1)
        trimlocators[0][0] = trimlocators[0][0] - 1
        
        if Shape == 0:
            expandexcomp = smooth(expandexcomp, span=Width[cR], window='hanning')
            comp = copy.deepcopy(expandexcomp[trimlocators[0][0]:trimlocators[0][1]])
        else:
            # base seg
            expandexcomp = minmax_scaling(smooth(expandexcomp, span=Width[cR], window='hanning'),0,0,abs(Amplitude[cR]))
            tempshape = minmax_scaling(smooth(expandexcomp, span=Shape[cR], window='blackman'),0,0,abs(Amplitude[cR]))
    
            # trim down to original size
            comp = copy.deepcopy(expandexcomp[trimlocators[0][0]:trimlocators[0][1]])
            tempshape = copy.deepcopy(tempshape[trimlocators[0][0]:trimlocators[0][1]])
    
            # replace segments
            if Shape[cR] < 0:
                comp[0:matchindex-1] = tempshape[0:matchindex-1]
            else:
                comp[matchindex+1:-1] = tempshape[matchindex+1:-1]
                
        if float(Smoothing[cR]) != float(0.0):
            comp = smooth(comp, span=int(Smoothing[cR]), window='hanning')
            
        comp = minmax_scaling(comp, 0, 0.0, float(abs(Amplitude[cR])))
        if Amplitude[cR] < 0:
            comp = comp * -1
            
        outvect.append(copy.deepcopy(comp))
    
    outsum = numpy.sum(numpy.vstack(copy.deepcopy(outvect)), axis=0)
    if float(OverallSmooth) != float(0.0):
        outsum = smooth(outsum, span=int(OverallSmooth), window='hanning')

    return [outsum, outvect, xtime]

    
# # # # #
# DEBUG #
if __name__ == "__main__":
    
    EEG = eeglabstructure()
    
    basedate = pandas.to_datetime('2020-12-29 00:00:20')
    comparisondate = pandas.to_datetime('2020-12-29 00:01:20')
    timevvalue = msdatefromref(basedate, comparisondate)
    
    textvalue = 'Mean'
    textvalue = checkdefaultsettings(textvalue, ['median', 'mean'])
    
    
    Channels = ['FPZ', 'F3', 'FZ', 'F4', 'T7', 'C3', 'CZ', 'C4', 'T8', 'P7', 'P3', 'PZ', 'P4', 'P8', 'OZ']
    Amplitude = [0, 3, 3, 1, 0, 7, 5, 4, 0, 2, 7, 8, 2, 2, 0]
    eggheadplot(Channels, Amplitude, Scale = [1, 9], Steps = 256, BrainOpacity = 0.2, Title ='Egghead', Colormap=crushparula(256))

    
    [outsum, outvect, xtime] = createsignal(Window = [-0.1, 1.0],
                 Latency =   [ 0.08,  0.25, 0.35],
                 Amplitude = [-0.1,  -0.45, 0.50],
                 Width =     [40,       80,  180],
                 Shape =     [0,         0,    0],
                 Smoothing = [0,         0,    0],
                 OverallSmooth = 20,
                 Srate = 250.0)
    plot(outvect, xtime)
    plot(outsum*-1, xtime)
