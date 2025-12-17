import joblib
import pandas as pd
import numpy as np
import os

class HospitalAgent:
    def __init__(self, model_dir='models/'):
        """
        Initializes the AI Agent.
        :param model_dir: Path to the folder containing .pkl files
        """
        self.model_dir = model_dir
        self.triage = None
        self.los = None
        self.encoder_complaint = None
        self.encoder_urgency = None
        
        # Load models immediately
        self.load_models()

    def load_models(self):
        """
        Loads the trained Naive Bayes and Regression models.
        """
        try:
            print("Agent: Loading AI Models...")
            self.triage_model = joblib.load(os.path.join(self.model_dir, 'triage.pkl'))
            self.los_model = joblib.load(os.path.join(self.model_dir, 'los.pkl'))
            self.encoder_complaint = joblib.load(os.path.join(self.model_dir, 'encoder_complaint.pkl'))
            self.encoder_urgency = joblib.load(os.path.join(self.model_dir, 'encoder_urgency.pkl'))
            print("Agent: Models loaded successfully.")
        except FileNotFoundError as e:
            print(f"CRITICAL ERROR: Could not load models. {e}")
            print("Did you run your Jupyter Notebook training script yet?")

    def predictor(self, patient_features):
        """
        Input: Dictionary of patient data (Age, BP, Complaint, etc.)
        Output: (predicted_urgency_code, predicted_los_days)
        """
        # 1. Prepare Data for Model
        # We must convert 'Complaint' text to a number using the Encoder
        try:
            complaint_code = self.encoder_complaint.transform([patient_features['Complaint']])[0]
        except ValueError:
            # Handle unknown complaints (fallback to common one)
            complaint_code = 0 
        
        # Create a DataFrame matching the EXACT order of training columns
        input_data_triage = pd.DataFrame([{
            'HR': patient_features['HR'],
            'BP': patient_features['BP'],
            'Temp': patient_features['Temp'],
            'SpO2': patient_features['SpO2'],
            'Complaint_Code': complaint_code
        }])

        input_data_los = pd.DataFrame([{
            'Age': patient_features['Age'],
            'Gender': patient_features['Gender'],
            'HR': patient_features['HR'],
            'BP': patient_features['BP'],
            'Temp': patient_features['Temp'],
            'SpO2': patient_features['SpO2'],
            'Complaint_Code': complaint_code
        }])

        # 2. Run Predictions
        urgency_pred = self.triage_model.predict(input_data_triage)[0]
        los_pred = self.los_model.predict(input_data_los)[0]
        
        # Ensure LOS isn't negative
        los_pred = max(1.0, round(los_pred, 1))
        
        return urgency_pred, los_pred

    def allocate_resources(self, patient, hospital):
        """
        THE DECISION LOGIC (Constraint Satisfaction)
        Decides where to put the patient based on predictions and hospital state.
        """
        # Get AI predictions
        urgency, los = self.predictor(patient.features)
        
        # Assign these predictions to the patient object for HMM use later
        patient.urgency_label = urgency
        patient.expected_los = los
        
        # --- STRATEGY RULES ---
        
        # 1. CRITICAL PATIENTS (Label 0)
        if urgency == 0:
            # Try ICU first
            if hospital.admit_patient(patient, "ICU"):
                return "Assigned ICU (Critical)"
            # If ICU full, try General (Step-down care)
            elif hospital.admit_patient(patient, "GENERAL"):
                return "Assigned General (ICU Overflow)"
            else:
                return "Refused (No Beds)"

        # 2. MEDIUM PATIENTS (Label 2)
        elif urgency == 2:
            # Try General Ward
            if hospital.admit_patient(patient, "GENERAL"):
                return "Assigned General (Medium)"
            else:
                return "Refused (No General Beds)"

        # 3. LOW PATIENTS (Label 1)
        else:
            # Try General Ward, but only if we have > 10% capacity buffer
            # (Don't fill the hospital with healthy people!)
            free_general = hospital.capacity["GENERAL"] - len(hospital.occupied["GENERAL"])
            if free_general > (hospital.capacity["GENERAL"] * 0.1):
                if hospital.admit_patient(patient, "GENERAL"):
                    return "Assigned General (Low)"
            
            return "Refused (Low Priority / Ward Full)"