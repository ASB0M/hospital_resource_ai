import pandas as pd
import numpy as np
import os
import random

def generate_patient_data(num_patients = 10000, save_path = 'data/raw/patients.csv'):
    print(f"Generating {num_patients} synthetic patients....")

    data = []

    for i in range(num_patients):
        # 1. Randomly pick a profile
        # Weighted choice: Make Chest Pain and Trauma slightly rarer than Flu
        complaint = random.choices(
            ['Chest Pain', 'Flu', 'Difficulty Breathing', 'Trauma', 'General Checkup'],
            weights=[20, 30, 15, 15, 20], 
            k=1
        )[0]
        
        age = random.randint(18, 90)

        # 2. Generate Vitals based on profile (CORRELATION STEP)
        # We set defaults, then override based on complaint
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
            bp = random.randint(80, 110)      # Hypotension (bleeding)
            
        # 3. Assign Labels (THE IMPROVED LOGIC)
        # Priority: Critical -> Medium -> Low
        
        # CRITICAL CRITERIA (Any of these makes you Critical)
        if (complaint == 'Chest Pain' and bp > 160) or \
           (spo2 < 90) or \
           (complaint == 'Trauma' and bp < 90) or \
           (hr > 130):
            urgency = "Critical"
            
        # MEDIUM CRITERIA (If not Critical, check these)
        elif (temp > 38.5) or \
             (complaint == 'Chest Pain') or \
             (complaint == 'Trauma') or \
             (bp > 150):
            urgency = "Medium"
            
        # LOW CRITERIA
        else:
            urgency = "Low"

        # 4. Logic for Length of Stay (LOS)
        # Add noise using random.gauss so regression isn't too easy
        base_stay = 2
        
        if urgency == "Critical":
            base_stay += random.randint(5, 10) # 7-12 days
        elif urgency == "Medium":
            base_stay += random.randint(2, 5)  # 4-7 days
            
        if age > 65:
            base_stay += 3
            
        # Ensure no negative days, round to 1 decimal
        los = max(1.0, round(base_stay + random.uniform(-1, 1), 1))

        # 5. Append
        data.append({
            "ID": i,
            "Age": age,
            "Gender": random.choice([0, 1]), # 0=M, 1=F
            "HR": hr,
            "BP": bp,
            "Temp": round(temp, 1),
            "SpO2": spo2,
            "Complaint": complaint,
            "Urgency": urgency, 
            "LOS": los
        })

    df = pd.DataFrame(data)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    # Save the file
    df.to_csv(save_path, index=False)
    print(f"Success! Data saved to: {save_path}")

if __name__ == "__main__":
    # This block allows you to run this script directly
    generate_patient_data()