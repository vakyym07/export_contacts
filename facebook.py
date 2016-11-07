from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from token_handler import TokenHandler
import json

REDIRECT_URI = 'http://localhost:8080/'


class Facebook:
    def __init__(self):
        self._id = '201104140274628'
        self._secret = '279768ad7a089365bc496bc1d1d01a53'
        self.access_url = \
            ('https://www.facebook.com/dialog/' +
             'oauth?client_id=' + self._id + '&redirect_uri=' +
             REDIRECT_URI + "&scope=user_birthday,user_friends,"
             "publish_actions,manage_pages,"
             "publish_pages,user_education_history")
        self.api = ('https://graph.facebook.com/'
                    'v2.6/oauth/access_token?client_id=' + self._id +
                    '&redirect_uri=' + REDIRECT_URI +
                    '&client_secret=' + self._secret + '&code=')
        self.name = 'facebook'
        self.token_handler = TokenHandler(self._id, self._secret,
                                          self.access_url, self.api, self.name)
        self.access_token = None
        self.user_id = None
        self.error = None

    def fb_oauth(self):
        return self.token_handler.get_access_token()

    def get_response(self, url):
        try:
            with urlopen(url) as request:
                response = request.read().decode('utf-8')
            response = json.loads(response)
            return response, None
        except (URLError, HTTPError) as err:
            return None, err

    def get_friends(self):
        self.access_token, self.user_id, self.error = \
            self.fb_oauth()
        api_fb = 'https://graph.facebook.com/me?' \
                 'fields=friends{picture,name}&access_token=%s' % \
                 self.access_token
        if self.error is not None:
            return None, self.error
        if self.access_token is not None:
            response = self.get_response(api_fb)
            if response[1] is None:
                response = self._change_data(response[0])
                return response['friends']['data'], None
            else:
                return None, response[1]
        else:
            return None, 'Authentication error'

    def _change_data(self, response):
        for value in response['friends']['data']:
            value['picture'] = value['picture']['data']['url']
        return response
