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
    if complaint == 'Chest Pain':
        hr = random.randint(100, 140)
        bp = random.randint(150, 190)
        temp = random.uniform(36.5, 37.5)
        spo2 = random.randint(94, 99)
    elif complaint == 'Flu':
        hr = random.randint(80, 110)
        bp = random.randint(110, 130)
        temp = random.uniform(37.5, 40.0)
        spo2 = random.randint(95, 99)
    elif complaint == 'Difficulty Breathing':
        hr = random.randint(90, 120)
        bp = random.randint(130, 160)
        temp = random.uniform(36.5, 37.5)
        spo2 = random.randint(80, 92) # Low Oxygen!
    else: # Trauma
        hr = random.randint(100, 130)
        bp = random.randint(80, 100) # Low BP
        temp = random.uniform(36.5, 37.0)
        spo2 = random.randint(90, 99)

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
def run_simulation(days=30, new_patients_per_day=10):
    print("------------------------------------------------")
    print("INITIALIZING HOSPITAL AI SYSTEM")
    print("------------------------------------------------")

    # 1. Setup the Environment
    # We create a small hospital to force the AI to make tough choices
    hospital = Hospital(total_icu=5, total_general=20) 
    
    # 2. Wake up the Agent
    agent = HospitalAgent(model_dir='src/models/') # Loads .pkl files

    patient_counter = 0

    # 3. Run the Time Loop
    for day in range(1, days + 1):
        print(f"\n=== DAY {day} ===")
        
        # A. Update existing patients (HMM Logic)
        hospital.simulate_day()
        
        # B. Generate New Arrivals
        print(f"\n--- New Arrivals ({new_patients_per_day}) ---")
        for _ in range(new_patients_per_day):
            patient_counter += 1
            
            # Create raw features
            features = generate_random_patient_features()
            
            # PRE-PROCESS: Ask Agent for initial prediction 
            # (We need this to initialize the Patient object's HMM state)
            pred_urgency, pred_los = agent.predictor(features)
            
            # Create Patient Object
            new_patient = Patient(patient_counter, features, pred_los, pred_urgency)
            
            # AGENT DECISION
            action = agent.allocate_resources(new_patient, hospital)
            
            # Visualize the decision
            urgency_text = ["Low", "Med", "Crit"][pred_urgency]
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
    run_simulation(days=7, new_patients_per_day=5)