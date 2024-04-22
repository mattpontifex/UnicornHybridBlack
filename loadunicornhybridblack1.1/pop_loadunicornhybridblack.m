function [EEG, command] = pop_loadunicornhybridblack(fullfilename, varargin)
%   Import an Unicorn Hybrid Black Collect file into EEGLAB. 
%
%   Input Parameters:
%        1    Specify the filename of the file (extension should be .csv).  
%
%   Example Code:
%
%       >> EEG = pop_loadunicornhybridblack;   % an interactive uigetfile window
%       >> EEG = loadunicornhybridblack;   % an interactive uigetfile window
%       >> EEG = loadunicornhybridblack('C:\Studies\File1.csv');    % no pop-up window 
%
%   Author: Matthew B. Pontifex, Health Behaviors and Cognition Laboratory, Michigan State University, January 7, 2020
%
%   If there is an error with this code, please email pontifex@msu.edu with
%   the issue and I'll see what I can do.

    command = '';
    if nargin < 1 % No file was identified in the call

        [filename, filepath] = uigetfile({'*.csv' 'All data files'}, 'Choose a file -- pop_loadunicornhybridblack()'); 
        
        drawnow;
        if filename == 0 % the user aborted
            error('pop_loadunicornhybridblack(): File selection cancelled. Error thrown to avoid overwriting data in EEG.')
            
        else % The user selected something
            
            % Get filename components
            [pathstr,name,ext] = fileparts([filepath, filename]);
            fullfilename = [filepath, filename];
            file = [pathstr, filesep, name];
            
            EEG = [];
            EEG = eeg_emptyset;
            [EEG, com] = loadunicornhybridblack(fullfilename);
            
            % Show user the direct call equivalent
            command = sprintf('\nEquivalent Command:\n\t %s', com);
            disp(command)

        end

    else % file was specified in the call
        
        EEG = [];
        EEG = eeg_emptyset;
        [EEG, command] = loadunicornhybridblack(fullfilename);
    end
        
end



