"""Test AGI Assistant components without GUI (for Codespaces)."""

import sys
from pathlib import Path

print("=" * 60)
print("Testing AGI Assistant Components (Headless)")
print("=" * 60)
print()

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

# Test 1: Database
print("1. Testing Database...")
try:
    from src.storage.database import Database
    db = Database()
    print("   ✓ Database initialized")
    
    # Test adding a workflow
    test_workflow = {
        "name": "Test Workflow",
        "description": "Test description",
        "category": "test",
        "steps": [{"step_number": 1, "action_type": "click", "target": "100,100"}],
        "variables": [],
        "confidence": 0.85,
        "frequency": "manual",
        "estimated_savings": 60
    }
    workflow_id = db.add_workflow(test_workflow)
    print(f"   ✓ Workflow added with ID: {workflow_id}")
    
    # Get workflow back
    retrieved = db.get_workflow(workflow_id)
    print(f"   ✓ Workflow retrieved: {retrieved['name']}")
    
    # Clean up
    db.delete_workflow(workflow_id)
    print("   ✓ Workflow deleted")
    db.close()
    
except Exception as e:
    print(f"   ✗ Database error: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 2: LLM Interface
print("2. Testing LLM Interface (Ollama)...")
try:
    from src.intelligence.llm_interface import LLMInterface
    llm = LLMInterface()
    
    if llm.test_connection():
        print("   ✓ Ollama connection successful")
        
        # Test generation
        response = llm.generate("Say 'Hello from AGI Assistant!' and nothing else.")
        print(f"   ✓ LLM response: {response[:100]}...")
    else:
        print("   ✗ Ollama connection failed")
        
except Exception as e:
    print(f"   ✗ LLM error: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 3: Pattern Detection
print("3. Testing Pattern Detection...")
try:
    from src.intelligence.pattern_detector import PatternDetector
    detector = PatternDetector()
    
    # Create mock sessions
    session1 = {
        "session_id": "test1",
        "timeline": {
            "timeline": [
                {"type": "event", "event_type": "mouse_press", "data": {"x": 100, "y": 100}},
                {"type": "event", "event_type": "key_press", "data": {"key": "a"}},
            ]
        }
    }
    
    session2 = {
        "session_id": "test2",
        "timeline": {
            "timeline": [
                {"type": "event", "event_type": "mouse_press", "data": {"x": 105, "y": 102}},
                {"type": "event", "event_type": "key_press", "data": {"key": "a"}},
            ]
        }
    }
    
    patterns = detector.detect_patterns([session1, session2])
    print(f"   ✓ Pattern detector works. Found {len(patterns)} patterns")
    
except Exception as e:
    print(f"   ✗ Pattern detection error: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 4: Workflow Generator
print("4. Testing Workflow Generator...")
try:
    from src.intelligence.workflow_generator import WorkflowGenerator
    generator = WorkflowGenerator()
    
    # Create mock timeline
    mock_timeline = {
        "session_id": "test_session",
        "timeline": [
            {
                "timestamp": "2025-01-01T10:00:00",
                "type": "event",
                "event_type": "mouse_press",
                "data": {"x": 100, "y": 200}
            },
            {
                "timestamp": "2025-01-01T10:00:01",
                "type": "event",
                "event_type": "key_press",
                "data": {"key": "excel"}
            },
        ],
        "transcript": "Open Excel and create a new spreadsheet"
    }
    
    print("   ⏳ Generating workflow (this may take 10-30 seconds)...")
    workflow = generator.generate_workflow(mock_timeline)
    print(f"   ✓ Workflow generated: {workflow.get('workflow_name', 'Unnamed')}")
    print(f"   ✓ Steps: {len(workflow.get('steps', []))}")
    print(f"   ✓ Confidence: {workflow.get('confidence', 0):.2f}")
    
except Exception as e:
    print(f"   ✗ Workflow generation error: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 5: Storage Manager
print("5. Testing Storage Manager...")
try:
    from src.storage.storage_manager import StorageManager
    from src.storage.database import Database
    
    db = Database()
    storage = StorageManager(db)
    
    usage = storage.get_storage_usage()
    print(f"   ✓ Storage usage: {usage['total_size_mb']:.2f} MB")
    print(f"   ✓ Session count: {usage['session_count']}")
    print(f"   ✓ Usage: {usage['usage_percentage']:.1f}%")
    
    db.close()
    
except Exception as e:
    print(f"   ✗ Storage error: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print("Component Testing Complete!")
print("=" * 60)
print()
print("Note: GUI components (screen recording, automation) require")
print("a desktop environment and cannot be tested in Codespaces.")
print()
print("To run the full application:")
print("1. Clone this repo to your local Windows/Mac/Linux machine")
print("2. Install dependencies: pip install -r requirements.txt")
print("3. Install Tesseract OCR and Ollama")
print("4. Run: python main.py")