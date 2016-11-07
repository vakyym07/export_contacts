import unittest
from unittest.mock import patch
import vk


class Test(unittest.TestCase):
    def setUp(self):
        self.vk_api = vk.VK()

    @patch.object(vk.VK, 'vk_oauth')
    @patch.object(vk.VK, 'get_response')
    def test_get_inf_friend_right_output(self, m_get_response, m_vk_oauth):
        response = {'response': {'items': [
            {'first_name': 'Artyom', 'last_name': 'Soldatenko',
             'occupation': {'name': 'Urfu'},
             'city': {'title': 'Ekaterinburg'},
             'country': {'title': 'Russia'}}]}}
        m_get_response.return_value = response, None
        m_vk_oauth.return_value = 'access_token', 'user_id', None
        res = self.vk_api.get_information_friends()

        flag = res[0][0].get('name') is not None and \
            res[0][0].get('picture') is not None and \
            res[0][0]['occupation'] == 'Urfu' and \
            res[0][0]['city'] == 'Ekaterinburg' and \
            res[0][0]['country'] == 'Russia'
        assert True, (flag and res[1] is False)

    @patch.object(vk.VK, 'vk_oauth')
    @patch.object(vk.VK, 'get_response')
    def test_error_get_response(self, m_get_response, m_vk_oauth):
        m_get_response.return_value = None, 'Connection error'
        m_vk_oauth.return_value = 'access_token', 'user_id', None

        res = self.vk_api.get_information_friends()
        assert res[0] is None and res[1] is not None

    @patch.object(vk.VK, 'vk_oauth')
    def test_bad_access_token(self, m_vk_oauth):
        m_vk_oauth.return_value = 'access_token', 'user_id', None
        res = self.vk_api.get_information_friends()
        assert res[0] is None and res[1] is not None

    @patch.object(vk.VK, 'vk_oauth')
    def test_external_error(self, m_vk_oauth):
        m_vk_oauth.return_value = 'access_token', 'user_id', None
        self.vk_api.error = 'External error'
        res = self.vk_api.get_information_friends()
        assert res[0] is None and res[1] is not None
