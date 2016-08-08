import os
import requests
import shutil
import soundcloud
import webbrowser

from services.service import Service
from servicetrack import ServiceTrack
from services import soundcloud_service

class SoundcloudDownload(soundcloud_service.Soundcloud):
    '''
    Looks for the "Free Download" option on SoundCloud tracks.
    
    Only uses public APIs and thus does not require an API secret or authentication.
    '''
    name = "SoundCloud Download"
    
    def __init__(self, config):
        self.client = soundcloud.Client(client_id = soundcloud_service.client_id)
        self.config = config
        
    def search(self, track):
        '''
        @param track A pylast track object
        @return A list containing ServiceTrack objects
        '''
        sc_track = self.search_first(track)
        if not sc_track or not sc_track.downloadable:
            return []

        st = ServiceTrack('Download "{}" to {}'.format(
            sc_track.title,
            self.config['save_directory']))
        st.track = sc_track
        st.artist = track.artist.name
        st.title = track.title
        return [st]
        
    def save(self, servicetrack):
        '''
        Download the track directly
        
        @param servicetrack A ServiceTrack object, generated from search()
        @return (success, message)
        '''
        sc_track = servicetrack.track
        download_url = sc_track.download_url + \
            '?client_id=' + soundcloud_service.client_id
        
        # download the song directly to the specified location
        # TODO: refactor this shared code
        filename = os.path.join(
            self.config['save_directory'],
            '{} - {}.mp3'.format(
                servicetrack.artist,
                servicetrack.title))
        r = requests.get(download_url, stream=True)
        if r.status_code == 200:
            with open(filename, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
            return (True, "Saved from SoundCloud to {}".format(filename))
        else:
            return (False, "SoundCloud download URL returned status {}".format(r.status_code))
