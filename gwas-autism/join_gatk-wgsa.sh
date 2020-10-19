#!/bin/bash

set -eo pipefail

### Join GATK outputs with WGSA annotations.

## GATK files
echo "Unzip phaseByTransmission vcf…"
time gunzip -dk KATU456.phaseByTransmission.possibleDeNovo.GQ20Filtered.withPosteriors.consensus.trio.vcf.gz

# Decompose GATK output since WGSA representation is not multiallelic.
echo "Decompose vcf…"
time vt decompose KATU456.phaseByTransmission.possibleDeNovo.GQ20Filtered.withPosteriors.consensus.trio.vcf > KATU456.GATK.decomposed.vcf

echo "Zip decomposed vcf…"
time gzip -k KATU456.GATK.decomposed.vcf

# Convert decomposed GATK vcf to tsv
echo "Convert vcf to tsv…"
time vk vcf2tsv wide --print-header KATU456.GATK.decomposed.vcf > katu456.GATK.decomposed.tsv

# Infer zygosity from GT fields for each sample
echo "Infer zygosities for each sample…"
time awk ' NR == 1 {print "KATU4_Zygosity"} NR > 1 {if ($53 ~ /\./) print "Missing"; if ($53 == "0/1" || $53 == "0|1" || $53 == "1/0" || $53 == "1|0") print "Heterozygous"; if ($53 == "0/0" || $53 == "0|0") print "Homozygous for reference"; if ($53 == "1/1" || $53 == "1|1") print "Homozygous for alternative"} ' < katu456.GATK.decomposed.tsv > katu4_zygosity.tsv
time awk ' NR == 1 {print "KATU5_Zygosity"} NR > 1 {if ($63 ~ /\./) print "Missing"; if ($63 == "0/1" || $63 == "0|1" || $63 == "1/0" || $63 == "1|0") print "Heterozygous"; if ($63 == "0/0" || $63 == "0|0") print "Homozygous for reference"; if ($63 == "1/1" || $63 == "1|1") print "Homozygous for alternative"} ' < katu456.GATK.decomposed.tsv > katu5_zygosity.tsv
time awk ' NR == 1 {print "KATU6_Zygosity"} NR > 1 {if ($73 ~ /\./) print "Missing"; if ($73 == "0/1" || $73 == "0|1" || $73 == "1/0" || $73 == "1|0") print "Heterozygous"; if ($73 == "0/0" || $73 == "0|0") print "Homozygous for reference"; if ($73 == "1/1" || $73 == "1|1") print "Homozygous for alternative"} ' < katu456.GATK.decomposed.tsv > katu6_zygosity.tsv

# Insert zygosity information of each sample next to relevant GT field.
echo "Insert zygosity columns…"
time paste <(cut -f-53 katu456.GATK.decomposed.tsv) katu4_zygosity.tsv <(cut -f54-63 katu456.GATK.decomposed.tsv) katu5_zygosity.tsv <(cut -f64-73 katu456.GATK.decomposed.tsv) katu6_zygosity.tsv <(cut -f74- katu456.GATK.decomposed.tsv) > katu456.GATK.decomposed.zygosity.tsv

# Sort GATK file with respect to chromosome and location
echo "Sort zygosity tsv…"
time ( head -n +1 katu456.GATK.decomposed.zygosity.tsv > katu456.GATK.decomposed.zygosity.sorted.tsv ; tail -n +2 katu456.GATK.decomposed.zygosity.tsv | sort -k1,1V -k2,2n --parallel 2 >> katu456.GATK.decomposed.zygosity.sorted.tsv )

## WGSA files

# Concatanate snv and indel WGSA files
echo "Concatanate WGSA snv and indel…"
time zcat katu456.annotated.snp.gz katu456.annotated.indel.gz > katu456.WGSA.all.tsv

# Fix chromosomes
echo "Add chr prefixes…"
time ( head -n +1 katu456.WGSA.all.tsv > katu456.WGSA.all.chrfixed.tsv ; sed -e 's/^/chr/' <( tail -n +2 katu456.WGSA.all.tsv ) >> katu456.WGSA.all.chrfixed.tsv )

# Sort fixed WGSA file with respect to chromosome and location
echo "Sort chromosome fixed tsv…"
time ( head -n +1 katu456.WGSA.all.chrfixed.tsv > katu456.WGSA.all.chrfixed.sorted.tsv ; tail -n +2 katu456.WGSA.all.chrfixed.tsv | sort -k1,1V -k2,2n --parallel 2  >> katu456.WGSA.all.chrfixed.sorted.tsv )

## Join two files

# Extract relevant columns from each file to generate a key which is a unique combination of chr-pos-alt-ref
echo "Create keys for each sample for joining…"
time awk '{print $1 "_" $2 "_" $4 "_" $5}' katu456.GATK.decomposed.zygosity.sorted.tsv > katu456.GATK.key.tsv

time awk '{print $1 "_" $2 "_" $3 "_" $4}' katu456.WGSA.all.chrfixed.sorted.tsv > katu456.WGSA.key.tsv

echo "Append keys before sorted files…"
time paste katu456.GATK.key.tsv katu456.GATK.decomposed.zygosity.sorted.tsv > katu456.GATK.withKey.tsv

