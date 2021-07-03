import pandas as pd
import numpy as np
import plotly as py
import plotly.graph_objs as go
import plotly_express as px


def df_user_top_artists(data):
    """
    :param data: in json format
    :return pandas dataframe
    """

    name, popularity, image_url, external_url, followers, genres = [], [], [], [], [], []
    for artist in data['items']:
        name.append(artist['name'])
        popularity.append(artist['popularity'])
        try:
            image_url.append(artist['images'][1]['url'])
        except:
            try:
                image_url.append(artist['images'][0]['url'])
            except IndexError:
                image_url.append(np.nan)
        external_url.append(artist['external_urls']['spotify'])
        followers.append(artist['followers']['total'])
        genres.append(artist['genres'])
    
    user_top_artist_data = pd.DataFrame(columns=['name','followers','popularity','genres','image_url', 'external_url'])

    user_top_artist_data['name'] = name
    user_top_artist_data['followers'] = followers
    user_top_artist_data['popularity'] = popularity
    user_top_artist_data['genres'] = genres
    user_top_artist_data['image_url'] = image_url
    user_top_artist_data['external_url'] = external_url

    return user_top_artist_data

def df_user_top_tracks(data):
    """
    :param data: in json format
    :return: pandas DataFrame
    """
    artist_name, artist_external_url = [], []
    album_name, album_release_date, album_image_url = [], [], []
    album_external_url, album_total_tracks = [], []
    song_external_url, song_name, song_popularity = [], [], []
    song_preview_url, song_number_in_album = [], []

    for track in data['items']:
        artist_external_url.append(track['album']['artists'][0]['external_urls']['spotify'])
        artist_name.append(track['album']['artists'][0]['name'])
        album_external_url.append(track['album']['external_urls']['spotify'])
        try:
            album_image_url.append(track['album']['images'][1]['url'])
        except IndexError:
            try:
                album_image_url.append(track['album']['images'][0]['url'])
            except IndexError:
                album_name.append(np.nan)
        album_name.append(track['album']['name'])
        album_release_date.append(track['album']['release_date'])
        album_total_tracks.append(track['album']['total_tracks'])
        song_external_url.append(track['external_urls']['spotify'])
        song_name.append(track['name'])
        song_popularity.append(track['popularity'])
        song_preview_url.append(track['preview_url'])
        song_number_in_album.append(track['track_number'])

    user_top_track_data = pd.DataFrame(
        columns=['song_name', 'song_duration', 'song_popularity', 'song_number_in_album',
                 'song_external_url', 'song_preview_url', 'album_name', 'album_release_date',
                 'album_total_tracks', 'album_image_url', 'album_external_url', 'artist_name',
                 'artist_external_url'])
    user_top_track_data['song_name'] = song_name
    user_top_track_data['song_popularity'] = song_popularity
    user_top_track_data['song_number_in_album'] = song_number_in_album
    user_top_track_data['song_external_url'] = song_external_url
    user_top_track_data['song_preview_url'] = song_preview_url
    user_top_track_data['album_name'] = album_name
    user_top_track_data['album_release_date'] = album_release_date
    user_top_track_data['album_total_tracks'] = album_total_tracks
    user_top_track_data['album_image_url'] = album_image_url
    user_top_track_data['album_external_url'] = album_external_url
    user_top_track_data['artist_name'] = artist_name
    user_top_track_data['artist_external_url'] = artist_external_url
    return user_top_track_data
    

def top_genres(df):
    genres_top_count = {}
    for genre_list in df['genres']:
        for genre in genre_list:
            if genre not in genres_top_count:
                genres_top_count[genre] = 1
            else:
                genres_top_count[genre] += 1
    genres_top_count = pd.Series(genres_top_count).sort_values(ascending=False)
    return genres_top_count.head()


def create_sunburst_data_artist(df, top_genres):
    genres, artists, values = [], [], []
    for i, row in df.iterrows():
        for genre, value in zip(top_genres.index, top_genres.values):
            if genre in row['genres']:
                genres.append(genre)
                values.append(str(value))
                artists.append(row['name'])

    dataframe = pd.DataFrame()
    dataframe['artist'] = artists
    dataframe['genres'] = genres
    dataframe['values'] = values
    return dataframe

def plot_artist_sunburst(df, title):
    if not df.empty:
        fig = px.sunburst(df, path=['genres','artist'], values='values')
        fig.update_layout(margin=dict(t=10, l=0, r=0, b=0), title={'text': title,
                                                                   'x': 0.5, 'y': 0.92})
    else:
        fig = {
            'data': [],
            'layout': go.Layout(
                xaxis={'showticklabels': False, 'ticks': '', 'showgrid': False, 'zeroline': False},
                yaxis={'showticklabels': False, 'ticks': '', 'showgrid': False, 'zeroline': False}
            )
        }
    return fig
