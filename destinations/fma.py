import requests
import webbrowser

from destinations.destination import Destination

correct_track_prompt = '''
Opened your browser to a track download link.
Was it the correct song? y/n '''

class FMA(Destination):
    name = "Free Music Archive"

    def __init__(self, config):
        self.config = config

    def search(self, track):
        '''
        Search the Free Music Archive for the track.
        @param track A pylast track object
        @return the track ID (str), or None if not found.
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
            return None        
        return id
        
    def save(self, track):
        '''
        @param track A pylast track object
        @return True iff saving was successful
        '''
        # Search for the track using the API
        q = track.artist.name + ' - ' + track.title
        id = self.search(track)
        if not id:
            return (False, "Free Music Archive search did not find {}".format(q))

        # Get track's webpage URL
        track_endpoint = 'https://freemusicarchive.org/api/get/tracks.json'
        params = {'track_id': id, 'limit': '1'}
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

        # Ask the user if the file was correct (FMA's search is pretty bad)
        if 'y' != input(correct_track_prompt):
            return (False, 'Free Music Archive search found incorrect track.')
        return (True, 'Opened Free Music Archive download link.')
