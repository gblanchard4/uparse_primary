#! /usr/bin/env python

from optparse import OptionParser
import numpy
import matplotlib.pyplot as plt
import os

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
	# filetype -f --filetype
	parser.add_option("-f", "--filetype", action="store", type="string", dest="filetype", help="The filetype, fastq/fasta")

	# Grab command line args
	(options, args) = parser.parse_args()

	# Arguments passed, assign them to variables
	input_file = options.input
	filetype = options.filetype

	if filetype == None:
		extension = input_file.split('.')[-1]
	else:
		extension = filetype

	if extension == "fastq":
		lengths = fastq(input_file)
	else:
		lengths = fasta(input_file)

	x_axis = []
	y_axis = []

	path = '/'.join(os.path.abspath(input_file).split('/')[:-1])+'/'

	with open(path+'sequence_lengths.txt', 'w') as len_file:
		for length, counter in lengths.items():
			len_file.write("%d\t%d" % (length, counter))
			x_axis.append(length)
			y_axis.append(counter)

	plt.plot(x_axis, y_axis)
	
	path = '/'.join(os.path.abspath(input_file).split('/')[:-1])+'/'
	filename = 'derep_'+os.path.abspath(input_file).split('/')[-1]
	plot_name = path+filename+'.png'
	plt.savefig(plot_name)



if __name__ == '__main__':
	main()
