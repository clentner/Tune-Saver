'''
To avoid difficulty with Unicode song titles, set your IO encoding:
    export PYTHONIOENCODING='UTF-8'
'''

import configparser
import queue
import threading
import pylast

from services import fma, soundcloud_playlist, spotify, jamendo, youtube
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
    # Services populate the queue
    servicetrack_queue = queue.Queue()
    threads = []
    for service in services:
        try:
            service_thread = threading.Thread(target=service.search, args=(track, servicetrack_queue))
            service_thread.start()
            threads.append(service_thread)
        except Exception as e:
            # This looks bad, but there's a real reason to just eat the exception.
            # For whatever reason, one service caused an error. This is not
            # cause for giving up on the other services.
            # TODO: Logging could be added here in the future.
            print(str(e))
            print('Could not search ' + service.name)
    
    for service_thread in threads:
        service_thread.join()
    
    # Print the list of track sources.
    # Consume all tracks from the queue.
    print('0. Cancel')
    i = 1
    track_prompts = {}
    while not servicetrack_queue.empty():
        servicetrack = servicetrack_queue.get()
        print('{}. {}: {}'.format(
            i,
            servicetrack.service.name,
            servicetrack.prompt))
        track_prompts[i] = servicetrack
        i += 1

    # Prompt the user for a selection. Repeat until success or the user cancels.
    success = False
    while not success:
        try:
            st_number = int(input('\nSelect an option number: '))
        except ValueError:
            print('Enter an integer')
            continue
        if st_number == 0:
            # User selected the cancel option
            print('Canceled.')
            return
        if st_number not in track_prompts:
            print('Not a valid option')
            continue
        
        # Save the track the user selected.
        try:
            servicetrack = track_prompts[st_number]
            success, message = servicetrack.service.save(servicetrack)
            print(message)
        except Exception as e:
            print(str(e))
    

def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    # last.fm initialization
    last_fm = config['Last.fm']
    last_fm_api_key = 'bbad67cabcce9598501d485b701698f1'
    if not last_fm['username']:
        print('Last.fm is required to use Tune Saver. Provide your Last.fm username in config.ini')
        quit()
    ln = pylast.get_lastfm_network(api_key=last_fm_api_key)
    user = pylast.User(last_fm['username'], ln)

    # The order these appear in this list will determine the order they appear
    # in the selection prompt.
    # List of (constructor, config) tuples
    service_constructors = [
        # Highest priority: The ability to download the track directly.
        # Try the services with better search capabilities first.
        (jamendo.Jamendo, config['Jamendo']),
        (fma.FMA, config['Free Music Archive']),
        (soundcloud_download.SoundcloudDownload, config['Soundcloud']),
        # Failing that, try to save to a streaming music service
        (spotify.Spotify, config['Spotify']),
        (soundcloud_playlist.SoundcloudPlaylist, config['Soundcloud']),
        # Last free resort: maybe it's available in video form
        (youtube.Youtube, config['YouTube']),
        # If the track cannot be obtained for free, look for a way to buy it.
        (last_fm_purchase.LastFmPurchase, config['Last.fm']),
    ]
    
    services = []
    for sc, config_section in service_constructors:
        if not all(value for _,value in config_section.items()):
            print('To use {}, fill out all of its fields in config.ini'.format(
                config_section.name))
            continue
        try:
            services.append(sc(config_section))
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
        print('\nNow Playing: {} - {}\n'.format(
            track.artist.name, track.title))

        save_track(track, services)

if __name__ == '__main__':
    main()
