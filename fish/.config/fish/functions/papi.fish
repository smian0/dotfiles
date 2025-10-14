function papi
    if test (count $argv) -eq 0
        echo "Usage: papi <service>"
        echo "Available services:"
        pass ls api 2>/dev/null | grep -v "^api\$" | sed 's/^[├└│─ ]*/  /'
        return 1
    end
    pass show "api/$argv[1]" 2>/dev/null | head -1
end
