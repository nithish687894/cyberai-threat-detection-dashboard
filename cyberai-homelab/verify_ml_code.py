import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
from sklearn.cluster import KMeans

def test_pipeline():
    print("Loading dataset...")
    df = pd.read_csv("notebooks/data/network_connections.csv")
    print(f"Shape: {df.shape}")
    
    print("\nPre-processing features...")
    X = df.drop(columns=['uid', 'label', 'attack_type'])
    y = df['label']
    
    categorical_cols = ['proto', 'service', 'conn_state']
    X_encoded = pd.get_dummies(X, columns=categorical_cols, drop_first=True)
    X_encoded = X_encoded.astype(float)
    print(f"Encoded shape: {X_encoded.shape}")
    
    print("\nSplitting train/test...")
    X_train, X_test, y_train, y_test = train_test_split(
        X_encoded, y, test_size=0.20, random_state=42, stratify=y
    )
    
    print("\nScaling...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print("\nTraining Logistic Regression...")
    lr_model = LogisticRegression(random_state=42)
    lr_model.fit(X_train_scaled, y_train)
    
    y_pred = lr_model.predict(X_test_scaled)
    acc = accuracy_score(y_test, y_pred)
    print(f"Logistic Regression Accuracy: {acc*100:.2f}%")
    
    print("\nTraining K-Means Clustering...")
    kmeans_model = KMeans(n_clusters=4, random_state=42, n_init=10)
    cluster_assignments = kmeans_model.fit_predict(X_train_scaled)
    
    compare_df = pd.DataFrame({
        'Actual Attack': df.loc[X_train.index, 'attack_type'],
        'Cluster': cluster_assignments
    })
    crosstab = pd.crosstab(compare_df['Actual Attack'], compare_df['Cluster'])
    print("\n=== Cluster Crosstab ===")
    print(crosstab)
    print("\nML pipeline verification completed successfully!")

if __name__ == "__main__":
    test_pipeline()
