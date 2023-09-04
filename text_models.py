# -*- coding: utf-8 -*-
"""TEXT MODELS.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/17Q0aoo7KyZl9KY14TWAcL0DUoPuuxlDQ
"""

# Commented out IPython magic to ensure Python compatibility.
import numpy as np # linear algebra
import pandas as pd # data processing
import matplotlib.pyplot as plt # data visualisation
import seaborn as sns  # data visualisation
# %matplotlib inline
import os

CBB = pd.read_csv("CollegeBasketballPlayers2009-2021.csv")
NBA = pd.read_csv("ALL YEARS 2009 - 2022.csv")

#turnover / (turover + assist)
CBB = CBB.dropna()
# Replace 0s in ast/tov column with a small positive number
CBB.loc[CBB['ast/tov'] == 0, 'ast/tov'] = 0.0001

# Calculate the new column and add it to the DataFrame
CBB['PR'] = 1 / CBB['ast/tov']

# Save the modified DataFrame to a new CSV file
CBB.to_csv('CollegeBasketballPlayers2009-2021_with_ratio.csv', index=False)

def subset_model_all_features(college_file, nba_file, features, k=9, test_year=2020, test_size=0.2, random_state=42, new_data=None):
    # Load the data from the CSV files
    college_data = pd.read_csv(college_file)
    nba_data = pd.read_csv(nba_file)

    results = {}

    for feat in features:
        # Find the latest year in college_data that is before the test_year
        year = college_data['year'].max()
        while year >= test_year:
            year -= 1

        # Merge college_data with nba_data to get target variable (PR)
        merged_data = pd.merge(college_data[college_data['year'] == year], nba_data[['PLAYER', feat]], left_on='player_name', right_on='PLAYER')

        # Drop any rows with missing target variable values
        merged_data = merged_data.dropna(subset=[feat])

        # Split the data into features (X) and target (y)
        # Modify this line to drop only columns not relevant for training
        X = merged_data.drop(['player_name', 'PLAYER', feat, 'team', 'conf', 'Unnamed: 64', 'Unnamed: 65', 'yr', 'ht', 'type', 'year'], axis=1)
        y = merged_data[feat]

        # The rest of your function can remain the same
        # Use feature selection to identify the most important features
        selector = SelectKBest(score_func=f_regression, k=k)

        # Impute missing values using mean strategy
        imputer = SimpleImputer(missing_values=np.nan, strategy='mean')

        # Create a pipeline to handle feature selection and imputation
        pipeline = Pipeline([('imputer', imputer), ('selector', selector)])

        # Fit the pipeline on the data and transform it
        X_selected = pipeline.fit_transform(X, y)

        # Get the indices and names of the most important features
        indices = selector.get_support(indices=True)
        feature_names = X.columns[indices]

        # Split the subset of data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X_selected, y, test_size=test_size, random_state=random_state)

        # Train a machine learning model on the subset of data
        model = RandomForestRegressor(random_state=random_state)
        model.fit(X_train, y_train)

        # Evaluate the model on the testing set
        score = model.score(X_test, y_test)

        # Make predictions on new data using the subset of features, if provided
        if new_data is not None:
            X_new = pd.DataFrame(new_data, columns=feature_names)
            X_new_selected = pipeline.transform(X_new)
            predictions = model.predict(X_new_selected)
            results[feat] = {'score': score, 'selected_features': feature_names, 'predictions': predictions}
        else:
            results[feat] = {'score': score, 'selected_features': feature_names}

    return results

features = ['FG%', 'PR', '3P%', 'PF', 'PTS']
results = subset_model_all_features("CollegeBasketballPlayers2009-2021.csv", "ALL YEARS 2009 - 2022.csv", features, k=9)

for feat, data in results.items():
    print(f"{feat} prediction score: {data['score']}")
    print(f"Selected features for {feat} prediction: {', '.join(data['selected_features'])}")

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.impute import SimpleImputer

