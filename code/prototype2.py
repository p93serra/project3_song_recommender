import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import re
from datetime import date
import random
from os import listdir
from os.path import isfile, join
import random
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pickle
import webbrowser

def create_hot_songs_database(url):
    # Make request to the url
    response = requests.get(url)
    if response.status_code != 200:
        print("Not able to connect with URL!!! Code=" + str(response.status_code))
        return None

    # Create the soup
    soup = BeautifulSoup(response.content, "html.parser")

    # Extract desired information from the soup
    song_names_soup = soup.select("ol > li span.chart-element__information__song.text--truncate.color--primary")
    artist_names_soup = soup.select("ol > li span.chart-element__information__artist.text--truncate.color--secondary")
    song_names = [song_names_soup[x].get_text() for x in range(len(song_names_soup))]
    artist_names = [artist_names_soup[x].get_text() for x in range(len(artist_names_soup))]

    # Create the data frame with the hot songs
    hot_top100_dict = {"Song":song_names, "Artist":artist_names}
    hot_top100 = pd.DataFrame(hot_top100_dict)

    hot_top100["Main Artist"] = hot_top100["Artist"].str.split(" Featuring ")
    hot_top100["Main Artist"] = hot_top100["Main Artist"].apply(lambda x: str(x[0]))

    hot_top100["Featuring Artist"] = hot_top100["Artist"].str.split(" Featuring ")
    hot_top100["Featuring Artist"] = hot_top100["Featuring Artist"].apply(lambda x: str(x[1]) if len(x) > 1 else None)

    # Save the data frame in a CSV file
    fileName = "hot_top100_" + str(date.today()) + ".csv"
    hot_top100.to_csv("../data/" + fileName)

    return hot_top100

def check_song_dataframe(song, df_hot_songs):
    songs_array = df_hot_songs["Song"].values
    return song in songs_array

def ask_song():
    user_song = input("Which song do you like? ")

    song_capitalized = ""
    for word in user_song.split():
        song_capitalized += word.capitalize() + " "

    return song_capitalized[:-1]

def recommend_hot_song(song, df_hot_songs):
    hot_song = random.choice(df_hot_songs["Song"].values)
    if hot_song == song:
        recommend_hot_song(song, df_hot_songs)
    else:
        return hot_song

def get_all_info_song(user_input):
    results = sp.search(user_input, limit=1)
    name = results["tracks"]["items"][0]["name"]
    artists = ""
    for i in range(len(results["tracks"]["items"][0]["artists"])):
        artists += results["tracks"]["items"][0]["artists"][i]["name"]
    url = results["tracks"]["items"][0]["external_urls"]["spotify"]
    return name, artists[:-1], url

def recommend_spotify_song(song, df_spotify_songs):
    keys = ['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
            'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo',
            'type', 'id', 'uri', 'track_href', 'analysis_url', 'duration_ms',
            'time_signature']
    keys_ = ['danceability', 'energy', 'acousticness', 'instrumentalness', 'valence']

    name_user_song, artist_user_song, url_user_song = get_all_info_song(song)
    user_song_a_f = sp.audio_features(url_user_song)[0].values()
    list_user_song_a_f = list(user_song_a_f)
    df_user_song_a_f = pd.DataFrame(columns=keys)
    df_user_song_a_f.loc[0] = list_user_song_a_f
    df_user_song_a_f_ = df_user_song_a_f[keys_]

    a_f_scaler = pickle.load(open("audio_features_scaler.pkl", "rb"))
    df_user_song_a_f_scaled = a_f_scaler.transform(df_user_song_a_f_)

    a_f_kmeans = pickle.load(open("audio_features_kmeans.pkl", "rb"))
    cluster = int(a_f_kmeans.predict(df_user_song_a_f_scaled))

    song_matches = df_spotify_songs.loc[df_spotify_songs["cluster"] == cluster, ["name","artist_1","artist_2","uri"]]
    list_index = list(song_matches.index)
    rand_value = int(random.choice(list_index))
    song_match_name = song_matches.loc[rand_value]["name"]

    return song_matches.loc[rand_value]["uri"]

if __name__ == "__main__":
    url_hot = "https://www.billboard.com/charts/hot-100"
    url_2010 = "https://www.billboard.com/charts/decade-end/hot-100"

    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id="af9ddcc5c792418e989d0746d5f123ea",
        client_secret="042754efae2146c8adcd80bf6811c3f0"))

    user_song = ask_song()

    mypath = "../data/"
    files = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    fileName = "hot_top100_" + str(date.today()) + ".csv"

    if fileName not in files:
        df_hot_songs = create_hot_songs_database(url_hot)
    else:
        df_hot_songs = pd.read_csv(mypath + fileName)

    df_spotify_songs = pd.read_csv("../data/songs_all.csv")

    if check_song_dataframe(user_song, df_hot_songs):
        print("This song is hot this week!!!")
        print("We would recommend another song from Top100 Hot Songs this week")
        recommended_song = recommend_hot_song(user_song, df_hot_songs)
        recommended_artist = df_hot_songs.loc[df_hot_songs["Song"] == recommended_song, ["Artist"]]["Artist"].values[0]
        print("RECOMMENDED SONG:")
        print(recommended_song, "BY", recommended_artist)
        results = sp.search(recommended_song + " " + recommended_artist, limit=1)
        if len(results["tracks"]["items"]) == 0:
            print("Song not found in Spotify...")
        else:
            recommended_song_url = results["tracks"]["items"][0]["external_urls"]["spotify"]
            reproduce = input("Do you want to open it in Spotify? Yes[y] or No[n]")
            if reproduce == "y":
                webbrowser.open(recommended_song_url)
            elif reproduce == "n":
                print("URL:", recommended_song_url)
    else:
        print("We would recommend a similar song from our Database!!!")
        recommended_song_uri = recommend_spotify_song(user_song, df_spotify_songs)
        recommended_song_name = df_spotify_songs.loc[df_spotify_songs["uri"] == recommended_song_uri, ["name"]].values[0][0]
        recommended_song_artist = df_spotify_songs.loc[df_spotify_songs["uri"] == recommended_song_uri, ["artist_1"]].values[0][0]
        print("RECOMMENDED SONG:")
        print(recommended_song_name, "BY", recommended_song_artist)
        results = sp.search(recommended_song_name + " " + recommended_song_artist, limit=1)
        if len(results["tracks"]["items"]) == 0:
            print("Song not found in Spotify...")
        else:
            recommended_song_url = results["tracks"]["items"][0]["external_urls"]["spotify"]
            reproduce = input("Do you want to open it in Spotify? Yes[y] or No[n]")
            if reproduce == "y":
                webbrowser.open(recommended_song_url)
            elif reproduce == "n":
                print("URL:", recommended_song_url)
