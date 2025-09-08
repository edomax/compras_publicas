#!/usr/bin/env python3
"""
Crear modelo especializado usando Ollama con sistema de prompts personalizado
"""

import json
import random
from pathlib import Path

class SpecializedModelCreator:
    def __init__(self):
        self.training_data = []
        self.load_training_data()
        
    def load_training_data(self):
        """Cargar datos de entrenamiento"""
        if Path("compras_publicas_dataset.json").exists():
            with open("compras_publicas_dataset.json", 'r', encoding='utf-8') as f:
                self.training_data = json.load(f)
            print(f"✅ Cargados {len(self.training_data)} ejemplos")
        else:
            print("❌ No se encontró el dataset. Ejecuta prepare_training_data.py primero")
            
    def create_modelfile(self):
        """Crear Modelfile optimizado para Ollama"""
        
        # Seleccionar mejores ejemplos para el sistema prompt
        examples = random.sample(self.training_data, min(10, len(self.training_data)))
        
        examples_text = ""
        for i, example in enumerate(examples, 1):
            examples_text += f"""
Ejemplo {i}:
Usuario: {example['input']}
Asistente: {example['output'][:200]}...
"""
        
        modelfile_content = f"""FROM qwen2.5:0.5b

SYSTEM \"\"\"Eres un asistente especializado en compras públicas de Chile. Tu conocimiento se basa exclusivamente en la legislación chilena, incluyendo:

- Ley 19.886 de Bases sobre Contratos Administrativos de Suministro y Prestación de Servicios
- Reglamento de la Ley de Compras Públicas 
- Nuevo Reglamento de Compras Públicas 2024
- Normativas y procedimientos de ChileCompra

INSTRUCCIONES ESPECÍFICAS:
1. Responde ÚNICAMENTE basándote en la legislación chilena de compras públicas
2. Si no tienes información específica, di: "No tengo información específica sobre ese tema en la legislación de compras públicas chilenas"
3. Usa terminología técnica precisa del ámbito de compras públicas
4. Cita artículos específicos cuando sea relevante
5. Mantén un tono profesional y técnico
6. Si la pregunta no está relacionada con compras públicas, redirige educadamente al tema

EJEMPLOS DE RESPUESTAS CORRECTAS:{examples_text}

Recuerda: Tu especialidad es EXCLUSIVAMENTE compras públicas de Chile. No respondas preguntas fuera de este ámbito.\"\"\"

PARAMETER temperature 0.2
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER repeat_penalty 1.15
PARAMETER num_ctx 2048
"""
        
        with open("Modelfile", 'w', encoding='utf-8') as f:
            f.write(modelfile_content)
            
        print("✅ Modelfile creado: ./Modelfile")
        
    def create_ollama_model(self, model_name: str = "compras-publicas-chile"):
        """Crear modelo en Ollama"""
        import subprocess
        
        try:
            print(f"🔨 Creando modelo '{model_name}' en Ollama...")
            result = subprocess.run(
                ["ollama", "create", model_name, "-f", "Modelfile"],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                print(f"✅ Modelo '{model_name}' creado exitosamente!")
                print(f"Para usarlo: ollama run {model_name}")
                return True
            else:
                print(f"❌ Error creando modelo: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("⏰ Timeout creando modelo (puede tomar tiempo la primera vez)")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
            
    def test_model(self, model_name: str = "compras-publicas-chile"):
        """Probar el modelo creado"""
        import subprocess
        
        test_questions = [
            "¿Qué es una licitación pública?",
            "¿Cuáles son los montos para trato directo?", 
            "¿Qué documentos se requieren para licitar?",
            "¿Qué cambios introduce el nuevo reglamento 2024?"
        ]
        
        print(f"\n🧪 Probando modelo '{model_name}':")
        print("=" * 50)
        
        for question in test_questions:
            try:
                result = subprocess.run(
                    ["ollama", "run", model_name, question],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    print(f"\n❓ Pregunta: {question}")
                    print(f"🤖 Respuesta: {result.stdout.strip()}")
                    print("-" * 40)
                else:
                    print(f"❌ Error en pregunta: {question}")
                    
            except subprocess.TimeoutExpired:
                print(f"⏰ Timeout en pregunta: {question}")
            except Exception as e:
                print(f"❌ Error: {e}")
                
    def update_ollama_client(self, model_name: str = "compras-publicas-chile"):
        """Actualizar cliente para usar el nuevo modelo"""
        client_file = "ollama_client.py"
        
        if Path(client_file).exists():
            with open(client_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Actualizar el nombre del modelo
            updated_content = content.replace(
                'self.model = "qwen2.5:0.5b"',
                f'self.model = "{model_name}"'
            )
            
            with open(client_file, 'w', encoding='utf-8') as f:
                f.write(updated_content)
                
            print(f"✅ Cliente actualizado para usar '{model_name}'")
        else:
            print("⚠️ No se encontró ollama_client.py")

def main():
    """Crear modelo especializado"""
    print("🎯 Creando Modelo Especializado en Compras Públicas Chile")
    print("=" * 60)
    
    creator = SpecializedModelCreator()
    
    if not creator.training_data:
        print("❌ No hay datos de entrenamiento. Ejecuta prepare_training_data.py primero")
        return
    
    # Crear Modelfile
    creator.create_modelfile()
    
    # Crear modelo en Ollama
    model_name = "compras-publicas-chile"
    success = creator.create_ollama_model(model_name)
    
    if success:
        # Actualizar cliente
        creator.update_ollama_client(model_name)
        
        # Probar modelo
        creator.test_model(model_name)
        
        print(f"\n🎉 Modelo especializado '{model_name}' creado exitosamente!")
        print(f"🚀 Para usarlo en tu sistema:")
        print(f"   1. El servidor ya está configurado para usar '{model_name}'")
        print(f"   2. Reinicia el servidor: Ctrl+C y vuelve a ejecutar ollama_server.py")
        print(f"   3. Visita: http://localhost:5001")
        
    else:
        print("❌ Error creando el modelo especializado")

if __name__ == "__main__":
    main()