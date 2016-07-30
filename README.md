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
Requires the google api client, pylast, soundcloud, and spotipy:

    pip install --upgrade google-api-python-client
    pip install --upgrade pylast
    pip install --upgrade soundcloud
	pip install --upgrade spotipy
    

API Keys
--------
For testing, you will need to obtain API keys from the links provided in
`config template.ini`. When this product is closer to a releasable form,
keys will be included.


Enabling/disabling services
---------------------------
Comment out the appropriate service from the `destinations` array in
`__init__.py` to disable it.


Todo
----

* Intelligent title matching
* Soundcloud purchase_url
* Multiple playlist targets
* Multiple tries with SoundCloud
* Scrape Last.fm for Buy link
* Proper OAuth2 via custom URI
* Investigate auth flows that don't involve client secrets.
* * Last.fm doesn't need one
* * YouTube api just expose the client secret
* * Spotify Implicit Grant flow
* * SoundCloud client side javascript flow?
* Playlist titles
* Refactor shared code
* Split search() out from every save() method