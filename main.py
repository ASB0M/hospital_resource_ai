# main.py

import random
import time
import pandas as pd
import numpy as np

# Import our custom modules
from src.simulation.hospital_env import Hospital, Patient
from src.agent.allocator import HospitalAgent

# ---------------------------------------------------------
# HELPER: Generate Random Patient Features (On the Fly)
# ---------------------------------------------------------
def generate_random_patient_features():
    """
    Creates a dictionary of random vitals to simulate a new arrival.
    We use similar logic to the generator to ensure realistic patterns.
    """
    complaint = random.choice(['Chest Pain', 'Flu', 'Difficulty Breathing', 'Trauma'])
    
    # Basic correlations
    hr = random.randint(60, 90)       # Normal
    bp = random.randint(110, 130)     # Normal
    temp = random.uniform(36.5, 37.2) # Normal
    spo2 = random.randint(97, 100)    # Normal

    if complaint == 'Chest Pain':
        hr = random.randint(100, 140)   # Tachycardia
        bp = random.randint(150, 200)   # Hypertension
        # Chest pain usually has normal temp/spo2
            
    elif complaint == 'Flu':
        temp = random.uniform(37.5, 40.5) # Fever
        hr = random.randint(90, 110)
            
    elif complaint == 'Difficulty Breathing':
        spo2 = random.randint(80, 95)     # Hypoxia
        hr = random.randint(100, 120)

    elif complaint == 'Trauma':
        hr = random.randint(110, 140)     # Shock
        bp = random.randint(80, 110) 
        
    return {
        "Age": random.randint(18, 90),
        "Gender": random.choice([0, 1]),
        "HR": hr,
        "BP": bp,
        "Temp": round(temp, 1),
        "SpO2": spo2,
        "Complaint": complaint
    }

# ---------------------------------------------------------
# MAIN SIMULATION LOOP
# ---------------------------------------------------------
def run_simulation(days, max_patients_per_day):
    print("------------------------------------------------")
    print("INITIALIZING HOSPITAL AI SYSTEM")
    print("------------------------------------------------")

    # 1. Setup the Environment
    # We create a small hospital to force the AI to make tough choices
    hospital = Hospital(total_icu=15, total_general=40) 
    
    # 2. Wake up the Agent
    agent = HospitalAgent(model_dir='src/models/') # Loads .pkl files

    patient_counter = 0

    # 3. Run the Time Loop
    for day in range(1, days + 1):
        print(f"\n=== DAY {day} ===")
        
        # A. Update existing patients (HMM Logic)
        hospital.simulate_day()
        
        # B. Generate New Arrivals

        new_patients_per_day = random.randint(1, max_patients_per_day)

        print(f"\n--- New Arrivals ({new_patients_per_day}) ---")
        # ... inside run_simulation ...

        print(f"\n--- New Arrivals ({new_patients_per_day}) ---")
        
        # OPTIMIZATION: In a real system, we would batch this.
        # For this simulation, we will keep the loop but ensure data flow is clean.
        
        for _ in range(new_patients_per_day):
            patient_counter += 1
            
            # 1. Generate Raw Data
            features = generate_random_patient_features()
            
            # 2. Predict (Uses the fixed Allocator logic)
            # The agent now handles the Dict -> DataFrame conversion internally
            pred_urgency, pred_los = agent.predictor(features)
            
            # 3. Create Patient
            new_patient = Patient(patient_counter, features, pred_los, pred_urgency)
            
            # 4. Decide
            action = agent.allocate_resources(new_patient, hospital)
            
            # 5. Logging (Fixing the Urgency Text mapping)
            # MAPPING: 0=Critical, 1=Low, 2=Medium (Alphabetical)
            urgency_map = {0: "Critical", 1: "Low", 2: "Medium"}
            urgency_text = urgency_map.get(pred_urgency, "Unknown")
            
            print(f"Patient {patient_counter} ({features['Complaint']}) -> AI: {urgency_text} -> Action: {action}")

        # C. Print Daily Status
        status = hospital.get_status()
        print(f"\n--- Bed Status ---")
        print(f"[ICU]: {status['ICU_Free']} free")
        print(f"[General]: {status['Gen_Free']} free")
        print(f"[Turned Away]: {status['Total_Refused']} total")
        
        # Optional: Sleep to make it look like a real-time log
        time.sleep(0.5)

    print("\n------------------------------------------------")
    print("SIMULATION COMPLETE")
    print(f"Total Admitted: {hospital.stats['admitted']}")
    print(f"Total Deceased: {hospital.stats['deceased']}")
    print(f"Total Discharged: {hospital.stats['discharged']}")
    print("------------------------------------------------")

if __name__ == "__main__":

    max_patients_per_day = input("Enter the number of new patients arriving each day (e.g., 20): ")

    run_simulation(days=50, max_patients_per_day=int(max_patients_per_day))