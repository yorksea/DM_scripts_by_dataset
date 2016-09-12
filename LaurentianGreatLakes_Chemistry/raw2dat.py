import os,sys,re,glob,time
from dataset_tools import Line,utils
from pip.utils import logging

## date and time representation
nowDate =time.strftime("%d %b %Y") #19 Aug 2016
print(nowDate)
   
#--------------------------------------------------------------------

folders = ['IRONMAN','NILSS']

 
PIname = ('Robert','Sterner');
        
for folder in folders:
    print "Folder: "+folder
    maxWidths = {} #for display purposes
    fileComment = "# "+folder+" CTD Profiles\n#    P.I. "+PIname[0]+' '+PIname[1]+"\n#    Version "+nowDate

    #setup toplevel file
    #   Station[width=14]    Cast    Date____    Time__    Lat______    Lon_______    >
    #prDM[width=12]    t090[width=12]    c0[width=12]    specc[width=12]    xmiss[width=12]    wetStar[width=12]    dz_dt[width=12]    ph[width=12]    par[width=12]    spar[width=12]    sal00[width=12]    sbeox0_Mm[width=12]    sbeox0_Mg[width=12]    sbeox0_PS[width=12]    wetCDOM[width=12]    latitude[width=12]    longitude[width=12]    scan[width=12]    flag
    toplevel_header_list = ('CruiseID','Cast','Date','Time','Lat','Lon');
    toplevel_header = ','.join(toplevel_header_list)
    second_header_list =('CruiseID','Station','Date','Time','Lat','Lon','press','temp','cond','cond_spec','beam_trans','fluor','O2_mg_L','pH','PAR','flag');
    second_header = ','.join(second_header_list);

    
    toplevel_data_delimiter = '\t'#what goes in between toplevel datalines, not the header
    toplevel_data = {}

    
    #setup directory structure if doesn't exist already (it checks)
    dataDirs = utils.setupDirs('../'+folder)# a dictionary of paths          
    
    ftop = open('../'+folder+'/'+folder+'_toplevel.dat','w')
    ftop.write(fileComment+'\n')
    ftop.write(toplevel_header+',>\n') #lineText must end ,>
    ftop.write(second_header+'\n') #lineText must end ,>
   # ftop.write()#need to add datetimeparam that is added here
    

    
             
    #working with just the csvs -----raw to clean------------        
    rawfiles = os.listdir(dataDirs['raw'])
    

    print(dataDirs['raw'])
    for rawfile in rawfiles:
       # print rawfile
        fraw = open(dataDirs['raw']+'/'+rawfile,'r')
        ffinal = open(dataDirs['final']+'/'+rawfile,'w')
        
        fparts = rawfile.split("_sheet-")
        cruise_id = fparts[0]
        cast = re.sub('\..*','',fparts[1])
        #add to header comment
        linecount = 0
        datalinecount = 0
        for origline in fraw:
            linecount =linecount+1
            
            
            origline = origline.rstrip('\r\n')
            #print(str(linecount)+'\t'+origline)    
            if re.search('^======',origline):
                #don't print
                continue
            
            if re.search('^#',origline) :
                #print and move on 
                
                #check for trailing commas
                cline = re.sub(',+$','',origline)
                
                ffinal.write(cline+'\n')
                continue
            
            datalinecount = datalinecount+1
            if datalinecount == 1:
                #write the last comment before the header
                specificLine = "#     cruise: "+cruise_id+' cast: '+cast+'\n'
                print(specificLine)
                ffinal.write(specificLine)
                
                header = origline
                continue
                
            # print("#      cruise: "+cruise_id+' cast: '+cast+'\n')                
            #do line stuff
            
            finalLine = Line(origline,header)
            # lineDict = finalLine.getDataDict()
            # print(lineDict)
           
            #in this case, dont' write first 6 params
            lineList = finalLine.getDataList()
            if datalinecount == 10:
                ftop.write('\t'.join(lineList[0:6])+'\tfinal/'+rawfile+'\n')
                            
            ffinal.write(','.join(lineList[7:])+'\n')   
            
            
                    #now test if param is longer than before
            thisPCount = finalLine.getParamLengths()
            for k, v in thisPCount.items():
                #v is the length of that param's value
                if k not in maxWidths:#then first time so fill it
                  maxWidths[k] = v+2
                    
                #if longer this time then make that the max in the list (+2 is becuase I use that for display)
                if v+2 > maxWidths[k]:
                    maxWidths[k] = v+2
                
            
        ffinal.close()
        fraw.close()
        
    
        
        dispWidths = '';
        for p in finalLine.getHeaderList(): 
                       
            #check if name is bigger than value
            if len(p) > maxWidths[p]:    
                val =  len(p)+2                  
            else:
                val = maxWidths[p]
                   
            dispWidths = dispWidths+p+'='+str(val)+'; '    
        fdisp = open('../'+folder+'/'+folder+'dispWidths.txt','w')
        fdisp.write(dispWidths)
        fdisp.close()
    
    ftop.close() #toplevel file
    


print "Done!"    