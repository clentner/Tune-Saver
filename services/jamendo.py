import requests

from services.service import Service
from servicetrack import ServiceTrack

client_id = 'c8186964'

class Jamendo(Service):
    name = "Jamendo"

    def __init__(self, config):
        self.config = config

    def search(self, track):
        '''
        @param track A pylast track object
        @return A list containing up to one ServiceTrack
        '''
        endpoint = 'https://api.jamendo.com/v3.0/tracks/'
        params = {
            'format': 'json',
            'limit': '1',
            'client_id': client_id,
            'artist_name': track.artist.name,
            'name': track.title
        }
        r = requests.get(endpoint, params=params)
        response = r.json()
        if response['headers']['results_count'] < 1:
            # track not found
            return []
        st = ServiceTrack('Download "{} - {}" as mp3 directly to {}'.format(
            response['results'][0]['artist_name'],
            response['results'][0]['name'],
            self.config['save_directory']))
        st.info = response['results'][0]
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
        return (True, "Saved from Jamendo to {}".format(filepath))
