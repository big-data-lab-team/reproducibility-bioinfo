#============================
#PACKAGES
#============================
import argparse
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
        #Checking for right argument from user
        parser = argparse.ArgumentParser(description='Extracting Features from Dataset')
        parser.add_argument('feature', type=str, help='Feature to Extract')
        parser.add_argument('dataset', type=str, help='Dataset from which the feature would be Extracted from (trainTest or Independent)')
        parser.parse_args()

        #Logging start of Program
        feature = parser.parse_args().feature
        dataset = parser.parse_args().dataset
        
        log(time.strftime("%m/%d/%Y, %H:%M:%S",time.localtime()))
        # log("Running extractFeature.py  << feature >> "+feature+" << dataset >> "+dataset)
        
        #Loading Json
        config=readFile("/config.json")
        
        #Config Json File
        configJson = json.loads(config)  

        #Features
        if feature=='aac':
            extractAAC(configJson,dataset,feature)
        
    except Exception:
        log("[ "+sys.argv[1]+" ] Feature Extraction Process Failed!!")
        log(traceback.format_exc())

if __name__ == "__main__":
    main()