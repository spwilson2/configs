"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""  =>                  Vundle                        """"
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
set nocompatible              " be iMproved, required
filetype off                  " required

" Find more plugins here
" http://vimawesome.com/

" set the runtime path to include Vundle and initialize
set rtp+=~/.vim/bundle/Vundle.vim
call vundle#begin()
" alternatively, pass a path where Vundle should install plugins
"call vundle#begin('~/some/path/here')

" let Vundle manage Vundle, required
Plugin 'VundleVim/Vundle.vim'

"""                     Colorschemes                   """"

" Plugin 'altercation/vim-colors-solarized'
Plugin 'jnurmine/Zenburn'


"""                     IDE Plugins                    """"
" Auto check syntax
Plugin 'scrooloose/syntastic'
" Improve folding of functions.
Plugin 'tmhedberg/SimpylFold'
" Autocompletion. Go to github for install docs. 
Plugin 'Valloric/YouCompleteMe'


""""            Better than an IDE Plugins             """"
" Helps with surrounding items in brackets/parthenesis etc.
" Plugin 'tpope/vim-surround'

" Better looking tagline - NOTE: Needs configurations.
" Plugin 'bling/vim-airline'

" Git integration
Plugin 'tpope/vim-fugitive'


""""               Filesystem Management                """"
" Ctrlp to search
" Plugin 'kien/ctrlp.vim'

" Plugin 'scrooloose/nerdtree'


"""                  Python Plugins                     """"
" PEP 8 checking ;)
Plugin 'nvie/vim-flake8'

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

" All of your Plugins must be added before the following line
call vundle#end()            " required
filetype plugin indent on    " required
" To ignore plugin indent changes, instead use:
"filetype plugin on
"
" Brief help
" :PluginList       - lists configured plugins
" :PluginInstall    - installs plugins; append `!` to update or just :PluginUpdate
" :PluginSearch foo - searches for foo; append `!` to refresh local cache
" :PluginClean      - confirms removal of unused plugins; append `!` to auto-approve removal
" see :h vundle for more details or wiki for FAQ
" Put your non-Plugin stuff after this line


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""  =>                  Configs                       """"
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Space is leader key
let mapleader=" "

" Turn backup off, since most stuff is in SVN, git et.c anyway...
set nobackup
set nowb
set noswapfile

set history=100 " Set the number of undos


" Let vim go past the last char.
set virtualedit=onemore

" Configure backspace to remove endlines and indents
set backspace=eol,start,indent

" Linebreak on 99 characters
set lbr
set tw=99
set formatoptions+=a

" Show the command in progress at bottom
set showcmd

" Always use *nix line endings.
set fileformat=unix

" Allow traveling between buffers without the error prompt (liberally hides buffers)
set hidden
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""  =>                  Functions                     """"
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

function PlainText()
    set spell spelllang=en
    setlocal formatoptions=1
    setlocal noexpandtab
    setlocal wrap
    setlocal linebreak
"   nnoremap j gj       
"   nnoremap k gk
    set formatprg=par
endfunction

" Preserves the previous state after running a command
function! Preserve(command)
  " Preparation: save last search, and cursor position.
  let _s=@/
  let l = line(".")
  let c = col(".")
  " Do the business:
  execute a:command
  " Clean up: restore previous search history, and cursor position
  let @/=_s
  call cursor(l, c)
endfunction 



"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""  =>                  Hotkeys                       """"
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Set the toggle for pastemode to <F2>
set pastetoggle=<F2>

" manually regen ctags
map <Leader>rt :!ctags --extra=+f -R *<CR><CR>

"split navigations
nnoremap <C-J> <C-W><C-J>
nnoremap <C-K> <C-W><C-K>
nnoremap <C-L> <C-W><C-L>
nnoremap <C-H> <C-W><C-H>

" Buffer navigation
nnoremap <silent> [b :bprevious<CR>
nnoremap <silent> ]b :bnext<CR>
nnoremap <silent> [B :bfirst<CR>
nnoremap <silent> ]B :blast<CR>

"Toggle linenumbers.
nmap <C-N> :set invnumber<CR>

" Remove the Windows ^M
noremap <Leader>m mmHmt:%s/<C-V><cr>//ge<cr>'tzt'm

