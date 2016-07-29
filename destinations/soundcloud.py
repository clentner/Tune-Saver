import soundcloud
import webbrowser
from urllib.error import HTTPError


class Soundcloud:
    name = "SoundCloud"

    def __init__(self, config, cache_path=None):
        self.config = config
        self.client = soundcloud.Client(
            client_id=config['client_id'],
            client_secret=config['client_secret'],
            redirect_uri='http://127.0.0.1/soundcloud'
        )
        # check for cached access token
        if cache_path is not None:
            self.cache_path = cache_path
        else:
            self.cache_path = '.soundcloud-cache-' + config['playlist_id']
        self.client.access_token = self._get_cached_token()
        if not self.client.access_token:
            webbrowser.open(self.client.authorize_url())
            code = input('Soundcloud code: ')
            response = self.client.exchange_token(code=code)
            self._save_cached_token(self.client.access_token)
        print("Authenticated to SoundCloud as %s" %
                self.client.get('/me').username)

    def _get_cached_token(self):
        token = None
        try:
            with open(self.cache_path) as f:
                token = f.read()
        except IOError:
            pass
        return token

    def _save_cached_token(self, token):
        try:
            with open(self.cache_path, 'w') as f:
                f.write(token)
        except IOError:
            pass

    def save(self, track):
        try:
            return self._save(track)
        except HTTPError as e:
            print(str(e))
            return False

    def _save(self, track):
        '''
        @param track A pylast track object
        @return True iff saving was successful
        '''
        q = track.artist.name + ', ' + track.title
        # Seem to sometimes get limit-1 tracks in response.
        # For example, with q='golden coast'.
        # Compensate for now by setting a limit of 2
        tracks = self.client.get('/tracks', q=q, limit=2)
        if len(tracks) < 1:
            # Empty list returned
            return False
        track = tracks[0]

        if 'y' != input('Is "{}" the correct track? y/n '.format(track.title)):
            return False

        playlist_id = self.config['playlist_id']
        tracklist = self.client.get('/playlists/' + playlist_id).tracks
        tracklist.append(track.obj)
        # Shrink network load by removing unneccessary information, and convert
        # ids to strings
        t = [{'id': str(x["id"])} for x in tracklist]
        # Add the track
        r = self.client.put(
            '/playlists/' + playlist_id,
            playlist={"tracks": t}
        )
        return r.status_code == 200
