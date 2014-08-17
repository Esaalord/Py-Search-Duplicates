#!/usr/bin/python2
# -*- coding: utf-8 -*-
#
#  Py-Search-Duplicates (https://github.com/NyanKiyoshi/Py-Search-Duplicates/)
# A Python2 script to search all duplicates files into a given directory recursively.
#
# Copyright (c) 2014 - NyanKiyoshi @ https://github.com/NyanKiyoshi/
#
#                           The MIT License (MIT)
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from md5sum import md5sum as mds
from os import (
    walk,
    makedirs,
    listdir,
    getcwd,
    name as os_name,
    system,
)
from shutil import rmtree
from os.path import (
    join,
    getsize,
    expanduser,
    exists,
    abspath,
    dirname,
    isdir,
    normpath,
    splitdrive,
)
from time import gmtime, strftime
from progressbar import ProgressBar, Percentage, ETA, Bar
from tempfile import gettempdir
from getopt import getopt, GetoptError
from sys import argv
#from re import match, compile as recompile

__VERSION__ = '1.1.0', '(release date: August 17, 2014)[RELEASE 3]'
#file_pattern = recompile('(\w)+')
RESULT_PATH = gettempdir() + '/search_duplicates_results/'
OPT_NEGATION = ['n', 'no', 'no sir!']
DEFAULT_PARAMS = dict(
    path='',
    results='',
    estimation=True,
    binary=False
)


