# cSpell:disable
# ============================
# PACKAGES
# ============================

import os
import math
import numpy as np
import pandas as pd
from sklearn.svm import SVC

# ============================
# Config
# ============================
config = {
    "featuresPath": os.path.join("dataset", "{}"),
    "scikitFeaturesPath": os.path.join("scikit","{}","{}","{}"),
    "scikitFeaturesFileTarget": os.path.join("scikit","{}","{}","{}", "{}")
}

# ============================
# Functions
# ============================
def clearFile(fileAddress):
     # Tries to create directories (If does not exist)
    try:
        open(fileAddress, 'w').close()
    except:
        newPath = (fileAddress).split((os.sep))
        path = ((os.sep).join(newPath[:(len(newPath)-1)]))
        os.makedirs(path, mode=0o777, exist_ok=False)
    finally:
        open(fileAddress, 'w').close()

def csv2file(dataFrame,fileAddress):
    handler=open(fileAddress,'w')
    handler.write(dataFrame.to_csv(index=False))
    handler.close()
        
def rewrite_label(_item,_class,Label='label'):
    # Label='actualLabel'
    _temp=_item[[Label]].copy()  
    del _item[Label]  
    _temp[_temp[Label]!=_class]="-1"
    _temp[_temp[Label]==_class]="+1"

    return (pd.concat([_temp,_item],axis=1))

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
    
    return _train_test.copy()


def _trainTest2File(_train_test,_classes,_num_of_folds,feature):
    
    for _fold in range(_num_of_folds):
        
        print("Processing fold [ "+str(_fold)+" ]")

        #Main Train/Test before transformation
        train,test = _train_test[_fold]

        #Main Train/Test before transformation
        actual_test_path=config['scikitFeaturesPath'].format(feature,"fold"+str(_fold),"test.csv")
        actual_train_path=config['scikitFeaturesPath'].format(feature,"fold"+str(_fold),"train.csv")

        clearFile(actual_test_path)
        clearFile(actual_train_path)

        csv2file(test.copy(),actual_test_path)
        csv2file(train.copy(),actual_train_path)

        for _class in _classes:

            _train=rewrite_label(train.copy(),_class)
            _test=rewrite_label(test.copy(),_class)

            fold_test_path=config['scikitFeaturesFileTarget'].format(feature,"fold"+str(_fold),_class,"test.csv")
            fold_train_path=config['scikitFeaturesFileTarget'].format(feature,"fold"+str(_fold),_class,"train.csv")

            clearFile(fold_test_path)
            clearFile(fold_train_path)

            csv2file(_test.copy(),fold_test_path)
            csv2file(_train.copy(),fold_train_path)

def _scikitClassify(_classes,_num_of_folds,_params,feature):

    for _fold in range(_num_of_folds):

        print("Classifying fold [ "+str(_fold)+" ]")

        for _class_index,_class in enumerate(_classes):

            fold_test_path=config['scikitFeaturesFileTarget'].format(feature,"fold"+str(_fold),_class,"test.csv")
            fold_train_path=config['scikitFeaturesFileTarget'].format(feature,"fold"+str(_fold),_class,"train.csv")
            fold_pred_path=config['scikitFeaturesFileTarget'].format(feature,"fold"+str(_fold),_class,"pred.csv")

            _train_= pd.read_csv(fold_train_path)
            _test_= pd.read_csv(fold_test_path)

            y_train=_train_['label']
            del _train_['label']
            x_train=_train_

            y_test=_test_['label']
            del _test_['label']
            x_test=_test_

            #Different for eache class
            _gamma,_C=_params[_class_index]


            _classifier=SVC(probability=True,kernel='rbf', gamma=_gamma,C=_C)

            _classifier.fit(x_train,y_train)
            y_pred = _classifier.predict(x_test)
            y_pred_prob = _classifier.predict_proba(x_test)


            _final_res=[]
            for i in range(len(y_pred)):

                if int(y_pred[i])== 1:
                    _final_res.append(y_pred_prob[i][1])

                elif int(y_pred[i])== -1:
                    _final_res.append((y_pred_prob[i][-1]*-1))


            pred = pd.DataFrame(_final_res,columns=[_class])


            clearFile(fold_pred_path)
            csv2file(pred.copy(),fold_pred_path)


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
    
    #SVMLightFeaturesPath = scikitFeaturesPath
    #SVMLightFeaturesFileTarget = scikitFeaturesFileTarget
    
    all_macros=[]
    all_micros=[]
    for _fold in range(num_of_folds):
    # for _fold in [0]:

        print("Evaluating Fold [{}]".format(str(_fold)))
        # print("==================================")

        _fold_macro_metrics=[]
        _fold_micro_metrics=[]
        
        #=======================================
        #=======================================
        if mode=='fold':
            
            all_preds=pd.DataFrame(data=None)

            # print("Evaluating Fold [{}]".format(str(_fold)))
            # print("==================================")

            _fold_macro_metrics=[]
            _fold_micro_metrics=[]

            for _class in classes:
            # for _class in ['amino']:
                
                source=config["scikitFeaturesFileTarget"].format(feature,("fold"+str(_fold)),_class,"pred.csv")
                #class_pred_csv=pd.read_csv(source, sep=' ',header=None,names=[_class])
                class_pred_csv=pd.read_csv(source, sep=' ')
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
            
            
            foldSource=config["scikitFeaturesPath"].format(feature,("fold"+str(_fold)),"test.csv")
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
        
                source=config["scikitFeaturesFileTarget"].format(feature,("fold"+str(_fold)),_class,"pred.csv")
                #class_pred_csv=pd.read_csv(source, sep=' ',header=None,names=[_class])
                class_pred_csv=pd.read_csv(source, sep=' ')
                #print(class_pred_csv)
                _pred_values = class_pred_csv.values
                
                
                for ii in range(len(_pred_values)):
                    if _pred_values[ii]>_thresh:
                        class_pred_csv.loc[ii][_class]=1
                    elif _pred_values[ii]==_thresh:
                        class_pred_csv.loc[ii][_class]=0
                    elif _pred_values[ii]<_thresh:
                        class_pred_csv.loc[ii][_class]=-1

                class_pred_csv[_class]=pd.to_numeric(class_pred_csv[_class], errors='coerce',downcast='integer')
                #print(class_pred_csv)

                source=config["scikitFeaturesPath"].format(feature,("fold"+str(_fold)),"test.csv")
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



    print("acc===sens====spec=============mcc")
    print("==================================")
    print("Total Macro for problem")
    print(_problem_macros)
    print("----------------------------------")
    print("Total Micro for problem")
    print(_problem_micros)
    print("==================================")
    print("==================================")