function dotremove
    if test (count $argv) -eq 0
        echo "Usage: dotremove <package>"
        return 1
    end
    cd ~/dotfiles; and stow --delete --target=$HOME $argv[1]
end
