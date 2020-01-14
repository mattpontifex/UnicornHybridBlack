
#https://docs.bokeh.org/en/latest/docs/user_guide/layout.html#userguide-layout

import math
import numpy
import scipy.signal
import matplotlib.mlab as mlab
from bokeh.io import output_file, show
from bokeh.layouts import row, column, widgetbox
from bokeh.plotting import curdoc, figure, ColumnDataSource
from bokeh.models.widgets import Button, Toggle
from bokeh.models.annotations import Label
from bokeh.palettes import viridis
from functools import partial
from threading import Thread
import time
from tornado import gen

# features to add
# plot spectrum instead of time - would have to be another tab with 4 x 4 grid of bar plots


class UnicornBlackFunctions():    
    """class for data visualization using the g.tec Unicorn Hybrid Black
	"""
    
    def __init__(self):
        
        self._numberOfAcquiredChannels = 8
        self._samplefreq = 250.0
        self._rollingspan = 5
        self._scale = 500
        self._datascale = 1
        self._rollingspanpoints = int(math.floor( float(self._rollingspan) * float(self._samplefreq) ))
        self._baselinerollingspan = int(self._rollingspanpoints / 10.0)
        
        self.channellabels = ['FZ', 'C3', 'CZ', 'C4', 'PZ', 'O1', 'OZ', 'O2']
        self.channellabels.reverse()
        self.data = [[0.0] * self._rollingspanpoints] * self._numberOfAcquiredChannels
        self.xlabel = 'Time'
        self.xtime = numpy.ndarray.tolist(numpy.linspace(0, self._rollingspan, self._rollingspanpoints))
        self.paletsize = int(self._numberOfAcquiredChannels*1.5)
        self.colorpalet = viridis(self.paletsize)
        self.res = None
        self.source = None
        self._filterdata = False
        self._filtersettings = [0.5, 30]
        bhp, ahp = scipy.signal.butter(2, (self._filtersettings[0] / (self._samplefreq / 2)), btype='high')
        blp, alp = scipy.signal.butter(2, (self._filtersettings[1] / (self._samplefreq / 2)))
        self._hpfiltersettings = [bhp, ahp]
        self._lpfiltersettings = [blp, alp]
        self._badchannelbools = [False] * self._numberOfAcquiredChannels
        self._power = []
        self._freqs = []

    def startvisualization(self):
        
        # add data to source
        res = {self.channellabels[i]: self.data[i] for i in range(self._numberOfAcquiredChannels)} 
        res[self.xlabel] = self.xtime
        
        # distribute data for plotting
        self.res = self._computedataoffset(res)
        self.source = ColumnDataSource(self.res)
                    
        output_file("UnicornBlackDataVisualizer.html")
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
                 plot_width=1400,         
                 title='Streaming Data',
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
           self.channeltext.append(Label(x=0, y=((cL + 1)*self._scale), x_offset=-45, x_units='data', y_units='data',text=self.channellabels[cL], text_font_size="20pt", text_color=self.colorpalet[cL], render_mode='css', background_fill_alpha=0.0, text_baseline="middle"))
           self.plots[cC].add_layout(self.channeltext[cL])
        
        self.scaletext = Label(x=(self._rollingspan + 0.05), y=5, y_offset=0, x_units='data', y_units='data',text=('Scale %.1f microvolts' % float(self._scale / float(self._datascale))), text_font_size="8pt", text_color='gray', render_mode='css', background_fill_alpha=0.0, text_baseline="middle")
        self.plots[cC].add_layout(self.scaletext)
        # This is important! Save curdoc() to make sure all threads
        # see the same document.
        self.doc = curdoc()
        
        self.doc.add_root(self.plots[0])
        
        # add a button widget and configure with the call back
        Scaleupbutton = Button(label="Scaleup")
        Scaleupbutton.on_click(self._scaleup)
        Scaledownbutton = Button(label="Scaledown")
        Scaledownbutton.on_click(self._scaledown)
        
        self.Filterdatabutton = Toggle(label="Turn on Data Filter")
        self.Filterdatabutton.on_click(self.filtertoggle_handler)
        
        self.doc.add_root(row(Scaledownbutton,Scaleupbutton,self.Filterdatabutton))
        
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
        
        if (self._filterdata):
            presource = self._computedatafilter(presource)
            
        for cC in range(self._numberOfAcquiredChannels):
            # baseline data to last points
            presource[self.channellabels[cC]] = numpy.ndarray.tolist(numpy.add(numpy.multiply(numpy.subtract(presource[self.channellabels[cC]], numpy.mean(presource[self.channellabels[cC]][-self._baselinerollingspan:])), float(self._datascale)), (cC + 1)*self._scale))
            
            
        return presource

    def _computedatafilter(self, presource):
        
        # check bad channels
        for cC in range(self._numberOfAcquiredChannels):
            self._power, self._freqs = mlab.psd(x=presource[self.channellabels[cC]], NFFT=self._scale, Fs=self._samplefreq, noverlap=int(self._rollingspanpoints/3.0), sides='onesided', scale_by_freq=True)
            
            nonnoise = numpy.mean(self._power[numpy.argmin(abs(self._freqs-(35))):numpy.argmin(abs(self._freqs-(50)))])
            noise = numpy.mean(self._power[numpy.argmin(abs(self._freqs-(55))):numpy.argmin(abs(self._freqs-(65)))])
            if ((noise / float(nonnoise)) > 1.5):
                self._badchannelbools[cC] = True
                self.channeltext[cC].text_color='red'
            else:
                self._badchannelbools[cC] = False
                self.channeltext[cC].text_color=self.colorpalet[cC]
        
            if (self._filterdata):
                tempdata = scipy.signal.filtfilt(self._hpfiltersettings[0], self._hpfiltersettings[1], presource[self.channellabels[cC]], method="gust") # High pass:
                presource[self.channellabels[cC]] = scipy.signal.filtfilt(self._lpfiltersettings[0], self._lpfiltersettings[1], tempdata, method="gust") # low pass:
            
        return presource


    def _scaleup(self):
        self._datascale = self._datascale * 2.0
        
        # but update the document from callback
        self.updatesamples()
        self._badchannelbools[3] = False
        self.scaletext.text = ('Scale %.1f microvolts' % float(self._scale / float(self._datascale)))
        
    def _scaledown(self):
        self._datascale = self._datascale / 2.0
        
        # but update the document from callback
        self.updatesamples()
        self._badchannelbools[3] = True
        self.scaletext.text = ('Scale %.1f microvolts' % float(self._scale / float(self._datascale)))

    @gen.coroutine
    def updatesamples(self):
        
        res = {self.channellabels[i]: self.data[i] for i in range(self._numberOfAcquiredChannels)} 
        res[self.xlabel] = self.xtime
        
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
            # do some blocking computation
            examplesamples = 20
            time.sleep((0.004) * examplesamples)
            for cS in range(examplesamples):
                newdatapoints = numpy.ndarray.tolist(numpy.multiply(numpy.random.rand(self._numberOfAcquiredChannels), 100))
                for cC in range(self._numberOfAcquiredChannels):
                    self.data[cC] = self.data[cC] + [newdatapoints[cC]]
                    self.data[cC].pop(0)
        
            # but update the document from callback
            self.doc.add_next_tick_callback(partial(self.updatesamples))
   
    