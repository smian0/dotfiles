"""
MinerU PDF Extraction Engine
Handles PDF-to-markdown conversion using MinerU with smart page filtering
"""
import os
import subprocess
import json
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from page_filter import PageFilter


class ExtractionEngine:
    """PDF extraction using MinerU"""

    # Common MinerU installation paths
    MINERU_PATHS = [
        str(Path(__file__).parent / "mineru" / "venv" / "bin" / "mineru"),  # Bundled with MCP server
        "mineru",  # System PATH
        "/usr/local/bin/mineru",
        "~/.local/bin/mineru"
    ]

    def __init__(self):
        self.mineru_path = self._detect_mineru()

    def _detect_mineru(self) -> Optional[str]:
        """Auto-detect MinerU installation"""
        # Check explicit paths first
        for path in self.MINERU_PATHS:
            expanded = Path(path).expanduser()
            if expanded.exists() and expanded.is_file():
                return str(expanded)

        # Check system PATH
        mineru_cmd = shutil.which("mineru")
        if mineru_cmd:
            return mineru_cmd

        return None

    def extract_pdf(
        self,
        pdf_path: str,
        output_dir: Optional[str] = None,
        mineru_path: Optional[str] = None,
        timeout: int = 600,
        use_smart_filtering: bool = True
    ) -> Dict[str, Any]:
        """
        Extract PDF to markdown using MinerU

        Args:
            pdf_path: Path to PDF file
            output_dir: Output directory (default: temp dir)
            mineru_path: Optional explicit path to mineru command
            timeout: Max execution time in seconds

        Returns:
            Dict with 'markdown' content and 'metadata'
        """
        # Validate PDF exists
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            return {
                "error": "PDF file not found",
                "path": pdf_path
            }

        # Determine MinerU executable
        mineru_cmd = mineru_path or self.mineru_path
        if not mineru_cmd:
            return {
                "error": "MinerU not found",
                "searched_paths": self.MINERU_PATHS,
                "help": "Install via: pip install magic-pdf[full] OR provide mineru_path"
            }

        # Setup output directory
        if output_dir:
            output_path = Path(output_dir)
        else:
            output_path = pdf_file.parent / f"{pdf_file.stem}_mineru_output"

        output_path.mkdir(parents=True, exist_ok=True)

        # Detect if PDF has extractable text (born-digital) vs needs OCR (scanned)
        needs_ocr = False
        use_pymupdf_fast = False
        try:
            import fitz
            doc = fitz.open(str(pdf_file))
            # Sample first page
            if len(doc) > 0:
                text = doc[0].get_text()
                needs_ocr = len(text.strip()) < 100  # Less than 100 chars = likely scanned

                # For born-digital PDFs, use PyMuPDF (100x faster than MinerU)
                # MinerU incorrectly classifies tax forms as needing OCR due to tables
                if not needs_ocr:
                    use_pymupdf_fast = True
                    print(f"PDF analysis: Born-digital - using PyMuPDF (100x faster)")
                else:
                    print(f"PDF analysis: Scanned - using MinerU OCR")
            doc.close()
        except Exception as e:
            print(f"Could not detect PDF type, defaulting to MinerU: {e}")
            needs_ocr = True
            use_pymupdf_fast = False

        # Smart page filtering and batch processing for large documents
        page_ranges = None
        page_stats = None
        if use_smart_filtering:
            try:
                page_filter = PageFilter()
                page_stats = page_filter.get_page_stats(str(pdf_file))
                page_ranges = page_stats['page_ranges']

                # Use batch processing if: (1) skips pages OR (2) many pages to process
                if page_stats['pages_skipped'] > 5 or page_stats['filled_pages_count'] > 15:
                    print(f"Batch processing: {page_stats['filled_pages_count']} pages in {len(page_ranges)} batches ({page_stats['estimated_speedup']} speedup from filtering)")
                else:
                    # Small document, don't use batch processing
                    page_ranges = None
            except Exception as e:
                print(f"Page filtering failed, processing all pages: {e}")
                page_ranges = None

        # Fast path for born-digital PDFs: Use PyMuPDF (100x faster than MinerU)
        if use_pymupdf_fast:
            try:
                import fitz
                doc = fitz.open(str(pdf_file))
                total_pages = len(doc)  # Store before closing
                markdown_parts = []

                # Extract text from each page with basic markdown formatting
                for page_num in range(total_pages):
                    page = doc[page_num]
                    text = page.get_text()

                    # Add page header
                    markdown_parts.append(f"\n\n## Page {page_num + 1}\n\n")
                    markdown_parts.append(text)

                doc.close()

                markdown_content = "".join(markdown_parts)

                return {
                    "markdown": markdown_content,
                    "metadata": {
                        "method": "pymupdf_fast",
                        "pages": total_pages,
                        "source": str(pdf_file)
                    }
                }
            except Exception as e:
                print(f"PyMuPDF fast extraction failed, falling back to MinerU: {e}")
                # Fall through to MinerU

        # Run MinerU extraction with CPU mode (for scanned PDFs or if PyMuPDF fails)
        try:
            # Set environment to force CPU and disable MPS
            env = os.environ.copy()
            env['PYTORCH_MPS_ENABLED'] = '0'  # Disable MPS entirely
            env['MINERU_DEVICE_MODE'] = 'cpu'  # Force CPU mode
            env['PYTORCH_ENABLE_MPS_FALLBACK'] = '0'  # Prevent MPS fallback
            env['MAGIC_PDF_CONFIG_PATH'] = '/Users/smian/magic-pdf.json'  # Point to CPU config

            # Build MinerU command with appropriate mode
            mineru_mode = "auto"  # Let MinerU decide, or force txt/ocr
            if not needs_ocr:
                mineru_mode = "txt"  # Fast text extraction for born-digital PDFs

            # Process pages in ranges if smart filtering enabled
            if page_ranges and len(page_ranges) > 0:
                all_markdown = []
                for start_page, end_page in page_ranges:
                    result = subprocess.run(
                        [
                            mineru_cmd,
                            "-p", str(pdf_file),
                            "-o", str(output_path / f"range_{start_page}_{end_page}"),
                            "-s", str(start_page),
                            "-e", str(end_page),
                            "-m", mineru_mode,  # Use detected mode (txt for born-digital, auto for scanned)
                        ],
                        capture_output=True,
                        text=True,
                        timeout=timeout,
                        env=env
                    )

                    if result.returncode != 0:
                        return {
                            "error": f"MinerU extraction failed for pages {start_page}-{end_page}",
                            "returncode": result.returncode,
                            "stderr": result.stderr[:500],
                            "stdout": result.stdout[:500]
                        }

                # Note: Combined markdown collection handled below
            else:
                # Process all pages (no filtering)
                result = subprocess.run(
                    [
                        mineru_cmd,
                        "-p", str(pdf_file),
                        "-o", str(output_path),
                        "-m", mineru_mode,  # Use detected mode (txt for born-digital, auto for scanned)
                    ],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    env=env  # Pass modified environment
                )

            if result.returncode != 0:
                return {
                    "error": "MinerU extraction failed",
                    "returncode": result.returncode,
                    "stderr": result.stderr[:500],  # Truncate error
                    "stdout": result.stdout[:500]
                }

            # Find and combine markdown from filtered pages or single output
            if page_ranges and len(page_ranges) > 0:
                # Combine markdown from multiple page range outputs
                all_markdown = []
                for start_page, end_page in page_ranges:
                    range_output = output_path / f"range_{start_page}_{end_page}"
                    md_files = list(range_output.rglob("*.md"))
                    if md_files:
                        content = md_files[0].read_text(encoding='utf-8')
                        all_markdown.append(f"\n\n<!-- Pages {start_page}-{end_page} -->\n\n{content}")

                if not all_markdown:
                    return {
                        "error": "No markdown files generated from filtered pages",
                        "output_dir": str(output_path),
                        "page_ranges": page_ranges
                    }

                markdown_content = "\n".join(all_markdown)
            else:
                # Standard single-file processing
                # MinerU creates: output_dir/{pdf_stem}/auto/{pdf_stem}.md
                expected_md = output_path / pdf_file.stem / "auto" / f"{pdf_file.stem}.md"

                if not expected_md.exists():
                    # Fallback: search for any .md file
                    md_files = list(output_path.rglob("*.md"))
                    if md_files:
                        expected_md = md_files[0]
                    else:
                        return {
                            "error": "No markdown file generated",
                            "output_dir": str(output_path),
                            "expected": str(expected_md)
                        }

                # Read extracted markdown
                markdown_content = expected_md.read_text(encoding='utf-8')

            # Cleanup MinerU intermediate files
            cleanup_success = self._cleanup_mineru_output(output_path)

            return {
                "markdown": markdown_content,
                "metadata": {
                    "source_pdf": str(pdf_file),
                    "output_file": str(expected_md),
                    "output_dir": str(output_path),
                    "file_size_bytes": pdf_file.stat().st_size,
                    "markdown_length": len(markdown_content),
                    "mineru_version": self._get_mineru_version(mineru_cmd),
                    "intermediate_files_cleaned": cleanup_success
                }
            }

        except subprocess.TimeoutExpired:
            return {
                "error": "MinerU extraction timeout",
                "timeout_seconds": timeout,
                "help": "Try increasing timeout parameter or use smaller PDF"
            }
        except Exception as e:
            return {
                "error": "Extraction failed",
                "exception": str(e),
                "exception_type": type(e).__name__
            }

    def _cleanup_mineru_output(self, output_dir: Path) -> bool:
        """
        Clean up MinerU intermediate files, keeping only the extracted markdown.

        Args:
            output_dir: Path to MinerU output directory

        Returns:
            True if cleanup succeeded, False otherwise
        """
        try:
            import shutil

            # Only delete if this looks like a MinerU output directory
            if output_dir.exists() and "_mineru_output" in output_dir.name:
                shutil.rmtree(output_dir)
                return True
            return False
        except Exception as e:
            # Don't fail the extraction if cleanup fails
            return False

    def _get_mineru_version(self, mineru_cmd: str) -> str:
        """Get MinerU version string"""
        try:
            result = subprocess.run(
                [mineru_cmd, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return "unknown"
        except:
            return "unknown"
