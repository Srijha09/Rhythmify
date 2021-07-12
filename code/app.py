#Flask imports
import os
import flask
from flask import Flask,Blueprint,request, url_for, session, redirect, render_template
import plotly as py
from plotly.subplots import make_subplots
import plotly.graph_objs as go
import plotly.express as px
import plotly.figure_factory as ff
import pandas as pd
import pickle
#script imports
from helper.spotifyclient import SpotifyClient
import helper.user_data as us
#spotify imports
import time
import config
import json
import requests


app = Flask(__name__)


app.secret_key = "rhythmify"
app.config['SESSION_COOKIE_NAME'] = "Rhythmify Cookie"
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
TOKEN_INFO = "token_info"
client_id = config.SPOTIFY_CLIENT_ID
client_secret = config.SPOTIFY_CLIENT_SECRET
app.config['all_sp_objects'] = {}

#-----------------------------------ERROR PAGE-------------------------------------
@app.errorhandler(404)
def error404(error):
    """
    handling 404 error 
    """
    return "Sorry! There's a bug. Try going back to homepage and reloading", 404


@app.errorhandler(500)
def error500(error):
    """
    handling 500 error
    """
    return "Sorry! There's a bug. Try going back to homepage and reloading", 500

#---------------------------------HOME PAGE-----------------------------------------
spotify_client = SpotifyClient(client_id, client_secret, port=5000)
@app.route("/", methods=['POST', 'GET'])
def login():
    """
    redirect to Spotify's log in page
    """
    auth_url = spotify_client.get_auth_url()
    return redirect(auth_url)


@app.route("/callback/q")
def callback():
    """
    set the session's authorization header
    """
    auth_token = request.args['code']
    spotify_client.get_authorization(auth_token)
    authorization_header = spotify_client.authorization_header
    session['authorization_header'] = authorization_header
    return redirect(url_for('home',_external=True))

@app.route("/home")
def home():
    return render_template('index.html')



#----------------------------------PLAYLIST GENERATOR PAGES------------------------------------
@app.route('/playstart')
def playstart():
    return render_template('playlist_start.html')

@app.route('/playlist_loading', methods=['GET','POST'])
def playlist_loading():
    if request.method=='GET':
        return render_template('playlist_loading.html')

@app.route("/select_tracks", methods=['GET', 'POST'])
def select_tracks():
    authorization_header = session['authorization_header']

    def extract_letters(string):
        return ''.join([letter for letter in string if not letter.isdigit()])

    if request.method == 'GET':
        # -------- Get user's name, id, and set session --------
        profile_data = spotify_client.get_user_profile_data(authorization_header)
        user_display_name, user_id = profile_data['display_name'], profile_data['id']
        session['user_id'], session['user_display_name'] = user_id, user_display_name

        # -------- Get user recently played tracks data --------
        playlist_data = spotify_client.get_user_playlist_data(authorization_header, user_id)

        return render_template('playlist_select_tracks.html',
                               user_display_name=user_display_name,
                               playlists_data=playlist_data,
                               func=extract_letters)

    return render_template('playlist_select_tracks.html')

@app.route("/your-playlist", methods=['GET', 'POST'])
def your_playlist():
    authorization_header = session['authorization_header']
    selected_tracks = request.form.get('selected_tracks').split(',')
    session['selected_tracks'] = selected_tracks
    if request.method == 'POST':
        params = {
            'seed_tracks': session['selected_tracks']
        }


        get_reccomended_url = f"https://api.spotify.com/v1/recommendations?limit={25}"
        response = requests.get(get_reccomended_url,
                                headers=authorization_header,
                                params=params).text
        tracks = list(json.loads(response)['tracks'])
        tracks_uri = [track['uri'] for track in tracks]
        session['tracks_uri'] = tracks_uri

        return render_template('playlist_result.html', data=tracks)

    return redirect(url_for('not_found'))

@app.route("/save-playlist", methods=['GET', 'POST'])
def save_playlist():
    authorization_header = session['authorization_header']
    user_id = session['user_id']

    playlist_name = request.form.get('playlist_name')
    playlist_data = json.dumps({
        "name": playlist_name,
        "description": "Spotify Recommended songs",
        "public": True
    })

    create_playlist_url = f"https://api.spotify.com/v1/users/{user_id}/playlists"

    response = requests.post(create_playlist_url,
                             headers=authorization_header,
                             data=playlist_data).text

    playlist_id = json.loads(response)['id']

    tracks_uri = session['tracks_uri']
    tracks_data = json.dumps({
        "uris": tracks_uri,
    })

    add_items_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    response = requests.post(add_items_url, headers=authorization_header, data=tracks_data).text

    return render_template('playlist_listen.html', playlist_id=playlist_id)


#--------------------------------RECOMMENDATIONS PAGES---------------------------------

@app.route('/recommendstart',methods=['GET', 'POST'])
def recommendstart():
    if request.method=='GET':
        return render_template('recommend_start.html')

@app.route('/recommend_artists', methods=['GET','POST'])
def recommend_artists():
    if request.method=='GET':
        return render_template('recommend_artists.html')

@app.route('/result_artists', methods=['GET','POST'])
def result_artists():
    results = pickle.load(open('code/notebooks/cos_sim_results', 'rb'))
    def recommend_artist(item_id, num):
        recs = results[item_id][:num]
        print(recs)
        preds = {}
        for pair in recs:
            preds[pair[1]] = pair[0]
        return preds
    
    artist = request.form.get('inputartist')
    res = list(recommend_artist(artist,10).keys())                                                                                                                                                                                                                                                                         
    return render_template('result_artists.html', res=res)
   
    
