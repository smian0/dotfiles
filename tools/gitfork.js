#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Simple argument parsing (avoiding external dependencies)
function parseArgs() {
    const args = process.argv.slice(2);
    const config = {
        upstreamRemote: 'upstream',
        upstreamBranch: 'main',
        forkBranch: 'HEAD',
        outputFile: 'fork-comparison.html',
        reportTitle: 'Fork Comparison Report',
        forkRepoName: null,
        upstreamRepoName: null,
        openBrowser: true,
        noFetch: false,
        help: false
    };

    for (let i = 0; i < args.length; i++) {
        const arg = args[i];
        
        if (arg === '--help' || arg === '-h') {
            config.help = true;
        } else if (arg === '--upstream-remote' || arg === '-r') {
            config.upstreamRemote = args[++i];
        } else if (arg === '--upstream-branch' || arg === '-u') {
            config.upstreamBranch = args[++i];
        } else if (arg === '--fork-branch' || arg === '-f') {
            config.forkBranch = args[++i];
        } else if (arg === '--output' || arg === '-o') {
            config.outputFile = args[++i];
        } else if (arg === '--title' || arg === '-t') {
            config.reportTitle = args[++i];
        } else if (arg === '--fork-name') {
            config.forkRepoName = args[++i];
        } else if (arg === '--upstream-name') {
            config.upstreamRepoName = args[++i];
        } else if (arg === '--no-open') {
            config.openBrowser = false;
        } else if (arg === '--no-fetch') {
            config.noFetch = true;
        } else if (!arg.startsWith('-')) {
            // Positional arguments: upstream-ref fork-ref
            if (i === 0) {
                config.upstreamBranch = arg.includes('/') ? arg : `${config.upstreamRemote}/${arg}`;
            } else if (i === 1) {
                config.forkBranch = arg;
            }
        }
    }

    return config;
}

function showHelp() {
    console.log(`
gitfork - Compare git fork with upstream and generate HTML diff report

Usage:
  gitfork [upstream-ref] [fork-ref] [options]

Arguments:
  upstream-ref    Upstream reference to compare against (default: upstream/main)
  fork-ref        Fork reference to compare (default: HEAD)

Options:
  -r, --upstream-remote <name>   Remote name for upstream (default: upstream)
  -u, --upstream-branch <branch> Upstream branch (default: main)  
  -f, --fork-branch <ref>        Fork branch/ref (default: HEAD)
  -o, --output <file>            Output HTML file (default: fork-comparison.html)
  -t, --title <title>            Report title (default: Fork Comparison Report)
      --fork-name <name>         Fork repository name for display
      --upstream-name <name>     Upstream repository name for display
      --no-fetch                 Skip fetching latest from upstream
      --no-open                  Don't open browser automatically
  -h, --help                     Show this help

Examples:
  gitfork                                    # Compare upstream/main vs HEAD
  gitfork upstream/develop HEAD              # Compare specific refs
  gitfork -r origin -u main                  # Use 'origin' remote instead of 'upstream'
  gitfork --no-fetch --title "My Fork Changes"  # Skip fetch with custom title
  gitfork --fork-name "myuser/repo" --upstream-name "org/repo"  # Custom display names
`);
}

function crossPlatformOpen(filePath) {
    const absolutePath = path.resolve(filePath);
    let command;
    
    switch (process.platform) {
        case 'darwin':
            command = 'open';
            break;
        case 'win32':
            command = 'start ""';
            break;
        default:
            command = 'xdg-open';
            break;
    }
    
    try {
        execSync(`${command} "${absolutePath}"`);
        console.log('🌐 Opening report in browser...');
    } catch (error) {
        const fileUrl = process.platform === 'win32' 
            ? `file:///${absolutePath.replace(/\\/g, '/')}`
            : `file://${absolutePath}`;
        console.log(`💡 Manual open: ${fileUrl}`);
    }
}

