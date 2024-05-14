import PyPDF2
from collections import Counter
import matplotlib.pyplot as plt

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

    # Plotting the character frequencies
    # Selecting the top characters if there are more than 26
    top_chars = char_counter.most_common(26)
    labels, values = zip(*top_chars)

    plt.figure(figsize=(10, 5))
    plt.bar(labels, values, color='b')
    plt.xlabel('Characters')
    plt.ylabel('Frequency')
    plt.title('Character Frequency in PDF')
    plt.show()

    # Print the top 10 words
    top_words = word_counter.most_common(10)
    print("\nTop 10 words:")
    for word, count in top_words:
        print(f"{word}: {count}")

# Example usage
file_path = r"ML_Scripts\DCVis_v41.pdf"  # Change this to your PDF file path
load_pdf_and_analyze(file_path)
