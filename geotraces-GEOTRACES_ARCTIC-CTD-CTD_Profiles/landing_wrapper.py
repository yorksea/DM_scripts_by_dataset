import os,re,io
from sys import platform as _platform
import pandas as pd
from dmtools import Line,paramLookup,utils
from collections import OrderedDict

# Author:Amber York
# 9 Sept 2016
# This script takes an input directory of csv files, and writes a toplevel file and generates bco-dmo format subfiles.
# Grabs relevant data from fileheaders to populate a toplevel file data

###-----------------------------------
dataset_identifier = 'ctd_profiles'
#BTMDEPTH = DEPTH
toplevel_header = 'cruise_id,EXPOCODE,SECT_ID,STNNBR,CASTNO,GEOTRC_EVENTNO,DATE,TIME,LATITUDE,LONGITUDE,DEPTH,INSTRUMENT_ID,TIMESTAMP,PREVIOUS_TIMESTAMP'
fileheader ='CTDPRS,CTDPRS_FLAG_W,CTDTMP,CTDTMP_FLAG_W,CTDSAL,CTDSAL_FLAG_W,CTDOXY,CTDOXY_FLAG_W,TRANSM,TRANSM_FLAG_W,FLUORM,FLUORM_FLAG_W,DEPTH,DEPTH_FLAG_W,CTDNOBS,CTDETIME'

#setupDirs makes a set of folders for output and tells what the orig dir is
dataDirs = utils.setupDirs(**{'origDir':'33HQ20150809_ct1'})# a dictionary of paths
print('source dir is '+dataDirs['orig'])
print('output dir is '+dataDirs['final'])

logFile = os.path.join(dataDirs['provenance'],dataset_identifier+'.log')      
flog = open(logFile,'w')
#-------------toplevel config

fileComment = \
'''# CTD-GTC profiles
#    U.S. GEOTRACES - Arctic Section
#      Healy HLY1502
#      9 August- 12 October 2015
#      version:20160609ODU
#    Dataset Version Date: 9 Sept 2016
'''

topf = open('../'+dataset_identifier+'_toplevel.dat','w')
topf.write(fileComment)
topf.write(toplevel_header+',>\n') #lineText must end delimiter then >
topf.write(fileheader+'\n')
toplevel_datalines = []


#logging stuff which gets written to provenance record
logList = []#will be filled with dictionraries of log messages

LogDict = {}
LogDict['comment'] = fileComment
#LogDict['dataDirs'] = dataDirs
LogDict['fileList'] = []
LogDict['fileMessages'] = [] #append to list every loop of files
gitInfo = {}
gitInfo['dmotools']= {'repo':'https://github.com/BCODMO/dmtools'}
#gitInfo['wrapper'] =   {'repo':'https://github.com/BCODMO/DM-scripts-by-dataset/tree/master/LaurentianGreatLakes_Chemistry','file':'Popp_CTD_Wrapper.py'} 
LogDict['gitInfo'] = gitInfo

#get list of files
rawfiles = os.listdir(dataDirs['orig'])
print(dataDirs['orig'])

#loop through the files
for rawfile in rawfiles:
    print(rawfile)
    lineMessages  = [] #populated if any error correction or data manipulation happens
    
    #this is a dictionary which is what toplevel lines are written from
    topLevel_data = {'cruise_id':'HLY1502'}
    
    #more info for log
    LogDict['fileList'].append(rawfile)
    
    finalFile= re.sub('csv','dat',rawfile)
    fraw = open(os.path.join(dataDirs['orig'],rawfile),'r') #might have unicode in there, but deal with it later
    ffinal = open(os.path.join(dataDirs['final'],finalFile),'w')
    

    linecount = 0
    datalinecount = 0
    dataflag = False #when data lines happen this is True, changed to one when line starts DBAR
    
    #loop lines, treating header and comment lines different from datalines
    for origline in fraw:
        linecount =linecount+1
        
        if dataflag == False:  #still in header if false
               
            #data is after "DBAR" line so after this lines get written to files
            if re.search('^DBAR',origline):
                #this is the end of the header.
                goflag = 1
                
                #print to toplevel
                
                ''' the stuff we want in no particular order:
                CTD,20160310CCHSIOSEE
                # CTD,20160119ODF - Previous Time Stamp 
                #    GEOTRC_EVENTNO = 6276
                EXPOCODE = 33HQ20150809
                SECT_ID = ARC01
                STNNBR = 40
                CASTNO = 1
                DATE = 20150912
                TIME = 2308
                LATITUDE = 86.6974
                LONGITUDE = -149.2945
                DEPTH = 3417
                INSTRUMENT_ID = 831
                
                '''
                
                #loop toplevel header to constuct the dataline
                top_dataline = [] #line to be written will be populated
                for param in toplevel_header.split(','):#loops through params in header
                    #print('['+param+']')
                    if param in topLevel_data:
                        top_dataline.append(topLevel_data[param])
                        #print('['+param+']'+ topLevel_data[param])
                    else: 
                        top_dataline.append('test')#will be nd
                top_dataline.append('final/'+rawfile)#append filename
                
                topf.write(','.join(top_dataline)+'\n') #write the toplevel data line
            
                #setup the new file
                ffinal.write(fileComment)
                ffinal.write(fileheader+'\n')
                
                
                           
            else: #is still filecomment stuff so get any needed data for topfile
                 
                                #print origline
                origline = re.sub('^,','',origline) #all files in this dataset have this problem of an empty column which results in a leading comma        
                origline = origline.rstrip('\r\n')
                #finalLine = Line(origline) #will fill in header after it is built with setHeader
    
                if re.search('^CTD,',origline):
                    #print(origline)
                    parts = re.split(',',origline)
                    #print parts
                    topLevel_data['TIMESTAMP'] = parts[1] 
                if re.search('# CTD',origline):
                    topLevel_data['PREVIOUS_TIMESTAMP'] = origline.strip(' - Previous Time Stamp|# CTD,')
                    
                           
                if re.search('EVENTNO',origline):
                    origline = re.sub('#.*GEO','GEO',origline)#remove comment and it gets added same as rest of = pairs
                    
                #get toplevel data if there
                if re.search('=',origline):
                    parts = re.split('=',origline)
                    topLevel_data[parts[0].strip(' \t\n\r')] = parts[1].strip(' \t\n\r')
                
            continue  
        else:  #this is data, progresses here if dataflag == True
            #if it got to here then it's data
            datalinecount = datalinecount+1
            
            finalLine = Line(**{'dataline':origline,'lineNum':linecount,'headerline':fileheader})                         

            ffinal.write(finalLine.getData()+'\n')#prints as comma delimited text
            
            m = finalLine.getLog(**{'format':'dict'})
            if len(m['messages']) > 0: #append if anything to say
                lineMessages.append(m)
                
                
    if len(lineMessages) > 0: #only write out if error messages
        LogDict['fileMessages'].append(OrderedDict([('sourceFile',rawfile), 
                          ('other_metadata', {'cruise_id':cruise_id,'cast':cast}), 
                          ('lineMessages', lineMessages)]))
    
    

    #loop lines
    fraw.close()
    ffinal.close()


utils.writeToLog({'errorLog':LogDict},flog)


#print the toplevel lines
topf.close()

flog.close()
print("DONE!")