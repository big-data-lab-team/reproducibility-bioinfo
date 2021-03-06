# cSpell:disable
# ============================
# PACKAGES
# ============================

import os
import requests
import traceback
import time
import numpy as np
import pandas as pd
from aaindex import AAIndex

# ============================
# SETTINGS
# ============================
config = {
    "ncbi": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=protein&id={}&rettype={}",
    "datasetPath": os.path.join(os.getcwd(), "dataset", "{}"),
    "downloadPath": os.path.join(os.getcwd(), "dataset", "{}", "{}"),
    "featuresPath": os.path.join(os.getcwd(), "features", "{}", "{}"),
    "SVMLightFeaturesPath": os.path.join(os.getcwd(), "svmLight", "features","{}", "{}"),
    "pssmPath": os.path.join(os.getcwd(), "pssm", "{}"),
}


# ============================
# LOG HANDLER
# ============================


def log(message):
    try:
        logHandler = open(os.path.join(os.getcwd(), "log.log"), 'a')
        print(message)
        logHandler.write(message)
        logHandler.write(os.linesep)
        logHandler.close()
    except Exception:
        print(traceback.format_exc())

# ============================
# FILE READER
# ============================


def readFile(fName):
    try:
        fileHandler = open(fName, 'r')
        log("Loading "+fName+" ...")
        rawFile = fileHandler.read()
        fileHandler.close()
        return rawFile
    except Exception:
        raise Exception(traceback.format_exc())
# ============================
# PROTEIN FASTA DOWNLOADER
# ============================


def getFileFromURL(webAddress, pFile, extension):
    try:
        URL = webAddress.format(pFile, extension)
        # log("Sending request to ... ")
        # log(URL)
        response = requests.get(URL)
        time.sleep(1)
        if response.ok:
            return response.text
        else:
            raise Exception(
                'Online Request Status for {} is {}'.format(
                    pFile+"."+extension, response.status_code))

    except Exception:
        raise Exception(traceback.format_exc())
# ============================
# FASTA PARSER
# ============================


def parseFasta(content):
    try:
        sequence = ("".join(content[1:]).replace(
            os.linesep, "")).replace(" ", "")
        log("Processing Downloaded Data for Sequence ...")
        return sequence
    except Exception:
        raise Exception(traceback.format_exc())


# ============================
# DOWNLOAD/PARSE/WRITE TO FILE
# ============================
def downloadCreateDataList(itemList, site, format, dataPath):
    try:
        try:
            open(dataPath, 'w').close()

        except Exception:
            newPath = (dataPath).split((os.sep))
            path = ((os.sep).join(newPath[:(len(newPath)-1)]))
            os.makedirs(path, mode=0o777, exist_ok=False)

        finally:
            fileHandler = open(dataPath, 'a')

        lastItemInList = itemList[len(itemList)-1]

        for item in itemList:
            log("Downloading ... "+item)
            callResult = getFileFromURL(site, item, format)

            parseResult = parseFasta(callResult.split(os.linesep))

            fileHandler.write(">")
            fileHandler.write(item)
            fileHandler.write(os.linesep)
            fileHandler.write(parseResult)

            if item != lastItemInList:
                fileHandler.write(os.linesep)

        fileHandler.close()

    except Exception:
        raise Exception(traceback.format_exc())


# ============================
# Removes Undesired Character
# ============================


def removeSpaceNewLine(seq):
    return ((seq.replace(os.linesep, '')).replace(' ', ''))

# ============================
# Creating Directory (if does not exist)
# Clearing the file (if already exist)
# ============================


def clearFile(fileAddress):
        # Trying to create directories (If does not exist)
    try:
        open(fileAddress, 'w').close()
    except:
        newPath = (fileAddress).split((os.sep))
        path = ((os.sep).join(newPath[:(len(newPath)-1)]))
        os.makedirs(path, mode=0o777, exist_ok=False)
    finally:
        open(fileAddress, 'w').close()

# ============================
# Calculates AAC(each Sequence)
# ============================


def calcSeqAAC(sequence, letters):
    sequence = removeSpaceNewLine(sequence)
    aminoPercentage = [(np.round(
        ((sequence.count(amino))/len(sequence))*100, 3)) for amino in letters]

    return aminoPercentage

# ============================
# Calculates AAC(each File)
# ============================


