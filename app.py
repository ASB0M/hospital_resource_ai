import streamlit as st
import time
import pandas as pd
import random
from src.simulation.hospital_env import Hospital, Patient
from src.agent.allocator import HospitalAgent
from src.simulation.generator import generate_random_patient_features

st.set_page_config(page_title="Hospital AI Simulator", layout="wide")

# --- INITIALIZATION ---
if 'hospital' not in st.session_state:
    st.session_state.hospital = None
if 'agent' not in st.session_state:
    st.session_state.agent = None
if 'day' not in st.session_state:
    st.session_state.day = 0
if 'simulation_running' not in st.session_state:
    st.session_state.simulation_running = False
if 'patient_history' not in st.session_state:
    st.session_state.patient_history = []
if 'stats_history' not in st.session_state:
    st.session_state.stats_history = []
if 'patient_counter' not in st.session_state:
    st.session_state.patient_counter = 0

def reset_simulation(icu_beds, gen_beds):
    st.session_state.hospital = Hospital(total_icu=icu_beds, total_general=gen_beds)
    st.session_state.agent = HospitalAgent(model_dir='src/models/')
    st.session_state.day = 0
    st.session_state.patient_history = []
    st.session_state.stats_history = []
    st.session_state.patient_counter = 0

# --- SIDEBAR ---
with st.sidebar:
    st.title("🏥 Configuration")
    
    st.subheader("Simulation Parameters")
    days_to_sim = st.number_input("Duration (Days)", min_value=1, max_value=365, value=50)
    sim_speed = st.slider("Simulation Speed (sec)", 0.05, 1.0, 0.2)
    
    st.subheader("Hospital Capacity")
    icu_beds = st.slider("ICU Beds", 5, 50, 15)
    gen_beds = st.slider("General Beds", 10, 100, 40)
    
    st.subheader("Scenario")
    max_patients = st.slider("Max Arrivals / Day", 5, 50, 20)
    
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶ Start", type="primary"):
            if st.session_state.hospital is None:
                reset_simulation(icu_beds, gen_beds)
            st.session_state.simulation_running = True
    
    with col2:
        if st.button("⏸ Pause"):
            st.session_state.simulation_running = False

    if st.button("🔄 Reset Simulation"):
        reset_simulation(icu_beds, gen_beds)
        st.session_state.simulation_running = False
        st.rerun()

# --- MAIN DASHBOARD ---
st.title("🚑 Hospital Resource AI Dashboard")

# Top Metrics Row
if st.session_state.hospital:
    status = st.session_state.hospital.get_status()
    
    # Calculate Occupancy %
    icu_occ = icu_beds - status['ICU_Free']
    gen_occ = gen_beds - status['Gen_Free']
    icu_pct = icu_occ / icu_beds
    gen_pct = gen_occ / gen_beds
    
    # 1. VISUAL STATUS
    col1, col2 = st.columns(2)
    with col1:
        st.metric("ICU Occupancy", f"{icu_occ} / {icu_beds}", f"{int(icu_pct*100)}%")
        st.progress(icu_pct)
        
    with col2:
        st.metric("General Occupancy", f"{gen_occ} / {gen_beds}", f"{int(gen_pct*100)}%")
        st.progress(gen_pct)
    
    st.divider()

    # 2. NUMERICAL METRICS
    m1, m2, m3 = st.columns(3)
    m1.metric("Current Day", f"{st.session_state.day} / {days_to_sim}")
    m2.metric("Total Admitted", st.session_state.hospital.stats['admitted'])
    m3.metric("Total Refused", status['Total_Refused'], delta_color="inverse")

else:
    st.info("Click 'Start' in the sidebar to begin the simulation.")
    st.stop()

