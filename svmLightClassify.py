import os
import time
import traceback
import argparse
from helpers import log

config = {
    "SVMLightLearningParams":"-z c -j {} -t 2 -g {}",
    "SVMLightApplicationPath": os.path.join("svmLight", "application", "{}"),
    "SVMLightFeaturesFileTarget": os.path.join("svmLight", "features","{}","{}","{}", "{}","{}")
}

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
        
        _params={
            "aac7":[
            [0.03,4.6],[0.04,5.0],[0.02,4.6], [0.02,4.0],[0.03,4.0],[0.04,5.0],[0.03,5.0]
            ],
            "aac8":[
            [0.03,4.6],[0.04,5.0],[0.02,4.6], [0.02,4.0],[0.02,4.8],[0.03,4.0],[0.04,5.0],[0.03,5.0]
            ]
        }
        # _params={"aac8":[
        #     [0.02,1.8],[0.02,1.8],[0.02,1.8],[0.02,1.8],[0.02,1.8],[0.02,1.8],[0.02,1.8],[0.02,1.8]
        #     ]
        # }
        
        # feature="aac8"
        num_of_folds=5
        num_of_classes=8
        
        for _class_index,_class in enumerate(classes):
            for ii in range(num_of_folds):

                # _class="amino"
                # _class_index=0
                # ii=0

                _fold="fold"+str(ii)
                gamma,cost=_params[feature][_class_index]

                learningParams=config["SVMLightLearningParams"].format(cost,gamma)
                learner=config["SVMLightApplicationPath"].format("svm_learn")
                classifier=config["SVMLightApplicationPath"].format("svm_classify")
                
                
                _train=config["SVMLightFeaturesFileTarget"].format(dataset,feature,_fold,_class,"train.dat")
                _test=config["SVMLightFeaturesFileTarget"].format(dataset,feature,_fold,_class,"test.dat")
                _model=config["SVMLightFeaturesFileTarget"].format(dataset,feature,_fold,_class,"model")
                _prediction=config["SVMLightFeaturesFileTarget"].format(dataset,feature,_fold,_class,"prediction.csv")

                learnCommand=learner+" "+learningParams+" "+_train+" "+_model 
                classifyCommand=classifier+" "+_test+" "+_model+" "+_prediction
                
                log(">>>> [ "+str(gamma)+" , "+str(cost)+" ] <<<<")
                log("Learning from [ "+_fold+" > "+_class+" ] on [ "+feature+" ]")
                os.system(learnCommand)
                time.sleep(1)
                log("Classifying for [ "+_fold+" > "+_class+" ] on [ "+feature+" ]")
                os.system(classifyCommand)
        
        log("[ "+feature+" ] learning / classification process done successfully!")

    except Exception:
        log("[ "+feature+" ] learning / classification process failed!")
        log(traceback.format_exc())



if __name__ == "__main__":
    main()