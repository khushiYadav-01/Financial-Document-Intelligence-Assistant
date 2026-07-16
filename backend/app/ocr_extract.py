"""
Handles turning an uploaded file (image, PDF, or plain text) into raw text,
then parsing that text into structured invoice/expense fields using
regex-based heuristics.

This is intentionally rule-based rather than a heavy NLP model, so it is
fast, dependency-light, and easy to explain in an interview: "here is
exactly why this field was extracted."
"""
import re
import io
from datetime import datetime
from typing import Optional, Dict

from PIL import Image
import pytesseract

try:
    from pdf2image import convert_from_bytes
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False


def extract_text(file_bytes: bytes, filename: str) -> str:
    """Dispatch to the right extractor based on file extension."""
    lower = filename.lower()

    if lower.endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff")):
        image = Image.open(io.BytesIO(file_bytes))
        return pytesseract.image_to_string(image)

    if lower.endswith(".pdf"):
        if not PDF_SUPPORT:
            raise RuntimeError(
                "PDF support requires pdf2image + poppler-utils. "
                "Install poppler-utils on the host or upload an image/txt file instead."
            )
        pages = convert_from_bytes(file_bytes)
        text_chunks = [pytesseract.image_to_string(page) for page in pages]
        return "\n".join(text_chunks)

    if lower.endswith((".txt", ".csv")):
        return file_bytes.decode("utf-8", errors="ignore")

    raise ValueError(f"Unsupported file type: {filename}")


# --- Regex patterns for common invoice/expense fields -----------------

_AMOUNT_PATTERNS = [
    r"(?:total|amount due|grand total|amount payable|balance due)\s*[:\-]?\s*(?:INR|Rs\.?|₹|\$|USD)?\s*([\d,]+\.\d{2})",
    r"(?:INR|Rs\.?|₹|\$|USD)\s*([\d,]+\.\d{2})",
    r"([\d,]+\.\d{2})",
]

_INVOICE_NO_PATTERNS = [
    r"(?:invoice\s*(?:no|number|#)?)\s*[:\-]?\s*([A-Za-z0-9\-\/]+)",
    r"(?:bill\s*(?:no|number|#)?)\s*[:\-]?\s*([A-Za-z0-9\-\/]+)",
]

_DATE_PATTERNS = [
    r"(?:date|invoice date|dated)\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})",
    r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})",
    r"(\d{4}-\d{2}-\d{2})",
]

_VENDOR_PATTERNS = [
    r"(?:vendor|from|seller|bill from|billed by)\s*[:\-]?\s*(.+)",
]

CATEGORY_KEYWORDS = {
    "travel": ["flight", "airline", "taxi", "uber", "ola", "hotel", "cab"],
    "meals": ["restaurant", "cafe", "food", "dinner", "lunch"],
    "office_supplies": ["stationery", "office", "supplies", "printer", "paper"],
    "software": ["subscription", "saas", "license", "software"],
    "consulting": ["consulting", "professional fees", "advisory"],
}


def _first_match(patterns, text: str) -> Optional[str]:
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def _parse_amount(text: str) -> Optional[float]:
    raw = _first_match(_AMOUNT_PATTERNS, text)
    if not raw:
        return None
    try:
        return float(raw.replace(",", ""))
    except ValueError:
        return None


def _parse_date(text: str) -> Optional[str]:
    raw = _first_match(_DATE_PATTERNS, text)
    if not raw:
        return None
    # Try a few common formats and normalize to YYYY-MM-DD; if none match, keep raw.
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y", "%Y-%m-%d", "%d/%m/%y", "%d-%m-%y"):
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return raw


def _guess_category(text: str) -> str:
    lower = text.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            return category
    return "uncategorized"


def parse_fields(text: str) -> Dict:
    """Extract structured fields from raw OCR/text content."""
    return {
        "vendor": _first_match(_VENDOR_PATTERNS, text) or "Unknown Vendor",
        "invoice_number": _first_match(_INVOICE_NO_PATTERNS, text),
        "amount": _parse_amount(text),
        "invoice_date": _parse_date(text),
        "category": _guess_category(text),
    }
