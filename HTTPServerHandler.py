from urllib.request import urlopen
import re
from http.server import BaseHTTPRequestHandler
import requests


class HTTPServerHandler(BaseHTTPRequestHandler):
    """
    HTTP Server callbacks to handle OAuth redirects
    """

    def __init__(self, request, address, server, client_id, client_secret, api, name_api):
        self._id = client_id
        self._secret = client_secret
        self._api = api
        self.name_api = name_api
        super().__init__(request, address, server)

    def get_access_token_from_url(self, url, name_api):
        if self.name_api == 'google':
            r = requests.post(url)
            token = r.content.decode('utf-8')
        else:
            token = str(urlopen(url).read(), 'utf-8')
        if 'access_token' in token:
            if self.name_api == 'google':
                return re.findall('.*?"access_token": "(.+?)".*', token)[0]
            regex = re.compile('.*?access_token.*?[=|:]"?(.+?)["|&]')
            if 'user_id' in token:
                return regex.findall(token)[0], re.split(':|}', token)[3]
            return regex.findall(token)[0]
        else:
            return None

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        if 'code' in self.path:
            if self.name_api == 'google':
                self.auth_code = self.path.split('=')[2]
            else:
                self.auth_code = self.path.split('=')[1]
            self.wfile.write(bytes('<html><h1>You may now close this window.' +
                                   '</h1></html>', 'utf-8'))
            self.server.access_token = self.get_access_token_from_url(self._api + self.auth_code, self.name_api)
