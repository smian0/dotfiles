function pcp
    if test (count $argv) -eq 0
        echo "Usage: pcp <service>"
        return 1
    end
    pass show -c "api/$argv[1]" 2>/dev/null
end
