import requests
import webbrowser

from services.service import Service
from servicetrack import ServiceTrack

correct_track_prompt = '''
Opened your browser to a track download link.
Was it the correct song? y/n '''

class FMA(Service):
    name = "Free Music Archive"

    def __init__(self, config):
        '''
        Instantiation. Currently, `config` is not used, but a 'save_directory'
        key in config may be used in the future if the Free Music Archive
        allows programmatic downloading (rather than via browser).
        '''
        self.config = config

    def search(self, track):
        '''
        Search the Free Music Archive for the track.
        @param track A pylast track object
        @return A list containing up to one ServiceTrack
        '''
        searchURL = 'https://freemusicarchive.org/api/trackSearch'
        q = track.artist.name + ' - ' + track.title
        params = {'q': q, 'limit': '1'}
        r = requests.get(searchURL, params=params)
        response = r.json()
        
        desc = response["aRows"][0]
        # Extract track ID from parenthetical at end of string
        id = desc[1 + desc.rfind('('):-1]
        
        # Kurt Vile's song Freeway is returned for all unsuccessful searches.
        if id == '10' and (track.artist.name != "Kurt Vile" or track.title != "Freeway"):
            return []
        
        st = ServiceTrack('Download "{}" with your browser'.format(q))
        st.id = id
        return [st]
        
    def save(self, servicetrack):
        '''
        @param servicetrack A ServiceTrack object, generated from search()
        @return (success, message)
        '''
        # Get track's webpage URL
        track_endpoint = 'https://freemusicarchive.org/api/get/tracks.json'
        params = {'track_id': servicetrack.id, 'limit': '1'}
        r = requests.get(track_endpoint, params=params)
        response = r.json()
        track_url = response["dataset"][0]["track_url"]

        # Scrape webpage for download link
        r = requests.get(track_url)
        html = r.text
        index = html.find('https://freemusicarchive.org/music/download/')
        index_end = html.find('"', index)
        download_link = html[index:index_end]

        # Then open a download prompt via the web browser.
        # Downloads via script are blocked (likely based on user-agent).
        webbrowser.open(download_link)
        return (True, 'Opened Free Music Archive download link.')
