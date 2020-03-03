# -*- coding: utf-8 -*-
from __future__ import print_function

'''
This script is used to setup and configure a new system using custom config
definitions and overlays.
'''

import argparse
import os
import re
import subprocess
import sys

#############################
# Constants
# Constants
#############################


# Use bitbake as a sort of example
# Setup files will be exec'd
#

# Core capabilities:
# - Overlays:
#   - diffs
#   - sed replace
# - Full configs:
#  - vimrc, vim, bashrc, profile
# - Dependencies 
#  - High-order configs - e.g. Ubuntu
#   - Lower-order e.g. 
# - Options:
#   - e.g. GHS

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
        return parser.add_argument(*self.args, **self.kwargs)

# Common Arguments
ARGS = {
        'base': Argument('--base', 
            default=None, required=False, 
            help='Directory to place dotfiles and .local into.'),
        'overwrite': Argument('--overwrite', '-f', 
            action='store_true', required=False,
            help='Allow overwriting of existing config files'),
        'distro': Argument('--distro', 
            required=False,
            help=('Manually specify the distro to use '
            '(otherwise automatically detected).'))
}

# Script utilities
#############################
class Programs(Subcommand):
    '''
    Manage programs.
    '''
    name = 'programs'
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

    def run(self):
        import cs_programs
        kwargs = {
                'distro': self.distro,
                'update': False,
                'upgrade': False,
                'sudo':False,
                }
        cs_programs.install(**kwargs)
        return 0

class Dotfiles(Subcommand):
    '''
    Manage dotfiles/configs.
    '''
    name = 'dotfiles'
    def __init__(self):
        pass

    def init_parser(self, subparser):
        ARGS['base'].add_to(subparser)
        ARGS['overwrite'].add_to(subparser)
        subparser.add_argument('--use-i3', action='store_true')

    def post_process_args(self, parser, args):
        self.overwrite = args.overwrite
        self.use_i3 = args.use_i3

    def run(self):
        import cs_configs
        kwargs = {
                'overwrite': self.overwrite,
                'i3': self.use_i3
                }
        cs_configs.dotfiles(**kwargs)
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

    def init_parser(self, subparser):
        self.p.init_parser(subparser)
        self.d.init_parser(subparser)

    def post_process_args(self, parser, args):
        self.p.post_process_args(parser, args)
        self.d.post_process_args(parser, args)

    def run(self):
        ret = self.p.run()
        if ret:
            return ret
        ret = self.d.run()
        import cs_sudo
        cs_sudo.System.set_nopasswd_sudo()
        return ret

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
