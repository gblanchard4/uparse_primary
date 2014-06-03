#!/usr/bin/env python

from optparse import OptionParser
import subprocess
import matplotlib.pyplot as plt
import os

__author__ = "Gene Blanchard"
__email__ = "me@geneblanchard.com"

'''
Count singletons and n-tons to see the total distribution
'''
def main():

	#Create the argument parser
	parser = OptionParser(usage="Usage: ")

	# input file
	# -i --input
	parser.add_option("-i", "--input", action="store", type="string", dest="input", help="The dereped filtered fasta to input")

	#  xton number
	# -n --number
	parser.add_option("-n", "--number", action="store", type="string", dest="number", help="The number of xtons to go count up to")

	#  output png
	# -o --output
	parser.add_option("-o", "--output", action="store", type="string", dest="output", help="The location to write the output file to")

	# Grab command line args
	(options, args) = parser.parse_args()

	# Set argument values
	input_name = options.input
	xton_number =  int(options.number)
	xton_range = range(1,xton_number+1)
	output_path =  options.output

	output_path = os.path.abspath(output_path)

	fasta_total = 0
	with open(input_name, 'r') as fasta:
		for line in fasta:
			if line.startswith('>'):
				line_value = int(line.split('=')[1].split(';\n')[0])
				fasta_total =  fasta_total + line_value

	x_axis = []
	y_axis = []
	percent = []

	with open(input_name, 'r') as fasta:
		for n in xton_range:
			n_command =  "less %s | grep ';size=%s;' | wc -l" % (input_name, n)
			n_result = int(subprocess.check_output([n_command], shell="True").rstrip())
			n_total = int(n * n_result)
			n_percent = round(n_total / float(fasta_total) * 100, 2)
			
			# plotting
			x_axis.append(n)
			y_axis.append(n_total)
			percent.append(n_percent)


			#print "%s\t%s\t%s\t%s" % (n, n_result, n_total, n_percent)

	plt.plot(x_axis, y_axis)
	for index,point in enumerate(percent):
		plt.annotate( str(point)+'%', xy=(x_axis[index], y_axis[index]) )
	
	#plt.show()
	path = '/'.join(os.path.abspath(input_name).split('/')[:-1])+'/'
	filename = 'derep_'+os.path.abspath(input_name).split('/')[-1]
	plot_name = path+filename+'.png'
	print "Saving file as %s" % plot_name
	plt.savefig(plot_name)


if __name__ == '__main__':
	main()
