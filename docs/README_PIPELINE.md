# Pipeline de Ejecución - Sistema RAG Compras Públicas Chile

## Descripción
Pipeline automatizado para ejecutar el sistema completo de consultas de compras públicas chilenas usando Ollama y RAG.

## Uso

### Ejecución Completa (Recomendada)
```bash
# Ejecutar pipeline completo - configura todo desde cero
python3 run_pipeline.py
```

### Inicio Rápido
```bash
# Solo verificar servicios y ejecutar (si ya está configurado)
python3 run_pipeline.py --quick
```

## Fases del Pipeline

### 1. Verificación de Prerrequisitos
- ✅ Python 3.8+
- ✅ Ollama instalado (`brew install ollama`)

### 2. Configuración del Entorno
- ✅ Entorno virtual Python
- ✅ Dependencias (`requirements.txt`)

### 3. Servicios
- ✅ Ollama service (`brew services start ollama`)
- ✅ Verificación API Ollama (puerto 11434)

### 4. Procesamiento de Documentos
- ✅ Conversión PDF → TXT (si necesario)
- ✅ Validación de documentos legales

### 5. Datos de Entrenamiento
- ✅ Extracción Q&A de documentos legales
- ✅ Generación dataset JSON

### 6. Modelo Especializado
- ✅ Creación `compras-publicas-chile` en Ollama
- ✅ Configuración con Modelfile

### 7. Servidor Web
- ✅ Flask server (puerto 5001)
- ✅ API endpoints y interfaz web

### 8. Verificación del Sistema
- ✅ Test de conectividad
- ✅ Consulta de prueba

## Endpoints de la API

- `GET /` - Interfaz web
- `GET /status` - Estado del sistema
- `POST /query` - Consultas RAG
- `GET /documents` - Lista de documentos
- `GET /reload_documents` - Recargar documentos

## Estructura de Archivos

```
/
├── run_pipeline.py          # Script principal del pipeline
├── src/
│   ├── api/server.py        # Servidor Flask
│   ├── core/ollama_client.py # Cliente RAG
│   ├── data/                # Procesamiento de datos
│   └── models/              # Gestión de modelos
├── data/
│   ├── raw/pdfs/           # PDFs originales
│   ├── processed/txt/      # Textos procesados
│   └── training/           # Dataset de entrenamiento
├── models/ollama/Modelfile  # Configuración modelo Ollama
└── web/templates/          # Interfaz web
```

## Solución de Problemas

### Error: Ollama no conecta
```bash
# Verificar servicio
brew services list | grep ollama

# Reiniciar servicio
brew services restart ollama

# Verificar puerto
curl http://localhost:11434/api/tags
```

### Error: Documentos no encontrados
```bash
# Verificar documentos TXT
ls -la data/processed/txt/

# Reconvertir PDFs
python3 src/data/pdf_converter.py
```

### Error: Modelo no existe
```bash
# Listar modelos Ollama
ollama list

# Recrear modelo
python3 src/models/model_creator.py
```

## Logs y Debugging

El pipeline incluye logging detallado:
- ✅ Pasos exitosos
- ⚠️ Advertencias (continúa ejecución)
- ❌ Errores críticos (detiene pipeline)

## Requisitos del Sistema

- **Python**: 3.8+
- **Ollama**: Última versión
- **Memoria**: 4GB+ RAM
- **Espacio**: 2GB+ (modelos + documentos)
- **OS**: macOS, Linux, Windows

## Próximos Pasos

Después de ejecutar el pipeline:

1. Abre http://localhost:5001
2. Verifica estado del sistema
3. Realiza consultas de prueba
4. Revisa logs para optimizaciones