# Auto-Update System Documentation

## Overview

The auto-update system automatically keeps your chatbot's data fresh by scraping the college website and cleaning the database monthly.

---

## Components

### 1. `cleanup_database.py`
**Purpose**: Cleans and enhances the database

**What it does**:
- ✅ Removes navigation menu duplicates (~200+ chunks)
- ✅ Resolves data conflicts (e.g., PhD year inconsistencies)
- ✅ Adds explicit FAQ entries for all key personnel
- ✅ Deletes cache files to force index rebuild
- ✅ Creates backup before modifications

**Usage**:
```bash
python scripts/cleanup_database.py
```

**Output**:
- Cleaned `unified_vectors.json`
- Backup file: `unified_vectors.json.backup`
- Deleted cache files (FAISS and BM25 indices)
- Statistics report

---

### 2. `auto_update.py`
**Purpose**: Automated monthly data refresh

**What it does**:
- 🔄 Checks if 30 days have passed since last update
- 🌐 Runs website scraper (if available)
- 🧹 Runs database cleanup
- 📝 Logs all activities
- ⏰ Schedules next update

**Usage**:

**Run scheduler (continuous mode)**:
```bash
python scripts/auto_update.py
```

**Force immediate update**:
```bash
python scripts/auto_update.py --force
```

**Check if update is needed**:
```bash
python scripts/auto_update.py --check
```

**Run as background service** (Windows):
```bash
Start-Process python -ArgumentList "scripts/auto_update.py" -WindowStyle Hidden
```

---

## Setup Instructions

### 1. Install Dependencies

```bash
pip install schedule
```

### 2. Create Required Directories

```bash
mkdir app/logs
mkdir app/database
```

### 3. Initial Setup

Run the cleanup script once to fix existing issues:

```bash
python scripts/cleanup_database.py
```

### 4. Start Auto-Update Scheduler

**Option A: Run in foreground** (for testing)
```bash
python scripts/auto_update.py
```

**Option B: Run as background service**
```bash
# Windows
Start-Process python -ArgumentList "scripts/auto_update.py" -WindowStyle Hidden

# Linux/Mac
nohup python scripts/auto_update.py &
```

---

## Configuration

### Update Interval

Edit `auto_update.py` to change the update frequency:

```python
self.update_interval_days = 30  # Change to desired number of days
```

### Schedule Time

Updates are checked daily at 2 AM. To change:

```python
schedule.every().day.at("02:00").do(self.check_and_update)
# Change "02:00" to your preferred time (24-hour format)
```

---

## Logs

All update activities are logged to:
- **File**: `app/logs/auto_update.log`
- **Console**: Real-time output

**Log format**:
```
2026-01-17 02:00:00 - INFO - Starting auto-update process
2026-01-17 02:00:05 - INFO - Running database cleanup...
2026-01-17 02:00:10 - INFO - ✓ Cleanup completed successfully
2026-01-17 02:00:10 - INFO - ✅ Auto-update completed successfully!
```

---

## Update Tracking

The system tracks updates in:
```
app/database/last_update.json
```

**Example**:
```json
{
  "last_update": "2026-01-17T02:00:00",
  "status": "success"
}
```

---

## Testing

### Test the Fixes

Run the test script to verify all fixes work:

```bash
python scripts/test_fixes.py
```

**Expected output**:
```
✅ PASS - Who is the principal?
✅ PASS - Who is the vice principal?
✅ PASS - Who is the HOD of CSE?
✅ PASS - Who is the HOD of CSM?
✅ PASS - Who is the HOD of CSD?
✅ PASS - Who is the founder?

Total: 6/6 tests passed
Success rate: 100.0%
```

---

## Troubleshooting

### Issue: Update not running

**Check**:
1. Is the scheduler running?
   ```bash
   # Check if process is running
   ps aux | grep auto_update.py  # Linux/Mac
   Get-Process | Where-Object {$_.ProcessName -like "*python*"}  # Windows
   ```

2. Check logs:
   ```bash
   cat app/logs/auto_update.log  # Linux/Mac
   Get-Content app/logs/auto_update.log  # Windows
   ```

### Issue: Scraper fails

The system will continue with cleanup even if the scraper fails. Check:
- Is `scripts/scrape_website.py` present?
- Check logs for error messages

### Issue: Cleanup fails

**Common causes**:
- File permissions
- Corrupted database file
- Insufficient disk space

**Solution**:
1. Check backup file exists: `unified_vectors.json.backup`
2. Restore from backup if needed:
   ```bash
   cp app/database/vectordb/unified_vectors.json.backup app/database/vectordb/unified_vectors.json
   ```

---

## Manual Operations

### Force Update Now

```bash
python scripts/auto_update.py --force
```

### Restore from Backup

```bash
# Windows
Copy-Item app/database/vectordb/unified_vectors.json.backup app/database/vectordb/unified_vectors.json

# Linux/Mac
cp app/database/vectordb/unified_vectors.json.backup app/database/vectordb/unified_vectors.json
```

### Clear Cache Manually

```bash
# Windows
Remove-Item app/database/vectordb/faiss_index.bin -ErrorAction SilentlyContinue
Remove-Item app/database/vectordb/bm25_index.pkl -ErrorAction SilentlyContinue

# Linux/Mac
rm -f app/database/vectordb/faiss_index.bin
rm -f app/database/vectordb/bm25_index.pkl
```

---

## Best Practices

1. **Monitor logs regularly** - Check `auto_update.log` weekly
2. **Keep backups** - Don't delete `.backup` files
3. **Test after updates** - Run `test_fixes.py` after each update
4. **Schedule during low traffic** - Default 2 AM is recommended
5. **Version control** - Commit database changes to git

---

## System Requirements

- Python 3.8+
- Required packages: `schedule`, `requests`, `beautifulsoup4`
- Disk space: ~500MB for database and backups
- RAM: ~2GB for index rebuilding

---

## Support

For issues or questions:
1. Check logs: `app/logs/auto_update.log`
2. Run test script: `python scripts/test_fixes.py`
3. Review this documentation
4. Check backup files exist

---

## Version History

- **v1.0** (2026-01-17)
  - Initial release
  - Monthly auto-updates
  - Database cleanup
  - FAQ enhancement
  - Conflict resolution
