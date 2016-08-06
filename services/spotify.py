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
        self._token_prompt()
        print('Authenticated to Spotify as ' +
              self.spotify.me()['display_name'])

    def _token_prompt(self):
        scope = 'playlist-modify-public'
        redirect_uri = "http://127.0.0.1/spotify"
        token = spotipy.util.prompt_for_user_token(
            self.config['username'],
            scope=scope,
            client_id=self.config['client_id'],
            client_secret=self.config['client_secret'],
            redirect_uri=redirect_uri
        )
        self.spotify = spotipy.Spotify(auth=token)
        self.spotify.trace = False

    def search(self, track):
        '''
        @param track A pylast track object
        @return A list containing up to one ServiceTrack
        '''
        self._token_prompt()
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
                self.config['username'],
                self.config['playlist_id'],
                [spotify_track["uri"]])
        # print(results) # contains the snapshot id
        return (True, "Saved to Spotify playlist")
