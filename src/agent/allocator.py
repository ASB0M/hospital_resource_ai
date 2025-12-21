import joblib
import pandas as pd
import numpy as np
import os

class HospitalAgent:
    def __init__(self, model_dir='src/models/'):
        self.model_dir = model_dir
        
        self.feature_order = ['Age', 'Gender', 'Complaint_Code', 'HR', 'BP', 'Temp', 'SpO2']
        
        self.load_models()

    def load_models(self):
        try:
            self.triage_model = joblib.load(os.path.join(self.model_dir, 'triage.pkl'))
            self.los_model = joblib.load(os.path.join(self.model_dir, 'los.pkl'))
            self.encoder_complaint = joblib.load(os.path.join(self.model_dir, 'encoder_complaint.pkl'))
            self.encoder_urgency = joblib.load(os.path.join(self.model_dir, 'encoder_urgency.pkl'))
            self.scaler = joblib.load(os.path.join(self.model_dir, 'scaler.pkl')) 
        except FileNotFoundError as e:
            print(f"CRITICAL ERROR: {e}")
            print("Run 'triage_analysis.ipynb' again to generate the missing .pkl files.")

    def predictor(self, features):
        """
        Input: Dictionary (e.g., {'Age': 20, 'Complaint': 'Flu'...})
        Output: urgency_level (int), los (float)
        """
        # Converting Dictionary to DataFrame
        df = pd.DataFrame([features])

        try:
            # Check if valid complaint
            if df['Complaint'].iloc[0] in self.encoder_complaint.classes_:
                df['Complaint_Code'] = self.encoder_complaint.transform(df['Complaint'])
            else:
                df['Complaint_Code'] = 0 # Default to 0 if unknown
        except:
             df['Complaint_Code'] = 0

        X_raw = df[self.feature_order]

        X_scaled = self.scaler.transform(X_raw)

        urgency_pred = self.triage_model.predict(X_scaled)[0]
        
        los_pred = self.los_model.predict(X_scaled)[0]

        return urgency_pred, los_pred

    def allocate_resources(self, patient, hospital):
        urgency = patient.urgency_label
        
        # Decoding the LabelEncoder Logic
        # Based on your files: 0=Critical, 2=Medium, 1=Low
        
        if urgency == 0: # Critical
            if hospital.admit_patient(patient, "ICU"):
                return "Assigned ICU (Critical)"
            elif hospital.admit_patient(patient, "GENERAL"):
                return "Assigned General (ICU Overflow)"
            else:
                return "Refused (No Beds)"
        
        elif urgency == 2: # Medium
             if hospital.admit_patient(patient, "GENERAL"):
                return "Assigned General (Medium)"
             else:
                return "Refused (No Beds)"

        elif urgency == 1: # Low
            # Only admit low priority if we have > 10% buffer
            buffer = hospital.capacity["GENERAL"] * 0.1
            if (hospital.capacity["GENERAL"] - len(hospital.occupied["GENERAL"])) > buffer:
                hospital.admit_patient(patient, "GENERAL")
                return "Assigned General (Low Priority)"
            else:
                return "Refused (Save Beds for Critical)"
        
        return "Error in Allocation Logic"