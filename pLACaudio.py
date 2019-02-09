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
import glob
import multiprocessing as mp
import psutil
import logging
from mp3Thread import mp3Thread
from pLogger import pLogger
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout, QGroupBox, QFileDialog, QStyle, QProgressBar, QVBoxLayout, QHBoxLayout, QComboBox, QMessageBox, QLCDNumber, QLabel, QSlider
from PyQt5.QtCore import pyqtSlot, QTimer, QDateTime
from PyQt5.QtGui import QIcon
from PyQt5 import sip


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'pLACaudio'
        self.setWindowIcon(QIcon('./icon/beer.ico'))
        self.setBaseSize(480, 640)
        self.lossless_folder = ''
        self.lossy_location = ''
        self.ncpu = 0
        self.btn_lossless = QPushButton('FLAC / ALAC / DSF / WAV / AIFF')
        self.btn_lossy = QPushButton('Output')
        self.format = QComboBox()
        self.quality = QComboBox()
        self.btn_start = QPushButton('START')
        self.btn_stop = QPushButton('STOP')
        self.btn_about = QPushButton('About')
        self.progress = QProgressBar()
        self.cpu_percent = QProgressBar()
        self.lcd_count = QLCDNumber()
        self.elapsed_time = QLCDNumber()
        self.perf = QLabel()
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
        self.qval = {'MP3':{'Low':['9', 'VBR 45-85 kbit/s'], 'Medium':['5', 'VBR 120-150 kbit/s'], 'High':['0', 'VBR 220-260 kbit/s']},\
                     'AAC':{'Low':['64k', 'CBR 64 kbit/s'], 'Medium':['128k', 'CBR 128 kbit/s'], 'High':['256k', 'CBR 256 kbit/s']},\
                     'Ogg Vorbis':{'Low':['0', 'VBR 64 kbit/s'], 'Medium':['5', 'VBR 160 kbit/s'], 'High':['10', 'VBR 500 kbit/s']},\
                     'Opus':{'Low':['32k', 'CBR 32 kbit/s'], 'Medium':['64k', 'CBR 64 kbit/s'], 'High':['128k', 'CBR 128 kbit/s']},\
                     'FLAC':{'Low':['0', 'Compression Level: 0'], 'Medium':['5', 'Compression Level: 5'], 'High':['12', 'Compression Level: 12']},\
                     'ALAC':{'Low':['0', 'Compression Level: 0'], 'Medium':['1', 'Compression Level: 1'], 'High':['2', 'Compression Level:2']}, \
                     'WAV': {'Low': ['0', 'No Compression'], 'Medium': ['0', 'No Compression'], 'High': ['0', 'No Compression']}, \
                     'AIFF': {'Low': ['0', 'No Compression'],'Medium': ['0', 'No Compression'], 'High': ['0', 'No Compression']}}

        self.myquality = ''
        self.myformat = ''
        self.initUI()

    def initUI(self):
        # window title and geometry
        self.setWindowTitle(self.title)

        # button for the folder selection (ALAC)
        self.btn_lossless.setMinimumHeight(50)
        self.btn_lossless.move(50, 10)
        self.btn_lossless.setToolTip('Folder of lossless files to convert')
        self.btn_lossless.clicked.connect(self.on_click_alac)

        # button for the folder selection (MP3)
        self.btn_lossy.setMinimumHeight(50)
        self.btn_lossy.move(50, 60)
        self.btn_lossy.setToolTip('Destination folder for the audio files')
        self.btn_lossy.clicked.connect(self.on_click_mp3)

        # buttons for starting and stopping
        self.btn_start.setMinimumHeight(100)
        self.btn_start.setToolTip('Start conversion')
        self.btn_start.setIcon(QIcon(QApplication.style().standardIcon(QStyle.SP_MediaPlay)))
        self.btn_start.clicked.connect(self.call_convert2lossy)
        self.btn_stop.setMinimumHeight(100)
        self.btn_stop.setEnabled(False)
        self.btn_stop.setToolTip('Stop conversion')
        self.btn_stop.setIcon(QIcon(QApplication.style().standardIcon(QStyle.SP_MediaStop)))

        # button 'about'
        self.btn_about.setMaximumWidth(100)
        self.btn_about.clicked.connect(self.call_info)

        # Choosing number of cpu with a ComboBox
        combo = QComboBox()
        combo.setToolTip('Choose the number of CPUs')
        combo.addItem('CPU')
        ncpu = mp.cpu_count()
        combo.addItems([str(i+1) for i in range(ncpu)])
        combo.currentIndexChanged['int'].connect(self.current_index_changed)

        # logging display
        logTextBox = pLogger(self)
        logTextBox.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s -> %(message)s', "%Y-%m-%d %H:%M"))
        logging.getLogger().addHandler(logTextBox)
        logging.getLogger().setLevel(logging.DEBUG) # default level

        # LCD
        self.lcd_count.setSegmentStyle(2)
        self.lcd_count.setToolTip('Counting down files')
        self.elapsed_time.setToolTip('Elapsed time')
        self.elapsed_time.setDigitCount(9)
        self.elapsed_time.display('%03d:%02d:%02d' % (0, 0, 0))

        # CPU activity
        self.cpu_percent.setMinimum(0.)
        self.cpu_percent.setMaximum(100.)
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
        grp_log = QGroupBox('logger')
        grp_log.setLayout(vlayout5)
        grp_log.setToolTip('Information')

        hlayout3 = QHBoxLayout()
        hlayout3.addWidget(self.progress)
        hlayout3.addWidget(self.btn_about)
        vlayout6 = QVBoxLayout()
        vlayout6.addLayout(hlayout3)
        vlayout6.addWidget(self.perf)
        grp_pro = QGroupBox('progress')
        grp_pro.setLayout(vlayout6)
        grp_pro.setToolTip('See the progress status')

        grid = QGridLayout()
        grid.addWidget(grp_io, 0, 0)
        grid.addWidget(grp_codec, 0, 1)
        grid.addWidget(grp_conv, 1, 0, 1, 0)
        grid.addWidget(grp_log, 2, 0, 1, 0)
        grid.addWidget(grp_pro, 3, 0, 1, 0)
        self.setLayout(grid)

        # show window
        self.show()

    @pyqtSlot()
    def on_click_alac(self):
        self.lossless_folder = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if os.name == 'nt':  # Windows specific
            self.lossless_folder = self.lossless_folder.replace('/', '\\')
        logging.info('from folder: ' + self.lossless_folder)
        if self.lossless_folder != '':
            self.btn_lossless.setToolTip(self.lossless_folder)

    @pyqtSlot()
    def on_click_mp3(self):
        self.lossy_location = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if os.name == 'nt':  # Windows specific
            self.lossy_location = self.lossy_location.replace('/', '\\')
        logging.info('to folder: ' + self.lossy_location)
        if self.lossy_location != '':
            self.btn_lossy.setToolTip(self.lossy_location)

    @pyqtSlot()
    def call_info(self):
        QMessageBox.information(self, "Information", "<a href='https://github.com/fzao/pLACaudio'>pLACaudio v0.2</a> - License GNU GPL v3.0 - Copyright (c) 2019\n")

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
        # get the list of all files to convert
        ext = 'm4a'
        audio_alac = glob.glob(self.lossless_folder + '/**/*.' + ext, recursive=True)
        ext = 'flac'
        audio_flac = glob.glob(self.lossless_folder + '/**/*.' + ext, recursive=True)
        ext = 'dsf'
        audio_dsf = glob.glob(self.lossless_folder + '/**/*.' + ext, recursive=True)
        ext = 'wav'
        audio_wav = glob.glob(self.lossless_folder + '/**/*.' + ext, recursive=True)
        ext = 'aif'
        audio_aiff1 = glob.glob(self.lossless_folder + '/**/*.' + ext, recursive=True)
        ext = 'aiff'
        audio_aiff2 = glob.glob(self.lossless_folder + '/**/*.' + ext, recursive=True)
        audio_aiff = audio_aiff1 + audio_aiff2
        audio_files = audio_alac + audio_flac + audio_dsf + audio_wav + audio_aiff
        # Number of files found
        if len(audio_files) == 0:
            logging.error('No files found!')
            QMessageBox.warning(self, 'Warning', 'No lossless files found!')
            return
        else:
            logging.info('Number of ALAC files: ' + str(len(audio_alac)))
            logging.info('Number of FLAC files: ' + str(len(audio_flac)))
            logging.info('Number of DSF files: ' + str(len(audio_dsf)))
            logging.info('Number of WAV files: ' + str(len(audio_wav)))
            logging.info('Number of AIFF files: ' + str(len(audio_aiff)))
            logging.info('Total number of files: ' + str(len(audio_files)))
        self.progress.setMinimum(0)
        self.progress.setMaximum(len(audio_files) - 1)
        self.progress.setValue(0)
        self.lcd_count.display(len(audio_files))
        self.nm1 = len(audio_files)
        self.n0 = len(audio_files)
        # Thread execution
        n = min(self.ncpu, len(audio_files))
        audio = [audio_files[i * n:(i + 1) * n] for i in range((len(audio_files) + n - 1) // n)]
        audio_end = []
        if len(audio) > 1:
            audio_end = audio.pop(-1)
        audio = [[j[i] for j in audio] for i in range(len(audio[0]))]
        for i in range(len(audio_end)):
            audio[i].append(audio_end[i])
        self.threads = []
        for i in range(len(audio)):
            q = self.qval[self.myformat][self.myquality][0]
            self.threads.append(mp3Thread(audio[i], self.lossless_folder, self.lossy_location, q, self.myformat))
        self.nstart = 0
        for i in range(len(audio)):
            self.threads[i].update_progress_bar.connect(self.update_progress_bar)
            self.threads[i].finished.connect(self.done)
            self.threads[i].start()
            self.nstart += 1
            self.btn_stop.clicked.connect(self.threads[i].terminate)
        logging.info('Conversion in progress...')
        self.btn_stop.setEnabled(True)
        self.btn_start.setEnabled(False)

    def done(self):
        self.nstart -= 1
        if self.nstart == 0:
            self.btn_stop.setEnabled(False)
            self.btn_start.setEnabled(True)
            logging.info('Done!')
            QMessageBox.information(self, "Done!", "Conversion done!")
            self.progress.setValue(0)
            self.lcd_count.display(0)
            self.elapsed_time.display('%03d:%02d:%02d' % (0, 0, 0))
            self.perf.setText('speed:0 files/sec\t(mean: 0.0)')
            self.perfmean = []

    def update_progress_bar(self):
        self.progress.setValue(self.progress.value() + 1)
        self.lcd_count.display(self.lcd_count.value() - 1)

    def showCPU(self):
        if self.btn_stop.isEnabled() == True:
            cpu_load = psutil.cpu_percent()
            if cpu_load < 50.:
                self.cpu_percent.setStyleSheet(safe)
            elif cpu_load < 80.:
                self.cpu_percent.setStyleSheet(inter)
            else:
                self.cpu_percent.setStyleSheet(danger)
            self.cpu_percent.setValue(cpu_load)
        else:
            self.cpu_percent.setValue(0.)

    def showPERF(self):
        if self.btn_stop.isEnabled() == True:
            self.nm1 = self.n0
            self.n0 = self.lcd_count.value()
            delta = self.nm1 - self.n0
            self.perfmean.append(delta)
            meanval = sum(self.perfmean) / len(self.perfmean)
            self.perf.setText('speed: %d files/sec\t(mean: %.2f)' % (delta, meanval))

    def showTIME(self):
        if self.nstart > 0:
            now = QDateTime().currentDateTime().toPyDateTime()
            diff = now - self.start_time
            totsec = diff.total_seconds()
            h = int(totsec // 3600)
            m = int((totsec % 3600) // 60)
            sec = int((totsec % 3600) % 60)
            self.elapsed_time.display('%03d:%02d:%02d' % (h, m, sec))


if __name__ == '__main__':
    danger = "QProgressBar::chunk { background-color: #FF3633;}"
    inter = "QProgressBar::chunk { background-color: #FFAF33;}"
    safe = "QProgressBar::chunk {background-color: #61FF33;}"
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
