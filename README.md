# 🏥 Hospital Resource AI Simulator

A Machine Learning-powered simulation that manages hospital resources by predicting patient urgency and allocating beds (ICU vs General Ward) accordingly.

![Streamlit Dashboard](https://img.shields.io/badge/Interface-Streamlit-FF4B4B)
![Status](https://img.shields.io/badge/Status-Active-success)

## 🏥 Business Context
Hospital Emergency Departments (EDs) often face the critical challenge of **resource allocation**. With a finite number of ICU and General Ward beds, hospital administrators must make split-second decisions on patient admission.

**The Problem:**
- **Overcrowding & Wait Times:** Inefficient triage leads to long wait times and potential adverse outcomes.
- **Resource Bottlenecks:** ICU beds are scarce and expensive; misallocation denies critical care to those who need it most.
- **Unpredictability:** Patient influx is stochastic, making static planning ineffective.

**The Solution:**
This AI Simulator serves as a decision-support tool demonstrating how **Machine Learning** can optimize these operations. By accurately predicting **Urgency** (Triage) and **Length of Stay** (LOS), the system helps:
1.  **Prioritize Critical Patients:** Ensuring immediate access to life-saving resources.
2.  **Optimize Bed Utilization:** Forecasting bed turnover (LOS) allows for better capacity planning.
3.  **Simulate "What-If" Scenarios:** Allowing administrators to stress-test hospital capacity under high-load conditions.

## 📌 Overview
This project simulates a hospital environment where an AI Agent acts as the Triage Officer.
1.  **Synthetic Patients** arrive with random vitals and complaints.
2.  **AI Models** (Triage & LOS) predict:
    *   **Urgency Level** (Critical, Medium, Low).
    *   **Length of Stay (LOS)** in days.
3.  **Resource Allocator** assigns beds based on prediction and availability.
4.  **Simulation** runs day-by-day, handling discharges, bed freeing, and (unfortunately) patient deaths if resources are unavailable.

## ✨ Key Features
*   **🤖 AI Triage**: Uses Random Forest & Naive Bayes classifiers to prioritize patients based on vitals (HR, BP, SpO2, etc.).
*   **📊 Interactive Dashboard**: A **Streamlit** web app to control simulation speed, capacity, and view real-time analytics.
*   **📉 Real-time Visualization**: Live charts for bed occupancy and scrolling patient logs.
*   **📑 Post-Simulation Report**: auto-generated analysis of admission rates, refusal statistics, and clinical breakdowns.

## 🚀 Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository_url>
    cd hospital_resource_ai
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## 🎮 Usage

### Option 1: Interactive Dashboard (Recommended)
Run the Streamlit app for a visual experience:
```bash
streamlit run app.py
```
*   **Sidebar**: Adjust ICU/General beds, Daily Arrivals, and Simulation Speed.
*   **Tabs**: Switch between live charts, patient logs, and the final report.

### Option 2: Command Line Interface (Legacy)
Run the script directly in your terminal:
```bash
python main.py
```
*   Enter the number of daily patients when prompted.
*   View text-based logs of the simulation.

## 📂 Project Structure
```text
hospital_resource_ai/
├── app.py                # Main Streamlit Application
├── main.py               # CLI Entry Point
├── requirements.txt      # Python Dependencies
├── data/                 # Raw and processed patient data
├── notebooks/            # Jupyter Notebooks for model training
│   ├── triage_analysis.py # Generates Triage Model
│   └── los.py             # Generates LOS Model
└── src/
    ├── agent/
    │   └── allocator.py  # AI Agent logic (Prediction & Assignment)
    ├── models/           # Pre-trained .pkl models
    └── simulation/
        ├── generator.py  # Synthetic patient generator
        └── hospital_env.py # Hospital State & logic (Beds, Patient objects)
```

## 🧠 Model Details
The system relies on two key models stored in `src/models/`:
1.  **Triage Model**: Classifies patients into `Critical`, `Medium`, or `Low` urgency.
2.  **LOS Model**: Regressor that predicts expected days in hospital.

*To retrain models, run the scripts in the `notebooks/` directory.*

## 📊 Model Evaluation Metrics

### 1. Triage Model (Classification)
The Triage model predicts patient urgency (`Critical`, `Medium`, `Low`) based on vital signs.
- **Algorithm:** Naive Bayes (GaussianNB)
- **Performance:**
    - **Accuracy:** ~82%
    - **Precision (Weighted):** 0.85
    - **Recall (Weighted):** 0.82
    - **F1-Score (Weighted):** 0.81

### 2. Length of Stay (LOS) Model (Regression)
The LOS model predicts the number of days a patient will require hospitalization. We compared Linear Regression and Random Forest models.
- **Winner:** **Random Forest Regressor**
- **Performance:**
    - **R² Score:** 0.85 (vs 0.55 for Linear Regression)
    - **Mean Absolute Error (MAE):** ~1.10 days
    - **Root Mean Squared Error (RMSE):** ~1.44 days

*The Random Forest model captures the non-linear relationships in patient data significantly better than the linear baseline.*

## 📈 Dashboard Preview
-   **Live Monitor**: Watch ICU and General Bed gauges fill up.
-   **Report Tab**: Analyze which complaints (Flu, Trauma, etc.) caused the most congestion.
