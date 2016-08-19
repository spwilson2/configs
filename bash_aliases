# Some more ls aliases
alias ll='ls -l'
alias la='ls -A'
alias l='ls'
alias sl='ls'

function ytdl {
  youtube-dl --extract-audio --audio-format mp3 --yes-playlist --ignore-errors -q $1 &&\
  find -name "* *" -type f | rename "s/ /_/g"
}

alias uwssh='ssh swilson@cs.wisc.edu'
alias uplssh='ssh swilson@upl.cs.wisc.edu'
alias cd..='cd ..'

# enable color support of ls and also add handy aliases
if [ -x /usr/bin/dircolors ]; then
    test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
    alias ls='ls --color=auto'
    alias dir='dir --color=auto'
    alias vdir='vdir --color=auto'

    alias grep='grep --color=auto'
    alias fgrep='fgrep --color=auto'
    alias egrep='egrep --color=auto'
fi
