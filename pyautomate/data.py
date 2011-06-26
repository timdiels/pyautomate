# Copyright 2011 Tim Diels <limyreth@gmail.com>
#
# This file is part of pyautomate.
# 
# pyautomate is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# pyautomate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with pyautomate.  If not, see <http://www.gnu.org/licenses/>.

import os.path
import yaml

class Data(dict):

    def __init__(self):
        dict.__init__(self)
        try:
            with self._open('r') as f:
                self.update(yaml.load(f))
        except IOError:
            self.update({
                'last_state' : {}
            })

        self._committed = {}
        self.commit()

        import pyautomate
        pyautomate.persisted = self['last_state']

    def _open(self, access):
        return open(os.path.abspath('.pyautomate'), access)

    def save(self):
        with self._open('w') as f:
            yaml.dump(self._committed, f)

    def commit(self):
        self._committed['last_state'] = self['last_state'].copy()

