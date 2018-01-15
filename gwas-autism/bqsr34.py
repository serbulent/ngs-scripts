#!/usr/bin/env python
import sys, os

'''
For referance please see;

https://gatkforums.broadinstitute.org/gatk/discussion/44/base-quality-score-recalibration-bqsr

https://gatkforums.broadinstitute.org/gatk/discussion/2801/howto-recalibrate-base-quality-scores-run-bqsr
'''

if len(sys.argv) != 7:
    print ("Usage: python "+sys.argv[0]+" input_bam reference_genome_path knownSites_indels_dbsnp knownSites_indels_mills knownSites_indels_1000G output_prefix")
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
'''
##############################################################################################################################
# 1. Analyze patterns of covariation in the sequence dataset
baseRecallCommand = "(time java -Xmx4g -jar /tools/GATK/GenomeAnalysisTK.jar -l INFO  " \
                                + "-T BaseRecalibrator "\
                                + " -R "+reference_genome_path \
                                + " -I "+ inputBam \
                                + " -knownSites " + knownSites_indels_dbsnp \
                                + " -knownSites " + knownSites_indels_mills \
                                + " -knownSites " + knownSites_indels_1000G \
                                + " -nct 8"\
                                + " -o "+prefix+"_recal_data.table  "\
                                + ")   1>  "+prefix+"_baseRecall.log  2> " \
                                + prefix + "_baseRecall.log"
print("Base Recall started...")
print(baseRecallCommand)

if os.WEXITSTATUS(os.system(baseRecallCommand)) != 0:
    os.system("time aws s3 sync . s3://rnaseq-bucket/Makrogen/KATU/" + prefix + " --exclude '*' --include '*.log'")
    print("Shutdown")
    if shutdown:
        os.system("shutdown -h now")
    quit()

createAndUploadMD5(prefix+"_recal_data.table")
print("Base Recall upload started...")
os.system("time aws s3 sync . s3://rnaseq-bucket/Makrogen/KATU/" + prefix + " --exclude '*' --include '*.table'")

##############################################################################################################################

# 2. Do a second pass to analyze covariation remaining after recalibration
baseRecallPostAnalyzeCommand = "(time java -Xmx4g -jar /tools/GATK/GenomeAnalysisTK.jar -l INFO  " \
                                + "-T BaseRecalibrator "\
                                + " -R "+reference_genome_path \
                                + " -I "+ inputBam \
                                + " -knownSites " + knownSites_indels_dbsnp \
                                + " -knownSites " + knownSites_indels_mills \
                                + " -knownSites " + knownSites_indels_1000G \
                                + " -BQSR " +prefix+"_recal_data.table "\
                                + " -nct 8"\
                                + " -o "+prefix+"_post_recal_data.table  "\
                                + ")   1>  "+prefix+"_baseRecallPost.log  2> " \
                                + prefix + "_baseRecallPost.log"
print("Base Recall Post Analyze started...")
print(baseRecallPostAnalyzeCommand)

if os.WEXITSTATUS(os.system(baseRecallPostAnalyzeCommand)) != 0:
    os.system("time aws s3 sync . s3://rnaseq-bucket/Makrogen/KATU/" + prefix + " --exclude '*' --include '*.log'")
    print("Shutdown")
    if shutdown:
        os.system("shutdown -h now")
    quit()

createAndUploadMD5(prefix+"_post_recal_data.table")
print("Base Recall upload started...")
os.system("time aws s3 sync . s3://rnaseq-bucket/Makrogen/KATU/" + prefix + " --exclude '*' --include '*.table'")

##############################################################################################################################
'''
# 3. Generate before/after plots
bqsrQCCommand = "(time java -Xmx4g -jar /tools/GATK/GenomeAnalysisTK.jar -l INFO " \
                                + "-T AnalyzeCovariates "\
                                + " -R "+reference_genome_path \
                                + " -before "+prefix+"_recal_data.table " \
                                + " -after "+prefix+"_post_recal_data.table  " \
                                + " -plots " +prefix+"_recalibration_plots.pdf  " \
                                + ")   1>  "+prefix+"_bqsrQC.log  2> " \
                                + prefix + "_bqsrQC.log"
print("BQSR QC started...")
print(bqsrQCCommand)

if os.WEXITSTATUS(os.system(bqsrQCCommand)) != 0:
    os.system("time aws s3 sync . s3://rnaseq-bucket/Makrogen/KATU/" + prefix + " --exclude '*' --include '*.log'")
    print("Shutdown")
    if shutdown:
        os.system("shutdown -h now")
    quit()

createAndUploadMD5(prefix+"_recalibration_plots.pdf")
print("BQSR QC upload started...")
os.system("time aws s3 sync . s3://rnaseq-bucket/Makrogen/KATU/" + prefix + " --exclude '*' --include '*.pdf'")

##############################################################################################################################

# 4. Apply the recalibration to your sequence data
printReadsCommand = "(time java -Xmx4g -jar /tools/GATK/GenomeAnalysisTK.jar -l INFO  --emit_original_quals " \
                                + " -T PrintReads "\
                                + " -R "+reference_genome_path \
                                + " -I "+ inputBam \
                                + " -BQSR " +prefix+"_recal_data.table "\
                                + " -nct 8"\
                                + " -o "+prefix+".bqsr.realigned.sorted.dupmarked.bam "\
                                + ")   1>  "+prefix+"_PrintReads.log  2> " \
                                + prefix + "_PrintReads.log"
print("Print Reads started...")
print(printReadsCommand)

if os.WEXITSTATUS(os.system(printReadsCommand)) != 0:
    os.system("time aws s3 sync . s3://rnaseq-bucket/Makrogen/KATU/" + prefix + " --exclude '*' --include '*.log'")
    print("Shutdown")
    if shutdown:
        os.system("shutdown -h now")
    quit()

createAndUploadMD5(prefix+".bqsr.realigned.sorted.dupmarked.bam")
print("Print Reads upload started...")
os.system("time aws s3 sync . s3://rnaseq-bucket/Makrogen/KATU/" + prefix + " --exclude '*' --include '*.bqsr.realigned.sorted.dupmarked.bam'")

##############################################################################################################################

os.system("time aws s3 sync . s3://rnaseq-bucket/Makrogen/KATU/"+prefix)
print("\n Upload ended Shutdown progress started...")
if shutdown:
    os.system("shutdown -h now")





