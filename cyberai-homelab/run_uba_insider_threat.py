# --- User Behavior Analytics (UBA) for Insider Threat Detection ---
# This script implements Case Study 3 from your course syllabus:
# Using an Unsupervised Anomaly Detection algorithm (Isolation Forest)
# to detect insider threats (disgruntled employees downloading data or logging in at 3 AM).

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

def run_uba_demo():
    print("=== CASE STUDY 3: GENERATING EMPLOYEES ACTIVITY LOGS ===")
    np.random.seed(42)
    num_employees = 100
    
    # Standard employee behaviors (benign baselines)
    # - login_hour: Peak around 9 AM (standard deviation ~1.5 hours)
    # - files_accessed: Mean ~15 files per day
    # - exfil_bytes: Mean ~500 KB per day
    # - remote_access: Binary (0 = office, 1 = VPN/Remote, mostly 0)
    
    data = []
    employees_list = [f"EMP_{str(i).zfill(3)}" for i in range(num_employees)]
    
    for emp in employees_list:
        # Standard benign logs (7 days per employee = 700 logs total)
        for day in range(7):
            login_hour = np.random.normal(9.0, 1.2) # ~7:30 AM to 10:30 AM
            files_accessed = int(np.random.poisson(15))
            exfil_bytes = np.random.lognormal(mean=6.2, sigma=0.4) # ~500 KB
            remote_access = np.random.choice([0, 1], p=[0.9, 0.1])
            
            data.append({
                'employee_id': emp,
                'day': day,
                'login_hour': round(login_hour, 2),
                'files_accessed': files_accessed,
                'exfil_bytes': int(exfil_bytes),
                'remote_access': remote_access,
                'is_anomaly': 0
            })
            
    df_uba = pd.DataFrame(data)
    
    # ------------------ INJECTING INSIDER THREATS ------------------
    print("\n=== INJECTING INSIDER ATTACK SIGNATURES (MALICIOUS EMPLOYEES) ===")
    
    # Threat 1: Disgruntled Employee (EMP_014) exfiltrating code/secrets
    # Behavioral anomaly: accessing 150+ sensitive files, transferring 85 MB
    print("- Injecting Data Exfiltration Anomaly for EMP_014...")
    df_uba.loc[(df_uba['employee_id'] == 'EMP_014') & (df_uba['day'] == 5), 
               ['files_accessed', 'exfil_bytes', 'is_anomaly']] = [187, 85000000, 1]
               
    # Threat 2: Compromised Account (EMP_067) hijacked by attacker
    # Behavioral anomaly: remote login at 3:15 AM from unusual geographic zone
    print("- Injecting Hijacked Credential Anomaly for EMP_067...")
    df_uba.loc[(df_uba['employee_id'] == 'EMP_067') & (df_uba['day'] == 3), 
               ['login_hour', 'remote_access', 'is_anomaly']] = [3.25, 1, 1]
               
    print(f"Total user activity database generated: {len(df_uba)} active rows.")
    
    # ------------------ TRAINING ISOLATION FOREST ------------------
    print("\n=== STEP 2: PREPROCESSING & TRAINING ISOLATION FOREST ===")
    
    # Select numerical features for anomaly detection
    features = ['login_hour', 'files_accessed', 'exfil_bytes', 'remote_access']
    X = df_uba[features]
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Initialize Isolation Forest
    # contamination=0.005 means we expect around 0.5% anomalies (2 anomalous records out of 700)
    iso_forest = IsolationForest(contamination=0.005, random_state=42)
    
    # Fit model & predict outliers
    # Isolation Forest outputs: 1 for normal data, -1 for anomalies/outliers
    predictions = iso_forest.fit_predict(X_scaled)
    
    # Get anomaly scores (lower/more negative score = more anomalous)
    anomaly_scores = iso_forest.decision_function(X_scaled)
    
    # Append results back to DataFrame
    df_uba['anomaly_prediction'] = predictions
    df_uba['anomaly_score'] = anomaly_scores
    
    # ------------------ EVALUATING UBA DETECTION ------------------
    print("\n=== STEP 3: USER RISK SCORING & THREAT HUNTING ===")
    
    # Find records flagged as anomalies (prediction == -1)
    anomalies_detected = df_uba[df_uba['anomaly_prediction'] == -1].copy()
    
    print(f"Isolation Forest flagged {len(anomalies_detected)} suspicious user sessions:")
    
    for idx, row in anomalies_detected.iterrows():
        print(f"\n[ALERT] Suspicious Session Detected!")
        print(f" |-- Employee ID    : {row['employee_id']}")
        print(f" |-- Day of Week    : Day {row['day']}")
        print(f" |-- Login Hour     : {row['login_hour']} AM/PM")
        print(f" |-- Files Accessed : {row['files_accessed']} sensitive records")
        print(f" |-- Data Transferred: {row['exfil_bytes'] / (1024*1024):.2f} MB")
        print(f" |-- Remote (VPN)   : {'Yes' if row['remote_access'] == 1 else 'No'}")
        print(f" |-- Anomaly Score  : {row['anomaly_score']:.4f} (Severe)")
        print(f" +-- True Threat?   : {'YES (True Positive)' if row['is_anomaly'] == 1 else 'NO (False Alarm)'}")

    # Aggregating a "Risk Scorecard" for the SRM Security Report
    print("\n=== STEP 4: COMPILING EXECUTIVE RISK SCORECARD ===")
    risk_scorecard = df_uba.groupby('employee_id').agg({
        'anomaly_score': 'min', # Find their most anomalous single day score
        'files_accessed': 'sum',
        'exfil_bytes': 'sum'
    }).sort_values(by='anomaly_score').head(5)
    
    print("Top 5 Most Suspicious Employees inside Corporate Network (Lowest Anomaly Scores):")
    print(risk_scorecard)
    print("\nCase Study 3: UBA Insider Threat Detection completed successfully!")

if __name__ == "__main__":
    run_uba_demo()
