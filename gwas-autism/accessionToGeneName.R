#!/usr/bin/env Rscript
args = commandArgs(trailingOnly=TRUE)

if (length(args)<1) {
stop("At least one argument must be supplied (input file).n", call.=FALSE)
} else if (length(args)==1) {

#install.packages("biomaRt")
library(biomaRt)
prefix = args[1]
refseqAccessionIds <- read.csv(paste(prefix,".refseq_accession.ids",sep=""), header = FALSE)
mart<- useDataset("hsapiens_gene_ensembl", useMart("ensembl"))
res <- getBM(c("refseq_mrna", "external_gene_name"), "refseq_mrna",refseqAccessionIds, mart=mart)
sfari <- read.csv(file="SFARI-Gene_genes_export25-05-2018.csv", header=TRUE, sep=",") 
isSfari <- res[,2] %in% sfari[,2]
res[,3] <- isSfari
write.table(res,paste(prefix,".gene_names.tsv",sep=""),row.names=FALSE,quote=FALSE)
}
