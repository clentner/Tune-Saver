import soundcloud
import webbrowser

client = soundcloud.Client(
    client_id = input('client_id: '),
    client_secret = input('client_secret: '),
    redirect_uri='http://127.0.0.1/soundcloud'
)

webbrowser.open(client.authorize_url())
code = input('Soundcloud code: ')
client.exchange_token(code=code)

playlists = client.get('/users/{}/playlists'.format(client.get('/me').id))
for playlist in playlists:
    print('{}: {}'.format(playlist.title, playlist.id))