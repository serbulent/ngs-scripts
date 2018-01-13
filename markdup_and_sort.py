#!/usr/bin/env python
import sys, os

if len(sys.argv) != 4:
    print ("Usage: python aligner.py input_bam reference_genome_path output_prefix")
    print(sys.argv)
    quit()

inputBam = sys.argv[1]
prefix = sys.argv[2]
shutdown = False

##############################################################################################################################
markdupCommand = "(time sambamba markdup " + inputBam + " " + prefix + ".dupmarked.bam)  1>  " + prefix + "_markdup.log 2>  " + prefix + "_markdup.log"
print("Marking duplacates started...")
print(markdupCommand)

if os.WEXITSTATUS(os.system(markdupCommand)) != 0:
    os.system("time aws s3 sync . s3://rnaseq-bucket/Makrogen/KATU/" + prefix + " --exclude '*' --include '*.log'")
    print("Shutdown")
    if shutdown:
        os.system("shutdown -h now")
    quit()

##############################################################################################################################

sortCommand = "(time sambamba sort " + prefix + ".dupmarked.bam --out=" + prefix + \
              ".sorted.dupmarked.bam --memory-limit=120G --nthreads=16 --show-progress)   1>  " \
              + prefix + "_sorting.log 2>  " + prefix + "_sorting.log"
print("Sorting started...")
print(sortCommand)
A
if os.WEXITSTATUS(os.system(sortCommand)) != 0:
    os.system("time aws s3 sync . s3://rnaseq-bucket/Makrogen/KATU/" + prefix + " --exclude '*' --include '*.log'")
    print("Shutdown")
    if shutdown:
        os.system("shutdown -h now")
    quit()

##############################################################################################################################

md5Command = "(time md5sum " + prefix + ".sorted.dupmarked.bam > " + prefix + ".sorted.dupmarked.bam.md5)  1>  "\
             + prefix + "_md5.log 2>  " + prefix + "_md5.log"
print("MD5 started...")
print(md5Command)

if os.WEXITSTATUS(os.system(md5Command)) != 0:
    os.system("time aws s3 sync . s3://rnaseq-bucket/Makrogen/KATU/" + prefix + " --exclude '*' --include '*.log'")
    print("Shutdown")
    if shutdown:
        os.system("shutdown -h now")
    quit()
##############################################################################################################################

uploadCommand = "(time aws s3 cp " + prefix + ".sorted.dupmarked.bam s3://rnaseq-bucket/Makrogen/KATU/" + prefix + "/)   1> "\
                + prefix + "_upload.log 2> " + prefix + "_upload.log"
print("Upload started...")
print(uploadCommand)

if os.WEXITSTATUS(os.system(uploadCommand)) != 0:
    os.system("time aws s3 sync . s3://rnaseq-bucket/Makrogen/KATU/" + prefix + " --exclude '*' --include '*.log'")
    print("Shutdown")
    if shutdown:
        os.system("shutdown -h now")
    quit()
##############################################################################################################################

os.system("time aws s3 sync . s3://rnaseq-bucket/Makrogen/KATU/"+prefix)
print("\n Upload ended Shutdown progress started...")
if shutdown:
    os.system("shutdown -h now")
