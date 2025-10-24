# MinerU PDF Extraction Tool

**Version**: 2.5
**Purpose**: Advanced PDF data extraction with formula recognition, table parsing, and LLM-ready markdown output
**Platform**: macOS Apple Silicon (M1/M2/M3/M4)
**Python**: 3.10 - 3.13

---

## Quick Start

### Installation
```bash
# From vault root
make -C .tools/mineru install

# Or from this directory
cd .tools/mineru
make install
```

### Basic Usage
```bash
# Convert single PDF
make -C .tools/mineru convert FILE=path/to/document.pdf

# Specify custom output directory
make -C .tools/mineru convert FILE=input.pdf OUTPUT=custom_output/

# Batch convert all PDFs in a directory
make -C .tools/mineru batch DIR=path/to/pdfs/

# Test installation
make -C .tools/mineru test
```

---

## What is MinerU?

MinerU is an advanced PDF extraction tool that converts complex documents into LLM-ready markdown/JSON formats.

### Key Features
- ✅ **Formula Recognition**: Extracts mathematical equations accurately
- ✅ **Table Parsing**: Maintains table structure and relationships
- ✅ **Layout Analysis**: Preserves document structure and hierarchy
- ✅ **Multilingual OCR**: Supports 84 languages
- ✅ **MPS Acceleration**: Uses Apple Silicon GPU for faster processing
- ✅ **Batch Processing**: Handle multiple documents efficiently

### When to Use MinerU vs Docling

| Use Case | Tool | Why |
|----------|------|-----|
| Tax forms with tables | MinerU | Superior table extraction |
| Financial statements | MinerU | Better structured data parsing |
| Technical papers with formulas | MinerU | Formula recognition |
| Books & reports | Docling | Better for narrative content |
| General PDFs | Docling | Faster, simpler |
| Quick markdown cleanup | Docling | Built-in cleaning |

**Best Practice**: Keep both! Use MinerU for complex/structured PDFs, Docling for general documents.

---

## Installation

### System Requirements
- ✅ macOS with Apple Silicon (M1/M2/M3/M4)
- ✅ Python 3.10 - 3.13 (NOT 3.14+)
- ✅ 16GB+ RAM (32GB recommended)
- ✅ 20GB+ storage for models

### First-Time Setup
```bash
# From vault root
make -C .tools/mineru install

# Verify installation
make -C .tools/mineru test
```

This will:
1. Create isolated Python virtual environment
2. Install `uv` package manager
3. Install MinerU core package
4. Download required models (~2GB)

---

## Usage

### Convert Single PDF
```bash
# Basic conversion (output to same directory as PDF)
make -C .tools/mineru convert FILE=/path/to/document.pdf

# Custom output directory
make -C .tools/mineru convert FILE=input.pdf OUTPUT=my_output/

# From tax documents
make -C .tools/mineru convert FILE=roles/life-architect/projects/tax-preparation-2025/tax-docs-dropbox/01-Income/W2-Forms/2024_W2.pdf
```

**Output Structure**:
```
mineru_output/
├── document.md        # Extracted markdown
├── images/           # Extracted images
├── tables/           # Extracted tables (if any)
└── metadata.json     # Document metadata
```

### Batch Convert Multiple PDFs
```bash
# Convert all PDFs in a directory
make -C .tools/mineru batch DIR=/path/to/pdfs/

# Custom output location
make -C .tools/mineru batch DIR=input_pdfs/ OUTPUT=results/
```

### Direct Command-Line Usage
```bash
# Activate environment first
cd .tools/mineru
source venv/bin/activate

# Run MinerU directly
mineru -p input.pdf -o output_directory/

# Advanced options
mineru -p input.pdf -o output/ --lang en --batch-size 10

# Deactivate when done
deactivate
```

---

## Privacy & Sensitive Documents

### ⚠️ Important: Tax & Financial Documents

When using MinerU on sensitive documents (tax forms, bank statements, etc.):

1. **Outputs contain sensitive data**: Extracted markdown will include all text from PDFs (SSNs, account numbers, etc.)
2. **Secure output location**: Store outputs in same secure location as source PDFs
3. **Git exclusion**: Add output directories to `.gitignore`
4. **Cleanup**: Use `make clean` to remove temporary files after processing

### Recommended Workflow for Tax Documents
```bash
# Convert tax PDFs (output stays in same secure folder)
make -C .tools/mineru convert FILE=tax-docs-dropbox/01-Income/W2-Forms/2024_W2.pdf

# Output automatically goes to: tax-docs-dropbox/01-Income/W2-Forms/mineru_output/

# Extract specific data manually (don't commit markdown to git)
# Add to .gitignore:
echo "**/mineru_output/" >> .gitignore
```

---

## Troubleshooting

### Common Issues

#### Issue 1: OpenGL Library Error
**Error**: `Symbol not found: _CGLGetCurrentContext`

**Solution**:
```bash
make -C .tools/mineru fix-opengl

# Or manually:
unset DYLD_LIBRARY_PATH
```

#### Issue 2: Python Version Error
**Error**: `MinerU requires Python 3.10-3.13`

**Solution**:
```bash
# Check your Python version
python3 --version

# If 3.14+, use pyenv to install 3.12
pyenv install 3.12.1
pyenv local 3.12.1

# Reinstall
make -C .tools/mineru clean-all
make -C .tools/mineru install
```

#### Issue 3: Installation Failed
**Error**: Various installation errors

