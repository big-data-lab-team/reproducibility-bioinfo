In this project and through the following pipeline, we tried to reproduce the results for the [TrSSP](#prediction-of-membrane-transport-proteins-and-their-substrate-specificities-using-primary-sequence-information-nitish-k-mishrajunil-changpatrick-x-zhao2014) paper using python(3.7.0), Scikit-Learn, Numpy, Pandas, Matplotlib.

## Before Running the program
Install Python 3 with all mentioned dependencies above

## Dataset
According to the paper, they have put together two different datasets: 
> * We first constructed a substrate-specific transport protein dataset that consisted of seven classes of transporters exclusive to a particular substrate, i.e., amino acid transporters/oligopeptides, anion transporters, cation transporters, electron transporters, protein/mRNA transporters, sugar transporters, and other transporters ... 

> * We further evaluated the performance of these models on 180 independent proteins ...

So, for the purpose of our study, we programmed `download.py` to download all the sequenecs form `ncbi` database by submitting a HTTP request. The protein IDs and the sequences are availbale at their [TrSSp](http://bioinfo.noble.org/TrSSP/?dowhat=Datasets) website. We put all those IDs together and and categorized them through different classes in a `.json` file for both [TrainTest](/dataset/trainTest.json) dataset and [Independent](/dataset/independent) dataset.
<br>Further on, we realized that some of those sequences has been updated through time, So, we checked all the downloaded sequences against the ones available on their website and modified our dataset (by adding the right version to the ID in the JSON file) to match the original dataset.

#### * Downlading the train/test dataset

```python
python3 download.py trainTest
```

## Features
According to the paper, they have develeoped 2 different models: 
> * [The first model] were developed to predict the substrate specificity of seven transporter classes: amino acid, anion, cation, electron, protein/mRNA, sugar, and other transporters.

> * An additional model to differentiate transporters from non-transporters was also developed ...

So, following the process being discussed in the paper, the `extractFeature.py` program generates two different files for each feature in `.csv` format.

#### * Extracting features from the dataset.

```python
python3 extractFeature.py aac trainTest
```

This syntax calculates `Amino Acid Composition (aac)` feature from the `train/test` dataset in `.csv` format. Two following files will be placed in [TrainTest](/features/trainTest) folder in [Features](/features) folder by program after running the syntax.

* `aac1.csv` which contains the Amino Acid Composition percentage for all sequences in the dataset (except non-transporters). Each sequence is labeled as `amino, anion, cation, electron, protein, sugar, other` which corresponds to  membrane transport proteins that transports this specific substrate.

* `aac2.csv` which contains the Amino Acid Composition percentage for all sequences in the dataset. All the sequences from `amino, anion, cation, electron, protein, sugar, other` category is labeled as `transporter` and all sequences from `non-transporter` file is labled as `nonTransporter`


## Reference
##### [Prediction of Membrane Transport Proteins and Their Substrate Specificities Using Primary Sequence Information](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0100278) Nitish K. Mishra,Junil Chang,Patrick X. Zhao (2014)
