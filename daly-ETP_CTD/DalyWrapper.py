import os,re
from sys import platform as _platform
from  DMTools import Line,xlsx2csv
from wsgiref import headers
from operator import itemgetter #to sort list of dictionaries


origDir = '../intermediate_files/orig/ctd_all'
outDir = '../intermediate_files/csv'
finalDataDir = '../cruise_data'

PIname = 'daly'

verbose = False
#original data is one worksheet xlsx data

print "Parsing data in "+origDir

origFiles = os.listdir(origDir)
needConversion = False #true if you haven't yet exported to csv

toplevel_header_list = ('year','cruise_id','station','castno','lat_start','lon_start','date_start','time_start');
toplevel_header = ','.join(toplevel_header_list)
toplevel_data_delimiter = '\t'#what goes in between toplevel datalines, not the header

#header is for what is in each filename
header= 'scan,date_string,time,lon,lat,depth,temp,temp2,potemp,potemp2,sal,cond1,cond2,sigma_e00,sigma_e11,press,O2_ml_L,O2_mg_L,O2_sat_pcnt,O2_umol_kg,sound_vel_Chen,sound_vel_Delgrosso,sound_vel_Wilson,beam_c,trans,cpar,fluor,par,spar'

#hFile = open('../'+PIname+'.vars','w')
#hFile.write(header+',ISO_DateTime_UTC')#derived params added to toplevel header
#hFile.close()


#orig header in the original data starts Scan,Date,Time,Longitude,Latitude... and data is that lineText num +2

origHeader = 'Scan,Date,Time,Longitude,Latitude'

fileComment = \
'''# Eastern Tropical Pacific CTD DATA
#    Kendra Daly, P.I.
#    Version 25 Jun 2016
'''

cFile = open('../'+PIname+'.comment','w')
cFile.write(fileComment)
cFile.close()


topf = open('../'+PIname+'_toplevel.dat','w')
topf.write(fileComment)
topf.write(toplevel_header+',>\n') #lineText must end ,>
topf.write(header+',ISO_DateTime_UTC\n')#need to add datetimeparam that is added here

print(fileComment)        
    
datData =[]#list of dat dictionaries (one per file)


