"""
Advanced LLM Integration for AGI Assistant
Uses Ollama with Llama 3.2 for intelligent workflow understanding
"""

import json
import subprocess
import requests
from pathlib import Path

class LLMWorkflowAnalyzer:
    """Enhanced workflow analyzer using local LLM"""
    
    def __init__(self, model="llama3.2:latest"):
        self.model = model
        self.ollama_url = "http://localhost:11434/api/generate"
        self.check_ollama()
        
    def check_ollama(self):
        """Check if Ollama is running"""
        try:
            response = requests.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                print("✅ Ollama is running")
                return True
        except:
            print("⚠️ Ollama not detected. Install from: https://ollama.ai")
            print("   Then run: ollama pull llama3.2")
            return False
    
    def analyze_with_llm(self, screenshots_text, transcriptions):
        """Use LLM to analyze user behavior"""
        
        # Prepare context
        context = f"""You are analyzing a user's desktop activity to identify automatable workflows.

Screen Activity (OCR from screenshots):
{self._format_list(screenshots_text)}

User Commands (Audio transcriptions):
{self._format_list(transcriptions)}

Based on this data, identify:
1. What workflow is the user performing?
2. What are the repetitive steps?
3. What actions should be automated?

Respond in JSON format:
{{
  "workflow_name": "Short name",
  "description": "What the user is doing",
  "detected_steps": ["Step 1", "Step 2", ...],
  "automation_actions": ["Action 1", "Action 2", ...],
  "confidence": "high/medium/low"
}}
"""
        
        # Call Ollama
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model,
                    "prompt": context,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                llm_output = result.get("response", "")
                
                # Extract JSON from response
                return self._extract_json(llm_output)
            else:
                print(f"LLM Error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"LLM Analysis Error: {e}")
            return None
    
    def _format_list(self, items):
        """Format list items for prompt"""
        return "\n".join(f"- {item[:200]}" for item in items if item.strip())
    
    def _extract_json(self, text):
        """Extract JSON from LLM response"""
        try:
            # Try to find JSON in markdown code blocks
            if "```json" in text:
                start = text.find("```json") + 7
                end = text.find("```", start)
                json_str = text[start:end].strip()
            elif "{" in text and "}" in text:
                start = text.find("{")
                end = text.rfind("}") + 1
                json_str = text[start:end]
            else:
                return None
            
            return json.loads(json_str)
        except:
            return None
    
    def generate_workflow_suggestion(self, analysis_result):
        """Generate human-readable workflow suggestion"""
        if not analysis_result:
            return "No clear workflow detected yet. Continue observing."
        
        suggestion = f"""
🎯 Detected Workflow: {analysis_result.get('workflow_name', 'Unknown')}

📝 Description:
{analysis_result.get('description', 'No description')}

🔄 Observed Steps:
"""
        for step in analysis_result.get('detected_steps', []):
            suggestion += f"  • {step}\n"
        
        suggestion += "\n⚡ Proposed Automation:\n"
        for action in analysis_result.get('automation_actions', []):
            suggestion += f"  ✓ {action}\n"
        
        confidence = analysis_result.get('confidence', 'unknown')
        suggestion += f"\n📊 Confidence: {confidence.upper()}\n"
        
        return suggestion

# Example integration into WorkflowAnalyzer class
class EnhancedWorkflowAnalyzer:
    """Workflow analyzer with LLM support"""
    
    def __init__(self, use_llm=True):
        self.use_llm = use_llm
        if use_llm:
            self.llm_analyzer = LLMWorkflowAnalyzer()
        
    def analyze(self):
        """Analyze with optional LLM enhancement"""
        from pathlib import Path
        
        # Get recent OCR texts
        ocr_files = sorted(Path("agi_data").glob("ocr_*.txt"))[-10:]
        ocr_texts = []
        for file in ocr_files:
            with open(file, 'r', encoding='utf-8') as f:
                text = f.read()
                if text.strip():
                    ocr_texts.append(text)
        
        # Get recent transcriptions
        transcript_files = sorted(Path("agi_data").glob("transcript_*.txt"))[-10:]
        transcripts = []
        for file in transcript_files:
            with open(file, 'r', encoding='utf-8') as f:
                text = f.read()
                if text.strip():
                    transcripts.append(text)
        
        # Use LLM if available
        if self.use_llm and (ocr_texts or transcripts):
            result = self.llm_analyzer.analyze_with_llm(ocr_texts, transcripts)
            if result:
                suggestion = self.llm_analyzer.generate_workflow_suggestion(result)
                self._save_workflow(result)
                return suggestion
        
        # Fallback to keyword-based analysis
        return self._basic_analysis(ocr_texts, transcripts)
    
    def _basic_analysis(self, ocr_texts, transcripts):
        """Simple keyword-based fallback"""
        combined = " ".join(ocr_texts + transcripts).lower()
        
        if "excel" in combined:
            return "Detected: Excel workflow - Consider automating data entry"
        elif "chrome" in combined or "browser" in combined:
            return "Detected: Browser activity - Consider automating web searches"
        else:
            return "Continue observing to detect patterns..."
    
    def _save_workflow(self, workflow_data):
        """Save workflow to JSON"""
        from datetime import datetime
        
        workflow_dir = Path("agi_data/workflows")
        workflow_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = workflow_dir / f"workflow_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(workflow_data, f, indent=2)

# How to use in main app:
# Replace WorkflowAnalyzer with EnhancedWorkflowAnalyzer
# In the GUI, when clicking "Analyze Workflows":
"""
analyzer = EnhancedWorkflowAnalyzer(use_llm=True)
result = analyzer.analyze()
self.log(result)
"""

# Installation instructions for users:
"""
# Install Ollama:
# 1. Download from https://ollama.ai
# 2. Install and start the service
# 3. Pull the model:
ollama pull llama3.2

# Or use alternative models:
ollama pull phi3
ollama pull mistral
"""