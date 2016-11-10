import unittest
from database import DataBase


class Test(unittest.TestCase):
    def setUp(self):
        self.db = DataBase()
        self.db._change_file_name('TestDatabase.db')
        self.friends_data = \
            [{'name': 'Vasya', 'bdate': '01.03.1998', 'skype': 'blabla'},
             {'name': 'Bob', 'bdate': '03.06.1876',
              'country': 'USA', 'city': 'Boston'}]
        self.db.create(data=(self.friends_data, None))

    def test_insert_user(self):
        user_data = {'name': 'Artyom', 'bdate':
                     '03.06.1997', 'country': 'Russia'}
        resp = self.db.insert_user(user_data)
        assert True, resp

    def test_get_user_inf(self):
        name = 'Vasya'
        name1 = 'Bob'
        data = self.db.get_user_inf(name)
        data1 = self.db.get_user_inf(name1)

        flag = data is not None and data1 is not None
        assert True, flag

    def test_update_user_inf(self):
        up_data = {'instagram': 'qwer'}
        self.db.update_user_inf('Bob', up_data)
        inf_user = self.db.get_user_inf('Bob')
        assert True, inf_user.get('instagram') is not None

    def test_delete_user(self):
        user = {'name': 'Artyom Soldatenko',
                'email': 'vakyym07@gmail.com', 'bdate': '3.6.1997'}
        self.db.insert_user(user)
        self.db.delete_user(user['name'])
        res = self.db.contains_user(user['name'])
        assert True, not res

    def test_is_same_user_bdate(self):
        old_user = {'name': 'Artyom Soldatenko',
                    'email': 'vakyym07@gmail.com', 'bdate': '03.06.1997'}
        user = {'name': 'Artyom Soldatenko',
                'email': 'vakyym07@gmail.com', 'bdate': '3.6.1997'}
        res = self.db.is_same_users(old_user, user)
        assert True, res

    def test_is_same_user_not_inf(self):
        old_user = {'name': 'Artyom Soldatenko', 'email': '', 'bdate': ''}
        user = {'name': 'Artyom Soldatenko',
                'email': 'vakyym07@gmail.com', 'bdate': '3.6.1997'}
        res = self.db.is_same_users(old_user, user)
        assert True, res

    def test_is_same_user_error(self):
        old_user = {'name': 'Artyom Soldatenko',
                    'email': '', 'bdate': '12.12.1998'}
        user = {'name': 'Artyom Soldatenko',
                'email': 'vakyym07@gmail.com', 'bdate': '3.6.1997'}
        res = self.db.is_same_users(old_user, user)
        assert True, not res

    def test_contains_user(self):
        user = {'name': 'Artyom Soldatenko'}
        self.db.insert_user(user)
        assert True, self.db.contains_user(user['name'])

    def test_merge_users(self):
        old_user = {'name': 'Artyom Soldatenko', 'email': '', 'bdate': ''}
        self.db.insert_user(old_user)
        user = {'name': 'Artyom Soldatenko',
                'email': 'vakyym07@gmail.com', 'bdate': '3.6.1997'}
        self.db.merge_user(old_user, user)
        res = self.db.contains_user('Artyom Soldatenko')
        new_user = self.db.get_user_inf('Artyom Soldatenko')
        res1 = new_user['email'] == 'vakyym07@gmail.com' and \
            new_user['bdate'] == '3.6.1997'
        assert True, res and res1


if __name__ == '__main__':
    unittest.main()
