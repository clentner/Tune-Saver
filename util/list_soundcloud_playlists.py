from urllib.parse import parse_qs, urlencode, urlparse, urlsplit, urlunsplit
import soundcloud
import webbrowser

def set_query_parameter(url, param_name, param_value):
    """Given a URL, set or replace a query parameter and return the
    modified URL.

    >>> set_query_parameter('http://example.com?foo=bar&biz=baz', 'foo', 'stuff')
    'http://example.com?foo=stuff&biz=baz'
    
    http://stackoverflow.com/questions/4293460/how-to-add-custom-parameters-to-an-url-query-string-with-python
    """
    scheme, netloc, path, query_string, fragment = urlsplit(url)
    query_params = parse_qs(query_string)
    
    query_params[param_name] = [param_value]
    new_query_string = urlencode(query_params, doseq=True)
    
    return urlunsplit((scheme, netloc, path, new_query_string, fragment))

client = soundcloud.Client(
    client_id = 'bf717ba60ed729e683d10bd636916b15',
    redirect_uri='http://127.0.0.1/soundcloud'
)

auth_url = client.authorize_url()
auth_url = set_query_parameter(auth_url, 'response_type', 'code_and_token')
webbrowser.open(auth_url)
redirect_url = input('Enter the URL to which you were redirected: ')
# Extract the token from the URL
try:
    token = parse_qs(urlparse(redirect_url).fragment)['access_token'][0]
except KeyError:
    raise Exception('Authentication to SoundCloud failed. No access token found in URL.')
client.access_token = token

playlists = client.get('/users/{}/playlists'.format(client.get('/me').id))
for playlist in playlists:
    print('{}: {}'.format(playlist.title, playlist.id))