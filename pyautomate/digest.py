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
import os.path
from os.path import abspath
from pyautomate.manifest import generate_manifest

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

def hash_file(path):
    path = abspath(path)
    if not os.path.exists(path):
        return None
    elif os.path.isdir(path):
        return hash_directory(path)
    else:
        return md5(path)

def hash(*files):
    if len(files) == 1:
        return hash_file(files[0])

    alg = hashlib.md5()
    for file in files:
        alg.update(hash_file(file))
    return alg.hexdigest()

def hash_directory(dir):
    alg = hashlib.sha256()
    for line in generate_manifest(dir):
        alg.update((line + '\n').encode('UTF-8'))
    return alg.hexdigest()

