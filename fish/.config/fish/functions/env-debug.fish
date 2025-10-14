function env-debug
    if test -x $HOME/dotfiles/scripts/env-debug.sh
        $HOME/dotfiles/scripts/env-debug.sh
    else
        echo "env-debug.sh not found or not executable"
    end
end
