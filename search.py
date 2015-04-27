# -*- coding: utf-8 -*-
from __future__ import print_function
from argparse import ArgumentParser
from sys import version_info, stdout
from os import name as os_name, system
from os.path import isdir, expanduser
from AnalysingFiles import AnalysingFiles
from random import randint
from progressbar import ProgressBar, Percentage, Bar, ETA
from time import time, strftime, gmtime
input_ = raw_input if not version_info.major > 2 else input


def main():
    """
    Sets the `ArgumentParser`, manage the arguments and prompt to fix the invalid arguments (paths).
    Before calling and starting the `run_analyze`.
    :return:
    """
    parser = ArgumentParser(prog='search.py')
    parser.add_argument('-p', '--path', dest='path', metavar="DIRECTORY",
                        help='The path where search duplicated files.')
    parser.add_argument('-r', '--results', dest='results_path',
                        help='The file path where write the results displayed if you want save it.')
    parser.add_argument('-b', '--binary', dest='binary_mode', action='store_true', default=False,
                        help='If you want an estimation in binary mode (KiB, MiB, GiB, etc.) '
                             'instead of the default in decimal (KB, MB, GB, etc.).')
    parser.add_argument('--md5', dest='md5', action='store_true', default=False,
                        help='Using the MD5 hash digest (slower) instead of the CRC32.')
    args = parser.parse_args()

    # checks if the path to scan is entered or if it is a dir.
    args.path = translating_path(args.path)
    if not args.path or not isdir(args.path):
        args.path = translating_path(input_('Please enter a valid path to scan: '))
        while not isdir(args.path):  # prompt the user to enter a valid path
            print('[ERROR] "%s" is an invalid path.\n' % args.path)
            args.path = translating_path(input_('Please enter a valid path to scan: '))

    # if results_path is not None and is
    if args.results_path:
        valid = is_invalid_path(args.results_path)
        while valid:
            print('Invalid path: %s' % valid[1])
            args.results_path = translating_path(input_('Please enter a valid results path '
                                                        '(or let blank to display the results on the screen): '))
            if not args.results_path:
                break
            valid = is_invalid_path(args.results_path)
    run_analyze(path=args.path, results_path=args.results_path, binary_mode=args.binary_mode, md5=args.md5)


def run_analyze(path, results_path, binary_mode, md5):
    """
    Clears the screen using the system command `clear` on POSIX, `cls` for NT or new blank lines.
    This function runs `AnalysingFiles` which will create a SQLite database into a temporary folder
    to sort the browsed files on the given path by ascending size. After that, `AnalysingFiles.analysing`, regroups
    each files with the same number of bytes before hashing them using the CRC32 or the MD5 (slower) hash digests
    if they have the same size.
    And finally, we print or export the results.

    :param path:
        :type path str:
    :param results_path:
        :type results_path str:
    :param binary_mode:
        :type binary_mode bool:
    :param md5:
        :type md5 bool:
    :return:
    """
    # Clearing the terminal
    if os_name == 'posix':
        system('clear')
    elif os_name == 'nt':
        system('cls')
    else:
        print('\n' * 100)

    t0 = time()  # initial time

    # Initializing the instance of `SortFiles` and creating/ dropping the SQLite database.
    analyze = AnalysingFiles(md5=md5)

    print('\nStep 1 of 3 - Estimating and preparing the analyze\n====')
    browsing = analyze.browse(path)
    chars = ['.', 'o', 'O', '@', '*', ' ']
    print('Progressing... [.]', end='')
    ts = time() + 0.3
    while 1:
        if ts < time():
            print('\b\b', end='')
            stdout.flush()
            print('%s]' % chars[randint(0, len(chars) - 1)], end='')
            ts = time() + 0.3
        try:
            next(browsing)
        except StopIteration:
            break
    del browsing
    print('\b'*18, end='')  # removing "Progressing... [.]"
    stdout.flush()
    converted_size = convert(analyze.stats['size'], binary_mode)
    print(
        """\
At %(date)s, we had: %(number_files)d files in %(number_directories)d directories for %(total_size)s bytes\
%(converted_size)s.
We will begin to scan "%(path)s", please avoid to change files may to distort final results and the above estimates.

The results will be displayed bellow after all was done.
""" % {
            'date': strftime("%H:%M:%S", gmtime()), 'number_files': analyze.stats['files'],
            'number_directories': analyze.stats['directories'], 'total_size': analyze.stats['size'],
            'converted_size': (converted_size and ' whether about {0}'.format(converted_size) or ''),
            'path': path,
        }
    )

    print('\nStep 2 of 3 - Analysing and hashing files\n====')
    bar = ProgressBar(widgets=[Percentage(), ' ', Bar(marker='#', left='[', right=']'), ' ', ETA()], maxval=100)
    bar.start()
    r = analyze.analysing(bar)
    bar.finish()

    t0 = time() - t0  # final time - initial time

    print('\n\nStep 3 of 3 - Exporting results\n====')
    print('Done in %d minutes and %d seconds!' % (int(t0/60), t0 - int(t0/60) * 60))
    if len(r) == 0:
        print('Good job! No duplicates found! o(^o^)O')
    else:
        if not results_path:
            if len(r) > 15:
                if input_('Too many results to display! '
                          'Do you want to export the results in a file instead? [y/n] ') != 'n':
                    p = translating_path(input_('Please enter a path: '))
                    valid = is_invalid_path(p)
                    while valid:
                        print('Invalid path: %s' % valid[1])
                        p = translating_path(input_('Please enter a valid results path: '))
                        valid = is_invalid_path(p)
                    export_results(p, r)
                    print('The results have been exported to "%s"!' % p)
                else:
                    print_results(r)
            else:
                print_results(r)
        else:
            export_results(results_path, r)
            print('The results have been exported to "%s"!' % results_path)
    if os_name == 'nt':
        input_('Push [ENTER] to quit... ')


