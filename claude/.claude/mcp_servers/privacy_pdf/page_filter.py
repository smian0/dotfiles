"""
Smart page filtering for tax forms using PyMuPDF
Detects filled pages vs blank templates to optimize MinerU processing
"""

import fitz  # PyMuPDF
from typing import List, Tuple
from pathlib import Path


class PageFilter:
    """Detect filled/meaningful pages in PDFs before expensive OCR processing"""

    def __init__(self, min_text_length: int = 100, min_widgets_filled: int = 1):
        """
        Args:
            min_text_length: Minimum text characters to consider page "filled"
            min_widgets_filled: Minimum filled form widgets to consider page "filled"
        """
        self.min_text_length = min_text_length
        self.min_widgets_filled = min_widgets_filled

    def identify_filled_pages(self, pdf_path: str) -> List[int]:
        """
        Identify pages with actual filled data (skip instructions/blank pages)

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of 0-based page indices that have filled content
        """
        doc = fitz.open(pdf_path)
        filled_pages = []

        for page_num in range(len(doc)):
            page = doc[page_num]

            # Check 1: Form fields with values
            filled_widgets = 0
            for widget in page.widgets():
                if widget.field_value:  # Has value = filled
                    filled_widgets += 1

            # Check 2: Text content length
            text_content = page.get_text()
            text_length = len(text_content.strip())

            # Check 3: Page is not completely blank
            has_content = page.get_contents() != []

            # Decision: Page is "filled" if it has widgets, substantive text, or any content
            is_filled = (
                filled_widgets >= self.min_widgets_filled or
                text_length >= self.min_text_length or
                (has_content and text_length > 50)  # Some content but not just headers
            )

            if is_filled:
                filled_pages.append(page_num)

        doc.close()
        return filled_pages

    def identify_k1_data_pages(self, pdf_path: str) -> List[int]:
        """
        Smart detection for Schedule K-1 forms - identifies ONLY pages with actual tax data.

        Filters out:
        - Cover letters
        - Instructions
        - Supplemental schedules without key data
        - Blank pages

        Keeps:
        - Main K-1 form (has SSN + tax line items)
        - Critical supplemental pages (high density of numeric data)

        Args:
            pdf_path: Path to K-1 PDF file

        Returns:
            List of 0-based page indices with actual K-1 tax data
        """
        import re

        doc = fitz.open(pdf_path)
        data_pages = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()

            # K-1 form indicators
            has_k1_form = bool(re.search(r'Schedule K-1.*Form 1065', text, re.IGNORECASE))
            has_ssn_pattern = bool(re.search(r'\d{3}-\d{2}-\d{4}', text))
            has_ein_pattern = bool(re.search(r'\d{2}-\d{7}', text))

            # Partner/Partnership identification
            has_partner_name = bool(re.search(r'(SHOAIB|YASMENE)\s+.*?MIAN', text, re.IGNORECASE))
            has_partnership_name = bool(re.search(r'LLC|LP|INVESTOR|FUND|PARTNER', text))

            # Count unique numbers (tax data indicator)
            numbers = re.findall(r'\b\d{1,3}(?:,\d{3})*\b', text)
            unique_numbers = len(set(numbers))

            # Detect key K-1 line items
            has_line_items = bool(re.search(r'(Ordinary business income|Net rental real estate|Distributions)', text, re.IGNORECASE))

            # Exclude instruction/cover pages
            is_cover_letter = bool(re.search(r'DEAR (MEMBER|PARTNER)|RE:|Sincerely', text, re.IGNORECASE))
            is_instructions = bool(re.search(r'INSTRUCTIONS|For more information|See the Partner', text, re.IGNORECASE))

            # Decision logic: This is a DATA page if:
            # 1. Has K-1 form structure AND has SSN/EIN AND high data density
            # 2. OR has partner name AND partnership AND many unique numbers
            # 3. AND NOT a cover letter or instructions page

            is_main_k1 = (
                has_k1_form and
                has_ssn_pattern and
                unique_numbers > 20 and
                not is_cover_letter
            )

            is_critical_supplement = (
                has_partnership_name and
                has_partner_name and
                unique_numbers > 15 and
                has_line_items and
                not is_instructions
            )

            if is_main_k1 or is_critical_supplement:
                data_pages.append(page_num)

        doc.close()

        # If no pages detected (edge case), fall back to basic detection
        if not data_pages:
            return self.identify_filled_pages(pdf_path)

        return data_pages

    def group_consecutive_pages(self, page_list: List[int], max_batch_size: int = 10) -> List[Tuple[int, int]]:
        """
        Group consecutive pages into ranges with maximum batch size limit

        Args:
            page_list: List of page numbers (0-based)
            max_batch_size: Maximum pages per batch (to avoid timeouts)

        Returns:
            List of (start, end) tuples representing page ranges

        Example:
            [0, 1, 2, 5, 6, 9] -> [(0, 2), (5, 6), (9, 9)]
            [0-20], max_batch=10 -> [(0, 9), (10, 19), (20, 20)]
        """
        if not page_list:
            return []

        ranges = []
        start = page_list[0]
        prev = page_list[0]
        batch_count = 1

        for page in page_list[1:]:
            if page == prev + 1 and batch_count < max_batch_size:
                # Consecutive and within batch limit
                prev = page
                batch_count += 1
            else:
                # Gap found OR batch size limit reached
                ranges.append((start, prev))
                start = page
                prev = page
                batch_count = 1

        # Close final range
        ranges.append((start, prev))
        return ranges

    def get_optimized_page_ranges(self, pdf_path: str) -> List[Tuple[int, int]]:
        """
        Get optimized page ranges for processing (filled pages only)

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of (start, end) page range tuples to process
        """
        filled_pages = self.identify_filled_pages(pdf_path)
        return self.group_consecutive_pages(filled_pages)

    def get_page_stats(self, pdf_path: str) -> dict:
        """
        Get statistics about page filtering for a PDF

        Returns:
            Dict with total_pages, filled_pages, ranges, estimated_speedup
        """
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        doc.close()

        filled_pages = self.identify_filled_pages(pdf_path)
        ranges = self.group_consecutive_pages(filled_pages)

        estimated_speedup = total_pages / max(len(filled_pages), 1)

        return {
            "total_pages": total_pages,
            "filled_pages_count": len(filled_pages),
            "filled_pages": filled_pages,
            "page_ranges": ranges,
            "estimated_speedup": f"{estimated_speedup:.1f}x",
            "pages_to_process": len(filled_pages),
            "pages_skipped": total_pages - len(filled_pages)
        }


# Example usage
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python page_filter.py <pdf_path>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    filter = PageFilter()

    print("Page Filtering Analysis")
    print("=" * 50)

    stats = filter.get_page_stats(pdf_path)
    print(f"Total pages: {stats['total_pages']}")
    print(f"Filled pages: {stats['filled_pages_count']}")
    print(f"Pages skipped: {stats['pages_skipped']}")
    print(f"Estimated speedup: {stats['estimated_speedup']}")
    print(f"\nFilled page numbers (0-based): {stats['filled_pages']}")
    print(f"Page ranges to process: {stats['page_ranges']}")
