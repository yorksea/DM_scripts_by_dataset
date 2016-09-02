import os,re,io
from sys import platform as _platform
import pandas as pd
from dmtools import Line,paramLookup,utils
from collections import OrderedDict

###-----------------------------------
dataset_identifier = 'popp'

dataDirs = utils.setupDirs()# a dictionary of paths
print('source dir is '+dataDirs['orig'])

outputRaw = False

logFile = os.path.join(dataDirs['provenance'],dataset_identifier+'.log')      
flog = open(logFile,'w')
#-------------toplevel config

fileComment = \
'''# CTD Profiles
#    Brian Popp, P.I.
#    Version 23 Aug 2016
'''

topf = open('../'+dataset_identifier+'_toplevel.dat','w')
topf.write(fileComment)
topf.write('cruise_id,station,cast,lat,lon,ISO_DateTime_UTC,>\n') #lineText must end ,>
toplevel_datalines = []
all_params_in_orig_files = [] #will be filled in dynamically from each file

logList = []#will be filled with dictionraries of log messages
#------------extract sheets-------------
if outputRaw == True:
    utils.XLS2CSV_byFolder(dataDirs['orig'],dataDirs['raw'],'!1506');#d    

    #note: header is built dynamically from any line that starts with this '#,name'

    print "extracted sheets to csv (saved to raw folder "+dataDirs['raw']+')'

rawfiles = os.listdir(dataDirs['raw'])
#-------------------------
#working with just the csvs -----raw to clean------------        
datasetFolder = 'popp/Popp_CTD/final'#what is under /data302 on dmoserv3

LogDict = {}
LogDict['comment'] = fileComment
LogDict['dataStorageLocation'] = 'dmoserv3:/data302/'+datasetFolder
#LogDict['dataDirs'] = dataDirs
LogDict['fileList'] = []
LogDict['fileMessages'] = [] #append to list every loop of files
gitInfo = {}
gitInfo['dmotools']= {'repo':'https://github.com/BCODMO/dmtools'}
gitInfo['wrapper'] =   {'repo':'https://github.com/BCODMO/DM-scripts-by-dataset/tree/master/LaurentianGreatLakes_Chemistry','file':'Popp_CTD_Wrapper.py'} 
LogDict['gitInfo'] = gitInfo

