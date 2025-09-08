#!/usr/bin/env python3
"""
Fine-tuning script para crear modelo especializado en compras públicas chilenas
"""

import json
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    TrainingArguments, 
    Trainer,
    DataCollatorForLanguageModeling
)
from datasets import Dataset
import os
from pathlib import Path

class ComprasPublicasFineTuner:
    def __init__(self, base_model: str = "microsoft/DialoGPT-small"):
        self.base_model = base_model
        self.model = None
        self.tokenizer = None
        self.dataset = None
        
    def load_model_and_tokenizer(self):
        """Cargar modelo base y tokenizer"""
        print(f"📦 Cargando modelo base: {self.base_model}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.base_model)
        
        # Agregar pad token si no existe
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        self.model = AutoModelForCausalLM.from_pretrained(
            self.base_model,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None
        )
        
        print("✅ Modelo y tokenizer cargados")
        
    def load_dataset(self, dataset_file: str = "compras_publicas_dataset.json"):
        """Cargar dataset de entrenamiento"""
        print(f"📊 Cargando dataset: {dataset_file}")
        
        with open(dataset_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Formatear datos para entrenamiento conversacional
        formatted_data = []
        for example in data:
            # Formato: Sistema + Usuario + Asistente
            text = f"Sistema: {example['instruction']}\nUsuario: {example['input']}\nAsistente: {example['output']}"
            formatted_data.append({"text": text})
        
        self.dataset = Dataset.from_list(formatted_data)
        print(f"✅ Dataset cargado: {len(self.dataset)} ejemplos")
        
    def tokenize_dataset(self):
        """Tokenizar dataset"""
        print("🔤 Tokenizando dataset...")
        
        def tokenize_function(examples):
            return self.tokenizer(
                examples["text"],
                truncation=True,
                padding=True,
                max_length=512,
                return_tensors="pt"
            )
        
        self.dataset = self.dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=["text"]
        )
        
        print("✅ Dataset tokenizado")
        
    def setup_training_args(self, output_dir: str = "./compras-publicas-model"):
        """Configurar argumentos de entrenamiento"""
        training_args = TrainingArguments(
            output_dir=output_dir,
            overwrite_output_dir=True,
            num_train_epochs=3,
            per_device_train_batch_size=4,
            per_device_eval_batch_size=4,
            warmup_steps=100,
            logging_steps=50,
            save_steps=500,
            evaluation_strategy="no",
            save_strategy="steps",
            load_best_model_at_end=False,
            dataloader_drop_last=True,
            fp16=torch.cuda.is_available(),
            gradient_accumulation_steps=2,
            learning_rate=5e-5,
            weight_decay=0.01,
            max_grad_norm=1.0,
            lr_scheduler_type="cosine",
            report_to="none"  # Desactivar wandb
        )
        
        return training_args
        
    def train(self):
        """Entrenar el modelo"""
        print("🚀 Iniciando entrenamiento...")
        
        # Dividir dataset
        train_size = int(0.9 * len(self.dataset))
        eval_size = len(self.dataset) - train_size
        
        train_dataset = self.dataset.select(range(train_size))
        eval_dataset = self.dataset.select(range(train_size, train_size + eval_size))
        
        print(f"📊 Train: {len(train_dataset)}, Eval: {len(eval_dataset)}")
        
        # Configurar training args
        training_args = self.setup_training_args()
        
        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False  # Causal LM, no masked LM
        )
        
        # Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            data_collator=data_collator,
            tokenizer=self.tokenizer,
        )
        
        # Entrenar
        print("⏳ Entrenando modelo...")
        trainer.train()
        
        # Guardar modelo
        print("💾 Guardando modelo entrenado...")
        trainer.save_model()
        self.tokenizer.save_pretrained(training_args.output_dir)
        
        print("✅ Entrenamiento completado!")
        
    def test_model(self, test_questions: list = None):
        """Probar el modelo entrenado"""
        if test_questions is None:
            test_questions = [
                "¿Qué es una licitación pública?",
                "¿Cuáles son los tipos de procedimientos de compra?",
                "¿Qué documentos se requieren para licitar?",
                "¿Cuáles son los montos para licitación pública?"
            ]
        
        print("\n🧪 Probando modelo entrenado:")
        print("=" * 50)
        
        for question in test_questions:
            prompt = f"Sistema: Eres un experto en compras públicas de Chile. Responde basándote únicamente en la legislación chilena.\nUsuario: {question}\nAsistente:"
            
            inputs = self.tokenizer.encode(prompt, return_tensors="pt")
            
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=inputs.shape[1] + 100,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            response = response.replace(prompt, "").strip()
            
            print(f"\n❓ Pregunta: {question}")
            print(f"🤖 Respuesta: {response}")
            print("-" * 30)
            
    def export_to_ollama_format(self, model_dir: str = "./compras-publicas-model"):
        """Crear Modelfile para Ollama"""
        modelfile_content = f"""FROM qwen2.5:0.5b

SYSTEM \"\"\"Eres un experto en compras públicas de Chile. Tu conocimiento se basa exclusivamente en la legislación chilena de compras públicas, incluyendo la Ley 19.886 y sus reglamentos.

Características de tus respuestas:
- Precisas y basadas únicamente en la legislación chilena
- Cita artículos específicos cuando sea relevante
- Usa terminología técnica apropiada
- Responde "No tengo información específica sobre ese tema" si la pregunta está fuera del ámbito de compras públicas chilenas
- Mantén un tono profesional y técnico\"\"\"

PARAMETER temperature 0.3
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER repeat_penalty 1.1
"""
        
        with open("Modelfile", 'w', encoding='utf-8') as f:
            f.write(modelfile_content)
            
        print("✅ Modelfile creado para Ollama")
        print("Para crear el modelo en Ollama ejecuta:")
        print("  ollama create compras-publicas-chile -f Modelfile")

def main():
    """Ejecutar fine-tuning"""
    print("🎯 Fine-tuning para Compras Públicas Chile")
    print("=" * 50)
    
    # Verificar si existe el dataset
    if not Path("compras_publicas_dataset.json").exists():
        print("❌ No se encontró compras_publicas_dataset.json")
        print("Ejecuta primero: python prepare_training_data.py")
        return
    
    # Inicializar fine-tuner
    finetuner = ComprasPublicasFineTuner()
    
    try:
        # Cargar modelo base
        finetuner.load_model_and_tokenizer()
        
        # Cargar dataset
        finetuner.load_dataset()
        
        # Tokenizar
        finetuner.tokenize_dataset()
        
        # Entrenar
        finetuner.train()
        
        # Probar modelo
        finetuner.test_model()
        
        # Crear Modelfile para Ollama
        finetuner.export_to_ollama_format()
        
        print("\n🎉 Fine-tuning completado exitosamente!")
        
    except Exception as e:
        print(f"❌ Error durante el fine-tuning: {e}")
        print("💡 Sugerencia: Usa un modelo más pequeño o reduce el batch size")

if __name__ == "__main__":
    main()