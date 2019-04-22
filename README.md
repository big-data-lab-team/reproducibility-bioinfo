> In this project and through the following pipeline, we tried to reproduce the results for the [TrSSP](#1-prediction-of-membrane-transport-proteins-and-their-substrate-specificities-using-primary-sequence-information) paper using python(3.7.0), Scikit-Learn, Numpy, Pandas, Matplotlib.

### Running the Pipeline
***
* Install Python 3 with all mentioned dependencies above
* Downlading the train/test dataset
```python
python3 download.py trainTest
```
* Extracting features from the dataset
```python
python3 extractFeature.py acc trainTest
```

### Dataset
***

### Reference
***
[TrSSp]:https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0100278
##### [Prediction of Membrane Transport Proteins and Their Substrate Specificities Using Primary Sequence Information](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0100278) Nitish K. Mishra,Junil Chang,Patrick X. Zhao (2014)