def main():
    """
    First function called.
    :return: None
    """
    if os_name == 'nt':
        print "[WARNING] The DOS of Windows doesn't support the UTF-8 like accents and more.\n"

    global RESULT_PATH
    try:
        if not exists(RESULT_PATH):
            makedirs(RESULT_PATH)
        with open(RESULT_PATH + 'test', 'a') as o:
            o.write('')
    except IOError as e:
        unavailable = True
        print '[ERROR] Unable to write into the temporary directory: {error}'.format(error=e)
        user_response = raw_input('Do you want replace it? [y/n/exit] ').strip().lower()
        if user_response == 'exit':
            print 'Operation canceled.'
            exit(1)
        elif user_response not in OPT_NEGATION:
            while unavailable:
                results_path = raw_input('New absolute directory (type ":exit" to quit): ')
                if not RESULT_PATH == ':exit':
                    check = check_path(results_path)
                    if not check[0]:
                        if check[1] == 'NOT_EXIST':
                            print '[ERROR] {RESULT_PATH} is not a valid path or ' \
                                  'the directory does not exist please check this lasted.\n' \
                                  ''.format(RESULT_PATH=results_path)
                        elif check[1] == 'NOT_DIR':
                            print '[ERROR] {RESULT_PATH} is not a directory.\n'.format(RESULT_PATH=results_path)
                        elif check[1] == 'RESERVED_PATH':
                            print '[ERROR] {RESULT_PATH} ' \
                                  'is a reserved path for this script.'.format(RESULT_PATH=results_path)
                        continue
                    if raw_input(
                            '[WARNING] Are you sure to use {RESULT_PATH} as temporary folder for Py Search Duplicates? '
                            'All data into this folder will be deleted! [y/n] '.format(RESULT_PATH=results_path)
                    ) .strip().lower() in OPT_NEGATION:
                        RESULT_PATH = results_path
                        unavailable = False
                else:
                    print 'Operation canceled.'
                    exit(1)
    params = DEFAULT_PARAMS

    # reading the possibles arguments given by the user
    opts = []
    try:
        opts, args = getopt(argv[1:], 'hp:r:b', ['help', 'path=', 'result=', 'no-estimation', 'binary'])
    except GetoptError as e:
        print str(e)
        usage()
        exit(1)
    for p, arg in opts:
        if p in ('-h', '--help'):
            usage()
            exit()
        elif p in ('-p', '--path'):
            params['path'] = replace_in_path(arg)
        elif p in ('-r', '--result'):
            params['results'] = replace_in_path(arg)
        elif p == '--no-estimation':
            params['estimation'] = False
        elif p in ('-b', '--binary'):
            params['binary'] = True
        else:
            print 'Unknown option'
            usage()
            exit(1)

    # if the parameter path is not set we ask to the user to do it
    if params['path'] == '':
        valid = False
        while not valid:
            params['path'] = replace_in_path(
                raw_input(
                    'Please give an absolute path to a directory to search duplicates (e.q.: /home/nyan/music/): '
                )
            )
            check = check_path(params['path'])
            if not check[0]:
                if check[1] == 'NOT_EXIST':
                    print '[ERROR] {PATH} is not a valid path or ' \
                          'the directory does not exist please check this lasted.\n'.format(PATH=params['path'])
                elif check[1] == 'NOT_DIR':
                    print '[ERROR] {PATH} is not a directory.\n'.format(PATH=params['path'])
                elif check[1] == 'RESERVED_PATH':
                    print '[ERROR] {PATH} is a reserved path for this script.'.format(PATH=params['path'])
                continue
            valid = True
    else:
        check = check_path(params['path'])
        if not check[0]:
            if check[1] == 'NOT_EXIST':
                print '[ERROR] {PATH} is not a valid path or ' \
                      'the directory does not exist please check this lasted.\n'.format(PATH=params['path'])
            elif check[1] == 'NOT_DIR':
                print '[ERROR] {PATH} is not a directory.\n'.format(PATH=params['path'])
            elif check[1] == 'RESERVED_PATH':
                print '[ERROR] {PATH} is a reserved path for this script.'.format(PATH=params['path'])
            exit(1)

    # if the user has not give any arguments we prompt a wizard
    if not opts:
        params = wizard(params)
    else:  # we test the results paths
        if params['results'] != '':
            if isdir(params['results']):
                if raw_input(
                    '[ERROR] Oops! The results path is invalid: this is a directory. '
                    'It will be replaced by this path: "{new_results_path}". '
                    'Are you okay with this decision? [y/n] '.format(
                        new_results_path=params['results'] + '/results.txt' if params['results'][-1] not in ['\\', '/']
                        else params['results'] + 'results.txt'
                    )
                ) not in OPT_NEGATION:
                    params['results'] = params['results'] + '/results.txt' if params['results'][-1] not in ['\\', '/'] \
                        else params['results'] + 'results.txt'

            check = check_path(params['results'], True, must_be_a_directory=False)
            if not check[0]:
                if check[1] == 'NOT_EXIST':
                    print '[ERROR] {PATH} is not a valid path or ' \
                          'the directory does not exist please check this lasted.\n'.format(PATH=params['results'])
                elif check[1] == 'RESERVED_PATH':
                    print '[ERROR] {PATH} ' \
                          'is a reserved path for this script.'.format(PATH=params['results'])
                elif check[1] == 'WRITING_ERR':
                    print 'Unable to take an access to the results path, ' \
                        'the results will not saved into "{results_path}" ' \
                        '(we have this following error: "{error}"). ' \
                        ''.format(results_path=params['results'], error=check[2])
                print 'The results stay displayed bellow.'
                params['results'] = ''

    okay = False
    while not okay:
        if os_name == 'posix':
            system('clear')
        elif os_name == 'nt':
            system('cls')
        else:
            print '\n' * 100

        print '=== Wizard of Py Search Duplicates %s' % __VERSION__[0]
        print 'You have been selected these following parameters:'
        print '\t* path to scan: {path_to_scan}\n' \
              '\t* results path: {results_path}' \
              '\n'.format(path_to_scan=params['path'], results_path=params['results'] or None)
        for i in params.keys():
            if i not in ['path', 'results']:
                print '\t* {key}: {param}'.format(key=i, param=params[i])

        if raw_input('\n\nDo you want to keep it? [y/n] ').strip().lower() not in OPT_NEGATION:
            okay = True
        else:
            wizard(params, True)
    beginning(params)


def replace_in_path(path):
    """
    There is two possibilities:
        * [POSIX ONLY] it replace the tilde of the path with the absolute path to the home
        * it replace "./" with the current working directory
    :param path: The path to replace.
    :return: Return the new path.
    """
    if not len(path) < 1:
        if path[0] == '~' and os_name == 'posix':
                path = expanduser('~') + path[1:]
        elif path[:2] == './':
                path = getcwd() + path[1:]
    return path