**Solution**:
```bash
# Clean and reinstall
make -C .tools/mineru clean-all
make -C .tools/mineru install

# If still failing, check:
python3 --version  # Must be 3.10-3.13
which python3      # Should be a valid path
```

#### Issue 4: Slow Performance
**Symptoms**: Conversion taking very long

**Solutions**:
- Ensure you're on AC power (MPS acceleration may throttle on battery)
- Close other resource-intensive apps
- Try smaller batch sizes: `mineru -p input.pdf --batch-size 5`
- Check Activity Monitor for memory usage

---

## Advanced Usage

### Custom Configuration
```bash
cd .tools/mineru
source venv/bin/activate

# English-only OCR (faster)
mineru -p input.pdf -o output/ --lang en

# Specific page range
mineru -p input.pdf -o output/ --pages 1-10

# JSON output instead of markdown
mineru -p input.pdf -o output/ --format json

# Batch size adjustment (lower = less memory)
mineru -p input.pdf -o output/ --batch-size 5
```

### Python API Usage
```python
from mineru import Mineru

# Initialize
converter = Mineru()

# Convert PDF
result = converter.convert(
    pdf_path="input.pdf",
    output_dir="output/",
    lang="en",
    format="markdown"
)

print(f"Converted: {result.pages} pages")
print(f"Output: {result.output_path}")
```

---

## Maintenance

### Update MinerU
```bash
# Update to latest version
make -C .tools/mineru update-deps

# Or manually
cd .tools/mineru
source venv/bin/activate
uv pip install -U "mineru[core]"
```

### Clean Up
```bash
# Clean temporary files
make -C .tools/mineru clean

# Remove everything (including venv)
make -C .tools/mineru clean-all
```

### Reinstall
```bash
# Complete reinstallation
make -C .tools/mineru clean-all
make -C .tools/mineru install
make -C .tools/mineru test
```

---

## Performance Benchmarks

### Apple Silicon M4 Expected Performance
- **Small PDF** (<10 pages): ~10-30 seconds
- **Medium PDF** (10-50 pages): ~30-120 seconds
- **Large PDF** (50-200 pages): ~2-8 minutes
- **Complex tables/formulas**: +20-50% processing time

### Optimization Tips
1. **Batch Processing**: More efficient for multiple files
2. **MPS Acceleration**: Automatically enabled on Apple Silicon
3. **Memory Management**: 32GB RAM recommended for large documents
4. **Disk I/O**: Use SSD for input/output for best performance

---

## Integration with Vault

### Recommended Workflow

#### For Tax Documents
```bash
# 1. Convert tax PDF
make -C .tools/mineru convert FILE=tax-docs-dropbox/01-Income/W2-Forms/2024_W2.pdf

# 2. Review extracted markdown
open tax-docs-dropbox/01-Income/W2-Forms/mineru_output/2024_W2.md

# 3. Extract needed data manually to vault notes
# (Don't copy full markdown - contains sensitive data)

# 4. Clean up when done
rm -rf tax-docs-dropbox/01-Income/W2-Forms/mineru_output/
```

#### For Research Papers
```bash
# 1. Convert research PDF
make -C .tools/mineru convert FILE=inbox/research-paper.pdf OUTPUT=resources/research/

# 2. Move markdown to appropriate vault location
mv resources/research/mineru_output/research-paper.md resources/research/papers/

# 3. Link from relevant notes
# [[resources/research/papers/research-paper]]
```

---

## Comparison: MinerU vs Docling

### MinerU Strengths
- ✅ Superior table extraction and structure preservation
- ✅ Mathematical formula recognition (LaTeX format)
- ✅ Better for structured documents (forms, statements, reports)
- ✅ Multilingual OCR (84 languages)
- ✅ JSON output option for data processing

### Docling Strengths
- ✅ Simpler, faster for general documents
- ✅ Built-in markdown cleaning
- ✅ Better for books and narrative content
- ✅ Lower memory footprint
- ✅ Fewer dependencies

### Use Case Matrix
| Document Type | Recommended Tool |
|--------------|------------------|
| Tax forms (W-2, 1099) | MinerU |
| Financial statements | MinerU |
| Technical papers with formulas | MinerU |
| Research papers with tables | MinerU |
| Books & articles | Docling |
| General PDFs | Docling |
| Quick conversions | Docling |

---

## Help & Support

### Get Help
```bash
# Show all available commands
make -C .tools/mineru help

# Test installation
make -C .tools/mineru test

# MinerU CLI help
cd .tools/mineru && source venv/bin/activate && mineru -h
```

### Common Commands Reference
```bash
# Installation
make -C .tools/mineru install

# Convert single file
make -C .tools/mineru convert FILE=input.pdf

# Batch convert
make -C .tools/mineru batch DIR=pdfs/

# Update
make -C .tools/mineru update-deps

# Clean
make -C .tools/mineru clean

# Test
make -C .tools/mineru test
```

---

## References

- **MinerU GitHub**: https://github.com/opendatalab/MinerU
- **Documentation**: https://opendatalab.github.io/MinerU/
- **PyPI Package**: https://pypi.org/project/mineru/
- **Related Vault Tools**:
  - [[.tools/docling/README|Docling PDF Converter]]
  - [[.tools/README|Tools Overview]]

---

*Last Updated: 2025-10-05 | MinerU 2.5 | Apple Silicon M4 Compatible*
