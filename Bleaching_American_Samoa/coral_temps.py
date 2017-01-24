import os.path
import re,os,sys
import csv

'''
used in directory /data302/palumbi/Bleaching_American_Samoa/scripts/

This file flips the data files so that instead of 
Timestamp temp_colony1 temp_colony2  ... temp_colony N

You get:

deployment_id timestamp colony_id temp 

Can join this with the sample log

'''
   

        
        
origDir = '../working'

print "Extracting data in "+origDir
 
def main():   
    origFiles = os.listdir(origDir)
    fout = open(os.path.join(origDir,'..','final','all_temps.csv'),'w')
    fout.write('deployment_id,date,time,colony_id,temp\n')    
    
    for filename in origFiles:
        if re.search('^~',filename):
            continue
        
        deployment = re.sub('.txt','',filename)
        f = open(os.path.join(origDir,filename))

                
                
        line_count = 0
        for line in f:
            #some newline issues that even dos2unix didn't get
            line = line.rstrip('\n|\r')
            
            print line
            if line_count ==0:
                header = line.split('\t')
                print header
                line_count=line_count+1
                continue
                        
            cols = line.split('\t')
            
            for col_count in range(2, len(cols)):
                        
                date = cols[0]
                time = cols[1]
                #some were AM/PM some 24 hour
                if re.search('AM$|PM$',line):
                    if re.search('PM$',line):
  
                        t = re.sub(':',',',time).split(',')

                        time = str(int(t[0])+12)+':'+t[1]
                        #there can seconds, 12:00:00, some not but always :00 at end so cutting off if present
                
                print header[col_count]+ ' = '+cols[col_count]
                if len(header[col_count]) > 0: #only writes as many values as you have col headers 
                    #this prevents the weird lines with spaces then AM/PM from writing out
                    fout.write(deployment+','+date+','+time+','+header[col_count]+','+cols[col_count]+'\n')
                col_count = col_count+1
            
            line_count = line_count+1
            print('end')
            
            #end line loop
        f.close()
        
        #end file loop
    fout.close()    
if __name__ == '__main__':
    main()
   
