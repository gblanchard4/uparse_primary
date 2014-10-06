#! /usr/bin/env python

__author__ = "Gene Blanchard"
__email__ = "me@geneblanchard.com"
__version__ = "1.5"

# Imports
#~~~~~~~~~~~~~~~~~~~~~~
import argparse
import os
import commands
import subprocess
import sys
import distutils.spawn

'''
Uparse primary analysis script

Steps

'''

def main():


	
	# Parameters
	#~~~~~~~~~~~~~~~~~~~~~~

	#Create the option parser
	parser = argparse.ArgumentParser(description='Run a primary analysis on the raw fastqs')

	#input_dir -i --input
	parser.add_argument("-i", "--input", type="string", dest="input_dir", help="The directory containing the fastqs you want to analize", required=True)
	#output_dir -o --output
	parser.add_argument("-o", "--output",  type="string", dest="output_dir", help="The directory to write the results to", required=True)
	#merge_truncqual --merge_truncqual
	parser.add_argument("--merge_truncqual", type="string", dest="merge_truncqual", help="Truncate the forward and reverse reads at the first Q<=q,  if present. This truncation is performed before aligning the pair. With Illumina paired reads, it is recommended to use -fastq_truncqual 2 , as low-quality tails will otherwise often cause alignment of the pair to fail. Default: no quality truncation.", required=True)
	#filter_truncqual --filter_truncqual
	parser.add_argument("--filter_truncqual", type="string", dest="filter_truncqual", help="Truncate the read at the first position having quality score <= N, so that all remaining Q scores are >N.", required=True)
	#filter_trunclen --filter_trunclen
	parser.add_argument("--filter_trunclen", type="string", dest="filter_trunclen", help="Truncate sequences at the L'th base. If the sequence is shorter than L, discard.", required=True)
	# Parse arguments
	args = parser.parse_args()

	#Set variables from command line args
	input_dir = args.input_dir
	output_dir = args.output_dir
	merge_truncqual = args.merge_truncqual
	filter_truncqual = args.filter_truncqual
	filter_trunclen = args.filter_trunclen
	



	#~~~~~~~~~~~~~~~~~~~~~~
	# Error checking
	#~~~~~~~~~~~~~~~~~~~~~~

	ERROR = False
	# Make sure all parameters are entered

	

	try:
		subprocess.Popen("print_qiime_config.py", stdout=open(os.devnull, 'w') ) 	
	except OSError:
		print "ERROR: Qiime is not loaded into your path\n"
		ERROR = True

	if input_dir == None:
		print 'ERROR: You need to enter an input directory\n'
		ERROR = True
	else:
		input_dir = os.path.abspath(input_dir)+'/'

	if output_dir == None:
		print 'ERROR: You need to enter an output directory\n'
		ERROR = True
	else:
		output_dir = os.path.abspath(output_dir)+'/'

	if merge_truncqual == None:
		print 'ERROR: You need to enter a --merge_truncqual value\n'
		ERROR = True

	if filter_truncqual == None:
		print 'ERROR: You need to enter a --filter_truncqual value\n'
		ERROR = True

	if filter_trunclen == None:
		print 'ERROR: You need to enter a --filter_trunclen value\n'
		ERROR = True

	# Check if the output directory exists
	if not output_dir == None:
		if not os.path.exists(output_dir):
			os.makedirs(output_dir)

	# Check if usearch7 is in the path
	if not commands.getstatusoutput('usearch7')[0] == 0:
		print 'ERROR: Check if usearch7 is in the path\n'
		print '\t Try the typing qiime18 to put it in the path\n'
		ERROR = True

	# Check if Qiime is in the path
	if not commands.getstatusoutput('print_qiime_config.py')[0] == 0:
		print 'ERROR: Check if Qiime is in the path\n'
		print '\t Try the typing qiime18 to put it in the path\n'
		ERROR = True

	# Quit on error
	if ERROR == True:
		print "\n Errors found: Use the -h option for more information"
		sys.exit()


	bin_dir =  '/'.join(distutils.spawn.find_executable('uparse_primary.py').split('/')[:-1])


	#~~~~~~~~~~~~~~~~~~~~~~
	# Command Builder
	#~~~~~~~~~~~~~~~~~~~~~~
	command_list = []

	# Output Directories
	merged_dir = output_dir+'merged'
	filtered_dir = output_dir+'filtered'
	pynast_dir = output_dir+'pynast_aligned/'

	# Merge
	merge_command = merge_reads(bin_dir, input_dir, merged_dir, merge_truncqual)
	command_list.append(merge_command)

	# Filter
	filter_command = filter_reads(bin_dir, merged_dir, filtered_dir, filter_truncqual, filter_trunclen)
	command_list.append(filter_command)

	# Cat the fastas together to create an FNA
	cat_filtered_command = "cat %s/*.fasta > %sfiltered.fna" % (filtered_dir, output_dir)
	command_list.append(cat_filtered_command)

	# Derep seqs
	derep_seqs_command = "derep_seqs.py -i %sfiltered.fna" % (output_dir)
	command_list.append(derep_seqs_command)

	# Sort by size
	sort_command = "usearch7 -sortbysize %sderep_filtered.fna -output %ssorted_derep_filtered.fna -minsize 2" % (output_dir, output_dir)
	command_list.append(sort_command)

	# Xton counter
	xton_command = "crouton.py -i %sderep_filtered.fna -o %s -n 10" % (output_dir, output_dir)
	command_list.append(xton_command)
	
	# Cluster
	cluster_command = "usearch7 -cluster_otus %ssorted_derep_filtered.fna -otus %sotus.fasta" % (output_dir, output_dir)
	command_list.append(cluster_command)

	# Chimera
	chimera_command = "usearch7 -uchime_ref %sotus.fasta -db %s/gold.fa -strand plus -nonchimeras %snon_chimeric_otus.fna" % (output_dir, bin_dir, output_dir)
	command_list.append(chimera_command)

	# Fasta number
	renumber_command = "fasta_number.py %snon_chimeric_otus.fna > %srenum_non_chimeric_otus.fna" % (output_dir, output_dir)
	command_list.append(renumber_command)

	# Usearch global
	usearch_global_command = "usearch7 -usearch_global %sfiltered.fna -db %srenum_non_chimeric_otus.fna -strand plus -id 0.97 -uc %smap.uc" % (output_dir, output_dir, output_dir)
	command_list.append(usearch_global_command)

	# Map UC to OTUs
	mapuc2otus_command = "mapuc2otustxt.pl %smap.uc" % (output_dir)
	command_list.append(mapuc2otus_command)

	# Pick rep set
	pick_rep_set_command = "pick_rep_set.py -i %smap.uc_otus.txt -f %sfiltered.fna" % (output_dir, output_dir)
	command_list.append(pick_rep_set_command)

	# Align Seqs
	align_seqs_command = "align_seqs.py -i %sfiltered.fna_rep_set.fasta -o %s" % (output_dir, pynast_dir)
	command_list.append(align_seqs_command)

	# Assign taxa
	assign_taxa_command = "assign_taxonomy.py -i %sfiltered.fna_rep_set_aligned.fasta -m rdp -o %srdp_assigned_taxonomy/" % (pynast_dir, output_dir)
	command_list.append(assign_taxa_command)
	
	# Filter alignment
	filter_alignment_command = "filter_alignment.py -i %sfiltered.fna_rep_set_aligned.fasta -o %s" % (pynast_dir, pynast_dir)
	command_list.append(filter_alignment_command)
	
	# Make Phylogony
	tree_command = "make_phylogeny.py -i %sfiltered.fna_rep_set_aligned_pfiltered.fasta" % (pynast_dir)
	command_list.append(tree_command)
	
	# Make OTU 
	otu_command = "make_otu_table.py -i %smap.uc_otus.txt -o %sotus.biom -t %srdp_assigned_taxonomy/filtered.fna_rep_set_aligned_tax_assignments.txt" % (output_dir, output_dir, output_dir)
	command_list.append(otu_command)

	stdout_file =  output_dir+'uparse_primary_stdout.txt'
	stderr_file =  output_dir+'uparse_primary_stderr.txt'
	shell_file =  output_dir+'uparse_primary.sh'
	with open(shell_file, 'wb') as shell:
		with open(stdout_file, 'wb') as stdout:
			with open(stderr_file, 'wb') as stderr:low-quality
				for command in command_list:
					try:	
						shell.write(command+'\n')
						proc = subprocess.Popen(command, shell=True, stdout=stdout, stderr=stderr)
						proc.wait()
					except OSError:
						print 'BROKE'


def merge_reads(bin_dir, input_dir, output_dir, truncqual):
	command = "uparse_batch_merge.py -i %s -o %s --fastq_truncqual %s" % (input_dir, output_dir, truncqual)
	return command

def filter_reads(bin_dir, input_dir, output_dir, truncqual, trunclen):
	command = "uparse_batch_filter.py -i %s -o %s --fastq_truncqual %s --fastq_trunclen %s " % (input_dir, output_dir, truncqual, trunclen)
	return command


if __name__ == '__main__':
	main()
