# Claude Credentials in macOS Keychain

This document explains how to find and access Claude Code credentials stored in the macOS Keychain.

## 🔍 Quick Reference

**Entry Details:**
- **Service**: `Claude Code-credentials`
- **Account**: `smian`
- **Keychain**: Login Keychain
- **Type**: Generic Password
- **Created**: August 20, 2025

## 📋 Finding Credentials in Keychain Access UI

### Method 1: GUI Search (Recommended)

1. **Open Keychain Access**
   ```bash
   open -a "Keychain Access"
   ```

2. **Select the correct keychain and category:**
   - In left sidebar, click **"login"** (NOT "System" or "System Roots")
   - In category list, select **"All Items"** (sometimes "Passwords" doesn't show all entries)

3. **Search for the credential:**
   - In search box (top-right), type: `Claude Code-credentials`
   - Or search for just: `Claude`

4. **View the password:**
   - Double-click the "Claude Code-credentials" entry
   - Check **"Show password"** checkbox
   - Enter your Mac password when prompted

### Method 2: Alternative UI Search

If the entry doesn't appear with the above steps:

1. **Try different category views:**
   - Click "Passwords" category
   - Click "All Items" category
   - Try sorting by "Name" column

2. **Refresh the view:**
   - Close and reopen Keychain Access
   - Try cmd+R to refresh

3. **Search variations:**
   - Search for: `Claude`
   - Search for: `credentials`
   - Search for account: `smian`

## 💻 Command Line Methods

### View Entry Information
```bash
# Show entry details (no password)
security find-generic-password -s "Claude Code-credentials" -a "smian"
```

### Get Password (Interactive)
```bash
# Will prompt for Mac password, then display the credential password
security find-generic-password -s "Claude Code-credentials" -a "smian" -g
```

### Copy Password to Clipboard
```bash
# Copy password directly to clipboard (prompts for Mac password)
security find-generic-password -s "Claude Code-credentials" -a "smian" -w | pbcopy
```

### Search All Claude Entries
```bash
# Find any keychain entries related to Claude
security dump-keychain | grep -i "claude" -A 3 -B 1
```

## 🔧 Troubleshooting

### "Item could not be found"
- Make sure you're searching in the **login keychain**, not system keychain
- The entry name is case-sensitive: `Claude Code-credentials`
- Account name is: `smian`

### UI Not Showing Entry
- Switch to **"All Items"** category instead of "Passwords"
- Close and reopen Keychain Access
- Try searching for partial names like "Claude" or "credentials"
- Sort entries by Name column to scan manually

### Permission Denied
- The terminal commands will prompt for your Mac user password
- Make sure you enter your Mac login password (not Claude password)
- If using Touch ID, you may need to use password instead

## 📝 Entry Details Reference

```
Service: Claude Code-credentials
Account: smian  
Keychain: /Users/smian/Library/Keychains/login.keychain-db
Type: Generic Password (genp)
Created: 2025-08-20 06:51:03Z
Modified: 2025-08-20 06:51:03Z
```

## 🛡️ Security Notes

- This keychain entry likely contains Claude authentication tokens
- Never share these credentials or commit them to version control
- The password field may contain JSON with OAuth tokens or API keys
- Treat this as sensitive information equivalent to passwords

## 🔗 Related Files

- `KNOWN_ISSUES.md` - OAuth authentication bug documentation
- `USAGE.md` - OAuth token generation instructions  
- `index.ts` - OAuth token generator that may create keychain entries

---

**Last Updated:** August 20, 2025  
**Keychain Path:** `/Users/smian/Library/Keychains/login.keychain-db`