def translating_path(path):
    if path and path[:1] == '~' and os_name == 'posix':
        return expanduser('~') + path[1:]
    return path


def is_invalid_path(path):
    """
    Checks if the path is valid and writable using open() and returns False if the path is valid.
    :param path:
    :return:
    """
    try:
        open(path, 'w+').close()
        return False
    except (OSError, IOError) as e:
        print('[ERROR] The results path "%s" is invalid path or not writable. (%s)\n' % (path, e))
        return True, e


def convert(block, binary=False):
    """
    It choose between an unit (KB, MB, GB or TB) according with the bytes block given either in binary mode (1024) or
    decimal mode (10^2).

    :param block: An integer in bytes.
    :param binary: A boolean to activate or not the binary mode.
    :return: The new value with the unit at the end of the string or False if it stay in bytes.
    """
    if not binary:
        if 10**3 <= block < 10**6:
            return '%s KB' % (block / 10**3)
        elif 10**6 <= block < 10**9:
            return '%s MB' % (block / 10**6)
        elif 10**9 <= block < 10**12:
            return '%s GB' % (block / 10**9)
        elif block >= 10**12:
            return '%s TB' % (block / 10**12)
        else:
            return False
    else:
        if 2**10 <= block < 2**20:
            return '%s KiB' % (block / 2**10)
        elif 2**20 <= block < 2**30:
            return '%s MiB' % (block / 2**20)
        elif 2**30 <= block < 2**40:
            return '%s GiB' % (block / 2**30)
        elif block >= 2**40:
            return '%s TiB' % (block / 2**40)
        else:
            return False


def export_results(destination, results):
    """
    Formats and exports the results into a file given.
    :param destination:
        :type destination str:
    :param results:
        :type results dict:
    :return:
    """
    with open(destination, mode='a+', buffering=-1) as dest:
        if version_info.major > 2:
            for k in results.keys():
                dest.write(
                    '\n\n# %s\n%s' % (
                        k,  '\n'.join(str(i.encode('utf-8', errors="surrogateescape")) for i in results[k])
                    )
                )  # FIXME on Python3: the results contains the bytes chars `b'<PATH>'`
        else:
            for k in results.keys():
                dest.write('\n\n# %s\n%s' % (k,  '\n'.join(str(i) for i in results[k])))
            dest.close()


def print_results(results):
    """
    Like `export_results()`, it formats the results but instead of writing them, it displays on the screen.
    :param results:
        :type results dict:
    :return:
    """
    print('\nDuplicates are:')
    for k in results.keys():
        print('\n# %s\n\t%s' % (k, '\n\t'.join(results[k])))

if __name__ == '__main__':
    main()