def neural_network_model(csv_file, nba_file, features, test_year=2020, test_size=0.2, random_state=42):
    # Load the data from the CSV files
    college_data = pd.read_csv(csv_file, low_memory=False)
    nba_data = pd.read_csv(nba_file)

    # Initialize an empty dictionary to store R-squared scores
    scores = {}

    for feat in features:
        # Find the latest year in college_data that is before the test_year
        year = college_data['year'].max()
        while year >= test_year:
            year -= 1

        # Merge college_data with nba_data to get target variables (PR and PTS)
        merged_data = pd.merge(college_data[college_data['year'] <= year], nba_data[['PLAYER', feat, 'PTS']], left_on='player_name', right_on='PLAYER')

        # Drop any rows with missing target variable values
        merged_data = merged_data.dropna(subset=['PTS', feat])

        # Split the data into features (X) and target (y)
        X = merged_data.drop(['player_name', 'PLAYER', 'team', 'PTS', feat, 'yr', 'conf', 'Unnamed: 64', 'Unnamed: 65', 'year', 'ht', 'type'], axis=1)
        y = merged_data[feat]

        # Impute missing values using mean strategy
        imputer = SimpleImputer(missing_values=np.nan, strategy='mean')
        X = imputer.fit_transform(X)

        # Standardize the features
        scaler = StandardScaler()
        X = scaler.fit_transform(X)

        # Split the data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)

        # Train a neural network model on the training set
        model = MLPRegressor(hidden_layer_sizes=(100,100), max_iter=100, random_state=random_state)
        model.fit(X_train, y_train)

        # Evaluate the model on the testing set
        score = model.score(X_test, y_test)

        # Store the R-squared score for this feature in the scores dictionary
        scores[feat] = score

    return scores

features = ['FG%', 'PR', '3P%', 'PF', 'PTS']
scores = neural_network_model("CollegeBasketballPlayers2009-2021.csv", "ALL YEARS 2009 - 2022.csv", features, test_year=2020)

for feat in features:
    print(f"R^2 score for {feat} prediction: {scores[feat]}")

from sklearn.neural_network import MLPClassifier

def neural_network_model_classification(csv_file, nba_file, features, test_year, test_size=0.2, random_state=42):
    # Load the data from the CSV files
    college_data = pd.read_csv(csv_file, low_memory=False)
    nba_data = pd.read_csv(nba_file)

    # Initialize an empty dictionary to store accuracy scores
    scores = {}

    for feat in features:
        # Find the latest year in college_data that is before the test_year
        year = college_data[college_data['year'] < test_year]['year'].max()

        # Merge college_data with nba_data to get target variables (above/below median)
        merged_data = pd.merge(college_data[college_data['year'] == year], nba_data[['PLAYER', feat]], left_on='player_name', right_on='PLAYER')

        # Drop any rows with missing target variable values
        merged_data = merged_data.dropna(subset=[feat])

        # Calculate the median of the target variable
        target_median = merged_data[feat].median()

        # Classify the samples as above or below median
        merged_data['target'] = merged_data[feat].apply(lambda x: 1 if x >= target_median else 0)

        # Split the data into features (X) and target (y)
        X = merged_data.drop(['player_name', 'PLAYER', 'team', 'target', 'conf', 'Unnamed: 64', 'Unnamed: 65', 'year', 'yr', 'ht', 'type', feat], axis=1)
        y = merged_data['target']

        # Impute missing values using mean strategy
        imputer = SimpleImputer(missing_values=np.nan, strategy='mean')
        X = imputer.fit_transform(X)

        # Standardize the features
        scaler = StandardScaler()
        X = scaler.fit_transform(X)

        # Split the data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)

        # Train a neural network model on the training set
        model = MLPClassifier(hidden_layer_sizes=(100,100), max_iter=100, random_state=random_state)
        model.fit(X_train, y_train)

        # Evaluate the model on the testing set
        score = model.score(X_test, y_test)

        # Store the accuracy score for this feature in the scores dictionary
        scores[feat] = score

    return scores

features = ['FG%', 'PR', '3P%', 'PF', 'PTS']
score = neural_network_model_classification("CollegeBasketballPlayers2009-2021.csv", "ALL YEARS 2009 - 2022.csv", features, test_year=2020)

print(f"Accuracy score for classification using data from 2009-2019 to predict 2019-2020: {score}")