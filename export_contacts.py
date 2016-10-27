from urllib.request import urlopen
from urllib.error import URLError, HTTPError
import re
import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPainter, QColor, QFont, QPixmap
from PyQt5.QtCore import Qt, QUrl
from database import DataBase


def download_img(url_image):
    name = re.findall('.*/(.+)', url_image)[0]
    name = name.split('?')[0]
    if name not in os.listdir():
        try:
            with urlopen(url_image) as page:
                logo = page.read()
        except (URLError, HTTPError):
            return None
        try:
            os.mkdir('UsersPhoto')
        except OSError:
            pass
        image = open('UsersPhoto\\' + name, 'wb')
        image.write(logo)
        image.close()
    return 'UsersPhoto\\' + name


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DataBase()
        self.widget = Contacts(self.db)
        self.initUI()

    def initUI(self):
        self.resize(400, 600)
        self.centre()
        self.setWindowTitle('export_contacts')
        self.setCentralWidget(self.widget)

        vkAction = QAction('&VK', self)
        vkAction.triggered.connect(lambda: self.widget.initUI())

        fbAction = QAction('&Facebook', self)
        fbAction.triggered.connect(lambda: self.widget.initUI())

        fbPost = QAction('&Post on Facebook', self)
        fbPost.triggered.connect(self.showDialog)

        exitAction = QAction('&Exit', self)
        exitAction.triggered.connect(qApp.quit)

        menubar = self.menuBar()
        export = menubar.addMenu('&Export from')

        ex = menubar.addMenu('&Exit')
        ex.addAction(exitAction)

        from_vk = export.addMenu('&VK')
        from_fb = export.addMenu('&Facebook')
        post_fb = export.addMenu('&Post on Facebook')

        from_vk.addAction(vkAction)
        from_fb.addAction(fbAction)
        post_fb.addAction(fbPost)
        self.show()
        if self.db.db_exists():
            self.widget.initUI()

    def centre(self):
        # прямоугольник, определяющий геометрию главного окна
        qr = self.frameGeometry()
        # разрешение экрана нашего монитора. И с этим разрешением, мы получаем центральную точку
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def showDialog(self):
        text, ok = QInputDialog.getText(self, 'Input Dialog', 'В связи с политикой компаниии Facebook\n'
                                                              'возможно получить доступ к списку друзей,\n'
                                                              'если они установят данное предложение.\n'
                                                              'Создать пост на вашей стене? Если да, введите\n'
                                                              'текс поста:')
        if ok:
            fb = Facebook()
            fb.post_on_wall(str(text) + '\n' + fb.access_url)


class Contacts(QWidget):
    def __init__(self, db):
        self.dic_wind = {}
        self.list_error_wind = []
        self.mygroupbox = QGroupBox('Contacts list')
        self.myform = QFormLayout()
        self.scroll = QScrollArea()
        self.db = db
        super().__init__()

    def initUI(self):
        sender = self.sender()
        if sender is not None:
            if sender.text() == '&VK':
                self.db.create(sender.text())
            if sender.text() == '&Facebook':
                self.db.create(sender.text())

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
        inf_friend = self.db.get_user_inf(friend)
        if inf_friend['picture'] != '':
            logo = inf_friend['picture']

        self.dic_wind[name] = Window(name, logo, inf_friend, self)
        button.clicked.connect(lambda: self.dic_wind[name].initUI())
        return button


class Window(QWidget):
    def __init__(self, name_wind, url_logo, inf_friend, parent_window):
        self.name_wind = name_wind
        self.url_logo = url_logo
        self.inf_friend = inf_friend
        self.titles = ['name:', 'bdate:', 'city:', 'country:', 'home_phone:', 'instagram:', 'skype:',
                       'email:', 'occupation:']
        self.qlabels = []
        self.edit_window = None
        self.parent_window = parent_window
        self.p_button = None
        super().__init__()

    def initUI(self):
        grid = QGridLayout()
        vbox_title = QVBoxLayout()
        vbox_inf = QVBoxLayout()
        self.p_button = self.sender()

        for title in self.titles:
            label = QLabel(title)
            vbox_title.addWidget(label)
            self.qlabels.append(label)
            vbox_inf.addWidget(QLabel(self.inf_friend[title[:len(title) - 1]]))

        grid.addLayout(vbox_title, 0, 1)
        grid.addLayout(vbox_inf, 0, 2)

        photo = download_img(self.url_logo)
        logo = QLabel(self)
        if photo is not None:
            pixmap = QPixmap(photo)
            logo.setPixmap(pixmap)
        grid.addWidget(logo, 0, 0)

        edit_button = QPushButton('Edit', self)
        edit_button.clicked.connect(self.edit_inf_dialog)
        grid.addWidget(edit_button, 1, 0)

        self.setLayout(grid)
        self.setGeometry(300, 300, 700, 300)
        self.setWindowTitle(self.name_wind)
        self.show()

    def edit_inf_dialog(self):
        self.edit_window = EditWindow(self.titles, self.name_wind, self, self.parent_window, self.p_button)
        self.edit_window.initUI()


class EditWindow(QWidget):
    def __init__(self, column, edit_user, parent_window, base_widget, base_button):
        super().__init__()
        self.column = column
        self.edits = {}
        self.dic_edit_label = {}
        self.edit_user = edit_user
        self.parent_window = parent_window
        self.base_widget = base_widget
        self.base_button = base_button

    def initUI(self):
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

        self.dic_edit_label = {x[0]: x[1] for x in zip(list_edits, list_labels)}

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
        self.create_new_parent_window(dic_change)
        self.parent_window.close()
        self.close()

    def create_new_parent_window(self, dic_change):
        self.base_widget.db.update_user_inf(self.edit_user, dic_change)
        self.base_widget.dic_wind.pop(self.edit_user)
        user_inf = self.base_widget.db.get_user_inf(self.edit_user)

        self.base_button.setText(user_inf['name'])
        up_window = Window(user_inf['name'], user_inf['picture'], user_inf, self.base_button)
        self.base_widget.dic_wind[user_inf['name']] = up_window
        self.base_button.clicked.connect(lambda: self.base_widget.dic_wind[user_inf['name']].initUI())


class ErrorWindow(QWidget):
    def __init__(self, text_error):
        self.error = text_error
        super().__init__()

    def initUI(self):
        self.setGeometry(300, 300, 500, 300)
        self.setWindowTitle('Error')
        self.show()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.drawText(event, qp)
        qp.end()

    def drawText(self, event, qp):
        qp.setPen(QColor(0, 0, 0))
        qp.setFont(QFont('Decorative', 14))
        qp.drawText(event.rect(), Qt.AlignCenter, self.error)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = MainWindow()
    sys.exit(app.exec_())

