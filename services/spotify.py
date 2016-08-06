from datetime import datetime, timedelta
from urllib.parse import parse_qs, urlencode, urlparse
import webbrowser

import spotipy
import spotipy.util

from services.service import Service
from servicetrack import ServiceTrack

class Spotify(Service):
    name = "Spotify"

    def __init__(self, config):
        self.config = config
        # Call this initially to get the user a chance to sign in on their
        # first run of the program. It is also called on every save(), as
        # a lazy method of refreshing. Subsequent calls do not require
        # user interaction.
        if self._token_prompt():
            me = self.spotify.me()
            self.username = me['id']
            print('Authenticated to Spotify as ' +
                me['display_name'])
        else:
            print('Could not authenticate to Spotify')

    def _token_prompt(self):
        '''
        Authenticate to Spotify using the Implicit Grant Flow.
        '''
        # Check to see if we already have an unexpired access token
        if hasattr(self, 'token_expiry_time') and datetime.now() < self.token_expiry_time:
            return True
        # Obtain a new access token.
        scope = 'playlist-modify-public'
        redirect_uri = "http://127.0.0.1/spotify"
        # Step 1. Your application requests authorization
        endpoint = 'https://accounts.spotify.com/authorize?'
        params = dict(
            client_id=self.config['client_id'],
            redirect_uri=redirect_uri,
            response_type='token')
        url = endpoint + urlencode(params)
        webbrowser.open(url)
        # Step 2. The user is asked to authorize access within the scopes
        # Step 3. The user is redirected back to your specified URI
        redirect_url = input('Enter the URL to which you were redirected: ')
        try:
            query_dict = parse_qs(urlparse(redirect_url).fragment)
            expires_in = query_dict['expires_in'][0]
            self.token_expiry_time = datetime.now() + timedelta(0, int(expires_in))
            token = query_dict['access_token'][0]
        except KeyError:
            print('Authentication to Spotify failed. No access token found in URL.')
            return False
        except ValueError:
            print('Invalid expires_in value')
            return False
        # Step 4. Use the access token to access the Spotify Web API
        self.spotify = spotipy.Spotify(auth=token)
        self.spotify.trace = False
        return True

    def search(self, track):
        '''
        @param track A pylast track object
        @return A list containing up to one ServiceTrack
        '''
        q = 'artist:"{}" track:"{}"'.format(
            track.artist.name,
            track.title)
        try:
            spotify_track = self.spotify.search(q, type='track', limit=1)["tracks"]["items"][0]
        except IndexError:
            return []
        
        st = ServiceTrack('Save "{}" to playlist'.format(spotify_track['name']))
        st.track = spotify_track
        return [st]
        
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
        return (True, "Saved to Spotify playlist")
