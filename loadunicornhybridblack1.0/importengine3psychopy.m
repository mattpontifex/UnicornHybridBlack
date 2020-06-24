function [ EEG ] = importengine3psychopy(EEG, filin, varargin)
%   Imports behavioral data stored in a modified PsychoPy data format.
%   'Trial','Event','Duration','ISI','ITI','Type','Resp','Correct','Latency','ClockLatency','Trigger','MinRespWin','MaxRespWin','Stimulus'       
%
%   Following merging, the trial type in EEG.event is modified based on the correctness of behavioral responses.
%       Correct Trials are increased by 10,000 
%       Error of Commission Trials are increased by 50,000
%       Error of Omission Trials are increased by 60,000
%       (i.e., type 27 would become 10,027 if correct; 50,027 if an
%       incorrect response was made; and 60,027 if an incorrect
%       non-response occurred)
%
%   1   Input EEG File From EEGLAB 
%      
%   Example Code:    
%           
%   EEG = importengine3psychopy(EEG, 'File.psydat', 'Force', 'True');
%
%   Author: Matthew B. Pontifex, Health Behaviors and Cognition Laboratory, Michigan State University, October 28, 2015

    if ~isempty(varargin)
         r=struct(varargin{:});
    end
    try r.Force; catch r.Force = 'False'; end
    try, r.Skip;  skipcodes = [r.Skip];    catch, skipcodes = []; end
    try, r.Check;  validateresponses = r(1).Check;    catch, validateresponses= 'True'; end
    try, r.Debug; catch r.Debug = 'False'; end

    if ~(exist(filin, 'file') == 0) 
        fid = fopen(filin,'rt');
        if (fid ~= -1)
            cell = textscan(fid,'%s');
            fclose(fid);
            cont = cell{1};

            % Check file version
            if strcmpi(cont(1,1),'gentask.....=') % Could be Neuroscan Stim2 or modified Psychopy formats
                if strcmpi(cont(2,1),'PsychoPy_Engine_3')

                    delimiter = ' ';
                    startRow = 7;
                    endRow = inf;
                    formatSpec = '%f%s%s%s%s%s%f%s%f%f%f%s%s%s%[^\n\r]';
                    fid = fopen(filin,'r');
                    dataArray = textscan(fid, formatSpec, endRow, 'Delimiter', delimiter, 'MultipleDelimsAsOne', true, 'HeaderLines', startRow-1);
                    fclose(fid);

                    % Set as table
                    datain = table(dataArray{1:end-1}, 'VariableNames', {'Trial','Event','Duration','ISI','ITI','Type','Resp','Correct','Latency','ClockLatency','Trigger','MinRespWin','MaxRespWin','Stimulus'});

                    % Change Formats
                    datain.Duration = str2double(datain.Duration(:));
                    datain.ISI = str2double(datain.ISI(:));
                    datain.ITI = str2double(datain.ITI(:));
                    datain.Type = str2double(datain.Type(:));
                    datain.Correct = str2double(datain.Correct(:));
                    datain.MinRespWin = str2double(datain.MinRespWin(:));
                    datain.MaxRespWin = str2double(datain.MaxRespWin(:));
                    datain.ClockLatency = datain.ClockLatency*1000; % adjust from sec to ms
                    datain.ClockLatency = datain.ClockLatency-datain.ClockLatency(1); % baseline

                    % Clear any trials where a trigger was not sent
                    rC = 1;
                    while rC <= size(datain,1)
                       if (datain.Trigger(rC) == 0) || (datain.Type(rC) == 0)
                           datain(rC,:) = [];
                           rC = rC - 1;
                       end
                       rC = rC + 1;
                    end

                    if (size(datain,1) > 0)
                        if (size(EEG.event,2) == 0)
                           error('Error in importengine3psychopy(): the EEG.event structure does not contain any events.')
                        end
                        %Create Matrix of Events in EEG
                        temp = NaN(size(EEG.event,2),3);
                        for index = 1:size(EEG.event,2)
                            temp(index,1) = EEG.event(index).type;
                            temp(index,2) = index;
                            temp(index,3) = EEG.event(index).latency;
                        end
                        eegmatchmatrix = [temp(:,2),temp(:,1)];
                        
                        %Create Matrix of Events in behavioral output
                        temp = NaN(1,3); tindex = 1;
                        for index = 1:size(datain,1)
                            if (datain.Trigger(index) == 1) % if a trigger was sent
                                if isnan(datain.Type(index)) % if there is not a type code
                                    temp(tindex,1) = datain.Resp(index);
                                else
                                    temp(tindex,1) = datain.Type(index);
                                end
                                temp(tindex,2) = index;
                                temp(tindex,3) = datain.ClockLatency(index);
                                tindex = tindex + 1;
                            end
                        end
                        datmatchmatrix = [temp(:,2),temp(:,1)];
                        
                        % remove skipped event codes
                        if ~isempty(skipcodes)
                            cR = 1;
                            while (cR <= size(eegmatchmatrix,1))
                                boldel = 0;
                                for tempval2 = skipcodes
                                    if (eegmatchmatrix(cR,2) == tempval2)
                                        boldel = 1;
                                    end
                                end
                                if (boldel == 1)
                                    eegmatchmatrix(cR,:) = [];
                                    cR = cR - 1;
                                end
                                cR = cR + 1;
                            end
                            
                            cR = 1;
                            while (cR <= size(datmatchmatrix,1))
                                boldel = 0;
                                for tempval2 = skipcodes
                                    if (datmatchmatrix(cR,2) == tempval2)
                                        boldel = 1;
                                    end
                                end
                                if (boldel == 1)
                                    datmatchmatrix(cR,:) = [];
                                    cR = cR - 1;
                                end
                                cR = cR + 1;
                            end
                        end       
                        
                        % remove events that only occur in one data stream
                        commonstimcodes = intersect(eegmatchmatrix(:,2),datmatchmatrix(:,2));
                        eegmatchmatrix(~ismember(eegmatchmatrix(:,2),commonstimcodes),2) = 0;
                        datmatchmatrix(~ismember(datmatchmatrix(:,2),commonstimcodes),2) = 0;
                        
                        % attempt to align samples
                        cRdat = 1;
                        cReeg = 1;
                        matchSearch = 1;
                        alignmatrixindices = NaN(1,4);
                        while (matchSearch > 0)
                            if (datmatchmatrix(cRdat,2) == eegmatchmatrix(cReeg,2)) % if the current lines match 
                                alignmatrixindices(matchSearch,1) = eegmatchmatrix(cReeg,1);
                                alignmatrixindices(matchSearch,2) = eegmatchmatrix(cReeg,2);
                                alignmatrixindices(matchSearch,3) = datmatchmatrix(cRdat,1);
                                alignmatrixindices(matchSearch,4) = datmatchmatrix(cRdat,2);
                                cRdat = cRdat + 1; cReeg = cReeg + 1; matchSearch = matchSearch + 1;
                            else % current lines do not match
                                boolerr = 0;
                                linestart = cRdat + cReeg;
                                try
                                    if (datmatchmatrix(cRdat+1,2) == eegmatchmatrix(cReeg,2)) % Check to see if the event is missing in the DAT data
                                        cRdat = cRdat + 1; 
                                    elseif (datmatchmatrix(cRdat,2) == eegmatchmatrix(cReeg+1,2)) % Check to see if the event is missing in the EEG data
                                        cReeg = cReeg + 1;
                                    elseif (datmatchmatrix(cRdat+2,2) == eegmatchmatrix(cReeg,2)) % Check to see if more than one event is missing in the DAT data
                                        cRdat = cRdat + 2; 
                                    elseif (datmatchmatrix(cRdat,2) == eegmatchmatrix(cReeg+2,2)) % Check to see if more than one event is missing in the EEG data
                                        cReeg = cReeg + 2;
                                    end
                                catch
                                    boolerr = 1;
                                end
                                lineend = cRdat + cReeg;
                                if (linestart == lineend) %nothing was found or an error happened
                                    cRdat = cRdat + 1; cReeg = cReeg + 1; 
                                end
                            end
                            % Check to see if we are out of samples to check
                            if (cRdat > size(datmatchmatrix,1)) | (cReeg > size(eegmatchmatrix,1))
                                matchSearch = 0;
                            end
                        end
                        boolerr = 0;
                        if (boolerr == 0)

                            % store original in case the data do not match
                            ORIGEEG = EEG; ORIGEEG.event = EEG.event; 

                            if (strcmpi(r.Debug, 'True'))
                               boolerr = 1; 
                            end
                            
                            
                            % Load data into EEG.event structure
                            for rC = 1:size(alignmatrixindices,1)
                                eVntInd = alignmatrixindices(rC,1);
                                dVntInd = alignmatrixindices(rC,3);
                                EEG.event(eVntInd).stimorder = datain.Trial(dVntInd);
                                EEG.event(eVntInd).stimresp = datain.Event(dVntInd);
                                EEG.event(eVntInd).masterclocklatency = datain.ClockLatency(dVntInd);
                                if (strcmpi(datain.Event(dVntInd),'Stimulus'))
                                    EEG.event(eVntInd).respcode = datain.Resp(dVntInd);
                                    EEG.event(eVntInd).respcorr = datain.Correct(dVntInd);
                                    EEG.event(eVntInd).resplatency = datain.Latency(dVntInd);
                                    EEG.event(eVntInd).stimduration = datain.Duration(dVntInd);
                                    EEG.event(eVntInd).isi = datain.ISI(dVntInd);
                                    EEG.event(eVntInd).iti = datain.ITI(dVntInd);
                                    EEG.event(eVntInd).minrespwin = datain.MinRespWin(dVntInd);
                                    EEG.event(eVntInd).maxrespwin = datain.MaxRespWin(dVntInd);
                                    EEG.event(eVntInd).stimulus = datain.Stimulus(dVntInd);
                                end
                                if (alignmatrixindices(rC,2) == 0)
                                    EEG.event(eVntInd).type = alignmatrixindices(rC,4);
                                end
                            end

                            % Verify that the Stimuli and Responses match
                            samprate = (1/EEG.srate)*1000;
                            is = zeros(1,5);
                            isthres = 25;
                            hitthres = 33; % 2 frames (16.7) difference between response and response trigger
                            for rC = 1:size(EEG.event,2)
                                tindex = 1;
                                if strcmpi(EEG.event(rC).stimresp, 'Stimulus')
                                    if (EEG.event(rC).respcode > 0)
                                        if (rC+1 <= size(EEG.event,2))
                                            if ~strcmpi(EEG.event(rC+1).stimresp, 'Stimulus')
                                                if (EEG.event(rC+1).type == EEG.event(rC).respcode)
                                                    tempa = (EEG.event(rC+1).latency - EEG.event(rC).latency)*samprate;
                                                    EEG.event(rC).('offby') = (tempa-EEG.event(rC).resplatency); 
                                                    if (abs(tempa-EEG.event(rC).resplatency) > hitthres)
                                                        if ~(EEG.event(rC).respcorr < 0)
                                                            is(1) = is(1) + 1; %difference between response event and when the stimulus says the response occured is outside of the specified latency threshold
                                                        end
                                                    end
                                                else
                                                    is(2) = is(2) + 1; %stimulus says there was a response, but the response events recorded do not match
                                                end
                                            else
                                                if ~(EEG.event(rC).respcorr < 0)
                                                    is(3) = is(3) + 1; %stimulus says there was a response but no response event was recorded in EEG data
                                                end
                                            end
                                        else
                                            is(3) = is(3) + 1; %stimulus says there was a response but no response event was recorded in EEG data
                                        end
                                    else
                                        if ((rC+1) < size(EEG.event,2))
                                            if strcmpi(EEG.event(rC+1).stimresp, 'Response')
                                                is(4) = is(4) + 1; %stimulus says there was not a response but a response event was recorded in EEG data
                                            end
                                        end
                                    end
                                end
                            end

                            % Check clock drift
                            hitthres = 30; % 10ms drift
                            temp = find(strcmpi([EEG.event.stimresp],'Stimulus'));
                            for rC = 2:size(temp,2)
                                if (strcmpi(EEG.event(temp(rC-1)).stimresp, 'Stimulus'))
                                    if (strcmpi(EEG.event(temp(rC)).stimresp, 'Stimulus'))
                                        markgap = (EEG.event(temp(rC)).latency-EEG.event(temp(rC-1)).latency)*samprate;
                                        stimgap = round(EEG.event(temp(rC)).masterclocklatency - EEG.event(temp(rC-1)).masterclocklatency,0);
                                        EEG.event(temp(rC)).('clockoffby') = markgap-stimgap;
                                        if (abs(markgap-stimgap) > hitthres)
                                            is(5) = is(5) + 1; %The latency between stimuli does not match between the events and the stimuli clock.
                                        end
                                    end
                                end
                            end

                            if (sum(is) > isthres)
                                fprintf('\nWarning - Response Events do not match up with when they are reported to occur in the DAT file.\n');
                                if (is(1) > 0)
                                    fprintf('%d events have a difference between response event and when the stimulus says the response occured outside of the specified latency threshold.\n', is(1));
                                end
                                if (is(2) > 0)
                                    fprintf('%d events have stimuli that say there was a response, but the response events recorded do not match.\n', is(2));
                                end
                                if (is(3) > 0)
                                    fprintf('%d events have stimuli that say there was a response but no response event was recorded in EEG data.\n', is(3));
                                end
                                if (is(4) > 0)
                                    fprintf('%d events have stimuli that say there was not a response but a response event was recorded in EEG data.\n', is(4));
                                end
                                if (is(5) > 0)
                                    fprintf('%d events have stimuli latencies that do not match between the events and the stimuli clock.\n', is(5));
                                end
                                if strcmpi(r.Force,'False')
                                    EEG = ORIGEEG;
                                    error('Please make sure that the correct DAT file is being specified and that this sequence of trials was not re-run with the EEG and PSYDAT files under different filenames.')
                                end
                            end
                            boolerr = 0;
                            if strcmpi(r.Force,'False')
                                if (sum(is) > isthres)
                                    boolerr = 1;
                                end
                            end
                            if (boolerr == 0)

                                if strcmpi(r.Force,'False')
                                    % Correct response markers by stimulus offset
                                    rEnd = size(EEG.event,2);
                                    for rC = 1:rEnd-1
                                        if (strcmpi(EEG.event(rC).stimresp, 'Stimulus'))
                                           if (strcmpi(EEG.event(rC+1).stimresp, 'Response'))
                                               if (EEG.event(rC+1).type == EEG.event(rC).respcode)
                                                   if (EEG.event(rC).offby == (((EEG.event(rC+1).latency - EEG.event(rC).latency)*samprate)-EEG.event(rC).resplatency))
                                                       newlat = EEG.event(rC).latency + round((EEG.event(rC).resplatency/samprate));
                                                       % Find next available latency (in case there is a conflict)
                                                       offset = 0;
                                                       termlimit = 500;
                                                       while ~isempty(find([EEG.event.latency] == newlat,1))
                                                          offset = offset + 1;
                                                          if (offset > termlimit)
                                                              break
                                                          end
                                                       end
                                                       newlat = newlat + offset;
                                                       EEG.event(rC+1).latency = newlat;
                                                       EEG.event(rC).offby = (((EEG.event(rC+1).latency - EEG.event(rC).latency)*samprate)-EEG.event(rC).resplatency);                               
                                                   end
                                               end
                                           end
                                        end
                                    end
                                end
                                %try
                                %    EEG.event = rmfield(EEG.event, 'clockoffby');
                                %    EEG.event = rmfield(EEG.event, 'offby');
                                %catch
                                %    errbol = 1;
                                %end

                                % Recode Trial Types Based Upon Performance
                                rEnd = size(EEG.event, 2);
                                for r = 1:rEnd
                                    if (strcmpi(EEG.event(r).stimresp, 'Stimulus')) % Recode Stimulus Related 
                                        if (EEG.event(r).('respcorr') == 1) %Correct Trials
                                            EEG.event(r).('type') = EEG.event(r).('type') + 10000;
                                        else
                                             if ~isempty(EEG.event(r).('respcode'))
                                                 if ~isnan(EEG.event(r).('respcode')) % Errors of Commission
                                                        EEG.event(r).('type') = EEG.event(r).('type') + 50000;
                                                 else % Errors of Omission
                                                        EEG.event(r).('type') = EEG.event(r).('type') + 60000;
                                                 end
                                             end
                                        end
                                    end
                                end

                            end
                        end
                    end
                end
            end
        end
    end
end