def split_path(path):
    """
    Inspired of the NT os.path._abspath_split
    :param path: the path to split.
    :return: a tuple with: the prefix (drive letter on NT and empty on Posix) and a list of the rest.
    """
    path = abspath(normpath(path))
    prefix, rest = splitdrive(path)  # on Posix, drive is always empty
    if os_name == 'nt':
        return prefix, [x for x in rest.split('\\') if x]
    elif os_name == 'posix':
        return prefix, [x for x in rest.split('/') if x]
    else:
        return prefix, [rest]


def check_path(path, writing_test=False, must_exist=True, must_be_a_directory=True, must_be_not_reserved=True):
    """
    ERRORS LIST:
        * WRITING_ERR   -> unable to write into the given path
        * NOT_EXIST     -> the given path/directory doesn't exist
        * NOT_DIR       -> the directory of the given path/directory doesn't exist
        * RESERVED_PATH -> the path given is reserved on/for this script

    :param path: The path to check.
    :return: boolean, Error str ID, can return more information.
    """
    if writing_test:
        try:
            with open(path, 'w') as r:
                r.write('')
                r.close()
        except IOError as e:
            return False, 'WRITING_ERR', str(e)
    if must_exist:
        if not exists(path):
            return False, 'NOT_EXIST'
    if must_be_a_directory:
        if not isdir(path):
            return False, 'NOT_DIR'
    if must_be_not_reserved:
        s_path = split_path(path)
        for reserved_path in [RESULT_PATH]:
            # for reserved_path in reserved paths
            reserved_path = split_path(reserved_path)
            if s_path[0] == reserved_path[0] and s_path[1][:len(reserved_path[1])] == reserved_path[1]:
                return False, 'RESERVED_PATH'
    return True, 'SUCCESS'


