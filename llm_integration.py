"""
Advanced LLM Integration for AGI Assistant
Enhanced version with better error handling, multiple LLM support, and fallback options
"""

import json
import subprocess
import requests
from pathlib import Path
from datetime import datetime
import time

class LLMWorkflowAnalyzer:
    """Enhanced workflow analyzer using local LLM with fallback options"""
    
    def __init__(self, model="llama3.2:latest", log_callback=None):
        self.model = model
        self.ollama_url = "http://localhost:11434/api/generate"
        self.ollama_available = False
        self.log_callback = log_callback
        self.timeout = 60  # Increased timeout for LLM responses
        
        self.check_ollama()
        
    def log(self, message):
        """Send log messages to GUI or console"""
        if self.log_callback:
            self.log_callback(message)
        print(message)
    
    def check_ollama(self):
        """Check if Ollama is running and available"""
        try:
            response = requests.get(
                "http://localhost:11434/api/tags",
                timeout=5
            )
            if response.status_code == 200:
                models = response.json()
                available_models = [m.get('name', '') for m in models.get('models', [])]
                
                if available_models:
                    self.log(f"✅ Ollama is running with {len(available_models)} model(s)")
                    self.log(f"   Available models: {', '.join(available_models[:3])}")
                    
                    # Check if requested model is available
                    if self.model in available_models:
                        self.log(f"✅ Model '{self.model}' is ready")
                        self.ollama_available = True
                    else:
                        self.log(f"⚠️ Model '{self.model}' not found")
                        self.log(f"   Run: ollama pull {self.model}")
                        # Try to use first available model
                        if available_models:
                            self.model = available_models[0]
                            self.log(f"   Using '{self.model}' instead")
                            self.ollama_available = True
                else:
                    self.log("⚠️ Ollama running but no models installed")
                    self.log("   Install a model: ollama pull llama3.2")
                return self.ollama_available
                
        except requests.exceptions.ConnectionError:
            self.log("⚠️ Ollama not running. Start it or install from: https://ollama.ai")
            self.log("   Falling back to keyword-based analysis")
            return False
        except requests.exceptions.Timeout:
            self.log("⚠️ Ollama connection timeout")
            return False
        except Exception as e:
            self.log(f"⚠️ Ollama check failed: {e}")
            return False
    
    def analyze_with_llm(self, screenshots_text, transcriptions):
        """Use LLM to analyze user behavior with enhanced prompting"""
        
        if not self.ollama_available:
            self.log("❌ LLM not available, using fallback analysis")
            return None
        
        # Prepare context with better formatting
        context = self._build_analysis_prompt(screenshots_text, transcriptions)
        
        self.log("🤖 Analyzing workflows with LLM...")
        
        # Call Ollama with proper error handling
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model,
                    "prompt": context,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,  # More deterministic
                        "top_p": 0.9,
                        "num_predict": 500  # Limit response length
                    }
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                llm_output = result.get("response", "")
                
                if not llm_output:
                    self.log("⚠️ LLM returned empty response")
                    return None
                
                self.log("✅ LLM analysis complete")
                
                # Extract and validate JSON from response
                workflow_data = self._extract_json(llm_output)
                
                if workflow_data and self._validate_workflow(workflow_data):
                    return workflow_data
                else:
                    self.log("⚠️ LLM response invalid or incomplete")
                    return None
                    
            elif response.status_code == 404:
                self.log(f"❌ Model '{self.model}' not found. Run: ollama pull {self.model}")
                return None
            else:
                self.log(f"❌ LLM Error: HTTP {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            self.log(f"⏱️ LLM request timed out after {self.timeout}s")
            return None
        except requests.exceptions.ConnectionError:
            self.log("❌ Lost connection to Ollama")
            self.ollama_available = False
            return None
        except Exception as e:
            self.log(f"❌ LLM Analysis Error: {e}")
            return None
    
    def _build_analysis_prompt(self, screenshots_text, transcriptions):
        """Build enhanced analysis prompt with examples"""
        
        # Limit data to prevent token overflow
        max_items = 10
        screen_data = "\n".join(
            f"• {text[:300]}" 
            for text in screenshots_text[:max_items] 
            if text.strip()
        )
        
        audio_data = "\n".join(
            f"• {text[:200]}" 
            for text in transcriptions[:max_items] 
            if text.strip()
        )
        
        # Build comprehensive prompt
        prompt = f"""You are analyzing a user's desktop activity to identify automatable workflows.

CAPTURED DATA:

Screen Activity (OCR text from screenshots):
{screen_data if screen_data else "No screen text captured"}

Voice Commands (Audio transcriptions):
{audio_data if audio_data else "No voice commands captured"}

ANALYSIS TASK:
Based on the captured data, identify:
1. What specific workflow is the user performing?
2. What are the repetitive, automatable steps?
3. What actions should be automated in sequence?
4. How confident are you in this detection?

EXAMPLES OF WORKFLOWS:
- Excel data entry: Open Excel → Navigate to cell → Enter data → Apply formula → Save
- Web research: Open browser → Search Google → Click results → Copy information → Save to document
- Email workflow: Open email client → Compose → Add recipients → Type message → Send
- File organization: Open folder → Select files → Rename → Move to destination

RESPONSE FORMAT (JSON only, no other text):
{{
  "workflow_name": "Brief descriptive name",
  "description": "Clear description of what user is doing",
  "detected_steps": ["Step 1", "Step 2", "Step 3"],
  "automation_actions": ["Action 1", "Action 2", "Action 3"],
  "categories": ["category1", "category2"],
  "confidence": "high|medium|low",
  "reasoning": "Why you detected this pattern"
}}

IMPORTANT:
- Only return valid JSON, nothing else
- Be specific in detected_steps and automation_actions
- Use clear, actionable language
- Set confidence based on data quality and clarity
- If data is insufficient, set confidence to "low"

ANALYZE NOW:"""
        
        return prompt
    
    def _extract_json(self, text):
        """Extract and parse JSON from LLM response with multiple strategies"""
        
        # Strategy 1: Look for JSON in markdown code blocks
        if "```json" in text:
            try:
                start = text.find("```json") + 7
                end = text.find("```", start)
                json_str = text[start:end].strip()
                return json.loads(json_str)
            except (json.JSONDecodeError, ValueError) as e:
                self.log(f"Failed to parse JSON from markdown block: {e}")
        
        # Strategy 2: Look for JSON in plain code blocks
        if "```" in text:
            try:
                start = text.find("```") + 3
                end = text.find("```", start)
                json_str = text[start:end].strip()
                # Remove language identifier if present
                if json_str.startswith(('json', 'JSON')):
                    json_str = json_str[4:].strip()
                return json.loads(json_str)
            except (json.JSONDecodeError, ValueError):
                pass
        
        # Strategy 3: Look for raw JSON
        if "{" in text and "}" in text:
            try:
                start = text.find("{")
                end = text.rfind("}") + 1
                json_str = text[start:end]
                return json.loads(json_str)
            except (json.JSONDecodeError, ValueError) as e:
                self.log(f"Failed to parse raw JSON: {e}")
        
        # Strategy 4: Try parsing entire response
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            pass
        
        self.log("❌ Could not extract valid JSON from LLM response")
        return None
    
    def _validate_workflow(self, workflow_data):
        """Validate workflow data structure"""
        required_fields = [
            'workflow_name',
            'description',
            'detected_steps',
            'automation_actions',
            'confidence'
        ]
        
        try:
            # Check all required fields exist
            for field in required_fields:
                if field not in workflow_data:
                    self.log(f"⚠️ Missing required field: {field}")
                    return False
            
            # Validate field types
            if not isinstance(workflow_data['detected_steps'], list):
                self.log("⚠️ detected_steps must be a list")
                return False
            
            if not isinstance(workflow_data['automation_actions'], list):
                self.log("⚠️ automation_actions must be a list")
                return False
            
            # Check for content
            if not workflow_data['detected_steps']:
                self.log("⚠️ No detected steps in workflow")
                return False
            
            if not workflow_data['automation_actions']:
                self.log("⚠️ No automation actions in workflow")
                return False
            
            # Validate confidence value
            valid_confidence = ['high', 'medium', 'low']
            if workflow_data['confidence'].lower() not in valid_confidence:
                workflow_data['confidence'] = 'medium'  # Default
            
            return True
            
        except Exception as e:
            self.log(f"⚠️ Workflow validation error: {e}")
            return False
    
    def _format_list(self, items):
        """Format list items for prompt with length limit"""
        if not items:
            return "None"
        return "\n".join(f"- {str(item)[:200]}" for item in items if str(item).strip())
    
    def generate_workflow_suggestion(self, analysis_result):
        """Generate human-readable workflow suggestion with enhanced formatting"""
        
        if not analysis_result:
            return "❌ No clear workflow detected yet. Continue observing to gather more data."
        
        suggestion_parts = [
            "=" * 70,
            f"🎯 Detected Workflow: {analysis_result.get('workflow_name', 'Unknown')}",
            "=" * 70,
            "",
            "📝 Description:",
            f"   {analysis_result.get('description', 'No description available')}",
            ""
        ]
        
        # Add reasoning if available
        if 'reasoning' in analysis_result:
            suggestion_parts.extend([
                "🧠 Detection Reasoning:",
                f"   {analysis_result.get('reasoning')}",
                ""
            ])
        
        # Add detected steps
        steps = analysis_result.get('detected_steps', [])
        if steps:
            suggestion_parts.extend([
                f"🔄 Observed Steps ({len(steps)}):"
            ])
            for i, step in enumerate(steps, 1):
                suggestion_parts.append(f"   {i}. {step}")
            suggestion_parts.append("")
        
        # Add automation actions
        actions = analysis_result.get('automation_actions', [])
        if actions:
            suggestion_parts.extend([
                f"⚡ Proposed Automation ({len(actions)} actions):"
            ])
            for i, action in enumerate(actions, 1):
                suggestion_parts.append(f"   ✓ {action}")
            suggestion_parts.append("")
        
        # Add categories if available
        categories = analysis_result.get('categories', [])
        if categories:
            suggestion_parts.extend([
                f"📂 Categories: {', '.join(categories)}",
                ""
            ])
        
        # Add confidence
        confidence = analysis_result.get('confidence', 'unknown').upper()
        confidence_emoji = {
            'HIGH': '🟢',
            'MEDIUM': '🟡',
            'LOW': '🔴'
        }.get(confidence, '⚪')
        
        suggestion_parts.extend([
            f"📊 Confidence: {confidence_emoji} {confidence}",
            "=" * 70
        ])
        
        return "\n".join(suggestion_parts)


class EnhancedWorkflowAnalyzer:
    """Workflow analyzer with LLM support and fallback options"""
    
    def __init__(self, use_llm=True, log_callback=None):
        self.use_llm = use_llm
        self.log_callback = log_callback
        self.llm_analyzer = None
        
        if use_llm:
            try:
                self.llm_analyzer = LLMWorkflowAnalyzer(log_callback=log_callback)
            except Exception as e:
                self.log(f"⚠️ Could not initialize LLM analyzer: {e}")
                self.use_llm = False
    
    def log(self, message):
        """Send log messages to GUI or console"""
        if self.log_callback:
            self.log_callback(message)
        print(message)
        
    def analyze(self):
        """Analyze with optional LLM enhancement and fallback"""
        
        # Get recent OCR texts
        ocr_files = sorted(Path("agi_data").glob("ocr_*.txt"))[-15:]  # Increased to 15
        ocr_texts = []
        for file in ocr_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    text = f.read()
                    if text.strip():
                        ocr_texts.append(text)
            except Exception as e:
                self.log(f"Error reading {file.name}: {e}")
        
        # Get recent transcriptions
        transcript_files = sorted(Path("agi_data").glob("transcript_*.txt"))[-15:]
        transcripts = []
        for file in transcript_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    text = f.read()
                    if text.strip():
                        transcripts.append(text)
            except Exception as e:
                self.log(f"Error reading {file.name}: {e}")
        
        # Check if we have enough data
        if not ocr_texts and not transcripts:
            return "ℹ️ No data collected yet. Start observing to detect workflows."
        
        # Use LLM if available and data is sufficient
        if self.use_llm and self.llm_analyzer and (ocr_texts or transcripts):
            self.log("🤖 Using LLM-powered analysis...")
            result = self.llm_analyzer.analyze_with_llm(ocr_texts, transcripts)
            
            if result:
                suggestion = self.llm_analyzer.generate_workflow_suggestion(result)
                self._save_workflow(result)
                return suggestion
            else:
                self.log("⚠️ LLM analysis failed, using fallback method")
        
        # Fallback to keyword-based analysis
        self.log("📊 Using keyword-based analysis...")
        return self._basic_analysis(ocr_texts, transcripts)
    
    def _basic_analysis(self, ocr_texts, transcripts):
        """Enhanced keyword-based fallback analysis"""
        combined = " ".join(ocr_texts + transcripts).lower()
        
        # Enhanced pattern detection
        patterns = {
            "excel": {
                "keywords": ["excel", "spreadsheet", "cells", "formula", "workbook", "xlsx", "csv"],
                "actions": [
                    "Open Excel application",
                    "Navigate to specific cell range",
                    "Enter or paste data",
                    "Apply formulas or formatting",
                    "Save workbook"
                ]
            },
            "browser": {
                "keywords": ["chrome", "firefox", "safari", "edge", "browser", "search", "google", "url", "website", "web"],
                "actions": [
                    "Open web browser",
                    "Navigate to URL",
                    "Perform search query",
                    "Click on elements",
                    "Extract information"
                ]
            },
            "email": {
                "keywords": ["email", "outlook", "gmail", "compose", "send", "inbox", "mail", "message"],
                "actions": [
                    "Open email client",
                    "Compose new email",
                    "Add recipients",
                    "Type message content",
                    "Send email"
                ]
            },
            "file_management": {
                "keywords": ["folder", "file", "rename", "move", "copy", "delete", "explorer", "finder", "directory"],
                "actions": [
                    "Open file explorer",
                    "Navigate to folder",
                    "Select files",
                    "Rename or move files",
                    "Organize directory structure"
                ]
            },
            "document_editing": {
                "keywords": ["word", "document", "doc", "edit", "text", "paragraph", "typing", "write"],
                "actions": [
                    "Open document editor",
                    "Create or open document",
                    "Type and format content",
                    "Save document"
                ]
            }
        }
        
        # Detect matching patterns
        detected_patterns = []
        for category, config in patterns.items():
            matches = sum(1 for kw in config["keywords"] if kw in combined)
            if matches >= 2:  # Need at least 2 keyword matches
                detected_patterns.append((category, matches, config["actions"]))
        
        if not detected_patterns:
            return self._generate_basic_suggestion(None, ocr_texts, transcripts)
        
        # Sort by number of matches
        detected_patterns.sort(key=lambda x: x[1], reverse=True)
        primary_pattern = detected_patterns[0]
        
        # Build workflow data
        workflow_data = {
            "workflow_name": f"{primary_pattern[0].replace('_', ' ').title()} Workflow",
            "description": f"Detected {primary_pattern[0].replace('_', ' ')} activity",
            "detected_steps": [f"User performed {primary_pattern[0].replace('_', ' ')} tasks"],
            "automation_actions": primary_pattern[2],
            "categories": [p[0] for p in detected_patterns],
            "confidence": "medium" if primary_pattern[1] >= 3 else "low",
            "timestamp": datetime.now().isoformat(),
            "data_points": len(ocr_texts) + len(transcripts)
        }
        
        # Save and return
        self._save_workflow(workflow_data)
        return self._generate_basic_suggestion(workflow_data, ocr_texts, transcripts)
    
    def _generate_basic_suggestion(self, workflow_data, ocr_texts, transcripts):
        """Generate suggestion from basic analysis"""
        
        if not workflow_data:
            return f"""ℹ️ Continue observing to detect clear patterns...

📊 Data Collected:
   • Screenshots with text: {len(ocr_texts)}
   • Voice transcriptions: {len(transcripts)}

💡 Tips for better detection:
   • Perform tasks step-by-step
   • Speak commands while working
   • Repeat workflows 2-3 times
   • Observe for 2-3 minutes minimum"""
        
        suggestion_parts = [
            "=" * 70,
            f"🎯 Detected: {workflow_data['workflow_name']}",
            "=" * 70,
            "",
            f"📝 {workflow_data['description']}",
            "",
            f"⚡ Suggested Actions ({len(workflow_data['automation_actions'])}):"
        ]
        
        for i, action in enumerate(workflow_data['automation_actions'], 1):
            suggestion_parts.append(f"   {i}. {action}")
        
        suggestion_parts.extend([
            "",
            f"📊 Confidence: {workflow_data['confidence'].upper()}",
            f"📂 Categories: {', '.join(workflow_data['categories'])}",
            f"📈 Data Points: {workflow_data.get('data_points', 0)}",
            "",
            "💡 Note: This is keyword-based detection. For better accuracy,",
            "   install Ollama and use LLM-powered analysis.",
            "=" * 70
        ])
        
        return "\n".join(suggestion_parts)
    
    def _save_workflow(self, workflow_data):
        """Save workflow to JSON with error handling"""
        try:
            workflow_dir = Path("agi_data/workflows")
            workflow_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = workflow_dir / f"workflow_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(workflow_data, f, indent=2, ensure_ascii=False)
            
            self.log(f"💾 Workflow saved: {filename.name}")
            
        except Exception as e:
            self.log(f"⚠️ Failed to save workflow: {e}")


# ===== INTEGRATION GUIDE =====

"""
HOW TO INTEGRATE INTO MAIN APPLICATION:

1. Replace WorkflowAnalyzer import in agi_assistant_main.py:
   
   from llm_integration import EnhancedWorkflowAnalyzer

2. Initialize with LLM support:
   
   self.workflow_analyzer = EnhancedWorkflowAnalyzer(
       use_llm=True,  # Set to False to use only keyword-based
       log_callback=self.log
   )

3. Use in analyze_workflows method:
   
   def analyze_workflows(self):
       self.log("🔍 Analyzing workflows...")
       result = self.workflow_analyzer.analyze()
       self.log(result)

4. Install Ollama (optional but recommended):
   
   # Download from: https://ollama.ai
   # Install and start service
   # Pull a model:
   ollama pull llama3.2
   # Or smaller models:
   ollama pull phi3
   ollama pull mistral

5. The analyzer will automatically:
   - Try LLM analysis if Ollama is available
   - Fall back to keyword-based if LLM fails
   - Show helpful messages about what's available
   - Work even without any LLM installed
"""

# ===== TESTING =====

if __name__ == "__main__":
    print("=" * 70)
    print("🤖 LLM Integration Test")
    print("=" * 70)
    
    # Test with mock data
    mock_ocr = [
        "Microsoft Excel - Quarterly Report",
        "Cell A1: Revenue, Cell B1: 15000",
        "Save file as Q4_Report.xlsx"
    ]
    
    mock_transcripts = [
        "Open Excel",
        "Enter revenue data",
        "Save the file"
    ]
    
    analyzer = EnhancedWorkflowAnalyzer(use_llm=True)
    
    print("\n📊 Analyzing mock data...")
    result = analyzer.analyze()
    print("\n" + result)
