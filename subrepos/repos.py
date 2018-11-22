# TODO Add python2 support
# TODO Support other remotes than github
# TODO Support other branches
# TODO Support updating all
# TODO Support subrepos

import configparser
import os
import subprocess


SUBREPOS_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_REMOTE = 'https://github.com/'

INI_FILE = os.path.join(SUBREPOS_DIR, 'repos.ini')

class Options:
    PATH = 'path'

if __name__ == '__main__':
    cf_parser = configparser.ConfigParser()
    cf_parser.read(INI_FILE)

    for subrepo, options in cf_parser.items():

        # Ignore the default namespace
        if subrepo == 'DEFAULT':
            continue

        dest = options.get(Options.PATH, subrepo)
        dest = os.path.join(SUBREPOS_DIR, dest)

        remote = DEFAULT_REMOTE + options.get('remote')

        call = ('git','clone', remote, dest)
        print(call)
        subprocess.call(('git','clone', remote, dest))

