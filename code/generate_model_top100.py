import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import pickle
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
from datetime import date

if __name__ == "__main__":
    path = "/Users/pauserrabergeron/Private/Ironhack/Course/credentials/"
    f = open(path + "spotify_credentials.txt", "r")
    dict_credentials = json.loads(f.read()[:-1])

    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=dict_credentials["client_id"],
        client_secret=dict_credentials["client_secret"]))

    keys = ['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
            'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo',
            'type', 'id', 'uri', 'track_href', 'analysis_url', 'duration_ms',
            'time_signature']

    keys_ = ['danceability', 'energy', 'acousticness', 'instrumentalness', 'valence']

    songs_all = pd.read_csv("../data/hot_top100_" + str(date.today()) + ".csv")

    name_songs_top = []
    artist_songs_top = []
    uri_songs_top = []
    songs_audio_features = []
    j = 1
    for i in range(len(songs_all)):
        results = sp.search(songs_all.loc[i]["name"] + " " + songs_all.loc[i]["Main Artist"])
        if len(results["tracks"]["items"]) != 0:
            name_song = results["tracks"]["items"][0]["name"]
            artist_song = results["tracks"]["items"][0]["artists"][0]["name"]
            song_uri = results["tracks"]["items"][0]["uri"]
            name_songs_top.append(name_song)
            artist_songs_top.append(artist_song)
            uri_songs_top.append(song_uri)
            songs_audio_features.append(sp.audio_features(song_uri)[0].values())
            print("Processed:", str(j), "/", str(len(songs_all)))
            j += 1

    df_audio_features = pd.DataFrame(songs_audio_features)
    df_audio_features.columns = keys
    df_audio_features.drop(df_audio_features.columns[[11, 12, 14, 15, 17]], axis=1, inplace=True)

    song_dict = {"name":name_songs_top, "artist":artist_songs_top, "uri":uri_songs_top}
    song_features = pd.DataFrame(song_dict)

    songs_top_all = song_features.merge(df_audio_features, how='left', on='uri')

    audio_features = songs_top_all[keys_]

    a_f_scaler = StandardScaler()
    a_f_scaler.fit(audio_features)
    pickle.dump(a_f_scaler, open("audio_features_top_scaler.pkl", "wb"))

    audio_features_scaled = a_f_scaler.transform(audio_features)
    df_audio_features_scaled = pd.DataFrame(audio_features_scaled, columns=audio_features.columns)

    a_f_kmeans = KMeans(n_clusters=5, random_state=1234)
    a_f_kmeans.fit(audio_features_scaled)
    pickle.dump(a_f_kmeans, open("audio_features_top_kmeans.pkl", "wb"))

    clusters = a_f_kmeans.predict(audio_features_scaled)
    songs_top_all["cluster"] = clusters

    songs_top_all.to_csv("../data/songs_top_all_" + str(date.today()) + ".csv", index=False)
