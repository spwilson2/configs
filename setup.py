#!/usr/bin/python3
# TODO Python2 support

import argparse
import os
import subprocess
import shutil
import configparser

# TODO Create groupings of setup components:
# dotfiles
# sudo
# additional programs
# local additinal programs

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")

class Options():
    def _convert_args(self, args):
        self.force = bool(args.force)

    def parse_options(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--force', '-f', default=False, action='store_true',
                help='Overwrite exiting folders and files without prompting')
        self._convert_args(parser.parse_args())


class Ubuntu:
    def setup(self):
        self.install_spotify()

    def install_spotify():
        # 1. Add the Spotify repository signing key to be able to verify downloaded packages
        run('sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80'
                '--recv-keys BBEBDCB318AD50EC6865090613B00F1FD2C19886')
        # 2. Add the Spotify repository
        run('echo deb http://repository.spotify.com stable non-free | sudo tee'
                '/etc/apt/sources.list.d/spotify.list')
        # 3. Update list of available packages
        run('sudo apt-get update')
        # 4. Install Spotify
        run('sudo apt-get install -y spotify-client')


def run(program, cwd=THIS_DIR):
    ''' Run a shell command, default directory is the DIR of this script.'''
    print("Executing: %s" % program)
    subprocess.call(program, shell=True, cwd=cwd)

def symlink(src, dst, force=False):
    '''Create a symbolic link pointing to src named dst.'''
    try:
        os.symlink(src, dst)
    except FileExistsError:
        if not force:
            # TODO, don't print anything if a symlink is already correct
            print("Already exists: %s" % dst)
            return
        print("Overwriting: %s" % dst)
        os.remove(dst)
        os.symlink(src, dst)

def symlink_dotfiles(force):
    cp = configparser.ConfigParser()
    dotfiles_dir = os.path.join(THIS_DIR, 'dotfiles')
    cp.read(os.path.join(dotfiles_dir, 'dotfiles.ini'))

    # TODO Handle destination option
    for file_, options in cp.items():
        if file_ == 'DEFAULT':
            continue
        if not options:
            symlink(os.path.join(dotfiles_dir, file_),
                    os.path.join(HOME, '.' + file_), force)

def main():
    options = Options()
    options.parse_options()
    symlink_dotfiles(options.force)

if __name__ == '__main__':
    main()