time paste katu456.WGSA.key.tsv katu456.WGSA.all.chrfixed.sorted.tsv > katu456.WGSA.withKey.tsv

echo "Sort key appended files…"
time tail -n +2 katu456.GATK.withKey.tsv | sort -k1,1 > katu456.GATK.withKey.sorted.tsv

time tail -n +2 katu456.WGSA.withKey.tsv | sort -k1,1  > katu456.WGSA.withKey.sorted.tsv

echo "Join two files based on unique key…"
time join -t $’\t’ -1 1 -2 1 katu456.GATK.withKey.sorted.tsv katu456.WGSA.withKey.sorted.tsv > katu456.join.tsv

# Extract headers from both files and paste them
echo "Prepare header and append before joined file…"
time paste <(head -n +1 katu456.GATK.withKey.tsv) <(head -n +1 katu456.WGSA.withKey.tsv) | cut --complement -f83 > header.txt # cut is used to get rid of unique key header of wgsa file.

time ( cat header.txt katu456.join.tsv | cut --complement -f1 > katu456.result.tsv ) # Get rid of unique key used for sorting

# Sort again result file
echo "Sorting resulting file…"
time sort -k1,1V -k2,2n katu456.result.tsv > katu456.result.sorted.tsv


# Rearrange column order and remove unnecessary columns
echo "Rearranging and removing columns…"

<<C
# Awk is obselete for now as there is a defect…
time awk 'FS="\t"; OFS="\t"; {print $1,$2,$3,$4,$5,$202,$53,$54,$52,$50,$64,$65,$63,$61,$75,$76,$74,$72,$141,$142,$143,$144,$145,$146,$147,$148,$194,$195,$196,$197,$198,$199,$200,$202,$207,$208,$219,$220,$221,$222,$223,$272,$273,$274,$275,$284,$285,$288,$289,$290,$291,$300,$301,$304,$305,$306,$307,$316,$317,$320,$321,$322,$338,$339,$340,$344,$345,$346,$347,$348,$349,$365,$366,$367,$368,$369,$370,$373,$375,$382,$383,$384,$385,$386,$387,$388,$389,$390,$391,$392,$393,$394,$395,$396,$397,$398,$399,$404,$405,$406,$407,$408,$409,$410,$411,$412,$413,$414,$415,$416,$417,$418,$419,$420,$444,$445,$446,$447,$448,$449,$450,$451,$452,$453,$454,$455,$456,$457,$458,$459,$460,$461,$462,$463,$464,$465,$466,$467,$480,$481,$482,$483,$484,$485,$486,$8,$9,$10,$14,$15,$22,$23,$24,$25,$29,$30,$35,$37,$43,$44,$45,$46,$48}' < katu456.result.sorted.tsv > katu456.reduced.tsv
C

time paste <(cut -f1-5 katu456.result.sorted.tsv) <(cut -f202 katu456.result.sorted.tsv) <(cut -f53,54 katu456.result.sorted.tsv) <(cut -f52 katu456.result.sorted.tsv) <(cut -f50 katu456.result.sorted.tsv) <(cut -f64,65 katu456.result.sorted.tsv) <(cut -f63 katu456.result.sorted.tsv) <(cut -f61 katu456.result.sorted.tsv) <(cut -f75,76 katu456.result.sorted.tsv) <(cut -f74 katu456.result.sorted.tsv) <(cut -f72 katu456.result.sorted.tsv) <(cut -f94-118 katu456.result.sorted.tsv) <(cut -f273,274,289,290,305,306,322,346,349,370,375 katu456.result.sorted.tsv) <(cut -f444-452 katu456.result.sorted.tsv) <(cut -f8,9,10,14,15,22,23,24,25,29,30,35,37,43,44,45,46,48 katu456.result.sorted.tsv) > katu456.reduced.tsv

<<C
# Annovar annot didn’t allow us to filter on mutation types and effects!
time paste <(cut -f1-5 katu456.result.sorted.tsv) <(cut -f202 katu456.result.sorted.tsv) <(cut -f53,54 katu456.result.sorted.tsv) <(cut -f52 katu456.result.sorted.tsv) <(cut -f50 katu456.result.sorted.tsv) <(cut -f64,65 katu456.result.sorted.tsv) <(cut -f63 katu456.result.sorted.tsv) <(cut -f61 katu456.result.sorted.tsv) <(cut -f75,76 katu456.result.sorted.tsv) <(cut -f74 katu456.result.sorted.tsv) <(cut -f72 katu456.result.sorted.tsv) <(cut -f141-148 katu456.result.sorted.tsv) <(cut -f194-201 katu456.result.sorted.tsv) <(cut -f273,274,289,290,305,306,322,346,349,370,375 katu456.result.sorted.tsv) <(cut -f444-452 katu456.result.sorted.tsv) <(cut -f8,9,10,14,15,22,23,24,25,29,30,35,37,43,44,45,46,48 katu456.result.sorted.tsv) > katu456.reduced.tsv
C
echo “Split joined files into equal parts…”
# Split resulting file to 20 parts.
time split -l$((`wc -l < katu456.result.tsv`/20)) katu456.result.tsv katu456.result.split. -da 4
