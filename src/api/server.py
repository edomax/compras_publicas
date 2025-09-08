#!/usr/bin/env python3
"""
Servidor Flask para la interfaz web de Ollama con RAG
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
import sys
sys.path.append('/Users/edomax/Documents/GitHub/compras_publicas')
from src.core.ollama_client import OllamaClient
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Permitir CORS para requests desde el navegador

# Inicializar cliente Ollama
ollama_client = OllamaClient()

@app.route('/')
def index():
    """Servir la página HTML"""
    try:
        with open('web/templates/index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return """
        <h1>Error</h1>
        <p>No se encontró el archivo web/templates/index.html</p>
        <p>Asegúrate de que esté en el mismo directorio que este servidor.</p>
        """

@app.route('/status')
def status():
    """Verificar estado del sistema"""
    try:
        # Verificar conexión a Ollama
        ollama_connected = ollama_client.test_connection()
        
        # Verificar documentos cargados
        documents_loaded = len(ollama_client.documents) > 0
        document_count = len(ollama_client.documents)
        
        return jsonify({
            'ollama_connected': ollama_connected,
            'documents_loaded': documents_loaded,
            'document_count': document_count,
            'status': 'ready' if ollama_connected and documents_loaded else 'not_ready'
        })
    except Exception as e:
        logger.error(f"Error checking status: {e}")
        return jsonify({
            'ollama_connected': False,
            'documents_loaded': False,
            'document_count': 0,
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/query', methods=['POST'])
def query():
    """Procesar pregunta del usuario"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        # Verificar que el sistema esté listo
        if not ollama_client.test_connection():
            return jsonify({'error': 'Ollama not connected'}), 503
        
        if len(ollama_client.documents) == 0:
            return jsonify({'error': 'No documents loaded'}), 503
        
        logger.info(f"Processing question: {question}")
        
        # Buscar documentos relevantes
        relevant_docs = ollama_client.search_documents(question, top_k=3)
        
        # Generar respuesta con contexto
        response = ollama_client.query_with_context(question)
        
        # Preparar información de fuentes
        sources = []
        for doc in relevant_docs:
            sources.append({
                'source': doc['source'],
                'similarity': doc['similarity']
            })
        
        return jsonify({
            'response': response,
            'sources': sources,
            'question': question
        })
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return jsonify({'error': f'Error processing query: {str(e)}'}), 500

@app.route('/reload_documents')
def reload_documents():
    """Recargar documentos"""
    try:
        ollama_client.load_documents()
        return jsonify({
            'success': True,
            'message': f'Loaded {len(ollama_client.documents)} documents',
            'document_count': len(ollama_client.documents)
        })
    except Exception as e:
        logger.error(f"Error reloading documents: {e}")
        return jsonify({'error': f'Error reloading documents: {str(e)}'}), 500

@app.route('/documents')
def list_documents():
    """Listar documentos cargados"""
    try:
        documents = []
        for doc in ollama_client.documents:
            documents.append({
                'filename': doc['filename'],
                'path': doc['path'],
                'size': len(doc['content'])
            })
        
        return jsonify({
            'documents': documents,
            'count': len(documents)
        })
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        return jsonify({'error': f'Error listing documents: {str(e)}'}), 500

def initialize_system():
    """Inicializar el sistema al arrancar"""
    try:
        logger.info("Initializing Ollama RAG system...")
        
        # Verificar conexión a Ollama
        if not ollama_client.test_connection():
            logger.warning("Ollama not connected. Make sure it's running with: brew services start ollama")
        else:
            logger.info("✅ Ollama connected successfully")
        
        # Cargar documentos
        ollama_client.load_documents()
        logger.info(f"✅ Loaded {len(ollama_client.documents)} documents")
        
        return True
    except Exception as e:
        logger.error(f"Error initializing system: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Iniciando servidor Ollama RAG...")
    print("📚 Sistema de consultas de Compras Públicas Chile")
    print("=" * 50)
    
    # Inicializar sistema
    if initialize_system():
        print("✅ Sistema inicializado correctamente")
    else:
        print("⚠️  Sistema iniciado con errores")
    
    print("\n🌐 Servidor disponible en:")
    print("   http://localhost:5001")
    print("\n📖 Para usar el sistema:")
    print("   1. Asegúrate de que Ollama esté ejecutándose")
    print("   2. Abre http://localhost:5001 en tu navegador")
    print("   3. Haz preguntas sobre compras públicas")
    print("\n⚡ Para detener el servidor: Ctrl+C")
    print("=" * 50)
    
    # Instalar dependencias si no están disponibles
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
    except ImportError:
        print("\n⚠️  Instalando dependencias faltantes...")
        os.system("pip install scikit-learn numpy")
    
    app.run(host='0.0.0.0', port=5001, debug=True)