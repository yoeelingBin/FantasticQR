from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
import sys
import utils.work


class Loader:
    def __init__(self):
        self.ui = uic.loadUi("main_window.ui")
        utils.work.modify(self.ui)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # logo
    icon = QIcon('./img/logo.png')
    app.setWindowIcon(icon)

    # 显示窗口
    loader = Loader()
    loader.ui.show()
    sys.exit(app.exec_())
