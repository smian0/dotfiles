#!/usr/bin/env node

/**
 * Comprehensive Command Transformer Test
 * 
 * Combines detailed audit analysis with unit testing:
 * 1. Shows step-by-step transformation process
 * 2. Validates output against expected results
 * 3. Saves converted files for inspection
 * 4. Returns appropriate exit codes for CI/automation
 * 
 * Usage:
 *   node test-command-transformer.js                    # Test default fixture
 *   node test-command-transformer.js /path/to/command.md  # Test specific command
 */

import { readFile, writeFile, mkdir } from 'fs/promises';
import { join, dirname, basename } from 'path';
import { fileURLToPath } from 'url';
import { existsSync } from 'fs';
import { 
  parseCommandYAML, 
  transformCommand, 
  validateTransformedCommand,
  getSampleClaudeCommand,
  getSampleOpenCodeCommand,
  CLAUDE_TO_OPENCODE_TOOLS
} from '../plugin-util/command-transformer-core.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

/**
 * Test configuration
 */
const DEFAULT_SOURCE = join(__dirname, 'fixtures', 'claude-test-command.md');
const DEFAULT_EXPECTED = join(__dirname, 'fixtures', 'claude-test-command-converted-expected.md');
const OUTPUT_DIR = join(__dirname, 'test-output', 'converted');

/**
 * Show frontmatter with line numbers for audit display
 */
function showFrontmatter(content, title) {
  console.log(`📄 ${title}:`);
  console.log('---------------------------');
  
  const lines = content.split('\n');
  const startIdx = lines.findIndex(line => line.trim() === '---');
  const endIdx = lines.findIndex((line, idx) => idx > startIdx && line.trim() === '---');
  
  if (startIdx === -1 || endIdx === -1) {
    console.log('❌ No valid frontmatter found');
    return;
  }
  
  for (let i = startIdx; i <= endIdx; i++) {
    const lineNum = (i + 1).toString().padStart(2, ' ');
    console.log(`${lineNum}: ${lines[i]}`);
  }
  
  console.log('---------------------------\n');
}

/**
 * Show transformation analysis
 */
function showTransformationAnalysis(claudeContent, openCodeContent) {
  console.log('🔍 TRANSFORMATION ANALYSIS');
  console.log('============================\n');
  
  // Parse frontmatter from both
  const claudeParts = claudeContent.split('---');
  const openCodeParts = openCodeContent.split('---');
  
  if (claudeParts.length >= 3 && openCodeParts.length >= 3) {
    const claudeFM = parseCommandYAML(claudeParts[1]);
    const openCodeFM = parseCommandYAML(openCodeParts[1]);
    
    console.log('📊 Field-by-field comparison:');
    console.log('------------------------------');
    
    // Show tool mapping
    if (claudeFM['allowed-tools']) {
      console.log('🔧 Tool Mapping:');
      claudeFM['allowed-tools'].forEach(tool => {
        const mapped = CLAUDE_TO_OPENCODE_TOOLS[tool] || tool.toLowerCase();
        const status = mapped !== tool ? '✅ mapped' : '⚪ unchanged';
        console.log(`   ${tool} → ${mapped} ${status}`);
      });
      console.log('');
    }
    
    // Show field transformations
    console.log('📝 Field Transformations:');
    console.log('   Claude Format           →   OpenCode Format');
    console.log('   -----------------           -----------------');
    
    // Check title → description
    if (claudeFM.title) {
      console.log(`   title: "${claudeFM.title}"         →   description: "${openCodeFM.description}"`);
    }
    
    // Check allowed-tools removal
    if (claudeFM['allowed-tools']) {
      console.log(`   allowed-tools: [list]        →   agent: ${openCodeFM.agent}`);
    }
    
    // Check other fields
    ['category', 'author', 'version'].forEach(field => {
      if (claudeFM[field] && openCodeFM[field]) {
        console.log(`   ${field}: "${claudeFM[field]}"        →   ${field}: "${openCodeFM[field]}"`);
      }
    });
    
    console.log('');
  }
  
  // Show body transformations
  const claudeBody = claudeParts.slice(2).join('---');
  const openCodeBody = openCodeParts.slice(2).join('---');
  
  console.log('📄 Body Transformations:');
  console.log('-------------------------');
  
  const transformations = [
    { from: '.claude/', to: '.opencode/', name: 'Directory references' },
    { from: 'Task tool', to: 'agent tool', name: 'Tool references' },
    { from: 'Claude Code', to: 'OpenCode', name: 'Product name' },
    { from: 'claude run', to: 'opencode run', name: 'Command references' }
  ];
  
  transformations.forEach(({ from, to, name }) => {
    const hadFrom = claudeBody.includes(from);
    const hasTo = openCodeBody.includes(to);
    if (hadFrom && hasTo) {
      console.log(`   ✅ ${name}: "${from}" → "${to}"`);
    } else if (hadFrom && !hasTo) {
      console.log(`   ❌ ${name}: "${from}" not transformed`);
    }
  });
  
  console.log('');
}

