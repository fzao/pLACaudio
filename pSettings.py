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


def ChangeStyle(self, theme=0):
    if theme == 0:  # default
        self.setStyleSheet('')
    elif theme == 1:  # dark
        self.setStyleSheet('QWidget { background-color: #2C2F33; color: #B2B2B2; selection-color: #B2B2B2; selection-background-color: #787878 }')
    elif theme == 2:  # gray
        self.setStyleSheet('QWidget { background-color: #BCBCBE; color: #3E4444; selection-color: #3E4444; selection-background-color: #B2B2B2 } }')
    elif theme == 3:  # rustic
        self.setStyleSheet('QWidget { background-color: #563F46; color: #E0E2E4; selection-color: #E0E2E4; selection-background-color: #8CA3A3 }')
    elif theme == 4:  # sky
        self.setStyleSheet('QWidget { background-color: #8D9DB6; color: #DAEBE8; selection-color: #DAEBE8; selection-background-color: #667292 }')
    elif theme == 5:  # sand
        self.setStyleSheet('QWidget { background-color: #FFF2DF; color: #674D3C; selection-color: #674D3C; selection-background-color: #F4A688 }')
    elif theme == 6:  # flower
        self.setStyleSheet('QWidget { background-color: #EEAC99; color: #622569; selection-color: #622569; selection-background-color: #C83349 }')
    elif theme == 7:  # beach
        self.setStyleSheet('QWidget { background-color: #588C7E; color: #F2AE72; selection-color: #588C7E; selection-background-color: #96CEB4 }')
    else:
        self.setStyleSheet('')
    # save settings
    self.settings.setValue('theme', theme)


def ShowLogger(self, log=1):
    if log == 1:
        self.grp_log.setVisible(True)
    else:
        self.grp_log.setVisible(False)
    # save settings
    self.settings.setValue('logger', log)
