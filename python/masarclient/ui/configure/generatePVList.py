#!/usr/bin/env python2.7
#import time

#fileName = "SR_All_SCR_20140421.txt"
#fileName = "SR_All_SCR_20140421.csv"
fileName = "SR-All-20140304.txt"
fileNamePrefix = fileName.split('.')[0]
fileType = fileName.split('.')[1]
inputFile=open(fileName)
lines=inputFile.readlines()

spPVList=[]

if fileType == "csv": #.csv is the file saved by MASAR GUI   
    print("Generating preliminary configuration from .csv file which was saved by MASAR ...\n") 
    for line in lines:
        spPVList.append(line.split(',')[0])       
    outFileName = fileNamePrefix + '.cfg_'
    outFile = open(outFileName, 'w')
    for pv in spPVList:
        outFile.write(pv+'\t\t'+pv.replace('-SP', 'DCCT1-I').replace('Sp', 'Ps')+'\n')
    print("Done. Copy %s to %s.cfg and test it to create the final PV list file %s.txt"\
    %(outFileName, fileNamePrefix, fileNamePrefix))
    
elif fileType == "txt":#.txt is the final PV list (only one Column)
    print("Generating final configuration from censored PV list ...")
    for line in lines:
        spPVList.append(line[:-1])#remove the trailing '\n'       
    outFileName = fileNamePrefix + '.cfg'
    outFile = open(outFileName, 'w')
    for pv in spPVList:
        outFile.write(pv+'\t\t'+pv.replace('-SP', 'DCCT1-I').replace('Sp', 'Ps')+'\t\t'+
                      pv.replace('I:', 'Rate:').replace('Sp', 'Rmp') + '\n')
    print("\nDone.")    
         
else:
    print("unknown file format")

#time.sleep(1.0)
    
