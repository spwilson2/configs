#!/usr/bin/python

from __future__ import print_function
import signal
import os
import sys
import subprocess
import urllib
import tempfile

# Keep input safe in python2
try:
    input = raw_input
except NameError:
    pass

DIR = os.path.abspath(os.path.dirname(__file__))
DEFAULT_PROMPT = "Select an option: "
DOTFILES = 'dotfiles'
CONFIGS = 'config'
DOTFILES_AUTO_LIST = 'FILES'
LOCAL_BIN_PATH = os.path.expanduser('~/.local/bin')
SCRIPT_EXPORTS_FILE=DIR+'/%s/SCRIPT_EXPORTS' % CONFIGS
HOME = os.path.expanduser("~")


VERBOSE=''
V_WARN  = 1
V_INFO  = 2
V_DEBUG = 3

def printv(level, verbosity=VERBOSE, *args, **kwargs):
    if (level >= len(verbosity)):
        print(*args, **kwargs)

def command(program, cwd=DIR):
    ''' Run a shell command, default directory is the DIR of this script.'''
    printv(V_INFO, "Executing: %s" % program)
    subprocess.call(program, shell=True, cwd=cwd)

class Menu(object):
    class Option(object):
        def __init__(self, option, select, callback):
            self.option = option
            self.select = select
            self.callback = callback

    def __init__(self, name="menu"):
        self._options = {}
        self._options_ordered = []
        self._name = name
        pass

    def add_option(self, option, select, callback):
        self._options[str(select)] = Menu.Option(option, select, callback)
        self._options_ordered.append(Menu.Option(option, select, callback))

    def add_space(self, string=''):
        self._options_ordered.append(string)

    def _prompt(self, prompt):
        # Register our signal handler for the duration of this menu.
        signal.signal(signal.SIGINT, Menu._signal_handler)

        for option in self._options_ordered:
            if type(option) is str:
                print(option)
            else:
                print(str(option.option) + ': ' + str(option.select))

        print()
        selection = input(DEFAULT_PROMPT).strip()
        print()

        if selection in self._options:
            self._options[selection].callback()
            return True
        else:
            return False

    def prompt(self, prompt=DEFAULT_PROMPT):
        try:
            while not self._prompt(prompt):
                pass
        except Interrupt:
            print()
            print("Exiting %s." % str(self._name))

    @staticmethod
    def _signal_handler(signal, frame):
        raise Interrupt()


class Interrupt(Exception):
    pass


def is_file_or_dir(file_path):
    return os.path.isfile(file_path) or os.path.isdir(file_path)


def symlink_file_to_home(file_, file_path, forced=False):

    symlink_path = os.path.join(HOME, '.' + file_)

    if not is_file_or_dir(file_path):
        print(file_path)
        print("Config file: %s doesn't exist!" % str(file_))
        print()
        return

    if is_file_or_dir(symlink_path):
        if not forced:
            print("%s already exists!" % symlink_path)
            print()
            return
        os.remove(symlink_path)

    print('Creating symlink for %s' % file_)
    os.symlink(file_path, symlink_path)


def setup_dotfiles(forced=False):

    dotfiles_dir = os.path.join(DIR, DOTFILES)

    dotfiles_list = os.path.join(dotfiles_dir, DOTFILES_AUTO_LIST)

    with open(dotfiles_list, 'r') as dotfiles_list:
        for file_ in dotfiles_list.readlines():
            file_ = file_.strip()
            try:
                dotfile_path = os.path.join(dotfiles_dir, file_)

                symlink_file_to_home(file_, dotfile_path, forced)

            except OSError as e:
                print(e)

    setup_vim(forced)


def setup_vim(forced=False):

    vim_path = os.path.join(DIR, 'vim')
    symlink_file_to_home('vim', vim_path, forced)

    vimrc_path = os.path.join(vim_path, 'vimrc')
    symlink_file_to_home('vimrc', vimrc_path, forced)


def update_sudo():
    command('sudo python%d %s' %
            (sys.version_info[0], os.path.join(DIR, 'init', 'update-sudo.py')))


def setup_offline(forced=False):

    print('Setting sudo to NOPASSWD...')
    update_sudo()

    print('Setting up dconf...')
    setup_dconf()

    print('Setting up dotfiles...')
    setup_dotfiles(forced)


def setup_personal_scripts(forced=False):

    if not os.path.isdir(LOCAL_BIN_PATH):
        os.makedirs(LOCAL_BIN_PATH)

    with open(SCRIPT_EXPORTS_FILE, 'r') as scripts_list:
        for file_ in scripts_list:
            file_ = file_.strip()
            script_file_path = DIR+'/personal-scripts/' + file_
            bin_link_path = "%s/%s" % (LOCAL_BIN_PATH, file_)

            if os.path.isfile(bin_link_path) or os.path.islink(bin_link_path):
                if not forced:
                    print("%s already exists!" % bin_link_path)
                    print()
                    continue
                os.remove(bin_link_path)
            os.symlink(script_file_path, bin_link_path)


def setup_dconf():
    DCONF_CONFIG = os.path.join(DIR, CONFIGS, 'dconf-config')
    command('dconf load / < %s' % DCONF_CONFIG)

def main():
    # Option Menu:
    main_menu = Menu(name='main menu')

    main_menu.add_option('Setup All', 1, setup_offline)
    main_menu.add_option('Setup Dotfiles', 2, setup_dotfiles)
    main_menu.add_option('Add My Scripts to PATH', 3, setup_personal_scripts)

    main_menu.add_space()

    forced_setup_offline = lambda: setup_offline(forced=True)
    forced_setup_dotfiles = lambda: setup_dotfiles(forced=True)
    forced_setup_personal_scripts = lambda: setup_personal_scripts(forced=True)

    main_menu.add_option('Setup offline (forced)', '1f', forced_setup_offline)
    main_menu.add_option('Setup Dotfiles (forced)', '2f', forced_setup_dotfiles)
    main_menu.add_option('Add My Scripts to PATH (forced)', '3f', forced_setup_personal_scripts)

    main_menu.prompt()


if __name__ == '__main__':
    main()
