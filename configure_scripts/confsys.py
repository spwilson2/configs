# -*- coding: utf-8 -*-
from __future__ import print_function

'''
This script is used to setup and configure a new system using custom config
definitions and overlays.
'''
import argparse
import configparser
import errno
import getpass
import os
import re
import shutil
import subprocess
import sys

#############################
# Constants
DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))
# Constants
#############################

# Use bitbake as a sort of example
# Setup files will be exec'd
#
class Command():
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def run(self):
        _print('Running: ')
        _print('\t%s' % self.args)
        subprocess.check_call(*self.args, **self.kwargs)

#############################
# Script utilities

PRINTV = [True]
def _print(*args, **kwargs):
    if PRINTV[0]:
        print(*args, **kwargs)

def splitall(path):
    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path: # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts

def parse_config(filename):
    assert os.path.exists(filename)
    cfg = configparser.ConfigParser()
    cfg.read(filename)
    items = {sec: dict(cfg.items(sec)) for sec in cfg.sections()}
    return items

# ABC for subcommands
class Subcommand(object):
    name = None

    def init_parser(self, subparser):
        raise NotImplementedError

    def process_args(self, parser, args):
        raise NotImplementedError

    def run(self):
        raise NotImplementedError

def parse_args(argv):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True

    subcommands = Subcommand.__subclasses__()

    # Instantiate subcommand objects from their class,
    # assign them their name used by the parser
    # (sc -> subcommand)
    commands = {}
    for sc in subcommands:
        assert sc.name is not None, ('Subclass %s name not set in class'
            'definition' % str(sc))
        assert sc.name not in commands, 'Multiple commands with the same name'
        commands[sc.name] = sc()

    # Initialize all subparsers
    for name, sc in commands.items():
        subparser = subparsers.add_parser(name, help=sc.__doc__)
        sc.init_parser(subparser)

    # Parse arguments and get subcommand
    options = parser.parse_args(argv)
    sc = commands[options.command]
    sc.post_process_args(parser, options)
    return sc

class Argument():
    if __debug__:
        _bogus_parser = argparse.ArgumentParser()

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

        # Verify that we can set the argument early on
        if __debug__:
            self.add_to(self._bogus_parser)

    def add_to(self, parser):
        key = '__args__'
        if not key in parser.__dict__:
            parser.__dict__[key] = set([])
        if self not in parser.__dict__[key]:
            ret = parser.add_argument(*self.args, **self.kwargs)
            parser.__dict__[key].add(self)
            return ret

