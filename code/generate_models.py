import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import pickle

if __name__ == "__main__":
    keys_ = ['danceability', 'energy', 'acousticness', 'instrumentalness', 'valence']

    songs_all = pd.read_csv("../data/songs_all.csv")
    audio_features = songs_all[keys_]

    a_f_scaler = StandardScaler()
    a_f_scaler.fit(audio_features)
    pickle.dump(a_f_scaler, open("audio_features_scaler.pkl", "wb"))

    audio_features_scaled = a_f_scaler.transform(audio_features)
    df_audio_features_scaled = pd.DataFrame(audio_features_scaled, columns=audio_features.columns)

    a_f_kmeans = KMeans(n_clusters=7, random_state=1234)
    a_f_kmeans.fit(audio_features_scaled)
    pickle.dump(a_f_kmeans, open("audio_features_kmeans.pkl", "wb"))

    clusters = a_f_kmeans.predict(audio_features_scaled)
    songs_all["cluster"] = clusters

    songs_all.to_csv("../data/songs_all.csv", index=False)
