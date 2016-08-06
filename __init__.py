'''
To avoid difficulty with Unicode song titles, set your IO encoding:
    export PYTHONIOENCODING='UTF-8'
'''

import configparser
import pylast

from services import fma, soundcloud, spotify, jamendo, youtube
from services import soundcloud_download, last_fm_purchase


def most_current_track(last_fm_user):
    '''
    Gets either the now playing track or the most recently played track.
    '''
    now_playing = last_fm_user.get_now_playing()
    if now_playing:
        return now_playing
    try:
        # now playing track is excluded from get_recent_tracks by pylast,
        # so in the event of unfortunate timing, we will need it to
        # initially fetch two tracks from the api in order to have a
        # nonempty list. Assume the API will never mark two tracks as
        # "now playing" in one response.
        return last_fm_user.get_recent_tracks(limit=2)[0].track
    except IndexError:
        # No tracks returned
        return None


def save_track(track, services):
    '''
    Loop through each service. Get a list of potential tracks. Display them
    to the user. Prompt the user for a selection. Save the selection.
    '''
    #TODO: more comments
    #TODO: refactor
    potential_tracks = []
    for service in services:
        try:
            servicetracks = service.search(track)
            for st in servicetracks:
                potential_tracks.append((service, st))
        except Exception as e:
            # This looks bad, but there's a real reason to just eat the exception.
            # For whatever reason, one service caused an error. This is not
            # cause for giving up on the other services.
            print(str(e))
            print('Could not search ' + service.name)
    
    print('0. Cancel')
    # TODO: use enumerate()
    i = 1
    for service, servicetrack in potential_tracks:
        print('{}. {}: {}'.format(
            i,
            service.name,
            servicetrack.prompt))
        i += 1
        
    try:
        st_number = int(input('\nSelect an option number: ')) - 1
    except ValueError:
        print('Not a number')
        return
    if st_number < 0:
        # User selected the cancel option
        return
    if st_number >= len(potential_tracks):
        print('Not a valid option')
        return
    
    # TODO: failover to another service on False success or exception
    try:
        service, servicetrack = potential_tracks[st_number]
        success, message = service.save(servicetrack)
        print(message)
    except Exception as e:
        print(str(e))
    

def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    # last.fm initialization
    last_fm = config['Last.fm']
    ln = pylast.get_lastfm_network(api_key=last_fm['api_key'])
    user = pylast.User(last_fm['username'], ln)

    # The order these appear in this list will determine the order they appear
    # in the selection prompt.
    services = [
        # Highest priority: The ability to download the track directly.
        # Try the services with better search capabilities first.
        jamendo.Jamendo(config['Jamendo']),
        fma.FMA(config['Free Music Archive']),
        soundcloud_download.SoundcloudDownload(config['Soundcloud']),
        # Failing that, try to save to a streaming music service
        spotify.Spotify(config['Spotify']),
        soundcloud.Soundcloud(config['Soundcloud']),
        # Last free resort: maybe it's available in video form
        youtube.Youtube(config['YouTube']),
        # If the track cannot be obtained for free, look for a way to buy it.
        last_fm_purchase.LastFmPurchase(config['Last.fm']),
    ]
    # Main input loop
    while True:
        input('\nPress enter to save song')
        # Fetch the song from the Last.fm api
        track = most_current_track(user)
        if not track:
            print('Could not get a track from Last.fm.')
            continue
        print(track.artist.name, " - ", track.title)

        save_track(track, services)

if __name__ == '__main__':
    main()
