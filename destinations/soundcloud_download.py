import os
import requests
import shutil
import soundcloud
import webbrowser

from destinations.destination import Destination


class SoundcloudDownload(Destination):
    '''
    Looks for the "Free Download" option on SoundCloud tracks.
    
    Only uses public APIs and thus does not require an API secret or authentication.
    '''
    name = "SoundCloud downloadable tracks"
    
    def __init__(self, config):
        self.client = soundcloud.Client(client_id = config['client_id'])
        self.config = config
        
    def save(self, track):
        #TODO: refactor this shared code
        q = track.artist.name + ', ' + track.title
        tracks = self.client.get('/tracks', q=q, limit=2)
        if len(tracks) < 1:
            return (False, 'SoundCloud search found 0 tracks for {}'.format(q))
        sc_track = tracks[0]
        if 'y' != input('Is "{}" the correct track? y/n '.format(sc_track.title)):
            return (False, 'SoundCloud search found incorrect track for {}'.format(q))
        if not sc_track.downloadable:
            return (False, 'SoundCloud track not downloadable')
        download_url = sc_track.download_url + '?client_id=' + self.config['client_id']
        
        # download the song directly to the specified location
        # TODO: refactor this shared code
        filename = os.path.join(self.config['save_directory'],
                                '{} - {}.mp3'.format(track.artist.name, track.title))
        r = requests.get(download_url, stream=True)
        if r.status_code == 200:
            with open(filename, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
            return (True, "Saved from SoundCloud to {}".format(filename))
        else:
            return (False, "SoundCloud download URL returned status {}".format(r.status_code))
