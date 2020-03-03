# -*- coding: utf-8 -*-
'''
This module handles configuration of the majority of system dotfiles and
config files.
'''
import errno
import os
import sys

from confsys import _print

HOME = os.path.expanduser('~')

# Dotfiles to place into the home directory
DOTFILES = '''\
bashrc
bash_profile
bash_profile_extra
bash_aliases
gitconfig
gitignore_global
dircolors
tmux.conf
profile
Xresources
npmrc
'''.split()

BASHRCS = '''\
ghs-bashrc
'''

# A list of files to simple drop and replace into the HOME directory.
COPY_FILES = { f: os.path.join(HOME, '.' + f) for f in DOTFILES }

PATH = 'dotfiles'
PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), PATH)


I3_DOTFILE_DST = os.path.join(HOME, '.config/i3/config')
I3_FILES = {
        'i3.config':(HOME, '.config/i3/config'),
}


def symlink(src, dst, force=False):
    '''Create a symbolic link pointing to src at path dst.'''
    try:
        os.symlink(src, dst)
    except OSError:
        if not force:
            return False
        os.remove(dst)
        os.symlink(src, dst)
    return True


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python ≥ 2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def dotfiles(overwrite, **kwargs):
    limit = 0
    for src, dst in COPY_FILES.items():
        src = os.path.join(PATH, src)
        res = symlink(src, dst, overwrite)
        if not res:
            if not limit:
                _print('Not all dotfiles added, the following files already exist:')
                limit = 1
            _print(dst)

        # TODO Add the option for case by case interaction

    if kwargs.get('i3'):
        if not os.path.exists(I3_DOTFILE_DIR):
            mkdir_p(I3_DOTFILE_DIR)

        for src, dst in I3_FILES:
            symlink(src, dst, overwrite)

def create_local(base, **kwargs):
    '''Create the ~/.local directory'''
    local_dir = os.path.join(base, '.local')
    mkdir_p(local_dir)
    bashrcs_dir = os.path.join(local_dir, 'bashrcs')
    for f in BASHRCS:
        src = os.path.join(PATH, f)
        symlink(src, os.path.join(bashrcs_dir, f))

# Comand to diff repo dotfiles with user's existing dotfiles
def diff_dotfiles(config):
    pass

if __name__ == '__main__':
    pass
