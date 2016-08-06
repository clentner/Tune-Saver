import os
import requests
import shutil
import webbrowser

from services.service import Service
from servicetrack import ServiceTrack

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
            'client_id': self.config['client_id'],
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
        # download the song directly to the specified location
        filename = '{} - {}.mp3'.format(
            servicetrack.info['artist_name'], 
            servicetrack.info['name'])
        filepath = os.path.join(self.config['save_directory'], filename)
        download_url = servicetrack.info['audiodownload']
        r = requests.get(download_url, stream=True)
        if r.status_code == 200:
            with open(filepath, 'wb') as f:
                r.raw.decode_content = True   # Uncompress gzipped content
                shutil.copyfileobj(r.raw, f)  # Save to disk
            return (True, "Saved from Jamendo to {}".format(filepath))
        else:
            return (False, "Jamendo download URL returned status {}".format(r.status_code))
