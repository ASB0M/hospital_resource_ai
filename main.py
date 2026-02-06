# main.py

import random
import time
import pandas as pd
import numpy as np

from src.simulation.hospital_env import Hospital, Patient
from src.agent.allocator import HospitalAgent
from src.simulation.generator import generate_random_patient_features



def run_simulation(days, max_patients_per_day):
    print("------------------------------------------------")
    print("INITIALIZING HOSPITAL AI SYSTEM")
    print("------------------------------------------------")

    # Setup of hospital Environment
    hospital = Hospital(total_icu=15, total_general=40) 
    
    agent = HospitalAgent(model_dir='src/models/') # Loads .pkl files

    patient_counter = 0

    for day in range(1, days + 1):
        print(f"\n=== DAY {day} ===")
        
        hospital.simulate_day()
        
        new_patients_per_day = random.randint(1, max_patients_per_day)

        print(f"\n--- New Arrivals ({new_patients_per_day}) ---")

        
        for _ in range(new_patients_per_day):
            patient_counter += 1
            
            features = generate_random_patient_features()
            
            pred_urgency, pred_los = agent.predictor(features)
            
            new_patient = Patient(patient_counter, features, pred_los, pred_urgency)
            
            action = agent.allocate_resources(new_patient, hospital)
            
            urgency_map = {0: "Critical", 1: "Low", 2: "Medium"}
            urgency_text = urgency_map.get(pred_urgency, "Unknown")
            
            print(f"Patient {patient_counter} ({features['Complaint']}) -> AI: {urgency_text} -> Action: {action}")

        status = hospital.get_status()
        print(f"\n--- Bed Status ---")
        print(f"[ICU]: {status['ICU_Free']} free")
        print(f"[General]: {status['Gen_Free']} free")
        print(f"[Turned Away]: {status['Total_Refused']} total")
        
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