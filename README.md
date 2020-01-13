# ims-preprocess
scripts to convert imZML dataset into columnar format

## NOTE: Maintained scripts have been moved to [`vitessce-data`](https://github.com/hubmapconsortium/vitessce-data).

## Usage
Conda is used to manage the environment
```bash
git clone https://github.com/manzt/ims-preprocess.git && cd ims-preprocess
conda env create -f environment.yml # install dependencies
conda activate ims-preprocess   # activate virtual env
python preprocess.py
```
