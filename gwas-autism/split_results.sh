#!/bin/bash

family=$1
file=${1}.reduced.tsv

# First filter: ( Father || Mother ) Heterozygous && Child Homozygous for alternative && protein coding genes && nonsense || frameshift || splicing region mutation
awk -F'\t' 'NR > 1 { if  ( ($8 ~ /Heterozygous/ && $12 ~ /Heterozygous/ && $16 ~ /alternative/ )  && ( $0 ~ /nonsense/ || $0 ~ /frameshift/ || $0 ~ /splicing/) ) print $0 }' < $file > ${family}.hetz-hetz-homz_coding_nonsense_frameshift_splicing.tsv 

# Second filter: ( Father || Mother ) Heterozygous && Child homozygous for alternative && protein coding genes && missense mutation
awk -F'\t' 'NR > 1 { if  ( ($8 ~ /Heterozygous/ && $12 ~ /Heterozygous/ && $16 ~ /alternative/ ) && $0 ~ /missense_variant/) print $0 }' < $file > ${family}.hetz-hetz-homz_coding_missense.tsv

# Third filter: ( Father || Mother ) Heterozygous && Child homozygous for alternative && intergenic regions
awk -F'\t' 'NR > 1 { if  ( ($8 ~ /Heterozygous/ && $12 ~ /Heterozygous/ && $16 ~ /alternative/ ) && $0 ~ /intergenic/) print $0 }' < $file > ${family}.hetz-hetz-homz_intergenic.tsv

# Fourth filter: Protein coding genes && possible de novo mutations in child
awk -F'\t' 'NR > 1 { if ( $0 ~ /protein_coding/ && $0 ~ /KATU6/ ) print $0 }' < $file > ${family}.coding_denovo.tsv

# Fifth filter: Intergenic regions && possible de novo mutations in child
awk -F'\t' 'NR > 1 { if ( $0 ~ /intergenic/ && $0 ~ /KATU6/ ) print $0 }' < $file > ${family}.coding_denovo.tsv

# Sixth filter: Variant not in dbSNP150 && ( intragenic || intergenic regions )
awk -F'\t' 'NR >1 { if ( $7 ~ /\./ && ($0 ~ /intronic/ || $0 ~ /intergenic/) ) print $0 }' < $file > ${family}.NOrsid_intragenic_intergenic.tsv
