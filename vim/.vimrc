" Vim Configuration for Dotfiles Management
" Auto-managed by dotfiles system

" =============================================================================
" Basic Settings
" =============================================================================

set nocompatible                " Disable vi compatibility
set encoding=utf-8              " Set encoding to UTF-8
set fileencoding=utf-8          " Set file encoding to UTF-8
set backspace=indent,eol,start  " Allow backspace over everything
set history=1000                " Keep 1000 lines of command history
set undolevels=1000             " Allow 1000 undo levels

" =============================================================================
" Display Settings
" =============================================================================

syntax on                       " Enable syntax highlighting
set number                      " Show line numbers
set relativenumber              " Show relative line numbers
set ruler                       " Show cursor position
set showmode                    " Show current mode
set showcmd                     " Show partial commands
set cursorline                  " Highlight current line
set wrap                        " Wrap long lines
set linebreak                   " Break lines at word boundaries
set showmatch                   " Show matching brackets
set matchtime=2                 " Show matches for 0.2 seconds

" Colors and themes
set t_Co=256                    " Enable 256 colors
colorscheme desert              " Set color scheme (fallback)
set background=dark             " Use dark background

" Status line
set laststatus=2                " Always show status line
set statusline=%f               " Filename
set statusline+=%m              " Modified flag
set statusline+=%r              " Read-only flag
set statusline+=%=              " Switch to right side
set statusline+=%l/%L           " Line number / total lines
set statusline+=\ %c            " Column number
set statusline+=\ %P            " Percentage through file

" =============================================================================
" Search Settings
" =============================================================================

set hlsearch                    " Highlight search results
set incsearch                   " Incremental search
set ignorecase                  " Ignore case in search
set smartcase                   " Case-sensitive if uppercase present
set wrapscan                    " Wrap search around file

" =============================================================================
" Indentation and Formatting
" =============================================================================

set autoindent                  " Auto-indent new lines
set smartindent                 " Smart indentation
set tabstop=4                   " Tab width
set shiftwidth=4                " Indentation width
set expandtab                   " Use spaces instead of tabs
set smarttab                    " Smart tab behavior
set softtabstop=4               " Soft tab stop

" File type specific settings
autocmd FileType yaml setlocal ts=2 sts=2 sw=2 expandtab
autocmd FileType yml setlocal ts=2 sts=2 sw=2 expandtab
autocmd FileType json setlocal ts=2 sts=2 sw=2 expandtab
autocmd FileType javascript setlocal ts=2 sts=2 sw=2 expandtab
autocmd FileType typescript setlocal ts=2 sts=2 sw=2 expandtab
autocmd FileType html setlocal ts=2 sts=2 sw=2 expandtab
autocmd FileType css setlocal ts=2 sts=2 sw=2 expandtab
autocmd FileType python setlocal ts=4 sts=4 sw=4 expandtab
autocmd FileType sh setlocal ts=4 sts=4 sw=4 expandtab
autocmd FileType bash setlocal ts=4 sts=4 sw=4 expandtab

" =============================================================================
" File Management
" =============================================================================

set autoread                    " Auto-reload files changed outside vim
set backup                      " Keep backup files
set backupdir=~/.vim/backup//   " Backup directory
set directory=~/.vim/swap//     " Swap file directory
set undofile                    " Persistent undo
set undodir=~/.vim/undo//       " Undo directory

" Create directories if they don't exist
if !isdirectory($HOME."/.vim/backup")
    call mkdir($HOME."/.vim/backup", "p", 0700)
endif
if !isdirectory($HOME."/.vim/swap")
    call mkdir($HOME."/.vim/swap", "p", 0700)
endif
if !isdirectory($HOME."/.vim/undo")
    call mkdir($HOME."/.vim/undo", "p", 0700)
endif

" =============================================================================
" Key Mappings
" =============================================================================

" Set leader key
let mapleader = ","

" Quick save and quit
nnoremap <Leader>w :w<CR>
nnoremap <Leader>q :q<CR>
nnoremap <Leader>x :x<CR>

" Clear search highlighting
nnoremap <Leader>/ :nohlsearch<CR>

" Navigate between windows
nnoremap <C-h> <C-w>h
nnoremap <C-j> <C-w>j
nnoremap <C-k> <C-w>k
nnoremap <C-l> <C-w>l

