In this project and through the following pipeline, we tried to reproduce the results for the [TrSSP](#prediction-of-membrane-transport-proteins-and-their-substrate-specificities-using-primary-sequence-information-nitish-k-mishrajunil-changpatrick-x-zhao2014) paper using python(3.7.0), Scikit-Learn, Numpy, Pandas, Matplotlib.

### Before Running the program
***
- Install Python 3 with all mentioned dependencies above

### Dataset
***
- Downlading the train/test dataset
```python
python3 download.py trainTest
```
### Features
***
According to the paper, they have develeoped 2 different models: 
> [The first model] were developed to predict the substrate specificity of seven transporter classes: amino acid, anion, cation, electron, protein/mRNA, sugar, and other transporters. An additional model to differentiate transporters from non-transporters was also developed 

So, following the process being discussed in the paper, the `extractFeature.py` program generates two different files for each feature in `.csv` format.

* Extracting features from the dataset.
    ```python
    python3 extractFeature.py aac trainTest
    ```

    This syntax calculates `Amino Acid Composition (aac)` feature from the `train/test` dataset in `.csv` format. Two following files will be placed in [trainTest](https://github.com/HamidHeyde/reproducibility-bioinfo/tree/master/features/trainTest) folder in [features](https://github.com/HamidHeyde/reproducibility-bioinfo/tree/master/features) folder by program after running the syntax.

    * `aac1.csv` which contains the Amino Acid Composition percentage for all sequences in the dataset (except non-transporters). Each sequence is labeled as `amino, anion, cation, electron, protein, sugar, other` which corresponds to  membrane transport proteins that transports this specific substrate.

    * `aac2.csv` which contains the Amino Acid Composition percentage for all sequences in the dataset. All the sequences from `amino, anion, cation, electron, protein, sugar, other` category is labeled as `transporter` and all sequences from `non-transporter` file is labled as `nonTransporter`


### Reference
***
##### [Prediction of Membrane Transport Proteins and Their Substrate Specificities Using Primary Sequence Information](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0100278) Nitish K. Mishra,Junil Chang,Patrick X. Zhao (2014)
