# Test Agent

Lightweight test agent for validating the production orchestration system.

## Quick Start

### Local Testing

```bash
# Initialize database
python3 db/init_db.py

# Generate test data
python3 scripts/generate_data.py test-1 100

# Verify
sqlite3 db/test.db "SELECT COUNT(*) FROM items WHERE test_id = 'test-1'"
```

### Via Production API

```bash
# Submit job
curl -X POST http://localhost:8000/api/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "test",
    "form_data": {
      "test_id": "test-1",
      "num_items": 100
    }
  }'

# Check status
curl http://localhost:8000/api/jobs/{job_id}

# Get results
curl http://localhost:8000/api/results/test-1/summary
```

### Load Testing

```bash
# Spin up 10 concurrent tests
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

# Wait for completion
wait

# Check results
for i in {1..10}; do
  curl http://localhost:8000/api/results/test-$i/summary | jq '.blocks[0]'
done
```

## Content Blocks Demonstrated

This agent returns examples of all content block types:

1. **Section** - Markdown text with formatting
2. **Divider** - Visual separator
3. **Metric Grid** (custom) - Key metrics display
4. **Context** - Small metadata text
5. **Data Table** (custom) - Paginated table with sorting
6. **Chart** (custom) - Bar chart data
7. **Markdown** (custom) - Multi-paragraph formatted text

## Database Schema

See [CLAUDE.md](CLAUDE.md) for complete schema documentation.

## Cost

- **Per run:** ~$0.01
- **100 runs:** ~$1.00
- **Duration:** ~30 seconds

## Files

```
test-agent/
├── CLAUDE.md              # Agent instructions
├── README.md              # This file
├── db/
│   ├── init_db.py         # Database initialization
│   └── test.db            # SQLite database (runtime)
├── scripts/
│   ├── generate_data.py   # Generate test data
│   └── log_usage.py       # Usage logging (hook)
└── .claude/
    └── settings.json      # Agent permissions & hooks
```

## Integration

To add to production orchestration:

1. **Add to `agent_runner.py`:**
   ```python
   repos = {
       "seo-research": "https://github.com/colma-ai/claude-seo-research-agent.git",
       "test": "https://github.com/colma-ai/test-agent.git"  # Add this
   }
   ```

2. **Add to `prompts.py`:**
   ```python
   if agent_type == "test":
       return build_test_prompt(form_data)
   ```

3. **Add extractor in `extractors/test.py`:**
   ```python
   class TestResultExtractor(ResultExtractor):
       async def extract(self, workspace: Path) -> dict:
           # Extract from db/test.db
           # Return content blocks
   ```

4. **Add results API endpoint in `results_api.py`:**
   ```python
   @router.get("/{test_id}/items")
   async def get_test_items(test_id: str, page: int = 1):
       # Query items table
       # Return paginated results
   ```

## License

MIT
