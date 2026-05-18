import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from scipy.cluster.hierarchy import linkage, dendrogram
uploaded = files.upload()  # champion_profile_dataset_final.csv yükle
filename = "champion_profile_dataset_final.csv"

df = pd.read_csv(filename)

# -----------------------------
# Feature engineering
# -----------------------------
df["formation_family"] = np.where(
    df["dominant_formation"].astype(str).str.startswith("4"),
    "Back Four",
    np.where(
        df["dominant_formation"].astype(str).str.startswith("3"),
        "Back Three",
        "Other"
    )
)

# ML features
X = df[["domestic_coach", "back_four_rate", "avg_age"]].copy()

# standardize
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# -----------------------------
# Find best k for KMeans
# -----------------------------
results = []
for k in range(2, 6):
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=20)
    labels = kmeans.fit_predict(X_scaled)
    sil = silhouette_score(X_scaled, labels)
    inertia = kmeans.inertia_
    results.append({"k": k, "silhouette_score": sil, "inertia": inertia})

k_results = pd.DataFrame(results)
print("KMeans model selection:")
display(k_results)

best_k = k_results.sort_values("silhouette_score", ascending=False).iloc[0]["k"]
best_k = int(best_k)
print("Selected k =", best_k)

# final KMeans
kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=20)
df["kmeans_cluster"] = kmeans.fit_predict(X_scaled)

# -----------------------------
# Hierarchical clustering
# -----------------------------
agg = AgglomerativeClustering(n_clusters=best_k)
df["hier_cluster"] = agg.fit_predict(X_scaled)

# -----------------------------
# PCA
# -----------------------------
pca = PCA(n_components=2, random_state=42)
X_pca = pca.fit_transform(X_scaled)

df["pca1"] = X_pca[:, 0]
df["pca2"] = X_pca[:, 1]

print("Explained variance ratio:", pca.explained_variance_ratio_)

# -----------------------------
# Cluster summaries
# -----------------------------
cluster_summary = (
    df.groupby("kmeans_cluster")
    .agg(
        count=("team", "count"),
        domestic_coach_rate=("domestic_coach", "mean"),
        mean_back_four_rate=("back_four_rate", "mean"),
        mean_avg_age=("avg_age", "mean")
    )
    .reset_index()
)

print("\nKMeans cluster summary:")
display(cluster_summary)

cluster_summary.to_csv("ml_cluster_summary.csv", index=False)
k_results.to_csv("ml_kmeans_model_selection.csv", index=False)

# -----------------------------
# PCA scatter
# -----------------------------
plt.figure(figsize=(7,5))
for c in sorted(df["kmeans_cluster"].unique()):
    subset = df[df["kmeans_cluster"] == c]
    plt.scatter(subset["pca1"], subset["pca2"], label=f"Cluster {c}")

for _, row in df.iterrows():
    plt.text(row["pca1"], row["pca2"], row["team"], fontsize=7)

plt.title("PCA Projection of Champion Teams")
plt.xlabel("PC1")
plt.ylabel("PC2")
plt.legend()
plt.tight_layout()
plt.savefig("ml_pca_clusters.png")
plt.show()

# -----------------------------
# Dendrogram
# -----------------------------
Z = linkage(X_scaled, method="ward")

plt.figure(figsize=(10,5))
dendrogram(Z, labels=df["team"].tolist(), leaf_rotation=90)
plt.title("Hierarchical Clustering Dendrogram")
plt.tight_layout()
plt.savefig("ml_dendrogram.png")
plt.show()

# -----------------------------
# Save full ML dataset
# -----------------------------
df.to_csv("champion_profile_dataset_with_ml.csv", index=False)

files.download("champion_profile_dataset_with_ml.csv")