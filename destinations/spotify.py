import spotipy
import spotipy.util


class Spotify:
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

    def save(self, track):
        '''
        @param track A pylast track object
        @return True iff saving was successful
        '''
        self._token_prompt()
        q = 'artist:"' + track.artist.name + '" track:"' + track.title + '"'
        try:
            spotify_track = self.spotify.search(q, type='track', limit=1)["tracks"]["items"][0]["uri"]
            results = self.spotify.user_playlist_add_tracks(
                self.config['username'],
                self.config['playlist_id'],
                [spotify_track]
            )
            # print(results) # contains the snapshot id
            return True
        except IndexError:
            return False
