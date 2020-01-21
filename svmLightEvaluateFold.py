import os
import time
import math
import argparse
import traceback
import numpy as np
import pandas as pd
from helpers import log

config = {

    "SVMLightFeaturesPath": os.path.join("svmLight", "features","{}","{}","{}", "{}"),
    "SVMLightFeaturesFileTarget": os.path.join("svmLight", "features","{}","{}","{}", "{}","{}")
}

def rewrite_label(_item,_class,Label):
    # Label='actualLabel'
    _temp=_item[[Label]].copy()  
    del _item[Label]  
    _temp[_temp[Label]!=_class]="-1"
    _temp[_temp[Label]==_class]="+1"
    return (pd.concat([_temp,_item],axis=1))

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

def main():
    try:
        # Checking for right argument from user
        parser = argparse.ArgumentParser(
            description='Learn from train set and classify the test set')
        parser.add_argument('feature', type=str, help='Feature (CSV) to convert (aac7,aac8,etc.)')
        parser.add_argument(
            'dataset', type=str, help='Dataset from which the feature would be Extracted from (trainTest or Independent)')
        parser.parse_args()

        # Logging start of Program
        feature = parser.parse_args().feature
        dataset = parser.parse_args().dataset


        log(time.strftime("%m/%d/%Y, %H:%M:%S", time.localtime()))

        classes=[]
        if "8" in feature:
            classes=["amino","anion","cation","electron","nonTransporter","other","protein","sugar"]
        else:
            classes=["amino","anion","cation","electron","other","protein","sugar"]
        
        num_of_folds=5

        all_macros=[]
        all_micros=[]
        for _fold in range(num_of_folds):
        # for _fold in [0]:

            all_preds=pd.DataFrame(data=None)

            print("Processing Fold [{}]".format(str(_fold)))
            print("==================================")

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
            _res=pd.DataFrame(columns=['predictedLabel','predictedValue'])
            for kk in range(len(all_preds)):
                _max=max(all_preds.values[kk])
                if _max<0:
                    # _max=min(all_preds.values[kk])
                    _max=max(all_preds.values[kk])
                for i in range(len(all_preds.values[kk])):
                    if all_preds.values[kk][i]==_max:
                        _res.loc[kk]=[_headers[i],_max]
                        break
            
            
            foldSource=config["SVMLightFeaturesPath"].format(dataset,feature,("fold"+str(_fold)),"test.csv")
            fold_test=pd.read_csv(foldSource)

            

            _res=pd.concat([_res,fold_test['Label']],axis=1)
            _res=_res.rename(columns={'Label':'actualLabel'})
            _res.drop(labels=['predictedValue'],axis=1,inplace=True)
            

            for _class in classes:

                class_res=rewrite_label(_res.copy(),_class,'actualLabel')
                class_res=rewrite_label(class_res,_class,'predictedLabel')
                class_res['actualLabel']=pd.to_numeric(class_res['actualLabel'], errors='coerce',downcast='integer')
                class_res['predictedLabel']=pd.to_numeric(class_res['predictedLabel'], errors='coerce',downcast='integer')
                # print(class_res)
                # print(_res)
                _class_res=class_res[class_res['actualLabel']==1]
                try:
                    tp=_class_res['predictedLabel'].value_counts()[1]
                except Exception:
                    tp=0

                try:
                    fn=_class_res['predictedLabel'].value_counts()[-1]
                except Exception:
                    fn=0
                
                _other_res=class_res[class_res['actualLabel']==-1]
                try:
                    tn=_other_res['predictedLabel'].value_counts()[-1]
                except Exception:
                    tn=0

                try:
                    fp=_other_res['predictedLabel'].value_counts()[1]
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
            print("==================================")
            print("Macro for Fold [{}]".format(str(_fold)))
            print(_fold_macros)
            print("----------------------------------")
            print("Micro for Fold [{}]".format(str(_fold)))
            print(_fold_micros)
            print("==================================")
        

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


            

    except Exception:
        log("[ "+feature+" ] Evaluation failed!")
        log(traceback.format_exc())
    


if __name__ == "__main__":
    main()