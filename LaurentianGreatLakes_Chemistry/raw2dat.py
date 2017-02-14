import os,sys,re,glob,time

## date and time representation
nowDate =time.strftime("%d %b %Y") #19 Aug 2016
print(nowDate)
   
#--------------------------------------------------------------------

folders = ['IRONMAN','NILSS']

          
for folder in folders:
    allparams = []  #all params in level 1
    level1_dats = {} #dictionary for all files to write
    level0_lines = {}
        
    print "Folder: "+folder
    datafolder = 'Z:/LaurentianGreatLakes_Chemistry/CTD/'+folder+'/'
    fileComment = "# "+folder+" CTD Profiles\n#    PI: Robert Sterner\n#    Data version "+nowDate

    #setup toplevel file
    #   Station[width=14]    Cast    Date____    Time__    Lat______    Lon_______    >
    #prDM[width=12]    t090[width=12]    c0[width=12]    specc[width=12]    xmiss[width=12]    wetStar[width=12]    dz_dt[width=12]    ph[width=12]    par[width=12]    spar[width=12]    sal00[width=12]    sbeox0_Mm[width=12]    sbeox0_Mg[width=12]    sbeox0_PS[width=12]    wetCDOM[width=12]    latitude[width=12]    longitude[width=12]    scan[width=12]    flag
    toplevel_header = ['CruiseID','Station','Date','Time','Lat','Lon','ISO_DateTime_UTC'];
 
    ftop = open(datafolder+folder+'_toplevel.dat','wb')
    ftop.write(fileComment+'\n')
    ftop.write(",".join(toplevel_header)+',>\n') #lineText must end ,>
   
   # ftop.write()#need to add datetimeparam that is added here
       
             
    #working with just the csvs -----raw to clean------------        
    level1files = os.listdir(datafolder+'raw')
    
    for level1file in level1files:
        print 'reading '+level1file
        fraw = open(datafolder+'raw/'+level1file)
        #ffinal = open(dataDirs['final']+'/'+level1file,'w')
  
        #initialize if not exist
        if level1file not in level1_dats:
            level1_dats[level1file] = []
                  
        fparts = level1file.split("_sheet-")
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
                #remove trailing commas, and add to list of output
                level1_dats[level1file].append( re.sub(',+$','',origline) )
                continue
            
            datalinecount = datalinecount+1
            #do header stuff once
            if datalinecount == 1:
                
                header = origline.split(',')
                
                level1_dats[level1file].append("#   cast: "+cast)
                level1_dats[level1file].append(",".join(header[6:]))

                #add variables to all param list if not already
                for p in header:
                    #print p
                    if p not in allparams:
                        allparams.append(p)
                
                continue

            dline = origline.split(',')
            level1_dats[level1file].append(",".join(dline[6:]))

            if datalinecount == 2:
                #first line of real data not header

                #is CruiseID,Station,Date,Time,Lat,Lon data plus the nd for ISO_DateTime_UTC placeholder
                #index is datetime (dline[2]+dline[3]) so it can be sorted by time
                level0_lines[dline[2]+dline[3]] = "\t".join(dline[0:6])+'\tnd\tfinal/'+level1file
           
             
        fraw.close()        
    
    #write everything
    
    # second line of level1 variables to toplevel file

    ftop.write(",".join(allparams[6:])+'\n')
    #write the data lines to level 0 topfile in order
    for k in sorted(level0_lines.keys()):
        ftop.write(level0_lines[k]+'\n')

    ftop.close() #toplevel file
    
    
    for level1file in level1files:
        print 'writing '+level1file
        fout = open(datafolder+'final/'+level1file,'wb')
        fout.write("\n".join(level1_dats[level1file]))
        fout.close()

print "Done!"    