# CS270 Final Project
Final Project for CS270 at Stanford University.

# Getting the data
Follow these steps to retrieve the appropriate data:
1. Go to the following [link](https://www.yelp.com/dataset/download) and click "Download JSON".
2. Unzip the file and move `yelp_academic_dataset_business.json` and `yelp_academic_dataset_review.json` into the `yelp_dataset` folder.
3. Create an environment with Python 2.7. e.g. run `conda create -n cs270-python27 python=2.7`.
4. Activate the environment. e.g. run `conda activate cs270-python27`.
5. Install the following packages in your new env: `simplejson`
6. Run `python yelp_dataset/json_to_csv.py yelp_academic_dataset_business.json` and `python yelp_dataset/json_to_csv.py yelp_academic_dataset_review.json`.
7. Congratulations! You now have the two necessary csv files to run the other parts of the project.

# Running EDA Python scripts
1. Create a new python environment with the latest version of Python. e.g. run `conda create --name cs270-python3`.
2. Activate the environment. e.g. run `conda activate cs270-python3`.
3. Install the following packages in your new env: `pandas`, `pyarrow`
4. Run the desired scripts to get the results.
