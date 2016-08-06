Tune Saver
==========
Saves songs.

1. Play a song on any of the hundreds of sources supported by a Last.fm
scrobbler (Pandora, YouTube, Spotify, Windows Media Player, Vevo...)
2. Hit enter in the Tune Saver interface
3. Many music sources, streaming and download-based are
automatically searched for the song, including
Jamendo, the Free Music Archive, SoundCloud, Spotify, and YouTube.
4. When found, the song is downloaded or added to a playlist, depending
on the service.


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
* Multiple playlist targets
* Multiple tries with SoundCloud
* Abstract out shared OAuth flows
* Proper OAuth2 via custom URI
    - Use the client used for YouTube?
* Remove need for list_soundcloud_playlists tool
* Hotkey?