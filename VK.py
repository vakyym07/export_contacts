from urllib.error import URLError, HTTPError
from TokenHandler import TokenHandler
from urllib.request import urlopen
import json


REDIRECT_URI = 'http://localhost:8080/'


class VK:
    def __init__(self):
        self._id = '5457440'
        self._secret = 'r6JtGyRNOwdHxV3OQ6tK'
        self.access_url = 'https://oauth.vk.com/authorize?client_id=%s&' \
                          'display=page&redirect_uri=%s&' \
                          'scope=friends&response_type=code&v=5.52' % (self._id, REDIRECT_URI)
        self.api = 'https://oauth.vk.com/access_token?client_id=%s&' \
                   'client_secret=%s&' \
                   'redirect_uri=%s&' \
                   'code=' % (self._id, self._secret, REDIRECT_URI)
        self.name = 'vk'
        self.token_handler = TokenHandler(self._id, self._secret, self.access_url, self.api, self.name)

    def vk_oauth(self):
        return self.token_handler.get_access_token()

    def get_information_friends(self):
        access_token, user_id = self.vk_oauth()
        fields = 'bdate,photo_200,photo_50,contacts,status,occupation,city,country,connections'
        api_friend = 'https://api.vk.com/method/friends.get?' \
                     'user_id=%s&v=5.52&fields=%s&access_token=%s' % (user_id, fields, access_token)
        if access_token is not None:
            try:
                with urlopen(api_friend) as request:
                    response = request.read().decode('utf-8')
                response = json.loads(response)

                for friend in response['response']['items']:
                    if friend.get('occupation') is not None:
                        friend['occupation'] = friend['occupation']['name']
                    if friend.get('city') is not None:
                        friend['city'] = friend['city']['title']
                    if friend.get('country') is not None:
                        friend['country'] = friend['country']['title']
                    if friend.get('photo_200') is not None:
                        friend['picture'] = friend['photo_200']
                    elif friend.get('photo_50') is not None:
                        friend['picture'] = friend['photo_50']
                    friend['name'] = friend['first_name'] + ' ' + friend['last_name']

            except (URLError, HTTPError):
                return None
            return response['response']['items']
        else:
            return None
