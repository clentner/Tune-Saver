import soundcloud
import webbrowser
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlencode, urlparse, urlsplit, urlunsplit

from services.service import Service
from servicetrack import ServiceTrack

client_id = 'bf717ba60ed729e683d10bd636916b15'

class Soundcloud(Service):
    name = "SoundCloud"

    def search_first(self, track):
        '''
        Find the first soundcloud track matching the info in `track`.
        
        @param track A pylast track object
        @return A soundcloud track, or None if not found
        '''
        #TODO: return more than one track
        q = track.artist.name + ', ' + track.title
        # Seem to sometimes get limit-1 tracks in response.
        # For example, with q='golden coast'.
        # Compensate for now by setting a limit of 2
        tracks = self.client.get('/tracks', q=q, limit=2)
        if len(tracks) < 1:
            return None
        return tracks[0]