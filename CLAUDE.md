# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a specialized RAG (Retrieval-Augmented Generation) system for Chilean public procurement law consultation. The system combines document search with a fine-tuned Ollama model (`compras-publicas-chile`) trained specifically on Chilean legislation including Ley 19.886 and related regulations.

## Architecture

### Core Components

**Ollama Integration Layer:**
- `src/core/ollama_client.py`: Main client handling Ollama API communication, TF-IDF vectorization, and RAG functionality
- `src/api/server.py`: Flask web server providing REST API endpoints for the web interface
- `ollama_interface.html`: Web UI for document queries with real-time status indicators

**Model Training Pipeline:**
- `prepare_training_data.py`: Extracts Q&A pairs from legal documents using regex patterns
- `create_specialized_model.py`: Creates custom Ollama model using training data and specialized prompts
- `Modelfile`: Ollama configuration defining the specialized model behavior and parameters

**Document Processing:**
- `pdf_to_txt.py`: Converts legal PDFs to text using PyPDF2 and pdfplumber
- Legal documents: Contains official Chilean procurement law texts in both PDF and TXT formats

**Legacy Components:**
- `lmstudio_*`: Previous LM Studio integration (replaced by Ollama)
- `finetune_model.py`: Traditional transformer fine-tuning script (not used in current implementation)

### System Architecture

The system uses a hybrid approach:
1. **Document Retrieval**: TF-IDF vectorization finds relevant text chunks from legal documents
2. **Specialized Model**: Custom Ollama model (`compras-publicas-chile`) trained with domain-specific prompts
3. **RAG Pipeline**: Combines retrieved context with model generation for accurate legal responses

## Common Commands

### Environment Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install flask flask-cors scikit-learn numpy requests
```

### Ollama Model Management
```bash
# Start Ollama service
brew services start ollama

# Create specialized model (after training data preparation)
python src/models/model_creator.py

# Test model directly
ollama run compras-publicas-chile "¿Qué es una licitación pública?"
```

### Data Processing Pipeline
```bash
# Convert PDFs to text (if new documents added)
python src/data/pdf_converter.py

# Prepare training dataset from TXT files
python src/data/data_preparer.py

# Create/update specialized model
python src/models/model_creator.py
```

### Running the System
```bash
# Start the web server (ensure Ollama is running first)
source venv/bin/activate
python src/api/server.py

# Access web interface at http://localhost:5001
```

### System Status
```bash
# Check if Ollama is connected and documents loaded
curl http://localhost:5001/status

# Test query endpoint
curl -X POST http://localhost:5001/query \
  -H "Content-Type: application/json" \
  -d '{"question": "¿Qué es una licitación pública?"}'
```

## Key Configuration

**Model Configuration:**
- Current model: `compras-publicas-chile` (based on qwen2.5:0.5b)
- Model parameters: temperature=0.2, top_p=0.9, repeat_penalty=1.15
- Context window: 2048 tokens

**RAG Configuration:**
- Document chunking: 1000 characters with paragraph boundaries
- Vectorization: TF-IDF with max 5000 features, 1-2 gram range
- Search: Top 3 relevant chunks with cosine similarity > 0.1

**Server Configuration:**
- Port: 5001 (changed from 5000 due to macOS AirPlay conflict)
- CORS enabled for browser access
- Debug mode enabled for development

## Training Data Format

The training dataset (`compras_publicas_dataset.json`) uses conversational format:
```json
{
  "instruction": "Eres un experto en compras públicas de Chile...",
  "input": "¿Qué es una licitación pública?",
  "output": "Una licitación pública es..."
}
```

Generated from legal documents using pattern matching for definitions, procedures, and requirements.

## Important Notes

- The `compras-publicas-chile` model is specialized exclusively for Chilean public procurement law
- Document chunks are automatically loaded from TXT files in the repository
- The system requires Ollama to be running locally on port 11434
- Web interface provides real-time status of Ollama connection and document loading
- Virtual environment is required due to Python dependency management constraints on macOS