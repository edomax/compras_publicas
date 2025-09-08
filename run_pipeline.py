#!/usr/bin/env python3
"""
Pipeline de ejecución completo para el sistema RAG de Compras Públicas Chile
"""

import subprocess
import sys
import os
import time
import json
import requests
from pathlib import Path

class ComprasPublicasPipeline:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.venv_path = self.base_dir / 'venv'
        self.python_exe = self.venv_path / 'bin' / 'python3' if os.name != 'nt' else self.venv_path / 'Scripts' / 'python.exe'
        self.pip_exe = self.venv_path / 'bin' / 'pip' if os.name != 'nt' else self.venv_path / 'Scripts' / 'pip.exe'
        
    def log(self, message, level="INFO"):
        """Log con timestamp"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def run_command(self, command, description="", check=True):
        """Ejecutar comando con logging"""
        if description:
            self.log(f"Ejecutando: {description}")
        self.log(f"Comando: {command}")
        
        try:
            result = subprocess.run(command, shell=True, check=check, 
                                  capture_output=True, text=True)
            if result.stdout:
                print(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            self.log(f"Error ejecutando comando: {e}", "ERROR")
            if e.stderr:
                print(e.stderr)
            return False
    
    def check_prereqs(self):
        """Verificar prerrequisitos del sistema"""
        self.log("🔍 Verificando prerrequisitos...")
        
        # Verificar Python
        try:
            python_version = subprocess.check_output([sys.executable, '--version'], text=True)
            self.log(f"✅ {python_version.strip()}")
        except Exception as e:
            self.log(f"❌ Error verificando Python: {e}", "ERROR")
            return False
            
        # Verificar Ollama
        try:
            result = subprocess.run(['ollama', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.log("✅ Ollama instalado")
            else:
                self.log("❌ Ollama no encontrado. Instala con: brew install ollama", "ERROR")
                return False
        except FileNotFoundError:
            self.log("❌ Ollama no encontrado. Instala con: brew install ollama", "ERROR")
            return False
            
        return True
    
    def setup_environment(self):
        """Configurar entorno virtual y dependencias"""
        self.log("🔧 Configurando entorno...")
        
        # Crear entorno virtual si no existe
        if not self.venv_path.exists():
            self.log("Creando entorno virtual...")
            if not self.run_command(f"{sys.executable} -m venv {self.venv_path}"):
                return False
        
        # Instalar dependencias
        self.log("Instalando dependencias...")
        if not self.run_command(f"{self.pip_exe} install -r requirements.txt"):
            return False
            
        self.log("✅ Entorno configurado correctamente")
        return True
    
    def start_ollama_service(self):
        """Iniciar servicio Ollama"""
        self.log("🚀 Iniciando servicio Ollama...")
        
        # Verificar si ya está ejecutándose
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                self.log("✅ Ollama ya está ejecutándose")
                return True
        except:
            pass
        
        # Iniciar servicio
        if not self.run_command("brew services start ollama", check=False):
            self.log("Intentando iniciar Ollama de forma alternativa...")
            # Iniciar en background
            subprocess.Popen(['ollama', 'serve'], stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
        
        # Esperar a que el servicio esté listo
        for i in range(10):
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=2)
                if response.status_code == 200:
                    self.log("✅ Ollama iniciado correctamente")
                    return True
            except:
                time.sleep(2)
                self.log(f"Esperando Ollama... ({i+1}/10)")
        
        self.log("❌ No se pudo iniciar Ollama", "ERROR")
        return False
    
    def prepare_documents(self):
        """Preparar documentos para procesamiento"""
        self.log("📄 Preparando documentos...")
        
        # Convertir PDFs a texto si es necesario
        pdf_dir = self.base_dir / 'data' / 'raw' / 'pdfs'
        txt_dir = self.base_dir / 'data' / 'processed' / 'txt'
        
        if pdf_dir.exists() and any(pdf_dir.glob('*.pdf')):
            self.log("Convirtiendo PDFs a texto...")
            if not self.run_command(f"{self.python_exe} src/data/pdf_converter.py"):
                self.log("⚠️ Error convirtiendo PDFs, continuando...", "WARNING")
        
        # Verificar documentos de texto
        if not txt_dir.exists() or not any(txt_dir.glob('*.txt')):
            self.log("❌ No se encontraron documentos de texto", "ERROR")
            return False
        
        doc_count = len(list(txt_dir.glob('*.txt')))
        self.log(f"✅ {doc_count} documentos preparados")
        return True
    
    def prepare_training_data(self):
        """Preparar datos de entrenamiento"""
        self.log("🔧 Preparando datos de entrenamiento...")
        
        if not self.run_command(f"{self.python_exe} src/data/data_preparer.py"):
            self.log("⚠️ Error preparando datos de entrenamiento, continuando...", "WARNING")
        
        # Verificar dataset
        dataset_path = self.base_dir / 'data' / 'training' / 'compras_publicas_dataset.json'
        if dataset_path.exists():
            self.log("✅ Dataset de entrenamiento preparado")
            return True
        else:
            self.log("⚠️ Dataset no encontrado, el modelo base se usará sin fine-tuning", "WARNING")
            return True
    
    def create_specialized_model(self):
        """Crear modelo especializado en Ollama"""
        self.log("🤖 Creando modelo especializado...")
        
        # Verificar si el modelo ya existe
        try:
            response = requests.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                models = response.json().get('models', [])
                if any(model['name'].startswith('compras-publicas-chile') for model in models):
                    self.log("✅ Modelo especializado ya existe")
                    return True
        except:
            pass
        
        # Crear modelo
        if not self.run_command(f"{self.python_exe} src/models/model_creator.py"):
            return False
        
        self.log("✅ Modelo especializado creado")
        return True
    
    def start_web_server(self):
        """Iniciar servidor web"""
        self.log("🌐 Iniciando servidor web...")
        
        # Verificar si ya está ejecutándose
        try:
            response = requests.get("http://localhost:5001/status", timeout=5)
            if response.status_code == 200:
                self.log("✅ Servidor ya está ejecutándose en http://localhost:5001")
                return True
        except:
            pass
        
        self.log("Iniciando servidor Flask...")
        self.log("📖 Servidor estará disponible en http://localhost:5001")
        self.log("⚡ Para detener: Ctrl+C")
        
        # Iniciar servidor (esto bloqueará)
        os.chdir(self.base_dir)
        subprocess.run([str(self.python_exe), "src/api/server.py"])
        
        return True
    
    def test_system(self):
        """Probar el sistema completo"""
        self.log("🧪 Probando sistema...")
        
        # Probar conexión al servidor
        try:
            response = requests.get("http://localhost:5001/status", timeout=10)
            if response.status_code == 200:
                status = response.json()
                if status.get('status') == 'ready':
                    self.log("✅ Sistema listo y funcionando")
                    
                    # Probar consulta de ejemplo
                    test_query = {"question": "¿Qué es una licitación pública?"}
                    response = requests.post("http://localhost:5001/query", 
                                           json=test_query, timeout=30)
                    if response.status_code == 200:
                        result = response.json()
                        self.log("✅ Consulta de prueba exitosa")
                        self.log(f"Respuesta: {result['response'][:100]}...")
                        return True
        except Exception as e:
            self.log(f"❌ Error probando sistema: {e}", "ERROR")
            
        return False
    
    def run_full_pipeline(self):
        """Ejecutar pipeline completo"""
        self.log("🚀 INICIANDO PIPELINE COMPRAS PÚBLICAS CHILE")
        self.log("=" * 50)
        
        steps = [
            ("Verificar prerrequisitos", self.check_prereqs),
            ("Configurar entorno", self.setup_environment),
            ("Iniciar Ollama", self.start_ollama_service),
            ("Preparar documentos", self.prepare_documents),
            ("Preparar datos de entrenamiento", self.prepare_training_data),
            ("Crear modelo especializado", self.create_specialized_model),
        ]
        
        for step_name, step_func in steps:
            self.log(f"📋 {step_name}...")
            if not step_func():
                self.log(f"❌ Error en: {step_name}", "ERROR")
                return False
            self.log(f"✅ {step_name} completado")
            self.log("-" * 30)
        
        self.log("🎉 ¡PIPELINE COMPLETADO EXITOSAMENTE!")
        self.log("🌐 Iniciando servidor web...")
        
        # Iniciar servidor (esto mantendrá el programa ejecutándose)
        return self.start_web_server()
    
    def run_quick_start(self):
        """Inicio rápido - solo verificar y ejecutar"""
        self.log("⚡ INICIO RÁPIDO - COMPRAS PÚBLICAS CHILE")
        self.log("=" * 40)
        
        if not self.start_ollama_service():
            return False
        
        return self.start_web_server()

def main():
    pipeline = ComprasPublicasPipeline()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        success = pipeline.run_quick_start()
    else:
        success = pipeline.run_full_pipeline()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()