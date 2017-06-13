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
    install_spacemacs(forced)


def setup_vim(forced=False):

    vim_path = os.path.join(DIR, 'vim')
    symlink_file_to_home('vim', vim_path, forced)

    vimrc_path = os.path.join(vim_path, 'vimrc')
    symlink_file_to_home('vimrc', vimrc_path, forced)

    command('git submodule update --init --recursive')
    command('vim +PluginInstall +qall')
    command('python3 %s' % os.path.join(vim_path, 'bundle', 'YouCompleteMe',
                                       'install.py'))


def install_spacemacs(forced=False):
    emacsd = os.path.join(HOME, '.emacs.d')

    if os.path.isdir(emacsd):
        if not forced:
            print("%s already exists!" % emacsd)
            print()
            return
        command('rm -rf .emacs.d')
    command('git clone https://github.com/syl20bnr/spacemacs %s' % str(emacsd))

    spacemacs_d_path = os.path.join(DIR, 'emacs-config')
    symlink_file_to_home('.spacemacs.d', spacemacs_d_path, forced)


def update_sudo():
    command('sudo python%d %s' %
            (sys.version_info[0], os.path.join(DIR, 'init', 'update-sudo.py')))


def setup_ubuntu(forced=False):

    print('Setting sudo to NOPASSD...')
    update_sudo()

    print('Installing base programs...')
    print()
    install_base_programs()

    print('Installing Google Chrome...')
    install_chrome()

    print('Installing i3-gaps')
    install_i3_gaps()

    print('Adding i3 config...')
    init_i3(forced, ubuntu=True)

    print('Setting up dconf...')
    setup_dconf()

    print('Setting up dotfiles...')
    setup_dotfiles(forced)

    print('Installing spacemacs....')
    install_spacemacs()

    print('Installing neovim....')
    install_neovim(forced)

def install_chrome():
    f = urllib.urlopen(
        "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"
    )
    deb = f.read()
    _, temp = tempfile.mkstemp()
    print(temp)
    with open(temp, 'w') as file_:
        file_.write(deb)
    command('sudo dpkg -i --force-depends %s' % temp)
    command('sudo apt-get install -f -y')


def install_i3_gaps():
    I3_GAPS_UBUNTU_DEPENDS = \
'''libxcb1-dev libxcb-keysyms1-dev libpango1.0-dev \
libxcb-util0-dev libxcb-icccm4-dev libyajl-dev libstartup-notification0-dev \
libxcb-randr0-dev libev-dev libxcb-cursor-dev libxcb-xinerama0-dev \
libxcb-xkb-dev libxkbcommon-dev libxkbcommon-x11-dev autoconf git automake \
libtool libxcb-xrm0 libxcb-xrm-dev'''

    command('sudo apt-get install -y %s' % I3_GAPS_UBUNTU_DEPENDS)
    I3_GAPS_SRC = 'https://www.github.com/Airblader/i3'
    I3_GAPS_SRC_DIR = os.path.join(HOME,'i3-gaps-src')
    command('git clone "%s" "%s"' % (I3_GAPS_SRC, I3_GAPS_SRC_DIR))

    command('autoreconf --install', cwd=I3_GAPS_SRC_DIR)
    command('rm -rf build/', cwd=I3_GAPS_SRC_DIR)
    command('mkdir build', cwd=I3_GAPS_SRC_DIR)
    build_dir = os.path.join(I3_GAPS_SRC_DIR, 'build')
    command('../configure --prefix=/usr --sysconfdir=/etc'
            '--disable-sanitizers', cwd=build_dir)
    command('make -j', cwd=build_dir)
    command('sudo make install', cwd=build_dir)

def install_spotify():
    # 1. Add the Spotify repository signing key to be able to verify downloaded packages
    command('sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80'
            '--recv-keys BBEBDCB318AD50EC6865090613B00F1FD2C19886')

    # 2. Add the Spotify repository
    command('echo deb http://repository.spotify.com stable non-free | sudo tee'
            '/etc/apt/sources.list.d/spotify.list')
    # 3. Update list of available packages
    command('sudo apt-get update')
    # 4. Install Spotify
    command('sudo apt-get install -y spotify-client')

def install_base_programs():
    with open(os.path.join(DIR, 'init', 'ubuntu-programs'), 'r') as programs:
        # Split on spaces, and newlines..
        programs = programs.read().split()
    print('About to install: %s' % ', '.join(programs))
    print()
    command('sudo apt-get update')
    command('sudo apt-get dist-upgrade -y')
    command('sudo apt-get install -y %s' % ' '.join(programs))


def init_i3(forced=False, ubuntu=False):

    command(
        'gsettings set org.gnome.desktop.background show-desktop-icons false')

    i3config_dir = os.path.join(HOME, '.config', 'i3')
    i3config_path = os.path.join(i3config_dir, 'config')
    i3config_dotfile = os.path.join(DIR, 'dotfiles', 'i3.config')

    if not os.path.isdir(i3config_dir):
        os.makedirs(i3config_dir)

    if os.path.isfile(i3config_path):
        if not forced:
            print("%s already exists!" % i3config_path)
            print()
            return
        os.remove(i3config_path)
    os.symlink(i3config_dotfile, i3config_path)

    if ubuntu:
        # Turn off nautilus full screen..
        command('gsettings set org.gnome.desktop.background show-desktop-icons false')


def install_neovim(forced=False):
    # Neovim, relies on python3
    command('sudo add-apt-repository ppa:neovim-ppa/unstable')
    command('sudo apt-get update')
    command('sudo apt-get install -y neovim')
    command('sudo pip3 install neovim -qqq')

    neovimrc_dir = os.path.join(HOME,'.config','nvim')
    neovimrc_path = os.path.join(neovimrc_dir, 'init.vim')
    dot_vimrc_path = os.path.join(HOME, '.vimrc')

    if not os.path.isdir(neovimrc_dir):
        os.makedirs(neovimrc_dir)

    if os.path.isfile(neovimrc_path):
        if not forced:
            print("%s already exists!" % neovimrc_path)
            print()
            return
    os.symlink(neovimrc_path, dot_vimrc_path)

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

def update_vim():
    command('git submodule foreach git pull origin master')

def main():
    # Option Menu:
    main_menu = Menu(name='main menu')

    main_menu.add_option('Setup Ubuntu', 1, setup_ubuntu)
    main_menu.add_option('Setup Dotfiles', 2, setup_dotfiles)
    main_menu.add_option('Update Vim Config', 3, update_vim)
    main_menu.add_option('Add My Scripts to PATH', 4, setup_personal_scripts)

    main_menu.add_space()

    forced_setup_dotfiles = lambda: setup_dotfiles(forced=True)
    forced_setup_ubuntu = lambda: setup_ubuntu(forced=True)
    forced_setup_personal_scripts = lambda: setup_personal_scripts(forced=True)

    main_menu.add_option('Setup Ubuntu (forced)', '1f', forced_setup_ubuntu)
    main_menu.add_option('Setup Dotfiles (forced)', '2f',
                         forced_setup_dotfiles)
    main_menu.add_option('Add My Scripts to PATH', '4f', forced_setup_personal_scripts)

    main_menu.prompt()


if __name__ == '__main__':
    main()
