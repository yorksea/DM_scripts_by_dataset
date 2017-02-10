from dmtools import *
import os,sys,re

'''
 Author:Amber York
 06 Feb 2017
 This script takes an input directory of csv files, and writes a toplevel file and generates bco-dmo format subfiles.
 Grabs relevant data from fileheaders to populate a toplevel file data

For CTD McMurdo Predators dataset:
https://www.bco-dmo.org/dataset/680929
PIs Stacy Kim and Kendra Daly
'''

# first convert all xls to csv (files based on original name
# input folder, output folder (doesn't have to exist, it will be made)
xlsdir = "Z:/daly/McMurdoPredPrey/CTD/data" #input
csvdir ="Z:/daly/McMurdoPredPrey/CTD/csv" #output
finaldir = "Z:/daly/McMurdoPredPrey/CTD/final" 

# do below line once to get xls to csv, just takes more time subsequent runs so you don't need it 
# utils.XLS2CSV_byFolder(xlsdir,csvdir)

#check for final data
if not os.path.exists(finaldir):
    os.makedirs(finaldir)



#-------------toplevel config
# get list of all possible params in files
allparams = []


#get list of files
rawfiles = os.listdir(csvdir)

#loop through the files
for rawfile in rawfiles:   
    
    linecount = 0
    datalinecount = 0
    dataflag = False #when data lines happen this is True, changed to one when line starts DBAR
    startread = '^Scan,' #the headerline and all under this are valid
    #loop lines, treating header and comment lines different from datalines

    x = rawfile.split('_')
    year = x[1]
    station = x[3]

    finalfile = "MCM_"+year+"_"+station+".csv"
    
    fraw = open(csvdir+'/'+rawfile)
    fout = open(finaldir+"/"+finalfile,'wb')
    
    #write header
    fout.write("# CTD data for McMurdo Sound\n")
    fout.write("# PIs: Kim and Daly\n")
    fout.write("#  data version: 06 Feb 2017\n")
    fout.write("#   year: "+year+" station: "+station+'\n')
    
    
    #fout = open(csvdir+'/'+)
    fileheader = []
    for origline in fraw:
        linecount =linecount+1
        
        origline = re.sub('^"','',origline) #get rid of some comment lines that have " in front due to ,s in line
        if (  not re.search(startread,origline)  ) and dataflag is False: #means haven't gotten to header yet
            #print origline
            #capture header info and get the seabird name for the params
            if re.search('^# name',origline):
                #print origline+'\n'
                x = re.split("= |:",origline)
                if re.search('"',x[2]): #had comma in content
                    x2 = re.split('"',x[2])
                    
                else:
                    x2 = re.split(',',x[2])
                
                definition = x2[0] 
                sbename = x[1]
                sbename = re.sub("\/|-",'_',sbename)
                sbename = re.sub("\xc3\xa9","e",sbename) #looks like cap A with tilda and then the copyright symbol
               # print sbename+' = '+definition
                fileheader.append(sbename)
                if sbename not in allparams: #need all in a master varlist
                    allparams.append(sbename)
                # name 2 = timeS: Time, Elapsed [seconds]
            continue
        elif dataflag is False: #means you are on header so write it to file
            #then still in header
            #setHeaderline(origline)
            dataflag = True #write all lines starting here
            #print "file header:"+origline+"\n"
            
            #v0 is in there twise so rename second 
            hline = ",".join(fileheader)
            hline = re.sub('v0,v0','v0,v0_dup',hline)
            fout.write(hline+"\n")
                             
        # FOR LINES GOING TO FINAL FILE                             
        if dataflag is True:
            if re.search("Scan|Voltage",origline):
                origline = "# "+origline
                fout.write(origline)
                continue
            
            dlist = re.sub('\n','',origline).split(",")
            #some lines had extra 0.0 value at end so show me them and put original with # and then take off last val
            if len(dlist) == len(fileheader): #then normal, write it
                fout.write(origline)
            else:
                print "BAD LINE: "+origline
                '''
                #troubleshooting line mismatches
                count = 0
                print dlist[0:len(fileheader)]
                print ",".join(dlist[0:len(fileheader)])
                for d in dlist:
                    print fileheader[count]+'='+d
                    count = count+1
                '''
                fout.write("# "+origline)
                fout.write(",".join(dlist[0:len(fileheader)])+'\n')#write up to the last variable in header
            
        
    fraw.close()
    fout.close()
print ','.join(allparams)
print("DONE!")