" %% can be used to get the directory of the file in the current buffer.
cnoremap <expr> %% getcmdtype() == ':' ? expand('%:h').'/' : '%%'

" Remove trailing whitespace and preserve the previous search pattern
nmap _$ :call Preserve("%s/\\s\\+$//e")<CR>

"%% is maped to the directory of % (The active buffer)
cnoremap %% <C-R>=fnameescape(expand('%:h')).'/'<cr>
" Edit from current file directory
map <leader>ew :e %%
" Split from current file dir
map <leader>es :sp %%
" VSplit from current file dir
map <leader>ev :vsp %%
" Tab from currrent file dir
map <leader>et :tabe %%

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""  =>                  Visuals                       """"
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Show matching brackets
set showmatch
" Show line numbers
set number
" Always show ruler
set ruler

" Wrap lines
set wrap 

" Enable syntax highlighting
syntax enable

" Color setting
if has('gui_running')
    set background=dark
    colorscheme solarized
else
    colorscheme zenburn
    highlight Pmenu ctermfg=darkgreen  ctermbg=black
    highlight PmenuSel ctermfg=black  ctermbg=darkblue
endif

" No annoying sound on errors
set noerrorbells
set novisualbell

" Move vertically earlier
set so=7

"" Add a bit extra margin to the left
"set foldcolumn=1

"" Set color of the line numbers
":highlight LineNr term=bold cterm=NONE ctermfg=DarkGrey ctermbg=NONE gui=NONE guifg=DarkGrey guibg=NONE

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""  =>                  Searches                      """"
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" When searching try to be smart about cases
set ignorecase
set smartcase
set incsearch 

" Highlight search results
" set hls

" Toggle highlight
noremap <silent> <Leader>l :set invhls<cr><C-l>

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""  =>                  Status                        """"
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Always show the status line
set laststatus=2

" Format the status line
set statusline=\ %{HasPaste()}%F%m%r%h\ %w\ \ CWD:\ %r%{getcwd()}%h\ \ \ Line:\ %l
" Returns true if paste mode is enabled
function! HasPaste()
    if &paste
        return 'PASTE MODE '
    en
    return ''
endfunction

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""  =>                  Tabs                          """"
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
set shiftwidth=4   " Width for > and < vcmds
set tabstop=4      " Visual length of tabs
set softtabstop=4  " Length to use spaces at instead of tabs
set expandtab      " Use spaces instead of tabs
set smarttab       " Tab to previous set lines
set autoindent     " Auto indent following lines

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""  =>                  Filetype configs              """"
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

"""""         All            """"""
if has("autocmd")
" Return to last edit position when opening files
 au BufReadPost *
 \ if line("'\"") > 0 && line("'\"") <= line("$") |
 \ exe "normal! g`\"" |
 \ endif


"""""         Make            """"""
au FileType make setl noexpandtab "On make files, don't use tab rules

"""""         Python          """"""
" PEP8 Compliant ;)
au BufNewFile,BufRead *.py
    \setl tabstop=4|
    \setl softtabstop=4|
    \setl shiftwidth=4|
    \setl textwidth=79|
    \setl expandtab|
    \setl encoding=utf-8|
    \let python_highlight_all=1
    
" auto remove trailing whitespace on save
au BufWritePre *.py :call Preserve("%s/\\s\\+$//e")<CR>

" Source the vimrc file after saving it
autocmd bufwritepost .vimrc source $MYVIMRC

endif

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""  =>               Plugin Configs                   """"
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

" syntastic, if python 3 not working. Set the path.
let g:syntastic_python_python_exec = '/usr/bin/python3'

" nerdtree
" map <Tab> :NERDTreeToggle<CR>
" autocmd bufenter * if (winnr("$") == 1 && exists("b:NERDTree") && b:NERDTree.isTabTree()) | q | endif

" ctrlp
" Search through ctags with <,.>
nnoremap <leader>c :CtrlPTag<cr> 

" Fold functions
" SimpylFold
set foldmethod=indent
set foldlevel=99

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""  =>                  Misc                          """"
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"Reminders:
"To make use of syntastic and vim-flake8 you need to have flake8 and pylint installed.

"set whichwrap+=<,>",h,l

" Linux standards.
"nmap <c-l> :set tabstop=8 softtabstop=8 shiftwidth=8 noexpandtab<CR>