# For songs 
@app.route('/recommend_songs', methods=['GET','POST'])
def recommend_songs():
    if request.method=='GET':
        return render_template('recommend_songs.html')

@app.route('/result_songs', methods=['GET','POST'])
def result_songs():
    results1 = pickle.load(open('code/notebooks/cos_sim_results_songs', 'rb'))
    def recommend_songs(item_id, num):
        recs = results1[item_id][:num]   
        print(recs)
        preds = {}
        for pair in recs:
            preds[pair[1]] = pair[0]
        return preds
    songs = request.form.get('inputsong')
    results = list(recommend_songs(songs,10).keys()) 
    return render_template('result_songs.html', results=results)


#--------------------------------USER DASHBOARD PAGES----------------------------------
@app.route('/userstart', methods = ['GET', 'POST'])
def userstart():
    if request.method=='GET':
        return render_template('user_start.html')

@app.route('/usergenre', methods = ['GET', 'POST'])
def usergenre():

    authorization_header = session['authorization_header']

   
    user_top_artists_short_term = spotify_client.df_get_user_top_track_artists(authorization_header,"artists","short_term")
    user_top_artists_medium_term = spotify_client.df_get_user_top_track_artists(authorization_header,"artists","medium_term")
    user_top_artists_long_term = spotify_client.df_get_user_top_track_artists(authorization_header,"artists","long_term")

    top_genres_artist_short_term = us.top_genres(user_top_artists_short_term)
    top_genres_artist_medium_term = us.top_genres(user_top_artists_medium_term)
    top_genres_artist_long_term = us.top_genres(user_top_artists_long_term)

    top_genres_sunburst_data_short_artists = us.create_sunburst_data_artist(user_top_artists_short_term, top_genres_artist_short_term)
    top_genres_sunburst_data_medium_artists = us.create_sunburst_data_artist(user_top_artists_medium_term, top_genres_artist_medium_term)
    top_genres_sunburst_data_long_artists = us.create_sunburst_data_artist(user_top_artists_long_term, top_genres_artist_long_term)

    fig_1_1 = us.plot_artist_sunburst(top_genres_sunburst_data_short_artists, title='Last few months')
    fig_1_2 = us.plot_artist_sunburst(top_genres_sunburst_data_medium_artists,title = 'Last 6 months')
    fig_1_3 = us.plot_artist_sunburst(top_genres_sunburst_data_long_artists, title='All Time')


    graph1JSON = json.dumps(fig_1_1, cls=py.utils.PlotlyJSONEncoder)
    graph2JSON = json.dumps(fig_1_2, cls=py.utils.PlotlyJSONEncoder)
    graph3JSON = json.dumps(fig_1_3, cls=py.utils.PlotlyJSONEncoder)
    return render_template('user_top_genres.html', graph1JSON=graph1JSON,graph2JSON=graph2JSON,graph3JSON=graph3JSON)

   

@app.route('/usertoptracks')
def usertoptracks():
    authorization_header = session['authorization_header']

    user_top_tracks_medium_term = spotify_client.df_get_user_top_track_artists(authorization_header,"tracks","medium_term")

    user_top_tracks_medium_term = user_top_tracks_medium_term[['song_name','artist_name','album_name']]
    #user_top_all_tracks = pd.concat([user_top_tracks_short_term,user_top_tracks_medium_term,user_top_tracks_long_term], axis=1)
    fig = ff.create_table(user_top_tracks_medium_term)
    
    graph4JSON = json.dumps(fig, cls=py.utils.PlotlyJSONEncoder)


    return render_template('user_top_tracks.html', graph4JSON=graph4JSON)

@app.route('/usertopartists')
def usertopartists():
    authorization_header = session['authorization_header']

    
    user_top_artists_medium_term = spotify_client.df_get_user_top_track_artists(authorization_header,"artists","medium_term")
    user_top_artists_medium_term = user_top_artists_medium_term[['name','followers','popularity','genres']]
    fig = ff.create_table(user_top_artists_medium_term)
    graph6JSON = json.dumps(fig, cls=py.utils.PlotlyJSONEncoder)
    return render_template('user_top_artists.html', graph6JSON=graph6JSON)

@app.route('/viz')
def viz():
    authorization_header = session['authorization_header']

    
    user_top_tracks = spotify_client.df_get_user_top_track_artists(authorization_header,"tracks","long_term")

    fig = px.scatter(user_top_tracks, x='album_release_date', y="song_popularity",
                     size="song_duration", color="artist_name",
                     hover_name="song_name", size_max=50)
    fig.update_layout(yaxis=dict(gridcolor='#DFEAF4'),
                      xaxis=dict(gridcolor='#DFEAF4'), plot_bgcolor='white',
                      legend=dict(
                          xanchor='center',
                          yanchor='top',
                          y=-0.3,
                          x=0.5,
                          orientation='h')
                      )
    graph7JSON = json.dumps(fig, cls=py.utils.PlotlyJSONEncoder)
    return render_template('viz.html', graph7JSON=graph7JSON)





production = app.config.from_object('config.ProdConfig')

if __name__ == '__main__':
    if production:
        app.run()
    else:
        app.run(host='127.0.0.1', port=5000, debug=True)
        # app.run())
   
    
