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
from PyQt5.QtWidgets import QMainWindow, QCheckBox, QWidget
from PyQt5.QtGui import QIcon
from PyQt5 import Qt


class Preference(QMainWindow):
    def __init__(self, parent):
        super(Preference, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Preferences')
        self.setWindowIcon(QIcon('./icon/beer.ico'))
        self.setWindowModality(Qt.Qt.WindowModal)
        self.setFixedSize(400, 400)
        self.style = QCheckBox('Dark theme', self)
        self.style.move(25, 25)
        self.style.resize(200, 50)
        self.style.stateChanged.connect(self.changeStyle)

    def changeStyle(self):
        if self.style.isChecked():
            self.parent().setStyleSheet('QWidget { background-color: #2C2F33 ; color: #D9D9D9; selection-color: #D9D9D9; selection-background-color: #2C2F33}')
        else:
            self.parent().setStyleSheet('')






