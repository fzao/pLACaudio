"""
A minimalist tool designed for the simple and fast conversion of large libraries
 of lossless audio files (ALAC, FLAC, WAV & AIFF)
 to lossy formats (MP3, Ogg Vorbis, AAC & Opus)

pLAC-Audio has an intensive parallel use of FFmpeg for the conversion

FFmpeg (A complete, cross-platform solution to record, convert and stream audio and video)
 is free software and distributed under the terms of the GNU General Public License v3
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

Copyright (c) 2019 Fabrice Zaoui

License GNU GPL v3

"""

import os
import subprocess
import sys
import logging
import glob
import multiprocessing as mp
import psutil
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QPlainTextEdit, QStyle, QProgressBar, QVBoxLayout, QHBoxLayout, QComboBox, QMessageBox, QLCDNumber, QLabel, QSlider
from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal, QTimer, QDateTime, Qt
from PyQt5.QtGui import QIcon
from PyQt5 import sip


class mp3Thread(QThread):
    update_progress_bar = pyqtSignal()

    def __init__(self, audio_files, lossless_folder, lossy_location, qvalue, codec):
        QThread.__init__(self)
        self.audio_files = audio_files
        self.lossless_folder = lossless_folder
        self.lossy_location = lossy_location
        self.qval = qvalue
        self.codec = codec
        self.sep = '/'
        self.null = '/dev/null'
        if os.name == 'nt':
            self.sep = '\\'
            self.null = 'NUL'

    def __del__(self):
        self.wait()

    def convert2lossy(self, audio_file_in):
        path_audio = os.path.dirname(audio_file_in)
        file_name = os.path.splitext(os.path.basename(audio_file_in))[0]
        len_indir = len(self.lossless_folder)
        path_audio = path_audio[len_indir:]
        path_audio = self.lossy_location + path_audio
        if not os.path.isdir(path_audio):
            try:
                os.makedirs(path_audio)
            except OSError:
                # logging.exception('Unable to create the destination folder')
                pass
        if self.codec == 1:
            ext = 'mp3'
            audio_file = file_name + '.' + ext
            audio_file_out = path_audio + self.sep + audio_file
            if self.qval == 1:
                q = '9'
            elif self.qval == 2:
                q = '5'
            else:
                q = '0'
            if not os.path.isfile(audio_file_out):
                subprocess.call('ffmpeg -nostats -loglevel 0 -i '
                          + '"' + audio_file_in + '"'
                          + ' -vn -acodec libmp3lame -q:a '+ q + ' -map_metadata 0'
                          + ' -id3v2_version 3 '
                          + '"' + audio_file_out + '"' + ' > ' + self.null,
                                shell=True)
        elif self.codec == 2:
            ext = 'ogg'
            audio_file = file_name + '.' + ext
            audio_file_out = path_audio + self.sep + audio_file
            if self.qval == 1:
                q = '0'
            elif self.qval == 2:
                q = '5'
            else:
                q = '10'
            if not os.path.isfile(audio_file_out):
                subprocess.call('ffmpeg -nostats -loglevel 0 -i '
                                + '"' + audio_file_in + '"'
                                + ' -vn -acodec libvorbis -q:a ' + q + ' -map_metadata 0 '
                                + '"' + audio_file_out + '"' + ' > ' + self.null,
                                shell=True)
        elif self.codec == 3:
            ext = 'm4a'
            audio_file = file_name + '.' + ext
            audio_file_out = path_audio + self.sep + audio_file
            if self.qval == 1:
                q = '64k'
            elif self.qval == 2:
                q = '160k'
            else:
                q = '500k'
            if not os.path.isfile(audio_file_out):
                subprocess.call('ffmpeg -nostats -loglevel 0 -i '
                                + '"' + audio_file_in + '"'
                                + ' -vn -acodec aac -b:a ' + q + ' -map_metadata 0 '
                                + '"' + audio_file_out + '"' + ' > ' + self.null,
                                shell=True)
        elif self.codec == 4:
            ext = 'opus'
            audio_file = file_name + '.' + ext
            audio_file_out = path_audio + self.sep + audio_file
            if self.qval == 1:
                q = '32k'
            elif self.qval == 2:
                q = '64k'
            else:
                q = '128k'
            if not os.path.isfile(audio_file_out):
                subprocess.call('ffmpeg -nostats -loglevel 0 -i '
                                + '"' + audio_file_in + '"'
                                + ' -vn -acodec libopus -b:a ' + q + ' -map_metadata 0 '
                                + '"' + audio_file_out + '"' + ' > ' + self.null,
                                shell=True)

    def run(self):
        for audio_file_in in self.audio_files:
            self.convert2lossy(audio_file_in)
            self.update_progress_bar.emit()

class QPlainTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QPlainTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'pLACaudio'
        self.setWindowIcon(QIcon('./icon/beer.ico'))
        self.setFixedSize(480, 640)
        self.lossless_folder = ''
        self.lossy_location = ''
        self.ncpu = 0
        self.btn_lossless = QPushButton('ALAC / FLAC / WAV / AIFF')
        self.btn_lossy = QPushButton('Output')
        self.format = QComboBox()
        self.quality = QComboBox()
        self.btn_start = QPushButton('START')
        self.btn_stop = QPushButton('STOP')
        self.btn_about = QPushButton('About')
        self.progress = QProgressBar()
        self.cpu_percent = QProgressBar()
        self.lcd_count = QLCDNumber()
        self.elapsed_time= QLCDNumber()
        self.threads = []
        self.nstart = 0
        self.qval = 0
        self.compression = 0
        self.timer_cpu = QTimer()
        self.timer_elapsed = QTimer()
        self.start_time = QDateTime.currentDateTime().toPyDateTime()
        self.initUI()

    def initUI(self):
        # window title and geometry
        self.setWindowTitle(self.title)

        # button for the folder selection (ALAC)
        self.btn_lossless.setMinimumHeight(50)
        self.btn_lossless.move(50,10)
        self.btn_lossless.setToolTip('Folder of lossless files to convert')
        self.btn_lossless.clicked.connect(self.on_click_alac)

        # button for the folder selection (MP3)
        self.btn_lossy.setMinimumHeight(50)
        self.btn_lossy.move(50, 60)
        self.btn_lossy.setToolTip('Destination folder for the lossy files')
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
        logTextBox = QPlainTextEditLogger(self)
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

        # Elapsed time
        self.timer_elapsed.timeout.connect(self.showTIME)
        self.timer_elapsed.start(1000)

        # Progress
        self.progress.setToolTip('Conversion progress')

        # Format
        self.format.setToolTip("Choose the format compression")
        self.format.addItem('Format')
        self.format.addItems(['MP3', 'Ogg Vorbis', 'AAC', 'Opus'])
        self.format.currentIndexChanged['int'].connect(self.current_index_changed_format)

        # Quality
        combo_qual = QComboBox()
        combo_qual.setToolTip("Choose the compression quality ('Low' for a small file size only!)")
        combo_qual.addItem('Quality')
        combo_qual.addItems(['Low', 'Medium', 'High'])
        combo_qual.currentIndexChanged['int'].connect(self.current_index_changed_qual)

        #  Layout
        hlayout1 = QHBoxLayout()
        hlayout1.addWidget(combo)
        hlayout1.addWidget(self.cpu_percent)
        hlayout2 = QHBoxLayout()
        hlayout2.addWidget(self.btn_start)
        hlayout2.addWidget(self.btn_stop)
        vlayout = QVBoxLayout()
        vlayout.addWidget(self.elapsed_time)
        vlayout.addWidget(self.lcd_count)
        hlayout2.addLayout(vlayout)
        hlayout3 = QHBoxLayout()
        hlayout3.addWidget(self.btn_lossy)
        hlayout3.addWidget(self.format)
        hlayout3.addWidget(combo_qual)
        hlayout4 = QHBoxLayout()
        hlayout4.addWidget(self.progress)
        hlayout4.addWidget(self.btn_about)
        layout = QVBoxLayout()
        layout.addWidget(self.btn_lossless)
        layout.addLayout(hlayout3)
        layout.addLayout(hlayout1)
        layout.addLayout(hlayout2)
        layout.addWidget(logTextBox.widget)
        layout.addLayout(hlayout4)
        self.setLayout(layout)

        # show window
        self.show()

    @pyqtSlot()
    def on_click_alac(self):
        self.lossless_folder = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if os.name == 'nt': # Windows specific
            self.lossless_folder = self.lossless_folder.replace('/', '\\')
        logging.info('from ALAC folder:\n' + self.lossless_folder)
        if self.lossless_folder != '':
            self.btn_lossless.setToolTip(self.lossless_folder)

    @pyqtSlot()
    def on_click_mp3(self):
        self.lossy_location = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if os.name == 'nt':  # Windows specific
            self.lossy_location = self.lossy_location.replace('/', '\\')
        logging.info('to MP3 folder:\n' + self.lossy_location)
        if self.lossy_location != '':
            self.btn_lossy.setToolTip(self.lossy_location)

    @pyqtSlot()
    def call_info(self):
        QMessageBox.information(self, "Information", "<a href='https://github.com/fzao/pLACaudio'>pLACaudio v0.1</a> - License GNU GPL v3.0 - Copyright (c) 2019\n")

    @pyqtSlot(int)
    def current_index_changed(self, index):
        self.ncpu = index
        logging.info('Number of CPUs:\n' + str(self.ncpu))

    @pyqtSlot(int)
    def current_index_changed_qual(self, index):
        self.qval = index
        logging.info('Quality is set to:\n' + str(self.qval))

    @pyqtSlot(int)
    def current_index_changed_format(self, index):
        self.compression = index
        logging.info('Format is:\n' + str(self.compression))

    @pyqtSlot()
    def call_convert2lossy(self):
        # check the folders
        if not os.path.isdir(self.lossless_folder):
            logging.error('ALAC folder is not correctly set!')
            QMessageBox.warning(self, 'Warning', 'Folder of lossless files is not correctly set')
            return
        if not os.path.isdir(self.lossy_location):
            logging.error('MP3 folder is not correctly set!')
            QMessageBox.warning(self, 'Warning', 'Folder of lossy files is not correctly set')
            return
        # check the CPUs
        if self.ncpu < 1:
            logging.error('The number of CPUs is not defined!')
            QMessageBox.warning(self, 'Warning', 'The number of CPUs is not defined')
            return
        # check the Quality
        if self.qval < 1:
            logging.error('The quality compression is not chosen!')
            QMessageBox.warning(self, 'Warning', 'Choose the quality compression')
            return
        # start time
        self.start_time = QDateTime().currentDateTime().toPyDateTime()
        # get the list of all files to convert
        ext = 'm4a'
        audio_alac = glob.glob(self.lossless_folder + '/**/*.' + ext, recursive=True)
        ext = 'flac'
        audio_flac = glob.glob(self.lossless_folder + '/**/*.' + ext, recursive=True)
        ext = 'wav'
        audio_wav = glob.glob(self.lossless_folder + '/**/*.' + ext, recursive=True)
        ext = 'aif'
        audio_aiff1 = glob.glob(self.lossless_folder + '/**/*.' + ext, recursive=True)
        ext = 'aiff'
        audio_aiff2 = glob.glob(self.lossless_folder + '/**/*.' + ext, recursive=True)
        audio_aiff = audio_aiff1 + audio_aiff2
        audio_files = audio_alac + audio_flac + audio_wav + audio_aiff
        # Number of files found
        if len(audio_files) == 0:
            logging.error('No files found!')
            QMessageBox.warning(self, 'Warning', 'No lossless files found!')
            return
        else:
            logging.info('Number of ALAC files:\n' + str(len(audio_alac)))
            logging.info('Number of FLAC files:\n' + str(len(audio_flac)))
            logging.info('Number of WAV files:\n' + str(len(audio_wav)))
            logging.info('Number of AIFF files:\n' + str(len(audio_aiff)))
            logging.info('Total number of files:\n' + str(len(audio_files)))
        self.progress.setMinimum(0)
        self.progress.setMaximum(len(audio_files) - 1)
        self.progress.setValue(0)
        self.lcd_count.display(len(audio_files))
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
            self.threads.append(mp3Thread(audio[i], self.lossless_folder, self.lossy_location, self.qval, self.compression))
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
            QMessageBox.information(self, "Done!", "Lossy conversion done!")
            self.progress.setValue(0)
            self.lcd_count.display(0)
            self.elapsed_time.display('%03d:%02d:%02d' % (0, 0, 0))

    def update_progress_bar(self):
        self.progress.setValue(self.progress.value() + 1)
        self.lcd_count.display(self.lcd_count.value() - 1)

    def showCPU(self):
        cpu_load = psutil.cpu_percent()
        if cpu_load < 50.:
            self.cpu_percent.setStyleSheet(safe)
        elif cpu_load < 80.:
            self.cpu_percent.setStyleSheet(inter)
        else:
            self.cpu_percent.setStyleSheet(danger)
        self.cpu_percent.setValue(cpu_load)

    def showTIME(self):
        if self.nstart > 0:
            now = QDateTime().currentDateTime().toPyDateTime()
            diff = now - self.start_time
            totsec = diff.total_seconds()
            h = int(totsec // 3600)
            m = int((totsec % 3600) // 60)
            sec = int((totsec % 3600) % 60)
            self.elapsed_time.display('%03d:%02d:%02d'%(h, m, sec))


if __name__ == '__main__':
    danger = "QProgressBar::chunk { background-color: #FF3633;}"
    inter = "QProgressBar::chunk { background-color: #FFAF33;}"
    safe = "QProgressBar::chunk {background-color: #61FF33;}"
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
