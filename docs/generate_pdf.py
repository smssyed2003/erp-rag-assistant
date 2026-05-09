from pathlib import Path
import re

try:
    from markdown import markdown
    from fpdf import FPDF
except ImportError as exc:
    raise SystemExit(
        "Missing PDF generation packages. Install with: pip install -r docs/requirements.txt"
    )

SOURCE_MD = Path(__file__).parent / "ERP_AI_Assistant_Documentation.md"
OUTPUT_PDF = Path(__file__).parent / "ERP_AI_Assistant_Documentation.pdf"

if not SOURCE_MD.exists():
    raise FileNotFoundError(f"Documentation file not found: {SOURCE_MD}")

markdown_text = SOURCE_MD.read_text(encoding="utf-8")
html_text = markdown(markdown_text)
plain_text = re.sub(r"<[^>]+>", "", html_text)
plain_text = plain_text.replace("&nbsp;", " ")
plain_text = plain_text.replace("&amp;", "&")

pdf = FPDF()
pdf.set_auto_page_break(True, margin=15)
pdf.add_page()
pdf.set_font("Arial", size=11)

for line in plain_text.splitlines():
    if not line.strip():
        pdf.ln(4)
        continue
    pdf.multi_cell(0, 7, line)

pdf.output(str(OUTPUT_PDF))
print(f"Generated PDF: {OUTPUT_PDF}")
