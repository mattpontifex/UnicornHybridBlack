function eegplugin_loadunicornhybridblack(fig,try_strings,catch_strings)

% create menu
toolsmenu1 = findobj(fig, 'tag', 'import data');

uimenu( toolsmenu1, 'label', 'From Unicorn Hybrid Black', 'separator','on','callback', '[EEG LASTCOM]=pop_loadunicornhybridblack;  [ALLEEG EEG CURRENTSET] = eeg_store(ALLEEG, EEG, CURRENTSET); eeglab redraw');
