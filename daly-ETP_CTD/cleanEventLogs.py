import os,re,time,datetime
#from sys import platform as _platform
from  DMTools import Line,xlsx2csv
#from wsgiref import headers
#from operator import itemgetter #to sort list of dictionaries

header = 'event,instrument,castno,station,action,month_local,day_local,time_local,month_utc,day_utc,time_utc,lat,lon,depth_w,depth_n,si,comment,ISO_DateTime_UTC'
headerList = header.split(',')

filepath = '../event_logs/'
files = ['SJ07.csv','KN195-02.csv']

#fout = open(filepath+'event_logs.dat','w')

fout = open('Z:/daly/event_logs/event_logs.dat','w')

fileComment = \
'''# Eastern Tropical Pacific Event logs from KN195-02 and SJ07
#    Kendra Daly, P.I.
#    Version 25 Jul 2016
'''

fout.write(fileComment)
fout.write("year,cruise_id,"+header+'\n')


for file in files:
    f = open(filepath+"intermediate_files/"+file)
    for line in f:
        
        if re.search('(,,,,,,,,,,,,,,,,|^#|^event)',line) :
            continue
        line = Line(line,header)
        line.stripQuotePairs()
        line = line.getText()
        
        #stop line returns
        line = re.sub('\n|\r','',line)
        #print line
        
        #trim whitespace from start | end
        re.sub('(^\s|\s*$)','',line)
        #print('['+line+']')
        #print len(line)
        '''
        if re.search('(\s|\d)',origLine):
            print "skipping just delimiters"
        else:
            line = Line(origLine,header) 
            print(line)
            parts = line.getDataList()
            #for part in parts:
            print line.getParam('lat')
            '''
        
        #some events have double ..
        line = re.sub('\.\.','.',line)
        parts = line.split(',')

        
        lat = parts[11]
        lon = parts[12]
        time_local = parts[7]
        time_utc = parts[10]
        #print "lat="+lat+" lon="+lon+' time_local='+time_local+" time_utc="+time_utc
        
        

        lat  = re.sub('\'','',lat)#remove tick marks
        lon  = re.sub('\'','',lon)#remove tick marks
        #print "["+lon+"]"
        lat  = re.sub(':',' ',lat)
        lon  = re.sub(':',' ',lon)
        
        #remove .\s
        lat  = re.sub('\.\s',' ',lat)#remove tick marks
        lon  = re.sub('\.\s',' ',lon)#remove tick marks
        
        #correct a known mistakes in original submission
        lon = re.sub('^150','105',lon) #finger entry error
        lon = re.sub('299.9997$','29.9997',lon)
        lon = re.sub('900.0062$','00.0062',lon)
        
        #for all . in spaces 105.00.0647 to 105 00.0647
        if len(lon.split('.')) > 2:
            print line+'\n'+lon
            lon = re.sub('^(\d*)\.',r'\1 ',lon)


        if len(lat.split('.')) > 2:
            print line+'\n'+lon
            lat = re.sub('^(\d*)\.',r'\1 ',lat)            
        '''
        bad loc examples
        13.00.0053    13 00.0053
                        105.  0012
        10.59.02    97.28.63
        13.00.002    105.00.013
        13.00.0053    105.00.0647
        13.00.2772    105.00.9531

        '''
        lon = re.sub(' (\d\d)(\d*)$',r' \1.\2',lon)
        lat = re.sub(' (\d\d)(\d*)$',r' \1.\2',lat)
                
        #trim and add back to parts
        parts[11] = re.sub('(^ *| *$)','',lat)
        parts[12] = re.sub('(^ *| *$)','',lon)


        #time stuff (local)
        time = re.sub(':','',time_local)
        #padd correctly
        time = re.sub('^(\d)$',r'000\1',time)
        time = re.sub('^(\d\d)$',r'00\1',time)
        time = re.sub('^(\d)(\d\d)$',r'0\1\2',time)
        
        parts[7] = time #tiem local
        
        #UTC time 
        time = re.sub(':','',time_utc)
        #padd correctly
        time = re.sub('^(\d)$',r'000\1',time)
        time = re.sub('^(\d\d)$',r'00\1',time)
        time = re.sub('^(\d)(\d\d)$',r'0\1\2',time)
        parts[10] = time #tiem local  
       
        #print time+'\t'+parts[7] #time local
       # print time+'\t'+parts[10] #time utc
        cruise_id = ''
        year = ''
        if re.search('^K',parts[0],re.IGNORECASE):
           cruise_id = 'KN195-02'
           year = '2008'
        elif ('^S',parts[0],re.IGNORECASE):
           cruise_id = 'SJ07'
           year = '2007'
        newline = year+","+cruise_id+","+",".join(parts)
        fout.write(newline+'\n')
        #print newline+"\n"
    f.close()
fout.close()