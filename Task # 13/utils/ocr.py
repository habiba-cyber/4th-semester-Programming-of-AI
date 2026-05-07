import pytesseract
from PIL import Image
import pdfplumber


pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# IMAGE OCR
def extract_text_from_image(image):
    return pytesseract.image_to_string(image)

# PDF TEXT EXTRACTION
def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text