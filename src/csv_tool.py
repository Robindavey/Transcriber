import pandas as pd
import os

def csv_to_text(csv_path: str, txt_output_path: str = None) -> str:
    """
    Extracts text from a CSV file.

    Args:
        csv_path: Path to the input CSV
        txt_output_path: Optional path for output .txt file.
                         If None, will create next to CSV.

    Returns:
        The extracted text as a string.
    """
    if txt_output_path is None:
        txt_output_path = os.path.splitext(csv_path)[0] + ".txt"

    df = pd.read_csv(csv_path)
    extracted_text = df.to_string(index=False)

    with open(txt_output_path, "w", encoding="utf-8") as f:
        f.write(extracted_text)

    return extracted_text