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
        def recurse(sub):
            # To ensure that a line-by-line comparison of the manifests
            # is possible, we require that filenames don't contain newlines.
            # Otherwise, you can name a file so that the part after the \n
            # would be interpreted as another line in the manifest.
            if '\n' in sub: raise Exception("Newline in filename '%s'" % sub)
            assert sub.startswith('/')

            full = os.path.join(root, sub[1:])
            info = os.lstat(full)
            new_digest = self.new_digest
            
            m = info.st_mode
            if not stat.S_ISDIR(m): raise Exception('Not a directory: "%s"' % full)
            if sub != '/':
                yield "D %s" % sub
            items = os.listdir(full)
            items.sort()
            dirs = []
            for leaf in items:
                path = os.path.join(root, sub[1:], leaf)
                info = os.lstat(path)
                m = info.st_mode

                if stat.S_ISREG(m):
                    if leaf == '.manifest': continue

                    d = digest(path, new_digest)
                    if m & 0o111:
                        yield "X %s %s %s %s" % (d, int(info.st_mtime), info.st_size, leaf)
                    else:
                        yield "F %s %s %s %s" % (d, int(info.st_mtime), info.st_size, leaf)
                elif stat.S_ISLNK(m):
                    target = os.readlink(path)
                    d = new_digest(target).hexdigest()
                    # Note: Can't use utime on symlinks, so skip mtime
                    # Note: eCryptfs may report length as zero, so count ourselves instead
                    yield "S %s %s %s" % (d, len(target), leaf)
                elif stat.S_ISDIR(m):
                    dirs.append(leaf)
                else:
                    raise Exception("Unknown object '%s' (not a file, directory or symlink)" %
                            path)

            if not sub.endswith('/'):
                sub += '/'
            for x in dirs:
                # Note: "sub" is always Unix style. Don't use os.path.join here.
                for y in recurse(sub + x): yield y
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


