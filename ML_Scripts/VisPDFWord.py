import PyPDF2
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

def load_pdf_and_analyze(file_path):
    # Open the PDF file
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)
        
        # Extract text from each page and concatenate it
        text = ""
        for page_num in range(num_pages):
            text += reader.pages[page_num].extract_text()

    # Count characters, ignoring spaces and converting to lowercase
    char_counter = Counter([char.lower() for char in text if char.isalpha()])
    
    # Count words
    word_counter = Counter(text.lower().split())

    # Sort the character counts alphabetically
    sorted_chars = sorted(char_counter.items())
    labels, values = zip(*sorted_chars)

    # Set font properties to Noto Sans, Noto Sans Oriya, Noto Sans Symbols, and Noto Sans CJK
    font_paths = [
        r"fonts\NotoSans-Regular.ttf",  # Path to Noto Sans font
        r"fonts\NotoSansOriya-Regular.ttf",  # Path to Noto Sans Oriya font
        r"fonts\NotoSansSymbols-Regular.ttf",  # Path to Noto Sans Symbols font
        r"fonts\NotoSansCJK-Regular.ttc",  # Path to Noto Sans CJK font
        r"fonts\NotoSansMath-Regular.ttf"  # Path to Noto Sans Math font
    ]

    # Create a font property object that includes all specified fonts
    prop = fm.FontProperties(fname=font_paths[0])
    for font_path in font_paths[1:]:
        prop.set_file(font_path)

    plt.figure(figsize=(10, 5))
    plt.bar(labels, values, color='b')
    plt.xlabel('Characters', fontproperties=prop)
    plt.ylabel('Frequency', fontproperties=prop)
    plt.title('Character Frequency in PDF (Alphabetically Ordered)', fontproperties=prop)
    plt.show()

    # Print the top 10 words
    top_words = word_counter.most_common(10)
    print("\nTop 10 words:")
    for word, count in top_words:
        print(f"{word}: {count}")

# Load the PDF file and analyze it
file_path = r"Related_Papers/DCVis_v41.pdf"
load_pdf_and_analyze(file_path)
