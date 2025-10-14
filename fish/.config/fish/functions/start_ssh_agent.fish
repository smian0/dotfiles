function start_ssh_agent
    set -l ssh_agent_file "$HOME/.ssh/ssh-agent-env"

    # Kill any existing dead agents
    if test -f $ssh_agent_file
        source $ssh_agent_file >/dev/null 2>&1
        if not kill -0 $SSH_AGENT_PID 2>/dev/null
            rm -f $ssh_agent_file
            set -e SSH_AUTH_SOCK
            set -e SSH_AGENT_PID
        end
    end

    # Start new agent if needed
    if not set -q SSH_AUTH_SOCK; or not ssh-add -l >/dev/null 2>&1
        ssh-agent -c > $ssh_agent_file
        source $ssh_agent_file >/dev/null 2>&1
    end

    # Add GitHub SSH key automatically
    if test -f $HOME/.ssh/id_ed25519_github_smian0
        if not ssh-add -l 2>/dev/null | grep -q "id_ed25519_github_smian0"
            ssh-add $HOME/.ssh/id_ed25519_github_smian0 >/dev/null 2>&1
        end
    end
end
