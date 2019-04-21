#============================
#PACKAGES
#============================
import sys
import json
import time
import traceback
from helpers import extractAAC,log,readFile


#============================
#MAIN
#============================
def main():

    #Extracting feature from Dataset files
    try:
        #Logging start of Program
        feature = sys.argv[1]
        dataset = sys.argv[2]
        
        log(time.strftime("%m/%d/%Y, %H:%M:%S",time.localtime()))
        log("Running extractFeature.py  << feature >> "+feature+" << dataset >> "+dataset)
        
        #Loading Json
        err,config=readFile("/config.json")
        if not err:
            #Config Json File
            configJson = json.loads(config)  
    
            #Features
            if feature=='aac':
                extractAAC(configJson,dataset,feature)
            
        else:
            log("ERROR: Reading CONFIG file")
            log(traceback.format_exc())
        
    except Exception:
        log("[ "+sys.argv[1]+" ] Feature Extraction Process Failed!!")
        log(traceback.format_exc())

if __name__ == "__main__":
    main()