Amber York 9 Jun 2016 scripts version 2 (in /scripts dir)
* for Essington's PelagicHypoxia, "bcodmo link":http://www.bco-dmo.org/dataset/648914
----------------------------------------------------
"parse_ctd_makeCMDlist.pl":parse_ctd_makeCMDlist.pl
* IN: directory of xls files
* OUT: cmd.txt , cmds_tab2.txt, cmds_tab3.txt
* I executed in cygwin on windows

Takes a folder full of xlsx files and produces a text file full of commands to convert them to csv.
* xlsx files used are under intermediate_data/orig
----------------------------------------------------
then in windows terminal I did @ cmd < cmd.txt @

to execute the commands in the file

* this called "XlsToCsv.vbs":XlsToCsv.vbs sourcefilepath sourcefilename for each of the xlsx files
** created csvs of each tab are in:
intermediate_data/tab1
intermediate_data/tab2
intermediate_data/tab3

Only two files had a third tab (DO corrections for one, not sure what the values are in the other).

----------------------------------------------------
"parse_ctd_toplevel.pl":parse_ctd_toplevel.pl

Usage: @perl parse_ctd_toplevel.pl 0@

* IN: directory of csv files (intermediate_data/tab2)
* OUT: hypoxia_toplevel.dat which grabs values from tab2 data
** also outputs comments and header to toplevel
* the 0 during execution just means don't display stuff(I used 1 during development)
* I executed in cygwin on windows

----------------------------------------------------
-----XlsToCsv----
Got the base of the XlsToCsv vbs scripts from "stackoverflow here":http://stackoverflow.com/questions/1858195/convert-xls-to-csv-on-command-line and modified as necessary for tab2/3:


Modificaitons:
* took out Done messages
* changed to export tabs 1-3 instead of just one tab
* changed input arguments to support above
* added if for only exporting tab 3 when there was one (to preven hundreds of error messages for all that didn't)

----------------------------------------------------
previous versions:
* scripts v1 folder contains scripts before supporting all tabs export and does not have the dat file creation.
current version:
* cruise_id  source changed. version v1 had errors as it wasn't consistant with name and in file two cruise names were sometimes listed.  This is fixed.
* added correct header for toplevel file. With delimeter before > in param name list.
* changed first lat lon in toplevel file to latitude and longitude as it is also a column in the data files.