" Navigate between tabs
nnoremap <Leader>tn :tabnext<CR>
nnoremap <Leader>tp :tabprevious<CR>
nnoremap <Leader>tt :tabnew<CR>
nnoremap <Leader>tc :tabclose<CR>

" Move lines up and down
nnoremap <Leader>j :m .+1<CR>==
nnoremap <Leader>k :m .-2<CR>==
vnoremap <Leader>j :m '>+1<CR>gv=gv
vnoremap <Leader>k :m '<-2<CR>gv=gv

" Copy to system clipboard
vnoremap <Leader>y "+y
nnoremap <Leader>Y "+yg_
nnoremap <Leader>yy "+yy

" Paste from system clipboard
nnoremap <Leader>p "+p
nnoremap <Leader>P "+P
vnoremap <Leader>p "+p
vnoremap <Leader>P "+P

" =============================================================================
" Editing Enhancements
" =============================================================================

set wildmenu                    " Enhanced command completion
set wildmode=list:longest       " Complete longest common string
set completeopt=menuone,longest " Completion options
set pumheight=15                " Limit popup menu height

" Show whitespace characters
set list
set listchars=tab:▸\ ,trail:·,extends:❯,precedes:❮,nbsp:×

" Folding
set foldmethod=indent           " Fold based on indentation
set foldlevelstart=99           " Start with all folds open
set foldnestmax=10              " Maximum fold nesting

" =============================================================================
" Security Settings
" =============================================================================

set modelines=0                 " Disable modelines for security
set nomodeline                  " Disable modeline processing

" =============================================================================
" File Type Detection
" =============================================================================

filetype on                     " Enable file type detection
filetype plugin on              " Enable file type plugins
filetype indent on              " Enable file type indentation

" Custom file type associations
autocmd BufNewFile,BufRead *.zsh-theme set filetype=zsh
autocmd BufNewFile,BufRead *.conf set filetype=conf
autocmd BufNewFile,BufRead *.log set filetype=messages
autocmd BufNewFile,BufRead Dockerfile* set filetype=dockerfile
autocmd BufNewFile,BufRead *.env set filetype=sh
autocmd BufNewFile,BufRead .env* set filetype=sh

" =============================================================================
" Plugin Configuration
" =============================================================================

" Basic plugin management (if plugins are installed)
if isdirectory($HOME."/.vim/pack")
    packloadall         " Load all packages
    silent! helptags ALL    " Generate help tags
endif

" =============================================================================
" Custom Functions
" =============================================================================

" Toggle line numbers
function! ToggleNumbers()
    if &relativenumber
        set norelativenumber
        set number
    elseif &number
        set nonumber
    else
        set relativenumber
    endif
endfunction
nnoremap <Leader>n :call ToggleNumbers()<CR>

" Strip trailing whitespace
function! StripTrailingWhitespace()
    let l:save = winsaveview()
    keeppatterns %s/\s\+$//e
    call winrestview(l:save)
endfunction
nnoremap <Leader>ss :call StripTrailingWhitespace()<CR>

" Toggle paste mode
function! TogglePaste()
    if &paste
        set nopaste
        echo "Paste mode OFF"
    else
        set paste
        echo "Paste mode ON"
    endif
endfunction
nnoremap <Leader>pp :call TogglePaste()<CR>

" =============================================================================
" Auto Commands
" =============================================================================

" Auto-strip trailing whitespace for certain file types
autocmd BufWritePre *.py,*.js,*.ts,*.sh,*.bash,*.zsh call StripTrailingWhitespace()

" Return to last edit position when opening files
autocmd BufReadPost *
     \ if line("'\"") > 0 && line("'\"") <= line("$") |
     \   exe "normal! g`\"" |
     \ endif

" Highlight TODO, FIXME, NOTE, etc.
autocmd BufWinEnter * match Todo /\v<(TODO|FIXME|NOTE|HACK|BUG):/

" =============================================================================
" Load Local Configuration
" =============================================================================

" Load machine-specific configuration if it exists
if filereadable($HOME."/.vimrc.local")
    source $HOME/.vimrc.local
endif

" Load work-specific configuration if it exists
if filereadable($HOME."/.vimrc.work")
    source $HOME/.vimrc.work
endif