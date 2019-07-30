# cSpell:disable
# ============================
# PACKAGES
# ============================
import argparse
import os
import sys
import time
import json
import traceback
from helpers import downloadCreateDataList, log, readFile, config

# ============================
# MAIN
# ============================


def main():
    # Checking for right argument from user
    parser = argparse.ArgumentParser(
        description='Downloading Proteins from NCBI')
    parser.add_argument('List_File_Name', type=str,
                        help='Input Protein List in (Json)')
    parser.parse_args()

    _list = parser.parse_args().List_File_Name

    # Downloading the DATA for DATASET
    try:
        # Logging start of Program
        log(time.strftime("%m/%d/%Y, %H:%M:%S", time.localtime()))

        # Loading The Download List
        downloadListAddress = config["datasetPath"].format(_list+".json")
        downloadList = readFile(downloadListAddress)
        downloadListJson = json.loads(downloadList)

        for item in downloadListJson:
            try:
                _path = config["downloadPath"].format(_list, (item+".fasta"))
                open(_path, 'r').close()
                log(item+".fasta >> already downloaded!")

            except Exception:
                downloadCreateDataList(
                    downloadListJson[item],
                    config["ncbi"],
                    'fasta',
                    config["downloadPath"].format(_list, (item+".fasta")))

        log("[ "+_list+" ] Downloaded Succesfully!!")

    except Exception:
        log("[ "+_list+" ] Download Process Failed!!")
        log(traceback.format_exc())


if __name__ == "__main__":
    main()
