from urllib.request import urlopen
from urllib.error import URLError, HTTPError
import facebook
from TokenHandler import TokenHandler
import json

REDIRECT_URI = 'http://localhost:8080/'


class Facebook:
    def __init__(self):
        self._id = '201104140274628'
        self._secret = '279768ad7a089365bc496bc1d1d01a53'
        self.access_url = ('https://www.facebook.com/dialog/' +
                           'oauth?client_id=' + self._id + '&redirect_uri=' +
                           REDIRECT_URI + "&scope=user_birthday,user_friends,"
                                          "publish_actions,manage_pages,publish_pages,user_education_history")
        self.api = ('https://graph.facebook.com/v2.6/oauth/access_token?client_id=' + self._id +
                    '&redirect_uri=' + REDIRECT_URI + '&client_secret=' + self._secret + '&code=')
        self.name = 'facebook'
        self.token_handler = TokenHandler(self._id, self._secret, self.access_url, self.api, self.name)

    def fb_oauth(self):
        return self.token_handler.get_access_token()

    def get_api(self, access_token):
        return facebook.GraphAPI(access_token)

    def get_friends(self):
        access_token = self.fb_oauth()
        api_fb = 'https://graph.facebook.com/me?fields=friends{picture,name}&access_token=%s' % access_token
        if access_token is not None:
            try:
                with urlopen(api_fb) as request:
                    response = request.read().decode('utf-8')
                response = json.loads(response)
            except (URLError, HTTPError):
                return None
            for value in response['friends']['data']:
                value['picture'] = value['picture']['data']['url']
            return response['friends']['data']
        else:
            return None

    def post_on_wall(self, message):
        access_token = self.fb_oauth()
        api_post = 'https://graph.facebook.com/me/feed?message=%s&amp;access_token=%s' % (message, access_token)
        if access_token is not None:
            graph = self.get_api(access_token)
            try:
                graph.put_object("me", "feed", message=message)
            except (URLError, HTTPError):
                return None
        else:
            return None
