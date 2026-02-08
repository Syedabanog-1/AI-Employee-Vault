# Quickstart: Bronze Phase - AI Employee Foundation

**Time to complete**: ~15 minutes
**Prerequisites**: Python 3.13+, Claude Code CLI, Obsidian

---

## Step 1: Install Dependencies (2 minutes)

Open terminal in the vault directory and install Python packages:

```bash
cd "D:\syeda Gulzar Bano\AI_Employee_Vault_"
pip install -r requirements.txt
```

Or install individually:
```bash
pip install watchdog pyyaml python-dotenv
```

---

## Step 2: Verify Vault Structure (1 minute)

Open the vault in Obsidian and verify these folders exist:
- `/Needs_Action/` - Where tasks appear
- `/Done/` - Where completed tasks go
- `/Logs/` - Where logs are written
- `/Drop_Folder/` - Where you drop files

Verify these files exist:
- `Dashboard.md` - Should show "System initialized"
- `Company_Handbook.md` - Should have rules defined

---

## Step 3: Configure Environment (2 minutes)

Create `.env` file from template:

```bash
copy .env.example .env
```

Edit `.env` and set:
```
DEV_MODE=true
DRY_RUN=false
VAULT_PATH=D:\syeda Gulzar Bano\AI_Employee_Vault_
DROP_FOLDER=D:\syeda Gulzar Bano\AI_Employee_Vault_\Drop_Folder
```

---

## Step 4: Start the FileSystem Watcher (2 minutes)

Open a new terminal and run:

```bash
cd "D:\syeda Gulzar Bano\AI_Employee_Vault_\watchers"
python filesystem_watcher.py
```

You should see:
```
FileSystem Watcher starting...
Watching: D:\syeda Gulzar Bano\AI_Employee_Vault_\Drop_Folder
Tasks go to: D:\syeda Gulzar Bano\AI_Employee_Vault_\Needs_Action
Press Ctrl+C to stop
--------------------------------------------------
```

---

## Step 5: Test File Detection (2 minutes)

1. Keep the watcher running
2. Copy any file (e.g., `test.txt`) into `/Drop_Folder/`
3. Within 5 seconds, check `/Needs_Action/`
4. You should see `FILE_test.txt.md`

Open the task file - it should have:
```yaml
---
type: file_drop
status: pending
timestamp: 2026-02-07T...
---

## File Received
...
```

---

## Step 6: Process with Claude Code (3 minutes)

Open Claude Code in the vault directory:

```bash
cd "D:\syeda Gulzar Bano\AI_Employee_Vault_"
claude
```

Give Claude this prompt:

```
You are my Personal AI Employee.

Your job:
1. Look inside /Needs_Action folder
2. For each file:
   - Read it
   - Write a short summary
   - Update Dashboard.md with what you did
3. Move the file to /Done when finished

Rules:
- Do not delete files
- Only work inside this vault
- Be concise
```

Claude will:
1. Read the task file
2. Summarize it
3. Update Dashboard.md
4. Move the file to /Done

---

## Step 7: Verify Success (2 minutes)

Check these items:

**✅ Task processed**:
- `/Needs_Action/` should be empty
- `/Done/` should have `FILE_test.txt.md`

**✅ Dashboard updated**:
- Open `Dashboard.md` in Obsidian
- Recent Activity should show the processed task

**✅ Log created**:
- Check `/Logs/2026-02-07.json`
- Should have log entries for the actions

---

## Troubleshooting

### Watcher doesn't detect files
- Check the watcher is running (terminal should show output)
- Verify `DROP_FOLDER` path in `.env` is correct
- Try restarting the watcher

### Task file not created
- Check `/Needs_Action/` folder permissions
- Look for errors in watcher terminal output
- Try with `--dry-run` flag to debug

### Claude doesn't process
- Ensure you're in the vault directory
- Check Claude Code is properly configured
- Try the prompt again with more specific instructions

### Dashboard not updated
- Check file permissions on `Dashboard.md`
- Close and reopen in Obsidian
- Manually refresh the file

---

## Next Steps

**Bronze Phase Complete!** You now have:
- ✅ Working vault structure
- ✅ FileSystem Watcher detecting files
- ✅ Claude processing tasks
- ✅ Basic logging

**To continue to Silver Phase**:
1. Run `/sp.plan` for Silver Phase
2. Add Gmail Watcher
3. Add Human-in-the-Loop approval
4. Add Email MCP server

---

## Demo Script (For Hackathon)

Use this to demonstrate Bronze tier:

1. "Here's my AI Employee vault in Obsidian"
2. "The FileSystem Watcher is monitoring Drop_Folder"
3. *Drop a file*
4. "Within 5 seconds, a task file appears"
5. *Show task file with YAML frontmatter*
6. "Now Claude processes it..."
7. *Run Claude with process prompt*
8. "Dashboard is updated, file moves to Done"
9. "Logs capture everything for audit"

**Time**: ~2 minutes for demo
