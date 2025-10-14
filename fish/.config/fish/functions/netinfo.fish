function netinfo
    echo "Network Information:"
    echo "==================="
    set -l local_ip (ipconfig getifaddr en0 2>/dev/null; or echo 'Not connected')
    set -l public_ip (curl -s https://ipinfo.io/ip 2>/dev/null; or echo 'Not available')
    set -l wifi (networksetup -getairportnetwork en0 2>/dev/null | cut -d: -f2 | xargs)

    echo "Local IP: $local_ip"
    echo "Public IP: $public_ip"
    echo "WiFi Network: $wifi"
end
