import re,os,json,sys
import pandas as pd

'''
DM: Amber York
date: 08 Feb 2017
This script takes large deployment data files and splits them into subfiles with toplevel file
* this way site locations and lat lons can go in toplevel and group by site when serving

'''
from datetime import date

outdir = "data_by_site/"
origfiles = os.listdir('orig/') #run from same dir


bysite = {} #
    

for origfile in origfiles:
    
    if not re.search('^g',origfile): #only galapagos files
            continue
        
    
    print origfile
    deployment = origfile
    deployment  = re.sub(".csv","",deployment)
    deployment  = re.sub(".*_2","2",deployment)
    deployment = re.sub("(-|to)","_",deployment)
    
        
    f = open("orig/"+origfile)
    for line in f:
        
        if re.search('temp',line):#skip it is a header
            continue
        
        line = re.sub('\"','',line)

        if re.search(' - ',line):
            line = re.sub(' - ',',',line)

        line = re.sub(' m",| m,',',',line)
        line = re.sub('NA','nd',line)
               
        dlist = line.rstrip().split(',')
        #print line
        #print dlist              

        
        if len(dlist) == 4: #then no time, just date
            
            x = dlist[0].split(' ')#some first columns have date\stime some just have date
            date = x[0]
            if len(x) > 1:
                time = x[1]
            else:
                time = 'nd'
            
            site = dlist[1]
            depth = dlist[2]
            temp = dlist[3]

        depth = re.sub('( )m','',depth)
        site = re.sub(" ","_",site)
        outname = deployment+"-"+depth+"m"
        outline = [date,time,temp]
        
        #see if this site exists in dictonary
        if site not in bysite:
            bysite[site] = {}
            
        #print lines list to dictionary
        if outname in bysite[site]:                
            bysite[site][outname].append(",".join(outline))
        else:
            #initialize it first 
            print "   "+site+" " +outname
            bysite[site][outname] = []
            bysite[site][outname].append('date,time,temp')

# now write everything to site/deployment
topf_level0 = open("level0_sites.dat","wb")
topf_level0.write("site,>\n")
topf_level0.write("deployment,depth,>\n")
topf_level0.write("date,time,temp\n")


for site in sorted(bysite.iterkeys()):

    level1name = "level1_site_"+site+".dat"
    topf_level1 = open(outdir+level1name,"wb")
    topf_level1.write("deployment,depth,>\n")
    topf_level1.write("date,time,temp\n")

    #write to level0 topfile
    topf_level0.write(site+","+outdir+level1name+"\n")        
            
    print "writing toplevel for site "+site
    for outname in sorted(bysite[site].iterkeys()):
        level2name ="level2_"+site+"-"+outname+'.csv'
        (deployment,depth) = outname.split('-')
        depth = re.sub('m','',depth)
        
        #write to level1 topfile
        topf_level1.write(deployment+","+depth+","+level2name+"\n")
        print "writing toplevel for deployment "+outname
        fout = open(outdir+level2name,'wb')
        fout.write('\n'.join(bysite[site][outname]))
        fout.close()
    

    topf_level1.close()
topf_level0.close()

#-------now by site-------------
# now write everything to site/deployment
topf = open("./temp_by_site_toplevel.dat","wb")
topf.write("site,deployment,depth,>\n")
topf.write("date,time,temp\n")




print "DONE!\n"                