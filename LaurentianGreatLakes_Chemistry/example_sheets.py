import os,re
from sys import platform as _platform
import pandas as pd
from dataset_tools import Line,utils
import time
 
## date and time representation
nowDate =time.strftime("%d %b %Y") #19 Aug 2016
print(nowDate)
#--------------------------------------------------------------------

cruises = ('IRONMAN','NILSS')

header_list =('CruiseID','Station','Date','Time','Lat','Lon','press','temp','cond','cond_spec','beam_trans','fluor','O2_mg_L','pH','PAR','flag');
header = ','.join(header_list);

for cruise in cruises:
    print cruise
    dataDirs = utils.setupDirs('../'+cruise+'/intermediate_files',)# a dictionary of paths
    
    PIname = ('Robert','Sterner');
    
    fileComment = "# "+cruise+" CTD Profiles\n#    P.I. "+PIname[0]+' '+PIname[1]+"\n#    Version "+nowDate
    
 #   Station[width=14]    Cast    Date____    Time__    Lat______    Lon_______    >
#prDM[width=12]    t090[width=12]    c0[width=12]    specc[width=12]    xmiss[width=12]    wetStar[width=12]    dz_dt[width=12]    ph[width=12]    par[width=12]    spar[width=12]    sal00[width=12]    sbeox0_Mm[width=12]    sbeox0_Mg[width=12]    sbeox0_PS[width=12]    wetCDOM[width=12]    latitude[width=12]    longitude[width=12]    scan[width=12]    flag
    toplevel_header_list = ('Station','Cast','Date','Time','Lat','Lon');
    toplevel_header = ','.join(toplevel_header_list)
    toplevel_data_delimiter = '\t'#what goes in between toplevel datalines, not the header
    toplevel_data = {}
    
    
    topf = open('../'+cruise+'/toplevel.dat','w')
    topf.write(fileComment)
    topf.write(toplevel_header+',>\n') #lineText must end ,>
   # topf.write()#need to add datetimeparam that is added here
    
    #---------------------GET FIRST CHUNK OF DATA FOR TOPLEVEL--------------------------
    print "Extracting data in "+dataDirs['orig']
    
    origFiles = os.listdir(dataDirs['orig'])
    datData =[]#list of dat dictionaries (one per file)
    
    for filename in origFiles:
        #only get the files that have cruise name and xls
        if (not re.search(cruise,filename,re.IGNORECASE)) or  (not re.search('xls',filename,re.IGNORECASE)):
            continue                               
    
        #toplevel_data['cruise_id'] = os.path.splitext(filename)[0]
        #print('CruiseID',toplevel_data['cruise_id'])
        
      #  outfile =re.sub('\.xls.*','.dat',filename)
        utils.XLS2CSV(dataDirs['orig']+'/'+filename,dataDirs['raw'])
        
    topf.close() #toplevel file
print "DONE!"   