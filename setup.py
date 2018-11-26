#!/usr/bin/python3
# TODO Python2 support

import argparse
import configparser
import pwd
import os
import subprocess
import shutil
import sys

# TODO Create groupings of setup components:
# dotfiles
# additional programs
# local additinal programs

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")
USERNAME = pwd.getpwuid(os.getuid())[0]
PROGRAM_CFG = os.path.join(THIS_DIR, 'programs.cfg')

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
    def setup(self, force):
        System.set_nopasswd_sudo()
        self.apt_installer()
        self.install_spotify()

    @staticmethod
    def apt_installer():
        cp = configparser.ConfigParser()
        cp.read(PROGRAM_CFG)
        programs = cp['ubuntu']['programs']
        run('sudo apt install -y %s' % programs)

    @staticmethod
    def install_spotify():
        # 1. Add the Spotify repository signing key to be able to verify downloaded packages
        run('sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80'
            '--recv-keys 931FF8E79F0876134EDDBDCCA87FF9DF48BF1C90')
        # 2. Add the Spotify repository
        run('echo deb http://repository.spotify.com stable non-free | sudo tee'
                '/etc/apt/sources.list.d/spotify.list')
        # 3. Update list of available packages
        run('sudo apt-get update')
        # 4. Install Spotify
        run('sudo apt-get install -y spotify-client')

class User:
    class Options:
        PATH = 'path'

    def setup(self, force):
        self.symlink_dotfiles(force)
        self.setup_subrepos()

    @staticmethod
    def setup_subrepos():
        Subrepos.setup()

    @staticmethod
    def symlink_dotfiles(force):
        cp = configparser.ConfigParser()
        dotfiles_dir = os.path.join(THIS_DIR, 'dotfiles')
        cp.read(os.path.join(dotfiles_dir, 'dotfiles.ini'))

        # TODO Handle destination option
        for file_, options in cp.items():
            if file_ == 'DEFAULT':
                continue

            dst = os.path.join('~', '.' + file_)
            dst = options.get(User.Options.PATH, dst)
            dst = os.path.expanduser(dst)
            symlink(os.path.join(dotfiles_dir, file_), dst, force)

class Subrepos:
    SUBREPOS_DIR = os.path.join(THIS_DIR, 'subrepos')
    DEFAULT_REMOTE = 'https://github.com/'
    INI_FILE = os.path.join(SUBREPOS_DIR, 'repos.ini')
    # TODO Support other remotes than github
    # TODO Support other branches
    # TODO Support updating all
    # TODO Support subrepos

    class Options:
        '''Options available in the subrepos .ini file.'''
        PATH = 'path'
        SETUP = 'setup'

    @classmethod
    def setup(cls):
        cf_parser = configparser.ConfigParser()
        cf_parser.read(cls.INI_FILE)
        for subrepo, options in cf_parser.items():
            # Ignore the default namespace
            if subrepo == 'DEFAULT':
                continue
            dest = options.get(cls.Options.PATH, subrepo)
            dest = os.path.join(cls.SUBREPOS_DIR, dest)
            remote = cls.DEFAULT_REMOTE + options.get('remote')

            call = ('git','clone', remote, dest)
            print(call)
            subprocess.call(('git','clone', remote, dest))

            setup_script = options.get(cls.Options.SETUP)
            if setup_script:
                print('Running setup script.')
                run(os.path.join(dest, setup_script))

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

def main():
    options = Options()
    options.parse_options()

    User().setup(options.force)
    if options.ubuntu:
        Ubuntu().setup()

if __name__ == '__main__':
    main()
