#!/bin/bash

# Google Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i --force-depends google-chrome-stable_current_amd64.deb
sudo apt-get update
sudo apt-get install -f -y

# i3 fix display settings
gsettings set org.gnome.desktop.background show-desktop-icons false

# Other programs
sudo apt-get update
sudo apt-get install $(cat programs) -y
sudo apt-get dist-upgrade 

# Neovim, relies on python3
sudo add-apt-repository ppa:neovim-ppa/unstable
sudo apt-get update
sudo apt-get install neovim
sudo pip3 install neovim
