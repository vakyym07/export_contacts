import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import *


def runBrowser(url):
    app = QApplication(sys.argv)
    browser = QWebEngineView()
    browser.load(QUrl(url))
    browser.show()
    sys.exit(app.exec_())
