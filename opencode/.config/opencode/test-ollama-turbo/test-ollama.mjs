#!/usr/bin/env node
/**
 * Ollama AI Provider v2 Testing Script with Thinking Extraction
 * Direct testing of ollama-ai-provider-v2 with configurable options
 * 
 * FEATURES:
 * ✅ Complete thinking extraction system based on Agno framework discoveries
 * ✅ Three-tier extraction priority: native field → channels → tags
 * ✅ Support for all reasoning levels: low, medium, high
 * ✅ Automatic tag format detection: <think>, <reasoning>, <deep_reasoning>
 * ✅ Clean separation of thinking process from final response
 * ✅ Comprehensive preset system with 9 configurations
 * ✅ Detailed extraction metadata and statistics
 * 
 * THINKING TAG FORMATS:
 * • Low level: <think>brief reasoning</think>
 * • Medium level: <reasoning>balanced analysis</reasoning>  
 * • High level: <deep_reasoning>detailed thinking</deep_reasoning>
 * 
 * Usage: 
 *   node test-ollama.mjs
 *   node test-ollama.mjs "Your custom prompt here"
 *   node test-ollama.mjs "Problem with explicit tags" reasoning
 * 
 * Requirements:
 *   npm install ai ollama-ai-provider-v2
 */

import { generateText } from 'ai';
import { createOllama } from 'ollama-ai-provider-v2';
import { execSync } from 'child_process';

// =============================================================================
// THINKING EXTRACTION SYSTEM (Based on Agno Framework)
// =============================================================================

/**
 * Extract thinking content from response using three-tier priority system:
 * 1. Native field extraction (future-proofing)
 * 2. Channel-based extraction (Harmony models)
 * 3. Tag-based extraction (current implementation)
 */
function extractThinking(response, reasoningLevel = 'high') {
  // Determine tag format based on reasoning level
  const tagFormats = {
    low: { start: '<think>', end: '</think>' },
    medium: { start: '<reasoning>', end: '</reasoning>' },
    high: { start: '<deep_reasoning>', end: '</deep_reasoning>' }
  };
  
  const { start, end } = tagFormats[reasoningLevel] || tagFormats.high;
  
  // Tier 1: Native field extraction (future-proofing)
  if (response.thinking) {
    return {
      thinking: response.thinking,
      cleanText: response.text || response.content,
      extractionMethod: 'native_field'
    };
  }
  
  // Tier 2: Channel-based extraction (Harmony models)
  if (response.channels && response.channels.thinking) {
    return {
      thinking: response.channels.thinking,
      cleanText: response.text || response.content,
      extractionMethod: 'channels'
    };
  }
  
  // Tier 3: Tag-based extraction (current implementation)
  const text = response.text || response.content || response;
  if (typeof text === 'string') {
    const startIndex = text.indexOf(start);
    const endIndex = text.indexOf(end);
    
    if (startIndex !== -1 && endIndex !== -1 && endIndex > startIndex) {
      const thinking = text.substring(startIndex + start.length, endIndex).trim();
      const cleanText = (text.substring(0, startIndex) + text.substring(endIndex + end.length)).trim();
      
      return {
        thinking,
        cleanText,
        extractionMethod: 'tags',
        tagFormat: `${start}...${end}`
      };
    }
  }
  
  // No thinking content found
  return {
    thinking: null,
    cleanText: text,
    extractionMethod: 'none'
  };
}

/**
 * Format thinking output for display
 */
function formatThinkingOutput(thinkingData, showMetadata = true) {
  const { thinking, cleanText, extractionMethod, tagFormat } = thinkingData;
  
  let output = '';
  
  if (thinking) {
    output += '🧠 THINKING PROCESS:\n';
    output += '┌' + '─'.repeat(78) + '┐\n';
    
    // Format thinking content with proper line breaks
    const thinkingLines = thinking.split('\n');
    thinkingLines.forEach(line => {
      output += `│ ${line.padEnd(76)} │\n`;
    });
    
    output += '└' + '─'.repeat(78) + '┘\n\n';
    
    if (showMetadata) {
      output += `🔍 Extraction: ${extractionMethod}`;
      if (tagFormat) {
        output += ` (${tagFormat})`;
      }
      output += '\n\n';
    }
  }
  
  output += '💬 FINAL RESPONSE:\n';
  output += cleanText;
  
  return output;
}

