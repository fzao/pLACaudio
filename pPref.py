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
from PyQt5.QtWidgets import QMainWindow, QCheckBox, QPushButton, QComboBox
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
        # checkbox (dark theme)
        self.style = QComboBox(self)
        self.logger = QCheckBox('Display logger', self)
        # quit button
        self.btn_ok = QPushButton('OK', self)
        self.initUI()

    def initUI(self):
        # combo (color theme)
        self.style.move(25, 25)
        self.style.resize(100, 25)
        self.style.setToolTip('Change the theme color of pLACaudio')
        self.style.addItem('- Theme')
        self.style.addItems(['Default', 'Dark', 'Gray', 'Rustic', 'Sky', 'Sand', 'Flower', 'Beach'])
        self.style.currentIndexChanged['int'].connect(self.changeStyle)
        # checkbox (display logger)
        self.logger.move(25, 75)
        self.logger.resize(200, 50)
        self.logger.stateChanged.connect(self.changeLogger)
        # quit button
        self.btn_ok.clicked.connect(self.pref_exit)
        self.btn_ok.resize(150,50)
        self.btn_ok.move(125, 340)

    @pyqtSlot(int)
    def changeStyle(self, theme):
        ChangeStyle(self.parent(), theme)

    @pyqtSlot()
    def changeLogger(self):
        if self.logger.isChecked():
            ShowLogger(self.parent(), 1)
        else:
            ShowLogger(self.parent(), 0)

    def pref_exit(self):
        self.close()




