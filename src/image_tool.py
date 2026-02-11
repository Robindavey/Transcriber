import pytesseract
from PIL import Image
import os

def image_to_text(image_path: str, txt_output_path: str = None) -> str:
    """
    Extracts text from an image using OCR.

    Args:
        image_path: Path to the input image
        txt_output_path: Optional path for output .txt file.
                         If None, will create next to image.

    Returns:
        The extracted text as a string.
    """
    if txt_output_path is None:
        txt_output_path = os.path.splitext(image_path)[0] + ".txt"

    # Open image
    image = Image.open(image_path)

    # Extract text
    extracted_text = pytesseract.image_to_string(image)

    # Save to file
    with open(txt_output_path, "w", encoding="utf-8") as f:
        f.write(extracted_text)

    return extracted_text
if __name__ == "__main__":
    print(image_to_text("/home/robin/Pictures/Screenshots/test.png", "dummy.txt"))