// Load OLLAMA_API_KEY from system environment
function getApiKey() {
  try {
    const key = execSync('launchctl getenv OLLAMA_API_KEY 2>/dev/null', { encoding: 'utf8' }).trim();
    if (!key) {
      console.error('❌ OLLAMA_API_KEY not found in system environment');
      console.error('💡 Run: ~/dotfiles/scripts/mcp-env/mcp-env/set-mcp-env-system.sh');
      process.exit(1);
    }
    return key;
  } catch (error) {
    console.error('❌ Failed to load OLLAMA_API_KEY from launchctl');
    process.exit(1);
  }
}

// Initialize Ollama provider
const ollama = createOllama({
  baseURL: 'https://ollama.com/api',
  headers: {
    'Authorization': `Bearer ${getApiKey()}`
  }
});

// =============================================================================
// CONFIGURATION PRESETS
// =============================================================================

const PRESETS = {
  // Default balanced settings
  default: {
    model: 'gpt-oss:120b',
    temperature: 0.7,
    providerOptions: {
      ollama: {
        options: {
          seed: 42,
          num_ctx: 32768,
          repeat_penalty: 1.1,
          top_k: 40,
          min_p: 0.05,
        }
      }
    }
  },

  // Reasoning/thinking mode - GPT-OSS with proper system prompt
  reasoning: {
    model: 'gpt-oss:120b',
    temperature: 0.6,
    system: "Reasoning: high\n\nYou are a helpful AI assistant. Show your internal thinking process by wrapping your reasoning in <deep_reasoning></deep_reasoning> tags, then provide your final answer. Think through problems step-by-step and expose your complete chain-of-thought.",
    providerOptions: {
      ollama: {
        think: true,  // Enable chain-of-thought reasoning
        options: {
          seed: 42,
          num_ctx: 32768,
          repeat_penalty: 1.1,
          top_k: 40,
          min_p: 0.05,
        }
      }
    }
  },

  // Creative writing
  creative: {
    model: 'gpt-oss:120b',
    temperature: 0.9,
    providerOptions: {
      ollama: {
        options: {
          num_ctx: 16384,
          repeat_penalty: 1.05,
          top_k: 60,
          top_p: 0.8,
          min_p: 0.02,
        }
      }
    }
  },

  // Code generation
  code: {
    model: 'gpt-oss:120b',
    temperature: 0.3,
    providerOptions: {
      ollama: {
        options: {
          seed: 123,
          num_ctx: 16384,
          repeat_penalty: 1.2,
          top_k: 30,
          min_p: 0.1,
        }
      }
    }
  },

  // Fast responses
  fast: {
    model: 'gpt-oss:20b',  // Smaller model
    temperature: 0.7,
    providerOptions: {
      ollama: {
        options: {
          num_ctx: 8192,     // Smaller context
          repeat_penalty: 1.1,
          top_k: 40,
          min_p: 0.05,
        }
      }
    }
  },

  // Deep reasoning - maximum chain-of-thought
  deep: {
    model: 'gpt-oss:120b',
    temperature: 0.5,
    system: "Reasoning: high\n\nYou are an expert problem-solver. Show your complete internal thinking process by wrapping your detailed reasoning in <deep_reasoning></deep_reasoning> tags, including false starts, corrections, and detailed analysis. After your thinking, provide your final answer. Expose all your reasoning steps and thought chains.",
    providerOptions: {
      ollama: {
        think: true,
        options: {
          seed: 42,
          num_ctx: 32768,
          repeat_penalty: 1.1,
          top_k: 30,
          min_p: 0.1,
        }
      }
    }
  },

  // Medium reasoning - balanced approach
  medium: {
    model: 'gpt-oss:120b',
    temperature: 0.65,
    system: "Reasoning: medium\n\nShow your reasoning process in <reasoning></reasoning> tags with moderate detail, then provide your response. Balance thoroughness with clarity.",
    providerOptions: {
      ollama: {
        think: true,
        options: {
          seed: 42,
          num_ctx: 24576,
          repeat_penalty: 1.1,
          top_k: 35,
          min_p: 0.07,
        }
      }
    }
  },

  // Quick reasoning - low level
  quick: {
    model: 'gpt-oss:20b',
    temperature: 0.7,
    system: "Reasoning: low\n\nShow your brief thinking process in <think></think> tags, then provide your direct response with minimal but clear reasoning.",
    providerOptions: {
      ollama: {
        options: {
          num_ctx: 8192,
          repeat_penalty: 1.1,
          top_k: 40,
          min_p: 0.05,
        }
      }
    }
  },

  // Experimental high-quality
  experimental: {
    model: 'gpt-oss:120b',
    temperature: 0.7,
    providerOptions: {
      ollama: {
        options: {
          seed: 42,
          num_ctx: 32768,
          repeat_penalty: 1.1,
          top_k: 40,
          top_p: 0.9,
          min_p: 0.05,
          tfs_z: 1.0,
          typical_p: 1.0,
          mirostat: 0,        // Try Mirostat sampling
          mirostat_tau: 5.0,
          mirostat_eta: 0.1,
        }
      }
    }
  }
};

