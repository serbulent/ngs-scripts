#!/usr/bin/env python
import sys, os

if len(sys.argv) != 6:
    print ("Usage: python "+sys.argv[0]+" input_bam reference_genome_path known_indel_file1 known_indel_file2 output_prefix")
    print(sys.argv)
    quit()

inputBam = sys.argv[1]
reference_genome_path = sys.argv[2]
known_indel_file1 = sys.argv[3]
known_indel_file2 = sys.argv[4]
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

realignerTargetCreatorCommand = "(time java -jar /tools/GATK/GenomeAnalysisTK.jar  " \
                                + "-T RealignerTargetCreator "\
                                + " -R "+reference_genome_path \
                                + " -known " + known_indel_file1 \
                                + " -known " + known_indel_file2 \
                                + " -I "+ inputBam\
                                + " -nt 16"\
                                + " -o "+prefix+"_realignertargetcreator.intervals  "\
                                + ")   1>  "+prefix+"_RealignerTargetCreator.log  2> " \
                                + prefix + "_RealignerTargetCreator.log"
print("Realigner Target Creator started...")
print(realignerTargetCreatorCommand)

if os.WEXITSTATUS(os.system(realignerTargetCreatorCommand)) != 0:
    os.system("time aws s3 sync . s3://rnaseq-bucket/Makrogen/KATU/" + prefix + " --exclude '*' --include '*.log'")
    print("Shutdown")
    if shutdown:
        os.system("shutdown -h now")
    quit()

createAndUploadMD5(prefix+"_realignertargetcreator.intervals")
print("Realigner Target Creator upload started...")
os.system("time aws s3 sync . s3://rnaseq-bucket/Makrogen/KATU/" + prefix + " --exclude '*' --include '*.intervals'")

##############################################################################################################################

indelRealignerCommand = "(time java -jar /tools/GATK/GenomeAnalysisTK.jar  " \
                                + "-T IndelRealigner "\
                                + " -R "+reference_genome_path \
                                + " -known " + known_indel_file1 \
                                + " -known " + known_indel_file2 \
                                + " -targetIntervals " + prefix +"_realignertargetcreator.intervals" \
                                + " -I "+ inputBam\
                                + " -o "+prefix+".realigned.sorted.dupmarked.bam "\
                                + ")   1>  "+prefix+"_RealignerTargetCreator.log  2> " \
                                + prefix + "_RealignerTargetCreator.log"



print("Indel Realigner started...")
print(indelRealignerCommand)

if os.WEXITSTATUS(os.system(indelRealignerCommand)) != 0:
    os.system("time aws s3 sync . s3://rnaseq-bucket/Makrogen/KATU/" + prefix + " --exclude '*' --include '*.log'")
    print("Shutdown")
    if shutdown:
        os.system("shutdown -h now")
    quit()

createAndUploadMD5(prefix+".realigned.sorted.dupmarked.bam")
print("Indel Realigner upload started...")
os.system("time aws s3 sync . s3://rnaseq-bucket/Makrogen/KATU/" + prefix + " --exclude '*' --include '*.realigned.sorted.dupmarked.bam'")
##############################################################################################################################

os.system("time aws s3 sync . s3://rnaseq-bucket/Makrogen/KATU/"+prefix)
print("\n Upload ended Shutdown progress started...")
if shutdown:
    os.system("shutdown -h now")





