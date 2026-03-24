import PyPDF2

def extract_and_save(pdf_path):
    """
    Extract text from a PDF file and save it to a .txt file.
    """
    try:
        # Extract text from PDF
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        
        # Save to .txt file (e.g., 'doc_1.pdf' -> 'doc_1_extracted.txt')
        txt_path = pdf_path.replace('.pdf', '_extracted.txt')
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Text extracted and saved to {txt_path}")
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}") 