#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Simple argument parsing (avoiding external dependencies)
function parseArgs() {
    const args = process.argv.slice(2);
    const config = {
        baseDir: '.claude',
        overrideDir: '.claude-ext',
        outputFile: 'diffdir-report.html',
        extensions: ['.md'],
        title: 'Directory Comparison Report',
        autoOpen: true,
        help: false
    };

    for (let i = 0; i < args.length; i++) {
        const arg = args[i];
        
        if (arg === '--help' || arg === '-h') {
            config.help = true;
        } else if (arg === '--extension' || arg === '-e') {
            const ext = args[++i];
            if (ext) {
                config.extensions = ext.startsWith('.') ? [ext] : [`.${ext}`];
            }
        } else if (arg === '--extensions') {
            const exts = args[++i];
            if (exts) {
                config.extensions = exts.split(',').map(e => e.startsWith('.') ? e : `.${e}`);
            }
        } else if (arg === '--output' || arg === '-o') {
            config.outputFile = args[++i];
        } else if (arg === '--title' || arg === '-t') {
            config.title = args[++i];
        } else if (arg === '--no-open') {
            config.autoOpen = false;
        } else if (!arg.startsWith('-')) {
            // Positional arguments: baseDir overrideDir
            if (!config.baseDir || config.baseDir === '.claude') {
                config.baseDir = arg;
            } else if (!config.overrideDir || config.overrideDir === '.claude-ext') {
                config.overrideDir = arg;
            }
        }
    }

    return config;
}

