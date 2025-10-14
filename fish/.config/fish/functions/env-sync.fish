function env-sync
    echo "🔄 Syncing shell environment with system (launchctl)..."
    set -l synced 0

    # Key environment variables to sync
    set -l vars GITHUB_TOKEN OPENAI_API_KEY ANTHROPIC_API_KEY BRAVE_API_KEY OLLAMA_API_KEY DEEPSEEK_API_KEY GLM_API_KEY KIMI_API_KEY

    for var in $vars
        set -l system_val (launchctl getenv $var 2>/dev/null; or echo "")
        set -l shell_val (printenv $var 2>/dev/null; or echo "")

        if test -n "$system_val"; and test "$system_val" != "$shell_val"
            set -gx $var $system_val
            echo "✓ Synced $var"
            set synced (math $synced + 1)
        end
    end

    if test $synced -eq 0
        echo "✅ No sync needed - all variables match"
    else
        echo "✅ Synced $synced environment variables"
    end
end
