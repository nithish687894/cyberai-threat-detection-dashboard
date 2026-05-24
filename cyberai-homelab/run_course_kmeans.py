# --- Course Material K-Means Clustering Example ---
# This script runs the exact Python code provided in your "Lesson 2 of 72" course material.

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns

# Set style for consistency
sns.set_theme(style="whitegrid")

def run_course_kmeans():
    print("=== STEP 1: GENERATING COURSE SYNTHETIC DATA ===")
    np.random.seed(42)
    num_samples = 1000
    
    data_cluster = {
        'duration': np.random.uniform(1, 1000, num_samples),
        'protocol_type': np.random.randint(0, 3, num_samples), # 0: tcp, 1: udp, 2: icmp
        'src_bytes': np.random.randint(100, 100000, num_samples),
        'dst_bytes': np.random.randint(50, 50000, num_samples)
    }
    df_cluster_orig = pd.DataFrame(data_cluster) # Keep original for interpretation
    
    print(f"Data shape: {df_cluster_orig.shape}")
    print("Sample data:")
    print(df_cluster_orig.head())
    
    print("\n=== STEP 2: SCALING FEATURES ===")
    scaler_cluster = StandardScaler()
    X_cluster_scaled = scaler_cluster.fit_transform(df_cluster_orig)
    print("Features scaled successfully.")
    
    print("\n=== STEP 3: RUNNING ELBOW METHOD ===")
    inertia = []
    k_range = range(1, 11)
    
    # In the course code there was a small typo: "kmeans_અelbow" (containing an Indian character 'અ'). 
    # We have corrected this typo to "kmeans_elbow" so the code compiles and runs perfectly!
    for k in k_range:
        kmeans_elbow = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans_elbow.fit(X_cluster_scaled)
        inertia.append(kmeans_elbow.inertia_)
        
    print("Inertia values calculated for K=1 to 10.")
    print("Generating Elbow Plot (saving as elbow_plot.png)...")
    plt.figure(figsize=(10, 6))
    plt.plot(k_range, inertia, marker='o', color='purple', lw=2)
    plt.title('Elbow Method for K-Means (Course Code)')
    plt.xlabel('Number of Clusters (k)')
    plt.ylabel('Inertia')
    plt.grid(True)
    plt.savefig('elbow_plot.png')
    plt.close()
    print("Elbow plot saved successfully as 'elbow_plot.png'.")
    
    print("\n=== STEP 4: APPLYING K-MEANS WITH K=3 ===")
    k_chosen = 3
    kmeans = KMeans(n_clusters=k_chosen, random_state=42, n_init=10)
    kmeans.fit(X_cluster_scaled)
    cluster_labels = kmeans.labels_
    
    # Add labels back to original data
    df_cluster_orig['Cluster'] = cluster_labels
    
    print(f"K-Means completed. Cluster labels assigned (first 10): {cluster_labels[:10]}")
    
    print("\n=== STEP 5: VISUALIZING CLUSTERS WITH PCA ===")
    pca = PCA(n_components=2, random_state=42)
    X_cluster_pca = pca.fit_transform(X_cluster_scaled)
    
    pca_df = pd.DataFrame(data=X_cluster_pca, columns=['PCA1', 'PCA2'])
    pca_df['Cluster'] = cluster_labels.astype(str)
    
    plt.figure(figsize=(12, 8))
    sns.scatterplot(x='PCA1', y='PCA2', hue='Cluster', data=pca_df, palette='viridis', s=60, alpha=0.7)
    
    cluster_centers_pca = pca.transform(kmeans.cluster_centers_)
    sns.scatterplot(x=cluster_centers_pca[:, 0], y=cluster_centers_pca[:, 1], marker='X', s=250, color='red', label='Centers')
    
    plt.title('K-Means Clustering Visualization - PCA Reduced (Course Code)')
    plt.xlabel('Principal Component 1')
    plt.ylabel('Principal Component 2')
    plt.legend()
    plt.grid(True)
    plt.savefig('cluster_plot_pca.png')
    plt.close()
    print("PCA Cluster Plot saved successfully as 'cluster_plot_pca.png'.")
    
    print("\n=== STEP 6: CLUSTER INTERPRETATION (GROUP BY SUMMARY) ===")
    interpretation = df_cluster_orig.groupby('Cluster').agg(['mean', 'count'])
    print(interpretation)
    
    print("\n=== SUCCESS ===")
    print("The exact course code has executed successfully and generated your plots!")

if __name__ == "__main__":
    run_course_kmeans()
