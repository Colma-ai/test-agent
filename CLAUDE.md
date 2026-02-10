# Test Agent

**Purpose:** Lightweight test agent for validating the production orchestration system.

**Duration:** ~30 seconds per run

**Cost:** ~$0.01 per run

---

## Overview

This agent generates synthetic test data and demonstrates all content block types used in the results API. It's designed for:
- Load testing the orchestration system (can spin up 10+ concurrent)
- Validating content block rendering in the frontend
- Testing pagination and lazy loading
- Verifying database extraction logic

---

## Workflow

### Step 1: Intake
Record test metadata to database:
- Test ID (from form submission)
- Timestamp
- Status: "running"

### Step 2: Generate Test Data
Create synthetic data for testing:
- 100 "items" with random scores (for pagination testing)
- 10 metrics with random values
- Sample chart data
- Sample markdown content

### Step 3: Complete
Mark test as complete and record final timestamp.

---

## Database Schema

**Location:** `db/test.db`

**Tables:**
```sql
-- Test metadata
CREATE TABLE tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_id TEXT UNIQUE NOT NULL,
    status TEXT NOT NULL,  -- "running", "complete"
    created_at TEXT NOT NULL,
    completed_at TEXT
);

-- Metrics (for metric grid blocks)
CREATE TABLE metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_id TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    FOREIGN KEY (test_id) REFERENCES tests(test_id)
);

-- Items (for paginated table blocks)
CREATE TABLE items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_id TEXT NOT NULL,
    item_name TEXT NOT NULL,
    score REAL NOT NULL,
    category TEXT NOT NULL,
    FOREIGN KEY (test_id) REFERENCES tests(test_id)
);

-- Chart data (for chart blocks)
CREATE TABLE chart_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_id TEXT NOT NULL,
    label TEXT NOT NULL,
    value REAL NOT NULL,
    FOREIGN KEY (test_id) REFERENCES tests(test_id)
);

-- Usage tracking
CREATE TABLE usage_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_id TEXT NOT NULL,
    step_name TEXT NOT NULL,
    model TEXT NOT NULL,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    estimated_cost_usd REAL,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (test_id) REFERENCES tests(test_id)
);
```

---

## Form Fields

**Required:**
- `test_id` (text) - Unique identifier for this test run

**Optional:**
- `num_items` (number, default: 100) - Number of items to generate
- `duration_seconds` (number, default: 30) - How long to simulate work

---

## Expected Results

### Content Blocks Returned

1. **Section Block** (summary)
   - Markdown text with bold, italic, links
   - Shows test completion status

2. **Divider** (visual separator)

3. **Metric Grid** (custom block)
   - 6 metrics with labels and values
   - CPU usage, memory, duration, etc.

4. **Context Block** (metadata)
   - Small text showing timestamps, cost

5. **Data Table** (custom block, paginated)
   - Initial 20 items shown
   - Link to `/api/results/{test_id}/items?page=2` for more
   - Sortable columns: Name, Score, Category

6. **Chart Block** (custom block)
   - Bar chart data (categories vs values)
   - Ready for Chart.js or similar

7. **Markdown Block** (custom block)
   - Multi-paragraph formatted text
   - Code blocks, lists, headings

8. **Action Buttons** (future - not implemented yet)
   - "Rerun Test" button
   - "Export Data" button

### Pagination Endpoints

- `GET /api/results/{test_id}/summary` - Initial blocks
- `GET /api/results/{test_id}/items?page=1&per_page=20` - Paginated items
- `GET /api/results/{test_id}/chart-data` - Full chart dataset

---

## Cost Estimate

- **Step 1 (Intake):** $0.002 (Haiku, simple DB write)
- **Step 2 (Generate Data):** $0.005 (Haiku, INSERT statements)
- **Step 3 (Complete):** $0.002 (Haiku, UPDATE statement)

**Total:** ~$0.01 per test run

**100 test runs:** ~$1.00

---

## Concurrent Testing

Safe to run many instances concurrently:
- Each test gets unique `test_id`
- No shared state (except database writes, which are serialized)
- Fast completion (30 seconds)
- Low cost ($0.01 each)

**Recommended test:**
```bash
# Submit 10 tests simultaneously
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/jobs \
    -H "Content-Type: application/json" \
    -d "{
      \"agent_type\": \"test\",
      \"form_data\": {
        \"test_id\": \"test-$i\",
        \"num_items\": 100
      }
    }" &
done
```

