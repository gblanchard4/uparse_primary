#! /usr/bin/python

__author__ = "Gene Blanchard"
__email__ = "me@geneblanchard.com"

'''
Uparse merge reads batch script

Example command:
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
	parser.add_option("-i", "--input", action="store", type="string", dest="input_dir", help="The directory containing the fastqs you want to merge")

	#output_dir -o --output
	parser.add_option("-o", "--output", action="store", type="string", dest="output_dir", help="The directory to write the merged results to ")

	#fastq_minovlen --fastq_minovlen
	parser.add_option("--fastq_minovlen", action="store", type="string", dest="fastq_minovlen", help="Minimum length of the overlap. Default: no minimum")

	#fastq_minmergelen --fastq_minmergelen
	parser.add_option("--fastq_minmergelen", action="store", type="string", dest="fastq_minmergelen", help="Minimum length of the merged read. Default: no minimum")

	#fastq_maxmergelen --fastq_maxmergelen
	parser.add_option("--fastq_maxmergelen", action="store", type="string", dest="fastq_maxmergelen", help="Maximum length of the merged read. Default: no maximum")

	#fastq_maxdiffs --fastq_maxdiffs
	parser.add_option("--fastq_maxdiffs", action="store", type="string", dest="fastq_maxdiffs", help="Maximum number of mismatches allowed in the overlap region. Default: any number of mismatches allowed")

	#fastq_truncqual --fastq_truncqual
	parser.add_option("--fastq_truncqual", action="store", type="string", dest="fastq_truncqual", help="Truncate the forward and reverse reads at the first Q<=q,  if present. This truncation is performed before aligning the pair. With Illumina paired reads, it is recommended to use -fastq_truncqual 2 , as low-quality tails will otherwise often cause alignment of the pair to fail. Default: no quality truncation.")

	#fastq_minlen --fastq_minlen
	parser.add_option("--fastq_minlen", action="store", type="string", dest="fastq_minlen", help="Minimum length of the forward and reverse read, after truncating per  -fastq_truncqual if applicable. Default: no minimum")

	#fastq_minovlen --fastq_minovlen
	parser.add_option("--fastq_allowmergestagger", action="store_true", dest="fastq_allowmergestagger", help="Allow merge of a pair where the alignment is 'staggered'")



	#Grab command line options
	(options, args) = parser.parse_args()

	#Set variables from command line options
	input_dir = options.input_dir.rstrip('/')+'/'
	output_dir = options.output_dir.rstrip('/')+'/'
	fastq_minovlen = options.fastq_minovlen
	fastq_minmergelen = options.fastq_minmergelen
	fastq_maxmergelen = options.fastq_maxmergelen
	fastq_maxdiffs = options.fastq_maxdiffs
	fastq_truncqual = options.fastq_truncqual
	fastq_minlen = options.fastq_minlen
	fastq_allowmergestagger = options.fastq_allowmergestagger

	#~~~~~~~~~~~~~~~~~~~~~~
	# Error checking
	#~~~~~~~~~~~~~~~~~~~~~~

	ERROR = False
	# Make sure all parameters are entered
	if input_dir == None:
		print 'ERROR: You need to enter an input directory\n\tUse the -h option for more information'
		sys.exit()
		ERROR = True

	if  output_dir== None:
		print 'ERROR: You need to enter an output directory\n\tUse the -h option for more information'
		sys.exit()
		ERROR = True

	# Check if the input directory exists
	if not os.path.isdir(input_dir):
		print 'ERROR: %s is not a valid input_dir' % input_dir
		ERROR = True

	# Check if usearch7 is in the pathPy
	if not commands.getstatusoutput('usearch7')[0] == 0:
		print 'ERROR: Check if usearch7 is in the path'
		print '\t Try the typing qiime to put it in the path'
		ERROR = True

	# Check if the output directory exists
	if not output_dir == None:
		if not os.path.exists(output_dir):
			os.makedirs(output_dir)
			
	# Quit on error
	if ERROR == True:
		sys.exit()

	# Create a list of files from the input directory
	fileset = set([file.split('_L001_')[0] for file in os.listdir(input_dir)])
	command_list = []
	# Commmand_builder
	for filename in fileset:
		r1 = input_dir+filename+'_L001_R1_001.fastq'
		r2 = input_dir+filename+'_L001_R2_001.fastq'
		output_file =  output_dir+filename

		echo = "echo 'File:\t%s' >&2 " % filename
		command = "usearch7 -fastq_mergepairs %s -reverse %s -fastqout %s_merged.fastq" % (r1, r2, output_file)

		# Append options
		if not fastq_minovlen == None:
			comand =  command+" -fastq_minovlen %s" % fastq_minovlen
		if not fastq_minmergelen == None:
			command = command+" -fastq_minmergelen %s" % fastq_minmergelen
		if not fastq_maxmergelen == None:
			command = command+" -fastq_maxmergelen %s" % fastq_maxmergelen
		if not fastq_maxdiffs == None:
			command = command+" -fastq_maxdiffs %s" % fastq_maxdiffs
		if not fastq_truncqual == None:
			command = command+" -fastq_truncqual %s" % fastq_truncqual
		if not fastq_minlen == None:
			command = command+" -fastq_minlen %s" % fastq_minlen
		if not fastq_allowmergestagger == None:
			command = command+" -fastq_allowmergestagger %s" % fastq_allowmergestagger

		command_list.append(echo)
		command_list.append(command)

	# Run the commands and write the stderr log out
	logfile =  output_dir+'merge.log'
	with open(logfile, 'wb') as err:
		for command in command_list:
			try:
				proc = subprocess.Popen(command, shell=True, stderr=err)
				proc.wait()
			except OSError:
				print 'BROKE'

	statsfile = output_dir+'stats.txt'
	with open(statsfile, 'w') as stats:
		with open(logfile, 'r') as log:
			reader =  log.read()
		header = "Sample\tPairs\tConverted\tExactOverlaps\tNotAligned\tGaps\tMismatches\tFwdErrs\tRevErrs\tStaggered"
		stats.write(header)
		for i, part in enumerate(reader.split("File:\t")):
			if not part == '': 
				line = '\n'
				for e in part.split('\n'):
					if not e.startswith('00:'):
						value = e.strip().split('  ')[0]+'\t'
						line = line+value
				stats.write(line)

if __name__ == '__main__':
	main()