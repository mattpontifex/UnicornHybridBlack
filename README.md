UnicornHybridBlack
==============

A set of EEGLAB and Python functions to interact with the g.tec Unicorn Hybrid Black (https://www.unicorn-bi.com/) 8 channel wireless EEG device.  You 
can load the python functions using:

    import unicornhybridblack

UnicornBlackProcess provides the ability to run the device using multiprocessing so that it can run in the background collecting data. 

    UnicornBlack = unicornhybridblack.UnicornBlackProcess() 

UnicornBlackThreads provides direct access to the thread functions.
  
    UnicornBlack = unicornhybridblack.UnicornBlackThreads() 

UnicornBlackCheckSignal provides a class to evaluate signal quality based upon the variability of the signal and the ratio of frequency power in a noise
band relative to a control band.
  
    UnicornBlack = unicornhybridblack.UnicornBlackCheckSignal()


Package Contents
------------
This repo provides the Python module for interacting with the Unicorn Hybrid Black that outputs EEG data into a .CSV file and event markers into a 
.CSVE (comma seperated file format) file. This repo also provides an EEGLAB plugin (loadunicornhybridblack#.#) that enables reading the data into MATLAB.

PythonCollect is setup to run a psychopy (https://www.psychopy.org/) instance (version 3.0 or higher) that will prompt for a filename, show instructions,
connect to the Unicorn Hybrid Black, run a task based upon a sequence file, and output both EEG and behavioral data. An example task implementation is provided. Gentask provides the control files that specify task parameters. Sequence provides the .csv files that specify stimuli files, durations, and marker codes. Stimuli is where the stimuli file are stored. Raw is where the data will be stored.

Installation
------------
To use these functions, click the "Clone or download" button on the right and then select "Download ZIP".
Once the file has downloaded, unzip the package and then copy the loadunicornhybridblack.X file into the EEGLAB plugins
folder.

You will still need to have the python API (https://www.unicorn-bi.com/product/unicorn-python-api-hybrid-black/). The .PYD and .dll files from the API should be copied and placed into the PythonCollect -> Gentask -> Engine folder.

Execution
------------
It is suggested that you use Anaconda Spyder 3 with python 3.0 or higher. Spyder however does not play nicely with multiprocessing, so you should change the settings to have Spyder run the task in an external system terminal. 
Select Run -> Configuration per file...   
Change the Console to Execute in an external system terminal  
Select the checkbox for External system terminal Interact with the Python console after execution  

Then you can click the Run file button in Spyder on the PythonCollect -> Gentask -> ExampleTask.py file.