function isGitRepository() {
    try {
        execSync('git rev-parse --git-dir', { stdio: 'ignore' });
        return true;
    } catch {
        return false;
    }
}

function getRemotes() {
    try {
        const output = execSync('git remote -v', { encoding: 'utf8' });
        const remotes = {};
        output.split('\n').forEach(line => {
            const match = line.match(/^(\S+)\s+(\S+)\s+\((\w+)\)$/);
            if (match) {
                const [, name, url] = match;
                remotes[name] = url;
            }
        });
        return remotes;
    } catch {
        return {};
    }
}

function detectRepositoryNames(config) {
    const remotes = getRemotes();
    
    if (!config.forkRepoName && remotes.origin) {
        const match = remotes.origin.match(/github\.com[:/]([^/]+\/[^/.]+)/);
        if (match) config.forkRepoName = match[1];
    }
    
    if (!config.upstreamRepoName && remotes[config.upstreamRemote]) {
        const match = remotes[config.upstreamRemote].match(/github\.com[:/]([^/]+\/[^/.]+)/);
        if (match) config.upstreamRepoName = match[1];
    }
    
    // Fallback names
    config.forkRepoName = config.forkRepoName || 'Fork';
    config.upstreamRepoName = config.upstreamRepoName || 'Upstream';
}

function fetchUpstream(config) {
    if (config.noFetch) {
        console.log('⚠️  Skipping fetch (--no-fetch specified)');
        return;
    }
    
    try {
        console.log(`🔄 Fetching latest from ${config.upstreamRemote}...`);
        execSync(`git fetch ${config.upstreamRemote}`, { stdio: 'inherit' });
    } catch (error) {
        console.log(`⚠️  Warning: Could not fetch from ${config.upstreamRemote}. Continuing with local data.`);
    }
}

function getFileList(ref) {
    try {
        const output = execSync(`git ls-tree -r --name-only "${ref}"`, { encoding: 'utf8' });
        return output.trim().split('\n').filter(Boolean);
    } catch (error) {
        throw new Error(`Failed to get file list for ${ref}: ${error.message}`);
    }
}

function getFileChanges(upstreamRef, forkRef) {
    try {
        const output = execSync(`git diff --name-status "${upstreamRef}...${forkRef}"`, { encoding: 'utf8' });
        const changes = {};
        
        output.trim().split('\n').forEach(line => {
            if (line.trim()) {
                const [status, filePath] = line.split('\t');
                changes[filePath] = status;
            }
        });
        
        return changes;
    } catch (error) {
        throw new Error(`Failed to get file changes: ${error.message}`);
    }
}

function getFileContent(filePath, ref) {
    try {
        // For HEAD, use filesystem to properly handle symlinks
        if (ref === 'HEAD') {
            if (fs.existsSync(filePath)) {
                return fs.readFileSync(filePath, 'utf8');
            } else {
                return null;
            }
        }
        
        // For other refs, use git show
        const output = execSync(`git show "${ref}:${filePath}"`, { encoding: 'utf8' });
        return output;
    } catch (error) {
        // File doesn't exist in this ref
        return null;
    }
}

function fetchFileContents(changes, upstreamRef, forkRef) {
    console.log('📄 Fetching file contents for diffs...');
    const fileContents = {};
    
    Object.entries(changes).forEach(([filePath, status]) => {
        if (status === 'A' || status === 'M') {
            const upstreamContent = getFileContent(filePath, upstreamRef);
            const forkContent = getFileContent(filePath, forkRef);
            
            if (forkContent !== null) {
                fileContents[filePath] = {
                    upstream: upstreamContent || '',
                    fork: forkContent
                };
            }
        }
    });
    
    return fileContents;
}

