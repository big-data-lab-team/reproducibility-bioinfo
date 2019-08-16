# cSpell:disable
# ============================
# PACKAGES
# ============================
import argparse
import sys
import json
import time
import traceback
from helpers import extractAAC, log, readFile, extractDPC, extractPHC


# ============================
# MAIN
# ============================
def main():

    # Extracting feature from Dataset files
    try:
        # Checking for right argument from user
        parser = argparse.ArgumentParser(
            description='Extracting Features from Dataset')
        parser.add_argument('feature', type=str, help='Feature to Extract')
        parser.add_argument(
            'dataset', type=str, help='Dataset from which the feature would be Extracted from (trainTest or Independent)')
        parser.parse_args()

        # Logging start of Program
        feature = parser.parse_args().feature
        dataset = parser.parse_args().dataset

        log(time.strftime("%m/%d/%Y, %H:%M:%S", time.localtime()))

        # Features
        # AAC (Amino-acid Composition)
        if feature == 'aac':
            extractAAC(dataset, feature)
            log("AAC being extracted from [ "+dataset+" ] successfully!!!")
        # DPC (Di-peptid composition)
        elif feature == 'dpc':
            extractDPC(dataset, feature)
            log("DPC being extracted from [ "+dataset+" ] successfully!!!")
        # PHC (Physico-Chemical Composition)
        elif feature == 'phc':
            extractPHC(dataset, feature)
            log("PHC being extracted from [ "+dataset+" ] successfully!!!")

    except Exception:
        log("[ "+feature+" ] Feature Extraction Process Failed!!")
        log(traceback.format_exc())


if __name__ == "__main__":
    main()
