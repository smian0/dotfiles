#compdef install.sh install-master.sh backup-restore.sh profile-manager.sh api-key-manager.sh gpg-manager.sh pass-manager.sh
# Zsh completion for dotfiles scripts

_dotfiles_install() {
    local context state state_descr line
    typeset -A opt_args
    
    local packages=(
        'git:Git configuration'
        'zsh:Zsh shell configuration'
        'vim:Vim editor configuration'
        'claude-default:Default Claude profile'
        'claude-experimental:Experimental Claude profile'
        'npm-configs:NPM configuration'
        'config:System configuration'
        'bin:Binary scripts'
        'pass:Password store'
        'direnv:Directory environment'
    )
    
    local profiles=(
        'minimal:Essential tools only'
        'development:Development tools with Claude'
        'full:Complete setup with all packages'
        'work:Work-specific configuration'
        'personal:Personal machine setup'
    )
    
    _arguments -C \
        '--all[Install all packages]' \
        '--help[Show help message]' \
        '--dry-run[Show what would be done]' \
        '--verbose[Enable verbose output]' \
        '--force[Force installation]' \
        '--claude-profile[Claude profile]:profile:(default experimental)' \
        '--profile[Installation profile]:profile:((${profiles}))' \
        '--backup[Backup directory]:directory:_directories' \
        '*:packages:((${packages}))'
}

_dotfiles_backup_restore() {
    local context state state_descr line
    typeset -A opt_args
    
    local commands=(
        'backup:Create a new backup'
        'restore:Restore from backup'
        'list:List available backups'
        'clean:Remove old backups'
        'verify:Verify backup integrity'
    )
    
    _arguments -C \
        '1:command:((${commands}))' \
        '--help[Show help message]' \
        '--verbose[Enable verbose output]' \
        '--dry-run[Show what would be done]' \
        '--exclude-secrets[Exclude GPG and password store]' \
        '--include-brew[Include Homebrew packages list]' \
        '--backup-dir[Custom backup directory]:directory:_directories' \
        '*::arg:->args'
    
    case $state in
        args)
            case $words[1] in
                restore|verify)
                    # Complete with available backup timestamps
                    local backup_dir="${HOME}/.dotfiles-backups"
                    if [[ -d "$backup_dir" ]]; then
                        local backups=(${backup_dir}/*.tar.gz(N:t:r))
                        _describe 'backups' backups
                    fi
                    ;;
            esac
            ;;
    esac
}

_dotfiles_profile_manager() {
    local context state state_descr line
    typeset -A opt_args
    
    local commands=(
        'list:List available profiles'
        'install:Install specific profile'
        'status:Check installation status'
        'check:Validate profile configuration'
        'uninstall:Remove profile'
    )
    
    local profiles=(
        'minimal:Essential tools only'
        'development:Development tools with Claude'
        'full:Complete setup with all packages'
        'work:Work-specific configuration'
        'personal:Personal machine setup'
    )
    
    _arguments -C \
        '1:command:((${commands}))' \
        '--help[Show help message]' \
        '--verbose[Enable verbose output]' \
        '--dry-run[Show what would be done]' \
        '--force[Force installation]' \
        '*::arg:->args'
    
    case $state in
        args)
            case $words[1] in
                install|uninstall)
                    _describe 'profiles' profiles
                    ;;
            esac
            ;;
    esac
}

_dotfiles_api_key_manager() {
    local context state state_descr line
    typeset -A opt_args
    
    local commands=(
        'add:Add new API key'
        'get:Get API key'
        'list:List stored keys'
        'remove:Remove API key'
        'sync:Sync with pass store'
        'status:Show key status'
        'test:Test API key'
    )
    
    local services=(
        'openai:OpenAI API'
        'anthropic:Anthropic Claude API'
        'github:GitHub API'
        'aws:Amazon Web Services'
        'azure:Microsoft Azure'
        'gcp:Google Cloud Platform'
    )
    
    _arguments -C \
        '1:command:((${commands}))' \
        '--help[Show help message]' \
        '--verbose[Enable verbose output]' \
        '--dry-run[Show what would be done]' \
        '--pass-store[Use pass password store]' \
        '--env-file[Environment file]:file:_files' \
        '*::arg:->args'
    
    case $state in
        args)
            case $words[1] in
                add|get|remove|test)
                    _describe 'services' services
                    ;;
            esac
            ;;
    esac
}

_dotfiles_gpg_manager() {
    local context state state_descr line
    typeset -A opt_args
    
    local commands=(
        'export:Export GPG keys'
        'import:Import GPG keys'
        'backup:Backup GPG keyring'
        'restore:Restore GPG keyring'
        'list:List GPG keys'
        'generate:Generate new GPG key'
        'status:Show GPG status'
    )
    
    _arguments -C \
        '1:command:((${commands}))' \
        '--help[Show help message]' \
        '--verbose[Enable verbose output]' \
        '--dry-run[Show what would be done]' \
        '--key-id[GPG key ID]:key-id:_gpg_key_ids' \
        '--backup-file[Backup file]:file:_files' \
        '--force[Force operation]'
}

_dotfiles_pass_manager() {
    local context state state_descr line
    typeset -A opt_args
    
    local commands=(
        'init:Initialize password store'
        'setup:Setup password store'
        'sync:Sync with remote'
        'status:Show store status'
        'backup:Backup password store'
        'clone:Clone remote store'
    )
    
    _arguments -C \
        '1:command:((${commands}))' \
        '--help[Show help message]' \
        '--verbose[Enable verbose output]' \
        '--dry-run[Show what would be done]' \
        '--gpg-key[GPG key ID]:key-id:_gpg_key_ids' \
        '--force[Force operation]'
}

# Helper function to get GPG key IDs
_gpg_key_ids() {
    local keys
    keys=(${(f)"$(gpg --list-secret-keys --keyid-format SHORT 2>/dev/null | grep "sec" | awk '{print $2}' | cut -d'/' -f2)"})
    _describe 'GPG Key IDs' keys
}

# Register completions for different script names
_install() { _dotfiles_install }
_install-master() { _dotfiles_install }
_backup-restore() { _dotfiles_backup_restore }
_profile-manager() { _dotfiles_profile_manager }
_api-key-manager() { _dotfiles_api_key_manager }
_gpg-manager() { _dotfiles_gpg_manager }
_pass-manager() { _dotfiles_pass_manager }

# Also handle scripts without .sh extension
compdef _install install
compdef _install-master install-master
compdef _backup-restore backup-restore
compdef _profile-manager profile-manager
compdef _api-key-manager api-key-manager
compdef _gpg-manager gpg-manager
compdef _pass-manager pass-manager