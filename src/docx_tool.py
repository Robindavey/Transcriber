from docx import Document
import os

def docx_to_text(docx_path: str, txt_output_path: str = None) -> str:
    """
    Extracts text from a DOCX file.

    Args:
        docx_path: Path to the input DOCX
        txt_output_path: Optional path for output .txt file.
                         If None, will create next to DOCX.

    Returns:
        The extracted text as a string.
    """
    if txt_output_path is None:
        txt_output_path = os.path.splitext(docx_path)[0] + ".txt"

    doc = Document(docx_path)
    full_text = []

    for para in doc.paragraphs:
        full_text.append(para.text)

    extracted_text = "\n".join(full_text)

    with open(txt_output_path, "w", encoding="utf-8") as f:
        f.write(extracted_text)

    return extracted_text