function buildFileTree(files) {
    const tree = { name: 'root', type: 'directory', children: {} };
    
    files.forEach(file => {
        const parts = file.split('/');
        let current = tree;
        let currentPath = '';
        
        parts.forEach((part, index) => {
            if (index === parts.length - 1) {
                // File
                current.children[part] = {
                    name: part,
                    type: 'file',
                    path: file
                };
            } else {
                // Directory
                currentPath = currentPath ? `${currentPath}/${part}` : part;
                if (!current.children[part]) {
                    current.children[part] = {
                        name: part,
                        type: 'directory',
                        path: currentPath,
                        children: {}
                    };
                }
                current = current.children[part];
            }
        });
    });
    
    return tree;
}

function getTreeStats(tree) {
    let files = 0;
    let directories = 0;
    
    function count(node) {
        if (node.type === 'file') {
            files++;
        } else if (node.type === 'directory') {
            directories++;
            Object.values(node.children).forEach(count);
        }
    }
    
    Object.values(tree.children || tree).forEach(count);
    return { files, directories };
}

function renderTreeNode(name, node, depth = 0, changes = {}) {
    const indent = '  '.repeat(depth);
    const status = changes[node.path] || 'unchanged';
    
    if (node.type === 'file') {
        const statusClass = `status-${status}`;
        const dataAttrs = `data-type="file" data-status="${status}" data-path="${node.path}"`;
        
        return `
            <div class="tree-node ${statusClass}" ${dataAttrs}>
                <div class="tree-item">
                    <span class="tree-spacer"></span>
                    <span class="tree-icon">📄</span>
                    <span class="tree-name">${name}</span>
                    <span class="tree-status">${getStatusIcon(status)}</span>
                </div>
            </div>`;
    } else {
        const children = Object.entries(node.children)
            .sort(([a, nodeA], [b, nodeB]) => {
                if (nodeA.type !== nodeB.type) {
                    return nodeA.type === 'directory' ? -1 : 1;
                }
                return a.localeCompare(b);
            })
            .map(([childName, childNode]) => renderTreeNode(childName, childNode, depth + 1, changes))
            .join('');
        
        return `
            <div class="tree-node" data-type="directory" data-path="${node.path}">
                <div class="tree-item">
                    <span class="tree-toggle">▶</span>
                    <span class="tree-icon">📁</span>
                    <span class="tree-name">${name}</span>
                </div>
                <div class="tree-children" style="display: none;">${children}</div>
            </div>`;
    }
}

function getStatusIcon(status) {
    switch (status) {
        case 'A': return '🟢';
        case 'M': return '🟡';
        case 'D': return '🔴';
        default: return '⚪';
    }
}

