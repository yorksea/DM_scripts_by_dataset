from dmtools import *

# first convert all xls to csv (files based on original name
# input folder, output folder (doesn't have to exist, it will be made)
XLS2CSV_byFolder("Z:/daly/McMurdoPredPrey/CTD/data/","Z:/daly/McMurdoPredPrey/CTD/csv/")


#now do some extraction from raw csv output
addLines = '''\
# CTD data
# PIs: Stacy Kim and Kendra Daly
#    Version 04 Jan 2017
'''