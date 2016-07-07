#!/usr/bin/perl
# Amber York
# 9 Jun 2015

#flag to show all raw line parts as in file
$printparts = $ARGV[0];

print "Parsing CTD xlsx files...\n";


$ctdDIR = '../datafiles';
$scriptdir = "../scripts"; #../scripts

$filecount = 0; #make sure there are the expeced 113

$data_subfolder = "cruise_data"; #will be put in as the relative path to the csv file in the toplevel file

open(TOP,">../hypoxia_toplevel2.dat");

print TOP "# Pelagic hypoxia CTD data\n#   T. Essington, P.I.\n#   Version 10 Jun 2016\n";

print  TOP "cruise_id,station,depth_w,latitude,longitude,time_local,date_local,>\n"; #need delimeter before >
print TOP "press,depth,density,fluor,lat,lon,O2_raw,O2_sbe43,O2sat_GG,O2sat_Weiss,PAR,pH,sal,sv_Delgross,temp,dummy0,dummy1,dummy2,dummy3,dummy4,dummy5,dummy6,dummy7,dummy8,potemp,press_psi,sv_chen,sv_wilson,dummy9,dummy10,dummy11,dummy12,dummy13,dummy14,dummy15,dummy16,dummy17,flag\n";
#will fill hashes with key being ctdname
%depth_w;
%cruise_id;
%lat;
%lon;
%station; #needs to come from filename, is not in file
%station_description; #because that is what the line "Station: ..." has
%time; #from upload timestamp
%date; #from upload timestamp
#and an array of all ctdnames

opendir(DIR,"$ctdDIR/tab1");
@files = sort grep(/csv$/,readdir(DIR));
closedir(DIR);

