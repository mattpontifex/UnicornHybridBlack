
#https://docs.bokeh.org/en/latest/docs/user_guide/layout.html#userguide-layout
import os
import sys 
import math
import numpy
import scipy.signal
import matplotlib.mlab as mlab
from bokeh.io import output_file
from bokeh.layouts import row, column
from bokeh.plotting import curdoc, figure, ColumnDataSource
from bokeh.models.widgets import Button, Toggle, Panel, Tabs
from bokeh.models.annotations import Label
from bokeh.palettes import viridis
from functools import partial
from threading import Thread
import time
from tornado import gen
sys.path.append(os.getcwd())
import Engine.unicornhybridblack as unicornhybridblack

# features to add


class UnicornBlackPlottingFunctions():    
    """class for data visualization using the g.tec Unicorn Hybrid Black
	"""
    
    def __init__(self):
        
        self._scale = 500
        self._datascale = 1
        
        # Read in parameter file
        inputfile = r'StreamingDeviceID.txt'
        dcontents = 0
        deveryline = []
        dcontents = open(inputfile).readlines()
        for dinfo in range(0, len(dcontents)):
            deveryline.append(dcontents[dinfo].split('='))
            for dinfoC in range(0, len(deveryline[dinfo])):
                deveryline[dinfo][dinfoC] = deveryline[dinfo][dinfoC].strip()  
                deveryline[dinfo][dinfoC] = deveryline[dinfo][dinfoC].rstrip()   
         
        # set parameters
        self.deviceID = None
        self.channellabels = ['FZ', 'C3', 'CZ', 'C4', 'PZ', 'O1', 'OZ', 'O2']
        self._rollingspan = 5
        self._samplefreq = 250.0
        self._filtersettings = [0.5, 30]
        for dinfo in range(0, len(dcontents)):
            if (deveryline[dinfo][0] == 'deviceID'):
                self.deviceID = deveryline[dinfo][1]
            if (deveryline[dinfo][0] == 'channellabels'):
                self.channellabels = deveryline[dinfo][1].split(',')
                for dinfoC in range(0, len(self.channellabels)):
                    self.channellabels[dinfoC] = self.channellabels[dinfoC].strip()
            if (deveryline[dinfo][0] == 'rollingspan'):
                self._rollingspan = float(deveryline[dinfo][1])
            if (deveryline[dinfo][0] == 'samplefreq'):
                self._samplefreq = float(deveryline[dinfo][1])
            if (deveryline[dinfo][0] == 'filtersettings'):
                temparray = deveryline[dinfo][1].split(',')
                self._filtersettings = [float(temparray[0]), float(temparray[1])]
        
        
        self._rollingspanpoints = int(math.floor( float(self._rollingspan) * float(self._samplefreq) ))
        self._baselinerollingspan = int(self._rollingspanpoints / 10.0)
        self.res = None
        self.source = None
        self._filterdata = False
        self.freqdata = []
        self._numberOfAcquiredChannels = len(self.channellabels)
        self.altchannellabels = self.channellabels[:]
        self.altchannellabels.reverse()
        self.data = [[0.0] * self._numberOfAcquiredChannels] * self._rollingspanpoints
        
        # connect to Device
        self.UnicornBlack = unicornhybridblack.UnicornBlackFunctions() 
        self.UnicornBlack.connect(deviceID=self.deviceID, rollingspan=self._rollingspan)
        
        if self.deviceID is not None:
                # pull real data
                self.data = self.UnicornBlack.data
                
        self._plottingdata = numpy.array(self.data)
        self.xtime = numpy.ndarray.tolist(numpy.linspace(0, self._rollingspan, self._rollingspanpoints))
        self.paletsize = int(self._numberOfAcquiredChannels*1.5)
        self.colorpalet = viridis(self.paletsize)
                
        bhp, ahp = scipy.signal.butter(2, (self._filtersettings[0] / (self._samplefreq / 2)), btype='high')
        blp, alp = scipy.signal.butter(2, (self._filtersettings[1] / (self._samplefreq / 2)))
        self._hpfiltersettings = [bhp, ahp]
        self._lpfiltersettings = [blp, alp]
        self._badchannelbools = [False] * self._numberOfAcquiredChannels
        self.freqdatalength = 0
        for cP in range(self._numberOfAcquiredChannels):
            _power, tempfreqs = mlab.psd(x=self._plottingdata[:,cP], NFFT=self._scale, Fs=self._samplefreq, noverlap=int(self._rollingspanpoints/3.0), sides='onesided', scale_by_freq=True)
            self.freqdata.append(_power) 
        self.freqdatalength = len(_power)
        self._freqs = numpy.ndarray.tolist(tempfreqs)
        self._freqstep = tempfreqs[1]-tempfreqs[0]
        # grow the frequency list
        while len(self._freqs) < self._rollingspanpoints:
            self._freqs.append(float(self._freqs[-1]) + float(self._freqstep))
        self._freqs = numpy.array(self._freqs)
        
        
    def stopvisualization(self):
        self.UnicornBlack.disconnect()
        
    def startvisualization(self):
        
        # add data to source
        res = {self.channellabels[i]: self._plottingdata[:,i] for i in range(self._numberOfAcquiredChannels)} 
        res['Time'] = self.xtime
        
        # distribute data for plotting
        self.res = self._computedataoffset(res)
        self.source = ColumnDataSource(self.res)
                    
        output_file("UnicornBlackDataVisualizer.html")
                
        # time series
        self.plots = []
        self.lines = []
        self.channeltext = []
        cC = 0
        self.plots.append(figure(
                 x_axis_label='Time (seconds)',
                 x_axis_type='linear',
                 x_axis_location='below',
                 x_range=(0, self._rollingspan),         
                 y_axis_label='',
                 y_axis_type='linear',
                 y_axis_location='left',
                 y_range=(0, (self._numberOfAcquiredChannels+1)*self._scale),    
                 plot_height=850,
                 plot_width=1800,         
                 title='',
                 title_location='above',
                 tools=""))
        self.plots[cC].toolbar.autohide = True
        self.plots[cC].title.vertical_align = 'middle'
        self.plots[cC].title.align = 'left'
        self.plots[cC].ygrid.grid_line_color = None
        self.plots[cC].xaxis.minor_tick_line_color = None  # turn off x-axis minor ticks
        self.plots[cC].yaxis.major_tick_line_color = None  # turn off y-axis minor ticks
        self.plots[cC].yaxis.minor_tick_line_color = None  # turn off y-axis minor ticks
        self.plots[cC].yaxis[0].ticker.desired_num_ticks = self._numberOfAcquiredChannels
        self.plots[cC].yaxis.major_label_text_font_size = "0pt"
        self.plots[cC].min_border_left = 50
        
        for cL in range(self._numberOfAcquiredChannels):
           self.lines.append(self.plots[0].line(x='Time', y=self.channellabels[cL], source=self.source, color=self.colorpalet[cL], line_width=1, alpha=0.9))
           self.channeltext.append(Label(x=0, y=((cL + 1)*self._scale), x_offset=-45, x_units='data', y_units='data',text=self.altchannellabels[cL], text_font_size="20pt", text_color=self.colorpalet[cL], render_mode='css', background_fill_alpha=0.0, text_baseline="middle"))
           self.plots[cC].add_layout(self.channeltext[cL])
        
        self.scaletext = Label(x=(self._rollingspan + 0.05), y=5, y_offset=0, x_units='data', y_units='data',text=('Scale %.1f microvolts' % float(self._scale / float(self._datascale))), text_font_size="8pt", text_color='gray', render_mode='css', background_fill_alpha=0.0, text_baseline="middle")
        self.plots[cC].add_layout(self.scaletext)
        
        # add a button widget and configure with the call back
        Scaleupbutton = Button(label="Scaleup")
        Scaleupbutton.on_click(self._scaleup)
        Scaledownbutton = Button(label="Scaledown")
        Scaledownbutton.on_click(self._scaledown)
        
        self.Filterdatabutton = Toggle(label="Turn on Data Filter")
        self.Filterdatabutton.on_click(self.filtertoggle_handler)
        
        # frequency plots
        self.freqplots = []
        self.freqlines = []
        for cP in range(self._numberOfAcquiredChannels):
            self.freqplots.append(figure(
                             x_axis_label='Frequency',
                             x_axis_type='linear',
                             x_axis_location='below',
                             x_range=(0, 125),         
                             y_axis_label='',
                             y_axis_type='linear',
                             y_axis_location='left',
                             y_range=(0, 100000),    
                             plot_height=400,
                             plot_width=350,         
                             title=self.channellabels[cP],
                             title_location='above',
                             tools=""))
            self.freqplots[cP].toolbar.autohide = True
            self.freqplots[cP].title.vertical_align = 'middle'
            self.freqplots[cP].title.align = 'left'
            self.freqplots[cP].ygrid.grid_line_color = None
            self.freqplots[cP].xaxis.minor_tick_line_color = None  # turn off x-axis minor ticks
            self.freqplots[cP].yaxis.major_tick_line_color = None  # turn off y-axis minor ticks
            self.freqplots[cP].yaxis.minor_tick_line_color = None  # turn off y-axis minor ticks
            self.freqplots[cP].yaxis.major_label_text_font_size = "0pt"
            self.freqplots[cP].min_border_left = 20
        
            self.freqlines.append(self.freqplots[cP].line(x='Frequency', y=(self.channellabels[cP] + 'freq'), source=self.source, color='black', line_width=1.5, alpha=0.7))
        
        # This is important! Save curdoc() to make sure all threads
        # see the same document.
        self.doc = curdoc()
        
        tmseries = column(self.plots[0],row(Scaledownbutton,Scaleupbutton,self.Filterdatabutton))
        
        tab1 = Panel(child=tmseries, title="Time Series")
        
        fseries = column(row(self.freqplots[0],self.freqplots[1],self.freqplots[2],self.freqplots[3]),row(self.freqplots[4],self.freqplots[5],self.freqplots[6],self.freqplots[7]))
        tab2 = Panel(child=fseries, title="Frequency")
                
        # Put all the tabs into one application
        tabs = Tabs(tabs = [tab1, tab2])
        
        self.doc.add_root(tabs)        
        
        thread = Thread(target=self.blocking_task, args=[])
        thread.start()

    def filtertoggle_handler(self, active):
        if active:
            self._filterdata = True
            self.Filterdatabutton.label = 'Turn off Data Filter'
        else:
            self._filterdata = False
            self.Filterdatabutton.label = 'Turn on Data Filter'

    def _computedataoffset(self, presource):
        
        presource = self._computedatafilter(presource)
            
        for cC in range(self._numberOfAcquiredChannels):
            # baseline data to last points
            presource[self.channellabels[cC]] = numpy.ndarray.tolist(numpy.add(numpy.multiply(numpy.subtract(presource[self.channellabels[cC]], numpy.mean(presource[self.channellabels[cC]][-self._baselinerollingspan:])), float(self._datascale)), (cC + 1)*self._scale))
            
        return presource

    def _computedatafilter(self, presource):
        
        # check bad channels
        for cC in range(self._numberOfAcquiredChannels):
            _power, _freqs = mlab.psd(x=presource[self.channellabels[cC]], NFFT=self._scale, Fs=self._samplefreq, noverlap=int(self._rollingspanpoints/3.0), sides='onesided', scale_by_freq=True)
            self.freqdata[cC] = [0.0] * self._rollingspanpoints
            self.freqdata[cC][0:self.freqdatalength] = _power
            presource[self.channellabels[cC] + 'freq'] = self.freqdata[cC]
            presource['Frequency'] = self._freqs
            
            nonnoise = numpy.mean(self.freqdata[cC][numpy.argmin(abs(self._freqs-(35))):numpy.argmin(abs(self._freqs-(50)))])
            noise = numpy.mean(self.freqdata[cC][numpy.argmin(abs(self._freqs-(55))):numpy.argmin(abs(self._freqs-(65)))])
            if (float(nonnoise) > 0.0):
                if ((noise / float(nonnoise)) > 1.5):
                    self._badchannelbools[cC] = True
                    try:
                        self.channeltext[cC].text_color='red'
                    except:
                        pass
                else:
                    self._badchannelbools[cC] = False
                    try:
                        self.channeltext[cC].text_color=self.colorpalet[cC]
                    except:
                        pass
        
            if (self._filterdata):
                tempdata = scipy.signal.filtfilt(self._hpfiltersettings[0], self._hpfiltersettings[1], presource[self.channellabels[cC]], method="gust") # High pass:
                presource[self.channellabels[cC]] = scipy.signal.filtfilt(self._lpfiltersettings[0], self._lpfiltersettings[1], tempdata, method="gust") # low pass:
           
        return presource


    def _scaleup(self):
        self._datascale = self._datascale * 2.0
        self.updatesamples()
        self.scaletext.text = ('Scale %.1f microvolts' % float(self._scale / float(self._datascale)))
        
    def _scaledown(self):
        self._datascale = self._datascale / 2.0
        self.updatesamples()
        self.scaletext.text = ('Scale %.1f microvolts' % float(self._scale / float(self._datascale)))

    @gen.coroutine
    def updatesamples(self):
        
        res = {self.channellabels[i]: self._plottingdata[:,i] for i in range(self._numberOfAcquiredChannels)} 
        res['Time'] = self.xtime
        
        # distribute data for plotting
        nres = self._computedataoffset(res)
        
        self.source.data = nres
        
        # turn channel label red if bad
        for cC in range(self._numberOfAcquiredChannels):
            if self._badchannelbools[cC]:
                self.channeltext[cC].text_color='red'
            else:
                self.channeltext[cC].text_color=self.colorpalet[cC]

    def blocking_task(self):
        while True:
            
            samples = 25
            time.sleep((0.004) * samples) # do some blocking computation
            if self.deviceID is not None:
                # pull real data
                self.data = self.UnicornBlack.data
            #else:
            #    # show fake data
            #    for cS in range(samples):
            #        newdatapoints = numpy.ndarray.tolist(numpy.multiply(numpy.random.rand(self._numberOfAcquiredChannels), 100))
            #        self.data.append(newdatapoints) 
            #        self.data.pop(0)
                            
            self._plottingdata = numpy.array(self.data)
        
            # but update the document from callback
            self.doc.add_next_tick_callback(partial(self.updatesamples))
   
    