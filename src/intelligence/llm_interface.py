"""LLM interface for communicating with Ollama with robust error handling."""

import json
import time
from typing import Dict, Any, Optional
import ollama
from src.config import INTELLIGENCE_CONFIG
from src.logger import get_logger

logger = get_logger(__name__)


class LLMInterface:
    """Interface for communicating with Ollama LLM."""
    
    def __init__(self):
        """Initialize LLM interface."""
        self.config = INTELLIGENCE_CONFIG["ollama"]
        self.base_url = self.config["base_url"]
        self.model = self.config["model"]
        self.timeout = self.config["timeout"]
        self.max_retries = self.config["max_retries"]
        self.is_connected = False
        
        logger.info(f"LLM interface initialized with model: {self.model}")
        
        # Test connection on initialization
        self.is_connected = self.test_connection()
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text response from LLM.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            
        Returns:
            Generated text response or error message
        """
        if not self.is_connected:
            logger.warning("LLM not connected, attempting to reconnect...")
            self.is_connected = self.test_connection()
            if not self.is_connected:
                return self._generate_fallback_response(prompt)
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Generating response (attempt {attempt + 1}/{self.max_retries})")
                
                # Prepare messages
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                
                # Call Ollama API
                response = ollama.chat(
                    model=self.model,
                    messages=messages,
                    options={
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "num_predict": 2000,  # Max tokens
                    }
                )
                
                result = response["message"]["content"]
                logger.info("LLM response generated successfully")
                return result
                
            except ollama.ResponseError as e:
                logger.error(f"Ollama response error (attempt {attempt + 1}): {e}")
                if "model" in str(e).lower() and "not found" in str(e).lower():
                    logger.error(f"Model {self.model} not found. Please run: ollama pull {self.model}")
                    return self._generate_fallback_response(prompt)
                    
            except Exception as e:
                logger.error(f"Error generating LLM response (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error("Max retries reached, using fallback response")
                    return self._generate_fallback_response(prompt)
        
        return self._generate_fallback_response(prompt)
    
    def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Generate JSON response from LLM.
        
        Args:
            prompt: User prompt requesting JSON output
            system_prompt: Optional system prompt
            
        Returns:
            Parsed JSON dictionary or fallback dict
        """
        # Add JSON format instruction to prompt
        json_prompt = f"{prompt}\n\nIMPORTANT: Respond with valid JSON only. No markdown, no code blocks, just pure JSON."
        
        response_text = self.generate(json_prompt, system_prompt)
        
        # Try to extract JSON from response
        try:
            # Remove markdown code blocks if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            # Parse JSON
            return json.loads(response_text)
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response: {e}")
            logger.debug(f"Response text: {response_text[:500]}")
            
            # Return empty structure as fallback
            return self._generate_fallback_json()
    
    def test_connection(self) -> bool:
        """Test connection to Ollama.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            logger.info("Testing Ollama connection...")
            response = ollama.list()
            models = [model["name"] for model in response.get("models", [])]
            
            if self.model in models or any(self.model.split(':')[0] in m for m in models):
                logger.info(f"✅ Model {self.model} is available")
                return True
            else:
                logger.warning(f"⚠️ Model {self.model} not found. Available models: {models}")
                logger.warning(f"Please run: ollama pull {self.model}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error testing Ollama connection: {e}")
            logger.error("Make sure Ollama is installed and running:")
            logger.error("  1. Download from: https://ollama.ai/download")
            logger.error(f"  2. Run: ollama pull {self.model}")
            return False
    
    def _generate_fallback_response(self, prompt: str) -> str:
        """Generate a fallback response when LLM is unavailable.
        
        Args:
            prompt: Original prompt
            
        Returns:
            Fallback response string
        """
        logger.info("Using fallback response (LLM unavailable)")
        return "Unable to generate response. Please ensure Ollama is running and the phi3.5:mini model is installed."
    
    def _generate_fallback_json(self) -> Dict[str, Any]:
        """Generate a fallback JSON structure.
        
        Returns:
            Basic workflow structure
        """
        logger.info("Using fallback JSON structure (LLM unavailable)")
        return {
            "workflow_name": "Recorded Workflow",
            "description": "Workflow captured from user actions (LLM unavailable for analysis)",
            "confidence": 0.3,
            "category": "general",
            "estimated_time_manual": "60 seconds",
            "estimated_time_auto": "30 seconds",
            "steps": [],
            "variables": [],
            "triggers": ["manual"]
        }
    
    def is_available(self) -> bool:
        """Check if LLM is currently available.
        
        Returns:
            True if LLM is available
        """
        return self.is_connected