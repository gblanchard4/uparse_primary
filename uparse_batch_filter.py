#! /usr/bin/env python

__author__ = "Gene Blanchard"
__email__ = "me@geneblanchard.com"

'''
Uparse filtering batch script

Example command:
usearch7 -fastq_filter BKCHOW_S155_L001_R1_001.fastq -fastaout BKCHOW_S155_L001_R1_001.uparse_filtered.fasta -relabel BKCHOW_ -fastq_truncqual 15 -fastq_trunclen 250 2>>loguparsefilter.txt
'''

def main():
	#~~~~~~~~~~~~~~~~~~~~~~
	# Imports
	#~~~~~~~~~~~~~~~~~~~~~~
	from optparse import OptionParser
	import os
	import commands
	import subprocess
	import sys

	#~~~~~~~~~~~~~~~~~~~~~~
	# Parameters
	#~~~~~~~~~~~~~~~~~~~~~~

	#Create the option parser
	parser = OptionParser()

	#input_dir -i --input
	parser.add_option("-i", "--input", action="store", type="string", dest="input_dir", help="The directory containing the fastqs you want to filter")

	#output_dir -o --output
	parser.add_option("-o", "--output", action="store", type="string", dest="output_dir", help="The directory to store the created files ")

	#--fastq_truncqual
	parser.add_option("--fastq_truncqual", action="store", type="string", dest="fastq_truncqual", help="Truncate the read at the first position having quality score <= N, so that all remaining Q scores are >N.")

	#--fastq_trunclen
	parser.add_option("--fastq_trunclen", action="store", type="string", dest="fastq_trunclen", help="Truncate sequences at the L'th base. If the sequence is shorter than L, discard.")

	#forward read only --forward
	parser.add_option("--forward", action="store_true", dest="forward", default=False, help="Use only the forward reads *_R1_*")

	#Grab command line options
	(options, args) = parser.parse_args()

	#Set variables from command line options
	input_dir = options.input_dir.rstrip('/')+'/'
	output_dir = options.output_dir.rstrip('/')+'/'
	fastq_truncqual = options.fastq_truncqual
	fastq_trunclen = options.fastq_trunclen
	forward = options.forward

	#~~~~~~~~~~~~~~~~~~~~~~
	# Error checking
	#~~~~~~~~~~~~~~~~~~~~~~

	ERROR = False
	# Make sure all parameters are entered
	if input_dir == None:
		print 'ERROR: You need to enter an input directory\n\tUse the -h option for more information'
		sys.exit()
		ERROR = True

	if output_dir == None:
		print 'ERROR: You need to enter an output directory\n\tUse the -h option for more information'
		sys.exit()
		ERROR = True

	# Check if the input directory exists
	if not os.path.isdir(input_dir):
		print 'ERROR: %s is not a valid input_dir. Directory does not exist.' % input_dir
		ERROR = True

	# Check if usearch7 is in the path
	if not commands.getstatusoutput('usearch7')[0] == 0:
		print 'ERROR: Check if usearch7 is in the path'
		print '\t Try the typing qiime18 to put it in the path'
		ERROR = True

	# Check if the output directory exists
	if not output_dir == None:
		if not os.path.exists(output_dir):
			os.makedirs(output_dir)

	# Quit on error
	if ERROR == True:
		sys.exit()

	# Create a list of files from the input directory
	file_list = os.listdir(input_dir)
	command_list = []
	# Commmand_builder
	for filename in file_list:
		if filename.endswith('.fastq'):
			if not forward:
				fastq = input_dir+filename
				output_file =  output_dir+filename.split('.fastq')[0]+'.fasta'
				label = filename.split('_')[0]

				echo = "echo 'File:\t%s' >&2 " % fastq
				command = "usearch7 -fastq_filter %s -fastaout %s -relabel %s_" % (fastq, output_file, label)

				# Append options
				if not fastq_truncqual == None:
					command =  command+" -fastq_truncqual %s" % fastq_truncqual
				if not fastq_trunclen == None:
					command = command+" -fastq_trunclen %s" % fastq_trunclen

				command_list.append(echo)
				command_list.append(command)
			elif forward:
				if '_R1_' in filename:
					fastq = input_dir+filename
					output_file =  output_dir+filename
					label = filename.split('_')[0]

					echo = "echo 'File:\t%s' >&2 " % fastq
					command = "usearch7 -fastq_filter %s -fastaout -relabel %s_" % (fastq, output_file, label)

					# Append options
					if not fastq_truncqual == None:
						print "holla!"
						comand =  command+" -fastq_truncqual %s" % fastq_truncqual

					if not fastq_trunclen == None:
						command = command+" -fastq_trunclen %s" % fastq_trunclen
					
					command_list.append(echo)
					command_list.append(command)

	# Run the commands and write the stderr log out
	logfile =  output_dir+'filter.log'
	with open(logfile, 'wb') as err:
		for command in command_list:
			try:
				proc = subprocess.Popen(command, shell=True, stderr=err)
				proc.wait()
			except OSError:
				print 'FUQ'

if __name__ == '__main__':
	main()
