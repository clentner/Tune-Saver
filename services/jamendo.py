import requests

from services.service import Service
from servicetrack import ServiceTrack

client_id = 'c8186964'

class Jamendo(Service):
    name = "Jamendo"

    def __init__(self, config):
        '''
        @param config A configparser section.
            Requires a 'save_directory' key, with a valid directory path
            as its value.
        '''
        self.config = config

    def search(self, track):
        '''
        @param track A pylast track object
        @return A list containing up to one ServiceTrack
        '''
        # Use the Jamendo API to search for up to one track
        endpoint = 'https://api.jamendo.com/v3.0/tracks/'
        params = {
            'format': 'json',
            'limit': '1',
            'client_id': client_id,
            'artist_name': track.artist.name,
            'name': track.title
        }
        r = requests.get(endpoint, params=params)
        # If the request failed, abort here.
        r.raise_for_status()
        response = r.json()
        if response['headers']['results_count'] < 1:
            # Track not found. Return empty list.
            return []

        # The prompt will be passed to the UI.
        st = ServiceTrack('Download "{} - {}" as mp3 directly to {}'.format(
            response['results'][0]['artist_name'],
            response['results'][0]['name'],
            self.config['save_directory']))
        # Save the URL, artist name, and song name, for saving to a file.
        st.info = response['results'][0]  # Dictionary containing song information
        return [st]
        
    def save(self, servicetrack):
        '''
        @param servicetrack A ServiceTrack object, generated from search()
        @return (success, message)
        '''
        filepath = self.download(
            servicetrack.info['audiodownload'],
            servicetrack.info['artist_name'],
            servicetrack.info['name'],
            'mp3')
        # Would have raised exception on failure. Report success.
        return (True, "Saved from Jamendo to {}".format(filepath))
