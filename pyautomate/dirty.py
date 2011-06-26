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

import hashlib
from os.path import abspath

from pyautomate.application import application

def has_changed(key, value):
    '''
    checks if given value is different from persisted[key]
    '''
    return key not in application.persisted_data or application.persisted_data[key] != value

def has_file_changed(path):
    '''
    checks path to file/directory for changes, see also mark_file_current.
    '''
    return has_changed('#' + path, _hash(path))

def mark_file_current(path):

    '''
    Mark a directory or file current/unchanged. See also, has_changed(path).

    Note this also works for files which do not exist. In that case,
    has_changed(path) would return True if the file exists next time.

    path: path to directory or file.
    '''
    application.persisted_data['#' + path] = _hash(path)

def _hash(path):
    path = abspath(path)
    #if file...
    return _md5(path)

def _md5(file_path):
    '''return md5 digest of file'''
    try:
        block_size = 128 * 63
        md5 = hashlib.md5()
        with open(file_path,'rb') as f: 
            for chunk in iter(lambda: f.read(block_size), b''): 
                 md5.update(chunk)
        return md5.hexdigest()
    except IOError:
        return None

