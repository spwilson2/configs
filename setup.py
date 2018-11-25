#!/usr/bin/python3
# TODO Python2 support

import argparse
import pwd
import os
import subprocess
import shutil
import configparser

# TODO Create groupings of setup components:
# dotfiles
# additional programs
# local additinal programs

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")
USERNAME = pwd.getpwuid(os.getuid())[0]

class Options():
    def _convert_args(self, args):
        self.force = bool(args.force)
        self.ubuntu = bool(args.ubuntu)

    def parse_options(self):
        parser = argparse.ArgumentParser()
        # Add ubuntu option
        parser.add_argument('--ubuntu', default=False, action='store_true',
                help='Run ubuntu specific setup options')
        parser.add_argument('--force', '-f', default=False, action='store_true',
                help='Overwrite exiting folders and files without prompting')
        self._convert_args(parser.parse_args())

class System:

    @staticmethod
    def _set_nopasswd_sudo(username):
        SUDOER_ENTRY = '{} ALL=(ALL:ALL) NOPASSWD:ALL\n'.format(username)
        sudoer_file = '/etc/sudoers'
        # Check if we are already in sudoers
        with open(sudoer_file, 'r') as sudoers:
            for line in sudoers.readlines():
                if line.strip() == SUDOER_ENTRY:
                    print("Already in sudoer's file!")
                    return
        with open(sudoer_file, 'a') as sudoers:
            sudoers.write(SUDOER_ENTRY)

    @staticmethod
    def module_name():
        if __name__ == '__main__':
            return 'setup'
        else:
            raise NotImplemented


    @staticmethod
    def set_nopasswd_sudo():
        # TODO Python2/3
        script = ('from %s import System; System._set_nopasswd_sudo(\'%s\')'
            % (System.module_name(), USERNAME))
        run('sudo python3 -c "%s"' % script)

class Ubuntu:
    def setup(self):
        System.set_nopasswd_sudo()
        self.install_spotify()

    @staticmethod
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
    if options.ubuntu:
        Ubuntu().setup()

if __name__ == '__main__':
    main()
