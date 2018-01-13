#!/usr/bin/env python
import sys, os

if len(sys.argv) != 4:
	print ("Usage: skewer_trimmer.py readPair1.fa readPair2.fa adapterFasta.fa")
	quit()

readPair1 = sys.argv[1]
readPair2 = sys.argv[2]
adapterFasta = sys.argv[3]

if os.WEXITSTATUS(os.system("time skewer -t 32 -m pe -q 10 -Q 20 -l 35 -n -x " + adapterFasta + " "+ readPair1  +" "+ readPair2)) != 0:
	print("Shutdown")
	os.system("shutdown -h now")
else:
	print("\n Flexbar ended QC started for pair 1")
	readPair1Trimmed = readPair1.replace(".gz", "")
	readPair1Trimmed = readPair1Trimmed + "-trimmed-pair1.fastq"
	os.system("time fastqc -t 32 " + readPair1Trimmed)
	
	print("\n Flexbar ended QC started for pair 2")
	readPair2Trimmed = readPair1.replace(".gz", "")
	readPair2Trimmed = readPair2Trimmed + "-trimmed-pair2.fastq"
	os.system("time fastqc -t 32 " + readPair2Trimmed )

#	readPair1TrimmedGZ = readPair1Trimmed + ".gz"
#	readPair2TrimmedGZ = readPair2Trimmed + ".gz"

	print("\n Compressing output files...")
	os.system("pigz -p 32 " + readPair1Trimmed)	
	os.system("pigz -p 32 " + readPair2Trimmed)	

	print("\n QC ended sync started")
	os.system("time aws s3 sync . s3://rnaseq-bucket/Makrogen/KATU/KATU1/")

	print("\n SYNC ended Shutdown progress started...")
	os.system("shutdown -h now")
