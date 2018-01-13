#!/usr/bin/env python
import sys, os

if len(sys.argv) != 5:
  print ("Usage: python aligner.py reference_genome_path readPair1_trimmed.fa readPair2_trimmed.fa prefix_for_sam")
  print(sys.argv)
  quit()

referenceGenome = sys.argv[1]
readPair1 = sys.argv[2]
readPair2 = sys.argv[3]
prefix = sys.argv[4]
shutdown = False


##############################################################################################################################
alignCommand = "(time bwa mem -M -t 16 -R '@RG\\tID:" +prefix+"\\tPL:ILLUMINA\\tLB:KATULIB\\tSM:"+prefix+"' "+referenceGenome +\
               " "+readPair1+" "+readPair2+ " > "+prefix+".sam)  1>  " +prefix+ "_alignment.log 2>  " +prefix+ "_alignment.log"
print("Alignment started...")
print(alignCommand)

if os.WEXITSTATUS(os.system(alignCommand)) != 0:
  os.system("time aws s3 sync . s3://rnaseq-bucket/Makrogen/KATU/"+prefix+ "' --exclude '*' --include '*.log'")
  print("Shutdown")
  if shutdown:
    os.system("shutdown -h now")
  quit()

##############################################################################################################################

sam2BamCommand = "(time samtools view -Sb  "+prefix+".sam  >  "+prefix+".bam)   1>  " +prefix+ "_sam2Bam.log 2>  " +prefix+ "_sam2Bam.log"
print("Sam To Bam started...")
print(sam2BamCommand)

if os.WEXITSTATUS(os.system(sam2BamCommand)) != 0:
  os.system("time aws s3 sync . s3://rnaseq-bucket/Makrogen/KATU/"+prefix+ "' --exclude '*' --include '*.log'")
  print("Shutdown")
  if shutdown:
    os.system("shutdown -h now")
  quit()

##############################################################################################################################

md5Command = "(time md5sum "+prefix+".bam > "+prefix+".bam.md5)  1>  " +prefix+ "_md5.log 2>  " +prefix+ "_md5.log"
print("MD5 started...")
print(md5Command)

if os.WEXITSTATUS(os.system(md5Command)) != 0:
  os.system("time aws s3 sync . s3://rnaseq-bucket/Makrogen/KATU/"+prefix+ "' --exclude '*' --include '*.log'")
  print("Shutdown")
  if shutdown:
    os.system("shutdown -h now")
  quit()
##############################################################################################################################

uploadCommand = "( time aws s3 cp "+prefix+".bam s3://rnaseq-bucket/Makrogen/KATU/"+prefix+"/ )   1> " +prefix+"_upload.log 2> " +prefix+"_upload.log"
print("Upload started...")
print(uploadCommand)

if os.WEXITSTATUS(os.system(uploadCommand)) != 0:
  os.system("time aws s3 sync . s3://rnaseq-bucket/Makrogen/KATU/"+prefix+ "' --exclude '*' --include '*.log'")
  print("Shutdown")
  if shutdown:
    os.system("shutdown -h now")
  quit()
##############################################################################################################################


os.system("time aws s3 sync . s3://rnaseq-bucket/Makrogen/KATU/"+prefix)
print("\n Upload ended Shutdown progress started...")
if shutdown:
    os.system("shutdown -h now")
