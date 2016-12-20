import soundcloud
import webbrowser
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlencode, urlparse, urlsplit, urlunsplit

from services.service import Service
from servicetrack import ServiceTrack
from services import soundcloud_service
from oauth2implicit import run_flow

def set_query_parameter(url, param_name, param_value):
    """Given a URL, set or replace a query parameter and return the
    modified URL.

    >>> set_query_parameter('http://example.com?foo=bar&biz=baz', 'foo', 'stuff')
    'http://example.com?foo=stuff&biz=baz'
    
    http://stackoverflow.com/questions/4293460/how-to-add-custom-parameters-to-an-url-query-string-with-python
    """
    scheme, netloc, path, query_string, fragment = urlsplit(url)
    query_params = parse_qs(query_string)
    
    query_params[param_name] = [param_value]
    new_query_string = urlencode(query_params, doseq=True)
    
    return urlunsplit((scheme, netloc, path, new_query_string, fragment))


class SoundcloudPlaylist(soundcloud_service.Soundcloud):
    name = "SoundCloud Playlist"

    def __init__(self, config, cache_path=None):
        self.config = config
        self.client = self.get_authenticated_client(cache_path)
        print("Authenticated to SoundCloud as %s" %
                self.client.get('/me').username)
        self.playlist_title = self.client.get('/playlists/{}'.format(
            config['playlist_id'])
            ).title
        print('Using SoundCloud playlist "{}"'.format(self.playlist_title))
                
    def get_authenticated_client(self, cache_path=None):
        '''
        Do the heavy OAuth2 lifting and return an authenticated SoundCloud
        client instance.
        
        Raises Exception on failure.
        '''
        client = soundcloud.Client(
            client_id=soundcloud_service.client_id,
            redirect_uri='http://127.0.0.1:8080'
        )
        # check for cached access token
        if cache_path is not None:
            self.cache_path = cache_path
        else:
            self.cache_path = '.soundcloud-cache-' + self.config['playlist_id']
          
        client.access_token = self._get_cached_token()
        if not client.access_token:
            # Authenticate to SoundCloud, without needing to provide a client secret.
            # This is a bit of a patch job, because the SoundCloud python client
            # doesn't support this flow (it's normally used for clientside javascript).
            #
            # A few modifications are needed:
            #
            # 1. Use a response type of 'code_and_token' instead of just 'code'
            #    This means we do not need to exchange a code for a token,
            #    which is good, because the exchange requires a client secret.
            #
            # 2. Manually set the `client.access_token` field once the token
            #    has been obtained. This is normally done within a flow called
            #    internally by the client.
            auth_url = client.authorize_url()
            auth_url = set_query_parameter(auth_url, 'response_type', 'token')
            token, _ = run_flow(auth_url, 8080)
            client.access_token = token
            self._save_cached_token(client.access_token)
        return client

    def _get_cached_token(self):
        token = None
        try:
            with open(self.cache_path) as f:
                token = f.read()
        except IOError:
            pass  # Wind up returning None
        return token

    def _save_cached_token(self, token):
        try:
            with open(self.cache_path, 'w') as f:
                f.write(token)
        except IOError as e:
            # Being unable to cache the token isn't fatal.
            print(str(e))
            
    def search(self, track, queue):
        '''
        @param track A pylast track object
        @param queue Queue for results
        '''
        sc_track = self.search_first(track)
        if not sc_track:
            return []

        st = ServiceTrack(self, 'Save "{}" to playlist'.format(sc_track.title))
        st.track = sc_track
        queue.put(st)

    def save(self, servicetrack):
        '''
        Appends the track to the user's playlist
        
        @param servicetrack A ServiceTrack object, generated from search()
        @return (success, message)
        '''
        playlist_id = self.config['playlist_id']
        # Get the current playlist contents
        tracklist = self.client.get('/playlists/' + playlist_id).tracks
        # Add this song to the playlist
        tracklist.append(servicetrack.track.obj)
        # Shrink network load by removing unneccessary information,
        # and convert ids to strings for the API request
        t = [{'id': str(x["id"])} for x in tracklist]
        # Add the track by uploading the new list
        r = self.client.put(
            '/playlists/' + playlist_id,
            playlist={"tracks": t}
        )
        if r.status_code == 200:
            return (True, 'Added track to SoundCloud playlist "{}"'.format(self.playlist_title))
        else:
            return (False, 'SoundCloud playlist returned status code {}'.format(r.status_code))
