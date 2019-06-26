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
        log("Sending request to ... ")
        log(URL)
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
        log("Processing Data for Sequence...")
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
            log(item)
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
