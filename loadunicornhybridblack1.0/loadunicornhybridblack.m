function [EEG, command] = loadunicornhybridblack(fullfilename, varargin)
%   Import an Unicorn Hybrid Black Collect file into EEGLAB. 
%
%   If a psydat file is availble to merge, the trial type in EEG.event is 
%   modified based on the correctness of behavioral responses.
%       Correct Trials are increased by 10,000 
%       Error of Commission Trials are increased by 50,000
%       Error of Omission Trials are increased by 60,000
%       (i.e., type 27 would become 10,027 if correct; 50,027 if an
%       incorrect response was made; and 60,027 if an incorrect
%       non-response occurred)
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
        try
            % flip to pop_loadcurry()
            [EEG, command] = pop_loadunicornhybridblack();
        catch
            % only error that should occur is user cancelling prompt
            error('loadunicornhybridblack(): File selection cancelled. Error thrown to avoid overwriting data in EEG.')
        end
    else
        
        if ~isempty(varargin)
             r=struct(varargin{:});
        end

        EEG = [];
        EEG = eeg_emptyset;
        [pathstr,name,ext] = fileparts(fullfilename);
        filename = [name,ext];
        filepath = [pathstr, filesep];
        file = [pathstr, filesep, name];

        if (exist([file '.csv'], 'file') == 0)
            error('Error in loadunicornhybridblack(): The requested filename "%s" in "%s" does not exist.', name, filepath)
        end
        
        % load header information
        delimiter = ',';
        endRow = 6;
        formatSpec = '%s%*s%*s%*s%*s%*s%*s%*s%*s%*s%*s%*s%*s%*s%*s%*s%[^\n\r]';
        fileID = fopen(fullfilename,'r');
        dataArray = textscan(fileID, formatSpec, endRow, 'Delimiter', delimiter, 'TextType', 'string', 'ReturnOnError', false, 'EndOfLine', '\r\n');
        headerin = [dataArray{1:end-1}];
        nbchan = 0;
        samplerate = 0;
        for indxi = 1:size(headerin,1)
            newStr = split(headerin(indxi,1),'= ');
            headerin(indxi,1) = newStr(1);
            headerin(indxi,2) = newStr(2);
            temp = char(newStr(1));
            if strcmpi(temp(1:8), 'channels')
                nbchan = str2double(newStr(2));
            end
            temp = char(newStr(1));
            if strcmpi(temp(1:10), 'samplerate')
                samplerate = str2double(newStr(2));
            end
        end
        
        % load data headers
        fileID = fopen(fullfilename,'r');
        delimiter = ',';
        startRow = 7;
        endRow = 7;
        formatSpec = '%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%[^\n\r]';
        dataArray = textscan(fileID, formatSpec, endRow-startRow+1, 'Delimiter', delimiter, 'TextType', 'string', 'HeaderLines', startRow-1, 'ReturnOnError', false, 'EndOfLine', '\r\n');
        labels = [dataArray{1:end-2}];
        fclose(fileID);
        
        % Populate channel labels
        EEG.chanlocs = struct('labels', [], 'ref', [], 'theta', [], 'radius', [], 'X', [], 'Y', [], 'Z', [],'sph_theta', [], 'sph_phi', [], 'sph_radius', [], 'type', [], 'urchan', []);
        for cC = 1:(numel(labels))
            EEG.chanlocs(cC).labels = char(upper(labels(cC))); % Convert labels to uppercase and store as character array string
            EEG.chanlocs(cC).urchan = cC;
        end
        EEG.nbchan = nbchan-1;
        EEG.setname = name;
        datafileextension = '.csv';
        EEG.filename = [name, datafileextension];
        EEG.filepath = filepath;
        EEG.comments = sprintf('Original file: %s%s', filepath, [name, datafileextension]);
        EEG.ref = 'Common';
        EEG.trials = 1;
        EEG.srate = samplerate;
        EEG.urchanlocs = [];
        EEG.chaninfo.plotrad = [];
        EEG.chaninfo.shrink = [];
        EEG.chaninfo.nosedir = '+X';
        EEG.chaninfo.nodatchans = [];
        EEG.chaninfo.icachansind = [];
        
        % load data
        fileID = fopen(fullfilename,'r');
        delimiter = ',';
        startRow = 8;
        formatSpec = '%f%f%f%f%f%f%f%f%f%f%f%f%f%f%f%f%[^\n\r]';
        dataArray = textscan(fileID, formatSpec, 'Delimiter', delimiter, 'TextType', 'string', 'EmptyValue', NaN, 'HeaderLines' ,startRow-1, 'ReturnOnError', false, 'EndOfLine', '\r\n');
        datain = [dataArray{1:end-1}];
        fclose(fileID);
        
        % make sure all the points are at the correct times
        samplingpoints = [datain(2,end):1:datain(end-1,end)];
        EEG.times = samplingpoints * (1/samplerate); % change samples to time
        EEG.pnts = size(EEG.times,2);
        EEG.data = NaN(EEG.nbchan, EEG.pnts);
        for indxi = 1:size(datain,1)
            currentsample = datain(indxi,end);
            if (currentsample > 0)
                [~, eventtime] = min(abs(samplingpoints - (currentsample)));
                EEG.data(:,eventtime) = datain(indxi,1:end-1)';
            end
        end
        datacheck = sum(isnan(EEG.data(1,:)));
        if (datacheck > 2)
            fprintf("Warning: A total of %d out of %d (%.1f%%) sampling points were dropped during collection", datacheck, EEG.pnts, (datacheck/EEG.pnts)*100)
        end
        EEG.xmin = EEG.times(1);
        EEG.xmax = EEG.times(end);
        
        % Use default channel locations
        try
            tempEEG = EEG; % for dipfitdefs
            dipfitdefs;
            tmpp = which('eeglab.m');
            tmpp = fullfile(fileparts(tmpp), 'functions', 'resources', 'Standard-10-5-Cap385_witheog.elp');
            userdatatmp = { template_models(1).chanfile template_models(2).chanfile  tmpp };
            try
                [T, tempEEG] = evalc('pop_chanedit(tempEEG, ''lookup'', userdatatmp{1})');
            catch
                try
                    [T, tempEEG] = evalc('pop_chanedit(tempEEG, ''lookup'', userdatatmp{3})');
                catch
                    booler = 1;
                end
            end
            EEG.chanlocs = tempEEG.chanlocs;
        catch
            booler = 1;
        end
        EEG.history = sprintf('%s\nEEG = loadunicornhybridblack(''%s%s'');', EEG.history, filepath, [name, datafileextension]);
        
        % The Gain appears to be at 250 rather than 500
        EEG.data = EEG.data * 2; % double the gain
        
        % Put triggers in
        EEG.event = struct('type', [], 'latency', [], 'urevent', []);
        EEG.urevent = struct('type', [], 'latency', []);
        
        % see if there are events available
        if ~(exist([file '.csve'], 'file') == 0)
        
            % load data headers
            fileID = fopen([file '.csve'],'r');
            delimiter = ',';
            startRow = 5;
            endRow = 5;
            formatSpec = '%s%s%[^\n\r]';
            dataArray = textscan(fileID, formatSpec, 'Delimiter', delimiter, 'TextType', 'string', 'HeaderLines' ,startRow-1, 'ReturnOnError', false, 'EndOfLine', '\r\n');
            Latency = dataArray{:, 1};
            Event = dataArray{:, 2};
            fclose(fileID);
            
            
            for indxi = 1:size(Latency,1)
                EEG.event(indxi).urevent = indxi;
                EEG.event(indxi).type = str2double(Event(indxi,1));
                EEG.urevent(indxi).type = str2double(Event(indxi,1));
                
                currentsample = str2double(Latency(indxi,1));
                [~, eventtime] = min(abs(samplingpoints - (currentsample)));
                
                EEG.event(indxi).latency = double(eventtime);
                EEG.urevent(indxi).latency = double(eventtime);
            end
            
        end
        
        % Check to See if Behavioral Data is Available
        % Check for PsychoPy .PSYDAT file
        % 'Trial','Event','Duration','ISI','ITI','Type','Resp','Correct','Latency','ClockLatency','Trigger','MinRespWin','MaxRespWin','Stimulus'
        try
            AltFile = [pathstr, filesep, name, '.psydat'];
            if ~(exist(AltFile, 'file') == 0) 

                fid = fopen(AltFile,'rt');
                if (fid ~= -1)
                    cell = textscan(fid,'%s');
                    fclose(fid);
                    cont = cell{1};

                    % Check file version
                    if strcmpi(cont(1,1),'gentask.....=') % Could be Neuroscan Stim2 or modified Psychopy formats
                        if strcmpi(cont(2,1),'PsychoPy_Engine_3')
                            EEG = importengine3psychopy(EEG, AltFile, 'Threshold', (16.67 * 4));
                        end
                    end
                end
            end
        catch
            boolerr = 1;
        end
        
        EEG = eeg_checkset(EEG);
        EEG.history = sprintf('%s\nEEG = eeg_checkset(EEG);', EEG.history);
        
        
    end
end
