#!/bin/bash
set -ex
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
	DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
	SOURCE="$(readlink "$SOURCE")"
	[[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done

DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

cd "$DIR"

FILES="$(cat FILES)"

set +e
for FILE in $FILES; do
    ln -s "$DIR/$FILE" "$HOME/.$FILE"
done

# Run vim setup
git pull; git submodule update --init --recursive
bash "vim/setup.sh"
