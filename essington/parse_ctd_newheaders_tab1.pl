#!/usr/bin/perl
# Amber York
# 9 Jun 2015

#TODO
# uncomment header print in OUT
#parse station from filename and add to header


#flag to show all raw line parts as in file
$printparts = $ARGV[0];

print "stripping headers from csvs and adding new...\n";

push @comments , "# Pelagic hypoxia CTD data";
push @comments , "#   T. Essington, P.I.";
push @comments , "#   Version 9 Jun 2016";
#fills in cruise when writting comment
#fills in station when writting comment

$newheader = "density,depth,fluor,lat,lon,O2_raw,O2_sbe43,O2sat_GG,O2sat_Weiss,PAR,pH,sal,sv_Delgross,temp,dummy0,dummy1,dummy2,dummy3,dummy4,dummy5,dummy6,dummy7,dummy8,potemp,press,press_psi,sv_chen,sv_wilson,dummy9,dummy10,dummy11,dummy12,dummy13,dummy14,dummy15,dummy16,dummy17,flag";

$ctdDIR = '../datafiles'; #where the csvs live
$scriptdir = "../scripts"; #../scripts

$filecount = 0; #make sure there are the expeced 113

opendir(DIR,"$ctdDIR/tab1");
@files = sort grep(/csv$/,readdir(DIR));
closedir(DIR);

foreach $file(@files){
	$ctdname = $file;
	$ctdname =~ s/\.c.*//;
	
	$filecount += 1;
	
	#file to write to:
	open(OUT,">$ctdDIR/dat/$ctdname\.dat");
	
	$station = '';
	foreach $comment(@comments){
			print OUT "$comment\n";		
	}
	
	#add station and cruise to header
		#get station from filename
	## add station by stripping cruise from ctdname
	$ctdname =~ /^(\D*\d*)/;
	$cruise = $1;
	$station = $ctdname;
	$station =~ s/$cruise//i; #remove cruise from filename
	
	print OUT "#    Cruise: $cruise\n";	
	print OUT "#    Station: $station\n";
	
			
	print "$file $station\n";
	print OUT "$newheader\n"; #print new header when not TBD

	open(TAB1,"$ctdDIR/tab1/$file");
	@lines = <TAB1>;
	close(TAB1);
	
	$linecount = 1;
	foreach $line(@lines){

		$line =~ s/(\r|\n)//g;
		
		#find non-data lines
		if ($line =~ /(^#|ALIGNED|^\D)/){
			#print "OLDHEADER: $file [$line]\n";
			print OUT "# $line\n";
		} else {
			#print the data lines
		#	print "$file [$line]\n";
			print OUT "$line\n";
		}


		$linecount+=1;
	} #line loop

	close(OUT);#dat file
	
} #file loop