function showHelp() {
    console.log(`
diffdir - Compare two directories and generate HTML diff report

Usage:
  diffdir [base-dir] [override-dir] [options]

Arguments:
  base-dir        Base directory to compare from (default: .claude)
  override-dir    Override directory to compare to (default: .claude-ext)

Options:
  -e, --extension <ext>     File extension to compare (default: .md)
      --extensions <list>   Comma-separated list of extensions (e.g., .js,.ts,.md)
  -o, --output <file>       Output HTML file (default: diffdir-report.html)
  -t, --title <title>       Report title (default: Directory Comparison Report)
      --no-open            Don't open browser automatically
  -h, --help               Show this help

Examples:
  diffdir                                    # Compare .claude vs .claude-ext
  diffdir ./config ./config-dev             # Compare any two directories
  diffdir -e .js src src-modified            # Compare JavaScript files only
  diffdir --extensions .js,.ts,.json api api-v2  # Multiple file types
  diffdir --title "Config Comparison" --no-open config config-backup
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

function findComparisonFiles(baseDir, overrideDir, extensions) {
    console.log('🔍 Finding files to compare...');
    
    if (!fs.existsSync(baseDir)) {
        throw new Error(`Base directory not found: ${baseDir}`);
    }
    
    if (!fs.existsSync(overrideDir)) {
        throw new Error(`Override directory not found: ${overrideDir}`);
    }
    
    const comparisonFiles = [];
    
    function traverseDirectory(dir, relativePath = '') {
        const items = fs.readdirSync(dir);
        
        for (const item of items) {
            const itemPath = path.join(dir, item);
            const relativeItemPath = path.join(relativePath, item);
            
            if (fs.statSync(itemPath).isDirectory()) {
                traverseDirectory(itemPath, relativeItemPath);
            } else {
                const itemExt = path.extname(item);
                if (extensions.includes(itemExt)) {
                    const basePath = path.join(baseDir, relativeItemPath);
                    if (fs.existsSync(basePath)) {
                        comparisonFiles.push({
                            relative: relativeItemPath,
                            override: itemPath,
                            base: basePath
                        });
                    }
                }
            }
        }
    }
    
    traverseDirectory(overrideDir);
    return comparisonFiles;
}

function generateHtmlReport(comparisonFiles, config) {
    console.log('🎨 Generating diff report...');
    
    // Prepare file data for Monaco
    const fileData = comparisonFiles.map(file => {
        const baseContent = fs.readFileSync(file.base, 'utf8');
        const overrideContent = fs.readFileSync(file.override, 'utf8');
        
        return {
            name: file.relative,
            original: baseContent,
            modified: overrideContent,
            path: file.relative
        };
    });

    const html = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${config.title}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #1e1e1e;
            color: #d4d4d4;
            overflow: hidden;
        }

        .header {
            background: #2d2d30;
            padding: 20px;
            border-bottom: 1px solid #3e3e42;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 100;
            height: 80px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .header h1 {
            font-size: 24px;
            color: #ffffff;
            margin: 0;
        }

        .stats {
            display: flex;
            gap: 20px;
            font-size: 14px;
        }

        .stat {
            background: #007acc;
            padding: 4px 12px;
            border-radius: 12px;
            color: white;
            font-weight: 500;
        }

        .sidebar {
            position: fixed;
            top: 80px;
            left: 0;
            width: 350px;
            bottom: 0;
            background: #252526;
            border-right: 1px solid #3e3e42;
            overflow-y: auto;
        }

        .file-list {
            padding: 0;
        }

        .file-item {
            display: block;
            padding: 12px 20px;
            border-bottom: 1px solid #3e3e42;
            cursor: pointer;
            text-decoration: none;
            color: #d4d4d4;
            transition: background-color 0.2s;
        }

        .file-item:hover {
            background: #2a2d2e;
        }

        .file-item.active {
            background: #007acc;
            color: white;
        }

        .file-name {
            font-weight: 500;
            font-size: 14px;
            margin-bottom: 4px;
        }

        .file-path {
            font-size: 12px;
            color: #969696;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        }

        .diff-container {
            position: fixed;
            top: 80px;
            left: 350px;
            right: 0;
            bottom: 0;
            background: #1e1e1e;
        }

        .no-selection {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
            color: #969696;
            font-size: 16px;
        }

        #monaco-editor {
            width: 100%;
            height: 100%;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>${config.title}</h1>
        <div class="stats">
            <div class="stat">${comparisonFiles.length} files</div>
            <div class="stat">${config.extensions.join(', ')}</div>
        </div>
    </div>

    <div class="sidebar">
        <div class="file-list">
            ${comparisonFiles.map((file, index) => `
                <a href="#" class="file-item" data-index="${index}">
                    <div class="file-name">${path.basename(file.relative)}</div>
                    <div class="file-path">${file.relative}</div>
                </a>
            `).join('')}
        </div>
    </div>

    <div class="diff-container">
        <div class="no-selection">
            Select a file from the sidebar to view the diff
        </div>
        <div id="monaco-editor" style="display: none;"></div>
    </div>

    <script src="https://unpkg.com/monaco-editor@0.34.1/min/vs/loader.js"></script>
    <script>
        const fileData = ${JSON.stringify(fileData)};
        let diffEditor = null;
        let currentFileIndex = -1;

        require.config({ paths: { vs: 'https://unpkg.com/monaco-editor@0.34.1/min/vs' } });

        require(['vs/editor/editor.main'], function () {
            // Initialize Monaco
            monaco.editor.defineTheme('custom-dark', {
                base: 'vs-dark',
                inherit: true,
                rules: [],
                colors: {
                    'editor.background': '#1e1e1e',
                    'editor.foreground': '#d4d4d4',
                }
            });

            monaco.editor.setTheme('custom-dark');

            // File selection handling
            document.querySelectorAll('.file-item').forEach((item, index) => {
                item.addEventListener('click', (e) => {
                    e.preventDefault();
                    selectFile(index);
                });
            });

            function selectFile(index) {
                if (index === currentFileIndex) return;

                // Update UI
                document.querySelectorAll('.file-item').forEach(item => item.classList.remove('active'));
                document.querySelectorAll('.file-item')[index].classList.add('active');

                // Show editor
                document.querySelector('.no-selection').style.display = 'none';
                document.getElementById('monaco-editor').style.display = 'block';

                // Get file data
                const file = fileData[index];

                // Create or update diff editor
                if (diffEditor) {
                    const originalModel = monaco.editor.createModel(file.original, 'markdown');
                    const modifiedModel = monaco.editor.createModel(file.modified, 'markdown');
                    
                    diffEditor.setModel({
                        original: originalModel,
                        modified: modifiedModel
                    });
                } else {
                    const originalModel = monaco.editor.createModel(file.original, 'markdown');
                    const modifiedModel = monaco.editor.createModel(file.modified, 'markdown');
                    
                    diffEditor = monaco.editor.createDiffEditor(document.getElementById('monaco-editor'), {
                        theme: 'custom-dark',
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
                }

                currentFileIndex = index;
            }

            // Auto-select first file if available
            if (fileData.length > 0) {
                selectFile(0);
            }
        });

        // Handle window resize
        window.addEventListener('resize', () => {
            if (diffEditor) {
                diffEditor.layout();
            }
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
        console.log('🚀 Starting Directory Diff Report Generator');
        console.log(`📁 Base directory: ${config.baseDir}`);
        console.log(`📁 Override directory: ${config.overrideDir}`);
        console.log(`📄 Extensions: ${config.extensions.join(', ')}`);
        
        const comparisonFiles = findComparisonFiles(config.baseDir, config.overrideDir, config.extensions);
        
        if (comparisonFiles.length === 0) {
            console.log('⚠️  No matching files found to compare');
            console.log(`   Check that both directories exist and contain files with extensions: ${config.extensions.join(', ')}`);
            return;
        }
        
        console.log(`✅ Found ${comparisonFiles.length} files to compare:`);
        comparisonFiles.forEach(file => {
            console.log(`   📝 ${file.relative}`);
        });
        
        const html = generateHtmlReport(comparisonFiles, config);
        fs.writeFileSync(config.outputFile, html);
        
        console.log(`✅ Report generated: ${config.outputFile}`);
        
        if (config.autoOpen) {
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

module.exports = { main, parseArgs, findComparisonFiles, generateHtmlReport };