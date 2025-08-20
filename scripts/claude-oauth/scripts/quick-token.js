#!/usr/bin/env bun

/**
 * Quick OAuth Token Generator
 * A simplified Node.js/Bun script for generating Claude OAuth tokens
 */

import { execSync } from 'child_process';
import { readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectDir = dirname(__dirname);

console.log('🔐 Claude OAuth Token Generator');
console.log('===============================\n');

async function main() {
    try {
        // Change to project directory
        process.chdir(projectDir);
        
        // Check if we're in the right directory
        if (!existsSync('index.ts')) {
            throw new Error('index.ts not found. Are you in the correct project directory?');
        }
        
        console.log('📍 Project directory:', projectDir);
        console.log('🚀 Starting OAuth flow...\n');
        
        // Step 1: Generate login URL
        console.log('Step 1: Generating OAuth login URL...');
        const loginUrl = execSync('bun run index.ts', { encoding: 'utf8' }).trim();
        
        console.log('✅ Login URL generated:');
        console.log(`   ${loginUrl}\n`);
        
        console.log('📋 Instructions:');
        console.log('   1. Copy the URL above');
        console.log('   2. Open it in your browser');
        console.log('   3. Log in to Claude');
        console.log('   4. Copy the authorization code from the callback URL');
        console.log('   5. Run this script again with the code as an argument\n');
        
        console.log('💡 Usage with code:');
        console.log(`   bun run scripts/quick-token.js YOUR_AUTH_CODE_HERE\n`);
        
    } catch (error) {
        console.error('❌ Error:', error.message);
        process.exit(1);
    }
}

async function exchangeToken(authCode) {
    try {
        console.log('🔄 Exchanging authorization code for tokens...\n');
        
        // Exchange code for tokens
        execSync(`bun run index.ts "${authCode}"`, { 
            encoding: 'utf8',
            stdio: 'inherit'
        });
        
        // Check if credentials were created
        const credentialsPath = join(projectDir, 'credentials.json');
        if (existsSync(credentialsPath)) {
            const credentials = JSON.parse(readFileSync(credentialsPath, 'utf8'));
            const expiresAt = new Date(credentials.claudeAiOauth.expiresAt);
            
            console.log('\n🎉 Token generation successful!');
            console.log(`📁 Credentials saved to: ${credentialsPath}`);
            console.log(`⏰ Token expires: ${expiresAt.toLocaleString()}`);
            console.log(`🔑 Scopes: ${credentials.claudeAiOauth.scopes.join(', ')}\n`);
            
            console.log('⚠️  Security Notice:');
            console.log('   Keep credentials.json secure and never commit it to version control!');
        }
        
    } catch (error) {
        console.error('❌ Token exchange failed:', error.message);
        process.exit(1);
    }
}

// Handle command line arguments
const args = process.argv.slice(2);

if (args.length === 0) {
    // No auth code provided - generate login URL
    main();
} else if (args[0] === '--help' || args[0] === '-h') {
    console.log('Usage:');
    console.log('  bun run scripts/quick-token.js              # Generate login URL');
    console.log('  bun run scripts/quick-token.js <auth_code>  # Exchange code for tokens');
    console.log('');
    console.log('Options:');
    console.log('  --help, -h    Show this help message');
} else {
    // Auth code provided - exchange for tokens
    const authCode = args[0];
    exchangeToken(authCode);
}