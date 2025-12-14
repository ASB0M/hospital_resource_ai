

class Patient:
    """
    defines about the patient and if they get better or worse
    """
    def __init__(self, patient_id, features):  # __init__ is used as a cunstructor

        """
        Docstring for __init__
        
        initialize a patient
        :param patient_id: unique id
        :param features: dict of data containing Age, HR, BP, etc
        """

        self.id = patient_id
        self.features = features
        self.current_state = "Stable" # default start state
        self.assigned_bed = None #initially has no bed

    def update_vitals(self):
        """
        Docstring for update_vitals
        
        logic to change patients vitals
        """
        pass

    def next_state(self):
        """
        Docstring for next_state
        
        HMM logic to calculate if patient moves to critical or discharge state
        """
        pass


class Hospital:
    """
    defines the Hospital and how many beds are empty
    """

    def __init__(self, total_icu_beds, total_general_beds):

        self.icu_beds = {"total": total_icu_beds, "occupied": 0}
        self.general_beds = {"total": total_general_beds, "occupied": 0}
        self.waiting_queue = []
        
    def admit_patient(self, patient, bed_type):
        """
        Docstring for admit_patient
        
        logic to put a patient in a bed and decrease available count
        """
        pass

    def check_availability(self, bed_type):
        """
        Docstring for check_availability
        
        returns true if a bed is free
        """

    