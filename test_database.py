import unittest
from database import DataBase


class Test(unittest.TestCase):
    def setUp(self):
        self.db = DataBase()
        self.friends_data = \
            [{'name': 'Vasya', 'bdate': '01.03.1998', 'skype': 'blabla'},
             {'name': 'Bob', 'bdate': '03.06.1876',
              'country': 'USA', 'city': 'Boston'}]
        self.db.create(data=(self.friends_data, None))

    def test_set_new_user(self):
        user_data = {'name': 'Artyom', 'bdate':
                     '03.06.1997', 'country': 'Russia'}
        resp = self.db.set_new_user(user_data)
        assert 1, resp

    def test_get_user_inf(self):
        name = 'Vasya'
        name1 = 'Bob'
        data = self.db.get_user_inf(name)
        data1 = self.db.get_user_inf(name1)

        flag = data is not None and data1 is not None
        assert True, flag

    def test_get_list_users(self):
        list_test = self.db.get_list_users()
        list_ex = ['Bob', 'Vasya']
        self.assertListEqual(list_ex, list_test)

    def test_update_user_inf(self):
        up_data = {'instagram': 'qwer'}
        self.db.update_user_inf('Bob', up_data)
        inf_user = self.db.get_user_inf('Bob')
        assert True, inf_user.get('instagram') is not None
