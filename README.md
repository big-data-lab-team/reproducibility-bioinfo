In this project and through the following pipeline, we tried to reproduce the results of the [TrSSP](#prediction-of-membrane-transport-proteins-and-their-substrate-specificities-using-primary-sequence-information-nitish-k-mishrajunil-changpatrick-x-zhao2014) paper using python(3.7.0), Scikit-Learn, Numpy, Pandas and Matplotlib.

## Before Running the program
Install Python 3 with all mentioned dependencies above.

## Dataset
According to the paper, the TrSSP authors have put together two datasets: 
> * " We first constructed a substrate-specific transport protein dataset that consisted of seven classes of transporters exclusive to a particular substrate, i.e., amino acid transporters/oligopeptides, anion transporters, cation transporters, electron transporters, protein/mRNA transporters, sugar transporters, and other transporters ... "

> * " We further evaluated the performance of these models on 180 independent proteins ... "

So, for the purpose of our study, we programmed `download.py` to download all the sequences form `NCBI` database by submitting a HTTP request (The protein IDs and the sequences are available at [TrSSp](http://bioinfo.noble.org/TrSSP/?dowhat=Datasets) website) We put all those IDs together and categorized them through different classes in a `.json` file for both [TrainTest](/dataset/trainTest.json) dataset and [Independent](/dataset/independent) dataset.

<br>Further on, we found out that some of those sequences has been updated through time, So, we checked all the downloaded ones against the originals and updated our list (by adding the right version to the ID in the JSON file) and our dataset accordingly.
***
#### `Downloading the train/test dataset`

```python
python3 download.py trainTest
```

This downloads the `train/test` dataset using the [TrainTest.json](/dataset/trainTest.json) file. The outputs are eight `.fasta` files in [TrainTest](/dataset/trainTest) folder as a subfolder to [Dataset](/dataset).


## Reference
##### [Prediction of Membrane Transport Proteins and Their Substrate Specificities Using Primary Sequence Information](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0100278) Nitish K. Mishra,Junil Chang,Patrick X. Zhao (2014)