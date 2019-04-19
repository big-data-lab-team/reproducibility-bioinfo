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

