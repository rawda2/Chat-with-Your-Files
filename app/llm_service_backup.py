# app/llm_service.py
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
from typing import List, Dict, Any

class LLMService:
    """LLM service using Hugging Face."""
    
    def __init__(self, model_name: str = "HuggingFaceH4/zephyr-7b-beta"):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self._load_model()
    
    def _load_model(self):
        """Load the local or Hugging Face model."""
        try:
            print(f"🔄 Loading model: {self.model_name}")
            print("⚠️ This may take some time on first run...")
            
            # Use smaller model for speed (fallback)
            smaller_model = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"            
            self.tokenizer = AutoTokenizer.from_pretrained(
                smaller_model,
                trust_remote_code=True
            )
            
            self.model = AutoModelForCausalLM.from_pretrained(
                smaller_model,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None,
                trust_remote_code=True
            )
            
            # Create pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                max_new_tokens=512,
                do_sample=True,
                temperature=0.7,
                top_p=0.95
            )
            
            print(f"✅ Model loaded successfully")
            
        except Exception as e:
            print(f"⚠️ Model loading error: {e}")
            print("📝 Will use mock mode (simulation)")
            self.pipeline = None
    
    def generate_response(self, query: str, context: str, system_prompt: str = None) -> str:
        """Generate a response based on query and context."""
        
        # Default system prompt
        if not system_prompt:
            system_prompt = """You are an intelligent assistant specialized in answering questions based on provided documents.
            Answer accurately using only the information present in the context.
            If the information is not available in the context, say "There is not enough information to answer this question."
            Be helpful and clear in your answers."""
        
        # Build the prompt
        prompt = f"""<|system|>
{system_prompt}
<|user|>
Context:
{context}

Question: {query}

<|assistant|>
"""
        
        # If model is available, use it
        if self.pipeline:
            try:
                response = self.pipeline(
                    prompt,
                    max_new_tokens=512,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.95
                )
                
                generated_text = response[0]['generated_text']
                # Extract the part after assistant
                answer = generated_text.split("<|assistant|>")[-1].strip()
                return answer if answer else "Sorry, I couldn't generate an answer."
                
            except Exception as e:
                print(f"⚠️ Generation error: {e}")
                return self._mock_response(query, context)
        
        # Mock mode (when model is not available)
        return self._mock_response(query, context)
    
    def _mock_response(self, query: str, context: str) -> str:
        """Mock response when model is unavailable (for testing)."""
        return f"""📝 Received your question: "{query}"

🔍 Based on available information in the documents:

{context[:500] if context else "No context available"}

💡 Note: The system is currently running in mock mode. To use the real model, please install the required model with sufficient resources.
"""
    
    def generate_chat_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate a response from a complete conversation."""
        prompt = ""
        for msg in messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            prompt += f"{role}: {msg['content']}\n"
        prompt += "Assistant: "
        
        if self.pipeline:
            response = self.pipeline(prompt, max_new_tokens=512)
            return response[0]['generated_text'].split("Assistant:")[-1].strip()
        
        return "This is a test response from mock mode."