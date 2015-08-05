# -*- coding: utf-8 -*-
from __future__ import division
from os import walk
from os.path import abspath, join, getsize
from hashlib import md5 as hashmd5
from sys import version_info
from zlib import crc32


class AnalysingFiles:
    def __init__(self, md5=False):
        """
        Initialize this instance before proceeding to the analyzes.
        :param md5: Hashing using the MD5 hash digest (`True`) or by using the CRC32.
            :type md5 bool:
        :return:
        """
        self.stats = dict(directories=0, files=0, size=0)
        if md5:
            self.get_hash_file = self.get_md5_hash_file
        else:
            self.get_hash_file = self.get_crc32_hash_file
        self.files = dict()

    def browse(self, path):
        """
        Browses the given directory and counts the number of directories and by the same way.
        :param path:
            :type path str:
        :return:
        """
        for root, dirs, files in walk(path):
            self.stats['directories'] += len(dirs)
            self.stats['files'] += len(files)
            for name in files:
                try:
                    file_path = abspath(join(root, name))
                    file_size = getsize(file_path)

                    # if not already contain the size as key, we create a new list into containing the path
                    # else we append the path
                    self.files[file_size] = [file_path] if not self.files.get(file_size) else \
                        self.files[file_size] + [file_path]

                    # we return the file analysed and it size if the application want to know what is going on
                    yield True, {'path': path, 'size': file_size}

                    self.stats['size'] += file_size  # we add the new size into the total size of the statistics
                except OSError as e:
                    yield False, e  # there is an error! We return `False` and the error everything in a tuple

    def analysing(self, progress_bar_obj):
        """
        Sorts the files by size and regroups into a dictionary using the size in bytes as key and a list inside
        containing the paths to these files before calculating the hashes and comparing each others.
        And, finally, returns the hashes as key with inside, the paths of the duplicates.
        :param progress_bar_obj: An instance of the package `progressbar`'s object `ProgressBar`.
        :return:
        """
        possible_duplicates = list()
        hashes = dict()
        # sorts files by size
        files_appended = 0

        # removing alone paths
        for size, paths in self.files.items():
            length = len(paths)
            if length > 1:
                possible_duplicates += paths  # adding the paths with the same size into the `possible_duplicates` list
                files_appended += length
        del self.files  # liberating unnecessary memory used before hashing

        files_number = 0
        # getting sizes and hashing the files with the same size
        for path in possible_duplicates:
            hash_ = self.get_hash_file(path)
            if hash_:  # if the hashing as not occurred an error
                # if the hash calculated not already exists we create a new list containing the path
                # with the hash as key
                # else, we add the file into the list of the key (hash)
                hashes[hash_] = [path] if not hashes.get(hash_) else hashes[hash_] + [path]
            files_number += 1
            percentage = ((files_number / files_appended) * 100)
            progress_bar_obj.update(percentage if percentage <= 100 else 100)

        del possible_duplicates
        if version_info.major > 2:
            hashes_ = hashes.copy()
            for h in hashes.keys():
                if len(hashes[h]) < 2:
                    del hashes_[h]
        else:
            for h in hashes.keys():
                if len(hashes[h]) < 2:
                    del hashes[h]
        return hashes

    @staticmethod
    def get_md5_hash_file(path):
        """
        Returns the MD5 hash digest of a file.
        :param path:
        :type path str:
        :return:
        """
        md5 = hashmd5()
        try:
            with open(path, 'rb') as fd:
                while 1:
                    data = fd.read(2**9)
                    if not data:
                        break
                    md5.update(data)
        except IOError:
            return False
        return md5.hexdigest()

    @staticmethod
    def get_crc32_hash_file(path):
        """
        Returns the CRC32 hash digest of a file.
        :param path:
        :type path str:
        :return:
        """
        try:
            with open(path, 'rb') as fd:
                r = 0
                while 1:
                    data = fd.read(2**9)
                    r = crc32(data, r)
                    if not data:
                        return "%8X" % (r & 0xFFFFFFFF)
        except IOError:
            return False
