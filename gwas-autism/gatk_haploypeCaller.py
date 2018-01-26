#!/usr/bin/env python
import sys, os
import multiprocessing

if len(sys.argv) != 6:
    print ("Usage: python "+sys.argv[0]+" reference_genome_path father_bam mother_bam child_bam output_prefix")
    print(sys.argv)
    quit()

print(sys.argv)

numberOfCPU = str(multiprocessing.cpu_count())

reference_genome_path = sys.argv[1]
father_bam = sys.argv[2]
mother_bam = sys.argv[3]
child_bam = sys.argv[4]
prefix = sys.argv[5]
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

haplotypeCallerCommand = "(time java -jar -Xmx4g /tools/GATK/GenomeAnalysisTK.jar -T HaplotypeCaller -stand_call_conf 20 " \
                                + " -A BaseQualityRankSumTest -A Coverage -A DepthPerAlleleBySample -A FisherStrand -A QualByDepth -A ReadPosRankSumTest " \
                                + " -nct " + numberOfCPU \
                                + " -R " + reference_genome_path \
                                + " -I " + father_bam \
                                + " -I " + mother_bam \
                                + " -I " + child_bam \
                                + " -o " + prefix + ".haplotypecaller.trio.vcf " \
                                + " )   1>  "+prefix+"_haplotypecaller.log  2> " \
                                + prefix+"_haplotypecaller.log"
print("HaplotypeCaller started...")
print(haplotypeCallerCommand)

if os.WEXITSTATUS(os.system(haplotypeCallerCommand)) != 0:
    os.system("time aws s3 sync . s3://rnaseq-bucket/Makrogen/KATU/" + prefix + " --exclude '*' --include '*.log'")
    print("Shutdown")
    if shutdown:
        os.system("shutdown -h now")
    quit()

createAndUploadMD5(prefix + ".haplotypecaller.trio.vcf")
print("HaplotypeCaller upload started...")
os.system("time aws s3 sync . s3://rnaseq-bucket/Makrogen/KATU/" + prefix + " --exclude '*' --include '*.mpileup.trio.bcf'")


##############################################################################################################################

os.system("time aws s3 sync . s3://rnaseq-bucket/Makrogen/KATU/"+prefix)
print("\n Upload ended Shutdown progress started...")
if shutdown:
    os.system("shutdown -h now")




