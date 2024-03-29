UnicornHybridBlack
==============

A set of EEGLAB and Python functions to interact with the g.tec Unicorn Hybrid Black (https://www.unicorn-bi.com/) 
8 channel wireless EEG device.  

<p align="center"><img src="/screencaps/UnicornBanner.png?raw=true" width="500" alt="banner Unicorn"></p>

It is suggested that you use Anaconda Spyder 3 with python 3.0 or higher. Spyder however does not play nicely with
multiprocessing, so you should change the settings to have Spyder run the task in an external system terminal.   
-Select Run -> Configuration per file...   
-Change the Console to Execute in an external system terminal  
-Select the checkbox for External system terminal Interact with the Python console after execution  

Alternatively, if Anaconda is available as an Environmental Variable then it is possible to run the python collect
package by clicking on the run me batch file.
-Open system settings, search: Environmental Variables   
-Select Edit the system environmental variables  
-Select Environmental Variables  
-Click on Path, Click on Edit, Click New  
-Add:  
-C:\ProgramData\Anaconda3\Library\bin\conda.bat  
-C:\ProgramData\Anaconda3\Scripts\conda.exe  
-C:\ProgramData\Anaconda3\condabin\conda.bat  
-Open the command prompt and run conda activate. If no errors pop up then the paths were added correctly.  
-Open up Anaconda Prompt and run as administrator, then run the following commands:  
-pip install PeakUtils  
-pip install lmfit  
-pip install psychopy==2021.2.3  
-pip install alive-progress  


Device access in Python
------------

This repo provides the Python module for interacting with the Unicorn Hybrid Black. This file is located within:

'Python Collect' -> 'Gentask' -> 'Engine' and is labeled 'unicornhybridblack.py'.  

You can load the python functions using:

    import unicornhybridblack

UnicornBlackProcess provides the ability to run the device using multiprocessing so that it can run in the 
background collecting data. 

    UnicornBlack = unicornhybridblack.UnicornBlackProcess() 
    UnicornBlack.connect(deviceID='UN-20XX.0X.XX', rollingspan=3.0, logfilename='default')
    print('Battery: %0.1f%%' % UnicornBlack.check_battery())
    UnicornBlack.startrecording()
    UnicornBlack.mark_event(5) 
    UnicornBlack.disconnect()
    

UnicornBlackThreads provides direct access to the thread and retains the same core commands.
  
    UnicornBlack = unicornhybridblack.UnicornBlackThreads()
    UnicornBlack.connect(deviceID='UN-20XX.0X.XX', rollingspan=3.0, logfilename='default')
    print('Battery: %0.1f%%' % UnicornBlack.check_battery())
    UnicornBlack.startrecording()
    UnicornBlack.mark_event(5)
    UnicornBlack.disconnect()


Data read in
------------
The unicornhybridblack python module will save EEG data into a .CSV file and event markers into a .CSVE 
(comma seperated file format) file. These files are human readable with a simple header to facilitate 
data read in. However, for convenience, loadunicornhybridblackX.X is an EEGLAB plugin that enables reading
the data into EEGLAB in MATLAB.


Data Viewer
------------
To facilitate real time visualization of the EEG data, the unicornhybridblackviewer python module provides
a matplotlib app. This app plots both time-series and frequency spectrum data from each channel. The
color of the channel label will change based upon the signal quality evaluated based upon the variability
of the signal. This file is located within:

'Python Collect' -> 'Gentask' -> 'Engine' and is labeled 'unicornhybridblackviewer.py'.  

<p align="center"><img src="/screencaps/screencap_UnicornViewer.png?raw=true" width="900" alt="screencap Unicorn Viewer"></p>

Psychopy integration
------------
PythonCollect is setup to run a psychopy (https://www.psychopy.org/) instance (version 3.0 or higher) that
will prompt for a filename, show instructions, connect to the Unicorn Hybrid Black, run a task based upon
a sequence file, and output both EEG and behavioral data. An example task implementation is provided.    
-Gentask provides the control files that specify task parameters.   
-Sequence provides the .csv files that specify stimuli files, durations, and marker codes.   
-Stimuli is where the stimuli file are stored.   
-Raw is where the data will be stored.  

Once you select the Gentask file you wish to run, you can click the Run file button in Spyder to begin the task.


Installation
------------
To use these functions, click the "Clone or download" button on the right and then select "Download ZIP".
Once the file has downloaded, unzip the package and then copy the loadunicornhybridblack.X file into the EEGLAB plugins
folder.

You will still need to have the python API (https://www.unicorn-bi.com/product/unicorn-python-api-hybrid-black/). The .PYD and .dll files from the API should be copied and placed into the PythonCollect -> Gentask -> Engine folder.
