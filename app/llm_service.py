# app/llm_service.py - Mock Only Version (No Downloads)
from typing import List, Dict, Any

class LLMService:
    """LLM service - Mock mode (no downloads required)"""
    
    def __init__(self, model_name: str = "mock"):
        self.model_name = model_name
        print("📝 Running in MOCK MODE - No LLM downloaded")
        print("   The system will use template responses")
    
    def generate_response(self, query: str, context: str, system_prompt: str = None) -> str:
        """Generate a mock response based on query and context."""
        
        if not context:
            return "No context available. Please upload a file first."
        
        # Simple response based on context
        context_preview = context[:500]
        
        return f"""📄 **Based on your documents:**

{context_preview}

💡 **Answer to: "{query}"**

The information above is extracted from your uploaded documents. 
For more detailed AI responses, you can:
1. Upgrade your system with more RAM
2. Use a smaller LLM like TinyLlama
3. Continue using mock mode for testing

✅ Your file processing and search functionality is fully working!
"""
    
    def generate_chat_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate a mock chat response."""
        last_query = messages[-1]["content"] if messages else ""
        return f"This is a mock response to: {last_query}\n\nYour system is working correctly in mock mode."
    
    def _mock_response(self, query: str, context: str) -> str:
        """Mock response helper."""
        return self.generate_response(query, context)