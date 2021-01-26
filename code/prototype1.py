import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import re
from datetime import date
import random

url_hot = "https://www.billboard.com/charts/hot-100"
url_2010 = "https://www.billboard.com/charts/decade-end/hot-100"

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

if __name__ == "__main__":
    url_hot = "https://www.billboard.com/charts/hot-100"
    url_2010 = "https://www.billboard.com/charts/decade-end/hot-100"

    user_song = ask_song()

    df_hot_songs = create_hot_songs_database(url_hot)

    if check_song_dataframe(user_song, df_hot_songs):
        recommended_song = recommend_hot_song(user_song, df_hot_songs)
        recommended_artist = df_hot_songs.loc[df_hot_songs["Song"] == recommended_song, ["Artist"]]["Artist"].values[0]
        print("RECOMMENDED SONG")
        print(recommended_song, "BY", recommended_artist)
    else:
        print("For now I don't have any recommendation for you!!!")
        print("But stay tuned for Version 2")
