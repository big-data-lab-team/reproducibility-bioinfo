import os
import time
import traceback
import argparse
import pandas as pd
from helpers import log

config = {
    "featuresPath": os.path.join("features", "{}", "{}"),
    "SVMLightFeaturesPath": os.path.join("svmLight", "features","{}","{}","{}", "{}")
}

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

def rewrite_label(_item,_class):
    _temp=_temp=_item[['Label']].copy()  
    del _item['Label']  
    _temp[_temp['Label']!=_class]="-1"
    _temp[_temp['Label']==_class]="+1"
    return (pd.concat([_temp,_item],axis=1))

def svmlight_feature_to_file(fileAddress,item):
    _file = open(fileAddress, 'w').close()
    _file = open(fileAddress, 'a')
    
    for _row_index,_row in enumerate(item.values):
        for _index in range(len(_row)):
            if (_index>0):
                _file.write(" "+str(_index)+":")
                _file.write( str(round(_row[_index],3) ) )
            else:
                _file.write( str(_row[_index] ) )

        if _row_index!=(len(item.values)-1):
            _file.write(os.linesep)
    
    _file.close()

def processWrite(actual_test,actual_test_path):
    _headers=actual_test.columns[actual_test.columns!='Label'].values
    for i, row in actual_test.iterrows():
        for _header in _headers:
            actual_test.at[i,_header] = round(actual_test.at[i,_header],3)
    actual_test.to_csv(actual_test_path,index=False)

def main():
    try:
        # Checking for right argument from user
        parser = argparse.ArgumentParser(
            description='Converting CSV feature to SVM_Light feature format')
        parser.add_argument('feature', type=str, help='Feature (CSV) to convert (aac7,aac8,etc.)')
        parser.add_argument(
            'dataset', type=str, help='Dataset from which the feature would be Extracted from (trainTest or Independent)')
        parser.parse_args()

        # Logging start of Program
        feature = parser.parse_args().feature
        dataset = parser.parse_args().dataset

        log(time.strftime("%m/%d/%Y, %H:%M:%S", time.localtime()))

        # dataset="trainTest"
        # feature="aac8"
        source = config["featuresPath"].format(dataset, feature+".csv")

        log("Converting [ "+feature+" ] to SVM_Light feature from [ "+dataset+" ]")

        # Loading the feature file
        data=pd.read_csv(source)
        # Creating the unique class names and then sorting
        _classes=sorted(data['Label'].unique())
        # Putting each class in a differnet data frame
        _data_by_class=[data[data['Label']==_class] for _class in _classes ]

        
        _folds_by_class=[]
        _num_of_folds=5
        # Creating folds from each class
        for _item in _data_by_class:
            co=len(_item)//_num_of_folds
            _folds_by_class.append([_item[(i*co):((i*co)+co)] for i in range(_num_of_folds)])
        
        # Creating Folds from the whole feature
        # by concatenation of each fold from each class
        _folds=[
            pd.concat([_folds_by_class[i][j] for i in range(len(_folds_by_class))]) 
            for j in range(_num_of_folds)
            ]


        # Train,Test out of 5 folds
        _train_test=[]
        for ii in range(_num_of_folds):
            _test =_folds[ii]
            _train=pd.concat([_folds[xx] for xx in range(_num_of_folds) if xx!=ii])
            _train_test.append([_train,_test])

        # Export folds into corresponding svm_light feature
        # Each fold will be converted into 7 classes
        # Because the method for SVM is ONE vs ALL
        
        for _fold in range(_num_of_folds):
            log("Processing fold [ "+str(_fold)+" ]")
            # print(_classes)
            for _class in _classes:
                train,test = _train_test[_fold]
                # Writing actual train,test to the folder
                actual_test_path=config['SVMLightFeaturesPath'].format(dataset,feature,"fold"+str(_fold),"test.csv")
                actual_train_path=config['SVMLightFeaturesPath'].format(dataset,feature,"fold"+str(_fold),"train.csv")
                clearFile(actual_test_path)
                clearFile(actual_train_path)
                processWrite(test.copy(),actual_test_path)
                processWrite(train.copy(),actual_train_path)
                # converting label names into +1 and -1
                _train=rewrite_label(train.copy(),_class)
                _test=rewrite_label(test.copy(),_class)
                # converting the data to the required format
                path=config['SVMLightFeaturesPath'].format(dataset,feature,"fold"+str(_fold),_class)
                os.makedirs(path, mode=0o777, exist_ok=True)
                svmlight_feature_to_file(os.path.join(path,"train.dat"),_train)
                svmlight_feature_to_file(os.path.join(path,"test.dat"),_test)

        # log("[ "+feature+" ] successfully being converted!")
    
    except Exception:
        log("[ "+feature+" ] Conversion Process Failed!!")
        log(traceback.format_exc())

if __name__ == "__main__":
    main()