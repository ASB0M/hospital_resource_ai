# IMPORTS
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib

# DATA

data = pd.read_csv('../data/raw/patients.csv')
data.head()

# encoding numarical labels to Complaint

label = LabelEncoder()

data['Complaint_Code'] = label.fit_transform(data['Complaint'])

data.head()

# spliting data into train test split

features = ['Age', 'Gender', 'Complaint_Code', 'HR', 'BP', 'Temp', 'SpO2']

X = data.loc[:, features]
y = data.loc[:, ["LOS"]]

scaler = StandardScaler()
X = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2)

# MODELtraining

lr_model = LinearRegression()

lr_model.fit(X_train, y_train)

print(f"Intercept: {lr_model.intercept_}")
print(f"Coefficients: {lr_model.coef_}")

lr_pred = lr_model.predict(X_test)

# Evaluating the model

mse = mean_squared_error(y_test, lr_pred)
r2 = r2_score(y_test, lr_pred)
print(f"Mean Squared Error: {mse}")
print(f"R-squared: {r2}")

rfr_model = RandomForestRegressor()

rfr_model.fit(X_train, y_train.values.reshape(-1))

rfr_pred = rfr_model.predict(X_test)

# Evaluating the model

mse = mean_squared_error(y_test, rfr_pred)
r2 = r2_score(y_test, rfr_pred)
print(f"Mean Squared Error: {mse}")
print(f"R-squared: {r2}")

# EXPORTING MODEL TO SRC

joblib.dump(rfr_model, '../src/models/los.pkl')

