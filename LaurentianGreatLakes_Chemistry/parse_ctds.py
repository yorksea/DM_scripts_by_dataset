import os,re
from dataset_tools import Line,utils

#--------------------------------------------------------------------

folders = ['IRONMAN','NILSS']

        
for folder in folders:
    print "Folder: "+folder

    #setup directory structure if doesn't exist already (it checks)
    dataDirs = utils.setupDirs('../'+folder)# a dictionary of paths          
    

    utils.XLS2CSV_byFolder(dataDirs['orig'],dataDirs['raw'],folder);    
        
    #working with just the csvs -----raw to clean------------        
   # rawfiles = os.listdir(dataDirs['rawAsciiDir'])
   # for rawfile in rawfiles:
   #   print rawfile


print "Done!"
    