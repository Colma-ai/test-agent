#!/usr/bin/env python3
"""Initialize test agent database."""

import sqlite3
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent / "test.db"


def init_database():
    """Create all tables for test agent."""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create tests table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_id TEXT UNIQUE NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            completed_at TEXT
        )
    """)

    # Create metrics table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_id TEXT NOT NULL,
            metric_name TEXT NOT NULL,
            metric_value REAL NOT NULL,
            FOREIGN KEY (test_id) REFERENCES tests(test_id)
        )
    """)

    # Create items table (for pagination testing)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_id TEXT NOT NULL,
            item_name TEXT NOT NULL,
            score REAL NOT NULL,
            category TEXT NOT NULL,
            FOREIGN KEY (test_id) REFERENCES tests(test_id)
        )
    """)

    # Create chart_data table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chart_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_id TEXT NOT NULL,
            label TEXT NOT NULL,
            value REAL NOT NULL,
            FOREIGN KEY (test_id) REFERENCES tests(test_id)
        )
    """)

    # Create usage_log table (for cost tracking)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usage_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_id TEXT NOT NULL,
            step_name TEXT NOT NULL,
            model TEXT NOT NULL,
            prompt_tokens INTEGER,
            completion_tokens INTEGER,
            estimated_cost_usd REAL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (test_id) REFERENCES tests(test_id)
        )
    """)

    # Create indexes for performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tests_test_id ON tests(test_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_test_id ON metrics(test_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_test_id ON items(test_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_score ON items(score DESC)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_chart_test_id ON chart_data(test_id)")

    conn.commit()
    conn.close()

    print(f"Database initialized: {DB_PATH}")
    print(f"Database size: {DB_PATH.stat().st_size} bytes")


if __name__ == "__main__":
    init_database()
