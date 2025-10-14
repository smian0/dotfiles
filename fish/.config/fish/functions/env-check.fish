function env-check
    set -l var $argv[1]
    if test -z "$var"
        set var GITHUB_TOKEN
    end

    set -l system_val (launchctl getenv $var 2>/dev/null | head -c 20)
    set -l shell_val (printenv $var 2>/dev/null | head -c 20)

    echo "System (launchctl): $system_val..."
    echo "Shell (current):    $shell_val..."
end
