function dotadd
    if test (count $argv) -eq 0
        echo "Usage: dotadd <package>"
        echo "Available packages:"
        ls ~/dotfiles/
        return 1
    end
    cd ~/dotfiles; and stow --target=$HOME $argv[1]
end
