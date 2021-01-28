import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import sys

def get_playlist_tracks(playlist_id):
    results = sp.user_playlist_tracks("spotify", playlist_id)
    total_songs = results["total"]
    items = results['items']
    i = 1
    while results['next']:
        results = sp.next(results)
        items.extend(results['items'])
        print("Processed songs: " + str(i*100) + "/" + str(total_songs))
        i += 1
    print("Finished!")
    name_songs = [i["track"]["name"] for i in items]
    artists_songs = []
    for i in items:
        artists_songs.append([i["track"]["artists"][j]["name"] for j in range(len(i["track"]["artists"]))])
    uri_songs = [i["track"]["uri"] for i in items]
    return name_songs, artists_songs, uri_songs

def get_audio_features_tracks(uri_songs_list):
    keys = ['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
            'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo',
            'type', 'id', 'uri', 'track_href', 'analysis_url', 'duration_ms',
            'time_signature']

    songs_audio_features = []

    i = 0

    for song_uri in uri_songs_list:
        songs_audio_features.append(sp.audio_features(song_uri)[0].values())

        if i % 100 == 0:
            print("Processed: " + str(i) + "/" + str(len(uri_songs_list)))

        i += 1

    print("Processed: " + str(i) + "/" + str(len(uri_songs_list)))

    df_audio_features = pd.DataFrame(songs_audio_features)

    df_audio_features.columns = keys

    df_audio_features.drop(df_audio_features.columns[[11, 12, 14, 15, 17]], axis=1, inplace=True)

    return df_audio_features

if __name__ == "__main__":
    path = "/Users/pauserrabergeron/Private/Ironhack/Course/credentials/"
    f = open(path + "spotify_credentials.txt", "r")
    dict_credentials = json.loads(f.read()[:-1])

    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=dict_credentials["client_id"],
        client_secret=dict_credentials["client_secret"]))

    url_10000_songs_playlist = "https://open.spotify.com/playlist/1hMzceeWw7QiI6vaBkcEJO"

    input_url_playlist = input("URL of the playlist to append:")

    if input_url_playlist[:34] != "https://open.spotify.com/playlist/":
        print("Wrong URL format!!!")
        sys.exit()

    name_songs, artists_songs, uri_songs = get_playlist_tracks(input_url_playlist)

    song_dataframe_dict = {"name": name_songs, "artist": artists_songs, "uri": uri_songs}

    song_dataframe = pd.DataFrame(song_dataframe_dict)

    song_dataframe.to_csv("../data/songs.csv", index=False)

    audio_features_dataframe = get_audio_features_tracks(uri_songs)

    audio_features_dataframe.to_csv("../data/audio_features.csv", index=False)

    df_new = song_dataframe.merge(audio_features_dataframe, how='left', on='uri')

    df_new["artist_1"] = df_new["artist"].apply(lambda x: str(x[0]))
    df_new["artist_2"] = df_new["artist"].apply(lambda x: str(x[1]) if len(x) > 1 else None)

    df_new = df_new[['name', 'artist_1', 'artist_2', 'uri', 'duration_ms', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']]

    df_previous = pd.read_csv("../data/songs_all.csv")

    print("Previous database len:", len(df_previous))

    df_all = pd.concat([df_previous,df_new]).drop_duplicates().reset_index(drop=True)

    print("New database len:", len(df_all))

    df_all.to_csv("../data/songs_all.csv", index=False)
