#============================
#PACKAGES
#============================
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
        err,trainTest=readFile(trainTestList)
        trainTestJson=json.loads(trainTest)
        
        if not err:
            
            for item in trainTestJson:
                downloadCreateDataList(trainTestJson[item],ncbi,'fasta',downloadPath.format(item))
        else:
                log(trainTestJson)
        
    except Exception:
        log(traceback.format_exc())

    #Feature Generation
        
    #Training the SVM on train_test Data

    #Downloading the DATA for Independent Dataset

    #Testing the algorithm on the INdependent Dataset

if __name__ == "__main__":
    main()