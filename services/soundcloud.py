import soundcloud
import webbrowser
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlencode, urlparse, urlsplit, urlunsplit

from services.service import Service
from servicetrack import ServiceTrack

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


class Soundcloud(Service):
    name = "SoundCloud"

    def __init__(self, config, cache_path=None):
        self.config = config
        self.client = soundcloud.Client(
            client_id=config['client_id'],
            #client_secret=config['client_secret'],
            redirect_uri='http://127.0.0.1/soundcloud'
        )
        # check for cached access token
        if cache_path is not None:
            self.cache_path = cache_path
        else:
            self.cache_path = '.soundcloud-cache-' + config['playlist_id']
          
        self.client.access_token = self._get_cached_token()
        if not self.client.access_token:
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
            auth_url = self.client.authorize_url()
            auth_url = set_query_parameter(auth_url, 'response_type', 'code_and_token')
            webbrowser.open(auth_url)
            redirect_url = input('Enter the URL to which you were redirected: ')
            # Extract the token from the URL
            try:
                token = parse_qs(urlparse(redirect_url).fragment)['access_token'][0]
            except KeyError:
                raise Exception('Authentication to SoundCloud failed. No access token found in URL.')
            self.client.access_token = token
            self._save_cached_token(self.client.access_token)
        print("Authenticated to SoundCloud as %s" %
                self.client.get('/me').username)

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
            
    def search(self, track):
        '''
        @param track A pylast track object
        @return A list containing ServiceTrack objects
        '''
        # Can't save tracks to a playlist without being authenticated.
        if not hasattr(self.client, 'access_token') or not self.client.access_token:
            return []
        #TODO: return more than one track
        q = track.artist.name + ', ' + track.title
        # Seem to sometimes get limit-1 tracks in response.
        # For example, with q='golden coast'.
        # Compensate for now by setting a limit of 2
        tracks = self.client.get('/tracks', q=q, limit=2)
        if len(tracks) < 1:
            # Empty list returned
            return []
        sc_track = tracks[0]

        st = ServiceTrack('Save "{}" to playlist'.format(sc_track.title))
        st.track = sc_track
        return [st]

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
            return (True, 'Added track to SoundCloud playlist {}'.format(playlist_id))
        else:
            return (False, 'SoundCloud playlist returned status code {}'.format(r.status_code))
