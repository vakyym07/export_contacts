import os
import os.path as osp
import sqlite3
import collections

from facebook import Facebook
from vk import VK
from threading import Lock


def get_users_data(user_inf, column_example):
    user_list = []
    for column in column_example:
        if user_inf.get(column) is not None:
            user_list.append(user_inf[column])
        else:
            user_list.append('')
    return tuple(user_list)


def download_data(api):
    if api == '&VK':
        vkapi = VK()
        return vkapi.get_information_friends()
    if api == '&Facebook':
        fbapi = Facebook()
        return fbapi.get_friends()


class DataBase:
    def __init__(self):
        self.columns = ['name', 'bdate', 'city', 'country', 'home_phone',
                        'instagram', 'skype', 'email',
                        'occupation', 'picture']
        self.file_name = 'UsersDatabase.db'
        self.table_name = 'users_data'
        self.lock = Lock()

    def _change_file_name(self, name):
        self.file_name = name

    def create(self, data):
        conn = sqlite3.connect(self.file_name)
        cur = conn.cursor()

        try:
            cur.execute('''CREATE TABLE users_data
                            (name, bdate, city, country,
                            home_phone, instagram, skype,
                            email, occupation, picture)''')
        except sqlite3.OperationalError:
            pass

        if data[1] is not None:
            return data[1]
        list_inf = []
        for user_inf in data[0]:
            list_inf.append(get_users_data(user_inf, self.columns))

        cur.executemany('INSERT INTO users_data VALUES (?,?,?,?,?,?,?,?,?,?)',
                        list_inf)
        conn.commit()
        conn.close()

    def update_database(self, data):
        if data[1] is not None:
            return data[1]
        for user in data[0]:
            if user['name'] == 'Alex Stafeev':
                flag = True
            if self.contains_user(user['name']):
                old_user = self.get_user_inf(user['name'])
                if self.is_same_users(old_user, user):
                    self.merge_user(old_user, user)
            elif self.contains_user(user['name'].split(' ')[1] +
                                    ' ' + user['name'].split(' ')[0]):
                name = user['name'].split(' ')[1] + \
                       ' ' + user['name'].split(' ')[0]
                old_user = self.get_user_inf(name)
                if self.is_same_users(old_user, user):
                    self.merge_user(old_user, user)
            else:
                self.insert_user(user)

    def insert_user(self, dict_data):
        conn = sqlite3.connect(self.file_name)
        cur = conn.cursor()

        list_inf = get_users_data(dict_data, self.columns)
        cur.execute('INSERT INTO users_data VALUES (?,?,?,?,?,?,?,?,?,?)',
                    list_inf)
        res = self.contains_user(dict_data['name'])
        conn.commit()
        conn.close()
        return res

    def get_user_inf(self, user):
        with self.lock:
            conn = sqlite3.connect(self.file_name)
            cur = conn.cursor()
            cur.execute('SELECT * FROM users_data WHERE name=?', (user,))
            dic_inf = {x[0]: x[1] for x in zip(self.columns, cur.fetchone())}
            return dic_inf

    def get_list_users(self):
        with self.lock:
            conn = sqlite3.connect(self.file_name)
            cur = conn.cursor()
            try:
                list_users = [x[0] for x in cur.execute(
                    'SELECT name FROM users_data ORDER BY name')]
            except sqlite3.OperationalError:
                return []
            conn.close()
            return list_users

    def update_user_inf(self, user_name, dict_update):
        conn = sqlite3.connect(self.file_name)
        cur = conn.cursor()
        for key in dict_update:
            cur.execute('UPDATE users_data set ' +
                        key + '=?' + ' where name=?',
                        (dict_update[key], user_name))
        conn.commit()
        conn.close()

    def delete_user(self, user_name):
        conn = sqlite3.connect(self.file_name)
        cur = conn.cursor()
        cur.execute('DELETE FROM users_data WHERE name=?', (user_name,))
        conn.commit()
        conn.close()

    def merge_user(self, data_user1, data_user2):
        new_data = {}
        for title in data_user1.keys():
            if data_user2.get(title) is not None:
                if data_user2[title] != '':
                    new_data[title] = data_user2[title]
                else:
                    new_data[title] = data_user1[title]
            else:
                new_data[title] = data_user1[title]
        self.delete_user(data_user1['name'])
        self.insert_user(new_data)

    def contains_user(self, name):
        conn = sqlite3.connect(self.file_name)
        cur = conn.cursor()
        cur.execute('SELECT EXISTS'
                    '(SELECT * FROM users_data WHERE name=? LIMIT 1);',
                    (name,))
        res = cur.fetchone()
        if res[0] == 1:
            return True
        return False

    @staticmethod
    def is_same_users(data_user1, data_user2):
        is_bdate = False
        if data_user1['bdate'] != '' and data_user2.get('bdate') is not None:
            bdate1 = [int(e) for e in data_user1['bdate'].split('.')]
            bdate2 = [int(e) for e in data_user2['bdate'].split('.')]
            compare = lambda x, y: collections.Counter(x) == collections.Counter(y)
            if compare(bdate1, bdate2):
                is_bdate = True
        else:
            is_bdate = True

        is_email = False
        if data_user1['email'] != '' and data_user2.get('email') is not None:
            if data_user1['email'] == data_user2['email']:
                is_email = True
        else:
            is_email = True
        return is_bdate and is_email

    def db_exists(self):
        if not osp.isfile(self.file_name):
            return False
        if not os.stat(self.file_name).st_size:
            return False
        return True

    def _output(self):
        conn = sqlite3.connect(self.file_name)
        cur = conn.cursor()
        for row in cur.execute('SELECT * FROM users_data ORDER BY name'):
            print(row)
