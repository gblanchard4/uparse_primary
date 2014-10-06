uparse_primary
==============
Collection Of Scripts to run a uparse primary analysis

## Flow
1. Merge reads
`uparse_batch_merge.py -i input_dir -o output_dir --fastq_truncqual truncqual`
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
