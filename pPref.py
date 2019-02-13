"""     _               _____                _ _
       | |        /\   / ____|              | (_)
  _ __ | |       /  \ | |     __ _ _   _  __| |_  ___
 | '_ \| |      / /\ \| |    / _` | | | |/ _` | |/ _ \
 | |_) | |____ / ____ \ |___| (_| | |_| | (_| | | (_) |
 | .__/|______/_/    \_\_____\__,_|\__,_|\__,_|_|\___/
 | |
 |_|

This file is part of pLAC-audio.

pLAC-audio is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

pLAC-audio is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with pLAC-audio.  If not, see <http://www.gnu.org/licenses/>

Copyright (c) 2019 Fabrice Zaoui

License GNU GPL v3

"""
from pSettings import ChangeStyle, ShowLogger
from PyQt5.QtWidgets import QMainWindow, QCheckBox, QPushButton, QRadioButton, QLabel, QHBoxLayout, QVBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5 import Qt
from PyQt5.QtCore import pyqtSlot

class Preference(QMainWindow):
    def __init__(self, parent):
        super(Preference, self).__init__(parent)
        # window
        self.setWindowTitle('Preferences')
        self.setWindowIcon(QIcon('./icon/beer.ico'))
        self.setWindowModality(Qt.Qt.WindowModal)
        self.setFixedSize(400, 400)
        # radio button (color themes)
        txttheme = QLabel('Color theme : ', self)
        txttheme.move(10, 10)
        self.b1 = QRadioButton("Default", self)
        self.b1.toggled.connect(lambda: self.btnstate(self.b1))
        self.b1.move(30, 40)
        self.b2 = QRadioButton("Dark", self)
        self.b2.toggled.connect(lambda: self.btnstate(self.b2))
        self.b2.move(130, 40)
        if self.parent().theme == 0:
            self.b1.setChecked(True)
            self.b2.setChecked(False)
        else:
            self.b2.setChecked(True)
            self.b1.setChecked(False)
        # checkbox (view logger)
        txtlog = QLabel('Logger : ', self)
        txtlog.move(10, 80)
        self.logger = QCheckBox('Display', self)
        self.logger.move(30, 110)
        # quit button
        self.btn_ok = QPushButton('OK', self)
        self.btn_ok.resize(150,50)
        self.btn_ok.move(125, 340)
        self.initUI()

    def initUI(self):
        # checkbox (display logger)
        if self.parent().grp_log.isVisible():
            self.logger.setCheckState(Qt.Qt.Checked)
        else:
            self.logger.setCheckState(Qt.Qt.Unchecked)
        self.logger.stateChanged.connect(self.changeLogger)
        # quit button
        self.btn_ok.clicked.connect(self.pref_exit)

    @pyqtSlot()
    def btnstate(self, b):
        if b.text() == 'Default':
            if b.isChecked() is True:
                theme = 0
            else:
                theme = 1
        if b.text() == "Dark":
            if b.isChecked() is True:
                theme = 1
            else:
                theme = 0
        ChangeStyle(self.parent(), theme)

    @pyqtSlot()
    def changeLogger(self):
        if self.logger.isChecked():
            ShowLogger(self.parent(), 1)
        else:
            ShowLogger(self.parent(), 0)

    def pref_exit(self):
        self.close()




