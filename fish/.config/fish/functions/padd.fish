function padd
    if test (count $argv) -eq 0
        echo "Usage: padd <service>"
        return 1
    end
    pass insert "api/$argv[1]"
end
