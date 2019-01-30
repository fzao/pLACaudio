"""
parallel conversion of a large library of lossless audio files (ALAC & FLAC) to lossy MP3

 ________  ___       ________  ________
|\   __  \|\  \     |\   __  \|\   ____\
\ \  \|\  \ \  \    \ \  \|\  \ \  \___|
 \ \   ____\ \  \    \ \   __  \ \  \
  \ \  \___|\ \  \____\ \  \ \  \ \  \____
   \ \__\    \ \_______\ \__\ \__\ \_______\
    \|__|     \|_______|\|__|\|__|\|_______|

Copyright (c) Fabrice Zaoui

Licence GNU GPL v3

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

    def __init__(self, audio_files, alac_flac_location, mp3_location, qvalue):
        QThread.__init__(self)
        self.audio_files = audio_files
        self.alac_flac_location = alac_flac_location
        self.mp3_location = mp3_location
        self.qval = qvalue
        self.sep = '/'
        self.null = '/dev/null'
        if os.name == 'nt':
            self.sep = '\\'
            self.null = 'NUL'

    def __del__(self):
        self.wait()

    def convert2mp3(self, audio_file_in, qval):
        path_audio = os.path.dirname(audio_file_in)
        file_name = os.path.splitext(os.path.basename(audio_file_in))[0]
        len_indir = len(self.alac_flac_location)
        path_audio = path_audio[len_indir:]
        path_audio = self.mp3_location + path_audio
        if not os.path.isdir(path_audio):
            try:
                os.makedirs(path_audio)
            except OSError:
                # logging.exception('Unable to create the destination folder')
                pass
        ext = 'mp3'
        audio_file = file_name + '.' + ext
        audio_file_out = path_audio + self.sep + audio_file
        qval = str(self.qval)
        if not os.path.isfile(audio_file_out):
                subprocess.call('ffmpeg -nostats -loglevel 0 -i '
                      + '"' + audio_file_in + '"'
                      + ' -vn -acodec libmp3lame -q:a '+ qval + ' -map_metadata 0'
                      + ' -id3v2_version 3 '
                      + '"' + audio_file_out + '"' + ' > ' + self.null,
                            shell=True)

    def run(self):
        for audio_file_in in self.audio_files:
            self.convert2mp3(audio_file_in, self.qval)
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
        self.title = 'pLAC'
        self.setWindowIcon(QIcon('./icon/beer.ico'))
        self.setFixedSize(480, 640)
        self.alac_flac_location = ''
        self.mp3_location = ''
        self.ncpu = 0
        self.btn_alac = QPushButton('ALAC / FLAC')
        self.btn_mp3 = QPushButton('MP3')
        self.quality = QSlider(Qt.Horizontal)
        self.btn_start = QPushButton('START')
        self.btn_stop = QPushButton('STOP')
        self.progress = QProgressBar()
        self.cpu_percent = QProgressBar()
        self.lcd_count = QLCDNumber()
        self.elapsed_time= QLCDNumber()
        self.threads = []
        self.nstart = 0
        self.qval = 0
        self.timer_cpu = QTimer()
        self.timer_elapsed = QTimer()
        self.start_time = QDateTime.currentDateTime().toPyDateTime()
        self.initUI()

    def initUI(self):
        # window title and geometry
        self.setWindowTitle(self.title)

        # button for the folder selection (ALAC)
        self.btn_alac.setMinimumWidth(300)
        self.btn_alac.setMinimumHeight(50)
        self.btn_alac.move(50,10)
        self.btn_alac.setToolTip('ALAC or FLAC files to convert')
        self.btn_alac.clicked.connect(self.on_click_alac)

        # button for the folder selection (MP3)
        self.btn_mp3.setMinimumWidth(300)
        self.btn_mp3.setMinimumHeight(50)
        self.btn_mp3.move(50, 60)
        self.btn_mp3.setToolTip('MP3 destination folder')
        self.btn_mp3.clicked.connect(self.on_click_mp3)

        # buttons for starting and stopping
        self.btn_start.setMinimumHeight(100)
        self.btn_start.setToolTip('Start conversion')
        self.btn_start.setIcon(QIcon(QApplication.style().standardIcon(QStyle.SP_MediaPlay)))
        self.btn_start.clicked.connect(self.call_convert2mp3)
        self.btn_stop.setMinimumHeight(100)
        self.btn_stop.setEnabled(False)
        self.btn_stop.setToolTip('Stop conversion')
        self.btn_stop.setIcon(QIcon(QApplication.style().standardIcon(QStyle.SP_MediaStop)))

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

        # Quality
        self.quality.setToolTip('Choose between best MP3 quality (0-left) and size (9-right)')
        self.quality.setMinimum(0)
        self.quality.setMaximum(9)
        self.quality.setSingleStep(1)
        self.quality.setValue(5)
        self.qval = 5
        self.quality.valueChanged.connect(self.updateQuality)

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
        hlayout3.addWidget(self.btn_mp3)
        hlayout3.addWidget(self.quality)
        layout = QVBoxLayout()
        layout.addWidget(self.btn_alac)
        layout.addLayout(hlayout3)
        layout.addLayout(hlayout1)
        layout.addLayout(hlayout2)
        layout.addWidget(logTextBox.widget)
        layout.addWidget(self.progress)
        self.setLayout(layout)

        # show window
        self.show()

    @pyqtSlot()
    def on_click_alac(self):
        self.alac_flac_location = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if os.name == 'nt': # Windows specific
            self.alac_flac_location = self.alac_flac_location.replace('/', '\\')
        logging.info('from ALAC folder:\n' + self.alac_flac_location)
        if self.alac_flac_location != '':
            self.btn_alac.setToolTip(self.alac_flac_location)

    @pyqtSlot()
    def on_click_mp3(self):
        self.mp3_location = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if os.name == 'nt':  # Windows specific
            self.mp3_location = self.mp3_location.replace('/', '\\')
        logging.info('to MP3 folder:\n' + self.mp3_location)
        if self.mp3_location != '':
            self.btn_mp3.setToolTip(self.mp3_location)

    @pyqtSlot(int)
    def current_index_changed(self, index):
        self.ncpu = index
        logging.info('Number of CPUs:\n' + str(self.ncpu))

    @pyqtSlot()
    def call_convert2mp3(self):
        # check the folders
        if not os.path.isdir(self.alac_flac_location):
            logging.error('ALAC folder is not correctly set!')
            QMessageBox.warning(self, 'Warning', 'ALAC/FLAC folder is not correctly set!')
            return
        if not os.path.isdir(self.mp3_location):
            logging.error('MP3 folder is not correctly set!')
            QMessageBox.warning(self, 'Warning', 'MP3 folder is not correctly set!')
            return
        # check the CPUs
        if self.ncpu < 1:
            logging.error('The number of CPUs is not defined!')
            QMessageBox.warning(self, 'Warning', 'The number of CPUs is not defined!')
            return
        # start time
        self.start_time = QDateTime().currentDateTime().toPyDateTime()
        # get the list of all files to convert
        ext = 'm4a'
        audio_alac = glob.glob(self.alac_flac_location + '/**/*.' + ext, recursive=True)
        ext = 'flac'
        audio_flac = glob.glob(self.alac_flac_location + '/**/*.' + ext, recursive=True)
        audio_files = audio_alac + audio_flac
        # Number of files found
        if len(audio_files) == 0:
            logging.error('No files found!')
            QMessageBox.warning(self, 'Warning', 'No ALAC or FLAC files found!')
            return
        else:
            logging.info('Number of files:\n' + str(len(audio_files)))
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
            self.threads.append(mp3Thread(audio[i], self.alac_flac_location, self.mp3_location, self.qval))
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
            QMessageBox.information(self, "Done!", "MP3 conversion done!")
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

    def updateQuality(self):
        self.qval = self.quality.value()


if __name__ == '__main__':
    danger = "QProgressBar::chunk { background-color: #FF3633;}"
    inter = "QProgressBar::chunk { background-color: #FFAF33;}"
    safe = "QProgressBar::chunk {background-color: #61FF33;}"
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
