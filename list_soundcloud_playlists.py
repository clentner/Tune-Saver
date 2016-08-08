from urllib.parse import parse_qs, urlencode, urlparse, urlsplit, urlunsplit
import soundcloud
import webbrowser

from services import soundcloud_playlist

class S(soundcloud_playlist.SoundcloudPlaylist):
    def __init__(self):
        self.client = self.get_authenticated_client('.soundcloud-cache-list')
        print("Authenticated to SoundCloud as %s" %
                self.client.get('/me').username)

sc = S()

playlists = sc.client.get('/users/{}/playlists'.format(sc.client.get('/me').id))
for playlist in playlists:
    print('{}: {}'.format(playlist.title, playlist.id))