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


def ChangeStyle(self, dark=0):
    if dark ==1:
        # window theme
        self.setStyleSheet(
            'QWidget { background-color: #2C2F33 ; color: #D9D9D9; selection-color: #D9D9D9; selection-background-color: #2C2F33}')
        # cpu color bar
        self.danger = "QProgressBar::chunk { background-color: #B90000;}"
        self.inter = "QProgressBar::chunk { background-color: #B97F00;}"
        self.safe = "QProgressBar::chunk {background-color: #6D9200;}"
    else:
        # window theme
        self.setStyleSheet('')
        # cpu color bar
        self.danger = "QProgressBar::chunk { background-color: #FF3633;}"
        self.inter = "QProgressBar::chunk { background-color: #FFAF33;}"
        self.safe = "QProgressBar::chunk {background-color: #61FF33;}"
    # save settings
    self.settings.setValue('dark', dark)

