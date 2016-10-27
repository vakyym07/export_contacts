from http.server import HTTPServer
from webbrowser import open_new
from HTTPServerHandler import HTTPServerHandler
from browser import runBrowser


class TokenHandler:
    """
    Class used to handle oAuth
    """

    def __init__(self, client_id, client_secret, access_url, api, name_api):
        self._id = client_id
        self._secret = client_secret
        self._access_url = access_url
        self._api = api
        self.name_api = name_api

    def get_access_token(self):
        open_new(self._access_url)
        #runBrowser(self._access_url)
        httpServer = HTTPServer(('localhost', 8080),
                                lambda request, address, server: HTTPServerHandler(request, address, server, self._id,
                                                                                   self._secret, self._api,
                                                                                   self.name_api))
        # This function will block until it receives a request
        httpServer.handle_request()
        return httpServer.access_token
