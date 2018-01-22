#!/usr/bin/env python
import sys, os
import multiprocessing

'''
For referance please see;

'''

numberOfCPU = multiprocessing.cpu_count()

if len(sys.argv) != 6:
    print ("Usage: python "+sys.argv[0]+" reference_genome_path father_bam mother_bam child_bam output_prefix")
    print(sys.argv)
    quit()

inputBam = sys.argv[1]
reference_genome_path = sys.argv[2]
knownSites_indels_dbsnp = sys.argv[3]
knownSites_indels_mills = sys.argv[4]
knownSites_indels_1000G = sys.argv[5]
prefix = sys.argv[6]
shutdown = False

def createAndUploadMD5(fileName):
    md5Command = "(time md5sum " + fileName + " > " + fileName + ".md5)  1>  " \
                 + prefix + "_md5.log 2>  " + prefix + "_md5.log"
    print("MD5 started...")
    print(md5Command)
    os.system(md5Command)
    print("MD5 upload started...")
    os.system("time aws s3 sync . s3://rnaseq-bucket/Makrogen/KATU/" + prefix + " --exclude '*' --include '*.md5'")

##############################################################################################################################
mpileupCommand = "(time sambamba mpileup  -t "+numberOfCPU \
                                + " -o " + prefix+".mpileup.trio.bcf  "\
                                +"--samtools -u -g -f  " + reference_genome_path \
                                + " " + father_bam \
                                + " " + mother_bam \
                                + " " + child_bam \
                                + " -t AD,INFO/AD,ADF,INFO/ADF,ADR,INFO/ADR,DP "\
                                + " )   1>  "+prefix+"_mpileup.log  2> " \
                                + prefix+"_mpileup.log"
print("Mpileup started...")
print(mpileupCommand)

if os.WEXITSTATUS(os.system(mpileupCommand)) != 0:
    os.system("time aws s3 sync . s3://rnaseq-bucket/Makrogen/KATU/" + prefix + " --exclude '*' --include '*.log'")
    print("Shutdown")
    if shutdown:
        os.system("shutdown -h now")
    quit()

createAndUploadMD5(prefix+".mpileup.trio.vcf")
print("Mpileup upload started...")
os.system("time aws s3 sync . s3://rnaseq-bucket/Makrogen/KATU/" + prefix + " --exclude '*' --include '*.mpileup.trio.bcf'")

##############################################################################################################################
bcftoolsCommand = "(bcftools call -mv -O v " \
                                + prefix + ".mpileup.trio.bcf  " \
                                + "  -o "\
                                + prefix+".mpileup.trio.vcf  "\
                                + " )   1>  "+prefix+"_bcftools.log  2> " \
                                + prefix+"_bcftools.log"
print("BCFTools started...")
print(bcftoolsCommand)

if os.WEXITSTATUS(os.system(bcftoolsCommand)) != 0:
    os.system("time aws s3 sync . s3://rnaseq-bucket/Makrogen/KATU/" + prefix + " --exclude '*' --include '*.log'")
    print("Shutdown")
    if shutdown:
        os.system("shutdown -h now")
    quit()

createAndUploadMD5(prefix+".mpileup.trio.vcf")
print("BCFTools upload started...")
os.system("time aws s3 sync . s3://rnaseq-bucket/Makrogen/KATU/" + prefix + " --exclude '*' --include '*.mpileup.trio.vcf'")

##############################################################################################################################

os.system("time aws s3 sync . s3://rnaseq-bucket/Makrogen/KATU/"+prefix)
print("\n Upload ended Shutdown progress started...")
if shutdown:
    os.system("shutdown -h now")




