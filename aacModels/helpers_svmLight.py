# cSpell:disable
# ============================
# PACKAGES
# ============================

import os
import math
import time
import numpy as np
import pandas as pd

# ============================
# Config
# ============================

config = {
    "featuresPath": os.path.join("features", "{}", "{}"),
    "SVMLightFeaturesPath": os.path.join("svmLight", "features","{}","{}","{}", "{}"),
    "SVMLightLearningParams":"-z c -j {} -t 2 -g {}",
    "SVMLightApplicationPath": os.path.join("svmLight", "application", "{}"),
    "SVMLightFeaturesFileTarget": os.path.join("svmLight", "features","{}","{}","{}", "{}","{}")
}

dataset="trainTest"

# ============================
# Functions
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

def rewrite_label(_item,_class,Label='label'):
    # Label='actualLabel'
    _temp=_item[[Label]].copy()  
    del _item[Label]  
    _temp[_temp[Label]!=_class]="-1"
    _temp[_temp[Label]==_class]="+1"
    return (pd.concat([_temp,_item],axis=1))
        
def processWrite(actual_test,actual_test_path):
    _headers=actual_test.columns[actual_test.columns!='label'].values
    for i, row in actual_test.iterrows():
        for _header in _headers:
            actual_test.at[i,_header] = round(actual_test.at[i,_header],3)
    actual_test.to_csv(actual_test_path,index=False)

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
    
def _data2trainTest(_dataset,_classes,_num_of_folds,mode='normal'):
    
    if mode=='shuffle':
        np.random.seed(2)
        _dataset=_dataset.reindex(np.random.permutation(_dataset.index))
        _co=int(len(_dataset)/5)
        pieces=[_dataset.iloc[_co*i:_co*(i+1)] for i in range(_num_of_folds)]

        _train_test=[]
        for ii in range(_num_of_folds):
            _test = pieces[ii]
            _train=pd.concat([pieces[xx] for xx in range(_num_of_folds) if xx!=ii])
            _train_test.append([_train,_test])
            
    if mode=='normal' or mode=='downSample':

        # Putting each class in a differnet data frame
        _data_by_class=[_dataset[_dataset['label']==_class] for _class in _classes ]

        _folds_by_class=[]
        # Creating folds from each class
        for _item in _data_by_class:
            
            if mode=='normal':
                co=len(_item)//_num_of_folds
            if mode=='downSample':
                np.random.seed(2)
                _item=_item.reindex(np.random.permutation(_item.index))
                co=60//_num_of_folds
                
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
    
    return _train_test


def _trainTest2File(_train_test,_classes,_num_of_folds,feature):
    
    for _fold in range(_num_of_folds):
        
        print("Processing fold [ "+str(_fold)+" ]")
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

def _svmLightclassify(classes,num_of_folds,_params,feature):
    
    num_of_classes=len(classes)

    for _class_index,_class in enumerate(classes):
        for ii in range(num_of_folds):

            _fold="fold"+str(ii)
            gamma,cost=_params[_class_index]

            learningParams=config["SVMLightLearningParams"].format(cost,gamma)
            learner=config["SVMLightApplicationPath"].format("svm_learn")
            classifier=config["SVMLightApplicationPath"].format("svm_classify")


            _train=config["SVMLightFeaturesFileTarget"].format(dataset,feature,_fold,_class,"train.dat")
            _test=config["SVMLightFeaturesFileTarget"].format(dataset,feature,_fold,_class,"test.dat")
            _model=config["SVMLightFeaturesFileTarget"].format(dataset,feature,_fold,_class,"model")
            _prediction=config["SVMLightFeaturesFileTarget"].format(dataset,feature,_fold,_class,"prediction.csv")

            learnCommand=learner+" "+learningParams+" "+_train+" "+_model 
            classifyCommand=classifier+" "+_test+" "+_model+" "+_prediction

            print(">>>> [ "+str(gamma)+" , "+str(cost)+" ] <<<<")
            print("Learning from [ "+_fold+" > "+_class+" ] on [ "+feature+" ]")
            os.system(learnCommand)
            time.sleep(1)
            print("Classifying for [ "+_fold+" > "+_class+" ] on [ "+feature+" ]")
            os.system(classifyCommand)


