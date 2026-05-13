from io import BytesIO
from PyPDF2 import PdfReader
import re

def clean_text(text: str) -> str:
    text = re.sub(r'[^ -~\n]', '', text)   # remove weird chars
    text = re.sub(r'\n+', '\n', text)      # fix multiple new lines
    text = re.sub(r'[ ]{2,}', ' ', text)   # fix multiple spaces
    return text.strip()

def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(file_bytes))
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text.strip()        