function generateHtmlReport(upstreamFiles, forkFiles, changes, fileContents, config) {
    const upstreamRef = `${config.upstreamRemote}/${config.upstreamBranch}`;
    
    const forkTree = buildFileTree(forkFiles);
    const upstreamTree = buildFileTree(upstreamFiles);
    
    // Get statistics
    const upstreamStats = getTreeStats(upstreamTree);
    const forkStats = getTreeStats(forkTree);
    const changeStats = {
        added: Object.values(changes).filter(s => s === 'A').length,
        modified: Object.values(changes).filter(s => s === 'M').length,
        deleted: Object.values(changes).filter(s => s === 'D').length
    };

    const html = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${config.reportTitle}</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background-color: #f6f8fa;
        }
        .header {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .header h1 {
            margin: 0 0 10px 0;
            color: #24292e;
        }
        .header p {
            margin: 5px 0;
            color: #586069;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .stat-card {
            background: #f1f8ff;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #0366d6;
        }
        .stat-title {
            font-size: 14px;
            font-weight: 600;
            color: #24292e;
            margin-bottom: 10px;
        }
        .stat-number {
            font-size: 28px;
            font-weight: bold;
            color: #0366d6;
        }
        .stat-label {
            font-size: 12px;
            color: #586069;
            text-transform: uppercase;
        }
        .legend {
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .legend h3 {
            margin: 0 0 10px 0;
            color: #24292e;
        }
        .legend-items {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
        }
        .legend-item {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        .legend-icon {
            font-size: 16px;
        }
        .comparison-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        .tree-section {
            background: white;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .tree-header {
            background: #f6f8fa;
            padding: 15px;
            border-bottom: 1px solid #d8dee4;
            font-weight: 600;
            color: #24292e;
        }
        .tree-content {
            padding: 15px;
            max-height: 600px;
            overflow-y: auto;
            font-family: 'SFMono-Regular', Consolas, monospace;
            font-size: 13px;
        }
        .tree-node {
            margin: 2px 0;
        }
        .tree-item {
            display: flex;
            align-items: center;
            padding: 2px 0;
            cursor: pointer;
            border-radius: 3px;
        }
        .tree-item:hover {
            background-color: #f6f8fa;
        }
        .tree-toggle {
            width: 16px;
            cursor: pointer;
            user-select: none;
            color: #586069;
            font-size: 12px;
        }
        .tree-spacer {
            width: 16px;
        }
        .tree-icon {
            margin: 0 6px;
        }
        .tree-name {
            flex: 1;
            color: #24292e;
        }
        .tree-status {
            margin-left: 8px;
            font-size: 12px;
        }
        .tree-children {
            margin-left: 0;
        }
        .status-added .tree-name { color: #28a745; }
        .status-modified .tree-name { color: #ffa500; }
        .status-deleted .tree-name { color: #d73a49; }
        .status-unchanged .tree-name { color: #586069; }
        .controls {
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            text-align: center;
        }
        .btn {
            background: #0366d6;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            margin: 0 5px;
            font-size: 14px;
        }
        .btn:hover {
            background: #0256cc;
        }
        .powered-by {
            text-align: center;
            margin-top: 20px;
            color: #586069;
            font-size: 12px;
        }
        @media (max-width: 768px) {
            .comparison-container {
                grid-template-columns: 1fr;
            }
        }
        
        /* Modal Styles for Diff Display */
        .modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            z-index: 1000;
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.3s ease, visibility 0.3s ease;
        }
        .modal.show {
            opacity: 1;
            visibility: visible;
        }
        .modal-content {
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            width: 95vw;
            height: 90vh;
            max-width: 1400px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 20px;
            border-bottom: 1px solid #e1e4e8;
            background: #f6f8fa;
        }
        .modal-header h3 {
            margin: 0;
            color: #24292e;
            font-size: 16px;
        }
        .modal-close {
            cursor: pointer;
            font-size: 24px;
            color: #586069;
            font-weight: bold;
            line-height: 1;
        }
        .modal-close:hover {
            color: #24292e;
        }
        #diffContainer {
            padding: 20px;
            flex: 1;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }
        
        /* Click indicators for changed files */
        .tree-node[data-type="file"][data-status="A"] .tree-name,
        .tree-node[data-type="file"][data-status="M"] .tree-name {
            cursor: pointer;
            position: relative;
        }
        .tree-node[data-type="file"][data-status="A"]:hover .tree-name,
        .tree-node[data-type="file"][data-status="M"]:hover .tree-name {
            text-decoration: underline;
            font-weight: 500;
        }
        
        /* Visual feedback for clickable changed files */
        .tree-node[data-type="file"][data-status="A"] .tree-name::after,
        .tree-node[data-type="file"][data-status="M"] .tree-name::after {
            content: " 🔍";
            opacity: 0.6;
            font-size: 10px;
            margin-left: 4px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔄 ${config.reportTitle}</h1>
        <p><strong>Fork:</strong> <code>${config.forkRepoName}</code> vs <strong>Upstream:</strong> <code>${config.upstreamRepoName}</code></p>
        <p><strong>Generated:</strong> ${new Date().toLocaleString()}</p>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-title">Fork Repository</div>
                <div class="stat-number">${forkStats.files}</div>
                <div class="stat-label">Files</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">Upstream Repository</div>
                <div class="stat-number">${upstreamStats.files}</div>
                <div class="stat-label">Files</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">Added Files</div>
                <div class="stat-number">${changeStats.added}</div>
                <div class="stat-label">🟢 New in Fork</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">Modified Files</div>
                <div class="stat-number">${changeStats.modified}</div>
                <div class="stat-label">🟡 Changed</div>
            </div>
        </div>
    </div>
    
    <div class="legend">
        <h3>📋 Status Legend</h3>
        <div class="legend-items">
            <div class="legend-item">
                <span class="legend-icon">🟢</span>
                <span>Added (only in fork)</span>
            </div>
            <div class="legend-item">
                <span class="legend-icon">🟡</span>
                <span>Modified (different content)</span>
            </div>
            <div class="legend-item">
                <span class="legend-icon">🔴</span>
                <span>Deleted (only in upstream)</span>
            </div>
            <div class="legend-item">
                <span class="legend-icon">⚪</span>
                <span>Unchanged (identical)</span>
            </div>
        </div>
    </div>
    
    <div class="controls">
        <button class="btn" onclick="expandAll()">Expand All</button>
        <button class="btn" onclick="collapseAll()">Collapse All</button>
        <button class="btn" onclick="showChangedOnly()">${changeStats.added + changeStats.modified > 0 ? 'Show Changed Only' : 'All Files Unchanged'}</button>
    </div>
    
    <div class="comparison-container">
        <div class="tree-section">
            <div class="tree-header">
                📁 Fork Repository (${forkStats.files} files)
            </div>
            <div class="tree-content" id="forkTree">
                ${Object.entries(forkTree.children || forkTree)
                    .sort(([a, nodeA], [b, nodeB]) => {
                        if (nodeA.type !== nodeB.type) {
                            return nodeA.type === 'directory' ? -1 : 1;
                        }
                        return a.localeCompare(b);
                    })
                    .map(([name, node]) => renderTreeNode(name, node, 0, changes))
                    .join('')}
            </div>
        </div>
        
        <div class="tree-section">
            <div class="tree-header">
                📁 Upstream Repository (${upstreamStats.files} files)
            </div>
            <div class="tree-content" id="upstreamTree">
                ${Object.entries(upstreamTree.children || upstreamTree)
                    .sort(([a, nodeA], [b, nodeB]) => {
                        if (nodeA.type !== nodeB.type) {
                            return nodeA.type === 'directory' ? -1 : 1;
                        }
                        return a.localeCompare(b);
                    })
                    .map(([name, node]) => renderTreeNode(name, node, 0, changes))
                    .join('')}
            </div>
        </div>
    </div>
    
    <div class="powered-by">
        ${config.reportTitle} - Interactive repository tree diff viewer
    </div>

    <!-- Diff Modal -->
    <div id="diffModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3 id="modalTitle">File Diff</h3>
                <span class="modal-close" onclick="closeDiff()">×</span>
            </div>
            <div id="diffContainer"></div>
        </div>
    </div>

    <!-- Monaco Editor -->
    <script src="https://unpkg.com/monaco-editor@latest/min/vs/loader.js"></script>
    <script>
        // File contents for diff display - embedded using base64 encoding to avoid escaping issues
        window.fileContents = {};
        ${Object.entries(fileContents).map(([filePath, content]) => {
            const upstreamB64 = Buffer.from(content.upstream || '').toString('base64');
            const forkB64 = Buffer.from(content.fork || '').toString('base64');
            return `window.fileContents[${JSON.stringify(filePath)}] = {
            upstream: atob(${JSON.stringify(upstreamB64)}),
            fork: atob(${JSON.stringify(forkB64)})
        };`;
        }).join('\n        ')}

        // Tree expansion/collapse functionality - click on toggle
        document.addEventListener('click', function(e) {
            if (e.target.classList.contains('tree-toggle')) {
                const children = e.target.parentNode.parentNode.querySelector('.tree-children');
                if (children) {
                    const isExpanded = children.style.display !== 'none';
                    children.style.display = isExpanded ? 'none' : 'block';
                    e.target.textContent = isExpanded ? '▶' : '▼';
                }
            }
        });
        
        // Enhanced click handling for both tree navigation and diff display
        document.addEventListener('click', function(e) {
            if (e.target.classList.contains('tree-name')) {
                const treeNode = e.target.closest('.tree-node');
                const fileType = treeNode?.dataset.type;
                const fileStatus = treeNode?.dataset.status;
                const filePath = treeNode?.dataset.path;
                
                if (fileType === 'directory') {
                    // Handle folder expansion/collapse
                    const children = treeNode.querySelector('.tree-children');
                    if (children) {
                        const isExpanded = children.style.display !== 'none';
                        children.style.display = isExpanded ? 'none' : 'block';
                        
                        // Update the toggle icon if it exists
                        const toggle = treeNode.querySelector('.tree-toggle');
                        if (toggle) {
                            toggle.textContent = isExpanded ? '▶' : '▼';
                        }
                    }
                } else if (fileType === 'file' && (fileStatus === 'A' || fileStatus === 'M') && filePath) {
                    // Handle file clicks for diff display (only for changed files)
                    e.stopPropagation();
                    showDiff(filePath, fileStatus);
                }
            }
        });

        function expandAll() {
            document.querySelectorAll('.tree-children').forEach(children => {
                children.style.display = 'block';
            });
            document.querySelectorAll('.tree-toggle').forEach(toggle => {
                toggle.textContent = '▼';
            });
        }

        function collapseAll() {
            document.querySelectorAll('.tree-children').forEach(children => {
                children.style.display = 'none';
            });
            document.querySelectorAll('.tree-toggle').forEach(toggle => {
                toggle.textContent = '▶';
            });
        }

        function showChangedOnly() {
            const showAll = document.querySelector('.btn:last-child').textContent === 'Show All Files';
            
            document.querySelectorAll('.tree-node').forEach(node => {
                const status = node.getAttribute('data-status');
                if (showAll || status === 'A' || status === 'M' || status === 'D') {
                    node.style.display = 'block';
                } else {
                    node.style.display = 'none';
                }
            });
            
            document.querySelector('.btn:last-child').textContent = showAll ? 'Show Changed Only' : 'Show All Files';
        }

        function showDiff(filePath, status) {
            const fileData = window.fileContents[filePath];
            if (!fileData) return;

            document.getElementById('modalTitle').textContent = filePath + ' (' + status + ')';
            document.getElementById('diffModal').classList.add('show');

            require.config({ paths: { vs: 'https://unpkg.com/monaco-editor@latest/min/vs' } });
            require(['vs/editor/editor.main'], function () {
                const container = document.getElementById('diffContainer');
                container.innerHTML = '';

                const language = getLanguageFromFilename(filePath);
                
                let originalContent, modifiedContent;
                
                if (status === 'A') {
                    originalContent = fileData ? fileData.upstream : '';
                    modifiedContent = fileData ? fileData.fork : 'File content not available';
                } else {
                    originalContent = fileData ? fileData.upstream : 'Upstream content not available';
                    modifiedContent = fileData ? fileData.fork : 'Fork content not available';
                }

                const originalModel = monaco.editor.createModel(
                    originalContent, 
                    language,
                    monaco.Uri.parse('file:///' + filePath + '-original')
                );
                const modifiedModel = monaco.editor.createModel(
                    modifiedContent, 
                    language,
                    monaco.Uri.parse('file:///' + filePath + '-modified')
                );

                const diffEditor = monaco.editor.createDiffEditor(container, {
                    theme: 'vs',
                    automaticLayout: true,
                    readOnly: true,
                    renderSideBySide: true,
                    renderWhitespace: 'boundary',
                    diffWordWrap: 'on'
                });

                diffEditor.setModel({
                    original: originalModel,
                    modified: modifiedModel
                });
            });
        }

        function closeDiff() {
            document.getElementById('diffModal').classList.remove('show');
        }

        function getLanguageFromFilename(filename) {
            const ext = filename.split('.').pop()?.toLowerCase();
            const mapping = {
                'js': 'javascript', 'jsx': 'javascript', 'ts': 'typescript', 'tsx': 'typescript',
                'py': 'python', 'rb': 'ruby', 'go': 'go', 'rs': 'rust', 'php': 'php',
                'java': 'java', 'c': 'c', 'cpp': 'cpp', 'h': 'c', 'hpp': 'cpp',
                'cs': 'csharp', 'css': 'css', 'scss': 'scss', 'sass': 'scss',
                'html': 'html', 'xml': 'xml', 'json': 'json', 'yaml': 'yaml', 'yml': 'yaml',
                'md': 'markdown', 'txt': 'plaintext', 'sh': 'shell', 'bash': 'shell',
                'sql': 'sql', 'dockerfile': 'dockerfile'
            };
            return mapping[ext] || 'plaintext';
        }

        // Close modal when clicking outside or on close button
        document.getElementById('diffModal').addEventListener('click', function(e) {
            if (e.target === this || e.target.classList.contains('modal-close')) {
                closeDiff();
            }
        });
        
        // Escape key to close modal
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                closeDiff();
            }
        });

        // Initialize - collapse empty sections
        document.addEventListener('DOMContentLoaded', function() {
            expandAll(); // Start with all expanded
        });
    </script>
</body>
</html>`;

    return html;
}

function main() {
    const config = parseArgs();
    
    if (config.help) {
        showHelp();
        return;
    }

    try {
        // Validate we're in a git repository
        if (!isGitRepository()) {
            throw new Error('Not a git repository. Please run this command from within a git repository.');
        }

        // Check if upstream remote exists
        const remotes = getRemotes();
        if (!remotes[config.upstreamRemote]) {
            throw new Error(`Remote '${config.upstreamRemote}' not found. Available remotes: ${Object.keys(remotes).join(', ')}`);
        }

        console.log('🚀 Starting Fork Comparison Generator');
        
        // Auto-detect repository names
        detectRepositoryNames(config);
        
        const upstreamRef = `${config.upstreamRemote}/${config.upstreamBranch}`;
        console.log(`📊 Comparing ${config.forkBranch} against ${upstreamRef}`);
        
        // Fetch latest upstream
        fetchUpstream(config);
        
        console.log('📁 Analyzing file trees...');
        const upstreamFiles = getFileList(upstreamRef);
        const forkFiles = getFileList(config.forkBranch);
        
        console.log('🔍 Identifying changes...');
        const changes = getFileChanges(upstreamRef, config.forkBranch);
        
        console.log(`📊 Found ${upstreamFiles.length} upstream files, ${forkFiles.length} fork files`);
        console.log(`📝 Changes: ${Object.keys(changes).length} files modified`);
        
        console.log('🎨 Generating fork comparison report...');
        const fileContents = fetchFileContents(changes, upstreamRef, config.forkBranch);
        
        const html = generateHtmlReport(upstreamFiles, forkFiles, changes, fileContents, config);
        fs.writeFileSync(config.outputFile, html);
        
        console.log(`✅ Report generated: ${config.outputFile}`);
        
        if (config.openBrowser) {
            crossPlatformOpen(config.outputFile);
        } else {
            const absolutePath = path.resolve(config.outputFile);
            const fileUrl = process.platform === 'win32' 
                ? `file:///${absolutePath.replace(/\\/g, '/')}`
                : `file://${absolutePath}`;
            console.log(`💡 Open manually: ${fileUrl}`);
        }
        
    } catch (error) {
        console.error('❌ Error:', error.message);
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}

module.exports = { main, parseArgs, getFileList, getFileChanges, generateHtmlReport };