/**
 * Validate transformation results
 */
function validateTransformation(original, transformed) {
  console.log('✅ VALIDATION RESULTS');
  console.log('=====================\n');
  
  const validation = validateTransformedCommand(transformed);
  
  if (validation.valid) {
    console.log('✅ Transformation is valid');
    console.log('   • Contains proper frontmatter structure');
    console.log('   • Has required description field');
    console.log('   • Has required agent field');
    console.log('   • No Claude-specific fields remaining');
  } else {
    console.log('❌ Transformation failed validation:');
    console.log(`   Error: ${validation.error}`);
    return false;
  }
  
  // Additional semantic checks
  const parts = transformed.split('---');
  if (parts.length >= 3) {
    const frontmatter = parts[1];
    const body = parts.slice(2).join('---');
    
    // Check for Claude artifacts
    const claudeArtifacts = [
      'allowed-tools:',
      'tools:',
      '.claude/',
      'Task tool'
    ];
    
    const foundArtifacts = claudeArtifacts.filter(artifact => 
      frontmatter.includes(artifact) || body.includes(artifact)
    );
    
    if (foundArtifacts.length > 0) {
      console.log('⚠️  Warning: Claude artifacts found:');
      foundArtifacts.forEach(artifact => console.log(`   • ${artifact}`));
    } else {
      console.log('✅ No Claude artifacts remaining');
    }
  }
  
  console.log('');
  return validation.valid;
}

/**
 * Run comprehensive test suite
 */
