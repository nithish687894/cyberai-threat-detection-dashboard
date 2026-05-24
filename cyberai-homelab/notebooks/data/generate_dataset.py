import os
import numpy as np
import pandas as pd

def generate_cyber_dataset(output_path, num_samples=10000, random_state=42):
    np.random.seed(random_state)
    
    # Ratios
    n_benign = int(num_samples * 0.70)
    n_ddos = int(num_samples * 0.10)
    n_portscan = int(num_samples * 0.12)
    n_bruteforce = int(num_samples * 0.08)
    
    data = []
    
    # ------------------ 1. BENIGN TRAFFIC ------------------
    # Benign traffic is varied, has standard data transfer, SF connection states
    for _ in range(n_benign):
        proto = np.random.choice(['tcp', 'udp', 'icmp'], p=[0.75, 0.22, 0.03])
        service = '-'
        if proto == 'tcp':
            service = np.random.choice(['http', 'ssl', 'ssh', '-'], p=[0.40, 0.40, 0.05, 0.15])
        elif proto == 'udp':
            service = 'dns'
            
        duration = np.random.lognormal(mean=1.2, sigma=0.8) # Average duration ~3-5 seconds
        orig_pkts = int(np.random.lognormal(mean=2.0, sigma=0.6)) + 1
        resp_pkts = int(np.random.lognormal(mean=2.2, sigma=0.8)) + 1
        
        # Bytes are correlated with packets
        orig_bytes = orig_pkts * np.random.randint(60, 1000)
        resp_bytes = resp_pkts * np.random.randint(100, 3000)
        
        conn_state = np.random.choice(['SF', 'S1', 'REJ', 'RSTO'], p=[0.90, 0.04, 0.04, 0.02])
        
        data.append({
            'proto': proto,
            'service': service,
            'duration': round(duration, 4),
            'orig_bytes': orig_bytes,
            'resp_bytes': resp_bytes,
            'conn_state': conn_state,
            'orig_pkts': orig_pkts,
            'resp_pkts': resp_pkts,
            'label': 0,
            'attack_type': 'benign'
        })
        
    # ------------------ 2. DDOS TRAFFIC ------------------
    # DDoS traffic has extremely high packet counts but 0 or tiny bytes, very short durations, and S0 states (half-open)
    for _ in range(n_ddos):
        proto = np.random.choice(['tcp', 'udp'], p=[0.8, 0.2])
        service = '-'
        duration = np.random.uniform(0.0001, 0.05) # Tiny duration
        orig_pkts = np.random.randint(1, 3) # Very few packets per connection
        resp_pkts = 0 # No response from overwhelmed server
        
        orig_bytes = 0 # SYN flood packets contain no payload
        resp_bytes = 0
        
        conn_state = 'S0' # Connection attempt, no reply
        
        data.append({
            'proto': proto,
            'service': service,
            'duration': round(duration, 5),
            'orig_bytes': orig_bytes,
            'resp_bytes': resp_bytes,
            'conn_state': conn_state,
            'orig_pkts': orig_pkts,
            'resp_pkts': resp_pkts,
            'label': 1,
            'attack_type': 'ddos'
        })
        
    # ------------------ 3. PORTSCAN TRAFFIC ------------------
    # Portscans scan many ports, resulting in rapid connection attempts that are either ignored (S0) or rejected (REJ)
    for _ in range(n_portscan):
        proto = 'tcp'
        service = '-'
        duration = np.random.uniform(0.0, 0.01) # Near zero
        orig_pkts = 1 # Only SYN packet
        resp_pkts = np.random.choice([0, 1], p=[0.7, 0.3]) # 0 if silent/filtered, 1 if rejected (RST)
        
        orig_bytes = 0
        resp_bytes = 0
        
        conn_state = np.random.choice(['S0', 'REJ'], p=[0.7, 0.3])
        
        data.append({
            'proto': proto,
            'service': service,
            'duration': round(duration, 5),
            'orig_bytes': orig_bytes,
            'resp_bytes': resp_bytes,
            'conn_state': conn_state,
            'orig_pkts': orig_pkts,
            'resp_pkts': resp_pkts,
            'label': 1,
            'attack_type': 'portscan'
        })
        
    # ------------------ 4. BRUTEFORCE TRAFFIC ------------------
    # Bruteforce attempts involve making SSH or FTP login connections, resulting in repetitive connections
    for _ in range(n_bruteforce):
        proto = 'tcp'
        service = np.random.choice(['ssh', 'ftp'], p=[0.8, 0.2])
        duration = np.random.uniform(1.0, 4.0) # Standard authentication timeouts
        orig_pkts = np.random.randint(6, 12) # Handshake + credentials
        resp_pkts = np.random.randint(5, 10) # Handshake + failure response
        
        # Small bytes representing username/password attempts
        orig_bytes = orig_pkts * np.random.randint(40, 80)
        resp_bytes = resp_pkts * np.random.randint(30, 60)
        
        conn_state = 'SF' # Successful TCP termination (even if login failed)
        
        data.append({
            'proto': proto,
            'service': service,
            'duration': round(duration, 4),
            'orig_bytes': orig_bytes,
            'resp_bytes': resp_bytes,
            'conn_state': conn_state,
            'orig_pkts': orig_pkts,
            'resp_pkts': resp_pkts,
            'label': 1,
            'attack_type': 'bruteforce'
        })
        
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Shuffle the dataset
    df = df.sample(frac=1, random_state=random_state).reset_index(drop=True)
    
    # Add unique UID
    df.insert(0, 'uid', [f"C{str(i).zfill(6)}" for i in range(len(df))])
    
    # Save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Successfully generated {len(df)} realistic network traffic samples at: {output_path}")

if __name__ == "__main__":
    output_file = os.path.join(os.path.dirname(__file__), "network_connections.csv")
    generate_cyber_dataset(output_file)
