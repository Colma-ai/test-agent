#!/usr/bin/env python3
"""Generate test data for the test agent."""

import sys
import random
import sqlite3
from pathlib import Path
from datetime import datetime

def generate_test_data(test_id: str, num_items: int = 100):
    """Generate synthetic test data.

    Args:
        test_id: Unique test identifier
        num_items: Number of items to generate (default: 100)
    """

    db_path = Path(__file__).parent.parent / "db" / "test.db"

    if not db_path.exists():
        print(f"Error: Database not found at {db_path}")
        sys.exit(1)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Generate metrics
    metrics = [
        ("cpu_usage", random.uniform(10, 90)),
        ("memory_mb", random.uniform(100, 500)),
        ("duration_ms", random.uniform(1000, 5000)),
        ("items_processed", num_items),
        ("errors", 0),
        ("success_rate", 100.0)
    ]

    for metric_name, metric_value in metrics:
        cursor.execute("""
            INSERT INTO metrics (test_id, metric_name, metric_value)
            VALUES (?, ?, ?)
        """, [test_id, metric_name, metric_value])

    print(f"Generated {len(metrics)} metrics")

    # Generate items (for pagination testing)
    categories = ["Alpha", "Beta", "Gamma", "Delta"]

    for i in range(num_items):
        item_name = f"Item-{i+1:03d}"
        score = random.uniform(0, 100)
        category = random.choice(categories)

        cursor.execute("""
            INSERT INTO items (test_id, item_name, score, category)
            VALUES (?, ?, ?, ?)
        """, [test_id, item_name, score, category])

    print(f"Generated {num_items} items")

    # Generate chart data
    for category in categories:
        value = random.uniform(10, 100)
        cursor.execute("""
            INSERT INTO chart_data (test_id, label, value)
            VALUES (?, ?, ?)
        """, [test_id, category, value])

    print(f"Generated chart data for {len(categories)} categories")

    conn.commit()
    conn.close()

    print(f"✓ Test data generated successfully for test_id: {test_id}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 generate_data.py <test_id> [num_items]")
        sys.exit(1)

    test_id = sys.argv[1]
    num_items = int(sys.argv[2]) if len(sys.argv) > 2 else 100

    generate_test_data(test_id, num_items)
