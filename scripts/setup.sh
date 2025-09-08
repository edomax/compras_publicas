#!/bin/bash
# Script de configuración inicial del proyecto

echo "🚀 Configurando proyecto Compras Públicas Chile..."

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias
echo "📋 Instalando dependencias..."
pip install -r requirements.txt

# Verificar Ollama
echo "🤖 Verificando Ollama..."
if command -v ollama &> /dev/null; then
    echo "✅ Ollama encontrado"
    ollama list
else
    echo "❌ Ollama no encontrado. Instala con: brew install ollama"
fi

# Crear archivo .env si no existe
if [ ! -f ".env" ]; then
    echo "⚙️ Creando archivo .env..."
    cp .env.example .env
fi

# Crear directorio de logs
mkdir -p logs

echo "✅ Configuración completada!"
echo "Para continuar:"
echo "  1. source venv/bin/activate"
echo "  2. python src/api/server.py"
