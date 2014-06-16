from md5sum import md5sum as mds
from os import walk, makedirs, listdir, getcwd
from shutil import rmtree
from os.path import join, getsize, expanduser, exists, abspath, dirname
from time import gmtime, strftime
from progressbar import ProgressBar, Percentage, ETA, Bar
from tempfile import gettempdir
from getopt import getopt, GetoptError
from sys import argv

RESULT_PATH = gettempdir() + '/search_duplicates_results/'


def main():
    opts = []
    try:
        opts, args = getopt(argv[1:], 'hp:r:b', ['help', 'path=', 'result=', 'no-estimation', 'binary'])
    except GetoptError as e:
        print str(e)
        usage()
        exit(1)
    path = None
    result = ''
    estimation = True
    binary = False
    for p, arg in opts:
        if p in ('-h', '--help'):
            usage()
            exit()
        elif p in ('-p', '--path'):
                path = arg
        elif p in ('-r', '--result'):
            if arg[0] == '~':
                result = expanduser('~') + arg[1:]
            elif arg[:2] == './':
                result = getcwd() + arg[1:]
            else:
                result = arg
        elif p == '--no-estimation':
            estimation = False
        elif p in ('-b', '--binary'):
            binary = True
        else:
            print 'Unknown option'
            usage()
            exit(1)
    if path is None:
        path = raw_input('Please give an absolute path to directory where searching duplicates (e.q.: ~/music/): ')
    if path[0] == '~':
                path = expanduser('~') + path[1:]
    elif path[:2] == './':
                path = getcwd() + path[1:]
    if not exists(path):
        print 'ERROR: the selected path to scan does not exist (see the documentation for more information or --help).'
        exit(1)
    if result != '':
        try:
            with open(result, 'w') as r:
                r.write('')
                r.close()
        except IOError or OSError, e:
            print 'Unable to take an access to the results path, the results will not saved into "%s" \
(with the following error: "%s"). But they remain displayed below.' % (result, str(e))
            result = ''
    beginning(path, estimation, binary, result)


def beginning(target, get_estimation=False, binary_mode=False, result_output=''):
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
    """
    e = ''
    print 'Step 1 of 4: getting number of files and total size.\n---\n'
    if get_estimation:
        e = estimate(target)
        c = convert(e[2], binary_mode)
        print 'At', strftime("%H:%M:%S", gmtime()), 'we have:', e[1], 'files in', e[0], 'directories', 'for',
        print e[2], 'bytes' + (c and ' whether about %s.' % c or '.')
        print 'We will begin to scan "%s", please avoid to change files may to distort final result and above \
estimates.\n\n' % target, 'The results will be displayed bellow after all was done.',
        if result_output != '':
            print 'And will be displayed too into this file: "%s".' % result_output,
    else:
        print 'Operation canceled (see --help for more information).',
    print '\n\n'
    search(target, e and e[1] or None, result_output)


def estimate(target):
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
            return False
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
            return False


def calc(start, end):
    """
        w = 100
        start = 50
        end = 120

        = (start / end) * w
        = (50 / 120) * 100
        = 0.4166666666666667 * 100
        = 41.66666666666667
    """
    return (start / float(end)) * 100


def search(target, total_files, results_path=''):
    """
        * First, we clear the file "./tmp" before operate.
        * Next, we initialize the progress bar and the loop.
        * After it, we browse each file, if its MD5 hash is not in "./tmp" we write it and give its path.
          Else, if the hash is already into we write into "./found".

    NOTE: I don't think it's the best method. So if you have any more powerful to suggest don't hesitate to propose a
          beautiful pull request!
    """
    if exists(RESULT_PATH):
        rmtree(RESULT_PATH)
    makedirs(RESULT_PATH)
    p = None
    z = 1
    print 'Step 3 of 4: get all files.\n---'
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
        print 'Unknown remaining time and progress... (You\'ve specified no estimation or there is no file).'

    for root, dirs, files in walk(target):
        for name in files:
            try:
                f = join(root, name)
                hashed = mds(f)
                with open(str(RESULT_PATH) + str(hashed), 'a') as r:
                    r.write('%s\n' % f)
                    r.close()
                if total_files is not None:
                    p.update(calc(z, total_files))
                z += 1
            except OSError:
                pass
    if total_files is not None:
        p.finish()
    print '\n'

    print 'Step 4 of 4: compare all files and display duplicates.\n---'
    z = 0
    r = None
    for name in listdir(RESULT_PATH):
        f = open(join(RESULT_PATH, name)).readlines()
        if len(f) > 1:
            z += 1
            print z, '\n---'
            if results_path != '':
                try:
                    with open(results_path, 'a') as r:
                        r.write(str(z) + '\n---\n')
                except IOError or OSError:
                    pass
            for l in f:
                print ' ' * 4, '*', l
                if results_path != '':
                    try:
                        with open(results_path, 'a') as r:
                            r.write(' ' * 4 + ' * ' + l + '\n')
                    except IOError or OSError:
                        pass
            print '\n'
    if z == 0:
        print ' ' * 4, 'No duplicate found. Good job! \\(^o^)/'
        if results_path != '':
            with open(results_path, 'a') as r:
                try:
                    r.write('No duplicate found. Good job! \\(^o^)/')
                except IOError or OSError:
                    pass
    rmtree(RESULT_PATH)


def usage():
    try:
        print open(abspath(dirname(__file__)) + '/HELP.txt').read()
    except IOError or OSError, e:
        print 'ERROR: unable to find or open the help file.'
        print e
        exit(1)


if __name__ == '__main__':
    main()