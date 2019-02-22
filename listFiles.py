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

import glob
import logging
from PyQt5.QtWidgets import QMessageBox


def listofFiles(self):
    self.audio_files = []
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
    self.audio_files = audio_alac + audio_flac + audio_dsf + audio_wav + audio_aiff
    if len(self.audio_files) == 0:
        logging.error('No files found!')
        QMessageBox.warning(self, 'Warning', 'No lossless files found!')
        return
    else:
        logging.info('Number of ALAC files: ' + str(len(audio_alac)))
        logging.info('Number of FLAC files: ' + str(len(audio_flac)))
        logging.info('Number of DSF files: ' + str(len(audio_dsf)))
        logging.info('Number of WAV files: ' + str(len(audio_wav)))
        logging.info('Number of AIFF files: ' + str(len(audio_aiff)))
        logging.info('Total number of files: ' + str(len(self.audio_files)))
    self.progress.setMinimum(0)
    self.progress.setMaximum(len(self.audio_files) - 1)
    self.progress.setValue(0)
    self.lcd_count.display(len(self.audio_files))
    self.nm1 = len(self.audio_files)
    self.n0 = len(self.audio_files)

