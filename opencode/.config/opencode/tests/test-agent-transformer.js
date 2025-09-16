#!/usr/bin/env node

/**
 * Comprehensive Agent Transformer Test
 * 
 * Combines detailed audit analysis with unit testing:
 * 1. Shows step-by-step transformation process
 * 2. Validates output against expected results
 * 3. Saves converted files for inspection
 * 4. Returns appropriate exit codes for CI/automation
 * 
 * Usage:
 *   node test-agent-transformer.js                    # Test default fixture
 *   node test-agent-transformer.js /path/to/agent.md  # Test specific agent
 */

import { readFile, writeFile, mkdir } from 'fs/promises';
import { join, dirname, basename } from 'path';
import { fileURLToPath } from 'url';
import { existsSync } from 'fs';
import { parseYAML, transformAgent } from '../plugin-util/agent-transformer-core.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

/**
 * Test configuration
 */
const DEFAULT_SOURCE = join(__dirname, 'fixtures', 'claude-test-agent.md');
const DEFAULT_EXPECTED = join(__dirname, 'fixtures', 'claude-test-agent-converted-expected.md');
const OUTPUT_DIR = join(__dirname, 'test-output', 'converted');

// Transformation functions imported from shared module

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
    console.log(`${String(i + 1).padStart(2)}: ${lines[i]}`);
  }
  console.log();
}

/**
 * Show transformation steps for audit display
 */
function showTransformationSteps(claudeFM, opencodeFM) {
  console.log('🔧 TRANSFORMATION STEPS:');
  console.log('-------------------------');
  
  // Show removed fields
  for (const [key, value] of Object.entries(claudeFM)) {
    if (!(key in opencodeFM)) {
      const truncatedValue = value.length > 30 ? value.substring(0, 30) + '...' : value;
      console.log(`   ${key}: "${truncatedValue}" → REMOVED`);
    }
  }
  
  // Show modified fields
  for (const [key, newValue] of Object.entries(opencodeFM)) {
    if (key in claudeFM && claudeFM[key] !== newValue) {
      console.log(`   ${key}: "${claudeFM[key]}" → "${newValue}"`);
    }
  }
  
  // Show new fields
  for (const [key, value] of Object.entries(opencodeFM)) {
    if (!(key in claudeFM)) {
      console.log(`   ${key}: NEW → "${value}"`);
    }
  }
  
  console.log();
}

/**
 * Validate OpenCode compatibility for audit
 */
function validateOpenCodeCompatibility(content) {
  console.log('🔍 OPENCODE COMPATIBILITY CHECK:');
  console.log('---------------------------------');
  
  const checks = [];
  
  // Check frontmatter structure
  const parts = content.split('---');
  if (parts.length >= 3) {
    checks.push('✅ Valid frontmatter structure');
  } else {
    checks.push('❌ Invalid frontmatter structure');
  }
  
  // Check required fields
  const frontmatterStr = parts[1] || '';
  const hasDescription = frontmatterStr.includes('description:');
  const hasMode = frontmatterStr.includes('mode:');
  const hasModel = frontmatterStr.includes('model:');
  const hasTools = frontmatterStr.includes('tools:');
  
  checks.push(hasDescription ? '✅ Description field present' : '❌ Missing description field');
  checks.push(hasMode ? '✅ Mode field present' : '❌ Missing mode field');
  checks.push(hasModel ? '✅ Model field present' : '❌ Missing model field');
  checks.push(!hasTools ? '✅ Tools field removed (good)' : '⚠️  Tools field still present');
  
  checks.forEach(check => console.log(`   ${check}`));
  
  const allPassed = checks.every(check => check.startsWith('✅'));
  
  console.log();
  if (allPassed) {
    console.log('✅ PASS - Agent should work in OpenCode');
  } else {
    console.log('❌ FAIL - Agent may have compatibility issues');
  }
  
  console.log();
  return allPassed;
}

/**
 * Ensure output directory exists
 */
async function ensureOutputDir() {
  if (!existsSync(OUTPUT_DIR)) {
    await mkdir(OUTPUT_DIR, { recursive: true });
  }
}

/**
 * Save converted agent and return path
 */
async function saveConvertedAgent(originalPath, convertedContent) {
  await ensureOutputDir();
  
  const originalName = basename(originalPath, '.md');
  const outputPath = join(OUTPUT_DIR, `${originalName}-converted.md`);
  
  await writeFile(outputPath, convertedContent, 'utf8');
  
  console.log('💾 OUTPUT SAVED:');
  console.log('-----------------');
  console.log(`✅ Converted file: ${outputPath}`);
  console.log(`📏 File size: ${convertedContent.length} bytes`);
  console.log();
  
  return outputPath;
}

