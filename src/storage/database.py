"""SQLite database for workflows, sessions, and execution logs."""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any
from src.config import DB_PATH
from src.logger import get_logger

logger = get_logger(__name__)


class Database:
    """Database manager for workflows and sessions."""
    
    def __init__(self, db_path: Path = DB_PATH):
        """Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Create database tables if they don't exist."""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row  # Access columns by name
        
        cursor = self.conn.cursor()
        
        # Workflows table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workflows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                category TEXT,
                steps JSON NOT NULL,
                variables JSON,
                confidence REAL,
                frequency TEXT,
                estimated_savings INTEGER,
                times_run INTEGER DEFAULT 0,
                times_succeeded INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_run TIMESTAMP,
                last_modified TIMESTAMP
            )
        """)
        
        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                duration INTEGER,
                screenshots_count INTEGER,
                audio_clips_count INTEGER,
                events_count INTEGER,
                learned_workflow_id INTEGER,
                storage_size INTEGER,
                deleted BOOLEAN DEFAULT 0,
                deleted_at TIMESTAMP,
                FOREIGN KEY (learned_workflow_id) REFERENCES workflows(id)
            )
        """)
        
        # Execution logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS execution_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_id INTEGER NOT NULL,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                success BOOLEAN,
                steps_completed INTEGER,
                steps_total INTEGER,
                error_message TEXT,
                execution_time INTEGER,
                FOREIGN KEY (workflow_id) REFERENCES workflows(id)
            )
        """)
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_workflow_frequency 
            ON workflows(frequency)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_session_learned 
            ON sessions(learned_workflow_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_execution_workflow 
            ON execution_logs(workflow_id)
        """)
        
        self.conn.commit()
        logger.info(f"Database initialized at {self.db_path}")
    
    def add_workflow(self, workflow_data: Dict[str, Any]) -> int:
        """Add a new workflow to the database.
        
        Args:
            workflow_data: Dictionary containing workflow information
            
        Returns:
            ID of the created workflow
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO workflows (
                name, description, category, steps, variables,
                confidence, frequency, estimated_savings
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            workflow_data.get("name"),
            workflow_data.get("description"),
            workflow_data.get("category"),
            json.dumps(workflow_data.get("steps", [])),
            json.dumps(workflow_data.get("variables", [])),
            workflow_data.get("confidence", 0.0),
            workflow_data.get("frequency", "manual"),
            workflow_data.get("estimated_savings", 0)
        ))
        
        self.conn.commit()
        workflow_id = cursor.lastrowid
        logger.info(f"Added workflow: {workflow_data.get('name')} (ID: {workflow_id})")
        return workflow_id
    
    def get_workflow(self, workflow_id: int) -> Optional[Dict[str, Any]]:
        """Get a workflow by ID.
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            Workflow dictionary or None if not found
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM workflows WHERE id = ?", (workflow_id,))
        row = cursor.fetchone()
        
        if row:
            return self._row_to_dict(row)
        return None
    
    def get_all_workflows(self) -> List[Dict[str, Any]]:
        """Get all workflows.
        
        Returns:
            List of workflow dictionaries
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM workflows ORDER BY created_at DESC")
        return [self._row_to_dict(row) for row in cursor.fetchall()]
    
    def update_workflow(self, workflow_id: int, updates: Dict[str, Any]):
        """Update a workflow.
        
        Args:
            workflow_id: Workflow ID
            updates: Dictionary of fields to update
        """
        cursor = self.conn.cursor()
        
        # Build update query dynamically
        fields = []
        values = []
        
        if "steps" in updates:
            fields.append("steps = ?")
            values.append(json.dumps(updates["steps"]))
        if "variables" in updates:
            fields.append("variables = ?")
            values.append(json.dumps(updates["variables"]))
        if "name" in updates:
            fields.append("name = ?")
            values.append(updates["name"])
        if "description" in updates:
            fields.append("description = ?")
            values.append(updates["description"])
        if "confidence" in updates:
            fields.append("confidence = ?")
            values.append(updates["confidence"])
        
        fields.append("last_modified = ?")
        values.append(datetime.now().isoformat())
        values.append(workflow_id)
        
        query = f"UPDATE workflows SET {', '.join(fields)} WHERE id = ?"
        cursor.execute(query, values)
        self.conn.commit()
        logger.info(f"Updated workflow ID: {workflow_id}")
    
    def delete_workflow(self, workflow_id: int):
        """Delete a workflow.
        
        Args:
            workflow_id: Workflow ID
        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM workflows WHERE id = ?", (workflow_id,))
        self.conn.commit()
        logger.info(f"Deleted workflow ID: {workflow_id}")
    
    def add_session(self, session_data: Dict[str, Any]) -> int:
        """Add a new session.
        
        Args:
            session_data: Dictionary containing session information
            
        Returns:
            ID of the created session
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO sessions (
                session_id, start_time, end_time, duration,
                screenshots_count, audio_clips_count, events_count,
                storage_size, learned_workflow_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_data.get("session_id"),
            session_data.get("start_time"),
            session_data.get("end_time"),
            session_data.get("duration"),
            session_data.get("screenshots_count", 0),
            session_data.get("audio_clips_count", 0),
            session_data.get("events_count", 0),
            session_data.get("storage_size", 0),
            session_data.get("learned_workflow_id")
        ))
        
        self.conn.commit()
        session_id = cursor.lastrowid
        logger.info(f"Added session: {session_data.get('session_id')} (ID: {session_id})")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a session by session_id.
        
        Args:
            session_id: Session ID string
            
        Returns:
            Session dictionary or None if not found
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        
        if row:
            return self._row_to_dict(row)
        return None
    
    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """Get all sessions.
        
        Returns:
            List of session dictionaries
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM sessions ORDER BY start_time DESC")
        return [self._row_to_dict(row) for row in cursor.fetchall()]
    
    def log_execution(self, execution_data: Dict[str, Any]) -> int:
        """Log a workflow execution.
        
        Args:
            execution_data: Dictionary containing execution information
            
        Returns:
            ID of the created log entry
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO execution_logs (
                workflow_id, started_at, completed_at, success,
                steps_completed, steps_total, error_message, execution_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            execution_data.get("workflow_id"),
            execution_data.get("started_at"),
            execution_data.get("completed_at"),
            execution_data.get("success", False),
            execution_data.get("steps_completed", 0),
            execution_data.get("steps_total", 0),
            execution_data.get("error_message"),
            execution_data.get("execution_time", 0)
        ))
        
        # Update workflow stats
        if execution_data.get("success"):
            cursor.execute("""
                UPDATE workflows 
                SET times_succeeded = times_succeeded + 1,
                    times_run = times_run + 1,
                    last_run = ?
                WHERE id = ?
            """, (execution_data.get("completed_at"), execution_data.get("workflow_id")))
        else:
            cursor.execute("""
                UPDATE workflows 
                SET times_run = times_run + 1,
                    last_run = ?
                WHERE id = ?
            """, (execution_data.get("completed_at"), execution_data.get("workflow_id")))
        
        self.conn.commit()
        log_id = cursor.lastrowid
        logger.info(f"Logged execution for workflow ID: {execution_data.get('workflow_id')}")
        return log_id
    
    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert a database row to a dictionary.
        
        Args:
            row: SQLite row object
            
        Returns:
            Dictionary representation of the row
        """
        result = dict(row)
        
        # Parse JSON fields
        if "steps" in result and result["steps"]:
            result["steps"] = json.loads(result["steps"])
        if "variables" in result and result["variables"]:
            result["variables"] = json.loads(result["variables"])
        
        return result
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

