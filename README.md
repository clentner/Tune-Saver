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
* Rename 'destinations' to 'services'. This makes more sense because you
save a song *to* a destination but download *from* a source. Might as well
call them services.
* Make a class for potential track.
    - Implementation data, e.g. URL or UID
    - Prompt text, e.g. 'Buy this track for $1.29' or 'Save this track to SoundCloud?'
    - Offers ability to yield multiple potential tracks from one service
* Intelligent title matching
* Soundcloud purchase_url
* Multiple playlist targets
* Multiple tries with SoundCloud
* Proper OAuth2 via custom URI
    - Use the client used for YouTube?
* Investigate auth flows that don't involve client secrets.
    - Last.fm doesn't need one
    - YouTube api just expose the client secret?
    - Spotify Implicit Grant flow
    - SoundCloud client side javascript flow?
* Playlist titles
* Refactor shared code
* Split search() out from every save() method