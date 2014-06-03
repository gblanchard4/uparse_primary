#! /usr/bin/env python

from optparse import OptionParser
import numpy

__author__ = "Gene Blanchard"
__email__ = "me@geneblanchard.com"

'''
Fasta Sequence Length Counter
'''

def fasta(input_file):
	length_dict = dict()
	with open(input_file) as fasta:
		for line in fasta:
			if not line.startswith('>'):
				length = len(line)
				if length not in length_dict:
					length_dict[length] = 0
				length_dict[length] += 1
	return length_dict

def fastq(input_file):
	length_dict = dict()
	seqs = range(1,file_len(input_file), 4)
	with open(input_file) as fastq:
		line_list = fastq.readlines()
		for index in seqs:
			line = line_list[index]
			length = len(line.rstrip('\n'))
			if length not in length_dict:
				length_dict[length] = 0
			length_dict[length] += 1
	return length_dict


def file_len(fname):
	with open(fname) as f:
		for i, l in enumerate(f):
			pass
	return i + 1




def main():

	#Create the argument parser
	parser = OptionParser(usage="Usage: ")

	#fasta -i --input
	parser.add_option("-i", "--input", action="store", type="string", dest="input", help="The input file")

	# Grab command line args
	(options, args) = parser.parse_args()

	# Arguments passed, assign them to variables
	input_file = options.input

	extension = input_file.split('.')[-1]
	if extension == "fastq":
		lengths = fastq(input_file)
	else:
		lengths = fasta(input_file)

	for length, counter in lengths.items():
		print "%d\t%d" % (length, counter)


	
'''
	print "Minimum:\t%s" % min(length_array)
	print "Maximum:\t%s" % max(length_array)
	print "Average:\t%s" % numpy.mean(length_array)
	print "Length\tCount"  	
'''



if __name__ == '__main__':
	main()
