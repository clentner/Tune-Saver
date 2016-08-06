'''
To avoid difficulty with Unicode song titles, set your IO encoding:
    export PYTHONIOENCODING='UTF-8'
'''

import configparser
from functools import partial
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
    # Search every service for potential tracks to save
    potential_tracks = []  # list of (service, servicetrack) tuples
    for service in services:
        try:
            potential_tracks.extend((service, st) for st in service.search(track))
        except Exception as e:
            # This looks bad, but there's a real reason to just eat the exception.
            # For whatever reason, one service caused an error. This is not
            # cause for giving up on the other services.
            print(str(e))
            print('Could not search ' + service.name)
    
    # Print the list of track sources
    print('0. Cancel')
    i = 1
    for service, servicetrack in potential_tracks:
        print('{}. {}: {}'.format(
            i,
            service.name,
            servicetrack.prompt))
        i += 1

    # Prompt the user for a selection. Repeat until success or the user cancels.
    success = False
    while not success:
        try:
            st_number = int(input('\nSelect an option number: ')) - 1
        except ValueError:
            print('Enter an integer')
            continue
        if st_number >= len(potential_tracks):
            print('Not a valid option')
            continue
        if st_number < 0:
            # User selected the cancel option
            print('Canceled.')
            return
        
        # Save the track the user selected.
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
    service_constructors = [
        # Highest priority: The ability to download the track directly.
        # Try the services with better search capabilities first.
        partial(jamendo.Jamendo, config['Jamendo']),
        partial(fma.FMA, config['Free Music Archive']),
        partial(soundcloud_download.SoundcloudDownload, config['Soundcloud']),
        # Failing that, try to save to a streaming music service
        partial(spotify.Spotify, config['Spotify']),
        partial(soundcloud.Soundcloud, config['Soundcloud']),
        # Last free resort: maybe it's available in video form
        partial(youtube.Youtube, config['YouTube']),
        # If the track cannot be obtained for free, look for a way to buy it.
        partial(last_fm_purchase.LastFmPurchase, config['Last.fm']),
    ]
    
    services = []
    for sc in service_constructors:
        try:
            services.append(sc())
        except Exception as e:
            # This service could not be initialized. Print the reason,
            # but continue attempting to initialize other services.
            print(str(e))
    
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
