function [EEG, command] = loadunicornhybridblackraw(fullfilename, varargin)
%   Import an Unicorn Hybrid Black file into EEGLAB. 
%
%   Input Parameters:
%        1    Specify the filename of the file (extension should be .csv).  
%
%   Example Code:
%
%       >> EEG = pop_loadunicornhybridblack;   % an interactive uigetfile window
%       >> EEG = loadunicornhybridblack;   % an interactive uigetfile window
%       >> EEG = loadunicornhybridblack('C:\Studies\File1.csv');    % no pop-up window 
%       >> EEG = loadunicornhybridblackraw('C:\Studies\File1.csv', 'Channels', { 'EEG1', 'EEG2', 'EEG3', 'EEG4', 'EEG5', 'EEG6', 'EEG7', 'EEG8', 'ACCELEROMETERX', 'ACCELEROMETERY', 'ACCELEROMETERZ', 'GYROSCOPEX', 'GYROSCOPEY', 'GYROSCOPEZ', 'BATTERYLEVEL', 'COUNTER', 'VALIDATIONINDICATOR' });    % no pop-up window 
%
%   Author: Matthew B. Pontifex, Health Behaviors and Cognition Laboratory, Michigan State University, April 22, 2024
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
            error('loadunicornhybridblackraw(): File selection cancelled. Error thrown to avoid overwriting data in EEG.')
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
            error('Error in loadunicornhybridblackraw(): The requested filename "%s" in "%s" does not exist.', name, filepath)
        end
        
        % load header information
        delimiter = ',';
        endRow = 1;
        formatSpec = '%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%[^\n\r]';
        fileID = fopen(fullfilename,'r');
        dataArray = textscan(fileID, formatSpec, endRow, 'Delimiter', delimiter, 'TextType', 'string', 'ReturnOnError', false, 'EndOfLine', '\r\n');
        fclose(fileID);
        headerlabels = {};
        % remove spaces from labels
        for cI = 1:size(dataArray,2)
            if (any(isspace(dataArray{cI})))
                dataArray{cI} = strrep(dataArray{cI},' ','');
            end
            headerlabels{end+1} = dataArray{cI}(1);
            % swap user specified label
            try
                headerlabels{end} = r(cI).Channels;
            catch
                booler = 1;
            end
        end
        
        % load data
        samplerate = double(250.0); % unicorn currently has fixed sample rate
        
        formatSpec = '%f%f%f%f%f%f%f%f%f%f%f%f%f%f%f%f%f%[^\n\r]';
        delimiter = ',';
        startRow = 2;
        fileID = fopen(fullfilename,'r');
        dataArray = textscan(fileID, formatSpec, 'Delimiter', delimiter, 'TextType', 'string', 'EmptyValue', NaN, 'HeaderLines' ,startRow-1, 'ReturnOnError', false, 'EndOfLine', '\r\n');
        fclose(fileID);
        datain = [dataArray{1:end-1}];

        
        % Populate channel labels
        EEG.chanlocs = struct('labels', [], 'ref', [], 'theta', [], 'radius', [], 'X', [], 'Y', [], 'Z', [],'sph_theta', [], 'sph_phi', [], 'sph_radius', [], 'type', [], 'urchan', []);
        for cC = 1:((numel(headerlabels))-1)
            EEG.chanlocs(cC).labels = char(upper(headerlabels{cC})); % Convert labels to uppercase and store as character array string
            EEG.chanlocs(cC).urchan = cC;
        end
        EEG.nbchan = ((numel(headerlabels))-1);
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
        
        
        % make sure all the points are at the correct times
        samplingpoints = [datain(1,16):1:datain(end,16)];
        samplingpoints = samplingpoints - datain(1,16) + 1;
        EEG.times = samplingpoints * (1/samplerate); % change samples to time
        EEG.pnts = size(EEG.times,2);
        EEG.data = datain';
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
        
        % Put triggers in
        EEG.event = struct('type', [], 'latency', [], 'urevent', []);
        EEG.urevent = struct('type', [], 'latency', []);
        
        outstring = makecellarraystr({EEG.chanlocs.labels});
        command = sprintf('EEG = loadunicornhybridblackraw(''%s%s'', ''Channels'', %s);', filepath, [name, datafileextension], outstring);
        EEG.history = sprintf('%s\n%s;', EEG.history, command);
        
        EEG = eeg_checkset(EEG);
        EEG.history = sprintf('%s\nEEG = eeg_checkset(EEG);', EEG.history);
        
    end
end