def wizard(params, edit=False):
    """
    :param params: Take the actual parameters dictionary to edit it.
    :param edit: Boolean to activate or disable the edit mode.
    :return: The edited dictionary :param params:.
    """
    print '\n\n=== Wizard of Py Search Duplicates %s' % __VERSION__[0]
    if os_name == 'nt':
        print "[WARNING] The DOS of Windows doesn't support the UTF-8 like accents and more.\n"
    print '\n[TIP] Press [ENTER] to say "yes sir!" and "n" to say "no sir!".'

    if edit:
        if params['path'] == '':
            valid = False
            while not valid:
                params['path'] = replace_in_path(
                    raw_input(
                        'Please give an absolute path to a directory to search duplicates (e.q.: /home/nyan/music/): '
                    )
                )
                check = check_path(params['path'])
                if not check[0]:
                    if check[1] == 'NOT_EXIST':
                        print '[ERROR] {PATH} is not a valid path or ' \
                              'the directory does not exist please check this lasted.\n'.format(PATH=params['path'])
                    elif check[1] == 'NOT_DIR':
                        print '[ERROR] {PATH} is not a directory.\n'.format(PATH=params['path'])
                    elif check[1] == 'RESERVED_PATH':
                        print '[ERROR] {PATH} is a reserved path for this script.'.format(PATH=params['path'])
                    continue
                valid = True
        else:
            if raw_input('Do you want edit the path where search duplicates? [y/n] ').strip().lower() \
                    not in OPT_NEGATION:
                valid = False
                while not valid:
                    params['path'] = replace_in_path(
                        raw_input(
                            'Type your new path (e.q.: /home/nyan/music/): '
                        )
                    )
                    check = check_path(params['path'])
                    if not check[0]:
                        if check[1] == 'NOT_EXIST':
                            print '[ERROR] {PATH} is not a valid path or ' \
                                  'the directory does not exist please check this lasted.\n'.format(PATH=params['path'])
                        elif check[1] == 'NOT_DIR':
                            print '[ERROR] {PATH} is not a directory.\n'.format(PATH=params['path'])
                        elif check[1] == 'RESERVED_PATH':
                            print '[ERROR] {PATH} ' \
                                  'is a reserved path for this script.'.format(PATH=params['path'])
                        continue
                    valid = True

    if edit:
        if raw_input('Do you want change the path results? [y/n] ').strip().lower() not in OPT_NEGATION:
            params['results'] = replace_in_path(raw_input('Type your new path (e.q.: ./result.txt): '))
            if params['results'] != '':
                if isdir(params['results']):
                    if raw_input(
                        '[ERROR] Oops! The results path is invalid: this is a directory. '
                        'It will be replaced by this path: "{new_results_path}". '
                        'Are you okay with this decision? [y/n] '.format(
                            new_results_path=params['results'] + '/results.txt'
                            if params['results'][-1] not in ['\\', '/']
                            else params['results'] + 'results.txt'
                        )
                    ).strip().lower() not in OPT_NEGATION:
                        params['results'] = params['results'] + '/results.txt'\
                            if params['results'][-1] not in ['\\', '/'] \
                            else params['results'] + 'results.txt'
                check = check_path(params['results'], True, must_be_a_directory=False)
                if not check[0]:
                    if check[1] == 'NOT_EXIST':
                        print '[ERROR] {PATH} is not a valid path or ' \
                              'the directory does not exist please check this lasted.\n'.format(PATH=params['results'])
                    elif check[1] == 'RESERVED_PATH':
                        print '[ERROR] {PATH} ' \
                              'is a reserved path for this script.'.format(PATH=params['results'])
                    elif check[1] == 'WRITING_ERR':
                        print 'Unable to take an access to the results path, ' \
                            'the results will not saved into "{results_path}" ' \
                            '(we have this following error: "{error}"). ' \
                            ''.format(results_path=params['results'], error=check[2])
                    print 'The results stay displayed bellow.'
                    params['results'] = ''
    else:
        if raw_input('Do you want to save the results into a custom path? [y/n] ').strip().lower() not in OPT_NEGATION:
            params['results'] = replace_in_path(raw_input('Path to save the results (e.q.: ./result.txt): '))
            if params['results'] != '':
                if isdir(params['results']):
                    if raw_input(
                        '[ERROR] Oops! The results path is invalid: this is a directory. '
                        'It will be replaced by this path: "{new_results_path}". '
                        'Are you okay with this decision? [y/n] '.format(
                            new_results_path=params['results'] + '/results.txt'
                            if params['results'][-1] not in ['\\', '/']
                            else params['results'] + 'results.txt'
                        )
                    ).strip().lower() not in OPT_NEGATION:
                        params['results'] = params['results'] + '/results.txt'\
                            if params['results'][-1] not in ['\\', '/'] \
                            else params['results'] + 'results.txt'

                check = check_path(params['results'], True, must_be_a_directory=False)
                if not check[0]:
                    if check[1] == 'NOT_EXIST':
                        print '[ERROR] {PATH} is not a valid path or ' \
                              'the directory does not exist please check this lasted.\n'.format(PATH=params['results'])
                    elif check[1] == 'RESERVED_PATH':
                        print '[ERROR] {PATH} ' \
                              'is a reserved path for this script.'.format(PATH=params['results'])
                    elif check[1] == 'WRITING_ERR':
                        print 'Unable to take an access to the results path, ' \
                            'the results will not saved into "{results_path}" ' \
                            '(we have this following error: "{error}"). ' \
                            ''.format(results_path=params['results'], error=check[2])
                    print 'The results stay displayed bellow.'
                    params['results'] = ''
    if raw_input('Do you want an estimation? (recommended) [y/n] ').strip().lower() in OPT_NEGATION:
        params['estimation'] = False
    if params['estimation']:
        if not raw_input(
                'Do you want the usage of the decimal (human readable) mode? (MB, GB, etc.) [y/n] '
        ).strip().lower() not in OPT_NEGATION:
            params['binary'] = True

    return params


