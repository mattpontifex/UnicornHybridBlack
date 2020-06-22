import numpy
import matplotlib
from psychopy import visual, core, event
import unicornhybridblack as unicornhybridblack
import time


class checksignal():
    
    def __init__(self):

        self.windowsize = (1400,900)
        self.channellabels = ['FZ', 'C3', 'CZ', 'C4', 'PZ', 'O1', 'OZ', 'O2']

        # setup colormaps
        self.cmap = matplotlib.cm.get_cmap('plasma')
        self.norm = matplotlib.colors.Normalize(vmin=500, vmax=4000.0)
        
        self.winwidth = ((self.windowsize[0] / 3.0) * (1/self.windowsize[0]))
        self.winheight = ((self.windowsize[1] / 1.5) * (1/self.windowsize[0]))
        
        self.lowpassfilter = 20.0
        self.highpassfilter = 0.1
        self.controlband = [20, 40] # hz
        self.noiseband = [58, 62] # hz
        self.unicorn = 'UN-2019.05.51' 


    def start(self):
        
        if (len(self.unicorn) > 0):
            
            participantwin = visual.Window(size = self.windowsize, fullscr = False, screen = 0, allowGUI = False, allowStencil = False, monitor = 'testMonitor', color = '#000000', colorSpace = 'rgb')
                                 
            winblocks = [visual.Rect(participantwin, width = self.winwidth, height = self.winheight, pos = [0,0], fillColor='#FFFFFF', lineColor='#000000', autoLog=False, autoDraw=True) for cC in range(len(self.channellabels))]
            wintext = [visual.TextStim(participantwin, text='', pos=(0,0), color='#000000', height=0.15, antialias=True, bold=True, italic=False, autoLog=None) for cC in range(len(self.channellabels))]          
            winvariabilitytext = [visual.TextStim(participantwin, text='10.0', pos=(0,0), color='#000000', height=0.04, antialias=True, bold=True, italic=False, autoLog=None) for cC in range(len(self.channellabels))]          
                                       
            powertext = visual.TextStim(participantwin, text='-%', pos=(1.87,-0.95), color='#0dbd00', height=0.05, antialias=True, bold=True, italic=False, autoLog=None)          
            powertext.setAutoDraw(True)     
            
            statustext = visual.TextStim(participantwin, text='connecting', pos=(0.05,-0.95), color='#FFFFFF', height=0.03, antialias=True, bold=True, italic=False, autoLog=None)          
            statustext.setAutoDraw(True)     
                                
            calibpointsx = [-0.75, -0.25, 0.25, 0.75, -0.75, -0.25, 0.25, 0.75]
            calibpointsy = [0.5, 0.5, 0.5, 0.5, -0.5, -0.5, -0.5, -0.5]
            calibpointsxt = [0.13, 0.67, 1.13, 1.67, 0.13, 0.67, 1.13, 1.67]
            for cC in range(len(self.channellabels)):
                winblocks[cC].setPos([calibpointsx[cC],calibpointsy[cC]])
                wintext[cC].setAutoDraw(True)
                wintext[cC].setPos((calibpointsxt[cC],calibpointsy[cC])) 
                wintext[cC].setText(self.channellabels[cC])  
                winvariabilitytext[cC].setAutoDraw(True)
                winvariabilitytext[cC].setPos((calibpointsxt[cC]+0.15,calibpointsy[cC]-0.18))  
                newcolor = matplotlib.colors.to_hex(self.cmap(5.0), keep_alpha=False)
                winblocks[cC].setFillColor(newcolor)
                                           
            participantwin.flip()   
    
            # Connect to device
            UnicornBlack = unicornhybridblack.UnicornBlackProcess()   
            UnicornBlack.connect(deviceID='UN-2019.05.51', rollingspan=2.0)
            
            # wait up to 3 seconds for connection
            continueExperiment = False
            checktimer = core.CountdownTimer(start=3.0)
            while not continueExperiment:
                if UnicornBlack.ready:
                    continueExperiment = True
                if (checktimer.getTime() <= 0):
                    continueExperiment = True
            
            # prep data checks
            datacheck = unicornhybridblack.UnicornBlackCheckSignal()
            datacheck.controlband = self.controlband # hz
            datacheck.noiseband = self.noiseband # hz
            datacheck.highpassfilter = self.highpassfilter # hz
            datacheck.lowpassfilter = self.lowpassfilter # hz
                    
            _plottingdata = numpy.array(UnicornBlack.sample_data(), copy=True)
            powerlevel = 0
            try:
                powerlevel = int(_plottingdata[-1,-3]) # update power level
            except:
                continueExperiment = False
                print('The Unicorn is out of battery charge.')
            print('Battery is at %d percent.' % powerlevel) 
            
            overallTime = core.Clock(); 
            overallTime.reset() 
            event.BuilderKeyResponse()
            event.clearEvents()    
            
            while continueExperiment:     
                statustext.setText('sampling data... (press Q or ESC to quit)')
                powertext.setText('%d%%' % powerlevel)  # update power level
                _plottingdata = numpy.array(UnicornBlack.sample_data(), copy=True)
                 
                datacheck.data = _plottingdata
                datacheck.check()
                
                for cP in range(len(self.channellabels)):
                    if not continueExperiment:
                        break
                    
                    if continueExperiment:
                        if event.getKeys(["escape", "q"]): # Check for kill keys
                            continueExperiment = False
                            statustext.setText('shutting down...')
                            participantwin.flip() 
                            break
                            break          
                    
                        if (overallTime.getTime() > 120.0):
                            continueExperiment = False
                            statustext.setText('shutting down...')
                            participantwin.flip() 
                            break 
                            break      
                        
                        if continueExperiment:
                            
                            freqrat = numpy.divide(datacheck.freqratio[cP],1000)
                            if (freqrat > 999.9):
                                freqrat = 999.9
                            
                            winvariabilitytext[cP].setText('%0.1f' % freqrat) 
                            pstd = self.norm(datacheck.pointstd[cP])
                            newcolor = matplotlib.colors.to_hex(self.cmap(pstd), keep_alpha=False)
                            winblocks[cP].setFillColor(newcolor)
                            if (pstd > 0.5):
                                winvariabilitytext[cP].setColor('#000000')
                            else:
                                winvariabilitytext[cP].setColor('#FFFFFF')
                            
                
                participantwin.flip() 
                time.sleep(0.25)

            participantwin.close()
            
            # stop recording
            UnicornBlack.disconnect()
     
# # # # #
# DEBUG #
if __name__ == "__main__":
    
    #from checksignal import checksignal
    
    task = checksignal()
    task.channellabels = ['FCZ', 'C3', 'CZ', 'C4', 'PZ', 'O1', 'OZ', 'O2']
    task.unicorn = 'UN-2019.05.51' 
    
    task.start()
    