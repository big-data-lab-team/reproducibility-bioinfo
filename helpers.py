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