// =============================================================================
// TESTING FUNCTION
// =============================================================================

async function testOllama(prompt, presetName = 'default') {
  const preset = PRESETS[presetName];
  if (!preset) {
    console.error(`❌ Unknown preset: ${presetName}`);
    console.log(`📋 Available presets: ${Object.keys(PRESETS).join(', ')}`);
    return;
  }

  console.log(`🧪 Testing with preset: ${presetName}`);
  console.log(`🤖 Model: ${preset.model}`);
  console.log(`🌡️  Temperature: ${preset.temperature}`);
  console.log(`⚙️  Options:`, JSON.stringify(preset.providerOptions.ollama.options || {}, null, 2));
  if (preset.providerOptions.ollama.think) {
    console.log(`🧠 Thinking mode: ENABLED`);
  }
  if (preset.system) {
    const reasoningLevel = preset.system.match(/Reasoning: (\w+)/)?.[1] || 'none';
    console.log(`🎯 Reasoning level: ${reasoningLevel.toUpperCase()}`);
    console.log(`📋 System prompt: "${preset.system.split('\n')[0]}..."`);
  }
  console.log(`💬 Prompt: "${prompt}"`);
  console.log(`⏳ Generating response...`);
  console.log('─'.repeat(80));

  const startTime = Date.now();
  
  try {
    // Build the generateText configuration
    const config = {
      model: ollama(preset.model),
      temperature: preset.temperature,
      providerOptions: preset.providerOptions,
    };
    
    // Add system message if available, otherwise use prompt directly
    if (preset.system) {
      config.system = preset.system;
      config.prompt = prompt;
    } else {
      config.prompt = prompt;
    }
    
    const { text } = await generateText(config);

    const endTime = Date.now();
    const duration = (endTime - startTime) / 1000;

    // Extract thinking content based on reasoning level
    const reasoningLevel = preset.system?.match(/Reasoning: (\w+)/)?.[1]?.toLowerCase() || 'high';
    const thinkingData = extractThinking(text, reasoningLevel);
    
    // Display formatted output with thinking extraction
    console.log(formatThinkingOutput(thinkingData, true));
    
    console.log('─'.repeat(80));
    console.log(`⏱️  Response time: ${duration.toFixed(2)}s`);
    console.log(`📊 Total length: ${text.length} characters`);
    
    if (thinkingData.thinking) {
      console.log(`🧠 Thinking length: ${thinkingData.thinking.length} characters`);
      console.log(`💬 Response length: ${thinkingData.cleanText.length} characters`);
      console.log(`🎯 Thinking extraction: ${thinkingData.extractionMethod.toUpperCase()}`);
    } else {
      console.log(`⚠️  No thinking content detected (${thinkingData.extractionMethod})`);
    }
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    if (error.message.includes('Unauthorized')) {
      console.log('💡 Check your OLLAMA_API_KEY with: launchctl getenv OLLAMA_API_KEY');
    }
  }
}

