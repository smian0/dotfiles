#!/usr/bin/env bash
# Bash completion for dotfiles scripts

_dotfiles_install() {
    local cur prev opts packages profiles
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # Available packages
    packages="git zsh vim claude-default claude-experimental npm-configs config bin pass direnv"
    
    # Available profiles
    profiles="minimal development full work personal"
    
    # Options
    opts="--all --help --dry-run --verbose --force --claude-profile --profile --backup"
    
    # Handle specific flags
    case $prev in
        --claude-profile)
            COMPREPLY=($(compgen -W "default experimental" -- "$cur"))
            return 0
            ;;
        --profile)
            COMPREPLY=($(compgen -W "$profiles" -- "$cur"))
            return 0
            ;;
        --backup)
            COMPREPLY=($(compgen -d -- "$cur"))
            return 0
            ;;
    esac
    
    # Handle options starting with --
    if [[ $cur == --* ]]; then
        COMPREPLY=($(compgen -W "$opts" -- "$cur"))
        return 0
    fi
    
    # Handle package names
    COMPREPLY=($(compgen -W "$packages $opts" -- "$cur"))
}

_dotfiles_backup_restore() {
    local cur prev opts commands
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    commands="backup restore list clean verify"
    opts="--help --verbose --dry-run --exclude-secrets --include-brew --backup-dir"
    
    # First argument should be a command
    if [[ $COMP_CWORD -eq 1 ]]; then
        COMPREPLY=($(compgen -W "$commands" -- "$cur"))
        return 0
    fi
    
    # Handle specific flags
    case $prev in
        --backup-dir)
            COMPREPLY=($(compgen -d -- "$cur"))
            return 0
            ;;
        restore|verify)
            # Complete with available backup timestamps
            local backup_dir="${HOME}/.dotfiles-backups"
            if [[ -d "$backup_dir" ]]; then
                local backups=$(ls "$backup_dir"/*.tar.gz 2>/dev/null | xargs -n1 basename | sed 's/.tar.gz$//')
                COMPREPLY=($(compgen -W "$backups" -- "$cur"))
            fi
            return 0
            ;;
    esac
    
    # Handle options
    if [[ $cur == --* ]]; then
        COMPREPLY=($(compgen -W "$opts" -- "$cur"))
        return 0
    fi
}

_dotfiles_profile_manager() {
    local cur prev opts commands profiles
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    commands="list install status check uninstall"
    profiles="minimal development full work personal"
    opts="--help --verbose --dry-run --force"
    
    # First argument should be a command
    if [[ $COMP_CWORD -eq 1 ]]; then
        COMPREPLY=($(compgen -W "$commands" -- "$cur"))
        return 0
    fi
    
    # Handle install command - suggest profiles
    if [[ "${COMP_WORDS[1]}" == "install" ]] && [[ $COMP_CWORD -eq 2 ]]; then
        COMPREPLY=($(compgen -W "$profiles" -- "$cur"))
        return 0
    fi
    
    # Handle options
    if [[ $cur == --* ]]; then
        COMPREPLY=($(compgen -W "$opts" -- "$cur"))
        return 0
    fi
}

_dotfiles_api_key_manager() {
    local cur prev opts commands services
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    commands="add get list remove sync status test"
    services="openai anthropic github aws azure gcp"
    opts="--help --verbose --dry-run --pass-store --env-file"
    
    # First argument should be a command
    if [[ $COMP_CWORD -eq 1 ]]; then
        COMPREPLY=($(compgen -W "$commands" -- "$cur"))
        return 0
    fi
    
    # Handle commands that need service names
    case "${COMP_WORDS[1]}" in
        add|get|remove|test)
            if [[ $COMP_CWORD -eq 2 ]]; then
                COMPREPLY=($(compgen -W "$services" -- "$cur"))
                return 0
            fi
            ;;
    esac
    
    # Handle options
    if [[ $cur == --* ]]; then
        COMPREPLY=($(compgen -W "$opts" -- "$cur"))
        return 0
    fi
}

_dotfiles_gpg_manager() {
    local cur prev opts commands
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    commands="export import backup restore list generate status"
    opts="--help --verbose --dry-run --key-id --backup-file --force"
    
    # First argument should be a command
    if [[ $COMP_CWORD -eq 1 ]]; then
        COMPREPLY=($(compgen -W "$commands" -- "$cur"))
        return 0
    fi
    
    # Handle specific flags
    case $prev in
        --key-id)
            # Complete with available GPG key IDs
            local keys=$(gpg --list-secret-keys --keyid-format SHORT 2>/dev/null | grep "sec" | awk '{print $2}' | cut -d'/' -f2)
            COMPREPLY=($(compgen -W "$keys" -- "$cur"))
            return 0
            ;;
        --backup-file)
            COMPREPLY=($(compgen -f -- "$cur"))
            return 0
            ;;
    esac
    
    # Handle options
    if [[ $cur == --* ]]; then
        COMPREPLY=($(compgen -W "$opts" -- "$cur"))
        return 0
    fi
}

_dotfiles_pass_manager() {
    local cur prev opts commands
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    commands="init setup sync status backup clone"
    opts="--help --verbose --dry-run --gpg-key --force"
    
    # First argument should be a command
    if [[ $COMP_CWORD -eq 1 ]]; then
        COMPREPLY=($(compgen -W "$commands" -- "$cur"))
        return 0
    fi
    
    # Handle options
    if [[ $cur == --* ]]; then
        COMPREPLY=($(compgen -W "$opts" -- "$cur"))
        return 0
    fi
}

# Register completions
complete -F _dotfiles_install install.sh
complete -F _dotfiles_install install-master.sh
complete -F _dotfiles_backup_restore backup-restore.sh
complete -F _dotfiles_profile_manager profile-manager.sh
complete -F _dotfiles_api_key_manager api-key-manager.sh
complete -F _dotfiles_gpg_manager gpg-manager.sh
complete -F _dotfiles_pass_manager pass-manager.sh

# Also register for script names without .sh extension
complete -F _dotfiles_install install
complete -F _dotfiles_install install-master
complete -F _dotfiles_backup_restore backup-restore
complete -F _dotfiles_profile_manager profile-manager
complete -F _dotfiles_api_key_manager api-key-manager
complete -F _dotfiles_gpg_manager gpg-manager
complete -F _dotfiles_pass_manager pass-manager