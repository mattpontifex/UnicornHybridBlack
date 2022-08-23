import os, shutil
import numpy


def checkdefaultsettings(invar, settvar):
    # generic function for checking data inputs
    # first element of settvar is the default
    
    boolset = 0
    if invar == False:
        # user did not specify so use default
        invar = settvar[0]
        boolset = 1
    else:
        # user did specify so run case insensitive check
        for labs in settvar:
            if invar.lower() == labs.lower():
                invar = labs
                boolset = 1
                
        # user may have only put in part of the setting
        if boolset == 0:    
            for labs in settvar:
                if invar.lower() in labs.lower():
                    invar = labs
                    boolset = 1
                    
    # by this point if we still dont have a setting then use the default
    if boolset == 0:
        invar = settvar[0]

    return invar

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




def syncfiles(patha = [], pathb = [], file_types = [], direction = False):            
    if not file_types: # if no file types are specified
        file_types = ['.dat', '.psydat', '.ceo', '.dap', '.rs3', '.set', '.erp', '.cnt', '.csv', '.gz', '.m', '.py', '.sav', '.sps']

    direction = checkdefaultsettings(direction, ['bidirectional', 'AtoB', 'BtoA', 'Push', 'Pull'])
        
    if os.path.isdir(patha):
        if os.path.isdir(pathb):
    
            files_in_patha = [f.upper() for f in os.listdir(patha) for type_ in file_types if f.endswith(type_)]
            files_in_pathb = [f.upper() for f in os.listdir(pathb) for type_ in file_types if f.endswith(type_)]

            if (direction == 'bidirectional') or (direction == 'AtoB') or (direction == 'Push'):
                
                files_notin_pathb = numpy.unique(files_in_patha, files_in_pathb)
                if len(files_notin_pathb) > 0 and len(files_notin_pathb[0]) > 0:
                    files_notin_pathb = files_notin_pathb[0]

                for tfile in files_notin_pathb:
                    if len(tfile) > 0:
                        shutil.copyfile(patha + os.path.sep + tfile, pathb + os.path.sep + tfile)
                        if os.path.isfile(pathb + os.path.sep + tfile):
                            print('Successfully backed up: %s' % (patha + os.path.sep + tfile))
                        else:
                            print('Unable to back up: %s' % (patha + os.path.sep + tfile))
                          
            if (direction == 'bidirectional') or (direction == 'BtoA') or (direction == 'Pull'):   
                
                files_notin_patha = numpy.unique(files_in_pathb, files_in_patha)
                if len(files_notin_patha) > 0 and len(files_notin_patha[0]) > 0:
                    files_notin_patha = files_notin_patha[0]

                for tfile in files_notin_patha:
                    if len(tfile) > 0:
                        shutil.copyfile(pathb + os.path.sep + tfile, patha + os.path.sep + tfile)
                        if os.path.isfile(patha + os.path.sep + tfile):
                            print('Successfully backed up: %s' % (pathb + os.path.sep + tfile))
                        else:
                            print('Unable to back up: %s' % (pathb + os.path.sep + tfile))
                        
