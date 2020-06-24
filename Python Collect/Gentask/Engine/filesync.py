import os, shutil

def pushfiles(inpath = [], outpath = [], file_types = []):
    # Example Code:
    # pushfiles(inpath = 'S:\Data\Raw', outpath = 'R:\Data\Raw', file_types = ['.dat', '.psydat', '.ceo', '.dap', '.rs3', '.set', '.erp', '.cnt', '.csv', '.gz', '.m', '.py', '.sav', '.sps'])
    
    inpath = inpath.encode('string-escape')
    outpath = outpath.encode('string-escape')
    if os.path.isdir(outpath):
        if os.path.isdir(inpath):
            if not file_types: # if no file types are specified
                file_types = ['.dat', '.psydat', '.ceo', '.dap', '.rs3', '.set', '.erp', '.cnt', '.csv', '.gz', '.m', '.py', '.sav', '.sps']
                
            print('\n')
            files_on_output_computer = [f.lower() for f in os.listdir(outpath) for type_ in file_types if f.endswith(type_)]
            files_on_input_computer = [f for f in os.listdir(inpath) for type_ in file_types if f.endswith(type_)]
            for tfile in [f for f in files_on_input_computer if files_on_output_computer.count(f.lower()) == 0]:
                shutil.copyfile(inpath + os.path.sep + tfile, outpath + os.path.sep + tfile)
                if os.path.isfile(outpath + os.path.sep + tfile):
                    print('Successfully backed up: %s' % (inpath + os.path.sep + tfile))
                else:
                    print('Unable to back up: %s' % (inpath + os.path.sep + tfile))
