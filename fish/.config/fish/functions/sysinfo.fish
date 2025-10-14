function sysinfo
    echo "System Information:"
    echo "=================="
    echo "OS: "(uname -s)
    echo "Kernel: "(uname -r)
    echo "Architecture: "(uname -m)
    if command -v sw_vers >/dev/null 2>&1
        echo "macOS Version: "(sw_vers -productVersion)
    end
    echo "Shell: $SHELL"
    echo "Terminal: $TERM"
    echo "User: $USER"
    echo "Home: $HOME"
    echo "Working Directory: $PWD"
    echo "Date: "(date)
    echo "Uptime: "(uptime)
end
