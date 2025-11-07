"""LLM interface for communicating with Ollama."""

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
        
        logger.info(f"LLM interface initialized with model: {self.model}")
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text response from LLM.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            
        Returns:
            Generated text response
        """
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
                    }
                )
                
                result = response["message"]["content"]
                logger.info("LLM response generated successfully")
                return result
                
            except Exception as e:
                logger.error(f"Error generating LLM response (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise
        
        return ""
    
    def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Generate JSON response from LLM.
        
        Args:
            prompt: User prompt requesting JSON output
            system_prompt: Optional system prompt
            
        Returns:
            Parsed JSON dictionary
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
            logger.debug(f"Response text: {response_text}")
            return {}
    
    def test_connection(self) -> bool:
        """Test connection to Ollama.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            logger.info("Testing Ollama connection...")
            response = ollama.list()
            models = [model["name"] for model in response.get("models", [])]
            
            if self.model in models:
                logger.info(f"Model {self.model} is available")
                return True
            else:
                logger.warning(f"Model {self.model} not found. Available models: {models}")
                return False
                
        except Exception as e:
            logger.error(f"Error testing Ollama connection: {e}")
            return False