foreach $file(@files){
	$ctdname = $file;
	$ctdname =~ s/\.c.*//;
	
	$filecount += 1;
	
	if ($printparts){
		print "\n  $filecount $file\n";
	}
	
	if (-e "$ctdDIR/tab2/$file") { 
		#file exists - set variable and other things
	} else {
		print "NO TAB2 for $file\n";
	}
	
	$tab2path = "$ctdDIR/tab2/$file";
	
	#print "Opening $tab2path\n";
	open(TAB2,$tab2path);
	@lines = <TAB2>;
	close(TAB2);
	
	$linecount = 1;
	foreach $line(@lines){

		#remove line returns
		$line =~ s/(\r|\n)//g;
		
		if ($printparts){
			print "		file $filecount line $linecount  $ctdname [$line]\n";
		}
		
		@parts = split(',',$line);
		$partcount = 0;
		foreach $part(@parts){
		
			if ($printparts){
			#if ($printparts | $linecount == 9){
				print "$linecount   $partcount [$part]\n";
			}
			$partcount +=1;
		} #part loop
		## ----------------------------------------------		
		## add cruise_id to hash
		if ($line =~ /Cruise:/){
			#print "$linecount $ctdname $line\n";
			$cruise = $parts[$#parts];
			#if ($cruise =~ /Ref/){
			#	$cruise = $parts[4];
			#}
			$cruise_id{$ctdname} = $cruise;
			

		} elsif($line =~ /Cruise/ & $line !~ /:/){
						$cruise = $parts[2];
			if ($cruise =~ /Ref/){
				$cruise = $parts[4];
			}
			$cruise_id{$ctdname} = $cruise;
		}

		## ----------------------------------------------		
		## add depth_w to hash
		if ($line =~ /Depth:/){
			#value not at same part every file
			# there is one known missing value
			$d = $parts[2];
			if ($d !~ /\d/){ $d = $parts[3];}
			$d =~ s/m//;
			$depth_w{$ctdname} = $d;			
		}		

		## ----------------------------------------------		
		## add time to hash 
		#if ($line =~ /UTC/){
		#	#print "$linecount $ctdname $line\n";
		#	($h,$m,$s) = split(/\:/,$parts[5]);
		#	if (length $h < 2){ $h = "0".$h;}
		#	if (length $m < 2){ $m = "0".$m;}
		#	if (length $s < 2){ $s = "0".$s;}
		#	$time{$ctdname} = "$h:$m:$s";		
		#}			
		
		## ----------------------------------------------		
		## add date time to hash
		if ($line =~ /System,UpLoad,Time,=/){
			#print "FLAG $linecount $ctdname $line\n";			
			
			#split time because needs padding
			($h,$m,$s) = split(/\:/,$parts[8]);
			if (length $h < 2){ $h = "0".$h;}
			if (length $m < 2){ $m = "0".$m;}
			if (length $s < 2){ $s = "0".$s;}
			
			$time{$ctdname} = "$h:$m:$s";	
			$date{$ctdname} = "$parts[6]-$parts[5]-$parts[7]";		
		}			
		
		
		## ----------------------------------------------		
		## add Lat to hash
		if ($line =~ /NMEA,Lat/){
			#print "$linecount $ctdname $line\n";
			
			if ($parts[3] ne '='){
				print STDERR "ERROR: Lat line not aligned in file $file line $linecount\n";
			}
			
			@lparts = ()	;	
			if (length $parts[5] != 5){ 
				# number of digits too small in minutes, need to pad
				#   example 10 cb988UNd *,NMEA,Latitude,=,47,21.8,N,,,,,,,,,,
				#           10 cb982DBn *,NMEA,Latitude,=,47,48.4,N,,,,,,,,,,,,,,,,


				@lparts = split('\.',$parts[5]);
				$min = $lparts[0];
				$min_dec = $lparts[1];
				
				if (length $min < 2){ $min = "0"."$min";}
				if (length $min_dec < 2){ $min_dec = "$min_dec"."0";}
				#print "FLAG $linecount Lat $min $min_dec\n";
				$lat{$ctdname} = "$parts[4]$min\.$min_dec";

			} else {
				$lat{$ctdname} = "$parts[4]$parts[5]";
			}
				
		}
		## ----------------------------------------------
		## add Lon to hash
		if ($line =~ /NMEA,Lon/){
			print "$linecount $ctdname $line\n";
			
			if ($parts[3] ne '='){
				print STDERR "ERROR: Lon line not aligned in file $file line $linecount\n";
			}
			
			@lparts = ();
			if (length $parts[5] != 6){ 
				# number of digits too small in minutes, need to pad
				@lparts = split('\.',$parts[5]);
				$min = $lparts[0];
				$min_dec = $lparts[1];
				#print "$line FLAG $linecount Lon $min $min_dec\n";
				if (length $min < 2){ $min = "0"."$min";}
				if (length $min_dec < 2){ $min_dec = "$min_dec"."0";}
				#print "$line FLAG $linecount Lon $min $min_dec\n";
				$lon{$ctdname} = "$parts[4]$min\.$min_dec";
												
			} else {
				$lon{$ctdname} = "$parts[4]$parts[5]";
			}			
				
			#$lat{$ctdname} = $stationD;	
		}
		## ----------------------------------------------

		$linecount+=1;
	} #line loop

			## add station by stripping cruise from ctdname
			$ctdname =~ /^(\D*\d*)/;
			$remove = $1;
			$s = $ctdname;
			$s =~ s/$remove//i; #works because cruises end in numbers
			$station{$ctdname} = $s;
			#print "FLAG $file station $s name $ctdname cruise $cruise_id{$k}\n";
			
	#lines for toplevel TOP
	$k = $ctdname;
	#header: cruise_id,station,depth_w,lat,lon,time,file\n";
	

	if (length $depth_w{$k} == 0){
		$depth_w{$k} = 'nd';
	}
	print TOP "$cruise_id{$k}\t$station{$k}\t$depth_w{$k}\t$lat{$k}\t$lon{$k}\t$time{$k}\t$date{$k}\t$data_subfolder\/$ctdname\.dat\n";

} #file loop

close(TOP);
#for testing display

	$count = 0;
	%thisHash = %station; #change to test that one
	#%thisHash = %depth_w;
for my $c (keys %thisHash) {
		$count +=1;
	#print "file $count:  $c = [$thisHash{$c}]\n";	

}

