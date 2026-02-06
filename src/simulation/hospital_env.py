import numpy as np
import random

class Patient:
    """
    defines about the patient and if they get better or worse
    """
    def __init__(self, patient_id, features, predicted_los, predicted_urgency):  # __init__ is used as a cunstructor

        """
        Docstring for __init__
        
        initialize a patient
        :param patient_id: unique id
        :param features: dict of data containing Age, HR, BP, etc
        :param predicted_los: predicted length of stay
        :param predicted_urgency: predicted urgency level
        """

        self.id = patient_id
        self.features = features

        self.expected_los = predicted_los
        self.urgency_label = predicted_urgency

        self.days_stayed = 0
        self.assigned_bed_type = None #initially has no bed

        if predicted_urgency == 0: # Critical
            self.current_state = "Critical"
        elif predicted_urgency == 2: # Discharge
            self.current_state = "stable"
        else:
            self.current_state = "Stable"

    def update_vitals(self):
        """
        Docstring for update_vitals
        
        logic to change patients vitals
        """
        pass

    def next_state(self):
        """
        HMM Logic with RESOURCE DEPENDENCY
        """
        # Handle Terminal States
        if self.current_state in ["Discharged", "Deceased"]:
            return self.current_state

        # Define Probabilities
        # Format: [To Stable, To Critical, To Discharged, To Deceased]
        probs = None 

        if self.current_state == "Stable":
            probs = [0.80, 0.05, 0.15, 0.00] 
            
            if self.urgency_label == 2: 
                probs = [0.80, 0.10, 0.05, 0.05]

        elif self.current_state == "Critical":
            
            if self.assigned_bed_type == "ICU":
                # [Stable, Critical, Discharged, Deceased]
                probs = [0.30, 0.60, 0.05, 0.05] 
            
            elif self.assigned_bed_type == "GENERAL":
                probs = [0.10, 0.50, 0.05, 0.35] 
                
            else:
                probs = [0.00, 0.40, 0.00, 0.60] 

        if probs is None:
            self.current_state = "Stable"
            probs = [0.80, 0.05, 0.15, 0.00]

        states = ["Stable", "Critical", "Discharged", "Deceased"]
        
        probs = np.array(probs)
        probs /= probs.sum()
        
        new_state = np.random.choice(states, p=probs)
        
        self.current_state = new_state
        return new_state

    def tick(self):
        """
        Advance patient time by 1 day
        """
        self.days_stayed += 1
        
        # Force discharge if they exceeded their LOS (Simulation Logic)
        if self.days_stayed >= self.expected_los and self.current_state != "Deceased":
            self.current_state = "Discharged"
        else:
            self.next_state()


class Hospital:
    """
    defines the Hospital and how many beds are empty
    """

    def __init__(self, total_icu, total_general):
        # Resource Tracking
        self.capacity = {
            "ICU": total_icu,
            "GENERAL": total_general
        }
        self.occupied = {
            "ICU": [],      # List of Patient Objects
            "GENERAL": []   # List of Patient Objects
        }
        
        # Statistics for Reporting
        self.stats = {
            "admitted": 0,
            "discharged": 0,
            "deceased": 0,
            "refused": 0
        }
        
    def admit_patient(self, patient, bed_type):
        """
        Docstring for admit_patient
        
        logic to put a patient in a bed and decrease available count
        """
        """
        Attempts to put a patient in a bed.
        Returns True if successful, False if full.
        """
        if len(self.occupied[bed_type]) < self.capacity[bed_type]:
            self.occupied[bed_type].append(patient)
            patient.assigned_bed_type = bed_type
            self.stats["admitted"] += 1
            return True
        else:
            self.stats["refused"] += 1
            return False

    def simulate_day(self, verbose=True):
        """
        The Main Loop: Updates every patient currently in a bed.
        Returns a list of event strings for the UI.
        """
        events = []
        if verbose:
            print(f"\n--- End of Day Report ---")
        
        for bed_type in ["ICU", "GENERAL"]:
            for patient in self.occupied[bed_type][:]: 
                
                patient.tick() # Advance time/health
                
                # Handle Departures
                if patient.current_state == "Discharged":
                    msg = f"Patient {patient.id} recovered and left {bed_type}."
                    events.append(msg)
                    if verbose: print(msg)
                    self.occupied[bed_type].remove(patient)
                    self.stats["discharged"] += 1
                    
                elif patient.current_state == "Deceased":
                    msg = f"Patient {patient.id} passed away in {bed_type}."
                    events.append(msg)
                    if verbose: print(msg)
                    self.occupied[bed_type].remove(patient)
                    self.stats["deceased"] += 1
                    
                elif patient.current_state == "Critical" and bed_type == "GENERAL":
                    msg = f"WARNING: Patient {patient.id} in General Ward turned Critical!"
                    events.append(msg)
                    if verbose: print(msg)
        
        return events

    def get_status(self):
        return {
            "ICU_Free": self.capacity["ICU"] - len(self.occupied["ICU"]),
            "Gen_Free": self.capacity["GENERAL"] - len(self.occupied["GENERAL"]),
            "Total_Refused": self.stats["refused"]
        }

    