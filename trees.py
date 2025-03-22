from sklearn.tree import DecisionTreeClassifier as tree
from sklearn.ensemble import RandomForestClassifier as forest
from sklearn.neighbors import KNeighborsClassifier as knn, NearestCentroid as nearestc
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
import pandas as pd
import matplotlib.pyplot as plt
import os
from tqdm import tqdm
import warnings
import numpy as np

warnings.filterwarnings("ignore")

seed = 12345678

test_normal_data = [10000, 2.0, 75.0, 550.0, 70.0, 380.0, 10.0]
test_attack_data = [15000, 3.0, 80.0, 560.0, 75.0, 385.0, 15.0]

np.random.seed(seed)

# load the dataset
data = pd.read_csv("data.csv")

# drop rows with missing values in 'y'
data = data.dropna()

# split the data into features and labels
X = data.drop(columns=["is_normal"])
y = data["is_normal"]

# create the model

xte, xtr, yte, ytr = train_test_split(X, y, test_size=0.25, random_state=seed, shuffle=True)

DC = tree(max_depth=6)
DC.fit(xtr, ytr)

# check the accuracy
pred_normal = DC.predict([test_normal_data])
pred_attack = DC.predict([test_attack_data])
print("Predictions for normal data: ", pred_normal)
print("Predictions for attack data: ", pred_attack)