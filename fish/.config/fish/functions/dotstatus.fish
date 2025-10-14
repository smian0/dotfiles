function dotstatus
    echo "Dotfiles Status:"
    echo "==============="
    cd ~/dotfiles

    echo "Available packages:"
    for package in (ls -1 | grep -v README.md)
        if test -d $package
            # Check if package is stowed by looking for symlinks
            set -l stowed false
            for link in (find $HOME -maxdepth 2 -type l 2>/dev/null)
                set -l target (readlink $link 2>/dev/null)
                if string match -q "*$PWD/$package*" $target
                    set stowed true
                    break
                end
            end

            if test $stowed = true
                echo "  ✓ $package (stowed)"
            else
                echo "  ○ $package (not stowed)"
            end
        end
    end
end
