#!/bin/bash

FILES="bashrc     
gitconfig           
setup.sh
dircolors  
tmux.conf
"

for FILE in $FILES; do
    cp $FILE ~/.$FILE
done
