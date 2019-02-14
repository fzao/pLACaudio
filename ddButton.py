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
import os
import logging
from listFiles import listofFiles
from PyQt5.QtWidgets import QPushButton


class DDButtonFrom(QPushButton):
    def __init__(self, parent):
        super(DDButtonFrom, self).__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super(DDButtonFrom, self).dragEnterEvent(event)

    def dragMoveEvent(self, event):
        super(DDButtonFrom, self).dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if os.path.isdir(url.toLocalFile()):
                    self.parent().parent().lossless_folder = url.toLocalFile()
                    logging.info('from folder: ' + self.parent().parent().lossless_folder)
                    # get the list of all files to convert
                    listofFiles(self.parent().parent())
            event.acceptProposedAction()
        else:
            super(DDButtonFrom,self).dropEvent(event)


class DDButtonTo(QPushButton):
    def __init__(self, parent):
        super(DDButtonTo, self).__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super(DDButtonTo, self).dragEnterEvent(event)

    def dragMoveEvent(self, event):
        super(DDButtonTo, self).dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if os.path.isdir(url.toLocalFile()):
                    self.parent().parent().lossy_location = url.toLocalFile()
                    logging.info('to folder: ' + self.parent().parent().lossy_location)
            event.acceptProposedAction()
        else:
            super(DDButtonTo,self).dropEvent(event)