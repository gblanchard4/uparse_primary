uparse_primary
==============
Collection Of Scripts to run a uparse primary analysis

# Pipeline Usage
uparse_primary.py -i raw_unzipped_fastqs/ -o primary_q10_l400 --merge_truncqual 2 --filter_truncqual 10 --filter_trunclen 400 


## Standard
We merge the reads with a truncqual value of 2, this will remove any reads with extremely low Q-scores. Our standard practice has been to filter the reads at a trunclen value of 400 (for V3-V4) and truncqual of 10.

### Input  
Input is a directory that contains raw gunzipped fastq files.

### Output  
Output is a biom and tre we can pass to Qiime.

# Helper Scripts
##uparse_batch_merge.py  
Run a `usearch -fastq_mergepairs` command on a directory of fastqs. The standard protocal is to pass a `--fastq_truncqual` of 2. Other available options are:
* --fastq_minovlen  
  * Minimum length of the overlap. Default: no minimum
* --fastq_minmergelen  
  * Minimum length of the overlap. Default: no minimum
* --fastq_maxmergelen  
  * Maximum length of the merged read. Default: no maximum
* --fastq_maxdiffs  
  * Maximum number of mismatches allowed in the overlap region. Default: any number of mismatches allowed
* --fastq_minlen  
  * Minimum length of the forward and reverse read, after truncating per  -fastq_truncqual if applicable. Default: no minimum
* --fastq_minovlen    
  * Allow merge of a pair where the alignment is 'staggered'  

## uparse_batch_filter.py  
Runs the `usearch -fastq_filter` command on a directory of fastqs. Available options are `--fastq_truncqual` and `--fastq_trunclen`. You could also pass `--forward` if you only want the
forward reads to be processed due to poor reverse read quality.

## derep_seqs.py  
Dereplicate sequences in `usearch` style. This script was written to overcome the 32-bit memory limitation.

## crouton.py
This script graphs the number of singletons, doubletons, tripletons, up to the n you pass it. 

## sequence_length_counter.py
Counts the length of the sequences and outputs a graph and textfile of the numbers found. We have seen a trimodal distribution of lengths before trimming the sequences to a uniform length.

# uparse_primary.py Flow
1. Merge reads  
`uparse_batch_merge.py -i input_dir -o output_dir --fastq_truncqual 2`
2. Filter merged reads  
`uparse_batch_filter.py -i input_dir -o output_dir --fastq_truncqual truncqual --fastq_trunclen`
3. Concatenate reads together to form an '.FNA' file  
`cat filtered_dir/*.fasta > output_dir/filtered.fna`
4. Dereplicate sequences   
`derep_seqs.py -i output_dir/filtered.fna`
5. Sort sequences by frequency   
`usearch7 -sortbysize output_dir/derep_filtered.fna -output output_dir/sorted_derep_filtered.fna -minsize 2`
6. Count the singletons, doubletons, tripletons, etc  
*`crouton.py -i output_dir/derep_filtered.fna -o output_dir/ -n 10`
7. Cluster Otus  
`usearch7 -cluster_otus output_dir/sorted_derep_filtered.fna -otus output_dir/otus.fasta`
8. Detect Chimeras  
`usearch7 -uchime_ref output_dir/otus.fasta -db bin_dir/gold.fa -strand plus -nonchimeras output_dir/non_chimeric_otus.fna`
9. Renumber fasta  
`fasta_number.py output_dir/non_chimeric_otus.fna > output_dir/renum_non_chimeric_otus.fna`
10. Usearch global  
`usearch7 -usearch_global output_dir/filtered.fna -db output_dir/renum_non_chimeric_otus.fna -strand plus -id 0.97 -uc output_dir/map.uc`
11. Map UC to OTUs  
`mapuc2otustxt.pl output_dir/map.uc`
12. Pick rep set  
`pick_rep_set.py -i output_dir/map.uc_otus.txt -f output_dir/filtered.fna`
13. Align sequences  
`align_seqs.py -i output_dir/filtered.fna_rep_set.fasta -o pynast_dir/`
14. Assign taxa  
`assign_taxonomy.py -i pynast_dir/filtered.fna_rep_set_aligned.fasta -m rdp -o output_dir/rdp_assigned_taxonomy/`
15. Filter alignment  
`filter_alignment.py -i pynast_dir/filtered.fna_rep_set_aligned.fasta -o pynast_dir/`
16. Make phylogeny tree  
`make_phylogeny.py -i pynast_dir/.fna_rep_set_aligned_pfiltered.fasta`
17. Make biom  
`make_otu_table.py -i output_dir/map.uc_otus.txt -o output_dir/otus.biom -t output_dir/rdp_assigned_taxonomy/filtered.fna_rep_set_aligned_tax_assignments.txt`

# Reference
```
Edgar, R.C. (2013) UPARSE: Highly accurate OTU sequences from microbial amplicon reads,Nature Methods [Pubmed:23955772,  dx.doi.org/10.1038/nmeth.2604].

QIIME allows analysis of high-throughput community sequencing data
J Gregory Caporaso, Justin Kuczynski, Jesse Stombaugh, Kyle Bittinger, Frederic D Bushman, Elizabeth K Costello, Noah Fierer, Antonio Gonzalez Pena, Julia K Goodrich, Jeffrey I Gordon, Gavin A Huttley, Scott T Kelley, Dan Knights, Jeremy E Koenig, Ruth E Ley, Catherine A Lozupone, Daniel McDonald, Brian D Muegge, Meg Pirrung, Jens Reeder, Joel R Sevinsky, Peter J Turnbaugh, William A Walters, Jeremy Widmann, Tanya Yatsunenko, Jesse Zaneveld and Rob Knight; Nature Methods, 2010; doi:10.1038/nmeth.f.303
```
