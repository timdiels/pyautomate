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

def digest(file_path, alg):
    block_size = 128 * 63
    alg = alg()
    with open(file_path,'rb') as f: 
        for chunk in iter(lambda: f.read(block_size), b''): 
             alg.update(chunk)
    return alg.hexdigest()

def md5(file_path):
    '''return md5 digest of file'''
    return digest(file_path, hashlib.md5)