def calcAAC(aminoLetters, source, label, destination):
    try:
        # Reading Source Transporter
        sourceHandler = open(source, 'r')
        sourceData = (sourceHandler.read()).split(os.linesep)
        sourceHandler.close()

        # Calculating, Writing to File
        for line in sourceData:
            if '>' not in line:
                # Calculating the AAC feature and Writes it to aac.csv
                destination.write(os.linesep +
                                  (str(
                                      calcSeqAAC(line, aminoLetters)).replace('[', '')).replace(']', '')+","+label)
            # else:
            #     if '>' in line:
            #         log("calculating AAC for "+ line)

    except Exception:
        log(traceback.format_exc())
        raise Exception(traceback.format_exc())


# ============================
# Extract AAC
# ============================
def extractAAC(dataset, feature):

    try:
        aminoLetters = ['A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K',
                        'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'Y']

        source = config["datasetPath"].format(dataset)
        destination1 = config["featuresPath"].format(dataset, feature+"7.csv")
        destination2 = config["featuresPath"].format(dataset, feature+"8.csv")

        # Creating Directory (if does not exist)
        # Clearing the file (if already exist)
        clearFile(destination1)
        clearFile(destination2)

        # Logging
        log("Source : "+source)
        log("destination : "+destination1)
        log("destination : "+destination2)

        # List DataFiles from the Source
        log("Listing data files from "+source)

        trasnporters = []
        nonTransporters = []

        for file in os.listdir(source):
            if "nonTransporter" in file:
                nonTransporters.append(file[:-6])
            else:
                if "fasta" in file:
                    trasnporters.append(file[:-6])

        # AAC1
        # Transporters (amino-cation-anion-electron-sugar-protein-other)
        # Opening Destination1 and Printing the Header
        aac1 = open(destination1, 'a')
        aac1.write((str(aminoLetters).replace(
            '[', '')).replace(']', '')+",Label")

        log("Extracting AAC from "+dataset+" for 7 classes")
        for transporter in trasnporters:
            sourceFile = os.path.join(config["datasetPath"].format(
                dataset), (transporter+".fasta"))
            calcAAC(aminoLetters, sourceFile, transporter, aac1)

        # Closing destination1
        aac1.close()

        # AAC2
        # Transporter vs non-Transporters
        # Opening Destination1 and Printing the Header
        aac2 = open(destination2, 'a')
        aac2.write((str(aminoLetters).replace(
            '[', '')).replace(']', '')+",Label")

        log("Extracting AAC from "+dataset +
            " for 8 classes(Including non-transporters)")
        for transporter in trasnporters:
            sourceFile = os.path.join(config["datasetPath"].format(
                dataset), (transporter+".fasta"))
            calcAAC(aminoLetters, sourceFile, transporter, aac2)

        sourceFile = os.path.join(config["datasetPath"].format(
            dataset), "nonTransporter.fasta")
        calcAAC(aminoLetters, sourceFile, "nonTransporter", aac2)

        # Closing destination2
        aac2.close()

    except Exception:
        log(traceback.format_exc())
        raise Exception(traceback.format_exc())

# ============================
# DPC FEATURE
# ============================
# CALC DPC
# ============================


def calcDPC(diPeptids, source, label, destination):
    try:
        _in = open(source, 'r')
        _sequences = (_in.read()).split(os.linesep)
        _in.close()

        for line in _sequences:
            if '>' not in line:
                sequence = removeSpaceNewLine(line)
                _length = (len(sequence))-1

                results = []
                for item in diPeptids:
                    counter = 0
                    for ii in range(_length):
                        if (sequence[ii]+sequence[ii+1]) == item:
                            counter = counter+1

                    results.append(np.round((counter/(_length))*100, 3))

                destination.write(os.linesep)

                # if _label != "nonTransporter":
                #     _label="transporter"

                destination.write((str(results).replace(
                    '[', '')).replace(']', '')+","+label)

    except Exception:
        log(traceback.format_exc())
        raise Exception(traceback.format_exc())

# ============================
# Extract DPC
# ============================


def extractDPC(dataset, feature):

    try:
        aminoLetters = ['A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K',
                        'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'Y']

        _diPeptids = []
        for first in aminoLetters:
            for second in aminoLetters:
                _diPeptids.append((first+second))

        source = config["datasetPath"].format(dataset)
        destination1 = config["featuresPath"].format(dataset, feature+"7.csv")
        destination2 = config["featuresPath"].format(dataset, feature+"8.csv")

        # Creating Directory (if does not exist)
        # Clearing the file (if already exist)
        clearFile(destination1)
        clearFile(destination2)

        # Logging
        log("Source : "+source)
        log("destination : "+destination1)
        log("destination : "+destination2)

        # List DataFiles from the Source
        log("Listing data files from "+source)
        trasnporters = []
        nonTransporters = []

        for file in os.listdir(source):
            if "nonTransporter" in file:
                nonTransporters.append(file[:-6])
            else:
                if "fasta" in file:
                    trasnporters.append(file[:-6])

        # DPC1
        # Transporters (amino-cation-anion-electron-sugar-protein-other)
        # Opening Destination1 and Printing the Header
        dpc1 = open(destination1, 'a')
        dpc1.write((str(_diPeptids).replace(
            '[', '')).replace(']', '')+",Label")

        log("Extracting DPC from "+dataset+" for 7 classes")
        for transporter in trasnporters:
            sourceFile = os.path.join(config["datasetPath"].format(
                dataset), (transporter+".fasta"))
            calcDPC(_diPeptids, sourceFile, transporter, dpc1)

        # Closing destination1
        dpc1.close()

        # DPC2
        # Transporter vs non-Transporters
        # Opening Destination1 and Printing the Header
        dpc2 = open(destination2, 'a')
        dpc2.write((str(_diPeptids).replace(
            '[', '')).replace(']', '')+",Label")

        log("Extracting DPC from "+dataset +
            " for 8 classes(Including non-transporters)")
        for transporter in trasnporters:
            sourceFile = os.path.join(config["datasetPath"].format(
                dataset), (transporter+".fasta"))
            calcDPC(_diPeptids, sourceFile, transporter, dpc2)

        sourceFile = os.path.join(config["datasetPath"].format(
            dataset), ("nonTransporter"+".fasta"))
        calcDPC(_diPeptids, sourceFile, "nonTransporter", dpc2)

        # Closing destination2
        dpc2.close()

    except Exception:
        log(traceback.format_exc())
        raise Exception(traceback.format_exc())


# ============================
# PHC FEATURE
# ============================
# Extract PHC
# ============================
def calcPHC(phc, source, label, destination):
    try:
        _in = open(source, 'r')
        _sequences = (_in.read()).split(os.linesep)
        _in.close()

        for line in _sequences:
            if '>' not in line:

                sequence = removeSpaceNewLine(line)
                _length = len(sequence)

                _percentage = []
                for _property in phc:

                    _percentage.append(
                        np.round((sum([sequence.count(_item) for _item in _property])/_length)*100, 3))

                destination.write(os.linesep)

                # if label != "nonTransporter":
                #     label="transporter"

                destination.write((str(_percentage).replace(
                    '[', '')).replace(']', '')+","+label)

    except Exception:
        log(traceback.format_exc())
        raise Exception(traceback.format_exc())

# ============================
# Extract PHC
# ============================


def extractPHC(dataset, feature):
    try:
        phc_items = [
            "charged", "aliphatic", "aromatic", "polar",
            "neutral", "hydrophobic", "positively_charged",
            "negatively_charged", "tiny", "small", "large"
        ]
        _phc = [
            ["D", "E", "K", "H", "R"], ["I", "L", "V"],
            ["F", "H", "W", "Y"], ["D", "E", "R", "K", "Q", "N"],
            ["A", "G", "H", "P", "S", "T", "Y"], [
                "C", "F", "I", "L", "M", "V", "W"],
            ["K", "R", "H"], ["D", "E"], ["A", "C", "D", "G", "S", "T"],
            ["E", "H", "I", "L", "K", "M", "N", "P", "Q", "V"], ["F", "R", "W", "Y"]
        ]

        source = config["datasetPath"].format(dataset)
        destination1 = config["featuresPath"].format(dataset, feature+"7.csv")
        destination2 = config["featuresPath"].format(dataset, feature+"8.csv")

        # Creating Directory (if does not exist)
        # Clearing the file (if already exist)
        clearFile(destination1)
        clearFile(destination2)

        # Logging
        log("Source : "+source)
        log("destination : "+destination1)
        log("destination : "+destination2)

        # List DataFiles from the Source
        log("Listing data files from "+source)
        trasnporters = []
        nonTransporters = []

        for file in os.listdir(source):
            if "nonTransporter" in file:
                nonTransporters.append(file[:-6])
            else:
                if "fasta" in file:
                    trasnporters.append(file[:-6])

        # PHC1
        # Transporters (amino-cation-anion-electron-sugar-protein-other)
        # Opening Destination1 and Printing the Header
        phc1 = open(destination1, 'a')
        phc1.write((str(phc_items).replace('[', '')).replace(']', '')+",Label")

        log("Extracting PHC from "+dataset+" for 7 classes")
        for transporter in trasnporters:
            sourceFile = os.path.join(config["datasetPath"].format(
                dataset), (transporter+".fasta"))
            calcPHC(_phc, sourceFile, transporter, phc1)

        # Closing destination1
        phc1.close()

        # PHC2
        # Transporter vs non-Transporters
        # Opening Destination1 and Printing the Header
        phc2 = open(destination2, 'a')
        phc2.write((str(phc_items).replace('[', '')).replace(']', '')+",Label")

        log("Extracting PHC from "+dataset +
            " for 8 classes(Including non-transporters)")
        for transporter in trasnporters:
            sourceFile = os.path.join(config["datasetPath"].format(
                dataset), (transporter+".fasta"))
            calcPHC(_phc, sourceFile, transporter, phc2)

        sourceFile = os.path.join(config["datasetPath"].format(
            dataset), ("nonTransporter"+".fasta"))
        calcPHC(_phc, sourceFile, "nonTransporter", phc2)

        # Closing destination2
        phc2.close()

    except Exception:
        log(traceback.format_exc())
        raise Exception(traceback.format_exc())

# ============================
# AAIndex FEATURE
# ============================
# Extract AAIndex
# ============================
def calcAAIndex(AAIndex, source, label, destination):
    try:
        _in = open(source, 'r')
        _sequences = (_in.read()).split(os.linesep)
        _in.close()

        for line in _sequences:
            if '>' not in line:

                sequence = removeSpaceNewLine(line)
                _length = len(sequence)

                _results = []
                for item in AAIndex:
                    val=AAIndex.get(item)
                    _results.append((sum([val.setdefault(let, 0.0) for let in line ]))/_length)


                destination.write(os.linesep)

                # if label != "nonTransporter":
                #     label="transporter"

                destination.write((str(_results).replace(
                    '[', '')).replace(']', '')+","+label)

    except Exception:
        log(traceback.format_exc())
        raise Exception(traceback.format_exc())

# ============================
# Extract AAIndex
# ============================


def extractAAIndex(dataset, feature):
    try:
        aaindex_items=[
        "k0","ht","hp","p","phi","pk","mw","bl","rf","mu","hnc","esm","el","et",
        "pa","pb","pt","pc","ca","F","br","ra","ns","an","ac","am","v0","nm","nl",
        "hgm","asad","asan","dasa","dgh","ghd","ghn","dhh","tdsh","dcph","dgc","dhc",
        "tdsc","dg","dh","tds","v","s","f","pfs"
        ]

        source = config["datasetPath"].format(dataset)
        destination1 = config["featuresPath"].format(dataset, feature+"7.csv")
        destination2 = config["featuresPath"].format(dataset, feature+"8.csv")

        # Creating Directory (if does not exist)
        # Clearing the file (if already exist)
        clearFile(destination1)
        clearFile(destination2)

        # Logging
        log("Source : "+source)
        log("destination : "+destination1)
        log("destination : "+destination2)

        # List DataFiles from the Source
        log("Listing data files from "+source)
        trasnporters = []
        nonTransporters = []

        for file in os.listdir(source):
            if "nonTransporter" in file:
                nonTransporters.append(file[:-6])
            else:
                if "fasta" in file:
                    trasnporters.append(file[:-6])

        # AAIndex1
        # Transporters (amino-cation-anion-electron-sugar-protein-other)
        # Opening Destination1 and Printing the Header
        AAIndex1 = open(destination1, 'a')
        AAIndex1.write((str(aaindex_items).replace('[', '')).replace(']', '')+",Label")

        log("Extracting AAIndex from "+dataset+" for 7 classes")
        for transporter in trasnporters:
            sourceFile = os.path.join(config["datasetPath"].format(
                dataset), (transporter+".fasta"))
            calcAAIndex(AAIndex, sourceFile, transporter, AAIndex1)

        # Closing destination1
        AAIndex1.close()

        # AAIndex2
        # Transporter vs non-Transporters
        # Opening Destination1 and Printing the Header
        AAIndex2 = open(destination2, 'a')
        AAIndex2.write((str(aaindex_items).replace('[', '')).replace(']', '')+",Label")

        log("Extracting AAIndex from "+dataset +
            " for 8 classes(Including non-transporters)")
        for transporter in trasnporters:
            sourceFile = os.path.join(config["datasetPath"].format(
                dataset), (transporter+".fasta"))
            calcAAIndex(AAIndex, sourceFile, transporter, AAIndex2)

        sourceFile = os.path.join(config["datasetPath"].format(
            dataset), ("nonTransporter"+".fasta"))
        calcAAIndex(AAIndex, sourceFile, "nonTransporter", AAIndex2)

        # Closing destination2
        AAIndex2.close()

    except Exception:
        log(traceback.format_exc())
        raise Exception(traceback.format_exc())

# ============================
# PSSM FEATURE
# ============================
# PSSM to Feature
# ============================
def pssm_to_feature(filename):

    handler = open(filename, "r")
    data = handler.read().split(os.linesep)
    handler.close()    

    seq_len = int(data[len(data)-1])

    data_by_space = [data[x].split(" ") for x in range(len(data))]
    data_clean = [[data_by_space[y][k] for k in range(
        len(data_by_space[y])) if data_by_space[y][k] != ""] for y in range(2, (2+1+seq_len))]

    # Headers for the table
    header = [(["ID", "Seq"]+data_clean[0])[c] for c in range(0, 22)]

    data_trimed = [[data_clean[b][c]
                    for c in range(0, 22)] for b in range(1, len(data_clean))]
    
    # Data to Table
    table = pd.DataFrame(data_trimed, columns=header)
    table.drop(['ID'], axis=1, inplace=True)
    
    # String to number
    headers = table.columns
    for i in range(1, len(headers)):
        table[headers[i]] = pd.to_numeric(table[headers[i]], errors='coerce')
    
    # seq = table["Seq"].unique()
    # dd = pd.concat([table[table["Seq"] == kk].groupby(
    #     'Seq').aggregate(sum) for kk in seq], axis=0, sort=True)

    _all_aminos=['A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 'N', 'P', 'Q',
       'R', 'S', 'T', 'V', 'W', 'Y']
    
    dd=pd.DataFrame(data=None)

    for seq in _all_aminos:
        _temp=table[table["Seq"] == seq].groupby('Seq').aggregate(sum)
        if _temp.empty:
            _temp.loc[seq]=0
        
        if  seq=='Y':
            dd=pd.concat([dd,_temp],axis=0,sort=True)
        else:
            dd=pd.concat([dd,_temp],axis=0)
    
    
    dd=dd.sort_values(by=['Seq'])
    dd=dd/seq_len
    
    _max=dd.values.max()
    _min=dd.values.min()
    
    dd=dd-_min
    dd=dd/(_max-_min)
    
    return(dd)
# ============================
# PSSM FEATURE
# ============================
# CALC PSSM
# ============================
def calcPSSM(source,num_of_classes,pssm_csv):
    try:
        _pssms= os.listdir( os.path.join(source,num_of_classes)) # PSSM 2 / 7
        lableList=[label  for label in _pssms if "store" not in label.lower()]
        # print(lableList)

        for label in lableList:
            label_pssms = os.listdir( os.path.join(source,num_of_classes,label)) # PSSM 2 / 7 / amino
            pssm_files=[_file for _file in label_pssms if "store" not in _file.lower()]
            
            # print (len(pssm_files))
            # print (pssm_files)
            
            for _file in pssm_files:
                _file_address=os.path.join(source,num_of_classes,label,_file)
                res =  pssm_to_feature(_file_address)
                res_values=res.values
                flated=[res_values[i][j] for i in range(len(res_values)) for j in range(len(res_values[i]))]
                
                # print(flated[:3])
                pssm_csv.write(os.linesep)

                # if label != "nonTransporter":
                #     label="transporter"

                pssm_csv.write((str(flated).replace(
                    '[', '')).replace(']', '')+","+label)

    except Exception:
        log(traceback.format_exc())
        raise Exception(traceback.format_exc())

# ============================
# Extract PSSM
# ============================


def extractPSSM(dataset, feature):
    try:

        _classes=["7","8"]
        _iterations=["2","3"]
        
        aminoLetters = ['A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 
        'L', 'M', 'N', 'P', 'Q','R', 'S', 'T', 'V', 'W', 'Y']
        _pssm_headers = [(first+second)for first in aminoLetters for second in aminoLetters]

        for _class in _classes:
            for _iter in _iterations:
                
                log("Genrating {} iteration PSSM .csv file for {} classes".format(_iter,_class))
                source = config["pssmPath"].format("pssm"+_iter) # PSSM 2
                destination = config["featuresPath"].format(dataset, feature+_class+_iter+".csv") #PSSM 72
                clearFile(destination)

                log("Source : "+source)
                log("destination : "+destination)

                _pssm_csv = open(destination, 'a')
                _pssm_csv.write((str(_pssm_headers).replace('[', '')).replace(']', '')+",Label")

                calcPSSM(source,_class, _pssm_csv)

                _pssm_csv.close()


    except Exception:
        log(traceback.format_exc())
        raise Exception(traceback.format_exc())