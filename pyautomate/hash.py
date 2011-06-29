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
from pyautomate.manifest import generate_manifest
from pyautomate.helpers import files_exist

def hash(*files, alg_name='sha256'):
    alg = getattr(hashlib, alg_name)
    if not files or not files_exist(*files):
        return None

    if len(files) == 1:
        digest = hash_one(files[0], alg)
    else:
        digest = alg()
        for file in files:
            digest.update(hash_one(file, alg))
        digest = digest.hexdigest()
    return alg_name + '=' + digest

def hash_one(path, alg):
    # Note: path must exist
    if os.path.isdir(path):
        return hash_directory(path, alg)
    else:
        return hash_file(path, alg)

def hash_file(path, alg):
    block_size = 128 * 63
    with open(path,'rb') as f: 
        chunks = iter(lambda: f.read(block_size), b'')
        return hash_iterable(chunks, alg)

def hash_directory(path, alg):
    lines = ((line + '\n').encode('UTF-8') 
            for line in generate_manifest(path, alg))
    return hash_iterable(lines, alg)

def hash_iterable(iterable, alg):
    digest = alg()
    for chunk in iterable:
        digest.update(chunk)
    return digest.hexdigest()

