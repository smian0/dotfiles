# Remote Access Setup

This guide covers setting up remote access tools for secure connections to your machines.

## Mosh (Mobile Shell)

Mosh is a remote terminal application that allows roaming, supports intermittent connectivity, and provides intelligent local echo and line editing of user keystrokes.

### Features

- **Persistent connections** - Survives network changes, WiFi roaming, and sleep/wake
- **UDP-based** - Better performance over lossy networks (60000-61000)
- **Instant responsiveness** - Local echo for faster typing
- **No SSH multiplexing conflicts** - Works alongside SSH

### Installation

Mosh is automatically installed as part of the dotfiles setup:

```bash
# Complete dotfiles installation (includes mosh)
make install

# Or install specific packages
make install-minimal  # Includes mosh
make install-zsh      # Includes .zshenv with PATH fix

# Manual installation only
brew install mosh  # macOS
sudo apt-get install mosh  # Ubuntu
```

### Automated Configuration (Recommended)

After installing dotfiles, run the optional mosh configuration:

```bash
# Interactive setup (asks for confirmation at each step)
make setup-mosh

# Or run the script directly
./scripts/setup-mosh.sh
```

This will:
1. ✅ Enable SSH server (Remote Login)
2. ✅ Set up SSH keys for localhost
3. ✅ Configure macOS firewall
4. ✅ Test mosh connection

**Note:** The `.zshenv` file with Homebrew PATH is automatically installed with the zsh package, ensuring mosh-server is always accessible in SSH sessions.

### Verification

```bash
# Check mosh installation
which mosh
which mosh-server

# Check version
mosh --version
```

On macOS (Apple Silicon), mosh is typically installed at:
- `/opt/homebrew/bin/mosh`
- `/opt/homebrew/bin/mosh-server`

On macOS (Intel), it's at:
- `/usr/local/bin/mosh`
- `/usr/local/bin/mosh-server`

### macOS Firewall Configuration

Mosh uses UDP ports 60000-61000 for connections. On macOS, you need to configure the firewall to allow mosh-server:

#### Automatic Configuration

Run the included firewall configuration script:

```bash
./scripts/configure-mosh-firewall.sh
```

This script will:
1. Add mosh-server to the firewall allowed applications
2. Enable incoming connections for mosh-server
3. Reload firewall rules
4. Verify the configuration

#### Manual Configuration

If you prefer to configure manually:

1. **Open System Settings**
   - Go to: System Settings > Network > Firewall > Options

2. **Add mosh-server**
   - Click the `+` button
   - Navigate to the mosh-server location (use `which mosh-server` to find it)
   - Typical locations:
     - Apple Silicon: `/opt/homebrew/bin/mosh-server`
     - Intel: `/usr/local/bin/mosh-server`

3. **Allow Incoming Connections**
   - Set mosh-server to "Allow incoming connections"

4. **Reload Firewall Rules** (optional)
   ```bash
   sudo pfctl -f /etc/pf.conf
   ```

### Usage

#### Basic Connection

```bash
# Connect to remote host
mosh user@hostname

# Connect on specific SSH port
mosh --ssh="ssh -p 2222" user@hostname

# Use specific server port range
mosh -p 60000:60010 user@hostname
```

#### Advanced Usage

```bash
# Specify mosh-server path on remote
mosh --server=/custom/path/mosh-server user@hostname

# Use IPv6
mosh -6 user@hostname

# Disable prediction (useful on fast connections)
mosh --predict=never user@hostname
```

### Troubleshooting

#### Connection Issues

**Problem**: "mosh-server not found"
```bash
# On remote machine, install mosh
brew install mosh  # macOS
sudo apt-get install mosh  # Ubuntu
```

**Problem**: "Connection timed out"
- Check that firewall allows UDP ports 60000-61000
- Verify SSH connection works first: `ssh user@hostname`
- Check router doesn't block UDP ports
- Try specifying a smaller port range: `mosh -p 60000:60010 user@hostname`

**Problem**: "locale-related error"
```bash
# On local machine, ensure locale is set
echo 'export LC_ALL=en_US.UTF-8' >> ~/.zshrc
echo 'export LANG=en_US.UTF-8' >> ~/.zshrc
```

#### Firewall Issues on macOS

**Problem**: Firewall blocks mosh-server
```bash
# Run the firewall configuration script
./scripts/configure-mosh-firewall.sh

# Or manually check firewall settings
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --listapps
```

**Problem**: Rules not taking effect
```bash
# Reload firewall
sudo pfctl -f /etc/pf.conf

# Or disable/enable firewall in System Settings
```

#### Router Configuration

Some routers may block UDP traffic or specific ports. Check your router settings:

1. Port forwarding: Forward UDP 60000-61000 to your machine
2. UPnP/NAT-PMP: Enable if available
3. DMZ: As last resort, place machine in DMZ (less secure)

### Best Practices

1. **Use with SSH keys** - Set up SSH key authentication first
2. **Test SSH first** - Always verify SSH works before trying mosh
3. **Limit port range** - Use `-p 60000:60010` for better security
4. **Keep updated** - Run `brew upgrade mosh` regularly
5. **Use for mobile** - Ideal for laptop users with WiFi roaming

### Integration with Dotfiles

Mosh is integrated into the dotfiles in the following ways:

1. **Automatic Installation**
   - Added to `install.sh` for both macOS and Ubuntu
   - Installs via Homebrew on macOS: `brew install mosh`
   - Installs via apt on Ubuntu: `apt-get install mosh`

2. **Firewall Configuration**
   - Script: `scripts/configure-mosh-firewall.sh`
   - Automatically configures macOS firewall

3. **Documentation**
   - This guide: `docs/REMOTE-ACCESS.md`
   - Troubleshooting: Included in this document

### Security Considerations

- Mosh uses SSH for authentication (same security as SSH)
- Connection is encrypted using AES-128-OCB
- No additional authentication needed beyond SSH
- UDP ports 60000-61000 should be protected by firewall
- Consider using VPN for additional security on public networks

### Performance Tips

1. **Fast Networks**: Disable prediction for less visual artifacts
   ```bash
   mosh --predict=never user@hostname
   ```

2. **Slow Networks**: Enable adaptive prediction (default)
   ```bash
   mosh --predict=adaptive user@hostname
   ```

3. **High Latency**: Use experimental features
   ```bash
   mosh --predict=experimental user@hostname
   ```

### References

- [Mosh Official Website](https://mosh.org)
- [Mosh GitHub Repository](https://github.com/mobile-shell/mosh)
- [Mosh Technical Paper](https://mosh.org/mosh-paper.pdf)

---

*Last Updated: 2025-10-19*
