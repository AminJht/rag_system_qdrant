import fitz  
from text_chunkung import chunk_file_to_txt

def pdf_reader(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""

    for page in doc:
        text = page.get_text()
        full_text += text + "\n"
    doc.close()
    print("Text extracted from PDF and sent for chunking.")
    chunk_file_to_txt(pdf_path,full_text)
    
if __name__=="__main__":
    pass