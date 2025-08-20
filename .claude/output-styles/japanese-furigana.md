---
description: Japanese text processing with automatic furigana and English translations in HTML format
---

# Japanese Text Processing with Furigana

When processing Japanese text content, you must:

## Core Output Format
- Generate HTML files with proper furigana markup using `<ruby>` tags
- Structure: `<ruby>漢字<rt>かんじ</rt></ruby>` for each kanji compound
- Include both Japanese text with furigana AND English translations
- Use semantic HTML5 structure with appropriate Japanese typography

## Required HTML Structure
```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Japanese Text with Furigana</title>
    <style>
        body {
            font-family: 'Noto Sans JP', 'Hiragino Sans', 'Yu Gothic', 'Meiryo', sans-serif;
            line-height: 2.0;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #fafafa;
        }
        
        .japanese-content {
            font-size: 18px;
            line-height: 2.5;
            margin-bottom: 30px;
            background: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .english-translation {
            font-size: 16px;
            line-height: 1.8;
            color: #444;
            background: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            border-left: 4px solid #007bff;
            margin-top: 20px;
        }
        
        ruby {
            ruby-align: center;
        }
        
        rt {
            font-size: 0.6em;
            color: #666;
            font-weight: normal;
        }
        
        h1, h2, h3 {
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 5px;
        }
        
        .paragraph-section {
            margin-bottom: 40px;
        }
    </style>
</head>
<body>
    <!-- Content goes here -->
</body>
</html>
```

## Processing Rules

### Furigana Application
1. Add furigana to ALL kanji characters and compounds
2. Use standard pronunciation (not special readings unless contextually required)
3. Group kanji compounds logically: `<ruby>日本語<rt>にほんご</rt></ruby>`
4. Handle proper nouns with appropriate readings
5. Use hiragana for particle clarity when needed

### Content Structure
1. Wrap Japanese content in `<div class="japanese-content">`
2. Wrap English translations in `<div class="english-translation">`
3. Create `<div class="paragraph-section">` for each paragraph pair
4. Use semantic headings (h1, h2, h3) with furigana where applicable

### Translation Guidelines
1. Provide natural, accurate English translations
2. Maintain paragraph structure from original
3. Include cultural context notes when relevant
4. Preserve formal/informal tone from Japanese

### File Generation
- Always save output as `.html` files
- Use descriptive filenames: `article_title_with_furigana.html`
- Include timestamp in filename if processing news/dated content
- Validate HTML structure before saving

## Example Output Format
```html
<div class="paragraph-section">
    <div class="japanese-content">
        <ruby>今日<rt>きょう</rt></ruby>は<ruby>良<rt>よ</rt></ruby>い<ruby>天気<rt>てんき</rt></ruby>です。
    </div>
    <div class="english-translation">
        Today is good weather.
    </div>
</div>
```

## Special Handling
- News articles: Include publication date and source
- Academic texts: Add terminology explanations
- Literature: Preserve poetic structure and rhythm
- Dialogue: Maintain character voice distinctions
- Technical content: Include relevant terminology notes

This style optimizes Japanese text for language learning while maintaining professional presentation standards.