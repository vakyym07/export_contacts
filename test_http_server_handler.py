import unittest
from unittest.mock import patch
from http_server_handler import HTTPServerHandler
from token_handler import HTTPServer


class Test(unittest.TestCase):
    def setUp(self):
        self.http_server = HTTPServer(('localhost', 8080),
                                      lambda request, address, server:
                                      HTTPServerHandler
                                      (request, address, server))

    @patch('http_server_handler.HTTPServerHandler')
    def test_error_connection(self, m_instance):
        m_instance = m_instance.return_value
        m_instance.error = 'Connection Error'
        res = m_instance.get_access_token_from_url()
        assert res[0] is None and res[1] is None \
            and res[2] is not None

if __name__ == '__main__':
    unittest.main()