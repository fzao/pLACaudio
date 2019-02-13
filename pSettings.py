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
import qdarkstyle


def ChangeStyle(self, theme=0):
    if theme == 0:  # default
        self.setStyleSheet('')
    elif theme == 1:  # dark
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    # save settings
    self.settings.setValue('theme', theme)


def ShowLogger(self, log=1):
    if log == 1:
        self.grp_log.setVisible(True)
    else:
        self.grp_log.setVisible(False)
    self.app.processEvents()
    if self.grp_log.isVisible():
        self.resize(480, 640)
    else:
        self.resize(480, 440)
    # save settings
    self.settings.setValue('logger', log)