for filename in origFiles:
    if re.search('(^~|up)',filename,re.IGNORECASE):
        continue

    dat = {}#dictionary for this file
    dat["outfile"] =re.sub('xlsx','dat',filename)
    dat["infile"] = filename
    
    #make all toplevel variables nd (in case no info like ISO_DateTime_UTC
    #cruise_id=station=lat_start=lon_start=date=time= 'nd'  #this was when I wan't using dictionary
    for paramName in toplevel_header_list:
        dat[paramName] = 'nd'
    
    print(filename)
    #print "Orig: "+filename
    infile = origDir+'/'+filename
    outfile = outDir+'/'+re.sub('xlsx','csv',filename)
    if re.match("^S",filename):
        dat["year"] = '2007'
        dat["castno"] = re.sub('.*\.','',re.sub('_.*','',filename)) #SJ07.072.16_KD_BIN.dat
    else:
        dat["year"] = '2008'
        dat["castno"] = re.sub('(\d{6}|_.*)','',filename) #19502016_KD.dat
    
    if not re.match('linux',_platform):
        if needConversion:
            raise ValueError('You are not on linux, can not do xls2csv, needs linux and gnumeric package')

            xlsx2csv(infile, outfile)
            print("xlsx2csv("+infile+","+ outfile+')')      
        
    csvFile = open( outDir+'/'+re.sub('xlsx','csv',filename),'r') #the file directly after xls2csv conversion, no manipulation yet
    finalFile = open(finalDataDir+'/'+re.sub('xlsx','dat',filename),'w') #file to write to for serving
    
    finalFile.write(fileComment) #don't need if have vars file
    finalFile.write(header+'\n')
    
    lineCount = 1

    dataStartAt = '' #will be changed once orig header lineText read
     
    for origline in csvFile:
        origline = origline.rstrip('\r\n')
         
        if bool(re.search(origHeader,origline)): 
            dataStartAt = lineCount+2
       
        line = Line(origline) #this makes the lineText a Line class so can access methods for QA
               
        #if lineText.isDataLine(): #this works or do by dataStartAt detection
        if lineCount >= dataStartAt:
            line.stripQuotePairs()
            finalFile.write(line.getText()+'\n')
        
        if verbose == True:
            print(str(lineCount)+' '+str(line.isDataLine())+' '+line.getText())
            
        #fill in toplevel data if on this lineText
        
        ''' toplevel lineText examples
        lat_start:
        * NMEA Latitude = 09 59.91 N 
        
        lon_start:   
        * NMEA Longitude = 093 43.46 W    
        
        date and time:
        * NMEA UTC (Time) = Nov 05 2007 21:36:30    
        
        castno:
        ** castno 1
        ** castno: castno 8
        ** Operator: RC

        cruise_id: #need to find this but detected by
        R/V Knorr
        Ship: RVSJ
        
        ISO_DateTime_UTC:
        # start_time = Nov 09 2007 13:32:29 [System UTC, first data scan.]
        

                   
        ''' 
           
        lineText = line.getText()
        
        #if re.match('Knorr',lineText):
        if bool(re.search('Knorr',lineText)):
            print("Line "+lineText)
            dat['cruise_id'] = 'KN195-02'
            
        if bool(re.search('RVSJ',lineText)):
            print("Line "+lineText)
            dat['cruise_id'] = 'SJ07' #TODO need to find num
                

        if bool(re.search('NMEA Latitude',lineText)):
            print("Line "+lineText)
            lat_start = re.sub('.*= ','',lineText, re.IGNORECASE)    
            if re.match('S',lat_start):
                lat_start = '-'+lat_start
            lat_start = re.sub('(N|S|E|W|\s*)','',lat_start)  
            dat['lat_start'] = re.sub('\D*$','',lat_start) 
             

        if bool(re.search('NMEA Longitude',lineText)):
            print("Line "+lineText)
            lon_start = re.sub('.*= ','',lineText, re.IGNORECASE) 
            if re.match('W',lat_start):
                lon_start = '-'+lon_start
            lon_start = re.sub('(N|S|E|W|\s*)','',lon_start) 
            dat['lon_start'] =  re.sub('\D*$','',lon_start) 
                
        if bool(re.search('NMEA UTC',lineText)):
            print("Line "+lineText)
            date_string =  re.sub('.*= ','',lineText, re.IGNORECASE) 
            dateparts = date_string.split(' ')
            time = dateparts[len(dateparts)-1] #time is the last one
            date = re.sub(time,'',date_string)
            dat['date_start'] =  re.sub('\D*$','',date) #strip off any remaining non digits at end of line
            dat['time_start'] =  re.sub('\D*$','',time) #strip off any remaining non digits at end of line
            dat['date_string'] = date_string 

        if bool(re.search('Station',lineText,re.IGNORECASE)) and dat['station'] == 'nd':  #second logic to catch first description of station
            print("Line "+lineText)
            #this didn't work becaues matches stuff like "** 195-02-032 Station 8 deep cast (2500 m)"
            #need to have different lineText numbers for     
            station = re.sub('.*Station: ','',lineText,re.IGNORECASE)
            station =  re.sub('Station ','',station,re.IGNORECASE) #if like shown above station wrote twice\
            
            
                        #if it is a substation like 4a or 4b we want to preserve the letter
          
            p = re.compile("(\d+[a-zA-Z]+)")#take .group1 for first parenthesis
            m = p.search(station)
            # search() returns a Match object with information about what was matched
            if m:
                station = m.group(1)
            else:
                station = re.sub('(^\D*|\D*$)','',station)
                 
            if station == "":
                station = 'nd'
            
            station = station.lower()
            dat['station'] = station
                           
        lineCount += 1
    
    csvFile.close()
    finalFile.close()
    

    #add to dat dictionary list
    datData.append(dat)
#end filename loop   


#--------------------now write toplevel

## read back in and order by date/time
#TODO fix sort
    #datData = sorted(datData, key = lambda user: (user['date_start'], user['time_start']))  #this is same as below
    #datData = sorted(datData, key=itemgetter('date_start', 'time_start'))
for dat in datData:
    
    
    #loop dictionary sorted by time and write datline
    '''
    datLine = year+'\t'+cruise_id+'\t'+station+'\t'+str(castno)+'\t'+lat_start+'\t'+lon_start+'\t'+date+'\t'+time+'\tcruise_data/'+re.sub('xlsx','dat',filename)+'\n'
        print("Toplevel lineText: "+datLine)
        topf.write(datLine)
        
        to get decimal places
        
        >>> d.as_tuple().exponent
        -4
          '''  
    for param in toplevel_header_list:
        print(param+" "+dat[param]+toplevel_data_delimiter)

        topf.write(dat[param]+toplevel_data_delimiter)
        if param == toplevel_header_list[-1]: #add filename and line return  if last
            topf.write('cruise_data/'+dat['outfile']+'\n')
        
topf.close()

print "Done!"