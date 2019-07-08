# cSpell:disable
#============================
#PACKAGES
#============================

import os
import requests
import traceback
import time
import numpy as np

#============================
#LOG HANDLER
#============================
def log(message):
    try:
        logHandler=open((os.getcwd()+"/log.log"), 'a')
        print(message)
        logHandler.write(message)
        logHandler.write(os.linesep)
        logHandler.close()
    except Exception:
        print (traceback.format_exc())

#============================
#FILE READER
#============================
def readFile(fName):
    try:
        fileHandler=open((os.getcwd()+fName), 'r')
        log("Loading "+fName+" ...")
        rawFile=fileHandler.read()
        fileHandler.close()
        return rawFile
    except Exception:
        raise Exception(traceback.format_exc())
#============================
#PROTEIN FASTA DOWNLOADER
#============================
def getFileFromURL(webAddress,pFile,extension):
    try:
        URL=webAddress.format(pFile,extension)
        # log("Sending request to ... ")
        # log(URL)
        response = requests.get(URL)
        time.sleep(1)
        if response.ok:
            return response.text
        else:
            raise Exception(
                'Online Request Status for {} is {}'.format(
                    pFile+"."+extension,response.status_code))

    except Exception:
        raise Exception(traceback.format_exc())
#============================
#FASTA PARSER
#============================
def parseFasta(content):
    try:
        sequence = ("".join(content[1:]).replace(os.linesep,"")).replace(" ","")
        log("Processing Downloaded Data for Sequence ...")
        return sequence
    except Exception:
        raise Exception(traceback.format_exc())
        

#============================
#DOWNLOAD/PARSE/WRITE TO FILE
#============================
def downloadCreateDataList(itemList,site,format,dataPath):
    try:
        try:
            open((os.getcwd()+dataPath), 'w').close()
            
        except Exception:
            newPath=dataPath.split("/")
            path = ("/".join(newPath[:(len(newPath)-1)]))
            os.mkdir(os.getcwd()+path)
            
        finally:
            fileHandler=open((os.getcwd()+dataPath), 'a')


        lastItemInList=itemList[len(itemList)-1]

        for item in itemList:
            log( "Downloading ... "+item)
            callResult=getFileFromURL(site,item,format)
                
            parseResult = parseFasta(callResult.split(os.linesep))
                
            fileHandler.write(">")
            fileHandler.write(item)
            fileHandler.write(os.linesep)
            fileHandler.write(parseResult)
            
            if item!=lastItemInList:
                fileHandler.write(os.linesep)
        
        fileHandler.close()

    except Exception:
        raise Exception(traceback.format_exc())

#============================
#Amino Percentage based
# a Sequence and a Letter
#============================
def calcAminoPercentage(seq,letter):
  counter=0
  for alphabet in seq:
    if (alphabet==letter):
      counter=counter+1
  
  return ((counter/len(seq))*100)

#============================
#Rounds Floating Points Number
#============================
def roundFloatingpoint(num):
  return (np.round(num*1000)/1000)

#============================
#Removes Undesired Character
#============================
def removeSpaceNewLine(seq):
  return ((seq.replace('\n','')).replace(' ',''))

#============================
# Creating Directory (if does not exist)
# Clearing the file (if already exist) 
#============================
def clearFile(fileAddress):
    #Trying to create directories (If does not exist)
    try:
        open((os.getcwd()+fileAddress), 'w').close()
    except:
        newPath=(fileAddress).split("/")
        path = ("/".join(newPath[:(len(newPath)-1)]))
        os.mkdir(os.getcwd()+path)
    finally:
        open((os.getcwd()+fileAddress), 'w').close()

#============================
#Calculates AAC(each Sequence)
#============================
def calcSeqAAC(sequence,letters):
    sequence = removeSpaceNewLine(sequence)
    aminoPercentage=[]

    for amino in letters:

        aminoPercentage.append(
            roundFloatingpoint(
                calcAminoPercentage(sequence,amino)))

    return aminoPercentage

#============================
#Calculates AAC(each File)
#============================
def calcAAC(aminoLetters,source,label,destination):
    try:
        # Reading Source Transporter
        sourceHandler=open(source,'r')
        sourceData=(sourceHandler.read()).split("\n")
        sourceHandler.close()

        #Calculating, Writing to File
        for line in sourceData:
            if '>' not in line:
                #Calculating the AAC feature and Writes it to aac.csv
                destination.write('\n'+
                    (str(
                        calcSeqAAC(line,aminoLetters)).replace('[','')).replace(']','')+","+label)
            # else:
            #     if '>' in line:
            #         log("calculating AAC for "+ line)

    except Exception:
        log(traceback.format_exc())
        raise Exception(traceback.format_exc())
    
        
#============================
#Extract AAC
#============================
def extractAAC(config,dataset,feature):
    
    try:
        aminoLetters=['A','C','D','E','F','G','H','I','K','L','M','N','P','Q','R','S','T','V','W','Y']

        source = config["datasetPath"].format(dataset)    
        destination1= config["featuresPath"].format(dataset,feature+"7.csv")
        destination2= config["featuresPath"].format(dataset,feature+"8.csv")

        # Creating Directory (if does not exist)
        #Clearing the file (if already exist)
        clearFile(destination1)
        clearFile(destination2)
        
        #Logging
        log("Source : "+source)
        log("destination : "+destination1)
        log("destination : "+destination2)

        #List DataFiles from the Source
        log("Listing data files from "+source)
        trasnporters=[]
        nonTransporters=[]
        for file in os.listdir(os.getcwd()+source):
            if "nonTransporter" in file:
                nonTransporters.append(file[:-6])
            else:
                if "fasta" in file:
                    trasnporters.append(file[:-6])
        
        
        #AAC1
        # Transporters (amino-cation-anion-electron-sugar-protein-other)
        # Opening Destination1 and Printing the Header
        aac1=open((os.getcwd()+destination1), 'a')
        aac1.write((str(aminoLetters).replace('[','')).replace(']','')+",Label")

        log("Extraicting AAC from "+dataset+" for 7 classes")
        for transporter in trasnporters:
            sourceFile=os.getcwd()+config["datasetPath"].format(dataset)+transporter+".fasta"
            calcAAC(aminoLetters,sourceFile,transporter,aac1)
        
        #Closing destination1
        aac1.close()

        #AAC2
        # Transporter vs non-Transporters
        # Opening Destination1 and Printing the Header
        aac2=open((os.getcwd()+destination2), 'a')
        aac2.write((str(aminoLetters).replace('[','')).replace(']','')+",Label")

        log("Extraicting AAC from "+dataset+" for 8 classes(Including non-transporters)")
        for transporter in trasnporters:
            sourceFile=os.getcwd()+config["datasetPath"].format(dataset)+transporter+".fasta"
            calcAAC(aminoLetters,sourceFile,"transporter",aac2)
        
        sourceFile=os.getcwd()+config["datasetPath"].format(dataset)+"nonTransporter"+".fasta"
        calcAAC(aminoLetters,sourceFile,"nonTransporter",aac2)
        
        #Closing destination2
        aac2.close()

    except Exception:
        log(traceback.format_exc())
        raise Exception(traceback.format_exc())
