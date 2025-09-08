#!/usr/bin/env python3
"""
Cliente para usar Ollama localmente con sistema RAG
"""

import requests
import json
import os
import re
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model = "compras-publicas-chile"
        self.documents = []
        self.document_chunks = []
        self.vectorizer = None
        self.document_vectors = None
        
    def test_connection(self) -> bool:
        """Test connection to Ollama server"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except:
            return False
    
    def generate(self, prompt: str, stream: bool = False) -> str:
        """Generate response using Ollama"""
        url = f"{self.base_url}/api/generate"
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream
        }
        
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                return f"Error: {response.status_code}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def load_documents(self, directory: str = "data/processed/txt") -> None:
        """Load all TXT files from directory"""
        txt_files = list(Path(directory).glob("*.txt"))
        print(f"Cargando {len(txt_files)} archivos TXT...")
        
        self.documents = []
        for txt_file in txt_files:
            try:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.documents.append({
                        'filename': txt_file.name,
                        'content': content,
                        'path': str(txt_file)
                    })
                print(f"✓ Cargado: {txt_file.name}")
            except Exception as e:
                print(f"✗ Error cargando {txt_file.name}: {e}")
        
        # Crear chunks de documentos
        self._create_document_chunks()
        # Vectorizar documentos
        self._vectorize_documents()
    
    def _create_document_chunks(self, chunk_size: int = 1000) -> None:
        """Create chunks from documents for better search"""
        self.document_chunks = []
        
        for doc in self.documents:
            content = doc['content']
            # Split by paragraphs first, then by sentences
            paragraphs = content.split('\n\n')
            
            current_chunk = ""
            for paragraph in paragraphs:
                if len(current_chunk) + len(paragraph) < chunk_size:
                    current_chunk += paragraph + "\n\n"
                else:
                    if current_chunk.strip():
                        self.document_chunks.append({
                            'text': current_chunk.strip(),
                            'source': doc['filename'],
                            'path': doc['path']
                        })
                    current_chunk = paragraph + "\n\n"
            
            # Add final chunk
            if current_chunk.strip():
                self.document_chunks.append({
                    'text': current_chunk.strip(),
                    'source': doc['filename'],
                    'path': doc['path']
                })
        
        print(f"✓ Creados {len(self.document_chunks)} chunks de documentos")
    
    def _vectorize_documents(self) -> None:
        """Create TF-IDF vectors for document search"""
        if not self.document_chunks:
            return
        
        texts = [chunk['text'] for chunk in self.document_chunks]
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words=None,  # Keep Spanish stopwords for now
            ngram_range=(1, 2)
        )
        
        self.document_vectors = self.vectorizer.fit_transform(texts)
        print(f"✓ Vectorizados {len(texts)} chunks de documentos")
    
    def search_documents(self, query: str, top_k: int = 3) -> List[Dict]:
        """Search for relevant document chunks"""
        if not self.vectorizer or self.document_vectors is None:
            return []
        
        # Vectorize query
        query_vector = self.vectorizer.transform([query])
        
        # Calculate similarities
        similarities = cosine_similarity(query_vector, self.document_vectors)[0]
        
        # Get top k results
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.1:  # Minimum similarity threshold
                chunk = self.document_chunks[idx].copy()
                chunk['similarity'] = similarities[idx]
                results.append(chunk)
        
        return results
    
    def query_with_context(self, query: str) -> str:
        """Query with document context (RAG)"""
        # Search for relevant documents
        relevant_docs = self.search_documents(query, top_k=3)
        
        if not relevant_docs:
            # If no relevant docs, use general prompt
            prompt = f"""Pregunta: {query}

Responde de manera útil y precisa."""
        else:
            # Build context from relevant documents
            context = "\n\n".join([
                f"Documento: {doc['source']}\n{doc['text'][:800]}..."
                for doc in relevant_docs
            ])
            
            prompt = f"""Basándote en los siguientes documentos sobre compras públicas en Chile, responde la pregunta:

CONTEXTO:
{context}

PREGUNTA: {query}

RESPUESTA (basada en los documentos proporcionados):"""
        
        return self.generate(prompt)
    
    def list_documents(self) -> List[str]:
        """List loaded documents"""
        return [doc['filename'] for doc in self.documents]

def main():
    # Test basic functionality
    client = OllamaClient()
    
    if not client.test_connection():
        print("❌ No se puede conectar a Ollama. Asegúrate de que esté ejecutándose:")
        print("   brew services start ollama")
        return
    
    print("✅ Conectado a Ollama")
    
    # Load documents
    client.load_documents()
    
    if client.documents:
        print(f"\n📚 Documentos cargados: {len(client.documents)}")
        for filename in client.list_documents():
            print(f"  - {filename}")
    
    # Interactive mode
    print("\n🤖 Chat con documentos de compras públicas (escribe 'salir' para terminar)")
    print("Ejemplos de preguntas:")
    print("- ¿Qué es una licitación pública?")
    print("- ¿Cuáles son los procedimientos de compra?")
    print("- ¿Qué documentos se requieren para licitar?")
    
    while True:
        query = input("\n💬 Tu pregunta: ").strip()
        
        if query.lower() in ['salir', 'exit', 'quit']:
            break
        
        if not query:
            continue
        
        print("\n🤔 Pensando...")
        response = client.query_with_context(query)
        print(f"\n🤖 Respuesta:\n{response}")

if __name__ == "__main__":
    main()