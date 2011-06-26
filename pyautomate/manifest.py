# Python 3 version of taking a 0install manifest digest
# http://0install.net/2007/interfaces/ZeroInstall.xml

import os, stat
import hashlib
from digest import digest

class _ManifestAlgorithm(object):
    new_digest = None           # Constructor for digest objects

    def __init__(self, name):
        self.new_digest = getattr(hashlib, name)
        self.name = name

    def generate_manifest(self, root):
        def recurse(subdir):
            # To ensure that a line-by-line comparison of the manifests
            # is possible, we require that filenames don't contain newlines.
            # Otherwise, you can name a file so that the part after the \n
            # would be interpreted as another line in the manifest.
            if '\n' in subdir: raise Exception("Newline in filename '%s'" %
                                               subdir)
            assert subdir.startswith('/')

            full = os.path.join(root, subdir[1:])
            
            if not os.path.isdir(full): 
                raise Exception('Not a directory: "%s"' % full)

            if subdir != '/':
                yield "D %s" % subdir

            items = os.listdir(full)
            items.sort()
            dirs = []
            for item in items:
                path = os.path.join(root, subdir[1:], item)
                info = os.lstat(path)
                m = info.st_mode

                new_digest = self.new_digest

                if stat.S_ISREG(m):
                    d = digest(path, new_digest)
                    if m & 0o111:
                        yield "X %s %s %s" % (d, info.st_size, item)
                    else:
                        yield "F %s %s %s" % (d, info.st_size, item)
                elif stat.S_ISLNK(m):
                    target = os.readlink(path)
                    d = new_digest(target).hexdigest()
                    # Note: Can't use utime on symlinks, so skip mtime
                    # Note: eCryptfs may report length as zero, so count ourselves instead
                    yield "S %s %s %s" % (d, len(target), item)
                elif stat.S_ISDIR(m):
                    dirs.append(item)
                else:
                    raise Exception("Unknown object '%s' (not a file, directory or symlink)" %
                            path)

            if not subdir.endswith('/'):
                subdir += '/'
            for x in dirs:
                # Note: "subdir" is always Unix style. Don't use os.path.join here.
                for y in recurse(subdir + x): yield y
            return

        for x in recurse('/'): yield x

    def getID(self, digest):
        return self.name + '=' + digest.hexdigest()

    def get_digest(self, dir):
        digest = self.new_digest()
        for line in self.generate_manifest(dir):
            digest.update(line.encode('UTF-8') + b'\n')
        return digest

_manifest_alg = _ManifestAlgorithm('sha256')

def manifest_digest(directory_path):
    return _manifest_alg.getID(_manifest_alg.get_digest(directory_path))