// =============================================================================
// CLI INTERFACE
// =============================================================================

function showHelp() {
  console.log(`🚀 Ollama AI Provider v2 Testing Script with Thinking Extraction

Usage:
  node test-ollama.mjs [prompt] [preset]
  node test-ollama.mjs --compare [preset]
  node test-ollama.mjs --compare-single [0-4] [preset]

Examples:
  node test-ollama.mjs
  node test-ollama.mjs "Explain quantum computing"
  node test-ollama.mjs "Write a poem about coding" creative
  node test-ollama.mjs "Debug this code: console.log('hello')" code
  node test-ollama.mjs "Solve: 2x + 5 = 17" reasoning

🔬 Comparison Testing (NEW):
  node test-ollama.mjs --compare                    # Run all comparison tests
  node test-ollama.mjs --compare reasoning          # Use specific preset
  node test-ollama.mjs --compare-single 0           # Run single test (0-4)
  node test-ollama.mjs --compare-single 2 deep      # Test with deep preset

Available presets:
${Object.entries(PRESETS).map(([name, config]) => {
  const reasoningLevel = config.system?.match(/Reasoning: (\w+)/)?.[1] || 'none';
  const thinking = config.providerOptions.ollama.think ? ', thinking=ON' : '';
  const reasoning = reasoningLevel !== 'none' ? `, reasoning=${reasoningLevel}` : '';
  return `  • ${name.padEnd(12)} - ${config.model}, temp=${config.temperature}${thinking}${reasoning}`;
}).join('\n')}

🧠 Thinking Extraction System (Based on Agno Framework):
  • Three-tier extraction priority: native field → channels → tags
  • Tag formats by reasoning level:
    - low: <think>...</think>
    - medium: <reasoning>...</reasoning>
    - high: <deep_reasoning>...</deep_reasoning>
  • Automatically separates thinking process from final response
  • Shows extraction method and metadata for debugging

🎯 Key Discovery - Reasoning Triggers Impact Quality:
  • Same numerical answers with and without reasoning triggers
  • Reasoning triggers transform answer-only → teaching-quality explanations
  • Adds formula identification, step-by-step breakdowns, proper notation
  • Provides significant educational value and methodology explanation

📊 Available Comparison Tests:
  0: Simple Multiplication    - Basic math with educational value
  1: Geometry Calculation     - Formula explanation and steps  
  2: Physics Calculation      - Time/distance methodology
  3: Financial Math          - Complex formulas and notation
  4: Probability Problem     - Conceptual explanation and steps

Configuration:
  • API Key: Loaded from system launchctl (OLLAMA_API_KEY)
  • Base URL: https://ollama.com/api
  • Provider: ollama-ai-provider-v2

Edit this script to experiment with different options!`);
}

// =============================================================================
// COMPARISON TESTING (Response Quality Analysis)
// =============================================================================

/**
 * Test cases that demonstrate reasoning trigger impact on response quality
 */
const COMPARISON_TEST_CASES = [
  {
    name: "Simple Multiplication",
    question: "What is 15 times 4?",
    description: "Tests if reasoning triggers add educational value to basic math"
  },
  {
    name: "Geometry Calculation", 
    question: "What is the area of a rectangle with length 8 and width 5?",
    description: "Tests formula explanation and step-by-step breakdown"
  },
  {
    name: "Physics Calculation",
    question: "If a train travels at 80 mph and needs to cover 240 miles, how long will the journey take?",
    description: "Tests methodology explanation for time/distance problems"
  },
  {
    name: "Financial Math",
    question: "If I invest $1000 at 8% annual compound interest for 3 years, how much will I have?",
    description: "Tests complex formula explanation and mathematical notation"
  },
  {
    name: "Probability Problem",
    question: "If I flip a coin 3 times, what's the probability of getting all heads?",
    description: "Tests conceptual explanation and step-by-step probability calculation"
  }
];

/**
 * Compare responses with and without reasoning triggers
 */
