import os
import tarfile
import urllib
from urllib import request # solution - maybe
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from zlib import crc32
from sklearn.model_selection import train_test_split
from sklearn.model_selection import StratifiedShuffleSplit
from pandas.plotting import scatter_matrix
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OrdinalEncoder
from sklearn.preprocessing import OneHotEncoder
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestRegressor
import joblib
from sklearn.model_selection import GridSearchCV
from scipy import stats

print("--------------")


DOWNLOAD_ROOT = "https://raw.githubusercontent.com/ageron/handson-ml2/master/"
HOUSING_PATH = os.path.join('datasets', 'housing')
HOUSING_URL = DOWNLOAD_ROOT + "datasets/housing/housing.tgz"

## Get the Data
# Download the Data
def fetch_housing_data(housing_url=HOUSING_URL, housing_path=HOUSING_PATH):
    os.makedirs(housing_path, exist_ok=True)
    tgz_path = os.path.join(housing_path, 'housing.tgz')
    urllib.request.urlretrieve(housing_url, tgz_path)
    housing_tgz = tarfile.open(tgz_path)
    housing_tgz.extractall(path=housing_path)
    housing_tgz.close()

# Load the data using pandas
def load_housing_data(housing_path=HOUSING_PATH):
    csv_path = os.path.join(housing_path, 'housing.csv')
    return pd.read_csv(csv_path)

fetch_housing_data()
housing = load_housing_data()

#print(housing.head())
#print(housing.info())
#print(housing['ocean_proximity'].value_counts())
#print(housing.describe())

#housing.hist(bins=50,figsize=(20,15))
#plt.show()


# Create a Test Set
def split_train_test(data, test_ratio):
    shuffled_indices = np.random.permutation(len(data))
    test_set_size = int(len(data) * test_ratio)
    test_indices = shuffled_indices[:test_set_size]
    train_indices = shuffled_indices[test_set_size:]
    return data.iloc[train_indices], data.iloc[test_indices]

def test_set_check(identifier, test_ratio):
    return crc32(np.int64(identifier)) & 0xffffffff < test_ratio * 2**32

def spilt_train_test_by_id(data, test_ratio, id_column):
    ids = data[id_column]
    in_test_set = ids.apply(lambda id_: test_set_check(id_, test_ratio))
    return data.loc[~in_test_set], data.loc[in_test_set]

housing_with_id = housing.reset_index()
housing_with_id["id"] = housing["longitude"] * 1000 + housing["latitude"]

train_set, test = train_test_split(housing, test_size=0.2, random_state = 42)

housing['income_cat'] = pd.cut(housing['median_income'],bins=[0,1.5,3.0,4.5,6,np.inf], labels=[1,2,3,4,5])
split = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
for train_index, test_index in split.split(housing, housing['income_cat']):
    strat_train_set = housing.loc[train_index]
    strat_test_set = housing.loc[test_index]

# deletes 'income_cat' from strat_train_set and strat_test_set
#for set_ in (strat_train_set, strat_test_set):
    #set_.drop("income_cat", axis=1, inplace=True)

housing = strat_train_set.copy()
#housing.plot(kind='scatter', x='longitude', y='latitude', alpha=0.4, s=housing['population']/100,label='population',figsize=(10,7),c='median_house_value',cmap=plt.get_cmap('jet'), colorbar=True)
#plt.legend()
#plt.show()

# Looking for Correlations
#corr_matrix = housing.corr()

#corr_matrix['median_house_value'].sort_values(ascending=False)

#attributes = ['median_house_value', 'median_income', 'total_rooms', 'housing_median_age']
#scatter_matrix(housing[attributes], figsize=(12,8))
#plt.show()

#housing.plot(kind='scatter', x='median_income', y='median_house_value', alpha=0.1)
#plt.show()

#housing['rooms_per_household'] = housing['total_rooms']/housing['households']
#housing['bedrooms_per_room'] = housing['total_bedrooms']/housing['total_rooms']
#housing['populalation_per_household'] = housing['population'] / housing['households']
#corr_matrix = housing.corr()
#corr_matrix['median_house_value'].sort_values(ascending=False)

## Prepare the Data for Machine Learning Algorithms
housing = strat_train_set.drop('median_house_value', axis = 1)
housing_labels = strat_train_set['median_house_value'].copy()

# Data Cleaning
imputer = SimpleImputer(strategy='median')
housing_num = housing.drop('ocean_proximity', axis=1)
imputer.fit(housing_num)
X = imputer.transform(housing_num) # result is plain NumPy array containing transformed features
# do the below if you want to put X back into a pandas DataFrame
# housing_tr = pd.DataFrame(X, columns=housing_num.columns, index=housing_num.index)

# Handling Text and Catagorical Attruibutes
housing_cat = housing[['ocean_proximity']]

ordinal_encoder = OrdinalEncoder()
housing_cat_encoded = ordinal_encoder.fit_transform(housing_cat)
#print(housing_cat_encoded[:10])
#print(ordinal_encoder.categories_)
cat_encoder = OneHotEncoder()
housing_cat_1hot = cat_encoder.fit_transform(housing_cat)
#print(housing_cat_1hot)
# Custom Transformers
# transformer class that adds the combined attributes dicussed
rooms_ix, bedrooms_ix, population_ix, households_ix = 3,4,5,6
class CombinedAttributesAdder(BaseEstimator, TransformerMixin):
    def __init__(self, add_bedrooms_per_room = True): # no *args or **kwargs
        self.add_bedrooms_per_room = add_bedrooms_per_room
    def fit(self, X, y=None):
        return self #  nothing else to do
    def transform(self, X):
        rooms_per_household = X[:,rooms_ix] / X[:, households_ix]
        population_per_household = X[:, population_ix] / X[:, households_ix]
        if self.add_bedrooms_per_room:
            bedrooms_per_room = X[:, bedrooms_ix] / X[:, rooms_ix]
            return np.c_[X, rooms_per_household, population_per_household, bedrooms_per_room]
        else:
            return np.c_[X, rooms_per_household, population_per_household]

