#!/usr/bin/env python

import os
from osfs import OSFS
import tempfile

from fs.errors import *

class TempFS(OSFS):

    """Create a Filesystem in a tempory directory (with tempfile.mkdtemp),
    and removes it when the TempFS object is cleaned up."""

    def __init__(self, identifier=None, temp_dir=None, dir_mode=0700, thread_synchronize=True):
        """Creates a temporary Filesystem

        identifier -- A string that is included in the name of the temporary directory,
        default uses "TempFS"

        """
        self._temp_dir = tempfile.mkdtemp(identifier or "TempFS",dir=temp_dir)
        self._cleaned = False
        OSFS.__init__(self, self._temp_dir, dir_mode=dir_mode, thread_synchronize=thread_synchronize)

    def __str__(self):
        return '<TempFS: %s>' % self._temp_dir

    __repr__ = __str__

    def __unicode__(self):
        return unicode(self.__str__())

    @convert_os_errors
    def close(self):
        """Removes the temporary directory.
        This will be called automatically when the object is cleaned up by
        Python. Note that once this method has been called, the FS object may
        no longer be used.
        """
        if not self._cleaned and self.exists("/"):
            self._lock.acquire()
            try:
                # shutil.rmtree doesn't handle long paths on win32,
                # so we walk the tree by hand.
                entries = os.walk(self.root_path,topdown=False)
                for (dir,dirnames,filenames) in entries:
                    for filename in filenames:
                        os.remove(os.path.join(dir,filename))
                    for dirname in dirnames:
                        os.rmdir(os.path.join(dir,dirname))
                os.rmdir(self.root_path)
                self._cleaned = True
            finally:
                self._lock.release()
        super(TempFS,self).close()


