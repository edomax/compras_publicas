#!/usr/bin/env python3
"""
Script de migración para reorganizar automáticamente el proyecto
a la nueva estructura de carpetas
"""

import os
import shutil
from pathlib import Path
import json

class ProjectMigrator:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.backup_dir = self.project_root / "backup_before_migration"
        
        # Mapeo de archivos actuales a nueva ubicación
        self.file_mappings = {
            # Código fuente principal
            "ollama_client.py": "src/core/ollama_client.py",
            "ollama_server.py": "src/api/server.py",
            
            # Modelos y entrenamiento
            "create_specialized_model.py": "src/models/model_creator.py",
            "finetune_model.py": "src/models/fine_tuner.py",
            "prepare_training_data.py": "src/data/data_preparer.py",
            "pdf_to_txt.py": "src/data/pdf_converter.py",
            
            # Configuración de modelos
            "Modelfile": "models/ollama/Modelfile",
            
            # Frontend
            "ollama_interface.html": "web/templates/index.html",
            "lmstudio_interface.html": "web/legacy/lmstudio_interface.html",
            
            # Scripts de descarga
            "download_ley_compras.py": "scripts/download_documents.py",
            "download_ley_compras_pdf.py": "scripts/download_documents_pdf.py",
            "download_ley_oficial.py": "scripts/download_oficial.py",
            
            # Datos de entrenamiento
            "compras_publicas_dataset.json": "data/training/compras_publicas_dataset.json",
            "compras_publicas_dataset.jsonl": "data/training/compras_publicas_dataset.jsonl",
            
            # Legacy
            "lmstudio_client.py": "legacy/lmstudio_client.py",
            "server.py": "legacy/server.py",
        }
        
        # Mapeo de archivos PDF
        self.pdf_mappings = {
            "LEY_19886_Compras_Publicas_Chile_OFICIAL.pdf": "data/raw/pdfs/LEY_19886_Compras_Publicas_Chile_OFICIAL.pdf",
            "Nuevo_Reglamento_Compras_Publicas_2024.pdf": "data/raw/pdfs/Nuevo_Reglamento_Compras_Publicas_2024.pdf",
            "PPT_Nuevo_Reglamento_Compras_Publicas.pdf": "data/raw/pdfs/PPT_Nuevo_Reglamento_Compras_Publicas.pdf",
        }
        
        # Mapeo de archivos TXT
        self.txt_mappings = {
            "LEY_19886_Compras_Publicas_Chile_OFICIAL.txt": "data/processed/txt/LEY_19886_Compras_Publicas_Chile_OFICIAL.txt",
            "Nuevo_Reglamento_Compras_Publicas_2024.txt": "data/processed/txt/Nuevo_Reglamento_Compras_Publicas_2024.txt",
            "PPT_Nuevo_Reglamento_Compras_Publicas.txt": "data/processed/txt/PPT_Nuevo_Reglamento_Compras_Publicas.txt",
            "ley_compras_publicas_chile.txt": "data/processed/txt/ley_compras_publicas_chile.txt",
        }
        
        # Estructura de directorios a crear
        self.directories = [
            "src",
            "src/core",
            "src/api", 
            "src/models",
            "src/data",
            "src/utils",
            "web",
            "web/static",
            "web/static/css",
            "web/static/js",
            "web/static/images",
            "web/templates",
            "web/legacy",
            "data",
            "data/raw",
            "data/raw/pdfs",
            "data/raw/external",
            "data/processed",
            "data/processed/txt",
            "data/processed/embeddings",
            "data/training",
            "data/training/model_checkpoints",
            "models",
            "models/ollama",
            "models/ollama/model_configs",
            "models/checkpoints",
            "models/configs",
            "scripts",
            "tests",
            "tests/unit",
            "tests/integration",
            "tests/fixtures",
            "tests/fixtures/sample_documents",
            "docs",
            "legacy",
            "logs"
        ]
    
    def create_backup(self):
        """Crear backup del proyecto actual"""
        print("📦 Creando backup del proyecto actual...")
        
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        
        # Crear backup excluyendo venv y archivos temporales
        ignore_patterns = shutil.ignore_patterns('venv', '__pycache__', '*.pyc', '.git', 'backup_*')
        shutil.copytree(self.project_root, self.backup_dir, ignore=ignore_patterns)
        
        print(f"✅ Backup creado en: {self.backup_dir}")
    
    def create_directory_structure(self):
        """Crear estructura de directorios"""
        print("📁 Creando estructura de directorios...")
        
        for directory in self.directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            
            # Crear __init__.py en directorios Python
            if directory.startswith('src/') or directory in ['src', 'tests']:
                init_file = dir_path / "__init__.py"
                if not init_file.exists():
                    init_file.touch()
        
        print(f"✅ Creados {len(self.directories)} directorios")
    
    def move_files(self):
        """Mover archivos a nueva ubicación"""
        print("📋 Moviendo archivos a nueva estructura...")
        
        moved_count = 0
        
        # Combinar todos los mapeos
        all_mappings = {**self.file_mappings, **self.pdf_mappings, **self.txt_mappings}
        
        for source_file, target_path in all_mappings.items():
            source = self.project_root / source_file
            target = self.project_root / target_path
            
            if source.exists():
                # Crear directorio padre si no existe
                target.parent.mkdir(parents=True, exist_ok=True)
                
                # Mover archivo
                shutil.move(str(source), str(target))
                print(f"  ✓ {source_file} → {target_path}")
                moved_count += 1
            else:
                print(f"  ⚠ {source_file} no encontrado")
        
        print(f"✅ Movidos {moved_count} archivos")
    
    def create_config_files(self):
        """Crear archivos de configuración"""
        print("⚙️ Creando archivos de configuración...")
        
        # requirements.txt
        requirements_content = """flask>=2.3.0
flask-cors>=4.0.0
requests>=2.31.0
scikit-learn>=1.3.0
numpy>=1.24.0
PyPDF2>=3.0.0
pdfplumber>=0.9.0
python-dotenv>=1.0.0
pytest>=7.0.0
pathlib>=1.0.1
"""
        
        # .env.example
        env_example_content = """# Configuración del servidor
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
"""
        
        # .gitignore
        gitignore_content = """# Virtual environment
venv/
env/

# Environment variables
.env

# Python
__pycache__/
*.pyc
*.pyo
*.pyd

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
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Temporary files
*.tmp
*.temp

# Backup
backup_*/

# Testing
.pytest_cache/
.coverage
htmlcov/

# Distribution
dist/
build/
*.egg-info/
"""
        
        # Crear archivos
        config_files = {
            "requirements.txt": requirements_content,
            ".env.example": env_example_content,
            ".gitignore": gitignore_content
        }
        
        for filename, content in config_files.items():
            file_path = self.project_root / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✓ Creado {filename}")
        
        print("✅ Archivos de configuración creados")
    
    def update_imports(self):
        """Actualizar imports en archivos movidos"""
        print("🔧 Actualizando imports...")
        
        # Mapeo de imports antiguos a nuevos
        import_updates = {
            "from src.core.ollama_client import": "from src.core.ollama_client import",
            "import src.core.ollama_client": "import src.core.ollama_client",
            "from src.data.data_preparer import": "from src.data.data_preparer import",
            "from src.models.model_creator import": "from src.models.model_creator import",
        }
        
        # Buscar archivos Python en la nueva estructura
        python_files = list(self.project_root.rglob("*.py"))
        
        updated_files = 0
        for python_file in python_files:
            if "venv" in str(python_file) or "backup_" in str(python_file):
                continue
            
            try:
                with open(python_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Aplicar actualizaciones de imports
                for old_import, new_import in import_updates.items():
                    content = content.replace(old_import, new_import)
                
                # Si hubo cambios, guardar archivo
                if content != original_content:
                    with open(python_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"  ✓ Actualizado {python_file.relative_to(self.project_root)}")
                    updated_files += 1
                    
            except Exception as e:
                print(f"  ⚠ Error actualizando {python_file}: {e}")
        
        print(f"✅ Actualizados {updated_files} archivos")
    
    def create_init_files(self):
        """Crear archivos __init__.py con imports útiles"""
        print("📝 Creando archivos __init__.py...")
        
        # src/core/__init__.py
        core_init = '''"""
Módulo core - Lógica de negocio central
"""

from .ollama_client import OllamaClient

__all__ = ['OllamaClient']
'''
        
        # src/models/__init__.py
        models_init = '''"""
Módulo models - Gestión de modelos y entrenamiento
"""

from .model_creator import SpecializedModelCreator

__all__ = ['SpecializedModelCreator']
'''
        
        # src/data/__init__.py
        data_init = '''"""
Módulo data - Procesamiento de datos
"""

from .data_preparer import TrainingDataPreparer

__all__ = ['TrainingDataPreparer']
'''
        
        init_files = {
            "src/core/__init__.py": core_init,
            "src/models/__init__.py": models_init,
            "src/data/__init__.py": data_init,
        }
        
        for file_path, content in init_files.items():
            full_path = self.project_root / file_path
            if full_path.parent.exists():
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  ✓ Creado {file_path}")
        
        print("✅ Archivos __init__.py creados")
    
    def create_scripts(self):
        """Crear scripts de utilidad"""
        print("📜 Creando scripts de utilidad...")
        
        # setup.sh
        setup_script = '''#!/bin/bash
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
'''
        
        # train_model.sh
        train_script = '''#!/bin/bash
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
'''
        
        scripts = {
            "scripts/setup.sh": setup_script,
            "scripts/train_model.sh": train_script,
        }
        
        for script_path, content in scripts.items():
            full_path = self.project_root / script_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Hacer ejecutable
            os.chmod(full_path, 0o755)
            print(f"  ✓ Creado {script_path}")
        
        print("✅ Scripts creados")
    
    def update_claude_md(self):
        """Actualizar CLAUDE.md con nueva estructura"""
        print("📖 Actualizando CLAUDE.md...")
        
        claude_md_path = self.project_root / "CLAUDE.md"
        if claude_md_path.exists():
            with open(claude_md_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Actualizar rutas en el contenido
            updates = {
                "ollama_client.py": "src/core/ollama_client.py",
                "ollama_server.py": "src/api/server.py",
                "python ollama_server.py": "python src/api/server.py",
                "python create_specialized_model.py": "python src/models/model_creator.py",
                "python prepare_training_data.py": "python src/data/data_preparer.py",
                "python pdf_to_txt.py": "python src/data/pdf_converter.py",
            }
            
            for old_path, new_path in updates.items():
                content = content.replace(old_path, new_path)
            
            with open(claude_md_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("  ✓ CLAUDE.md actualizado")
        
        print("✅ Documentación actualizada")
    
    def generate_migration_report(self):
        """Generar reporte de migración"""
        print("📋 Generando reporte de migración...")
        
        report = {
            "migration_date": str(Path().cwd()),
            "backup_location": str(self.backup_dir),
            "directories_created": len(self.directories),
            "files_moved": len(self.file_mappings) + len(self.pdf_mappings) + len(self.txt_mappings),
            "new_structure": self.directories,
            "file_mappings": {**self.file_mappings, **self.pdf_mappings, **self.txt_mappings}
        }
        
        report_path = self.project_root / "migration_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Reporte guardado en: {report_path}")
    
    def run_migration(self):
        """Ejecutar migración completa"""
        print("🚀 Iniciando migración del proyecto...")
        print("=" * 60)
        
        try:
            # Paso 1: Backup
            self.create_backup()
            
            # Paso 2: Crear estructura
            self.create_directory_structure()
            
            # Paso 3: Mover archivos
            self.move_files()
            
            # Paso 4: Crear configuraciones
            self.create_config_files()
            
            # Paso 5: Actualizar imports
            self.update_imports()
            
            # Paso 6: Crear __init__.py
            self.create_init_files()
            
            # Paso 7: Crear scripts
            self.create_scripts()
            
            # Paso 8: Actualizar documentación
            self.update_claude_md()
            
            # Paso 9: Generar reporte
            self.generate_migration_report()
            
            print("=" * 60)
            print("🎉 ¡Migración completada exitosamente!")
            print(f"📦 Backup disponible en: {self.backup_dir}")
            print("\n🚀 Próximos pasos:")
            print("  1. cd al directorio del proyecto")
            print("  2. chmod +x scripts/setup.sh")
            print("  3. ./scripts/setup.sh")
            print("  4. python src/api/server.py")
            
        except Exception as e:
            print(f"❌ Error durante la migración: {e}")
            print(f"💡 Restaurar desde backup: {self.backup_dir}")
            raise

def main():
    """Función principal"""
    print("🏗️ Script de Migración - Compras Públicas Chile")
    print("Este script reorganizará automáticamente la estructura del proyecto")
    
    response = input("\n¿Continuar con la migración? (s/N): ").lower().strip()
    
    if response in ['s', 'si', 'sí', 'y', 'yes']:
        migrator = ProjectMigrator()
        migrator.run_migration()
    else:
        print("❌ Migración cancelada")

if __name__ == "__main__":
    main()