def beginning(params):
    """
    1.  After getting all arguments given we will call 'estimation()' who get and return the total of files, directories
        and size in bytes. After it we call 'convert()' it will choose the best conversion needed to return in another
        unit if needed (support KiB, MiB, GiB and TiB), if it is again a bytes unit we display anything.
        All quotes above take place if and only if the user has asked to do it or it has nothing specified any
        preferences.
    2.  If the user has specified want to display a progress bar or it has nothing specified any preferences, this
        Python Script will be display all progression according to the files number.
    3.  If the user has specified want to display a progress bar or it has nothing specified any preferences, we will
        display the speed according to the total size.
    4.  Finally we browse recursively the asked directory.

    NOTE: the steps 1, 2 and 3 can take a little more time depending on the target's size.

    :param params: A dictionary with parameters for the research.
    :return: None
    """
    if os_name == 'posix':
        system('clear')
    elif os_name == 'nt':
        system('cls')
    else:
        print '\n' * 100

    e = ''
    print 'Step 1 of 3: getting number of files and total size.\n---\n'
    if params['estimation']:
        e = estimate(params['path'])
        c = convert(e[2], params['binary'])
        print 'At', strftime("%H:%M:%S", gmtime()), 'we have:', e[1], 'files in', e[0], 'directories', 'for',
        print e[2], 'bytes' + (c and ' whether about {size}.'.format(size=c) or '.')
        print 'We will begin to scan "{path}", please avoid to change files may to distort final result and above ' \
              'estimates.\n\n'.format(path=params['path']), 'The results will be displayed bellow after all was done.',
        if params['results'] != '':
            print 'And will be displayed too into this file: "{results_path}".'.format(results_path=params['results'])
    else:
        print 'Operation canceled (see --help for more information).',
    print '\n\n'
    search(params['path'], e and e[1] or None, params['results'])


def estimate(target):
    """
    Return the number of directories, of files and the total size.
    :param target: A path to scan.
    :return: Two integers:
        - the number of directories
        - the number of files
        - the total size in bytes
    """
    n_dirs = 1
    n_files = 0
    size = 0
    for root, dirs, files in walk(target):
        n_dirs += len(dirs)
        n_files += len(files)
        try:
            size += sum([getsize(join(root, name)) for name in files])
        except OSError:
            pass
    return n_dirs, n_files, size


def convert(block, binary=False):
    """
    It choose between an unit (KB, MB, GB or TB) according with the bytes block given either in binary mode (1024) or
    decimal mode (10^2).

    :param block: An integer in bytes.
    :param binary: A boolean to activate or not the binary mode.
    :return: The new value with the unit at the end of the string or True if it stay in bytes.
    """
    if not binary:
        if 10**3 <= block < 10**6:
            return str(block / 10**3) + ' KB'
        elif 10**6 <= block < 10**9:
            return str(block / 10**6) + ' MB'
        elif 10**9 <= block < 10**12:
            return str(block / 10**9) + ' GB'
        elif block >= 10**2:
            return str(block / 10**12) + ' TB'
        else:
            return True
    else:
        if 2**10 <= block < 2**20:
            return str(block / 2**10) + ' KiB'
        elif 2**20 <= block < 2**30:
            return str(block / 2**20) + ' MiB'
        elif 2**30 <= block < 2**40:
            return str(block / 2**30) + ' GiB'
        elif block >= 2**40:
            return str(block / 2**40) + ' TiB'
        else:
            return True


def calc(start, end):
    """
        w = 100
        start = 50
        end = 120

        = (start / end) * w
        = (50 / 120) * 100
        = 0.4166666666666667 * 100
        = 41.66666666666667

    :param start:
    :param end:
    :return:
    """
    return ((start / float(end)) * 100) <= 100 and ((start / float(end)) * 100) or 100