def calculate_metrics(tp,tn,fp,fn):
    accuracy=(tp+tn)/(tp+tn+fp+fn)
    sensitivity=tp/(tp+fn)
    specificity=tn/(tn+fp)
    
    if (tp== 0 or tn==0) and (fn==0 or fp==0):
        mcc=0
    else:
        mcc= ((tp*tn)-(fn*fp))/math.sqrt((tp+fn)*(tn+fp)*(tp+fp)*(tn+fn))

    metric=[accuracy,sensitivity,specificity, mcc]
    metrics=[round(_metric*100,2) for _metric in metric]
    
    return metrics

def _evaluate(classes,num_of_folds,feature,mode,_thresh=0):

    all_macros=[]
    all_micros=[]
    for _fold in range(num_of_folds):
    # for _fold in [0]:

        print("Processing Fold [{}]".format(str(_fold)))
        # print("==================================")

        _fold_macro_metrics=[]
        _fold_micro_metrics=[]
        
        #=======================================
        #=======================================
        if mode=='fold':
            
            all_preds=pd.DataFrame(data=None)

            # print("Processing Fold [{}]".format(str(_fold)))
            # print("==================================")

            _fold_macro_metrics=[]
            _fold_micro_metrics=[]

            for _class in classes:
            # for _class in ['amino']:
                
                source=config["SVMLightFeaturesFileTarget"].format(dataset,feature,("fold"+str(_fold)),_class,"prediction.csv")
                class_pred_csv=pd.read_csv(source, sep=' ',header=None,names=[_class])
                all_preds = pd.concat([all_preds,class_pred_csv],axis=1)

            # Predict the one vs all
            # All Headers
            _headers=all_preds.columns.values
            # Creating new DataFrame
            # For final value out of all 8 prediction (One vs All)
            _res=pd.DataFrame(columns=['predicted','predictedValue'])
            for kk in range(len(all_preds)):
                _max=max(all_preds.values[kk])
                if _max<0:
                    #_max=min(all_preds.values[kk])
                    _max=max(all_preds.values[kk])
                for i in range(len(all_preds.values[kk])):
                    if all_preds.values[kk][i]==_max:
                        _res.loc[kk]=[_headers[i],_max]
                        break
            
            
            foldSource=config["SVMLightFeaturesPath"].format(dataset,feature,("fold"+str(_fold)),"test.csv")
            fold_test=pd.read_csv(foldSource)

            

            _res=pd.concat([_res,fold_test['label']],axis=1)
            _res=_res.rename(columns={'label':'actual'})
            _res.drop(labels=['predictedValue'],axis=1,inplace=True)

        #=======================================
        #=======================================

        for _class in classes:
        # for _class in ['sugar']:

        #=======================================
        #=======================================
            if mode == 'class':
        
                source=config["SVMLightFeaturesFileTarget"].format(dataset,feature,("fold"+str(_fold)),_class,"prediction.csv")
                class_pred_csv=pd.read_csv(source, sep=' ',header=None,names=[_class])
                _pred_values = class_pred_csv.values
                for ii in range(len(_pred_values)):
                    if _pred_values[ii]>_thresh:
                        class_pred_csv.loc[ii][_class]=1
                    elif _pred_values[ii]==_thresh:
                        class_pred_csv.loc[ii][_class]=0
                    elif _pred_values[ii]<_thresh:
                        class_pred_csv.loc[ii][_class]=-1

                class_pred_csv[_class]=pd.to_numeric(class_pred_csv[_class], errors='coerce',downcast='integer')

                source=config["SVMLightFeaturesPath"].format(dataset,feature,("fold"+str(_fold)),"test.csv")
                fold_test_csv = pd.read_csv(source)

                labels=fold_test_csv['label']

                fold_test_csv=rewrite_label(fold_test_csv.copy(),_class)
                fold_test_csv['label']=pd.to_numeric(fold_test_csv['label'], errors='coerce',downcast='integer')
                fold_test_csv=fold_test_csv.rename(columns={'label':'actual'})

                _test=fold_test_csv['actual']


                # _all_results=pd.DataFrame(data=None,columns=['predicted','actual','label'])
                _all_results=pd.concat([class_pred_csv,_test],axis=1)
                _all_results=_all_results.rename(columns={_class:'predicted'})


                _class_res=_all_results[_all_results['actual']==1]
            
        #=======================================
        #=======================================
            if mode=='fold':
                _all_results=rewrite_label(_res.copy(),_class,'actual')
                _all_results=rewrite_label(_all_results,_class,'predicted')
                _all_results['actual']=pd.to_numeric(_all_results['actual'], errors='coerce',downcast='integer')
                _all_results['predicted']=pd.to_numeric(_all_results['predicted'], errors='coerce',downcast='integer')
                
                _class_res=_all_results[_all_results['actual']==1]

        #=======================================
        #=======================================
            
            try:
                tp=_class_res['predicted'].value_counts()[1]
            except Exception:
                tp=0

            try:
                fn=_class_res['predicted'].value_counts()[-1]
            except Exception:
                fn=0

            _other_res=_all_results[_all_results['actual']==-1]
            try:
                tn=_other_res['predicted'].value_counts()[-1]
            except Exception:
                tn=0

            try:
                fp=_other_res['predicted'].value_counts()[1]
            except Exception:
                fp=0


            _metrics=calculate_metrics(tp,tn,fp,fn)
            # print(_metrics)
            # print([tp,fn,fp,tn])

            _fold_macro_metrics.append(_metrics)
            _fold_micro_metrics.append([tp,fn,fp,tn])

        # fold_metrics
        # metric=[accuracy,sensitivity,specificity, mcc]
        _fold_acc=np.sum([item[0] for item in _fold_macro_metrics]) / len(_fold_macro_metrics)
        _fold_sens=np.sum([item[1] for item in _fold_macro_metrics]) / len(_fold_macro_metrics)
        _fold_spec=np.sum([item[2] for item in _fold_macro_metrics]) / len(_fold_macro_metrics)
        _fold_mcc=np.sum([item[3] for item in _fold_macro_metrics]) / len(_fold_macro_metrics)

        _fold_macros=[_fold_acc,_fold_sens,_fold_spec,_fold_mcc]
        all_macros.append(_fold_macros)

        _fold_tp=np.sum([item[0] for item in _fold_micro_metrics]) / len(_fold_micro_metrics)
        _fold_fn=np.sum([item[1] for item in _fold_micro_metrics]) / len(_fold_micro_metrics)
        _fold_fp=np.sum([item[2] for item in _fold_micro_metrics]) / len(_fold_micro_metrics)
        _fold_tn=np.sum([item[3] for item in _fold_micro_metrics]) / len(_fold_micro_metrics)
        _fold_micros=calculate_metrics(_fold_tp,_fold_tn,_fold_fp,_fold_fn)
        all_micros.append(_fold_micros)
        # print("==================================")
        # print("Macro for Fold [{}]".format(str(_fold)))
        # print(_fold_macros)
        # print("----------------------------------")
        # print("Micro for Fold [{}]".format(str(_fold)))
        # print(_fold_micros)
        # print("==================================")


    # fold_metrics
    # metric=[accuracy,sensitivity,specificity, mcc]
    all_macros_acc=np.sum([item[0] for item in all_macros]) / len(all_macros)
    all_macros_sens=np.sum([item[1] for item in all_macros]) / len(all_macros)
    all_macros_spec=np.sum([item[2] for item in all_macros]) / len(all_macros)
    all_macros_mcc=np.sum([item[3] for item in all_macros]) / len(all_macros)

    _problem_macros=[all_macros_acc,all_macros_sens,all_macros_spec,all_macros_mcc]

    all_micros_acc=np.sum([item[0] for item in all_micros]) / len(all_micros)
    all_micros_sens=np.sum([item[1] for item in all_micros]) / len(all_micros)
    all_micros_spec=np.sum([item[2] for item in all_micros]) / len(all_micros)
    all_micros_mcc=np.sum([item[3] for item in all_micros]) / len(all_micros)

    _problem_micros=[all_micros_acc,all_micros_sens,all_micros_spec,all_micros_mcc]



    print("==================================")
    print("==================================")
    print("Total Macro for problem")
    print(_problem_macros)
    print("----------------------------------")
    print("Total Micro for problem")
    print(_problem_micros)
    print("==================================")
    print("==================================")