import unittest
from unittest.mock import patch
import facebook as fb


class Test(unittest.TestCase):
    def setUp(self):
        self.fb_api = fb.Facebook()

    @patch.object(fb.Facebook, 'fb_oauth')
    @patch.object(fb.Facebook, 'get_response')
    def test_get_inf_friend_right_output(self, m_get_response, m_fb_oauth):
        response = {'friends': {'data': [
            {'name': 'Artyom Soldatenko',
             'picture': {'data': {'url': 'logo'}}}]}}
        m_get_response.return_value = response, None
        m_fb_oauth.return_value = 'access_token', 'user_id', None
        res = self.fb_api.get_friends()

        flag = res[0][0].get('name') is not None and \
            res[0][0].get('picture') is not None
        assert True, (flag and res[1] is False)

    @patch.object(fb.Facebook, 'fb_oauth')
    @patch.object(fb.Facebook, 'get_response')
    def test_error_get_response(self, m_get_response, m_fb_oauth):
        m_get_response.return_value = None, 'Connection error'
        m_fb_oauth.return_value = 'access_token', 'user_id', None

        res = self.fb_api.get_friends()
        assert res[0] is None and res[1] is not None

    @patch.object(fb.Facebook, 'fb_oauth')
    def test_external_error(self, m_fb_oauth):
        m_fb_oauth.return_value = 'access_token', 'user_id', None
        self.fb_api.error = 'External error'
        res = self.fb_api.get_friends()
        assert res[0] is None and res[1] is not None