/**
 * Normalize content for comparison (handle whitespace differences)
 */
function normalizeContent(content) {
  return content
    .trim()
    .replace(/\r\n/g, '\n')  // Normalize line endings
    .replace(/\n\s*\n/g, '\n\n')  // Normalize multiple newlines
    .replace(/\s+$/gm, '');  // Remove trailing whitespace on lines
}

/**
 * Compare two YAML frontmatters
 */
function compareFrontmatter(actual, expected) {
  const actualLines = actual.split('\n').filter(line => line.trim());
  const expectedLines = expected.split('\n').filter(line => line.trim());
  
  const differences = [];
  
  // Check that all expected lines are present
  for (const expectedLine of expectedLines) {
    if (!actualLines.includes(expectedLine)) {
      differences.push(`Missing: ${expectedLine}`);
    }
  }
  
  // Check for unexpected lines
  for (const actualLine of actualLines) {
    if (!expectedLines.includes(actualLine)) {
      differences.push(`Unexpected: ${actualLine}`);
    }
  }
  
  return differences;
}

/**
 * Detailed content comparison
 */
function compareContent(actual, expected) {
  const results = {
    passed: true,
    differences: [],
    summary: {
      actualSize: actual.length,
      expectedSize: expected.length,
      sizeDelta: actual.length - expected.length
    }
  };
  
  // Normalize for comparison
  const normalizedActual = normalizeContent(actual);
  const normalizedExpected = normalizeContent(expected);
  
  if (normalizedActual === normalizedExpected) {
    results.summary.status = 'EXACT MATCH';
    return results;
  }
  
  results.passed = false;
  
  // Split into frontmatter and body for detailed analysis
  const actualParts = actual.split('---');
  const expectedParts = expected.split('---');
  
  if (actualParts.length !== expectedParts.length) {
    results.differences.push(`Structure mismatch: actual has ${actualParts.length} parts, expected has ${expectedParts.length}`);
    return results;
  }
  
  // Compare frontmatter
  if (actualParts.length >= 2) {
    const frontmatterDiffs = compareFrontmatter(actualParts[1], expectedParts[1]);
    if (frontmatterDiffs.length > 0) {
      results.differences.push('Frontmatter differences:');
      frontmatterDiffs.forEach(diff => results.differences.push(`  ${diff}`));
    }
  }
  
  // Compare body content
  if (actualParts.length >= 3) {
    const actualBody = actualParts.slice(2).join('---').trim();
    const expectedBody = expectedParts.slice(2).join('---').trim();
    
    if (actualBody !== expectedBody) {
      results.differences.push('Body content differences:');
      results.differences.push(`  Actual: "${actualBody}"`);
      results.differences.push(`  Expected: "${expectedBody}"`);
    }
  }
  
  return results;
}

/**
 * Main comprehensive test function
 */
