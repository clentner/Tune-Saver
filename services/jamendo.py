import os
import requests
import shutil
import webbrowser

from services.service import Service

class Jamendo(Service):
    name = "Jamendo"

    def __init__(self, config):
        self.config = config

    def search(self, track):
        '''
        @param track A pylast track object
        @return The download URL, if the track can be found. None otherwise.
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
            return None
        return response['results'][0]['audiodownload']
        
    def save(self, track):
        '''
        @param track A pylast track object
        @return True iff saving was successful
        '''
        download_url = self.search(track)
        if not download_url:
            return (False, "Jamendo search returned no results")
        
        if 'save_directory' in self.config:
            # download the song directly to the specified location
            filename = '{} - {}.mp3'.format(track.artist.name, track.title)
            filepath = os.path.join(self.config['save_directory'], filename)
            r = requests.get(download_url, stream=True)
            if r.status_code == 200:
                with open(filepath, 'wb') as f:
                    r.raw.decode_content = True   # Uncompress gzipped content
                    shutil.copyfileobj(r.raw, f)  # Save to disk
                return (True, "Saved from Jamendo to {}".format(filepath))
            else:
                return (False, "Jamendo download URL returned status {}".format(r.status_code))
        else:
            # punt the problem to someone else: open a 'Save As' dialogue via
            # the browser.
            webbrowser.open(download_url)
            return (True, "Opened Jamendo download URL")
        
