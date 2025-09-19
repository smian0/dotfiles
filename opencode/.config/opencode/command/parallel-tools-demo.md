---
description: Demonstrates parallel tool execution through batching within a single agent
---

# Parallel Tools Demo Command

You are an efficient task executor that maximizes parallelism by batching tool calls.

## Task: Analyze {{PROJECT}} 

When analyzing a project, execute multiple independent operations simultaneously by calling multiple bash tools in ONE message.

### Phase 1: Parallel Information Gathering

I'll gather project information by running multiple commands in parallel. Execute these commands simultaneously:

1) bash 'git status'
2) bash 'git log --oneline -10'  
3) bash 'ls -la'
4) bash 'cat package.json 2>/dev/null | grep -A 5 dependencies || echo "No package.json"'
5) bash 'npm test -- --listTests 2>/dev/null || echo "No npm tests"'

Execute all five bash commands above in a single message to run them in parallel.

### Phase 2: Parallel File Analysis

Now I'll read multiple files simultaneously to understand the project structure. Execute these read operations in parallel:

1) read 'README.md'
2) read 'package.json'
3) read '.gitignore'
4) read 'tsconfig.json'

Execute all four read commands above in a single message to read them in parallel.

### Phase 3: Parallel Search Operations

Finally, I'll search for various patterns across the codebase. Execute these searches simultaneously:

1) bash 'grep -r "TODO" --include="*.ts" --include="*.js" 2>/dev/null | head -10 || echo "No TODOs found"'
2) bash 'find . -name "*.test.*" -o -name "*.spec.*" | head -10'
3) bash 'find . -maxdepth 2 -name "*config*" | head -10'
4) bash 'grep -r "api_key\|secret\|password" --include="*.env*" 2>/dev/null | head -5 || echo "No exposed secrets"'

Execute all four bash commands above in a single message to search in parallel.

## Key Principles for OpenCode Parallel Execution:

1. **List commands explicitly**: Use numbered format like "1) bash 'command'" 
2. **Single message execution**: State "Execute all X commands above in a single message"
3. **Use bash prefix**: Each command needs explicit `bash` or `read` tool prefix
4. **Error handling**: Add `|| echo "fallback"` to prevent failures from breaking the batch
5. **Group by operation type**: Batch similar operations (all bash, all read) together

## Example - CORRECT OpenCode parallel syntax:

**Sequential (slow) approach:**
```
Let me check git status...
[executes git status]
Now let me look at the files...
[executes ls]
Now let me read package.json...
[reads package.json]
```

**Parallel (fast) approach:**
```
I'll gather project information by running these commands in parallel:

1) bash 'git status'
2) bash 'ls -la'  
3) read 'package.json'

Execute all three commands above in a single message to run them in parallel.
```

This leverages OpenCode's native tool batching for true parallel execution!