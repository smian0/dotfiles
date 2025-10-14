# GitHub CLI wrapper to prevent accidental operations on non-owned repos
function gh
    if test "$argv[1]" = "issue"; and test "$argv[2]" = "create"
        # Parse --repo flag to get target repository
        set -l target_repo ""

        # Look for --repo flag
        for i in (seq 3 (count $argv))
            if test "$argv[$i]" = "--repo"; and test $i -lt (count $argv)
                set target_repo $argv[(math $i + 1)]
                break
            else if string match -q -- "--repo=*" $argv[$i]
                set target_repo (string replace "--repo=" "" $argv[$i])
                break
            end
        end

        # If no --repo flag, use current repository context
        if test -z "$target_repo"
            set target_repo (command gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null; or echo "unknown")
        end

        # Extract owner from repo (e.g., "Cloud-Kinetix/bmad-enhanced" → "Cloud-Kinetix")
        set -l repo_owner (string split "/" $target_repo)[1]

        # Define allowed organizations/users
        set -l allowed_owners Cloud-Kinetix smian0

        if test "$target_repo" = "unknown"
            echo "❌ BLOCKED: Cannot determine target repository!"
            echo "Please run from within a git repository or use --repo flag"
            echo "If this is intentional, use: command gh issue create ..."
            return 1
        end

        if not contains $repo_owner $allowed_owners
            echo "❌ BLOCKED: Cannot create issues in third-party repository!"
            echo "Target repo: $target_repo"
            echo "Owner: $repo_owner"
            echo "Allowed owners: $allowed_owners"
            echo ""
            echo "If this is intentional, use: command gh issue create ..."
            return 1
        end

        echo "✅ Safe repository: $target_repo"
        command gh $argv
    else
        command gh $argv
    end
end
