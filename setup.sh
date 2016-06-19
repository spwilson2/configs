#!/bin/bash

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
	DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
	SOURCE="$(readlink "$SOURCE")"
	[[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

FILES="bashrc     
gitconfig           
dircolors  
tmux.conf"

cd $DIR

for FILE in $FILES; do
    ln -s "$FILE" "$HOME/.$FILE"
done

# Run vim setup
git pull && git submodule init && git submodule update && git submodule status
bash "vim/setup.sh"
