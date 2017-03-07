import re,os,json,sys
import pandas as pd

# used for dataset https://www.bco-dmo.org/dataset/682966
datadir = 'Z:\lasker\StJohn_octocorals'
out_file = open(os.path.join(datadir,'octo_transects2.csv'),'wb')
# script to add spcies names from species list

#species list 
f_sp = f = open(os.path.join(datadir,'species_list.csv'))

#main data
f_in = open(os.path.join(datadir,'adult_survey.csv'))

# make species dictionary
sp_dict = {}
for line in f_sp:
    (code,sp) = line.rstrip().split(',')
    sp_dict[code] = sp


print sp_dict

for line in f_in:
    line = line.rstrip()
    if re.search("\#|year",line):
        out_file.write(line+'\n')
        continue
    code_in_data =  line.split(',')[8].rstrip()

    if code_in_data in sp_dict:
        print line+','+sp_dict[code_in_data]
        out_file.write(sp_dict[code_in_data]+','+line+'\n')
    else:
        print "NO CODE: " + line
        out_file.write('nd,'+line+'\n')
        
        
f_sp.close()   
out_file.close()    
f_in.close()             