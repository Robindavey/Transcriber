import fitz  # PyMuPDF
from pathlib import Path
from typing import Optional

def pdf_to_text(pdf_path: str, txt_output_path: Optional[str] = None) -> str:

    """
    Extracts text from a PDF with high accuracy and writes it to a .txt file.

    Args:
        pdf_path: Path to the input PDF
        txt_output_path: Optional path for output .txt file.
                         If None, will create next to PDF.

    Returns:
        The extracted text as a string.
    """

    pdf_path = Path(pdf_path)

    if txt_output_path is None:
        txt_output_path = pdf_path.with_suffix(".txt")

    doc = fitz.open(pdf_path)
    full_text = []

    for page in doc:
        # "text" preserves layout best for reading order
        text = page.get_text("text")
        full_text.append(text)

    extracted_text = "\n".join(full_text)

    with open(txt_output_path, "w", encoding="utf-8") as f:
        f.write(extracted_text)

    return extracted_text
if __name__ == "__main__":
    print(pdf_to_text("data/projects/NewProject/uploads/2023-2-internet.pdf", "data/projects/NewProject/raw/raw.txt"))
    