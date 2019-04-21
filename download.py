#============================
#PACKAGES
#============================
import sys
from helpers import *

#============================
#GLOBALS
#============================
trainTestList="/dataset/trainTestList.json"
ncbi="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=protein&id={}&rettype={}"
downloadPath="/dataset/train_test/{}.fasta"

#============================
#MAIN
#============================
def main():

    #Downloading the DATA for DATASET
    try:
        #Loading Json
        err,config=readFile("/config.json")
        if not err:
            configJson = json.loads(config)    
            downloadListAddress = configJson["downloadList"].format(sys.argv[1])
            
            #Loading The Download List
            err,downloadList = readFile(downloadListAddress)
            
            if not err:
                downloadListJson=json.loads(downloadList)
                
                for item in downloadListJson:
                    downloadCreateDataList(
                        downloadListJson[item],
                        configJson["ncbi"],
                        'fasta',
                        configJson["downloadPath"].format(sys.argv[1],item))
                
                log("[ "+sys.argv[1]+" ] Downloaded Succesfully!!")

            else:
                log("ERROR: Reading DOWNLOAD List")
                log(traceback.format_exc())    
            
        else:
            log("ERROR: Reading CONFIG file")
            log(traceback.format_exc())
        
    except Exception:
        log("[ "+sys.argv[1]+" ] Download Process Failed!!")
        log(traceback.format_exc())

    #Feature Generation
    #Training the SVM on train_test Data
    #Downloading the DATA for Independent Dataset
    #Testing the algorithm on the INdependent Dataset

if __name__ == "__main__":
    main()