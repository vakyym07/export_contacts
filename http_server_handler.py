from urllib.request import urlopen
import re
from http.server import BaseHTTPRequestHandler
import requests


class HTTPServerHandler(BaseHTTPRequestHandler):
    """
    HTTP Server callbacks to handle OAuth redirects
    """

    def __init__(self, request, address,
                 server, client_id=None, client_secret=None,
                 api=None, name_api=None):
        self._id = client_id
        self._secret = client_secret
        self._api = api
        self.name_api = name_api
        self.error = None
        super().__init__(request, address, server)

    def get_access_token_from_url(self, url=None):
        if self.error is not None:
            return None, None, self.error
        if self.name_api == 'google':
            r = requests.post(url)
            token = r.content.decode('utf-8')
        else:
            token = str(urlopen(url).read(), 'utf-8')
        if 'access_token' in token:
            if self.name_api == 'google':
                return re.findall('.*?"access_token": "(.+?)".*', token)[0], None, None
            regex = re.compile('.*?access_token.*?[=|:]"?(.+?)["|&]')
            if 'user_id' in token:
                return regex.findall(token)[0], re.split(':|}', token)[3], None
            return regex.findall(token)[0], None, None
        else:
            return None, None, 'Fail authentication'

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        try:
            self.end_headers()
        except ConnectionResetError as con_err:
            self.error = con_err
        if 'code' in self.path:
            if self.name_api == 'google':
                self.auth_code = self.path.split('=')[2]
            else:
                self.auth_code = self.path.split('=')[1]
            try:
                self.wfile.write(bytes('<html><h1>You may now close this window.' +
                                       '</h1></html>', 'utf-8'))
            except ConnectionResetError:
                pass
            self.server.access_token = self.get_access_token_from_url(
                self._api + self.auth_code)
        else:
            self.error = 'Fail authentication'
