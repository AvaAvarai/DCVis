import PyPDF2
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.ft2font import FT2Font
import re

# Extract text from the PDF
def extract_text_from_pdf(file_path):
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)
        
        # Extract text from each page and concatenate it
        text = ""
        for page_num in range(num_pages):
            text += reader.pages[page_num].extract_text()
    return text

# Find unique characters in the text
def find_unique_characters(text):
    # Remove common punctuations and whitespace
    text = re.sub(r'[\s]', '', text)  # Remove all whitespace
    # Count characters
    char_counter = Counter(text)
    return char_counter

# List missing glyphs
def list_missing_glyphs(unique_chars, font_paths):
    missing_glyphs = []
    for char in unique_chars:
        glyph_found = False
        for font_path in font_paths:
            font = FT2Font(font_path)
            if font.get_char_index(ord(char)):
                glyph_found = True
                break
        if not glyph_found:
            missing_glyphs.append(char)
    return missing_glyphs

# Paths to the files
pdf_path = r"Related_Papers\DCVis_v41.pdf"
font_paths = [
    r"fonts\NotoSans-Regular.ttf",  # Path to Noto Sans font
    r"fonts\NotoSansOriya-Regular.ttf",  # Path to Noto Sans Oriya font
    r"fonts\NotoSansSymbols-Regular.ttf",  # Path to Noto Sans Symbols font
    r"fonts\NotoSansCJK-Regular.ttc",  # Path to Noto Sans CJK font
    r"fonts\NotoSansMath-Regular.ttf"  # Path to Noto Sans Math font
]

# Extract text from PDF
text = extract_text_from_pdf(pdf_path)
# Get unique characters
unique_chars = find_unique_characters(text)
print("Unique Characters:", unique_chars)

# List missing glyphs
missing_glyphs = list_missing_glyphs(unique_chars, font_paths)
print("Missing Glyphs:", missing_glyphs)
