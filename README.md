Py Search Duplicates [1.0.0](First Release)
===========================================
A Python2 script to search all duplicates files into a given directory recursively. It hash each file with the MD5 message-digest algorithm to compare each file and find who already exist.

Table of content:
-----------------
1. [Read before use](#Read-before-use)
2. [Requirements](#Requirements)
3. [System compatibility](#System-compatibility)
4. [Usage](#Usage)
5. [Screenshots](#Screenshots)
6. [Miscellaneous information](#Miscellaneous-information)

Read before use:
----------------
Please take awareness for the [MIT license](https://github.com/NyanKiyoshi/Py-Search-Duplicates/blob/master/LICENSE) of this script before doing anything! (by respect for me and if you are nice (^o^)).

Requirements:
-------------
1. This Python script must be run with __Python 2.x__.
2. It can be run on the system supporting the Linux Kernel and Windows 7 (see the "System compatibility" section for more information).

System compatibility:
---------------------
On Windows system you should use doubles-quotes ("[...]") instead of singles-quotes ('[...]'), for example instead of search.py -p 'C:/directory/' please use  search.py -p "C:/directory/".

| Tested system name                                | Works |
| ------------------------------------------------- | ----- |
| Linux system like Ubuntu, Debian, ArchLinux, etc. |  Yes  |
| Windows 7, Windows XP (SP3, SP2)                  |  Yes  |

Usage:
------
```bash
MAJOR NOTE FOR WINDOWS USER: on Windows system you should use doubles-quotes ("[...]") instead of singles-quotes ('[...]'), for example instead of search.py -p 'C:/directory/' please use  search.py -p "C:/directory/".

    -p, --path=PATH
            The path to search duplicates files.
            Usage examples:
                * -p "~/music"
                * --path="/usr/share/"

    -r, --result=PATH
            The file path where write the results displayed if you want save it.
            Usage examples:
                * -r "~/logs/search_results.txt"
                * result="./results.log"

    --no-estimation:
            If you don't want an estimation before proceed. The estimation display the total files and the current size of directory (recursively) and allow a progress bar.

    -b, --binary:
            If you want an estimation in binary mode (KiB, MiB, GiB, etc.) instead of the default in decimal (KB, MB, GB, etc.).


FEW EXAMPLES:
    * I would like search duplicates into '~/music' with an estimation and in binary mode without writing the output result. I can use:
        search.py -p "~/music" --binary

    * I'm a Windows user, I would like search into 'C:\Documents and Settings\user' and write the output result in 'C:\Documents and Settings\user\Desktop\results.txt' and I want an estimation. I use:
        search.py --path="C:\Documents and Settings\user" -r "C:\Documents and Settings\user\Desktop\results.txt" --no-estimation

```

Screenshots:
------------
![screenshot0](http://i.imgur.com/YeEhgrf.png)
![screenshot1](http://i.imgur.com/TBvrpyB.png)
![screenshot2](http://i.imgur.com/XF0lwJg.png)
![screenshot3](http://i.imgur.com/eX2FS3o.png)

Miscellaneous information:
--------------------------
This Python script was developed on Python 2.7.7 on Linux-2 with ArchLinux.

If you have any suggestion, improvement, issue or others don't hesitate to ask or make a pull request! We will be delighted to read it and response you!
