#!/usr/bin/perl -w
use strict;
###################################################################################################################
# This script reads in a map.uc file specified on the command line and converts it to an _otus.txt file to use    #
# with pick_rep_set.py in QIIME.                                                                                  #
###################################################################################################################

# Check the command line arguments
unless (($#ARGV == 0) && (-r $ARGV[0]))
{
	print STDERR "usage: $0 map.uc\n";
	exit;
}

open( MAP, "<$ARGV[0]" );
open( OUT, ">$ARGV[0]_otus.txt" );

my %hash = ();
while( my $line = <MAP> )
{
	my @cols = split " ", $line;
	my $otun = $cols[$#cols];
	my $seqid = $cols[$#cols - 1];
	if( defined $hash{$otun} )
	{
		push @{ $hash{$otun} }, $seqid;
	}
	else
	{
		$hash{$otun} = [$seqid];
	}
}

my $count = 0;
foreach my $otu (keys %hash)
{
	if( $otu eq "*" )
	{
		next;
	}
	unless ($count == 0)
	{
		print OUT "\n";
	}
	print OUT "$otu";
	foreach my $key (@{ $hash{$otu} })
	{
		print OUT "\t" . $key;
	}
	++$count;
}

close(MAP);
close(OUT);
