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
import logging
from pSettings import ChangeStyle, ShowLogger, ShowTrayIcon, Shutdown, SampleRate
from PyQt5.QtWidgets import QMainWindow, QCheckBox, QPushButton, QRadioButton, QLabel, QComboBox
from PyQt5.QtGui import QIcon, QFont
from PyQt5 import Qt
from PyQt5.QtCore import pyqtSlot

class Preference(QMainWindow):
    def __init__(self, parent):
        super(Preference, self).__init__(parent)

        # window
        self.setWindowTitle('Settings')
        self.setWindowIcon(QIcon('./icon/beer.ico'))
        self.setWindowModality(Qt.Qt.WindowModal)
        self.setFixedSize(370, 500)

        # bold font
        myFont = QFont()
        myFont.setBold(True)

        # radio button (color themes)
        txttheme = QLabel('Color theme : ', self)
        txttheme.setFont(myFont)
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
        txtlog.setFont(myFont)
        txtlog.move(10, 90)
        self.logger = QCheckBox('Display', self)
        self.logger.move(30, 120)

        # combo (shutdown)
        txtpwoff = QLabel('After conversion : ', self)
        txtpwoff.setFont(myFont)
        txtpwoff.setMinimumWidth(200)
        txtpwoff.move(10, 170)
        self.pwoff = QComboBox(self)
        self.pwoff.addItems(['Wait', 'Quit', 'Power-off'])
        self.pwoff.currentIndexChanged['int'].connect(self.poweroff)
        self.pwoff.setMinimumWidth(125)
        self.pwoff.move(30, 200)

        # checkbox (tray icon)
        txttray = QLabel('System tray icon : ', self)
        txttray.setFont(myFont)
        txttray.setMinimumWidth(150)
        txttray.move(10, 250)
        self.tray = QCheckBox('Use and Show', self)
        self.tray.setToolTip('Keep in the background when the main window is closed')
        self.tray.setMinimumWidth(150)
        self.tray.move(30, 280)

        # checkbox and combo (sample rate)
        txtsr = QLabel('User-defined sample rate (lossless DSF conversion) :', self)
        txtsr.setFont(myFont)
        txtsr.setMinimumWidth(360)
        txtsr.move(10, 330)
        self.sr = QCheckBox('Select (Hz)', self)
        self.sr.setToolTip('Choose a sample rate frequency when converting from DSF to FLAC/ALAC/WAV/AIFF')
        self.sr.setMinimumWidth(150)
        self.sr.move(30, 360)
        self.srfreq = QComboBox(self)
        self.srfreq.addItems(['44100', '88200', '176400', '352800'])
        self.srfreq.currentIndexChanged['int'].connect(self.samplerate)
        self.srfreq.setMinimumWidth(125)
        self.srfreq.move(160, 365)

        # quit button
        self.btn_ok = QPushButton('OK', self)
        self.btn_ok.resize(150, 50)
        self.btn_ok.move(110, 430)
        self.initUI()

    def initUI(self):
        # checkbox (display logger)
        if self.parent().grp_log.isVisible():
            self.logger.setCheckState(Qt.Qt.Checked)
        else:
            self.logger.setCheckState(Qt.Qt.Unchecked)
        self.logger.stateChanged.connect(self.changeLogger)

        # checkbox (tray icon)
        if self.parent().trayicon != 0:
            self.tray.setCheckState(Qt.Qt.Checked)
        else:
            self.tray.setCheckState(Qt.Qt.Unchecked)
        self.tray.stateChanged.connect(self.changeTrayIcon)

        # combo (after conversion)
        self.pwoff.setCurrentIndex(self.parent().poweroff)

        # checkbox (sample rate)
        if self.parent().samplerate == 0:
            self.sr.setCheckState(Qt.Qt.Unchecked)
            self.srfreq.setDisabled(True)
        else:
            self.sr.setCheckState(Qt.Qt.Checked)
            self.srfreq.setEnabled(True)
            self.srfreq.setCurrentIndex(self.parent().samplerate - 1)
        self.sr.stateChanged.connect(self.changeSR)

        # quit button
        self.btn_ok.clicked.connect(self.pref_exit)

    @pyqtSlot()
    def btnstate(self, b):
        if b.text() == 'Default':
            if b.isChecked() is True:
                theme = 0
                logging.info('the color theme is the default one')
            else:
                theme = 1
        if b.text() == "Dark":
            if b.isChecked() is True:
                theme = 1
                logging.info('the dark theme is selected')
            else:
                theme = 0
        ChangeStyle(self.parent(), theme)

    @pyqtSlot()
    def changeLogger(self):
        if self.logger.isChecked():
            ShowLogger(self.parent(), 1)
            logging.info('logger is visible')
        else:
            ShowLogger(self.parent(), 0)
            logging.info('logger is not shown')

    @pyqtSlot()
    def changeTrayIcon(self):
        if self.tray.isChecked():
            ShowTrayIcon(self.parent(), 1)
            logging.info('Tray icon is enabled')
        else:
            ShowTrayIcon(self.parent(), 0)
            logging.info('Tray icon is disabled')

    @pyqtSlot()
    def changeSR(self):
        if self.sr.isChecked():
            self.srfreq.setEnabled(True)
            SampleRate(self.parent(), self.srfreq.currentIndex() + 1)
        else:
            self.srfreq.setDisabled(True)
            SampleRate(self.parent(), 0)

    @pyqtSlot(int)
    def poweroff(self, value):
        if value == 0:
            logging.info('after the conversion pLACaudio will wait')
        elif value == 1:
            logging.info('after the conversion pLACaudio will quit')
        elif value == 2:
            logging.info('after the conversion pLACaudio will shutdown the computer')
        Shutdown(self.parent(), value)

    @pyqtSlot(int)
    def samplerate(self, value):
        if value == 0:
            logging.info('Sample rate frequency is set to 44100 Hz')
        elif value == 1:
            logging.info('Sample rate frequency is set to 88200 Hz')
        elif value == 2:
            logging.info('Sample rate frequency is set to 176400 Hz')
        elif value == 3:
            logging.info('Sample rate frequency is set to 352800 Hz')
        SampleRate(self.parent(), self.srfreq.currentIndex() + 1)

    def pref_exit(self):
        self.close()




