#============================
#PACKAGES
#============================
import os
import json
import requests
import traceback
import time

#============================
#LOG HANDLER
#============================
def log(message):
    try:
        logHandler=open((os.getcwd()+"/log.log"), 'a')
        print(message)
        logHandler.write(message)
        logHandler.write("\n")
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
        return [False,rawFile]
    except Exception:
        log(traceback.format_exc())
        return [True,traceback.format_exc()]
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
            return [False,response.text]
        else:
            raise Exception(
                'Online Request Status for {} is {}'.format(
                    pFile+"."+extension,response.status_code))

    except Exception:
        log(traceback.format_exc())
        return [True,traceback.format_exc()]
#============================
#FASTA PARSER
#============================
def parseFasta(content):
    try:
        sequence = ("".join(content[1:]).replace("\n","")).replace(" ","")
        log("Processing Data for Sequence...")
        return [False,sequence]
    except Exception:
        log(traceback.format_exc())
        return [True,traceback.format_exc()]
