import json
import pandas as pd
import datetime
import requests
from urllib.parse import quote
import helper.user_data as us

class SpotifyClient:
    # Spotify API URLS
    API_VERSION = "v1"
    SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
    SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
    SPOTIFY_API_BASE_URL = "https://api.spotify.com"
    SPOTIFY_API_URL = f"{SPOTIFY_API_BASE_URL}/{API_VERSION}"

    #Server-side parameters
    STATE = ""
    SHOW_DIALOG_bool = True
    SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()
    SCOPE = "playlist-modify-public playlist-modify-private playlist-read-private user-top-read"

    CLIENT_SIDE_URL = 'http://127.0.0.1'

    def __init__(self, client_id, client_secret, client_side_url=CLIENT_SIDE_URL, port=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.client_side_url = client_side_url
        self.port = port
        self._access_token = ''
        self.authorization_header = ''
        self.redirect_uri = f"{self.client_side_url}/callback/q" if port is None else f"{self.client_side_url}:{self.port}/callback/q"
    
    def get_auth_url(self):
        auth_query_parameters = {
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": self.SCOPE,
            "show_dialog": self.SHOW_DIALOG_str,
            "client_id": self.client_id
            #"state": STATE,
        }

        url_args = "&".join([f"{key}={quote(str(val))}" for key, val in auth_query_parameters.items()])
        return f"{self.SPOTIFY_AUTH_URL}/?{url_args}"
    
    def get_authorization(self, auth_token):
        """
        returning authorization data and setting the authorization_header
        :param auth_token:
        :return: dict
        """

        data = {
            "grant_type": "authorization_code",
            "code": str(auth_token),
            "redirect_uri": self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }
        post_request = requests.post(self.SPOTIFY_TOKEN_URL, data=data)

        response_data = json.loads(post_request.text)
        self._access_token = response_data["access_token"]
        self.authorization_header = {"Authorization": f"Bearer {self._access_token}"}

        return dict(
            access_token=response_data["access_token"],
            refresh_token=response_data["refresh_token"],
            token_type=response_data["token_type"],
            expires_in=response_data["expires_in"],
        )

    

    def get_user_profile_data(self, auth_header):
        """Getting user data 
        auth_header: the authentication header
        """
        user_profile_api_endpoint = f"{self.SPOTIFY_API_URL}/me"
        profile_data = requests.get(user_profile_api_endpoint, headers=auth_header).text
        return json.loads(profile_data)
    
    def get_user_playlist_data(self, auth_header, user_id):
        """
        :return: list of dictionaries with playlist information
        """
        playlist_api_endpoint = f"https://api.spotify.com/v1/users/{user_id}/playlists"
        playlists = json.loads(requests.get(playlist_api_endpoint, headers=auth_header).text)
        playlists = playlists['items']

        playlist_data = []
        try:
            for playlist in playlists:
                playlist_data.append({
                    'playlist_name': playlist['name'],
                    'playlist_url': playlist['external_urls']['spotify'],
                    'playlist_tracks_url': playlist['tracks']['href'],
                    'playlist_id': playlist['id'],
                    'playlist_tracks': self._get_playlist_tracks(auth_header, playlist['id'])
                })
            return playlist_data
        except:
            return "Internal Server Error"


    @staticmethod
    def _get_playlist_tracks(auth_header, playlist_id):
        """
        :return: list of dictionaries with track information
        """
        playlist_api_endpoint = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
        tracks = json.loads(requests.get(playlist_api_endpoint, headers=auth_header).text)['items']

        return [
            {
                'track_artist': track['track']['artists'][0]['name'],
                'track_name': track['track']['name'],
                'track_image': track['track']['album']['images'][0]['url'],
                'track_url': track['track']['external_urls']['spotify'],
                'track_id': track['track']['id']
            } for track in tracks
        ]

    # For User Dashboard

    def get_user_top_tracks_artists(self,auth_header,entity_type,limit,time_range, offset):
        """
        :param entity_type:  artists or tracks
        :param limit: The number of entities to return. Limit is 50
        :param time_range: Over what time frame the affinities are computed. Valid values: long_term
            (calculated from several years of data and including all new data as it becomes available),
            medium_term (approximately last 6 months), short_term (approximately last 4 weeks)
        :param offset: The index of the first entity to return. Default: 0 (i.e., the first track).
            Use with limit to get the next set of entities
        :return: json text
        """
        endpoint = f"https://api.spotify.com/v1/me/top/{entity_type}?time_range={time_range}&limit={limit}&offset={offset}"
        track_artists = json.loads(requests.get(endpoint, headers=auth_header).text)
        print(track_artists)
        return track_artists
    
    def df_get_user_top_track_artists(self,auth_header,entity_type,time_range):
        """
        :return a pandas DataFrame
        """
        total_top_entity = self.get_user_top_tracks_artists(auth_header,entity_type,1,time_range,0)["total"]
        print(total_top_entity)
        user_top_entity_data = pd.DataFrame()
        for i in range(int(total_top_entity/50)+1):
            temp_json = self.get_user_top_tracks_artists(auth_header,entity_type,50,time_range,i*50)
            if entity_type == "artists":
                temp = us.df_user_top_artists(temp_json)
            else:
                temp = us.df_user_top_tracks(temp_json)
            user_top_entity_data = pd.concat([user_top_entity_data, temp])
        return user_top_entity_data
    