def search(target, total_files, results_path=''):
    """
    Searching for duplicates into :target:,
        * First, we clear the file temporary files before operate (or RESULT_PATH).
        * Next, we initialize the progress bar and the loop and create estimations if it was asked (True by default).
        * After it, we browse each file, if its MD5 hash is not in RESULT_PATH we write the HASH and its path.
          Else, if the hash is already into RESULT_PATH we write the new path into RESULT_PATH/MD5_HASH.
        * Finally we read all and write/ display the results.

    :param target:
    :param total_files:
    :param results_path:
    :return:
    """
    if exists(RESULT_PATH):
        rmtree(RESULT_PATH)
    makedirs(RESULT_PATH)
    p = None
    z = 1
    print 'Step 2 of 3: analyzing files.\n---'
    if total_files is not None:
        widgets = [
            'Searching: ',
            Percentage(),
            ' ',
            Bar(marker='#', left='[', right=']'),
            ' ',
            ETA(),
        ]
        p = ProgressBar(widgets=widgets, maxval=100)
        p.start()
    else:
        print 'Unknown remaining time and progress... ' \
              'Maybe are you specified no estimation or there is no file into the selected folder?'

    for root, dirs, files in walk(target):
        for name in files:
            try:
                f = abspath(join(root, name))
                hashed = mds(f)
                with open(str(RESULT_PATH) + str(hashed), 'a') as r:
                    r.write('{path}\n'.format(path=f))
                    r.close()
                if total_files is not None:
                    p.update(calc(z, total_files))
                z += 1
            except OSError:
                pass
    if total_files is not None:
        p.finish()
    print '\n'

    print 'Step 3 of 3: comparing all files and display duplicates.\n---'
    error = False
    saved = False
    rendered_results_path = gettempdir() + '/py-search/'
    z = 0
    n_duplicated_files = 0
    with_rending = ''
    without_rending = ''
    for name in listdir(RESULT_PATH):
        f = open(join(RESULT_PATH, name)).readlines()
        if len(f) > 1:
            z += 1
            if not results_path != '':
                with_rending += str(z) + '\n---\n'
            else:
                without_rending += '\n# ' + str(z) + '\n# ---\n'
            for l in f:
                n_duplicated_files += 1
                if not results_path != '':
                    with_rending += ' ' * 5 + '* ' + l + '\n'
                else:
                    without_rending += l
            with_rending += '\n'
            if results_path != '':
                try:
                    with open(results_path, 'a') as f:
                        f.write(without_rending)
                except IOError:
                    raise IOError('Unable to save results into {results_path}'.format(results_path=results_path))
                except OSError:
                    raise OSError('Unable to save results into {results_path}'.format(results_path=results_path))
    if n_duplicated_files + z > 25 and results_path == '':
        if raw_input(
                'There is too many results to show, do you want to save it instead of displaying it? [y/n] '
        ).strip().lower() not in OPT_NEGATION:
            if exists(rendered_results_path):
                rmtree(rendered_results_path)
            makedirs(rendered_results_path)
            try:
                with open(rendered_results_path + 'results.txt', 'a') as f:
                    f.write(with_rending)
                    saved = True
            except IOError:
                print 'ERROR: unable to save results into "{rendered_results_path}"!'.format(
                    rendered_results_path=rendered_results_path + 'results.txt'
                )
                if raw_input('Continue and display it into this window? [y/n] ').strip().lower() not in OPT_NEGATION:
                    print with_rending
                    error = True
                else:
                    raise
            except OSError:
                print 'ERROR: unable to save results into "{rendered_results_path}"!'.format(
                    rendered_results_path=rendered_results_path + 'results.txt'
                )
                if raw_input('Continue and display it into this window? [y/n] ').strip().lower() not in OPT_NEGATION:
                    print with_rending
                    error = True
                else:
                    raise
            if not error:
                print 'The results have been saved into "{rendered_results_path}"!'.format(
                    rendered_results_path=rendered_results_path + 'results.txt'
                )
        else:
            print with_rending
    elif z == 0:
        print ' ' * 4, 'No duplicate found. Good job! \\(^o^)/'
        if results_path != '':
            with open(results_path, 'a') as r:
                try:
                    r.write('# No duplicate found. Good job! \\(^o^)/')
                except IOError:
                    pass
                except OSError:
                    pass
    elif z > 0 and results_path != '':
        print 'All has been successfully done! ' \
              'You can now check the duplicates here: "{results_path}"'.format(results_path=results_path)
    else:
        print with_rending
    rmtree(RESULT_PATH)
    if ((saved or results_path != '') and not error) and os_name == 'nt':
        op = results_path or rendered_results_path + 'results.txt'
        system('notepad {results_path}'.format(results_path=op))
        # trying to open the temporary results in notepad. It return int(0) if it was successful.

    #   ^ It works but it is very random. results=results.mp3  # weird, don't you?
    # (anyway Py Search Duplicates remains an command line script)

    if os_name == 'nt':
        raw_input('Push [ENTER] to quit... ')


def usage():
    """
    Reads HELP.txt and print.
    :return:
    """
    try:
        print open(abspath(dirname(__file__)) + '/HELP.txt').read()
    except IOError:
        raise IOError('ERROR: unable to find or open the help file.')


if __name__ == '__main__':
    main()
