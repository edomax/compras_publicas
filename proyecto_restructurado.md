# Propuesta de Reorganización del Proyecto

## Estructura Propuesta

```
compras_publicas/
├── README.md
├── CLAUDE.md
├── requirements.txt
├── .gitignore
├── .env.example
│
├── src/                          # Código fuente principal
│   ├── __init__.py
│   ├── core/                     # Lógica de negocio central
│   │   ├── __init__.py
│   │   ├── ollama_client.py      # Cliente principal de Ollama
│   │   └── rag_engine.py         # Motor RAG (extraído del cliente)
│   │
│   ├── api/                      # Servicios web y APIs
│   │   ├── __init__.py
│   │   ├── server.py             # Servidor Flask principal
│   │   └── routes.py             # Rutas de la API
│   │
│   ├── models/                   # Gestión de modelos
│   │   ├── __init__.py
│   │   ├── model_creator.py      # create_specialized_model.py
│   │   ├── fine_tuner.py         # finetune_model.py (opcional)
│   │   └── model_config.py       # Configuraciones de modelos
│   │
│   ├── data/                     # Procesamiento de datos
│   │   ├── __init__.py
│   │   ├── pdf_converter.py      # pdf_to_txt.py
│   │   ├── data_preparer.py      # prepare_training_data.py
│   │   └── document_loader.py    # Carga de documentos
│   │
│   └── utils/                    # Utilidades comunes
│       ├── __init__.py
│       ├── config.py             # Configuraciones globales
│       └── logger.py             # Sistema de logging
│
├── web/                          # Frontend y interfaces web
│   ├── static/                   # Archivos estáticos
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   │
│   ├── templates/                # Templates HTML
│   │   ├── index.html            # ollama_interface.html
│   │   └── admin.html            # Panel de administración
│   │
│   └── legacy/                   # Interfaces obsoletas
│       └── lmstudio_interface.html
│
├── data/                         # Datos del proyecto
│   ├── raw/                      # Documentos originales
│   │   ├── pdfs/
│   │   │   ├── LEY_19886_Compras_Publicas_Chile_OFICIAL.pdf
│   │   │   ├── Nuevo_Reglamento_Compras_Publicas_2024.pdf
│   │   │   └── PPT_Nuevo_Reglamento_Compras_Publicas.pdf
│   │   │
│   │   └── external/             # Datos de fuentes externas
│   │
│   ├── processed/                # Documentos procesados
│   │   ├── txt/
│   │   │   ├── LEY_19886_Compras_Publicas_Chile_OFICIAL.txt
│   │   │   ├── Nuevo_Reglamento_Compras_Publicas_2024.txt
│   │   │   ├── PPT_Nuevo_Reglamento_Compras_Publicas.txt
│   │   │   └── ley_compras_publicas_chile.txt
│   │   │
│   │   └── embeddings/           # Vectores y embeddings
│   │
│   └── training/                 # Datos de entrenamiento
│       ├── compras_publicas_dataset.json
│       ├── compras_publicas_dataset.jsonl
│       └── model_checkpoints/
│
├── models/                       # Modelos y configuraciones
│   ├── ollama/
│   │   ├── Modelfile
│   │   └── model_configs/
│   │
│   ├── checkpoints/              # Modelos entrenados
│   └── configs/                  # Configuraciones de modelos
│
├── scripts/                      # Scripts de utilidad y automatización
│   ├── setup.sh                 # Script de configuración inicial
│   ├── download_documents.py    # download_ley_*.py combinados
│   ├── train_model.sh           # Pipeline completo de entrenamiento
│   └── deploy.sh               # Script de despliegue
│
├── tests/                       # Pruebas
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_ollama_client.py
│   │   ├── test_rag_engine.py
│   │   └── test_data_processing.py
│   │
│   ├── integration/
│   │   ├── test_api.py
│   │   └── test_model_creation.py
│   │
│   └── fixtures/                # Datos de prueba
│       └── sample_documents/
│
├── docs/                        # Documentación
│   ├── architecture.md
│   ├── api_reference.md
│   ├── deployment.md
│   └── user_guide.md
│
├── legacy/                      # Código obsoleto (mantener por referencia)
│   ├── lmstudio_client.py
│   ├── server.py
│   └── README_legacy.md
│
└── venv/                        # Entorno virtual (en .gitignore)
```

## Beneficios de esta Estructura

### 1. **Separación Clara de Responsabilidades**
- `src/`: Código fuente organizado por funcionalidad
- `web/`: Todo lo relacionado con interfaces web
- `data/`: Datos organizados por estado de procesamiento
- `models/`: Configuraciones y artefactos de modelos

### 2. **Escalabilidad**
- Fácil agregar nuevos modelos o tipos de datos
- Estructura modular permite crecimiento
- Separación entre lógica de negocio y presentación

### 3. **Mantenibilidad**
- Código legacy preservado pero separado
- Tests organizados por tipo
- Documentación centralizada

### 4. **Desarrollo**
- Scripts de automatización centralizados
- Configuraciones separadas del código
- Entorno de desarrollo claro

## Scripts de Migración Sugeridos

### 1. `migrate_structure.py`
```python
# Script para mover archivos a la nueva estructura
# Preservando historial de git cuando sea posible
```

### 2. `update_imports.py`
```python
# Script para actualizar todas las importaciones
# después de la reestructuración
```

### 3. `setup.sh`
```bash
#!/bin/bash
# Script de configuración inicial del proyecto
# - Crear entorno virtual
# - Instalar dependencias
# - Configurar Ollama
# - Verificar estructura
```

## Archivos de Configuración Nuevos

### `requirements.txt`
```
flask>=2.3.0
flask-cors>=4.0.0
requests>=2.31.0
scikit-learn>=1.3.0
numpy>=1.24.0
PyPDF2>=3.0.0
pdfplumber>=0.9.0
python-dotenv>=1.0.0
pytest>=7.0.0
```

### `.env.example`
```bash
# Configuración del servidor
FLASK_ENV=development
FLASK_PORT=5001
FLASK_HOST=0.0.0.0

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=compras-publicas-chile

# Datos
DATA_DIR=./data
DOCUMENTS_DIR=./data/processed/txt
TRAINING_DATA_FILE=./data/training/compras_publicas_dataset.json

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
```

### `.gitignore`
```
# Virtual environment
venv/
env/

# Environment variables
.env

# Python
__pycache__/
*.pyc
*.pyo

# Models and checkpoints
models/checkpoints/
*.model
*.bin

# Logs
logs/
*.log

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Temporary files
*.tmp
*.temp
```

¿Te parece bien esta estructura? ¿Quieres que cree el script de migración para reorganizar los archivos?