#!/usr/bin/env python3
"""Log usage after each tool use (hook)."""

import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime

def log_usage():
    """Log usage to database (called by hook)."""

    # This is a simplified version - in real implementation,
    # would parse hook payload to get actual token counts

    db_path = Path(__file__).parent.parent / "db" / "test.db"

    if not db_path.exists():
        return  # Database not initialized yet

    try:
        conn = sqlite3.connect(db_path)

        # Get latest test_id
        cursor = conn.cursor()
        cursor.execute("SELECT test_id FROM tests ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()

        if not row:
            return  # No tests yet

        test_id = row[0]

        # Log minimal usage (since this is test agent)
        cursor.execute("""
            INSERT INTO usage_log
            (test_id, step_name, model, prompt_tokens, completion_tokens, estimated_cost_usd, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [
            test_id,
            "tool_use",
            "claude-haiku-4-5",
            50,  # Minimal tokens for test agent
            25,
            0.001,  # Very low cost
            datetime.now().isoformat()
        ])

        conn.commit()
        conn.close()

    except Exception as e:
        # Silently fail - don't break agent execution
        pass

if __name__ == "__main__":
    log_usage()