# --- SIMULATION LOGIC ---
if st.session_state.simulation_running:
    if st.session_state.day >= days_to_sim:
        st.session_state.simulation_running = False
        st.success("Simulation Complete!")
        st.stop()

    # 1. Simulate Day
    # We ignore raw logs now, focusing on data
    st.session_state.hospital.simulate_day(verbose=False)

    # 2. New Arrivals
    new_patients_count = random.randint(1, max_patients)
    for _ in range(new_patients_count):
        st.session_state.patient_counter += 1
        p_id = st.session_state.patient_counter
        features = generate_random_patient_features()
        
        # AI Prediction
        pred_urgency, pred_los = st.session_state.agent.predictor(features)
        new_patient = Patient(p_id, features, pred_los, pred_urgency)
        
        # Bed Allocation
        action = st.session_state.agent.allocate_resources(new_patient, st.session_state.hospital)
        
        # Structure Data for Table
        urgency_map = {0: "Critical", 1: "Low", 2: "Medium"}
        urgency_text = urgency_map.get(pred_urgency, "Unknown")
        
        patient_record = {
            "Day": st.session_state.day,
            "ID": p_id,
            "Age": features['Age'],
            "Complaint": features['Complaint'],
            "AI Urgency": urgency_text,
            "Action": action,
            "Outcome": "Admitted" if "Refused" not in action else "Refused"
        }
        st.session_state.patient_history.insert(0, patient_record) # Add to top

    # 3. Update Stats History
    current_status = st.session_state.hospital.get_status()
    st.session_state.stats_history.append({
        "Day": st.session_state.day,
        "ICU_Occupied": icu_beds - current_status['ICU_Free'],
        "General_Occupied": gen_beds - current_status['Gen_Free'],
        "Total_Refused": current_status['Total_Refused']
    })
    
    st.session_state.day += 1
    time.sleep(sim_speed)
    st.rerun()

# --- DATA VISUALIZATION ---
tab1, tab2, tab3 = st.tabs(["📊 Charts", "📋 Recent Patients", "📑 Simulation Report"])

with tab1:
    if st.session_state.stats_history:
        st.subheader("Occupancy Over Time")
        df_hist = pd.DataFrame(st.session_state.stats_history)
        st.line_chart(df_hist, x="Day", y=["ICU_Occupied", "General_Occupied"])

with tab2:
    st.subheader("Patient Admission Log (Latest First)")
    if st.session_state.patient_history:
        df_patients = pd.DataFrame(st.session_state.patient_history)
        
        # Color coding helper
        def highlight_urgency(val):
            color = 'white'
            if val == 'Critical': color = '#FFcccb' # light red
            elif val == 'Medium': color = '#FFDD99' # light orange
            elif val == 'Low': color = '#90EE90' # light green
            return f'background-color: {color}; color: black'

        # Display optimized table
        st.dataframe(
            df_patients.style.applymap(highlight_urgency, subset=['AI Urgency']),
            use_container_width=True,
            height=400
        )

with tab3:
    if not st.session_state.patient_history:
        st.info("Run the simulation to generate a report.")
    else:
        st.subheader("🏥 Post-Simulation Analysis Report")
        df = pd.DataFrame(st.session_state.patient_history)
        
        # --- 1. KEY METRICS ---
        total_patients = len(df)
        total_admitted = len(df[df['Outcome'] == 'Admitted'])
        total_refused = len(df[df['Outcome'] == 'Refused'])
        admission_rate = (total_admitted / total_patients) * 100
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Arrivals", total_patients)
        c2.metric("Admitted", total_admitted)
        c3.metric("Refused", total_refused, delta_color="inverse")
        c4.metric("Admission Rate", f"{admission_rate:.1f}%")
        
        st.divider()
        
        # --- 2. DEMOGRAPHICS & CLINICAL ---
        c_chart1, c_chart2 = st.columns(2)
        
        with c_chart1:
            st.markdown("#### Complaint Distribution")
            complaint_counts = df['Complaint'].value_counts()
            st.bar_chart(complaint_counts)
            
        with c_chart2:
            st.markdown("#### Urgency Breakdown")
            # Urgency Distribution
            urgency_counts = df['AI Urgency'].value_counts()
            st.bar_chart(urgency_counts, color="#FF4B4B") # Red theme

        # --- 3. OUTCOMES ---
        st.divider()
        st.markdown("#### Outcomes by Urgency")
        
        # Pivot table for Admitted vs Refused by Urgency
        outcome_pivot = df.groupby(['AI Urgency', 'Outcome']).size().unstack(fill_value=0)
        st.bar_chart(outcome_pivot)

        # --- 4. DOWNLOAD ---
        st.divider()
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download Full Patient Report (CSV)",
            data=csv,
            file_name="simulation_report.csv",
            mime="text/csv"
        )
