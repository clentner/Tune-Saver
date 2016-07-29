import requests
import webbrowser

class FMA:
    name = "Free Music Archive"
    
    def __init__(self, config):
        self.config = config
    
    def save(self, track):
        '''
        @param track A pylast track object
        @return True iff saving was successful
        '''
        # Search for the track using the API
        q = track.artist.name + ' - ' + track.title
        searchURL = 'https://freemusicarchive.org/api/trackSearch?q=' + q + '&limit=1'
        r = requests.get(searchURL)
        response = r.json()
        desc = response["aRows"][0]
        # Extract track ID from parenthetical at end of string
        id = desc[1 + desc.rfind('('):-1]
        
        # Kurt Vile's song Freeway is returned for all unsuccessful searches (?)
        if id == '10' and (track.artist.name != "Kurt Vile" or track.title != "Freeway"):
            return False
        
        # Get track's webpage URL
        r = requests.get('https://freemusicarchive.org/api/get/tracks.json?track_id=' + id + '&limit=1')
        response = r.json()
        track_url = response["dataset"][0]["track_url"]
        
        # Scrape webpage for download link
        r = requests.get(track_url)
        html = r.text
        index = html.find('https://freemusicarchive.org/music/download/')
        index_end = html.find('"', index)
        download_link = html[index:index_end]
        
        # Then open a download prompt via the web browser
        webbrowser.open(download_link)
        
        # Ask the user if the file was correct (FMA's search is pretty bad)
        return 'y' == input('Was that the correct song? y/n ')