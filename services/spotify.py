from datetime import datetime, timedelta
from urllib.parse import parse_qs, urlencode, urlparse
import webbrowser

import spotipy
import spotipy.util

from services.service import Service
from servicetrack import ServiceTrack
from oauth2implicit import run_flow

client_id = 'e8df8c23cd3b48638da9a55041ee4641'
# Tokens from the Implicit Grant flow currently expire in one hour.
# If unable to get an expires_in value from the auth response, use this.
DEFAULT_EXPIRY = 3600

class Spotify(Service):
    name = "Spotify"

    def __init__(self, config):
        self.config = config
        # Call this initially to get the user a chance to sign in on their
        # first run of the program. It is also called on every save(), in case
        # the token has expired. Subsequent calls do not require
        # user interaction.
        if self._token_prompt():
            me = self.spotify.me()
            self.username = me['id']
            # Not all users will have a display name.
            print('Authenticated to Spotify as ' +
                str(me['display_name'] or me['id']))
            # Extract the playlist title
            self.playlist_title = self.spotify.user_playlist(
                self.username,
                config['playlist_id']
            )['name']
            print('Using Spotify playlist "{}"'.format(
                self.playlist_title))
        else:
            raise Exception('Could not authenticate to Spotify')

    def _token_prompt(self):
        '''
        Authenticate to Spotify using the Implicit Grant Flow.
        '''
        # Check to see if we already have an unexpired access token
        if hasattr(self, 'token_expiry_time') and datetime.now() < self.token_expiry_time:
            return True
        # Obtain a new access token.
        scope = 'playlist-modify-public playlist-modify-private'
        redirect_uri = "http://127.0.0.1:8080"
        # Step 1. Your application requests authorization
        endpoint = 'https://accounts.spotify.com/authorize?'
        params = dict(
            client_id=client_id,
            redirect_uri=redirect_uri,
            response_type='token',
            scope=scope)
        url = endpoint + urlencode(params)
        token, query_dict = run_flow(url)
        try:
            expires_in = query_dict['expires_in']
            self.token_expiry_time = datetime.now() + timedelta(0, int(expires_in))
        except (KeyError, TypeError):
            # It's possible the flow had to be completed manually, via input().
            # In this case, we will not have the expires_in value, but it's likely
            # going to be one hour.
            self.token_expiry_time = datetime.now() + timedelta(0, DEFAULT_EXPIRY)
        # Step 4. Use the access token to access the Spotify Web API
        self.spotify = spotipy.Spotify(auth=token)
        self.spotify.trace = False
        return True

    def search(self, track, queue):
        '''
        @param track A pylast track object
        @param queue Queue for results
        '''
        q = 'artist:"{}" track:"{}"'.format(
            track.artist.name,
            track.title)
        try:
            spotify_track = self.spotify.search(q, type='track', limit=1)["tracks"]["items"][0]
        except IndexError:
            return []
        
        st = ServiceTrack(self, 'Save "{}" to playlist'.format(spotify_track['name']))
        st.track = spotify_track
        queue.put(st)
        
    def save(self, servicetrack):
        '''
        Adds the track to the user's playlist
        
        @param servicetrack A ServiceTrack object, generated from search()
        @return (success, message)
        '''
        self._token_prompt()
        spotify_track = servicetrack.track
        # TODO: Will this raise an exception on failure?
        results = self.spotify.user_playlist_add_tracks(
                self.username,
                self.config['playlist_id'],
                [spotify_track["uri"]])
        # print(results) # contains the snapshot id
        return (True, 'Saved to Spotify playlist "{}"'.format(
            self.playlist_title))
