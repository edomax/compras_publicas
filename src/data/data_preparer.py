#!/usr/bin/env python3
"""
Preparar datos de entrenamiento para fine-tuning del modelo de compras públicas
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any
import random

class TrainingDataPreparer:
    def __init__(self):
        self.documents = []
        self.training_data = []
        
    def load_documents(self, directory: str = ".") -> None:
        """Cargar documentos TXT"""
        txt_files = list(Path(directory).glob("*.txt"))
        print(f"Cargando {len(txt_files)} archivos TXT...")
        
        for txt_file in txt_files:
            try:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.documents.append({
                        'filename': txt_file.name,
                        'content': content
                    })
                print(f"✓ Cargado: {txt_file.name}")
            except Exception as e:
                print(f"✗ Error cargando {txt_file.name}: {e}")
    
    def extract_qa_pairs(self) -> None:
        """Extraer pares pregunta-respuesta de los documentos"""
        
        # Patrones para extraer información relevante
        patterns = {
            'definitions': [
                r'(?:se entiende por|significa|definición de|concepto de)\s+([^.]+)\s*[:.]?\s*([^.]+(?:\.[^.]*){0,3}\.)',
                r'([A-Z][^:]+):\s*([^.]+(?:\.[^.]*){0,2}\.)',
                r'Art[íi]culo\s+\d+[°º]?\.?\s*([^.]+)\s*\.\s*([^.]+(?:\.[^.]*){0,3}\.)'
            ],
            'procedures': [
                r'(procedimiento[^.]*)\s*[:.]?\s*([^.]+(?:\.[^.]*){0,3}\.)',
                r'(proceso de[^.]*)\s*[:.]?\s*([^.]+(?:\.[^.]*){0,3}\.)'
            ],
            'requirements': [
                r'(requisitos?[^.]*)\s*[:.]?\s*([^.]+(?:\.[^.]*){0,3}\.)',
                r'(documentos? (?:necesarios?|requeridos?)[^.]*)\s*[:.]?\s*([^.]+(?:\.[^.]*){0,3}\.)'
            ]
        }
        
        # Generar QA pairs
        qa_pairs = []
        
        for doc in self.documents:
            content = doc['content']
            filename = doc['filename']
            
            # Extraer definiciones
            for pattern in patterns['definitions']:
                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    concept = match.group(1).strip()
                    definition = match.group(2).strip()
                    
                    if len(concept) > 10 and len(definition) > 20:
                        qa_pairs.append({
                            'question': f"¿Qué es {concept.lower()}?",
                            'answer': definition,
                            'source': filename,
                            'type': 'definition'
                        })
                        
                        qa_pairs.append({
                            'question': f"Define {concept.lower()}",
                            'answer': definition,
                            'source': filename,
                            'type': 'definition'
                        })
            
            # Extraer procedimientos
            for pattern in patterns['procedures']:
                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    procedure = match.group(1).strip()
                    description = match.group(2).strip()
                    
                    if len(procedure) > 10 and len(description) > 20:
                        qa_pairs.append({
                            'question': f"¿Cómo funciona el {procedure.lower()}?",
                            'answer': description,
                            'source': filename,
                            'type': 'procedure'
                        })
        
        # Generar preguntas generales sobre compras públicas
        general_questions = [
            {
                'question': "¿Qué es una licitación pública?",
                'keywords': ['licitación pública', 'licitación', 'proceso licitatorio']
            },
            {
                'question': "¿Cuáles son los tipos de procedimientos de compra?",
                'keywords': ['tipos de procedimientos', 'procedimientos de compra', 'modalidades']
            },
            {
                'question': "¿Qué documentos se requieren para licitar?",
                'keywords': ['documentos', 'requisitos', 'licitación']
            },
            {
                'question': "¿Cuáles son los montos para licitación pública?",
                'keywords': ['montos', 'umbrales', 'licitación pública']
            },
            {
                'question': "¿Qué es el trato directo?",
                'keywords': ['trato directo', 'contratación directa']
            },
            {
                'question': "¿Cuáles son las etapas de una licitación?",
                'keywords': ['etapas', 'fases', 'proceso licitatorio']
            },
            {
                'question': "¿Qué es ChileCompra?",
                'keywords': ['ChileCompra', 'plataforma', 'sistema']
            },
            {
                'question': "¿Qué cambios introduce el nuevo reglamento 2024?",
                'keywords': ['nuevo reglamento', '2024', 'cambios', 'modificaciones']
            }
        ]
        
        # Buscar respuestas para preguntas generales
        for general_q in general_questions:
            best_answer = self.find_best_answer(general_q['keywords'])
            if best_answer:
                qa_pairs.append({
                    'question': general_q['question'],
                    'answer': best_answer['answer'],
                    'source': best_answer['source'],
                    'type': 'general'
                })
        
        print(f"✓ Generados {len(qa_pairs)} pares pregunta-respuesta")
        self.qa_pairs = qa_pairs
        
    def find_best_answer(self, keywords: List[str]) -> Dict[str, Any]:
        """Encontrar la mejor respuesta para palabras clave"""
        best_match = None
        best_score = 0
        
        for doc in self.documents:
            content = doc['content'].lower()
            score = 0
            
            for keyword in keywords:
                if keyword.lower() in content:
                    score += content.count(keyword.lower())
            
            if score > best_score:
                best_score = score
                # Extraer párrafo relevante
                sentences = content.split('.')
                relevant_sentences = []
                
                for sentence in sentences:
                    if any(keyword.lower() in sentence for keyword in keywords):
                        relevant_sentences.append(sentence.strip())
                        if len(relevant_sentences) >= 3:
                            break
                
                if relevant_sentences:
                    best_match = {
                        'answer': '. '.join(relevant_sentences) + '.',
                        'source': doc['filename']
                    }
        
        return best_match
    
    def create_training_dataset(self) -> None:
        """Crear dataset en formato para fine-tuning"""
        training_examples = []
        
        for qa in self.qa_pairs:
            # Formato conversacional
            conversation = {
                "instruction": "Eres un experto en compras públicas de Chile. Responde basándote únicamente en la legislación chilena.",
                "input": qa['question'],
                "output": qa['answer']
            }
            training_examples.append(conversation)
            
            # Variaciones de la pregunta
            variations = self.generate_question_variations(qa['question'])
            for variation in variations[:2]:  # Máximo 2 variaciones por pregunta
                training_examples.append({
                    "instruction": "Eres un experto en compras públicas de Chile. Responde basándote únicamente en la legislación chilena.",
                    "input": variation,
                    "output": qa['answer']
                })
        
        # Mezclar dataset
        random.shuffle(training_examples)
        
        print(f"✓ Dataset final: {len(training_examples)} ejemplos de entrenamiento")
        self.training_data = training_examples
        
    def generate_question_variations(self, question: str) -> List[str]:
        """Generar variaciones de preguntas"""
        variations = []
        
        # Patrones de variación
        if question.startswith("¿Qué es"):
            concept = question.replace("¿Qué es ", "").replace("?", "")
            variations.extend([
                f"Explícame {concept}",
                f"¿Podrías definir {concept}?",
                f"¿Cuál es la definición de {concept}?"
            ])
        
        elif question.startswith("¿Cómo"):
            variations.extend([
                question.replace("¿Cómo", "Explícame cómo"),
                question.replace("¿Cómo", "¿De qué manera")
            ])
        
        elif question.startswith("¿Cuáles son"):
            content = question.replace("¿Cuáles son ", "").replace("?", "")
            variations.extend([
                f"Dime cuáles son {content}",
                f"Lista {content}",
                f"¿Qué {content} existen?"
            ])
        
        return variations
    
    def save_dataset(self, filename: str = "compras_publicas_dataset.json") -> None:
        """Guardar dataset en formato JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.training_data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Dataset guardado en: {filename}")
        print(f"  - {len(self.training_data)} ejemplos de entrenamiento")
        
        # Crear también formato JSONL para algunos frameworks
        jsonl_filename = filename.replace('.json', '.jsonl')
        with open(jsonl_filename, 'w', encoding='utf-8') as f:
            for example in self.training_data:
                f.write(json.dumps(example, ensure_ascii=False) + '\n')
        
        print(f"✓ Dataset JSONL guardado en: {jsonl_filename}")
    
    def show_sample(self, n: int = 5) -> None:
        """Mostrar ejemplos del dataset"""
        print(f"\n📝 Muestra del dataset ({n} ejemplos):")
        print("=" * 50)
        
        for i, example in enumerate(self.training_data[:n]):
            print(f"\nEjemplo {i+1}:")
            print(f"Pregunta: {example['input']}")
            print(f"Respuesta: {example['output'][:200]}...")
            print("-" * 30)

def main():
    """Ejecutar preparación de datos"""
    print("🔧 Preparando datos de entrenamiento para compras públicas...")
    print("=" * 60)
    
    preparer = TrainingDataPreparer()
    
    # Cargar documentos
    preparer.load_documents()
    
    # Extraer pares Q&A
    preparer.extract_qa_pairs()
    
    # Crear dataset
    preparer.create_training_dataset()
    
    # Guardar dataset
    preparer.save_dataset()
    
    # Mostrar muestra
    preparer.show_sample()
    
    print("\n✅ Datos de entrenamiento preparados exitosamente!")

if __name__ == "__main__":
    main()