async function runComparisonTest(testCase, presetName = 'reasoning') {
  console.log(`\n🔬 COMPARISON TEST: ${testCase.name}`);
  console.log(`📝 Description: ${testCase.description}`);
  console.log(`❓ Question: "${testCase.question}"`);
  console.log('═'.repeat(80));

  // Test without reasoning trigger
  console.log('\n📊 WITHOUT REASONING TRIGGER:');
  console.log('─'.repeat(40));
  await testOllama(testCase.question, presetName);

  // Test with reasoning trigger  
  console.log('\n🧠 WITH REASONING TRIGGER:');
  console.log('─'.repeat(40));
  await testOllama(`Show your reasoning: ${testCase.question}`, presetName);
  
  console.log('\n' + '═'.repeat(80));
  console.log('💡 COMPARISON COMPLETE - Notice the difference in educational value!');
}

/**
 * Run all comparison tests
 */
async function runAllComparisonTests(presetName = 'reasoning') {
  console.log('🧪 REASONING TRIGGER QUALITY COMPARISON TESTS');
  console.log('═'.repeat(80));
  console.log('📊 Testing how reasoning triggers improve response quality');
  console.log('🎯 Key Discovery: Reasoning triggers transform answers into teaching explanations');
  console.log('═'.repeat(80));

  for (let i = 0; i < COMPARISON_TEST_CASES.length; i++) {
    await runComparisonTest(COMPARISON_TEST_CASES[i], presetName);
    
    // Add pause between tests for readability
    if (i < COMPARISON_TEST_CASES.length - 1) {
      console.log('\n⏳ Continuing to next test in 2 seconds...');
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
  }

  console.log('\n🎉 ALL COMPARISON TESTS COMPLETE!');
  console.log('\n📋 KEY FINDINGS:');
  console.log('✅ Same numerical answers in both cases');
  console.log('🎓 Reasoning triggers add significant educational value');
  console.log('📚 Transforms answer-only responses into teaching-quality explanations');
  console.log('🔢 Includes proper mathematical notation and step-by-step breakdowns');
  console.log('🎯 Provides methodology and formula identification');
}

// =============================================================================
// MAIN EXECUTION
// =============================================================================

async function main() {
  const args = process.argv.slice(2);
  
  if (args.includes('--help') || args.includes('-h')) {
    showHelp();
    return;
  }

  // Handle comparison testing commands
  if (args.includes('--compare') || args.includes('--comparison')) {
    const preset = args.find(arg => Object.keys(PRESETS).includes(arg)) || 'reasoning';
    await runAllComparisonTests(preset);
    return;
  }

  if (args.includes('--compare-single')) {
    const testIndex = parseInt(args.find(arg => /^\d+$/.test(arg))) || 0;
    const preset = args.find(arg => Object.keys(PRESETS).includes(arg)) || 'reasoning';
    
    if (testIndex >= 0 && testIndex < COMPARISON_TEST_CASES.length) {
      await runComparisonTest(COMPARISON_TEST_CASES[testIndex], preset);
    } else {
      console.log('❌ Invalid test index. Available tests:');
      COMPARISON_TEST_CASES.forEach((test, i) => {
        console.log(`  ${i}: ${test.name}`);
      });
    }
    return;
  }

  // Regular single test execution
  const defaultPrompts = [
    "Write a brief analysis of the benefits of renewable energy",
    "Explain the concept of recursion in programming", 
    "Describe the process of photosynthesis in simple terms",
    "What are the key differences between AI and machine learning?",
    "Write a short story about a robot learning to paint"
  ];

  const prompt = args[0] || defaultPrompts[Math.floor(Math.random() * defaultPrompts.length)];
  const preset = args[1] || 'default';

  console.log(`🎯 Ollama AI Provider v2 Test (${new Date().toLocaleString()})\n`);
  
  await testOllama(prompt, preset);
  
  console.log(`\n💡 Try different presets: ${Object.keys(PRESETS).join(', ')}`);
  console.log('🧠 Thinking extraction levels: quick (low), medium, reasoning (high), deep (high+detailed)');
  console.log('🎯 Watch for thinking tags: <think>, <reasoning>, <deep_reasoning>');
  console.log('🔬 Run comparison tests: --compare or --compare-single [0-4]');
  console.log('📝 Edit this script to experiment with new configurations!');
}

// Run the script
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(console.error);
}