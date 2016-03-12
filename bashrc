alias ytdl="youtube-dl --extract-audio --audio-format mp3 --yes-playlist --ignore-errors"
alias uwssh='ssh swilson@cs.wisc.edu'
alias uplssh='ssh swilson@upl.cs.wisc.edu'
eval $(dircolors -b .dir_colors)
export PAGER=less
export EDITOR=vim
export VISUAL=vim
git config --global push.default simple
git config --global user.name "Sean Wilson"
git config --global user.email "spwilson27@gmail.com"

# Add svn aliases..
git config --global alias.st status
git config --global alias.up pull
git config --global alias.update pull