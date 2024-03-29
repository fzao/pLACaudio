"""
A minimalist tool designed for a simple and fast conversion of large libraries
 of lossless audio files (ALAC, FLAC, DSD/DSF, WAV & AIFF) to another lossless
 or lossy formats (ALAC, FLAC, WAV, AIFF, MP3, AAC, Ogg Vorbis & Opus)

pLAC-Audio has an intensive parallel use of FFmpeg for the conversion

FFmpeg (A complete, cross-platform solution to record, convert and stream audio and video)
 is a free software and distributed under the terms of the GNU General Public License v3
 see https://www.ffmpeg.org/ for more information

pLAC-Audio is written in PyQT5 and has been tested on GNU/Linux, macOS X and MS Windows 64 bits
 with FFmpeg 4.1

pLAC-Audio supposes the presence of the FFmpeg executable in the PATH environment variable
 of your operating system. If not please go to https://www.ffmpeg.org/download.html and
 download a static version of ffMPEG

        _               _____                _ _
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

import os
import sys
import psutil
import logging
import subprocess
from mp3Thread import MP3Thread
from pLogger import PLogger
from ddButton import DDButtonFrom, DDButtonTo
from pPref import Preference
from pSettings import ChangeStyle, ShowLogger
from listFiles import listofFiles
from PyQt5.QtWidgets import QApplication, QWidget, QAction, QMenuBar,\
                            QPushButton, QGridLayout, QGroupBox, QFileDialog,\
                            QProgressBar, QVBoxLayout, QHBoxLayout,\
                            QComboBox, QMessageBox, QLCDNumber, QLabel, QSystemTrayIcon, QMenu
from PyQt5.QtCore import pyqtSlot, QTimer, QDateTime, QSettings
from PyQt5.QtGui import QIcon
from PyQt5 import sip


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.app = app
        self.myQMenuBar = QMenuBar(self)
        self.title = 'pLACaudio Transcoder'
        self.setWindowIcon(QIcon('./icon/beer.ico'))
        self.setBaseSize(480, 640)
        self.lossless_folder = ''
        self.lossy_location = ''
        self.audio_files = []
        self.ncpu = 0
        self.btn_lossless = DDButtonFrom(self)
        self.btn_lossless.setText('FLAC / ALAC / DSF / APE / WAV / AIFF')
        self.btn_lossy = DDButtonTo(self)
        self.btn_lossy.setText('OUTPUT')
        self.format = QComboBox()
        self.quality = QComboBox()
        self.btn_start = QPushButton('START')
        self.btn_stop = QPushButton('STOP')
        self.progress = QProgressBar()
        self.cpu_percent = QProgressBar()
        self.lcd_count = QLCDNumber()
        self.elapsed_time = QLCDNumber()
        self.perf = QLabel()
        self.grp_log = QGroupBox('logger')
        self.tray_icon = QSystemTrayIcon(self)
        self.threads = []
        self.nstart = 0
        self.nm1 = 0
        self.n0 = 0
        self.perfmean = []
        self.compression = 0
        self.timer_cpu = QTimer()
        self.timer_elapsed = QTimer()
        self.timer_perf = QTimer()
        self.start_time = QDateTime.currentDateTime().toPyDateTime()
        self.qval = {'MP3':{'Low':['9', 'VBR 45-85 kbit/s'], 'Medium':['5', 'VBR 120-150 kbit/s'], 'High':['0', 'VBR 220-260 kbit/s']},
                     'AAC':{'Low':['64k', 'CBR 64 kbit/s'], 'Medium':['128k', 'CBR 128 kbit/s'], 'High':['256k', 'CBR 256 kbit/s']},
                     'Ogg Vorbis':{'Low':['0', 'VBR 64 kbit/s'], 'Medium':['5', 'VBR 160 kbit/s'], 'High':['10', 'VBR 500 kbit/s']},
                     'Opus':{'Low':['32k', 'CBR 32 kbit/s'], 'Medium':['64k', 'CBR 64 kbit/s'], 'High':['128k', 'CBR 128 kbit/s']},
                     'FLAC':{'Low':['0', 'Compression Level: 0'], 'Medium':['5', 'Compression Level: 5'], 'High':['12', 'Compression Level: 12']},
                     'ALAC':{'Low':['0', 'Compression Level: 0'], 'Medium':['1', 'Compression Level: 1'], 'High':['2', 'Compression Level:2']},
                     'WAV': {'Low': ['0', 'No Compression'], 'Medium': ['0', 'No Compression'], 'High': ['0', 'No Compression']},
                     'AIFF': {'Low': ['0', 'No Compression'],'Medium': ['0', 'No Compression'], 'High': ['0', 'No Compression']}}
        self.danger = "QProgressBar::chunk { background-color: #FF3633;}"
        self.inter = "QProgressBar::chunk { background-color: #FFAF33;}"
        self.safe = "QProgressBar::chunk {background-color: #1CDA19;}"
        self.myquality = ''
        self.myformat = ''
        self.settings = QSettings('pLAC', 'pLAC')
        self.theme = self.settings.value('theme', type=int)
        self.poweroff = self.settings.value('poweroff', type=int)
        self.trayicon = self.settings.value('trayicon', type=int)
        self.samplerate = self.settings.value('samplerate', type=int)
        self.channels = self.settings.value('channels', type=int)
        self.initUI()

    def initUI(self):
        # settings
        ChangeStyle(self, self.theme)
        if 'logger' in self.settings.childKeys():
            log = self.settings.value('logger', type=int)
        else:
            log = 1
        ShowLogger(self, log)

        # window title and geometry
        self.setWindowTitle(self.title)

        # menu bar
        #colorcode = self.btn_lossless.palette().color(QPalette.Background).name()
        self.myQMenuBar.setStyleSheet("QMenuBar::item { background-color: rgba(255,255,255,0); }")
        self.myQMenuBar.setMaximumWidth(105)

        pLAC = self.myQMenuBar.addMenu('pLACaudio')
        prefpLAC = QAction('Settings', self)
        prefpLAC.triggered.connect(self.call_pref)
        pLAC.addAction(prefpLAC)
        aboutpLAC = QAction('About', self)
        aboutpLAC.triggered.connect(self.call_info)
        pLAC.addAction(aboutpLAC)

        # tray icon
        show_action = QAction("Show", self)
        hide_action = QAction("Hide", self)
        quit_action = QAction("Exit", self)
        show_action.triggered.connect(self.show)
        hide_action.triggered.connect(self.hide)
        quit_action.triggered.connect(self.pLACexit)
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.setIcon(QIcon('./icon/beer.ico'))
        self.tray_icon.activated.connect(self.iconActivated)
        if self.trayicon != 0:
            self.tray_icon.show()
        else:
            self.tray_icon.hide()

        # button for the folder selection (ALAC)
        self.btn_lossless.setMinimumHeight(50)
        self.btn_lossless.move(50, 10)
        self.btn_lossless.setToolTip('Drag and Drop the folder of lossless files to convert')
        self.btn_lossless.clicked.connect(self.on_click_alac)

        # button for the folder selection (MP3)
        self.btn_lossy.setMinimumHeight(50)
        self.btn_lossy.move(50, 60)
        self.btn_lossy.setToolTip('Drag and Drop the destination folder for the audio files')
        self.btn_lossy.clicked.connect(self.on_click_mp3)

        # buttons for starting and stopping
        self.btn_start.setMinimumHeight(100)
        self.btn_start.setToolTip('Start conversion')
        self.btn_start.setIcon(QIcon('./icon/play_on.png'))
        self.btn_start.clicked.connect(self.call_convert2lossy)
        self.btn_stop.setMinimumHeight(100)
        self.btn_stop.setEnabled(False)
        self.btn_stop.setToolTip('Stop conversion')
        self.btn_stop.setIcon(QIcon('./icon/stop_off.png'))

        # Choosing number of cpu with a ComboBox
        combo = QComboBox()
        combo.setToolTip('Choose the number of CPUs')
        combo.addItem('CPU')
        ncpu = os.cpu_count()
        combo.addItems([str(i+1) for i in range(ncpu)])
        combo.currentIndexChanged['int'].connect(self.current_index_changed)

        # logging display
        logTextBox = PLogger(self)
        logTextBox.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s -> %(message)s', "%Y-%m-%d %H:%M"))
        logging.getLogger().addHandler(logTextBox)
        logging.getLogger().setLevel(logging.DEBUG)  # default level

        # LCD
        self.lcd_count.setSegmentStyle(2)
        self.lcd_count.setToolTip('Counting down files')
        self.elapsed_time.setToolTip('Elapsed time')
        self.elapsed_time.setDigitCount(9)
        self.elapsed_time.display('%03d:%02d:%02d' % (0, 0, 0))

        # CPU activity
        self.cpu_percent.setMinimum(0)
        self.cpu_percent.setMaximum(100)
        self.cpu_percent.setStyleSheet("QProgressBar::chunk { background-color: orange; }")
        self.cpu_percent.setToolTip('CPU activity')
        self.timer_cpu.timeout.connect(self.showCPU)
        self.timer_cpu.start(1000)

        # Performance
        self.perf.setText('speed:0 files/sec\t(mean: 0.0)')
        self.timer_perf.timeout.connect(self.showPERF)
        self.timer_perf.start(1000)

        # Elapsed time
        self.timer_elapsed.timeout.connect(self.showTIME)
        self.timer_elapsed.start(1000)

        # Progress
        self.progress.setToolTip('Conversion progress')

        # Format
        self.format.setToolTip("Choose the destination format")
        self.format.addItem('- Format')
        self.format.addItems(list(self.qval.keys()))
        self.format.currentTextChanged.connect(self.current_index_changed_format)

        # Quality
        self.quality.setToolTip("Choose the compression quality ('Low' for a small file size only!)")
        self.quality.addItem('- Quality')
        self.quality.addItems(['Low', 'Medium', 'High'])
        self.quality.currentTextChanged.connect(self.current_index_changed_qual)

        #  Layout
        vlayout1 = QVBoxLayout()
        vlayout1.addWidget(self.btn_lossless)
        vlayout1.addWidget(self.btn_lossy)
        grp_io = QGroupBox('io')
        grp_io.setLayout(vlayout1)
        grp_io.setToolTip('Choose the folders')
        vlayout2 = QVBoxLayout()
        vlayout2.addWidget(self.format)
        vlayout2.addWidget(self.quality)
        grp_codec = QGroupBox('codec')
        grp_codec.setLayout(vlayout2)
        grp_codec.setToolTip('Audio file type')

        hlayout1 = QHBoxLayout()
        hlayout1.addWidget(combo)
        hlayout1.addWidget(self.cpu_percent)
        hlayout2 = QHBoxLayout()
        hlayout2.addWidget(self.btn_start)
        hlayout2.addWidget(self.btn_stop)
        vlayout3 = QVBoxLayout()
        vlayout3.addWidget(self.elapsed_time)
        vlayout3.addWidget(self.lcd_count)
        hlayout2.addLayout(vlayout3)
        vlayout4 = QVBoxLayout()
        vlayout4.addLayout(hlayout1)
        vlayout4.addLayout(hlayout2)
        grp_conv = QGroupBox('convert')
        grp_conv.setLayout(vlayout4)
        grp_conv.setToolTip('Control the conversion')

        vlayout5 = QVBoxLayout()
        vlayout5.addWidget(logTextBox.widget)
        self.grp_log.setLayout(vlayout5)
        self.grp_log.setToolTip('Information')

        vlayout6 = QVBoxLayout()
        vlayout6.addWidget(self.progress)
        vlayout6.addWidget(self.perf)
        grp_pro = QGroupBox('progress')
        grp_pro.setLayout(vlayout6)
        grp_pro.setToolTip('See the progress status')

        grid = QGridLayout()
        grid.addWidget(self.myQMenuBar, 0, 0, 1, 0)
        grid.addWidget(grp_io, 1, 0)
        grid.addWidget(grp_codec, 1, 1)
        grid.addWidget(grp_conv, 2, 0, 1, 0)
        grid.addWidget(self.grp_log, 3, 0, 1, 0)
        grid.addWidget(grp_pro, 4, 0, 1, 0)
        self.setLayout(grid)

        # show window
        self.show()

    @pyqtSlot()
    def on_click_alac(self):
        self.lossless_folder = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if self.lossless_folder != '':
            if os.name == 'nt':  # Windows specific
                self.lossless_folder = self.lossless_folder.replace('/', '\\')
            self.btn_lossless.setToolTip(self.lossless_folder)
            logging.info('from folder: ' + self.lossless_folder)
            # get the list of all files to convert
            listofFiles(self)

    @pyqtSlot()
    def on_click_mp3(self):
        self.lossy_location = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if self.lossy_location != '':
            if os.name == 'nt':  # Windows specific
                self.lossy_location = self.lossy_location.replace('/', '\\')
            self.btn_lossy.setToolTip(self.lossy_location)
            logging.info('to folder: ' + self.lossy_location)

    @pyqtSlot()
    def call_info(self):
        QMessageBox.information(self, "Information", "<a href='https://github.com/fzao/pLACaudio' style='color:#32C896'>pLACaudio v" + version + " </a> - License GNU GPL v3.0 - Copyright (c) 2019\n")

    @pyqtSlot()
    def call_pref(self):
        self.pref = Preference(self)
        self.pref.show()

    @pyqtSlot(int)
    def current_index_changed(self, index):
        self.ncpu = index
        logging.info('Number of CPUs: ' + str(self.ncpu))

    @pyqtSlot()
    def current_index_changed_qual(self):
        if self.quality.currentIndex() > 0:
            self.myquality = self.quality.currentText()
            if self.format.currentIndex() > 0:
                logging.info('Quality is set to: ' + self.qval[self.myformat][self.myquality][1])

    @pyqtSlot()
    def current_index_changed_format(self):
        if self.format.currentIndex() > 0:
            self.myformat = self.format.currentText()
            logging.info('Format is: ' + self.format.currentText())
            if self.quality.currentIndex() > 0:
                logging.info('Quality is set to: ' + self.qval[self.myformat][self.myquality][1])

    @pyqtSlot()
    def call_convert2lossy(self):
        # check the folders
        if not os.path.isdir(self.lossless_folder):
            logging.error('Lossless folder is not correctly set!')
            QMessageBox.warning(self, 'Warning', 'Folder of lossless files is not correctly set')
            return
        if not os.path.isdir(self.lossy_location):
            logging.error('Lossy folder is not correctly set!')
            QMessageBox.warning(self, 'Warning', 'Folder of lossy files is not correctly set')
            return
        # check the CPUs
        if self.ncpu < 1:
            logging.error('The number of CPUs is not defined!')
            QMessageBox.warning(self, 'Warning', 'The number of CPUs is not defined')
            return
        # check the format
        if self.format.currentIndex() < 1:
            logging.error('The format compression is not chosen!')
            QMessageBox.warning(self, 'Warning', 'Choose the format compression')
            return
        # check the Quality
        if self.quality.currentIndex() < 1:
            if self.format.currentIndex() != 7 and self.format.currentIndex() != 8:  # not WAV and AIFF
                logging.error('The quality compression is not chosen!')
                QMessageBox.warning(self, 'Warning', 'Choose the quality compression')
                return
            else:
                self.myquality = 'Low'  # WAV and AIFF (no compression)
        # start time
        self.start_time = QDateTime().currentDateTime().toPyDateTime()
        # is the list full?
        listofFiles(self)
        if len(self.audio_files) == 0:
            return
        # shutdown requested?
        if self.poweroff == 2:
            answer = QMessageBox.warning(self, 'Message', 'Computer will be shut down after conversion! Continue?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if answer == QMessageBox.No:
                return
        # Thread execution
        n = min(self.ncpu, len(self.audio_files))
        audio = [self.audio_files[i * n:(i + 1) * n] for i in range((len(self.audio_files) + n - 1) // n)]
        audio_end = []
        if len(audio) > 1:
            audio_end = audio.pop(-1)
        audio = [[j[i] for j in audio] for i in range(len(audio[0]))]
        for i in range(len(audio_end)):
            audio[i].append(audio_end[i])
        self.threads = []
        for i in range(len(audio)):
            q = self.qval[self.myformat][self.myquality][0]
            self.threads.append(MP3Thread(audio[i], self.lossless_folder, self.lossy_location, q, self.myformat,
                                          self.samplerate, self.channels))
        self.nstart = 0
        for i in range(len(audio)):
            self.threads[i].update_progress_bar.connect(self.update_progress_bar)
            self.threads[i].finished.connect(self.done)
            self.threads[i].start()
            self.nstart += 1
            self.btn_stop.clicked.connect(self.threads[i].terminate)
        logging.info('Conversion in progress...')
        self.tray_icon.showMessage(
            "pLACaudio",
            "Conversion has just started...",
            QSystemTrayIcon.Information,
            5000
        )
        self.btn_stop.setEnabled(True)
        self.btn_stop.setIcon(QIcon('./icon/stop_on.png'))
        self.btn_start.setEnabled(False)
        self.btn_start.setIcon(QIcon('./icon/play_off.png'))

    @pyqtSlot()
    def done(self):
        self.nstart -= 1
        if self.nstart == 0:
            logging.info('Done!')
            if self.poweroff == 0:
                self.btn_stop.setEnabled(False)
                self.btn_stop.setIcon(QIcon('./icon/stop_off.png'))
                self.btn_start.setEnabled(True)
                self.btn_start.setIcon(QIcon('./icon/play_on.png'))
                if not self.isHidden():
                    QMessageBox.information(self, "Done!", "Conversion done!")
                self.progress.setValue(0)
                self.lcd_count.display(0)
                self.elapsed_time.display('%03d:%02d:%02d' % (0, 0, 0))
                self.perf.setText('speed:0 files/sec\t(mean: 0.0)')
                self.perfmean = []
                self.tray_icon.showMessage(
                    "pLACaudio",
                    "Conversion just ended!",
                    QSystemTrayIcon.Information,
                    5000
                )
            elif self.poweroff == 1:
                self.app.quit()
            elif self.poweroff == 2:
                if sys.platform == 'win32':  # Windows specific
                    os.system('shutdown /s /f')
                elif 'linux' in sys.platform:
                    os.system('shutdown -h now')
                elif sys.platform == 'darwin':
                    subprocess.call(['osascript', '-e', 'tell app "System Events" to shut down'])
                self.app.quit()  # !?
            else:
                pass

    @pyqtSlot()
    def update_progress_bar(self):
        self.progress.setValue(self.progress.value() + 1)
        self.lcd_count.display(self.lcd_count.value() - 1)

    @pyqtSlot()
    def showCPU(self):
        if self.btn_stop.isEnabled() == True:
            cpu_load = int(psutil.cpu_percent())
            if cpu_load < 50:
                self.cpu_percent.setStyleSheet(self.safe)
            elif cpu_load < 80:
                self.cpu_percent.setStyleSheet(self.inter)
            else:
                self.cpu_percent.setStyleSheet(self.danger)
            self.cpu_percent.setValue(cpu_load)
        else:
            self.cpu_percent.setValue(0)

    @pyqtSlot()
    def showPERF(self):
        if self.btn_stop.isEnabled() == True:
            self.nm1 = self.n0
            self.n0 = self.lcd_count.value()
            delta = self.nm1 - self.n0
            self.perfmean.append(delta)
            meanval = sum(self.perfmean) / len(self.perfmean)
            self.perf.setText('speed: %d files/sec\t(mean: %.2f)' % (delta, meanval))

    @pyqtSlot()
    def showTIME(self):
        if self.nstart > 0:
            now = QDateTime().currentDateTime().toPyDateTime()
            diff = now - self.start_time
            totsec = diff.total_seconds()
            h = int(totsec // 3600)
            m = int((totsec % 3600) // 60)
            sec = int((totsec % 3600) % 60)
            self.elapsed_time.display('%03d:%02d:%02d' % (h, m, sec))

    def closeEvent(self, event):
        if self.trayicon != 0:
            event.ignore()
            if not self.isHidden():
                self.tray_icon.showMessage(
                    "pLACaudio",
                    "was minimized to Tray",
                    QSystemTrayIcon.Information,
                    5000
                )
                self.hide()
        else:
            if self.nstart > 0:  # conversion still in progress
                reply = QMessageBox.question(self, 'Message',
                                             "Conversion is still in progress. Are you sure to quit?", QMessageBox.Yes |
                                             QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    event.accept()
                else:
                    event.ignore()
            else:
                event.accept()

    @pyqtSlot()
    def pLACexit(self):
        if self.nstart > 0:  # conversion still in progress
            self.show()
            reply = QMessageBox.question(self, 'Message',
                                         "Conversion is still in progress. Are you sure to quit?", QMessageBox.Yes |
                                         QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.app.quit()
        else:
            self.app.quit()

    def iconActivated(self, reason):
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            self.show()
        elif reason == QSystemTrayIcon.MiddleClick:
            if self.nstart > 0:
                percent = (self.progress.value() - self.progress.minimum()) / (self.progress.maximum() - self.progress.minimum())
                percent = percent * 100
                self.tray_icon.showMessage("pLACaudio",
                    "Progress: " + "{0:0.1f}".format(percent) + ' %',
                    QSystemTrayIcon.Information,
                    2000)


if __name__ == '__main__':
    version = '0.4'
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
