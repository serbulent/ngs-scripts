#!/bin/bash

awk '{print $1 "_" $2 "_" $4 "_" $5}' katu123.GATK.decomposed.sorted.col1-6.tsv > katu123_GATK_test_key.tsv

awk '{print $1 "_" $2 "_" $3 "_" $4}' katu123.WGSA.all.chrfixed.sorted.col1-6.tsv > katu123_WGSA_test_key.tsv

paste -d'\t' {katu123_WGSA_test_key,katu123.WGSA.all.chrfixed.sorted.col1-6}.tsv > katu123_WGSA_with_key_test.tsv

paste -d'\t' {katu123_GATK_test_key,katu123.GATK.decomposed.sorted.col1-6}.tsv > katu123_GATK_with_key_test.tsv

sort -k1,1 -V katu123_WGSA_with_key_test.tsv > katu123_WGSA_with_key_test_sorted.tsv

sort -k1,1 -V katu123_GATK_with_key_test.tsv > katu123_GATK_with_key_test_sorted.tsv

join -t $'\t' -1 1 -2 1 katu123_GATK_with_key_test_sorted.tsv katu123_WGSA_with_key_test_sorted.tsv > katu123_join_test.tsv

time split -l$((`wc -l < katu123_annotation.tsv`/20)) katu123_annotation.tsv katu123_annotation.split.tsv -da 4