async function runComprehensiveTest() {
  // Parse command line arguments
  const customSourceFile = process.argv[2];
  const sourceFile = customSourceFile || DEFAULT_SOURCE;
  const expectedFile = customSourceFile ? null : DEFAULT_EXPECTED;
  const agentName = basename(sourceFile);
  
  console.log('🧪 COMPREHENSIVE AGENT TRANSFORMER TEST');
  console.log('==========================================\n');
  
  console.log('📋 TEST PHASES:');
  console.log('   1️⃣  Detailed Audit Analysis');
  console.log('   2️⃣  Unit Test Validation');
  console.log('   3️⃣  File Output & Summary\n');
  
  console.log(`📁 Source: ${sourceFile}`);
  if (expectedFile) {
    console.log(`🎯 Expected: ${expectedFile}`);
  }
  console.log();
  
  try {
    console.log('🔄 PHASE 1: DETAILED AUDIT ANALYSIS');
    console.log('====================================\n');
    
    // Read source file
    console.log('📖 Loading source Claude agent...');
    const sourceContent = await readFile(sourceFile, 'utf8');
    console.log(`   ✅ Source loaded (${sourceContent.length} chars)\n`);
    
    // Show original format
    showFrontmatter(sourceContent, 'ORIGINAL CLAUDE FORMAT');
    
    // Parse original frontmatter for analysis
    const parts = sourceContent.split('---');
    const claudeFM = parseYAML(parts[1] || '');
    
    // Transform the content
    console.log('🔄 Applying transformation...');
    const transformedContent = transformAgent(sourceContent);
    console.log(`   ✅ Transformation complete (${transformedContent.length} chars)\n`);
    
    // Parse transformed frontmatter for analysis
    const transformedParts = transformedContent.split('---');
    const opencodeFM = parseYAML(transformedParts[1] || '');
    
    // Show transformation steps
    showTransformationSteps(claudeFM, opencodeFM);
    
    // Show transformed format
    showFrontmatter(transformedContent, 'TRANSFORMED OPENCODE FORMAT');
    
    // Save converted agent
    const outputPath = await saveConvertedAgent(sourceFile, transformedContent);
    
    // Validate compatibility
    const compatibilityPassed = validateOpenCodeCompatibility(transformedContent);
    
    // Summary of audit phase
    console.log('📊 AUDIT SUMMARY:');
    console.log('------------------');
    const sizeDelta = transformedContent.length - sourceContent.length;
    const sizeChange = sizeDelta >= 0 ? `+${sizeDelta}` : `${sizeDelta}`;
    console.log(`📏 Size change: ${sourceContent.length} → ${transformedContent.length} chars (${sizeChange})`);
    console.log(`🔧 Fields removed: ${Object.keys(claudeFM).filter(k => !(k in opencodeFM)).length}`);
    console.log(`🆕 Fields added: ${Object.keys(opencodeFM).filter(k => !(k in claudeFM)).length}`);
    console.log(`📁 Output: ${outputPath}`);
    console.log(`🔍 Compatibility: ${compatibilityPassed ? 'PASS' : 'FAIL'}\n`);
    
    // Phase 2: Unit test validation (only if expected file exists)
    let testPassed = true;
    if (expectedFile && existsSync(expectedFile)) {
      console.log('🔄 PHASE 2: UNIT TEST VALIDATION');
      console.log('=================================\n');
      
      console.log('📖 Loading expected output...');
      const expectedContent = await readFile(expectedFile, 'utf8');
      console.log(`   ✅ Expected loaded (${expectedContent.length} chars)\n`);
      
      console.log('🔍 Comparing actual vs expected results...');
      const comparison = compareContent(transformedContent, expectedContent);
      
      console.log('\n📊 UNIT TEST RESULTS:');
      console.log('----------------------');
      
      if (comparison.passed) {
        console.log('✅ PASS - Transformation matches expected output exactly');
        console.log(`📏 Size: ${comparison.summary.actualSize} chars`);
        console.log(`🎯 Status: ${comparison.summary.status}`);
        testPassed = true;
      } else {
        console.log('❌ FAIL - Transformation does not match expected output');
        console.log(`📏 Actual size: ${comparison.summary.actualSize} chars`);
        console.log(`📏 Expected size: ${comparison.summary.expectedSize} chars`);
        console.log(`📏 Size delta: ${comparison.summary.sizeDelta} chars`);
        
        console.log('\n🔍 Differences found:');
        comparison.differences.forEach(diff => {
          console.log(`   ${diff}`);
        });
        testPassed = false;
      }
      console.log();
    } else {
      console.log('⏭️  PHASE 2: SKIPPED (No expected output file for comparison)\n');
    }
    
    // Phase 3: Final summary
    console.log('🔄 PHASE 3: FINAL SUMMARY');
    console.log('==========================\n');
    
    const overallPassed = compatibilityPassed && testPassed;
    
    console.log('🏆 OVERALL RESULTS:');
    console.log('-------------------');
    console.log(`📋 Agent: ${agentName}`);
    console.log(`🔍 Audit: ${compatibilityPassed ? '✅ PASS' : '❌ FAIL'}`);
    console.log(`🧪 Unit Test: ${expectedFile ? (testPassed ? '✅ PASS' : '❌ FAIL') : '⏭️  SKIPPED'}`);
    console.log(`📁 Output: ${outputPath}`);
    console.log(`🎯 Overall: ${overallPassed ? '✅ PASS' : '❌ FAIL'}\n`);
    
    console.log('🏁 Test completed\n');
    
    // Exit with appropriate code
    process.exit(overallPassed ? 0 : 1);
    
  } catch (error) {
    console.error('❌ TEST FAILED with error:', error.message);
    console.error('\n📍 Stack trace:');
    console.error(error.stack);
    process.exit(1);
  }
}

// Run the comprehensive test
runComprehensiveTest();