from VK import VK
from Facebook import Facebook
import sqlite3
import os, os.path as osp


def get_users_data(user_inf, column_example):
    user_list = []
    for column in column_example:
        if user_inf.get(column) is not None:
            user_list.append(user_inf[column])
        else:
            user_list.append('')
    return tuple(user_list)


class DataBase:
    def __init__(self):
        self.vkapi = VK()
        self.fbapi = Facebook()
        self.columns = ['name', 'bdate', 'city', 'country', 'home_phone', 'instagram', 'skype', 'email',
                        'occupation', 'picture']
        self.file_name = 'UsersDatabase.db'
        self.table_name = 'users_data'

    def create(self, api):
        if self.db_exists():
            os.remove(self.file_name)

        conn = sqlite3.connect(self.file_name)
        cur = conn.cursor()

        try:
            cur.execute('''CREATE TABLE users_data
                            (name, bdate, city, country, home_phone, instagram, skype,
                            email, occupation, picture)''')
        except Exception:
            pass
        if api == '&VK':
            data = self.vkapi.get_information_friends()
        if api == '&Facebook':
            data = self.fbapi.get_friends()

        list_inf = []
        for user_inf in data:
            list_inf.append(get_users_data(user_inf, self.columns))

        cur.executemany('INSERT INTO users_data VALUES (?,?,?,?,?,?,?,?,?,?)', list_inf)

        conn.commit()
        conn.close()

    def set_new_user(self, dict_data):
        conn = sqlite3.connect(self.file_name)
        cur = conn.cursor()

        list_inf = get_users_data(dict_data, self.columns)
        cur.execute('INSERT INTO users_data VALUES (?,?,?,?,?,?,?,?,?,?)', list_inf)

        conn.commit()
        conn.close()

    def get_user_inf(self, user):
        conn = sqlite3.connect(self.file_name)
        cur = conn.cursor()
        cur.execute('SELECT * FROM users_data WHERE name=?', (user, ))
        dic_inf = {x[0]: x[1] for x in zip(self.columns, cur.fetchone())}
        return dic_inf

    def get_list_users(self):
        conn = sqlite3.connect(self.file_name)
        cur = conn.cursor()
        list_users = [x[0] for x in cur.execute('SELECT name FROM users_data ORDER BY name')]
        conn.close()
        return list_users

    def update_user_inf(self, user_name, dict_update):
        conn = sqlite3.connect(self.file_name)
        cur = conn.cursor()
        for key in dict_update:
            cur.execute('UPDATE users_data set ' + key + '=?' + ' where name=?', (dict_update[key], user_name))
        conn.commit()
        conn.close()

    def db_exists(self):
        if not osp.isfile(self.file_name):
            return False
        if not os.stat(self.file_name).st_size:
            return False
        return True
