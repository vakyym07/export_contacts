from urllib.request import urlopen
from urllib.error import URLError, HTTPError
import re
import sys
import os

from PyQt5.QtWidgets import QWidget, QMainWindow, \
    QAction, QFormLayout, QScrollArea, \
    QDesktopWidget, QGroupBox, QPushButton, QVBoxLayout, \
    QLabel, QGridLayout, QHBoxLayout, QLineEdit, QApplication, qApp, \
    QInputDialog
from PyQt5.QtGui import QPainter, QColor, QFont, QPixmap
from PyQt5.QtCore import Qt
from database import DataBase
from google import Google
from threading import Thread
from webbrowser import open_new


def download_img(url_image):
    name = re.findall('.*/(.+)', url_image)[0]
    name = name.split('?')[0]
    try:
        os.mkdir('UsersPhoto')
    except OSError:
        pass
    if name not in os.listdir(path='UsersPhoto\\'):
        try:
            with urlopen(url_image) as page:
                logo = page.read()
        except (URLError, HTTPError):
            return None
        image = open('UsersPhoto\\' + name, 'wb')
        image.write(logo)
        image.close()
    return 'UsersPhoto\\' + name


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DataBase()
        self.widget = Contacts(self.db)
        self.err_win = None
        self.init_ui()

    def init_ui(self):
        self.resize(400, 600)
        self.centre()
        self.setWindowTitle('export_contacts')
        self.setCentralWidget(self.widget)

        vk_action = QAction('&VK', self)
        vk_action.triggered.connect(self.widget.init_ui)

        fb_action = QAction('&Facebook', self)
        fb_action.triggered.connect(lambda: self.widget.init_ui())

        exit_action = QAction('&Exit', self)
        exit_action.triggered.connect(qApp.quit)

        th = Thread(target=self.widget.import_all_contacts)
        import_action = QAction('&Import all contacts', self)
        import_action.triggered.connect(lambda: th.start())

        search_action = QAction('&Find contact', self)
        search_action.triggered.connect(self.find_contact)

        menubar = self.menuBar()
        export = menubar.addMenu('&Export from')

        find_contact = menubar.addMenu('&Find Contact')
        find_contact.addAction(search_action)

        import_cont = menubar.addMenu('&Import all contacts')
        import_cont.addAction(import_action)

        ex = menubar.addMenu('&Exit')
        ex.addAction(exit_action)

        from_vk = export.addMenu('&VK')
        from_fb = export.addMenu('&Facebook')

        from_vk.addAction(vk_action)
        from_fb.addAction(fb_action)

        self.show()
        if self.db.db_exists():
            self.widget.init_ui()

    def find_contact(self):
        name, ok = QInputDialog.getText(self, 'Find contact',
                                        'Enter username')
        if ok:
            if self.widget.dic_wind.get(name) is not None:
                self.widget.dic_wind[name].init_ui()
            else:
                self.err_win = ErrorWindow(
                    'Contact ' + name + ' not found')
                self.err_win.init_ui()

    def centre(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


class Contacts(QWidget):
    def __init__(self, db):
        self.dic_wind = {}
        self.dic_button = {}
        self.list_error_wind = {}
        self.layout = None
        self.mygroupbox = QGroupBox('Contacts list')
        self.myform = QFormLayout()
        self.scroll = QScrollArea()
        self.db = db
        self.google_api = Google()
        super().__init__()

    def init_ui(self):
        sender = self.sender()
        error = None
        if sender is not None:
            if sender.text() == '&VK':
                error = self.db.create(api=sender.text())
            if sender.text() == '&Facebook':
                error = self.db.create(api=sender.text())
        if error is not None:
            self.list_error_wind[error] = ErrorWindow(error)
            self.list_error_wind[error].init_ui()
        else:
            for friend in self.db.get_list_users():
                button = self.create_button(friend)
                self.myform.addRow(button)

            self.mygroupbox.setLayout(self.myform)

            self.scroll.setWidget(self.mygroupbox)
            self.scroll.setWidgetResizable(True)
            self.scroll.setFixedHeight(600)
            self.layout = QVBoxLayout(self)
            self.layout.addWidget(self.scroll)

    def create_button(self, friend):
        name = friend
        button = QPushButton(name, self)
        self.dic_button[name] = button
        inf_friend = self.db.get_user_inf(friend)
        if inf_friend['picture'] != '':
            logo = inf_friend['picture']

        self.dic_wind[name] = Window(name, logo,
                                     inf_friend, self, self.google_api)
        button.clicked.connect(lambda: self.dic_wind[name].init_ui())
        return button

    def import_all_contacts(self):
        for contact in self.db.get_list_users():
            contact_data = self.db.get_user_inf(contact)
            self.google_api.create_contact(
                self.google_api.create_xml(contact_data))
        open_new('https://contacts.google.com')

    def redrawing(self):
        self.clear_window()
        self.init_ui()

    def clear_layout(self, layout):
        for i in range(layout.count()):
            if layout.itemAt(i) is not None:
                layout.itemAt(i).widget().setParent(None)

    def clear_window(self):
        for i in range(self.layout.count()):
            if self.layout.itemAt(i) is not None:
                if self.layout.itemAt(i).layout() is not None:
                    self.clear_layout(self.layout.itemAt(i).layout())
                    self.layout.itemAt(i).layout().setParent(None)
                if self.layout.itemAt(i).widget() is not None:
                    self.layout.itemAt(i).widget().setParent(None)


class Window(QWidget):
    def __init__(self, name_wind, url_logo, inf_friend,
                 parent_window, google_api):
        self.name_wind = name_wind
        self.url_logo = url_logo
        self.inf_friend = inf_friend
        self.titles = ['name:', 'bdate:', 'city:', 'country:',
                       'home_phone:', 'instagram:', 'skype:',
                       'email:', 'occupation:']
        self.edit_window = None
        self.parent_window = parent_window
        self.p_button = None
        self.grid = QGridLayout()
        self.google_api = google_api
        super().__init__()

    def init_ui(self):
        self.clear_window()
        self.p_button = self.sender()
        vbox_title = QVBoxLayout()
        vbox_inf = QVBoxLayout()
        for title in self.titles:
            label = QLabel(title)
            vbox_title.addWidget(label)
            vbox_inf.addWidget(QLabel(self.inf_friend[title[:len(title) - 1]]))

        self.grid.addLayout(vbox_title, 0, 1)
        self.grid.addLayout(vbox_inf, 0, 2)

        photo = download_img(self.url_logo)
        logo = QLabel(self)
        if photo is not None:
            pixmap = QPixmap(photo)
            logo.setPixmap(pixmap)
        self.grid.addWidget(logo, 0, 0)

        edit_button = QPushButton('Edit', self)
        edit_button.clicked.connect(self.edit_inf_dialog)
        self.grid.addWidget(edit_button, 1, 0)

        th = Thread(target=self.import_contact)
        import_button = QPushButton('Import in Google Contacts', self)
        import_button.clicked.connect(lambda: th.start())
        self.grid.addWidget(import_button, 2, 0)

        delete_button = QPushButton('Delete contact', self)
        delete_button.clicked.connect(self.delete_contact)
        self.grid.addWidget(delete_button, 3, 0)

        self.setLayout(self.grid)
        self.setGeometry(300, 300, 700, 300)
        self.setWindowTitle(self.name_wind)
        self.show()

    def delete_contact(self):
        self.close()
        self.parent_window.dic_wind[self.name_wind].setParent(None)
        self.parent_window.dic_wind.pop(self.name_wind)
        self.parent_window.dic_button[self.name_wind].setParent(None)
        self.parent_window.dic_button.pop(self.name_wind)
        self.parent_window.db.delete_user(self.name_wind)

    def import_contact(self):
        self.google_api.create_contact(
            self.google_api.create_xml(self.inf_friend))
        open_new('https://contacts.google.com')

    def change_data(self, w_name, inf_friend):
        self.name_wind = w_name
        self.inf_friend = inf_friend

    def clear_layout(self, layout):
        for i in range(layout.count()):
            if layout.itemAt(i) is not None:
                layout.itemAt(i).widget().setParent(None)

    def clear_window(self):
        for i in range(self.grid.count()):
            if self.grid.itemAt(i) is not None:
                if self.grid.itemAt(i).layout() is not None:
                    self.clear_layout(self.grid.itemAt(i).layout())
                    self.grid.itemAt(i).layout().setParent(None)
                if self.grid.itemAt(i).widget() is not None:
                    self.grid.itemAt(i).widget().setParent(None)

    def redrawing(self):
        self.clear_window()
        self.init_ui()

    def edit_inf_dialog(self):
        self.edit_window = EditWindow(self.titles, self.name_wind,
                                      self, self.parent_window, self.p_button)
        self.edit_window.init_ui()


class EditWindow(QWidget):
    def __init__(self, column, edit_user,
                 parent_window, base_widget, base_button):
        super().__init__()
        self.column = column
        self.edits = {}
        self.dic_edit_label = {}
        self.edit_user = edit_user
        self.parent_window = parent_window
        self.base_widget = base_widget
        self.base_button = base_button

    def init_ui(self):
        grid = QGridLayout()
        grid.setSpacing(10)
        hbox_button = QHBoxLayout()
        list_edits = []
        list_labels = []

        position_label = [(i, 0) for i in range(len(self.column))]
        position_edit = [(i, 1) for i in range(len(self.column))]

        for label, pos in zip(self.column, position_label):
            lb = QLabel(label)
            list_labels.append(lb)
            grid.addWidget(lb, *pos)

        for pos in position_edit:
            qle = QLineEdit(self)
            list_edits.append(qle)
            qle.textChanged[str].connect(self.on_changed)
            grid.addWidget(qle, *pos)

        self.dic_edit_label = \
            {x[0]: x[1] for x in zip(list_edits, list_labels)}

        ok_button = QPushButton('Ok', self)
        ok_button.clicked.connect(self.is_ok)
        cancel_button = QPushButton('Cancel', self)
        cancel_button.clicked.connect(self.close)

        hbox_button.addWidget(ok_button)
        hbox_button.addWidget(cancel_button)

        grid.addLayout(hbox_button, len(self.column) + 1, 0)

        self.setLayout(grid)

        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('Edit information')
        self.show()

    def on_changed(self, text):
        self.edits[self.sender()] = text

    def is_ok(self):
        dic_change = {}
        for edit in self.dic_edit_label:
            if self.edits.get(edit) is not None:
                name = self.dic_edit_label[edit].text()
                dic_change[name[:len(name) - 1]] = self.edits[edit]
        self.edits = {}
        self.dic_edit_label = {}
        self.parent_window.close()
        self.create_new_parent_window(dic_change)
        self.close()

    def create_new_parent_window(self, dic_change):
        self.base_widget.db.update_user_inf(self.edit_user, dic_change)
        if dic_change.get('name') is not None:
            user_inf = self.base_widget.db.get_user_inf(dic_change['name'])
        else:
            user_inf = self.base_widget.db.get_user_inf(self.edit_user)
        self.parent_window.change_data(user_inf['name'], user_inf)
        self.parent_window.redrawing()


class ErrorWindow(QWidget):
    def __init__(self, text_error):
        self.error = text_error
        super().__init__()

    def init_ui(self):
        self.setGeometry(300, 200, 300, 200)
        self.setWindowTitle('Error')
        self.show()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.drawText(event, qp)
        qp.end()

    def drawText(self, event, qp):
        qp.setPen(QColor(0, 0, 0))
        qp.setFont(QFont('Decorative', 10))
        qp.drawText(event.rect(), Qt.AlignCenter, self.error)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = MainWindow()
    sys.exit(app.exec_())
