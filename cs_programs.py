# -*- coding: utf-8 -*-
'''
This file is reponsible for selecting all programs to install on the
system.
'''

from confsys import Command

# TODO Move these packages into .toml files for easy automated editing
UBUNTU_PACKAGES = '''
openssh-server
python3 python3-pip python-pip python-dev python3-dev
cmake build-essential scons m4
libncurses5-dev libssl-dev libgoogle-perftools-dev 
ctags vim tmux silversearcher-ag cscope 
'''.split()

# TODO nvidia drivers:

MANJARO_I3_PACKAGES = '''
i3-scripts
xfce4-power-manager-gtk3
'''

MANJARO_LAPTOP_PACKAGES = ('''
tlpui
'''
# NVIDIA P1000 drivers, TODO May need to mhwd to switch
'''
linux419-nvidia-440xx
xf86-video-nouveau
''')

MANJARO_PACKAGES = '''
elfutils cscope ctags gvim the_silver_searcher
rustup go ninja npm

firefox transmission-gtk tigervnc iotop xfce4-terminal
remmina freerdp
'''

def install_pacman(packages, update=False, upgrade=False, sudo=False):
    cmd = ''
    if sudo:
        cmd += 'sudo'

    cmd += ' pacman -S'
    if update:
        cmd += 'yu'

    cmd = cmd.split() + packages
    Command(cmd).run()

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

def install(distro, **kwargs):
    print(distro)
    if distro == 'manjaro':
        packages = MANJARO_PACKAGES
        install_pacman(packages, **kwargs)

    if distro == 'ubuntu':
        packages = UBUNTU_PACKAGES
        install_apt(packages, **kwargs)
        # TODO Add base utilities to detect the version of ubuntu to select
        # subset of packages (with correct naming)

if __name__ == '__main__':
    pass