async function runTests(sourceFile) {
  console.log('🚀 COMMAND TRANSFORMER COMPREHENSIVE TEST');
  console.log('==========================================\n');
  
  let success = true;
  
  // Ensure output directory exists
  if (!existsSync(OUTPUT_DIR)) {
    await mkdir(OUTPUT_DIR, { recursive: true });
  }
  
  try {
    // Read source file
    let claudeContent;
    if (existsSync(sourceFile)) {
      claudeContent = await readFile(sourceFile, 'utf8');
      console.log(`📂 Testing: ${sourceFile}`);
    } else {
      console.log('📂 Source file not found, using built-in sample');
      claudeContent = getSampleClaudeCommand();
    }
    
    console.log('');
    
    // Show original
    showFrontmatter(claudeContent, 'ORIGINAL CLAUDE COMMAND');
    
    // Transform
    console.log('🔄 TRANSFORMING...\n');
    const transformedContent = transformCommand(claudeContent, {
      returnOriginalOnError: false,
      enableLogging: true
    });
    
    if (!transformedContent) {
      console.error('❌ Transformation failed');
      return false;
    }
    
    // Show result
    showFrontmatter(transformedContent, 'TRANSFORMED OPENCODE COMMAND');
    
    // Analysis
    showTransformationAnalysis(claudeContent, transformedContent);
    
    // Validation
    if (!validateTransformation(claudeContent, transformedContent)) {
      success = false;
    }
    
    // Save output for inspection
    const outputFile = join(OUTPUT_DIR, `${basename(sourceFile, '.md')}-converted.md`);
    await writeFile(outputFile, transformedContent, 'utf8');
    console.log(`💾 Saved converted command to: ${outputFile}`);
    
    // Compare with expected if available
    const expectedFile = sourceFile.replace('.md', '-expected.md');
    if (existsSync(expectedFile)) {
      const expectedContent = await readFile(expectedFile, 'utf8');
      
      console.log('\n🎯 EXPECTED COMPARISON');
      console.log('======================');
      
      if (transformedContent.trim() === expectedContent.trim()) {
        console.log('✅ Output matches expected result exactly');
      } else {
        console.log('⚠️  Output differs from expected result');
        
        // Show differences
        const transformedLines = transformedContent.trim().split('\n');
        const expectedLines = expectedContent.trim().split('\n');
        
        const maxLines = Math.max(transformedLines.length, expectedLines.length);
        let diffCount = 0;
        
        for (let i = 0; i < maxLines && diffCount < 5; i++) {
          const actual = transformedLines[i] || '<missing>';
          const expected = expectedLines[i] || '<missing>';
          
          if (actual !== expected) {
            console.log(`   Line ${i + 1}:`);
            console.log(`     Got:      "${actual}"`);
            console.log(`     Expected: "${expected}"`);
            diffCount++;
          }
        }
        
        if (diffCount >= 5) {
          console.log('   ... (more differences exist)');
        }
        
        success = false;
      }
    }
    
    // Unit tests for individual functions
    console.log('\n🧪 UNIT TESTS');
    console.log('==============');
    
    // Test parsing
    const parts = claudeContent.split('---');
    if (parts.length >= 3) {
      const parsed = parseCommandYAML(parts[1]);
      if (parsed && typeof parsed === 'object') {
        console.log('✅ parseCommandYAML: Successfully parsed frontmatter');
      } else {
        console.log('❌ parseCommandYAML: Failed to parse frontmatter');
        success = false;
      }
    }
    
    // Test validation
    const validationResult = validateTransformedCommand(transformedContent);
    if (validationResult.valid) {
      console.log('✅ validateTransformedCommand: Validation passed');
    } else {
      console.log(`❌ validateTransformedCommand: ${validationResult.error}`);
      success = false;
    }
    
    // Test sample functions
    const sampleClaude = getSampleClaudeCommand();
    const sampleOpenCode = getSampleOpenCodeCommand();
    if (sampleClaude.includes('allowed-tools:') && sampleOpenCode.includes('agent:')) {
      console.log('✅ Sample functions: Provide valid test data');
    } else {
      console.log('❌ Sample functions: Invalid test data');
      success = false;
    }
    
  } catch (error) {
    console.error('❌ Test failed with error:', error);
    success = false;
  }
  
  // Final result
  console.log('\n🏁 FINAL RESULT');
  console.log('================');
  if (success) {
    console.log('✅ ALL TESTS PASSED - Command transformation is working correctly');
    return true;
  } else {
    console.log('❌ SOME TESTS FAILED - Review output above for details');
    return false;
  }
}

/**
 * Main entry point
 */
async function main() {
  const sourceFile = process.argv[2] || DEFAULT_SOURCE;
  
  console.log('Command Transformer Test Suite');
  console.log('==============================');
  console.log(`Node.js: ${process.version}`);
  console.log(`Test file: ${basename(__filename)}`);
  console.log(`Source: ${sourceFile}`);
  console.log(`Output dir: ${OUTPUT_DIR}\n`);
  
  const success = await runTests(sourceFile);
  process.exit(success ? 0 : 1);
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}

export { runTests, showFrontmatter, showTransformationAnalysis, validateTransformation };