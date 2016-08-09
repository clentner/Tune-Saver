# Copyright 2014 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# CHANGES:
# Modified from the original oauth2client tools.py:
# Authenticate via Implicit Grant flow rather than Web Server flow.
# Removed command-line options.
# Removed logging.
# Removed Python 2 compatibility

"""Command-line tools for authenticating via OAuth 2.0

Do the OAuth 2.0 Implicit Grant dance for a command line application. Stores the
generated credentials in a common file that is used by other example apps in
the same directory.
"""

from six.moves import BaseHTTPServer
from six.moves import http_client
from six.moves import input
from six.moves import urllib

import oauth2client
from oauth2client import _helpers
from oauth2client import clientsecrets
from oauth2client import transport
from oauth2client import client


import collections
import copy
import datetime
import json
import logging
import os
import shutil
import socket
import sys
import tempfile



__author__ = 'jcgregorio@google.com (Joe Gregorio)'
__all__ = ['argparser', 'run_flow', 'message_if_missing']

_FAILED_START_MESSAGE = """
Failed to start a local webserver listening on either port 8080
or port 8090. Please check your firewall settings and locally
running programs that may be blocking or using those ports.

Falling back to manual mode and continuing with
authorization.
"""

_BROWSER_OPENED_MESSAGE = """
Your browser has been opened to visit:

    {address}
"""

_GO_TO_LINK_MESSAGE = """
Go to the following link in your browser:

    {address}
"""


class ClientRedirectServer(BaseHTTPServer.HTTPServer):
    """A server to handle OAuth 2.0 redirects back to localhost.

    Waits for a single request and parses the query parameters
    into query_params and then stops serving.
    """
    query_params = {}


class ClientRedirectHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """A handler for OAuth 2.0 redirects back to localhost.

    Waits for a single request and parses the query parameters
    into the servers query_params and then stops serving.
    """

    def do_GET(self):
        """Handle a GET request.

        Parses the query parameters and prints a message
        if the flow has completed. Note that we can't detect
        if an error occurred.
        """
        self.send_response(http_client.OK)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        query = self.path.split('?', 1)[-1]
        if query and query != self.path:
            # Second get request has the query parameters available to the server.
            query = dict(urllib.parse.parse_qsl(query))
            self.server.query_params = query
            self.wfile.write(
                b"<html><head><title>Authentication Status</title></head>")
            self.wfile.write(
                b"<body><p>The authentication flow has completed.</p>")
            self.wfile.write(b"</body></html>")
        else:
            # First get request has the query parameters in a hash fragment, inaccessible
            # to this code.
            # Serve JavaScript which will move the query parameters into the regular URL.
            self.wfile.write(
                b"""<html><head><script>var loc=window.location.href.replace(/#/, '?');
                window.location.href=loc.replace(/\?\?/, '?');</script></head><body>
                <noscript>Please remove the # in the URL. If there is no question mark (?)
                in the URL, put one where the # was. Then press enter to reload.</noscript></body>
                </html>""")
    def log_message(self, format, *args):
        """Do not log messages to stdout while running as cmd. line program."""

def run_flow(authorize_url, port=8080):
    """
    Args:
        authorize_url: URL to which the user will be directed
        ports: The port on which to listen

    Returns:
        The access token and the full params dictionary
    """    
    success = False
    try:
        httpd = ClientRedirectServer(('localhost', port),
                                     ClientRedirectHandler)
    except socket.error:
        pass
    else:
        success = True
    noauth_local_webserver = not success
    if not success:
        print(_FAILED_START_MESSAGE)

    if not noauth_local_webserver:
        import webbrowser
        webbrowser.open(authorize_url, new=1, autoraise=True)
        print(_BROWSER_OPENED_MESSAGE.format(address=authorize_url))
    else:
        print(_GO_TO_LINK_MESSAGE.format(address=authorize_url))

    access_token = None
    params = None
    if not noauth_local_webserver:
        httpd.handle_request()
        httpd.handle_request()
        params = httpd.query_params
        if 'error' in params:
            raise Exception('Authentication request was rejected.')
        if 'access_token' in params:
            access_token = params['access_token']
        else:
            raise Exception('Failed to find "access_token" in the query parameters '
                            'of the redirect.')
    else:
        access_token = input('Enter access_token: ').strip()

    return access_token, params
