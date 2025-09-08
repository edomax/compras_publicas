#!/bin/bash
# Pipeline completo de entrenamiento del modelo

echo "🎯 Iniciando pipeline de entrenamiento..."

# Activar entorno virtual
source venv/bin/activate

# Paso 1: Convertir PDFs a TXT (si es necesario)
echo "📄 Convirtiendo PDFs a TXT..."
python src/data/pdf_converter.py

# Paso 2: Preparar datos de entrenamiento
echo "📊 Preparando datos de entrenamiento..."
python src/data/data_preparer.py

# Paso 3: Crear modelo especializado
echo "🤖 Creando modelo especializado..."
python src/models/model_creator.py

echo "✅ Pipeline de entrenamiento completado!"
