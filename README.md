Tune Saver
==========
Finds a way to save the currently playing song, by searching streaming services, music archives, and online stores.

Here's how it works:

1. Play a song on any of the hundreds of sources supported by a Last.fm
scrobbler (Pandora, YouTube, Spotify, Windows Media Player, Vevo...)
2. Hit enter in the Tune Saver interface
3. Many music sources, streaming and download-based are
automatically searched for the song, including
Jamendo, the Free Music Archive, SoundCloud, Spotify, and YouTube.
4. Choose from the presented list of services.
5. The song will be downloaded or added to a playlist automatically.
For purchase websites, your web browser will be opened to the song.


Usage
-----
* Install the dependencies below.
* Clone the repository or download and unzip the [source](https://github.com/clentner/Tune-Saver/archive/master.zip).
* Fill out the fields in `config.ini`, for any services you wish to use. Any service with empty fields will be disabled.
    - Provide your Last.fm username
    - Provide the path to a directory in which mp3 downloads will be saved, for Jamendo and Soundcloud
    - Find playlist IDs for SoundCloud (use `util/list_soundcloud_playlists.py`), YouTube and Spotify (copy from the playlist URL)
* Launch Tune Saver with `python3 __init__.py`
* Login prompts will be displayed for some services
* Press enter to save a song.
* A list of services will be displayed. Enter the number of the desired service.
* The song is saved.


Dependencies
------------
Requires `beautifulsoup4`, `requests`, `google-api-python-client`, `pylast`, 
`soundcloud`, and `spotipy`, all of which are available through pip.


Todo
----
* Make a proper module by adding a new directory
* Refactor shared code, especially from SoundCloud
* Playlist titles
* Soundcloud purchase_url
* Proper OAuth2 via custom URI
    - Use the client used for YouTube?
* Abstract out shared OAuth flows
* Short demo video showing usage
* Multiple tries with SoundCloud
* Remove need for list_soundcloud_playlists tool
* Multiple playlist targets
* Hotkey?