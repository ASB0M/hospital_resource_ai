# IMPORTS

import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from sklearn import metrics
from sklearn.metrics import ConfusionMatrixDisplay
import matplotlib.pyplot as plt
import joblib

# DATA

data = pd.read_csv('../data/raw/patients.csv')
data.head()

# adding numarical labels to Complaint and Urgency caulmn

le_complaint = LabelEncoder()
le_urgency = LabelEncoder()

data['Complaint_Code'] = le_complaint.fit_transform(data['Complaint'])
data['Urgency_Code'] = le_urgency.fit_transform(data['Urgency'])
data.head()

print("\nAutomatic mapping:")
print(dict(zip(le_complaint.classes_, range(len(le_complaint.classes_)))))
print(dict(zip(le_urgency.classes_, range(len(le_urgency.classes_)))))

# splitting data into training and testing sets

feature_order = ['Age', 'Gender', 'Complaint_Code', 'HR', 'BP', 'Temp', 'SpO2']
X = data.loc[:, feature_order]
y = data.loc[:, ["Urgency_Code"]]

scaler = StandardScaler()
X = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2)

print(f"X_train shape = {X_train.shape}")
print(f"X_test shape = {X_test.shape}")
print(f"y_train shape = {y_train.shape}")
print(f"y_test shape = {y_test.shape}")

# GaussianNB modelling

gnb_model = GaussianNB()

gnb_model.fit(X_train, y_train.values.reshape(-1))

y_pred = gnb_model.predict(X_test)


accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.4f}")

precision = precision_score(y_test, y_pred, average='weighted')
recall = recall_score(y_test, y_pred, average='weighted')
f1 = f1_score(y_test, y_pred, average='weighted')

print(f"Precision: {precision:.4f}")
print(f"Recall: {recall:.4f}")
print(f"F1 Score: {f1:.4f}")

print("\nClassification Report:\n")
print(classification_report(y_test, y_pred))

# CONFUSION METRICS

# CONFUSION METRICS
confusionmetrics = metrics.confusion_matrix(y_test, y_pred)
print(confusionmetrics)

# cm_display = ConfusionMatrixDisplay(confusion_matrix = confusionmetrics)
# cm_display.plot()
# plt.show()

# EXPORTING MODEL TO SRC

joblib.dump(gnb_model, '../src/models/triage.pkl')
joblib.dump(le_complaint, '../src/models/encoder_complaint.pkl')
joblib.dump(le_urgency, '../src/models/encoder_urgency.pkl')
joblib.dump(scaler, '../src/models/scaler.pkl')



