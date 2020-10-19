#!/bin/bash

set -eo pipefail

echo “Download 1000g phase1 release v3 population sites…”
time wget ftp://share.sph.umich.edu/1000genomes/fullProject/2012.03.14/phase1_release_v3.20101123.snps_indels_svs.genotypes.refpanel.ALL.vcf.gz.tgz

echo “Untar 1000g file…”
tar -xvf phase1_release_v3.20101123.snps_indels_svs.genotypes.refpanel.ALL.vcf.gz.tgz

echo “Concatanate all chromosomes in natural order…”
time zcat chr{1..22}.phase1_release_v3.20101123.snps_indels_svs.genotypes.refpanel.ALL.vcf.gz > all.1000g_phase1_release_v3.20101123.snps_indels_svs.genotypes.refpanel.ALL.vcf

echo “Bgzip compress 1000g file for tabix indexing…”
time bgzip all.1000g_phase1_release_v3.20101123.snps_indels_svs.genotypes.refpanel.ALL.vcf

echo “Tabix index bgzip compressed 1000g file…”
time tabix -p vcf all.1000g_phase1_release_v3.20101123.snps_indels_svs.genotypes.refpanel.ALL.vcf.gz

###Genotype Refinement Workflow

family=$1
capital=${family^^}

# Calculate Genotype Posteriors
# MLEAC is not present in every record. Fall back to using AC, instead.
echo “Calculate Genotype Posteriors…”
time java -jar /tools/GATK/GenomeAnalysisTK.jar -R /reference/hg19/bwa/ucsc.hg19.fasta -T CalculateGenotypePosteriors --defaultToAC --supporting all.1000g_phase1_release_v3.20101123.snps_indels_svs.genotypes.refpanel.ALL.vcf.gz -ped $family.ped --pedigreeValidationType SILENT -V $capital.T90.0Filtered.consensus.trio.vcf.gz -o $capital.withPosteriors.consensus.trio.vcf

# Filter low quality genotypes
echo “Filter low quality genotypes…”
time java -jar /tools/GATK/GenomeAnalysisTK.jar -R /reference/hg19/bwa/ucsc.hg19.fasta -T VariantFiltration -R /reference/hg19/bwa/ucsc.hg19.fasta -V $capital.withPosteriors.consensus.trio.vcf -G_filter “GQ < 20.0” -G_filterName lowGQ -o $capital.GQ20Filtered.withPosteriors.consensus.trio.vcf

# Annotate possible de novo mutations
echo “Annotate possible de novo mutations…”
time java -jar /tools/GATK/GenomeAnalysisTK.jar -R /reference/hg19/bwa/ucsc.hg19.fasta -T VariantAnnotator -A PossibleDeNovo -ped $family.ped -V  $capital.GQ20Filtered.withPosteriors.consensus.trio.vcf -o $capital.possibleDeNovo.GQ20Filtered.withPosteriors.consensus.trio.vcf

# Phase family
echo “Phase by tranmission…”
time java -jar /tools/GATK/GenomeAnalysisTK.jar -R /reference/hg19/bwa/ucsc.hg19.fasta -T PhaseByTransmission -V $capital.possibleDeNovo.GQ20Filtered.withPosteriors.consensus.trio.vcf -ped $family.ped -o $capital.phaseByTransmission.possibleDeNovo.GQ20Filtered.withPosteriors.consensus.trio.vcf