---

## Agent Instructions

When you receive a request to run a test:

1. **Extract parameters** from form data:
   - test_id (required)
   - num_items (default: 100)
   - duration_seconds (default: 30)

2. **Initialize database** (if first run):
   - Run `db/init_db.py` to create schema
   - Located at `db/test.db`

3. **Step 1: Intake**
   - INSERT into `tests` table:
     ```sql
     INSERT INTO tests (test_id, status, created_at)
     VALUES (?, 'running', datetime('now'))
     ```

4. **Step 2: Generate Test Data**

   a. Generate metrics:
   ```python
   metrics = [
       ("cpu_usage", random.uniform(10, 90)),
       ("memory_mb", random.uniform(100, 500)),
       ("duration_ms", random.uniform(1000, 5000)),
       ("items_processed", num_items),
       ("errors", 0),
       ("success_rate", 100.0)
   ]
   for name, value in metrics:
       INSERT INTO metrics (test_id, metric_name, metric_value)
       VALUES (?, ?, ?)
   ```

   b. Generate items (for pagination):
   ```python
   categories = ["Alpha", "Beta", "Gamma", "Delta"]
   for i in range(num_items):
       item_name = f"Item-{i+1:03d}"
       score = random.uniform(0, 100)
       category = random.choice(categories)
       INSERT INTO items (test_id, item_name, score, category)
       VALUES (?, ?, ?, ?)
   ```

   c. Generate chart data:
   ```python
   for category in categories:
       value = random.uniform(10, 100)
       INSERT INTO chart_data (test_id, label, value)
       VALUES (?, ?, ?)
   ```

   d. Sleep to simulate work:
   ```python
   import time
   time.sleep(duration_seconds)
   ```

5. **Step 3: Complete**
   - UPDATE tests table:
     ```sql
     UPDATE tests
     SET status = 'complete', completed_at = datetime('now')
     WHERE test_id = ?
     ```

6. **Log usage** (for cost tracking):
   ```sql
   INSERT INTO usage_log (test_id, step_name, model, prompt_tokens, completion_tokens, estimated_cost_usd, timestamp)
   VALUES (?, 'data_generation', 'claude-haiku-4-5', 100, 50, 0.005, datetime('now'))
   ```

7. **Report completion**:
   ```
   Test {test_id} completed successfully.
   - Generated {num_items} items
   - Created 6 metrics
   - Chart data ready
   - Duration: {duration_seconds}s
   - Cost: $0.01
   ```

---

## Verification

After running a test, verify:

```bash
# Check database
sqlite3 db/test.db "SELECT * FROM tests WHERE test_id = 'test-1'"

# Count items
sqlite3 db/test.db "SELECT COUNT(*) FROM items WHERE test_id = 'test-1'"

# Check metrics
sqlite3 db/test.db "SELECT * FROM metrics WHERE test_id = 'test-1'"

# Query via results API
curl http://localhost:8000/api/results/test-1/summary

# Paginated items
curl http://localhost:8000/api/results/test-1/items?page=1&per_page=20
```

Expected results:
- 1 test record (status: "complete")
- 100 items (or num_items specified)
- 6 metrics
- 4 chart data points
- Content blocks in summary response

---

## Troubleshooting

### Test hangs at "running"
- Check agent logs for errors
- Verify database is writable
- Check if sleep duration is too long

### No items returned
- Verify INSERT statements executed
- Check test_id matches in all tables
- Query database directly to confirm data exists

### Pagination not working
- Verify items table has data
- Check results API endpoint is registered
- Verify LIMIT/OFFSET in SQL query

---

## Settings

**File:** `.claude/settings.json`

```json
{
  "permissionMode": "acceptEdits",
  "allowedTools": {
    "bash": {
      "allowedCommands": [
        "python3 db/init_db.py",
        "sqlite3 db/test.db *",
        "sleep *"
      ]
    },
    "read": {
      "allowedPaths": [
        "db/*",
        "scripts/*",
        ".claude/*"
      ]
    },
    "write": {
      "allowedPaths": [
        "db/test.db"
      ]
    }
  }
}
```

---

## Notes

- This is a **test/development agent only** - not for production use
- Generates random data - not real analysis
- Safe to run many times (uses unique test_id)
- Fast completion makes it ideal for load testing
- Demonstrates all content block types for UI development
