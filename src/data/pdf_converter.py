#!/usr/bin/env python3
"""
Script para convertir archivos PDF a TXT
"""

import os
import sys
from pathlib import Path
import PyPDF2
import pdfplumber

def convert_pdf_to_txt_pypdf2(pdf_path, txt_path):
    """Convierte PDF a TXT usando PyPDF2"""
    try:
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
            
            with open(txt_path, 'w', encoding='utf-8') as txt_file:
                txt_file.write(text)
                
        print(f"✓ Convertido: {pdf_path} -> {txt_path}")
        return True
    except Exception as e:
        print(f"✗ Error con PyPDF2: {e}")
        return False

def convert_pdf_to_txt_pdfplumber(pdf_path, txt_path):
    """Convierte PDF a TXT usando pdfplumber (mejor para tablas)"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            with open(txt_path, 'w', encoding='utf-8') as txt_file:
                txt_file.write(text)
                
        print(f"✓ Convertido: {pdf_path} -> {txt_path}")
        return True
    except Exception as e:
        print(f"✗ Error con pdfplumber: {e}")
        return False

def convert_pdfs_in_directory(directory="."):
    """Convierte todos los PDFs en el directorio a TXT"""
    pdf_files = list(Path(directory).glob("*.pdf"))
    
    if not pdf_files:
        print("No se encontraron archivos PDF en el directorio.")
        return
    
    print(f"Encontrados {len(pdf_files)} archivos PDF:")
    for pdf_file in pdf_files:
        print(f"  - {pdf_file.name}")
    
    for pdf_file in pdf_files:
        txt_file = pdf_file.with_suffix('.txt')
        
        print(f"\nConvirtiendo: {pdf_file.name}")
        
        # Intentar primero con pdfplumber
        if convert_pdf_to_txt_pdfplumber(pdf_file, txt_file):
            continue
            
        # Si falla, intentar con PyPDF2
        print("Intentando con PyPDF2...")
        convert_pdf_to_txt_pypdf2(pdf_file, txt_file)

def main():
    if len(sys.argv) > 1:
        # Convertir archivo específico
        pdf_path = sys.argv[1]
        if not os.path.exists(pdf_path):
            print(f"Error: El archivo {pdf_path} no existe.")
            return
        
        txt_path = Path(pdf_path).with_suffix('.txt')
        
        print(f"Convirtiendo: {pdf_path}")
        if not convert_pdf_to_txt_pdfplumber(pdf_path, txt_path):
            print("Intentando con PyPDF2...")
            convert_pdf_to_txt_pypdf2(pdf_path, txt_path)
    else:
        # Convertir todos los PDFs del directorio actual
        convert_pdfs_in_directory()

if __name__ == "__main__":
    main()