Py Search Duplicates [2.1]
==========================
A Python2 script to search all duplicates files into a given directory recursively under MIT [license](./LICENSE).
It hash each files with the CRC32 (or MD5 if asked by using the "--md5" argument)
hash digest algorithm to compare each file and find which already exist after having classed the files by size.

Notice:
-------
__Python2.6__ or higher is recommended but Python3 is highly __unrecommended__ even if this one is half-supported.

Usage:
--------------
usage: search.py [-h] [-p PATH] [-r RESULTS_PATH] [-b] [--md5]

Arguments:
```
  -p PATH, --path PATH  The path where search duplicated files.
  -r RESULTS_PATH, --results RESULTS_PATH
                        The file path where write the results displayed if you
                        want save it.
  -b, --binary          If you want an estimation in binary mode (KiB, MiB,
                        GiB, etc.) instead of the default in decimal (KB, MB,
                        GB, etc.).
  --md5                 Using the MD5 hash digest (slower) instead of the
                        CRC32.
```

Examples:
---------
```bash
python2 search.py -p ~/musics -r /tmp/results.txt
```
It wills search duplicates on your "musics" folder of your home and save the results
if there are duplicates into "/tmp/results.txt".

```bash
python2 search.py --path /home/user/documents --md5 --binary
```
It wills search duplicates into "/home/user/documents",
displaying the total size to check in binary mode (KiB, MiB, GiB, ...) and hashing in MD5 (slower).

Miscellaneous information:
--------------------------
This Python script was developed on Python 2.7.9 on Linux-2 with ArchLinux.

If you have any suggestion, improvement, issue or others don't hesitate to ask or make a pull request!
We will be delighted to read it and response you!