atter_adder = CombinedAttributesAdder(add_bedrooms_per_room=False)
housing_extra_attribs = atter_adder.transform(housing.values)

num_pipeline = Pipeline([('imputer', SimpleImputer(strategy='median')), ('attribs_adder', CombinedAttributesAdder()), ('std_scaler', StandardScaler())])
#housing_num_tr = num_pipeline.fit_transform(housing_num)

# using ColumnTransformer
num_attribs = list(housing_num)
cat_attribs = ['ocean_proximity']
full_pipeline = ColumnTransformer([('num', num_pipeline, num_attribs), ('cat', OneHotEncoder(), cat_attribs)])
housing_prepared = full_pipeline.fit_transform(housing)

## Select and Train a Model
#lin_reg = LinearRegression()
#lin_reg.fit(housing_prepared, housing_labels)
#some_data = housing.iloc[:5]
#some_labels = housing_labels.iloc[:5]
#some_data_prepared = full_pipeline.transform(some_data)
#print("Predictions: ", lin_reg.predict(some_data_prepared))
#print("Labels: ", list(some_labels))

#housing_predictions = lin_reg.predict(housing_prepared)
#lin_mse = mean_squared_error(housing_labels, housing_predictions)
#lin_rsme = np.sqrt(lin_mse)
#print(lin_rsme)

#tree_reg = DecisionTreeRegressor()
#tree_reg.fit(housing_prepared, housing_labels)
#housing_predictions = tree_reg.predict(housing_prepared)
#tree_mse = mean_squared_error(housing_labels, housing_predictions)
#tree_rsme = np.sqrt(tree_mse)
#print(tree_rsme)

# Better Evaluation Using Cross-Validation
#scores = cross_val_score(tree_reg, housing_prepared, housing_labels, scoring = 'neg_mean_squared_error', cv = 10)
#tree_rsme_scores = np.sqrt(-scores)

#lin_scores = cross_val_score(lin_reg, housing_prepared, housing_labels, scoring = 'neg_mean_squared_error', cv = 10)
#lin_rsme_scores = np.sqrt(-lin_scores)

def display_scores(scores):
    print('Scores:', scores)
    print('Mean:', scores.mean())
    print('Standard deviation:', scores.std())

#display_scores(tree_rsme_scores)
#print()
#display_scores(lin_rsme_scores)

#forest_reg = RandomForestRegressor()
#forest_reg.fit(housing_prepared, housing_labels)
#housing_predictions = forest_reg.predict(housing_prepared)
#forest_mse = mean_squared_error(housing_labels, housing_predictions)
#forest_rsme = np.sqrt(forest_mse)
#scores = cross_val_score(forest_reg, housing_prepared, housing_labels, scoring = 'neg_mean_squared_error', cv = 10)
#forest_rsme_scores = np.sqrt(-scores)
#print(forest_rsme)
#display_scores(forest_rsme_scores)

#joblib.dump(lin_reg, 'linear_model.pkl')
#joblib.dump(tree_reg, 'tree_model.pkl')
#joblib.dump(forest_reg, 'forest_model.pkl')
#print(forest_reg)
## Fine-Tune Your Model
# Grid Search
print(housing.info())
print(housing_prepared.info())
param_grid = [{'n_estimators':[3,10,30], 'max_features':[2,4,6,8]},{'bootstrap':[False], 'n_estimators':[3,10],'max_features':[2,3,4]}]
forest_reg = RandomForestRegressor()
grid_search = GridSearchCV(forest_reg, param_grid, cv=5,scoring = 'neg_mean_squared_error', return_train_score = True)
grid_search.fit(housing_prepared, housing_labels)
#print(grid_search.best_params_)
#print(grid_search.best_estimator_)
cvres = grid_search.cv_results_
#for mean_score, params in zip(cvres['mean_test_score'], cvres['params']):
    #print(np.sqrt(-mean_score),params)
extra_attribs = ['rooms_per_hhold', 'pop_per_hhold', 'bedrooms_per_room']
cat_encoder = full_pipeline.named_transformers_['cat']
cat_one_hot_attribs = list(cat_encoder.categories_[0])
attributes = num_attribs + extra_attribs + cat_one_hot_attribs
#print(sorted(zip(feature_importance, attributes), reverse=True))

final_model = grid_search.best_estimator_
X_test = strat_test_set.drop('median_house_value', axis = 1)
y_test = strat_test_set['median_house_value'].copy()
X_test_prepared = full_pipeline.transform(X_test)
final_predictions = final_model.predict(X_test_prepared)
final_mse = mean_squared_error(y_test, final_predictions)
final_rsme = np.sqrt(final_mse)
print(final_rsme)

confidence = 0.95
squared_errors = (final_predictions - y_test) ** 2
print(np.sqrt(stats.t.interval(confidence, len(squared_errors)-1, loc=squared_errors.mean(), scale = stats.sem(squared_errors))))