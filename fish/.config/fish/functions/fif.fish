function fif
    grep -r --include="*.$argv[2]" "$argv[1]" .
end
