import os
import tempfile
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PDFPlumberLoader

def extract_main_headings(pdf_path):
    """Extract main headings from a PDF document."""
    toc = []
    with open(pdf_path, 'rb') as file:
        reader = PdfReader(file)
        if not reader.outline:
            return []
        for item in reader.outline:
            if isinstance(item, list):
                continue  # Skip subheadings
            else:
                if '.' not in item.title:  # Filter main headings
                    toc.append((item.title, reader.get_destination_page_number(item)))
    return toc

def extract_topic_text(pdf_path, start_page, end_page):
    """Extract text from a range of pages in a PDF."""
    reader = PdfReader(pdf_path)
    text = ""
    for page_num in range(start_page - 1, end_page):  # Page numbers are 0-based
        if page_num < len(reader.pages):
            text += reader.pages[page_num].extract_text()
    return text

def process_document_for_vector_store(pdf_path):
    """Process a PDF document for the vector store."""
    # Load the document
    loader = PDFPlumberLoader(pdf_path)
    documents = loader.load()
    
    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=150
    )
    splits = text_splitter.split_documents(documents)
    
    return splits