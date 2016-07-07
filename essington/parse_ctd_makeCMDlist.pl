#!/usr/bin/perl

#print "Parsing CTD xlsx files...\n";


$ctdDIR = '../ctds_xlsx';
$scriptdir = "/cygdrive/c/Users/Amber/Documents/BCODMO/essington_Hypoxia/scripts"; #../scripts

opendir(DIR,"$ctdDIR");
@dirs = sort grep(/Cruise/,readdir(DIR));
closedir(DIR);

$filecount = 0;
foreach $dir(@dirs){
	#print " Entering Directory $dir\n";


	opendir(DIR,"../ctds_xlsx/$dir");
	@files = sort grep(/xlsx$/,readdir(DIR));
	closedir(DIR);
	
	foreach $file(@files){
		$filecount += 1;
		$csvname = $file;
		$csvname =~ s/xlsx/csv/;
		#print "   $file\n";
		
		$sourcedir ='C:\Users\Amber\Documents\BCODMO\essington_Hypoxia\all';
		$sourcedir =~ s/ /\\\\/g;
		$outdir = $sourcedir;
		$outdir =~ s/xlsx/csv/;
		
		$outfile = $file;
		$outfile =~ s/xlsx/csv/g;
		
		#print 'XlsToCsv.vbs oxia\ctds_xlsx\$dir\$file C:\Users\Amber\Documents\BCODMO\essington_Hypoxia\ctds_csv\$file\n";
		#this works from cmd
		#C:\Users\Amber\Documents\BCODMO\essington_Hypoxia\scripts>XlsToCsv.vbs C:\Users\Amber\Documents\BCODMO\essington_Hypoxia\scripts\test.xlsx test.csv
		#`cd $scriptdir; ./XlsToCsv.vbs $sourcedir\\$file $outdir\\csv\\$outfile`;
		
		print "XlsToCsv.vbs $sourcedir\\$file $outdir\\tab1\\$outfile\n";
	}

}