print(dataDirs['raw'])
for rawfile in rawfiles:
    lineMessages  = []
    
    if not re.search('Sheet1',rawfile):
        continue
    LogDict['fileList'].append(rawfile)
    
    finalFile= re.sub('csv','dat',rawfile)
    fraw = open(os.path.join(dataDirs['raw'],rawfile),'r') #might have unicode in there, but deal with it later
    ffinal = open(os.path.join(dataDirs['final'],finalFile),'w')
    
    fparts = re.split("_|-|\.csv",rawfile);
    cruise_id = fparts[0].upper()
    stationcast = fparts[1]
    sheetname = fparts[-2]#second to last in list

    #for cast, get everything after last letter from c as in cast (take staring with digits)
    cast = re.sub('.*(cast|c)','',stationcast,flags=re.I)
    if re.search('^cast',stationcast,re.IGNORECASE):
        station = 'nd' #no station so say nd
    else:
        station = re.sub('(^s|(cast|c).*)','',stationcast,flags=re.I)
    
   
    '''examples of castinfo sheet
    
    Latitude,4.99183333333
    Longitude,-154.905
    UTCDateTime,2015-08-30 17:23:46
    LocalDateTime,2015-08-30 07:23:46
    '''
    fcastinfo = open(os.path.join(   dataDirs['raw'],re.sub('Sheet1','castinfo',rawfile)  ),'r')
    castinfo = fcastinfo.readlines()
    
    lat = castinfo[0].split(',')[1].rstrip()
    lat = utils.roundTo(lat,4)
    
    lon = castinfo[1].split(',')[1].rstrip()
    lon = utils.roundTo(lon,4)
    
    ISO_DateTime_UTC = (castinfo[2].split(',')[1].rstrip()+'Z')
    ISO_DateTime_UTC = re.sub(' ','T',ISO_DateTime_UTC).rstrip()
    
    fcastinfo.close()
    
   
    header = []#built dynamically
    linecount = 0
    datalinecount = 0
    for origline in fraw:
        
        
        linecount =linecount+1
        #print origline
        origline = re.sub('^,','',origline) #all files in this dataset have this problem of an empty column which results in a leading comma        
        origline = origline.rstrip('\r\n')
        #finalLine = Line(origline) #will fill in header after it is built with setHeader
        finalLine = Line(**{'dataline':origline,'lineNum':linecount}) #works but not needed
        #print(str(linecount)+'\t'+origline)    
        if re.search('^======',origline):
            #don't print
            continue
        
        if re.search('^(#|\*)',origline) :
            #it's a filecomment if starts with # or *
            if re.search('station.*aloha',origline,flags=re.I) or cruise_id == 'KM1418':
                station = 'ALOHA'               

            #check for trailing commas (for comment lines only)
            finalLine.stripCommas()
            
            if re.search('#,name',finalLine.getData()):
                #make header from these lines
                finalLine.replaceUnicode() #some params have this

                
                parts= finalLine.getDataList()
                newHeaderItem = re.sub(':$','',parts[4])#strip : at end of value
                newIndex = parts[2]#which column of data this is (starting at 0) #not used right now
                header.append(newHeaderItem)
                #add to toplevel second header if doesn't exist
                if not newHeaderItem in all_params_in_orig_files:
                    all_params_in_orig_files.append(newHeaderItem)
                    #print("new param:"+newHeaderItem+" from line: "+str(linecount))
                    #print rawfile+' '+origline+'\n'
                        
            #ffinal.write(cline+'\n')
            #print("Comment: "+origline)
            continue
        
        
        #if it got to here then it's data
        datalinecount = datalinecount+1
        if datalinecount == 1:
            print("cruise: "+cruise_id+' station: '+station+' cast: '+cast+' file: '+rawfile)
            #in ctd files this line starts with *END*
            #TODO: write header
            
            #write the last comment before the header
            #specificLine = "#     cruise: "+cruise_id+' cast: '+cast+'\n'
            #print(specificLine)
            #write header

            orig_header = header
            header = paramLookup(**{'lookupfile':'param_lookup_table.xlsx','origHeader':orig_header})
            #done building header so add to Line
            ffinal.write(fileComment)
            ffinal.write('#      cruise: '+cruise_id+'\n')
            ffinal.write(','.join(header)+'\n')
            #done building header
            
           
            continue   
        
        finalLine.setHeader(header)
        #print('Headerline: '+finalLine.getHeader())

        finalLine.roundVal('lat,lon',4)
        
        
        
        
        firstParam =finalLine.getHeaderList()[0]
        if re.search('-9.99e-29',finalLine.getData()): #Houston we have a problem
            finalLine.replaceAllBadValues()#that bad value is already known so don't have to specify it
        
        
        finalLine.matchHeaderLengthIfEmpty() #if length of data and header different, removes last values only if they are empty

        ffinal.write(finalLine.getData()+'\n')#prints as comma delimited text
        m = finalLine.getLog(**{'format':'dict'})
        if len(m['messages']) > 0: #append if anything to say
            lineMessages.append(m)
    if len(lineMessages) > 0: #only write out if error messages
        LogDict['fileMessages'].append(OrderedDict([('sourceFile',rawfile), 
                          ('other_metadata', {'cruise_id':cruise_id,'cast':cast}), 
                          ('lineMessages', lineMessages)]))
    
    
    #logJSON = utils.dict2json(LogDict)
    #flog.write(logJSON)
    
    #loop lines
    fraw.close()
    ffinal.close()


    toplevel_datalines.append('\t'.join([cruise_id,station,cast,str(lat),str(lon),ISO_DateTime_UTC,'final/'+finalFile]))

utils.writeToLog({'errorLog':LogDict},flog)

print("all data header:\n     "+ ','.join(all_params_in_orig_files))
print("Matched standard param names and saved to params.csv")
data_header = paramLookup(**{'lookupfile':'param_lookup_table.xlsx','origHeader':all_params_in_orig_files,'outpath':dataDirs['provenance']})
print(data_header)

#print the toplevel lines
topf.write(','.join(data_header)+'\n')
for item in toplevel_datalines:
  topf.write("%s\n" % item)
topf.close()

flog.close()
print("DONE!")