import configparser
import pylast

from destinations import fma
from destinations import soundcloud
from destinations import spotify
from destinations import jamendo


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


def save_track(track, destinations):
    '''
    Loop through each destination and attempt to save the given track.
    '''
    for destination in destinations:
        try:
            if destination.save(track):
                print('saved to ' + destination.name)
                return True
        except Exception as e:
            # This looks bad, but there's a real reason to just eat the exception.
            # For whatever reason, saving to one destination caused an error. This is not
            # cause for giving up on the other destinations.
            print(str(e))
        print('could not save to ' + destination.name)
    return False


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    # last.fm initialization
    last_fm = config['Last.fm']
    ln = pylast.get_lastfm_network(
        api_key=last_fm['api_key'],
        api_secret=last_fm['api_secret']
    )
    user = pylast.User(last_fm['username'], ln)

    # The order these appear in this list will determine the order of preference.
    # If saving to one destination succeeds, no others will be tried.
    destinations = [
        jamendo.Jamendo(config['Jamendo']),
        fma.FMA(config['Free Music Archive']),
        spotify.Spotify(config['Spotify']),
        soundcloud.Soundcloud(config['Soundcloud']),
    ]
    # Main input loop
    while True:
        input('\nPress enter to save song')
        # Fetch the song from the Last.fm api
        track = most_current_track(user)
        print(track.artist.name, " - ", track.title)

        success = save_track(track, destinations)
        if not success:
            print('Could not save to any destination.')

if __name__ == '__main__':
    main()