# Common Arguments
ARGS = {
        'root': Argument('--root', 
            default=os.path.expanduser('~'), required=False, 
            help='Directory to place dotfiles and .local into.'),
        'overwrite': Argument('--overwrite', '-f', 
            action='store_true', required=False,
            help='Allow overwriting of existing config files'),
        'distro': Argument('--distro', 
            required=False,
            help=('Manually specify the distro to use '
            '(otherwise automatically detected).'))
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


def join(abspath, partial):
    if partial.startswith('/'):
        return partial
    return os.path.join(abspath, partial)


def link_files(overwrite, files):
    linked = {True: [], False: []}
    for src, dst in files.items():
        res = symlink(src, dst, overwrite)
        linked[res].append((src, dst))

    def print_linked(src, dst):
        print('\t%s -> %s' % (dst, src))

    if linked[False]:
        print('The following symlinks could not be created:')
        for src,dst in linked[False]:
            print_linked(src, dst)
    if linked[True]:
        print('The following symlinks were successfully created:')
        for src,dst in linked[True]:
            print_linked(src, dst)

# Script utilities
#############################
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
        return os.path.splitext(os.path.basename(__file__))[0]


    @staticmethod
    def set_nopasswd_sudo():
        script = ('from %s import System; System._set_nopasswd_sudo(\'%s\')'
            % (System.module_name(), getpass.getuser()))
        subprocess.check_call('sudo python -c "%s"' % script, shell=True, cwd=DIR)


class Programs(Subcommand):
    '''
    Manage programs.
    '''
    name = 'programs'
    PROGRAM_CFG = os.path.join(DIR, 'programs.cfg')
    def __init__(self):
        pass

    def init_parser(self, subparser):
        ARGS['distro'].add_to(subparser)

    @staticmethod
    def detect_distro():
        with open('/etc/issue', 'r') as f:
            info = f.read()
            info = info.lower()
            for d in ['ubuntu', 'manjaro']:
                if d in info:
                    return d

    def post_process_args(self, parser, args):
        if args.distro:
            self.distro = args.distro
        else:
            self.distro = self.detect_distro()
            if not self.distro:
                raise ValueError('Unable to detect distro.')

    @staticmethod
    def parse_program_config():
        items = parse_config(Programs.PROGRAM_CFG)

        # Return into a dict with format:
        # {distro: {
        #   option: [program, program]
        # }

        programs = {}
        for _heading, keys in items.items():
            distro = keys.pop('distro')
            option = keys.pop('option')
            progs = keys.pop('programs')
            progs = progs.split()
            assert not keys
            if distro not in programs:
                programs[distro] = {}
            programs[distro][option] = progs
        return programs

    @staticmethod
    def install_pacman(packages, update=False, upgrade=False, sudo=False):
        cmd = ''
        if sudo:
            cmd += 'sudo'

        cmd += ' pacman -S'
        if update:
            cmd += 'yu'

        cmd = cmd.split() + packages
        Command(cmd).run()

    @staticmethod
    def install_apt(packages, update=False, upgrade=False, sudo=False):
        pfx = ''
        if sudo:
            pfx += 'sudo'
        pfx += ' apt-get '
        if update:
            cmd = pfx + 'update -y'
            Command(cmd.split()).run()
        if upgrade:
            cmd = pfx + 'dist-upgrade -y'
            Command(cmd.split()).run()

        cmd = pfx + ' install -y'
        cmd = cmd.split() + packages
        Command(cmd).run()

    @staticmethod
    def install_rust():
        subprocess.check_call("curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh", shell=True)

    @staticmethod
    def install_distro(distro, programs):
        installer = {
                'manjaro': Programs.install_pacman,
                'ubuntu': Programs.install_apt,
        }[distro]
        installer(programs, update=True, upgrade=True, sudo=True)

    def install_programs(self, distro, *options):
        programs = self.parse_program_config()
        program_list = programs[distro]['default']
        for option in options:
            program_list.extend(programs[distro][option])

        self.install_distro(distro, program_list)
        self.install_rust()

    def run(self):
        self.install_programs(self.distro)
        return 0


class Subrepos(Subcommand):
    name = 'subrepos'
    DEST = os.path.join(DIR, '../subrepos')
    CFG_PATH = os.path.join(DIR, 'subrepos.cfg')

    def init_parser(self, subparser):
        ARGS['overwrite'].add_to(subparser)
        ARGS['root'].add_to(subparser)
        subparser.add_argument('--rerun', action='store_true', help='Rerun setup scripts')
        subparser.add_argument('--relink', action='store_true', help='Relink all scripts in subrepos')

    def post_process_args(self, parser, args):
        self.overwrite = args.overwrite
        self.root = args.root
        self.rerun = args.rerun
        self.relink = args.relink

    @staticmethod
    def parse_subrepo_config():
        items = parse_config(Subrepos.CFG_PATH)
        # return: 
        # [
        # {
        #   'remote': path,
        #   'branch': master,
        #   'name': name
        # }
        # ]

        subrepos = {}
        for name, key in items.items():
            name = key.pop('name', name)
            name = join(Subrepos.DEST, name)
            remote = key.pop('remote')
            branch = key.pop('branch', None)
            setup = key.pop('setup', None)
            autolink = key.pop('autolink', '')
            if autolink.lower() == 'true':
                autolink = True
            subrepos[name] = {
                    'remote': remote,
                    'setup': setup,
                    'branch': branch,
                    'autolink': autolink,
                    }
            assert not key
        return subrepos

    @staticmethod
    def autolink(path, root, overwrite):
        # NOTE This method depends on completion of the dotfiles setup.
        root = join(root, '.local/bin')
        IGNORE = '.git'
        files = {}
        for path, dirs, fnames in os.walk(path):
            if IGNORE in splitall(path):
                continue
            for fname in fnames:
                src = os.path.join(path, fname)
                if os.access(src, os.X_OK):
                    dst = os.path.join(root, fname)
                    files[src] = dst
        link_files(overwrite, files)

    @staticmethod
    def clone(name, info, overwrite):
        cmd = 'git clone'.split() + [info['remote'], name]
        branch = info['branch']
        if branch:
            cmd.extend(['-b', branch])

        exists = os.path.exists(name) 
        if exists and not overwrite:
            print('Git subrepo \'%s\' already exists' % name)
            return False
        if exists and overwrite:
            print('Removing "%s"' % name)
            shutil.rmtree(name)
        print(cmd)
        subprocess.check_call(cmd)
        return True

    def setup_subrepos(self, root, relink, rerun, overwrite):
        subrepos = self.parse_subrepo_config()
        for name, info in subrepos.items():
            installed = self.clone(name, info, overwrite)
            setup = info['setup']
            link = info['autolink']
            if (installed or rerun) and setup:
                setup = os.path.join(name, setup)
                subprocess.check_call(setup)
            if (installed or relink) and link:
                self.autolink(name, root, overwrite)


    def run(self):
        self.setup_subrepos(self.root, self.relink, self.rerun, self.overwrite)
        return 0

class Dotfiles(Subcommand):
    '''
    Manage dotfiles/configs.
    '''
    name = 'dotfiles'
    SRC_PATH = os.path.join(DIR, '../dotfiles')
    CFG_PATH = os.path.join(DIR, 'dotfiles.cfg')

    def __init__(self):
        pass

    def init_parser(self, subparser):
        ARGS['root'].add_to(subparser)
        ARGS['overwrite'].add_to(subparser)

    def post_process_args(self, parser, args):
        self.overwrite = args.overwrite
        self.root = args.root

    @staticmethod
    def parse_dotfile_config(root):
        items = parse_config(Dotfiles.CFG_PATH)
        #import pdb;pdb.set_trace()

        # Attributes
        # Default is special
        src_dotfiles = items.pop('Default').pop('srcs').splitlines()
        src_dotfiles = (d for d in src_dotfiles if d)
        dotfiles = {}
        dirs = []
        for f in src_dotfiles:
            src = join(Dotfiles.SRC_PATH, f)
            dst = join(root, '.' + f)
            dotfiles[src] = dst

        ACCEPTED_KEYS = ['src', 'dst', 'dir']
        for _tag, keys in items.items():
            for key in keys:
                if key not in ACCEPTED_KEYS:
                    raise Exception('Invalid key "%s" in "%s"' % (key, Dotfiles.CFG_PATH))

            d = keys.pop('dir', None)
            if d:
                dirs.append(join(root, d))

            src = keys.pop('src', None)
            dst = keys.pop('dst', None)
            assert not keys

            if src and dst:
                src = join(Dotfiles.SRC_PATH, src)
                dst = join(root, dst)
                dotfiles[src] = dst
        return dirs, dotfiles

    def setup_dotfiles(self, overwrite, root):
        dirs, dotfiles = self.parse_dotfile_config(root)
        print('Creating the following directories:')
        for d in dirs:
            print('\t%s' % d)
            mkdir_p(d)
        link_files(overwrite, dotfiles)

    def run(self):
        self.setup_dotfiles(self.overwrite, self.root)
        return 0

class Setup(Subcommand):
    '''
    Perform initial setup/configuration on this host machine.
    '''
    name = 'setup'

    def __init__(self):
        self._sentinel = object()
        self.p = Programs()
        self.d = Dotfiles()
        self.s = Subrepos()

    def init_parser(self, subparser):
        self.p.init_parser(subparser)
        self.d.init_parser(subparser)
        self.s.init_parser(subparser)

    def post_process_args(self, parser, args):
        self.p.post_process_args(parser, args)
        self.d.post_process_args(parser, args)
        self.s.post_process_args(parser, args)

    def run(self):
        self.p.run()
        self.d.run()
        self.s.run()
        System.set_nopasswd_sudo()
        return 0

################################################
# Boilerplate for a standalone importable script

def main(argv):
    command = parse_args(argv)
    command.run()
    return 0

def entrypoint():
    '''
    Script entrypoint.
    '''
    sys.exit(main(sys.argv[1:]))

if __name__ == '__main__':
    entrypoint()
